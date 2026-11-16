#!/usr/bin/env python3
"""运行期解释器入口：六个工序算子的闭集 + 五值退出码（批次 0095）。

算子闭集（`spec/D6_REBASELINE_PROPOSAL.md` 4.3(3)）：本文件只认这六个名字，
出现其他算子即 `procedure_invalid`（退出码 2），不执行、不降级。

  fill_schema   把装配层给定的工件按 schema 填入槽位；缺产出即阻断
  compute       调注册表里的纯函数（CPM、预算汇总、风险排序、采样、偏差、EVM、留痕追加）
  lookup        只做精确键查找（术语表 / 配置项）；查不到即 cannot_evaluate
  check         按名称执行绑定检查；`fails` 取 block（默认）或 report
  human_approve 消费人类签字记录；无记录即 cannot_evaluate，拒绝即违规
  render        把槽位按模板渲染成 Markdown；不做自由文本生成

退出码（五值语义）：
  0 通过
  1 违规（含 config_drift、偏离开档以外的显式失败）
  2 输入/配置/工序不合法（含工件未过 schema、缺槽、跳步）
  3 存在无法机械判定项（配置缺项、跨工件证据缺失、待人类签字）
  4 解释器自身不可用（运行契约或 schema 缺失/非法）
聚合优先级：4 > 2 > 3 > 1 > 0；输入非法优先于不可判定，
不可判定优先于显式违规（“判不了”不能被“已发现的违规”掩盖）。

零第三方依赖：只用标准库。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pm_caps
import pm_config
from pm_schema import SchemaError, contract_errors, digest, validate

ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / "runtime"
ARTIFACT_DIR = RUNTIME / "artifacts"
PROCEDURE_DIR = RUNTIME / "procedures"
TEMPLATE_DIR = RUNTIME / "templates"
GLOSSARY = RUNTIME / "glossary.json"
CATALOG = RUNTIME / "task-catalog.json"

OPERATORS = ("fill_schema", "compute", "lookup", "check", "human_approve", "render")
STATUS_EXIT = {"pass": 0, "violation": 1, "invalid": 2, "cannot_evaluate": 3}
PRECEDENCE = {0: 0, 1: 1, 3: 2, 2: 3, 4: 4}
EXIT_STATUS = {1: "violation", 2: "invalid", 3: "cannot_evaluate"}
CAPABILITY_IDS = (
    "dependency_graph",
    "cost_budget",
    "risk_register",
    "status_collection",
    "deviation",
    "earned_value",
    "audit_trail",
)


class RuntimeBroken(Exception):
    """解释器自身不可用：退出码 4。"""


class InputInvalid(Exception):
    """输入/配置/工序不合法：退出码 2。"""


def aggregate(codes: list[int]) -> int:
    return max(codes, key=lambda code: PRECEDENCE.get(code, 4)) if codes else 0


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputInvalid(f"{path}：不可读取：{exc}") from exc
    except json.JSONDecodeError as exc:
        raise InputInvalid(f"{path}：不可解析：{exc}") from exc
    except RecursionError as exc:
        raise InputInvalid(f"{path}：嵌套过深，无法解析：{exc}") from exc


CONFIG_STATUS = {
    "config_invalid": "invalid",
    "config_incomplete": "invalid",
    "config_drift": "violation",
    "cannot_evaluate": "cannot_evaluate",
}


def config_findings(config_state: pm_config.ConfigState) -> list[dict]:
    """把配置层 finding 转成报告 finding；聚合前必须并入，不许只改退出码。

    依据：`spec/D6_REBASELINE_PROPOSAL.md` 9.2（配置层结论随判定一起出具）。
    """
    results: list[dict] = []
    for item in config_state.findings:
        code = str(item.get("code", "config_unknown"))
        status = CONFIG_STATUS.get(code, "cannot_evaluate")
        results.append(
            {
                "check": f"config.{code}",
                "status": status,
                "detail": str(item.get("detail", "")),
            }
        )
    return results


def status_code(status: str) -> int:
    return STATUS_EXIT.get(status, 4)


def _schema_cache() -> dict[str, dict]:
    if not ARTIFACT_DIR.is_dir():
        raise RuntimeBroken(f"缺少工件契约目录：{ARTIFACT_DIR}")
    schemas: dict[str, dict] = {}
    for path in sorted(ARTIFACT_DIR.glob("*.schema.json")):
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeBroken(f"工件契约不可读：{path}：{exc}") from exc
        defects = contract_errors(schema)
        if defects:
            raise RuntimeBroken(f"{path.name}：{'；'.join(defects)}")
        unknown = [name for name in schema["x-checks"] if name not in pm_caps.CHECK_REGISTRY]
        if unknown:
            raise RuntimeBroken(f"{path.name}：x-checks 未注册：{unknown}")
        schemas[path.name[: -len(".schema.json")]] = schema
    if not schemas:
        raise RuntimeBroken(f"{ARTIFACT_DIR} 下没有工件契约")
    return schemas


def validate_artifact(instance: object, config_state: pm_config.ConfigState | None) -> dict:
    """校验一件工件，返回 {exit_code, findings, digest, type}。

    契约要求（`spec/D6_REBASELINE_PROPOSAL.md` 3.2、9.2）：

    - 工件必须是对象；数组/标量属于输入不合法（2），不得抛 `AttributeError`。
    - 没有 `--config` 就无法比对 `config_ref.config_digest`，跨配置可比性无法建立，
      一律 `cannot_evaluate`（3），不存在“跳过比对后工件退 0”的路径。
    - 配置层 finding 必须并入报告后再聚合，不许只改退出码。
    """
    if not isinstance(instance, dict):
        raise InputInvalid(f"工件顶层必须是对象，实际是 {type(instance).__name__}")
    schemas = _schema_cache()
    artifact_type = instance.get("artifact_type")
    if not isinstance(artifact_type, str) or artifact_type not in schemas:
        raise InputInvalid(f"未注册的工件类型：{artifact_type!r}")
    schema = schemas[artifact_type]
    findings: list[dict] = []
    structural = validate(instance, schema)
    for error in structural:
        findings.append(
            {"check": "schema.shape", "status": "invalid", "detail": f"{error['path']}：{error['message']}"}
        )
    if structural:
        return {
            "exit_code": 2,
            "artifact_type": artifact_type,
            "digest": digest(instance),
            "findings": findings,
        }

    provenance = instance.get("provenance", {})
    for key in schema["x-provenance"]["requires"]:
        if not str(provenance.get(key, "")).strip():
            findings.append(
                {
                    "check": "provenance.required",
                    "status": "invalid",
                    "detail": f"缺少来源引用：{key}",
                }
            )
    if findings:
        return {
            "exit_code": 2,
            "artifact_type": artifact_type,
            "digest": digest(instance),
            "findings": findings,
        }

    if config_state is None:
        return {
            "exit_code": 3,
            "artifact_type": artifact_type,
            "digest": digest(instance),
            "findings": [
                {
                    "check": "config.missing",
                    "status": "cannot_evaluate",
                    "detail": "未提供 --config：config_ref/config_digest 无法比对，跨配置可比性无法建立",
                }
            ],
        }

    config_results = config_findings(config_state)
    if config_state.exit_code == pm_config.EXIT_INVALID:
        return {
            "exit_code": 2,
            "artifact_type": artifact_type,
            "digest": digest(instance),
            "findings": findings + config_results,
        }
    declared = instance.get("config_ref", {}).get("config_digest")
    if declared != config_state.snapshot["config_digest"]:
        config_results.append(
            {
                "check": "config.drift",
                "status": "violation",
                "detail": "工件携带的配置摘要与当前配置不一致（跨配置不可比）",
            }
        )

    ctx = {
        "config": config_state.config,
        "artifacts": {artifact_type: instance["data"]},
    }
    results = pm_caps.run_checks(schema["x-checks"], instance["data"], ctx)
    findings.extend(results)
    unsupported = instance.get("unsupported", [])
    if unsupported:
        findings.append(
            {
                "check": "artifact.unsupported",
                "status": "cannot_evaluate",
                "detail": f"工件自报无法机械判定项：{unsupported}",
            }
        )
    findings.extend(config_results)
    codes = [status_code(item["status"]) for item in findings]
    codes.append(config_state.exit_code)
    return {
        "exit_code": aggregate(codes),
        "artifact_type": artifact_type,
        "digest": digest(instance),
        "findings": findings,
    }


def _procedure_errors(procedure: dict) -> list[str]:
    errors: list[str] = []
    steps = procedure.get("steps")
    if not isinstance(steps, list) or not steps:
        return ["procedure.steps 必须是非空数组"]
    seen: set[str] = set()
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            errors.append(f"第 {index + 1} 步不是对象")
            continue
        step_id = step.get("id")
        if not isinstance(step_id, str) or not step_id:
            errors.append(f"第 {index + 1} 步缺少 id")
            continue
        if step_id in seen:
            errors.append(f"步骤 id 重复：{step_id}")
        seen.add(step_id)
        op = step.get("op")
        if op not in OPERATORS:
            errors.append(f"{step_id}：算子不在闭集内：{op!r}")
        for need in step.get("needs", []):
            if need not in seen or need == step_id:
                errors.append(f"{step_id}：needs 引用了未执行或自身步骤 {need}")
        if op == "fill_schema":
            if not step.get("schema") or not step.get("input"):
                errors.append(f"{step_id}：fill_schema 需要 schema 与 input")
        elif op == "compute":
            if step.get("method") not in pm_caps.COMPUTE_REGISTRY:
                errors.append(f"{step_id}：compute 方法未注册：{step.get('method')!r}")
        elif op == "lookup":
            if step.get("table") not in ("glossary", "config"):
                errors.append(f"{step_id}：lookup 表未登记：{step.get('table')!r}")
        elif op == "check":
            if not step.get("checks"):
                errors.append(f"{step_id}：check 需要 checks")
            if step.get("fails", "block") not in ("block", "report"):
                errors.append(f"{step_id}：fails 只能是 block/report")
        elif op == "human_approve":
            if not step.get("gate") or not step.get("must_see"):
                errors.append(f"{step_id}：human_approve 需要 gate 与 must_see")
        elif op == "render":
            if not step.get("template") or not step.get("input") or not step.get("out"):
                errors.append(f"{step_id}：render 需要 template、input 与 out")
        if op in ("compute", "check") and not step.get("slot") and op == "compute":
            errors.append(f"{step_id}：compute 需要 slot")
    return errors


class ProcedureRunner:
    def __init__(
        self,
        procedure: dict,
        inputs: Path,
        config_state: pm_config.ConfigState | None,
        out_dir: Path | None,
    ) -> None:
        self.procedure = procedure
        self.inputs = inputs
        self.config_state = config_state
        self.out_dir = out_dir
        self.slots: dict[str, object] = {}
        self.steps: list[dict] = []
        self.codes: list[int] = []

    # ---- 单个算子的实现

    def _fill_schema(self, step: dict) -> tuple[str, str]:
        path = self.inputs / step["input"]
        instance = load_json(path)
        schema_name = step["schema"]
        schemas = _schema_cache()
        if schema_name not in schemas:
            raise RuntimeBroken(f"{step['id']}：未注册工件契约：{schema_name}")
        result = validate_artifact(instance, self.config_state)
        if result["artifact_type"] != schema_name:
            raise InputInvalid(
                f"{step['id']}：工件类型 {result['artifact_type']} 与声明 {schema_name} 不符"
            )
        if result["exit_code"] != 0 and step.get("fails", "block") == "block":
            self.slots[step["slot"]] = instance
            detail = "；".join(item["detail"] for item in result["findings"])
            return (EXIT_STATUS[result["exit_code"]], detail)
        self.slots[step["slot"]] = instance
        return ("pass", f"schema={schema_name} digest={result['digest']}")

    def _payload(self, slot: str) -> object:
        if slot not in self.slots:
            raise InputInvalid(f"槽位不存在：{slot}")
        value = self.slots[slot]
        return value["data"] if isinstance(value, dict) and "data" in value else value

    def _compute(self, step: dict) -> tuple[str, str]:
        inputs = {name: self._payload(name) for name in step.get("inputs", [])}
        if step.get("record") is not None:
            inputs["record"] = step["record"]
        config = self.config_state.config if self.config_state is not None else {}
        result = pm_caps.COMPUTE_REGISTRY[step["method"]](inputs, config)
        if not isinstance(result, dict) or result.get("status") == pm_caps.CANNOT:
            detail = result.get("detail", "计算无法判定") if isinstance(result, dict) else "计算无结果"
            return ("cannot_evaluate", detail)
        self.slots[step["slot"]] = result
        return ("pass", f"{step['method']} 完成")

    def _lookup(self, step: dict) -> tuple[str, str]:
        key = step["key"]
        if step["table"] == "glossary":
            if not GLOSSARY.is_file():
                raise RuntimeBroken(f"缺少术语表：{GLOSSARY}")
            for entry in json.loads(GLOSSARY.read_text(encoding="utf-8")):
                if key in {entry.get("term_id"), entry.get("term"), *entry.get("aliases", [])}:
                    self.slots[step["slot"]] = entry
                    return ("pass", f"命中 {entry.get('term_id')}")
            return ("cannot_evaluate", f"术语表无此键：{key}")
        config = self.config_state.config if self.config_state is not None else {}
        if key in config:
            self.slots[step["slot"]] = config[key]
            return ("pass", f"配置项 {key} 命中")
        return ("cannot_evaluate", f"配置未给出 {key}")

    def _check(self, step: dict) -> tuple[str, str]:
        unknown = [name for name in step["checks"] if name not in pm_caps.CHECK_REGISTRY]
        if unknown:
            raise RuntimeBroken(f"{step['id']}：检查未注册：{unknown}")
        data = self._payload(step["input"])
        artifacts = {}
        for value in self.slots.values():
            if isinstance(value, dict) and "artifact_type" in value and "data" in value:
                artifacts[value["artifact_type"]] = value["data"]
                artifacts[value["artifact_type"].replace("-", "_")] = value["data"]
        ctx = {
            "config": self.config_state.config if self.config_state is not None else {},
            "artifacts": artifacts,
        }
        findings = pm_caps.run_checks(step["checks"], data, ctx)
        self.slots[step["slot"]] = findings if step.get("slot") else self.slots.get(step["slot"])
        statuses = {item["status"] for item in findings}
        detail = "；".join(
            f"{item['check']}={item['status']}：{item['detail']}" for item in findings
        )
        if "violation" in statuses:
            return ("violation", detail)
        if "cannot_evaluate" in statuses:
            return ("cannot_evaluate", detail)
        return ("pass", detail)

    def _human_approve(self, step: dict) -> tuple[str, str]:
        path = self.inputs / "approval.json"
        if self.config_state is None:
            return (
                "cannot_evaluate",
                f"未提供 --config：{step['gate']} 的签字角色映射（CFG-12）无法比对",
            )
        role_map = (self.config_state.config.get("CFG-12") or {}).get("approver_role_map")
        if not isinstance(role_map, dict) or step["gate"] not in role_map:
            return (
                "cannot_evaluate",
                f"CFG-12 未给出 {step['gate']} 的签字角色映射，角色一致性无法判定",
            )
        if not path.is_file():
            return ("cannot_evaluate", f"待人类签字：{step['gate']}（无 approval.json）")
        records = load_json(path)
        if not isinstance(records, list):
            raise InputInvalid(f"{path}：顶层必须是签字记录数组")
        matches = [
            record
            for record in records
            if isinstance(record, dict) and record.get("gate") == step["gate"]
        ]
        if not matches:
            return ("cannot_evaluate", f"待人类签字：{step['gate']}")
        latest = matches[-1]
        if latest.get("decision") == "reject":
            return ("violation", f"{step['gate']} 被拒绝，原因：{latest.get('reason', '未填写')}")
        seen = set(latest.get("seen", []))
        unseen = [item for item in step["must_see"] if item not in seen]
        if unseen:
            return ("violation", f"{step['gate']} 未见证据步骤：{unseen}")
        role = latest.get("role")
        if role != role_map[step["gate"]]:
            return (
                "violation",
                f"{step['gate']} 的签字角色 {role!r} 与 CFG-12 映射 {role_map[step['gate']]!r} 不符",
            )
        return ("pass", f"{step['gate']} 由 {latest.get('actor')}（{role}）签字")

    def _render(self, step: dict) -> tuple[str, str]:
        path = TEMPLATE_DIR / step["template"]
        if not path.is_file():
            raise RuntimeBroken(f"{step['id']}：模板不存在：{path}")
        payload = self._payload(step["input"])
        text = path.read_text(encoding="utf-8")
        text = text.replace("{{payload}}", json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
        text = text.replace(
            "{{config_digest}}",
            self.config_state.snapshot["config_digest"] if self.config_state else "（未提供配置）",
        )
        text = text.replace("{{procedure}}", self.procedure.get("procedure", "unknown"))
        if "{{" in text:
            raise InputInvalid(f"{step['id']}：模板存在未替换占位符")
        if self.out_dir is None:
            raise InputInvalid(f"{step['id']}：render 需要 --out-dir")
        self.out_dir.mkdir(parents=True, exist_ok=True)
        base = self.out_dir.resolve()
        target = (self.out_dir / step["out"]).resolve()
        if base not in target.parents:
            raise InputInvalid(
                f"{step['id']}：render.out 越出 --out-dir（{step['out']} → {target}）"
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        return ("pass", f"渲染至 {target}")

    # ---- 主循环

    def run(self) -> dict:
        errors = _procedure_errors(self.procedure)
        if errors:
            return {"exit_code": 2, "findings": [{"detail": item} for item in errors], "steps": []}
        for step in self.procedure["steps"]:
            handler = getattr(self, f"_{step['op']}")
            try:
                status, detail = handler(step)
            except RuntimeBroken:
                raise
            except InputInvalid as exc:
                status, detail = "invalid", str(exc)
            code = STATUS_EXIT[status]
            self.steps.append(
                {"id": step["id"], "op": step["op"], "status": status, "exit_code": code, "detail": detail}
            )
            self.codes.append(code)
            blocking = step.get("fails", "block") == "block"
            if code in (1, 3) and blocking:
                break
            if code == 2:
                break
        return {"exit_code": aggregate(self.codes), "steps": self.steps}


def check_catalog(config_state: pm_config.ConfigState | None = None) -> dict:
    """任务目录的机械检查：无过程、无检查、无出口的任务不得存在。"""
    catalog = load_json(CATALOG)
    tasks = catalog.get("tasks")
    findings: list[dict] = []
    if not isinstance(tasks, list) or not tasks:
        raise InputInvalid("task-catalog.tasks 必须是非空数组")
    ids = [task.get("id") for task in tasks]
    duplicates = sorted({key for key in ids if ids.count(key) > 1})
    if duplicates:
        findings.append({"detail": f"任务 id 重复：{duplicates}"})
    required = ("id", "title", "domain", "capabilities", "procedure", "outputs", "gates", "checks")
    procedure_checks: dict[str, set[str]] = {}
    for task in tasks:
        missing = [field for field in required if not task.get(field)]
        if missing:
            findings.append({"detail": f"{task.get('id')}：缺字段 {missing}"})
            continue
        unknown = [name for name in task["checks"] if name not in pm_caps.CHECK_REGISTRY]
        if unknown:
            findings.append({"detail": f"{task['id']}：检查未注册 {unknown}"})
        unknown_caps = [name for name in task["capabilities"] if name not in CAPABILITY_IDS]
        if unknown_caps:
            findings.append({"detail": f"{task['id']}：能力未登记 {unknown_caps}"})
        path = PROCEDURE_DIR / task["procedure"]
        if not path.is_file():
            findings.append({"detail": f"{task['id']}：过程不存在 {task['procedure']}"})
            continue
        procedure = load_json(path)
        errors = _procedure_errors(procedure)
        if errors:
            findings.append({"detail": f"{task['id']}：过程不合法 {errors}"})
        step_checks = {
            name
            for step in procedure.get("steps", [])
            for name in step.get("checks", [])
        }
        procedure_checks[str(path)] = step_checks
        uncovered = sorted(step_checks - set(task["checks"]))
        if uncovered:
            findings.append({"detail": f"{task['id']}：过程检查未列入任务卡 {uncovered}"})
    covered_caps = {name for task in tasks for name in task.get("capabilities", [])}
    lacking = sorted(set(CAPABILITY_IDS) - covered_caps)
    if lacking:
        findings.append({"detail": f"能力无任务承接：{lacking}"})
    referenced = {task.get("procedure") for task in tasks}
    orphans = sorted(
        path.name for path in PROCEDURE_DIR.glob("*.json") if path.name not in referenced
    )
    if orphans:
        findings.append({"detail": f"过程无任务引用：{orphans}"})
    schemas = _schema_cache()
    covered_types = set()
    for task in tasks:
        for output in task.get("outputs", []):
            covered_types.add(output)
    unused = sorted(set(schemas) - covered_types)
    if unused:
        findings.append({"detail": f"工件契约无任务产出：{unused}"})
    return {"exit_code": 2 if findings else 0, "findings": findings, "tasks": len(tasks)}


def _merge_config(result: dict, config_state: pm_config.ConfigState | None) -> None:
    """把配置层 finding 并入判定报告后再聚合退出码。

    依据：`spec/D6_REBASELINE_PROPOSAL.md` 9.2；不许出现“退 1 但 findings 里
    一条 `config.*` 都没有”的报告。
    """
    if config_state is None:
        return
    merged = config_findings(config_state)
    if not merged:
        return
    result.setdefault("findings", []).extend(merged)
    codes = [int(result.get("exit_code", 0))]
    codes.extend(status_code(item["status"]) for item in merged)
    result["exit_code"] = aggregate(codes)


def _emit(result: dict) -> None:
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="运行期解释器（六算子闭集）")
    parser.add_argument("--config", metavar="PATH", help="运行期配置")
    parser.add_argument("--lock", metavar="PATH", help="config.lock.json")
    parser.add_argument("--artifact", metavar="PATH", help="校验一件工件")
    parser.add_argument("--procedure", metavar="PATH", help="执行一条工序")
    parser.add_argument("--inputs", metavar="DIR", help="工序输入目录")
    parser.add_argument("--out-dir", metavar="DIR", help="render 输出目录")
    parser.add_argument("--catalog", action="store_true", help="校验任务目录")
    args = parser.parse_args(argv)

    try:
        if not ARTIFACT_DIR.is_dir():
            raise RuntimeBroken(f"缺少运行契约目录：{ARTIFACT_DIR}")
        config_state = None
        if args.config:
            config_state = pm_config.evaluate(
                Path(args.config), Path(args.lock) if args.lock else None
            )
            if args.artifact or args.procedure or args.catalog:
                if config_state.exit_code == pm_config.EXIT_INVALID:
                    _emit(
                        {
                            "exit_code": 2,
                            "findings": config_findings(config_state),
                            "detail": "配置不合法，判定不启动",
                        }
                    )
                    return 2
        if args.catalog:
            result = check_catalog(config_state)
            _merge_config(result, config_state)
            _emit(result)
            return result["exit_code"]
        if args.artifact:
            result = validate_artifact(load_json(Path(args.artifact)), config_state)
            _emit(result)
            return result["exit_code"]
        if args.procedure:
            if not args.inputs:
                raise InputInvalid("--procedure 需要 --inputs")
            procedure = load_json(Path(args.procedure))
            runner = ProcedureRunner(
                procedure,
                Path(args.inputs),
                config_state,
                Path(args.out_dir) if args.out_dir else None,
            )
            result = runner.run()
            _merge_config(result, config_state)
            _emit(result)
            return result["exit_code"]
        if config_state is not None:
            _emit({"exit_code": config_state.exit_code, "findings": config_state.findings})
            return config_state.exit_code
    except RuntimeBroken as exc:
        _emit({"exit_code": 4, "findings": [{"detail": f"解释器不可用：{exc}"}]})
        return 4
    except InputInvalid as exc:
        _emit({"exit_code": 2, "findings": [{"detail": str(exc)}]})
        return 2
    except RecursionError as exc:
        _emit({"exit_code": 2, "findings": [{"detail": f"输入嵌套过深：{exc}"}]})
        return 2
    except SchemaError as exc:
        _emit({"exit_code": 4, "findings": [{"detail": f"schema 内核不可用：{exc}"}]})
        return 4
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
