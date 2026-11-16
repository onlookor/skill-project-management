#!/usr/bin/env python3
"""运行期解释器与七项能力的正反例自测（批次 0095）。

覆盖：
- 配置求值：0（齐备）、2（结构非法）、3（判定性项缺失）、1（摘要漂移）、
  CFG-10/11 缺省时登记 defaulted；
- 六份工件契约：各 1 例通过 + 1 例可机械判定的违规或结构违规；
- 五条工序：无模型跑通；缺签字 → 3；拒绝签字 → 1；未知算子/跳步 → 2；
- 解释器不可用 → 4（运行契约目录缺失时为 4，不降级为“通过”）。

用法：python3 scripts/test_pm_runtime.py
退出码：0 全部通过；1 有用例失败。
"""

from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
from pathlib import Path

import pm_caps
import pm_check
import pm_config
import pm_schema

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "runtime/demo"
INPUTS = DEMO / "inputs"
CONFIG = DEMO / "config.json"
LOCK = DEMO / "config.lock.json"

PASSED = 0
FAILED: list[str] = []


def check(label: str, actual: object, expected: object) -> None:
    global PASSED
    if actual == expected:
        PASSED += 1
        print(f"  ok   {label}")
    else:
        FAILED.append(label)
        print(f"  FAIL {label}：期望 {expected!r}，实得 {actual!r}")


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, body: dict) -> None:
    path.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def mutate(source: Path, target: Path, change) -> Path:
    body = copy.deepcopy(read(source))
    change(body)
    write(target, body)
    return target


def main() -> int:
    temp = Path(tempfile.mkdtemp(prefix="pm-runtime-test-"))
    try:
        print("[配置求值]")
        state = pm_config.evaluate(CONFIG, LOCK)
        # 依据：条款：T-F-015-EXIT（五值退出码，齐备配置退 0）
        check("齐备配置退出码", state.exit_code, 0)
        check("未取默认值", state.defaulted, ())
        # 依据：条款：D6-9.2-DEFAULT、CFG-10-DEFAULT（默认值只允许落在非判定性项且须登记）
        check(
            "默认值登记",
            pm_config.effective_config(
                {"config": {key: value for key, value in state.raw["config"].items() if key not in ("CFG-10", "CFG-11")}},
                state.schema,
            )[1],
            ("CFG-10", "CFG-11"),
        )

        missing = mutate(
            CONFIG,
            temp / "config-missing.json",
            lambda body: body["config"].pop("CFG-01"),
        )
        # 依据：条款：D6-9.3-CANNOT、CFG-01-JUDGE（判定性配置缺失即 cannot_evaluate）
        check("判定性项缺失 → 3", pm_config.evaluate(missing, None).exit_code, 3)

        broken = mutate(
            CONFIG,
            temp / "config-broken.json",
            lambda body: body["config"].__setitem__("CFG-04", "fortnightly"),
        )
        # 依据：条款：D6-9.3-INVALID（配置值越界/类型错/分档不覆盖退 2）
        check("非法枚举 → 2", pm_config.evaluate(broken, None).exit_code, 2)

        drifted = mutate(
            CONFIG,
            temp / "config-drift.json",
            lambda body: body["config"].__setitem__("CFG-09", "USD"),
        )
        # 依据：条款：D6-9.3-DRIFT、CFG-09-JUDGE（配置被改但锁未更新退 1）
        check("摘要漂移 → 1", pm_config.evaluate(drifted, LOCK).exit_code, 1)

        gap = mutate(
            CONFIG,
            temp / "config-gap.json",
            lambda body: body["config"]["CFG-03"]["boundaries"][1].__setitem__("lower", 0.85),
        )
        # 依据：条款：D6-9.3-INVALID（分档不覆盖退 2）
        check("分档不连续 → 2", pm_config.evaluate(gap, None).exit_code, 2)

        unregistered = mutate(
            CONFIG,
            temp / "config-unregistered.json",
            lambda body: body["config"].__setitem__("CFG-99", {"x": 1}),
        )
        # 依据：条款：D6-9.3-UNREGISTERED、CFG-REGISTRY（未注册配置项不得被当成新参数）
        check("未注册配置项 → 2", pm_config.evaluate(unregistered, None).exit_code, 2)

        def make_contradictory(body: dict) -> None:
            body["config"]["CFG-04"] = "milestone_fraction"
            body["config"].pop("CFG-05")

        contradictory = mutate(CONFIG, temp / "config-contradictory.json", make_contradictory)
        # 依据：条款：D6-9.3-INCOMPLETE（配置项相互矛盾退 2）
        check("配置项相互矛盾 → 2", pm_config.evaluate(contradictory, None).exit_code, 2)

        print("[工件契约：正例]")
        for name in ("schedule", "budget", "risk", "status", "evm", "audit"):
            result = pm_check.validate_artifact(read(INPUTS / f"{name}.json"), state)
            check(f"{name} 通过", result["exit_code"], 0)

        print("[工件契约：反例]")
        cyclic = mutate(
            INPUTS / "schedule.json",
            temp / "schedule-cycle.json",
            lambda body: body["data"]["dependencies"].append(
                {"from": "D", "to": "A", "type": "FS", "lag": 0}
            ),
        )
        # 依据：条款：D6-8.3-RG06（依赖图 CAP-13）、T-F-015-EXIT（聚合优先级 4 > 2 > 3 > 1 > 0，不可判定优先于显式违规）。
        check("依赖成环（违规+不可判定）→ 3", pm_check.validate_artifact(read(cyclic), state)["exit_code"], 3)

        residual = mutate(
            INPUTS / "risk.json",
            temp / "risk-residual.json",
            lambda body: body["data"]["risks"][0].__setitem__("residual_score", 9),
        )
        # 依据：条款：D6-8.3-RG08（风险登记册 CAP-25 的字段与残余口径）
        check("残余高于初始 → 1", pm_check.validate_artifact(read(residual), state)["exit_code"], 1)

        implicit = mutate(
            INPUTS / "status.json",
            temp / "status-implicit.json",
            lambda body: body["data"]["samples"][1]["measurements"][0].pop("value"),
        )
        # 依据：条款：D6-8.3-RG09（状态采集 CAP-35：缺数不得默认通过）
        check("隐式缺数 → 1", pm_check.validate_artifact(read(implicit), state)["exit_code"], 1)

        wrong_ev = mutate(
            INPUTS / "evm.json",
            temp / "evm-wrong.json",
            lambda body: body["data"]["measurements"][0].__setitem__("ev", 4000),
        )
        # 依据：条款：D6-8.3-RG11、CFG-13-JUDGE（挣值 CAP-20 与计量规则）
        check("EV 与 CFG-13 不符 → 1", pm_check.validate_artifact(read(wrong_ev), state)["exit_code"], 1)

        chain = mutate(
            INPUTS / "audit.json",
            temp / "audit-chain.json",
            lambda body: body["data"]["records"][1].__setitem__("prev_digest", "sha256:" + "3" * 64),
        )
        # 依据：条款：D6-8.3-RG12（审计留痕 CAP-42 的 prev_digest 链）
        check("摘要链断 → 1", pm_check.validate_artifact(read(chain), state)["exit_code"], 1)

        provenance = mutate(
            INPUTS / "schedule.json",
            temp / "schedule-no-provenance.json",
            lambda body: body["provenance"].pop("schedule.dependencies"),
        )
        # 依据：条款：D6-4.3-XCHECKS（工件契约强制 x-checks 与 x-provenance）
        check("缺来源引用 → 2", pm_check.validate_artifact(read(provenance), state)["exit_code"], 2)

        wrong_type = mutate(
            INPUTS / "schedule.json",
            temp / "schedule-wrong-type.json",
            lambda body: body.__setitem__("artifact_type", "unknown-artifact"),
        )
        # 依据：条款：D6-4.3-XCHECKS（未注册工件类型不得进入运行期）
        check("未注册工件类型 → 2", pm_check.main(["--artifact", str(wrong_type)]), 2)

        print("[工序：正例]")
        # 依据：条款：D6-4.3-OPS、PROC-STATUS-STEP1（工序卡首步 fill_schema 与六算子闭集）
        for name in ("schedule_baseline", "cost_baseline", "risk_review", "status_review", "audit_review"):
            out = temp / f"out-{name}"
            code = pm_check.main(
                [
                    "--procedure",
                    str(ROOT / "runtime/procedures" / f"{name}.json"),
                    "--inputs",
                    str(INPUTS),
                    "--config",
                    str(CONFIG),
                    "--lock",
                    str(LOCK),
                    "--out-dir",
                    str(out),
                ]
            )
            check(f"{name} 跑通", code, 0)
        check("任务目录通过", pm_check.main(["--catalog", "--config", str(CONFIG), "--lock", str(LOCK)]), 0)

        print("[工序：反例]")
        no_approval = temp / "inputs-no-approval"
        shutil.copytree(INPUTS, no_approval)
        (no_approval / "approval.json").unlink()
        # 依据：条款：D6-4.3-MUSTSEE、PROC-STATUS-GATE（签字前必须看到的证据是固定清单）
        check(
            "缺人类签字 → 3",
            pm_check.main(
                ["--procedure", str(ROOT / "runtime/procedures/schedule_baseline.json"), "--inputs", str(no_approval), "--config", str(CONFIG), "--lock", str(LOCK), "--out-dir", str(temp / "out-na")]
            ),
            3,
        )

        rejected = temp / "inputs-rejected"
        shutil.copytree(INPUTS, rejected)
        records = json.loads((rejected / "approval.json").read_text(encoding="utf-8"))
        records[0]["decision"] = "reject"
        (rejected / "approval.json").write_text(
            json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        # 依据：条款：D6-4.3-MUSTSEE（人类拒绝即违规）
        check(
            "签字拒绝 → 1",
            pm_check.main(
                ["--procedure", str(ROOT / "runtime/procedures/schedule_baseline.json"), "--inputs", str(rejected), "--config", str(CONFIG), "--lock", str(LOCK), "--out-dir", str(temp / "out-rj")]
            ),
            1,
        )

        unknown_op = mutate(
            ROOT / "runtime/procedures/schedule_baseline.json",
            temp / "procedure-unknown-op.json",
            lambda body: body["steps"][1].__setitem__("op", "summon"),
        )
        # 依据：条款：D6-4.3-OPS（闭集之外的算子即 procedure_invalid）
        check(
            "算子越界 → 2",
            pm_check.main(["--procedure", str(unknown_op), "--inputs", str(INPUTS), "--config", str(CONFIG), "--lock", str(LOCK)]),
            2,
        )

        skipped = mutate(
            ROOT / "runtime/procedures/schedule_baseline.json",
            temp / "procedure-skip.json",
            lambda body: body["steps"][2].__setitem__("needs", ["S9"]),
        )
        # 依据：条款：D6-4.3-OPS（工序步骤顺序与依赖）
        check(
            "跳步/乱序 → 2",
            pm_check.main(["--procedure", str(skipped), "--inputs", str(INPUTS), "--config", str(CONFIG), "--lock", str(LOCK)]),
            2,
        )

        print("[契约派生回归：外复核 10 条]")
        # 依据：条款：D6-8.3-RG07（预算汇总 CAP-19）；批次 0096 外复核阻断 1：上卷后每个父节点都必须拿到完整子树，总数相等不够。
        cfg3 = copy.deepcopy(state.config)
        cfg3["CFG-15"] = {
            "accounts": [
                {"code": "A"},
                {"code": "B", "parent_code": "A"},
                {"code": "C", "parent_code": "B"},
            ]
        }
        budget_data = {
            "currency": "CNY",
            "work_packages": [
                {
                    "id": "W1",
                    "wbs_ref": "N1",
                    "account_code": "C",
                    "amount": 100,
                    "periods": [{"period": "2026-01", "amount": 100}],
                }
            ],
        }
        rollup3 = pm_caps.compute_budget(budget_data, cfg3)
        check(
            "三级科目逐节点上卷",
            rollup3["by_account"],
            {"A": 100.0, "B": 100.0, "C": 100.0},
        )
        check(
            "三级科目逐节点核验",
            [item["status"] for item in pm_caps._check_budget_total(budget_data, {"config": cfg3, "artifacts": {}})],
            ["pass"],
        )

        # 依据：条款：T-F-015-EXIT（输入/配置/工序不合法 = 2；
        # 无法机械判定 = 3）与 `GLOSSARY.md` T-F-015。
        def procedure(name: str, steps: list[dict]) -> Path:
            path = temp / name
            write(path, {"procedure": name, "version": 1, "steps": steps})
            return path

        missing_slot = procedure(
            "procedure-missing-slot.json",
            [{"id": "S1", "op": "compute", "method": "audit.append", "inputs": ["nope"], "slot": "x", "record": {}}],
        )
        check(
            "缺槽位 → 2",
            pm_check.main(["--procedure", str(missing_slot), "--inputs", str(INPUTS), "--config", str(CONFIG), "--lock", str(LOCK)]),
            2,
        )

        wrong_decl = procedure(
            "procedure-wrong-schema.json",
            [{"id": "S1", "op": "fill_schema", "schema": "audit-trail", "input": "schedule.json", "slot": "a", "fails": "block"}],
        )
        check(
            "工件类型与声明不符 → 2",
            pm_check.main(["--procedure", str(wrong_decl), "--inputs", str(INPUTS), "--config", str(CONFIG), "--lock", str(LOCK)]),
            2,
        )

        render_only = procedure(
            "procedure-render.json",
            [
                {"id": "S1", "op": "fill_schema", "schema": "audit-trail", "input": "audit.json", "slot": "a", "fails": "block"},
                {"id": "S2", "op": "render", "template": "audit_review.md", "input": "a", "out": "x.md", "needs": ["S1"]},
            ],
        )
        check(
            "render 缺 --out-dir → 2",
            pm_check.main(["--procedure", str(render_only), "--inputs", str(INPUTS), "--config", str(CONFIG), "--lock", str(LOCK)]),
            2,
        )

        array_artifact = temp / "artifact-array.json"
        array_artifact.write_text('[{"gate": "GATE-AUDIT"}]', encoding="utf-8")
        check(
            "非对象工件 → 2",
            pm_check.main(["--artifact", str(array_artifact), "--config", str(CONFIG), "--lock", str(LOCK)]),
            2,
        )

        deep_artifact = temp / "artifact-deep.json"
        deep_artifact.write_text("[" * 4000 + "]" * 4000, encoding="utf-8")
        check(
            "深嵌套 JSON → 2",
            pm_check.main(["--artifact", str(deep_artifact), "--config", str(CONFIG), "--lock", str(LOCK)]),
            2,
        )

        gate_only = procedure(
            "procedure-gate.json",
            [{"id": "S1", "op": "human_approve", "gate": "GATE-AUDIT", "must_see": ["S1"]}],
        )
        check(
            "无 --config 的人审关口 → 3",
            pm_check.main(["--procedure", str(gate_only), "--inputs", str(INPUTS)]),
            3,
        )

        # 依据：条款：D6-9.3-DRIFT、D6-9.3-CANNOT（配置 finding 随判定出具；
        # 9.3 第二列“阻断”）与批次 0096 外复核严重 3。
        drift_artifact = mutate(
            INPUTS / "schedule.json",
            temp / "schedule-drift.json",
            lambda body: body["config_ref"].__setitem__("config_digest", "sha256:" + "0" * 64),
        )
        drift_result = pm_check.validate_artifact(read(drift_artifact), state)
        check("配置摘要漂移 → 1", drift_result["exit_code"], 1)
        check(
            "退 1 时 findings 含 config.*",
            any(item["check"].startswith("config.") for item in drift_result["findings"]),
            True,
        )

        # 依据：条款：D6-9.1-NO-DEFAULT、AG-1BIS-NOCONFIG（缺配置不得默认通过；未配置即 cannot_evaluate），
        # 以及 `AGENTS.md` 1bis“未配置即 cannot_evaluate，不得回落为通过”。
        check(
            "缺 --config 的工件 → 3",
            pm_check.main(["--artifact", str(INPUTS / "schedule.json")]),
            3,
        )

        # 依据：条款：D6-9.4-ITEM、D6-9.4-DIGEST（item_digests 用于诊断可比性）
        # 与 `AGENTS.md` 1bis“跨配置不得比较”。
        lock_body = copy.deepcopy(read(LOCK))
        first_key = sorted(lock_body["item_digests"])[0]
        lock_body["item_digests"][first_key] = "0" * 64
        tampered_lock = temp / "config-lock-tampered.json"
        write(tampered_lock, lock_body)
        tampered_state = pm_config.evaluate(CONFIG, tampered_lock)
        check("item_digests 篡改 → 1", tampered_state.exit_code, 1)
        check(
            "item_digests 篡改登记 config_drift",
            any(item.get("code") == "config_drift" for item in tampered_state.findings),
            True,
        )

        # 依据：条款：CFG-12-GATE（`runtime-config.schema.json` CFG-12 的 description）
        # “角色未解析则 blocked”与 `spec/D6_REBASELINE_PROPOSAL.md` 9.2 CFG-12 行。
        empty_gate = copy.deepcopy(state.config)
        empty_gate["CFG-12"] = {}
        empty_gate_path = temp / "config-empty-gate.json"
        write(empty_gate_path, {"schema_version": "config.schema/1", "config": empty_gate})
        check(
            "CFG-12 为空 → 3",
            pm_check.main(["--procedure", str(gate_only), "--inputs", str(INPUTS), "--config", str(empty_gate_path)]),
            3,
        )

        # 依据：条款：D6-4.3-XCHECKS（工件契约强制 x-checks）；render 越界的出处是 GAP_LEDGER.md 外复核派生条（批次 0096 严重 7），提案无此规定；render 的
        # `out` 必须相对 `--out-dir` 解析，不得写出输出目录。
        escape_proc = procedure(
            "procedure-render-escape.json",
            [
                {"id": "S1", "op": "fill_schema", "schema": "audit-trail", "input": "audit.json", "slot": "a", "fails": "block"},
                {"id": "S2", "op": "render", "template": "audit_review.md", "input": "a", "out": "/tmp/escape-test.md", "needs": ["S1"]},
            ],
        )
        check(
            "render.out 越出 out-dir → 2",
            pm_check.main(
                [
                    "--procedure",
                    str(escape_proc),
                    "--inputs",
                    str(INPUTS),
                    "--config",
                    str(CONFIG),
                    "--lock",
                    str(LOCK),
                    "--out-dir",
                    str(temp / "out-escape"),
                ]
            ),
            2,
        )

        # 依据：条款：D6-9.1-NO-DEFAULT、D6-9.2-DEFAULT（判定性项无默认）与 9.2 的
        # 依据：条款：CFG-03-JUDGE、CFG-13-JUDGE、D6-9.3-CANNOT、AG-1BIS-NOCONFIG（不设默认值）。
        no_metric = copy.deepcopy(state.config)
        no_metric["CFG-03"].pop("metric")
        check(
            "CFG-03.metric 缺失 → cannot_evaluate",
            pm_caps.compute_deviation(
                {"measurements": [{"period": "P1", "pv": 100, "ev": 80, "ac": 90}]}, no_metric
            )["status"],
            "cannot_evaluate",
        )
        percent_cfg = copy.deepcopy(state.config)
        percent_cfg["CFG-13"] = {"rule": "percent_complete"}
        check(
            "percent_complete 缺失 → cannot_evaluate",
            [
                item["status"]
                for item in pm_caps.run_checks(
                    ["evm.ev_measurement"],
                    {
                        "work_packages": [{"id": "W1", "budget": 100, "status": "in_progress"}],
                        "measurements": [{"period": "P1", "pv": 100, "ev": 0, "ac": 0}],
                    },
                    {"config": percent_cfg, "artifacts": {}},
                )
            ],
            ["cannot_evaluate"],
        )
        no_workdays = copy.deepcopy(state.config)
        no_workdays["CFG-08"].pop("workdays")
        workdays_error = ""
        try:
            pm_config.sample_points("2026-01-05", "2026-01-07", no_workdays)
        except RuntimeError as exc:
            workdays_error = str(exc)
        check("CFG-08.workdays 缺失即拒绝", "workdays" in workdays_error, True)

        # 依据：条款：CFG-04-JUDGE、CFG-06-EXPLICIT（采样口径与基准必须显式，不能由实现猜）
        # 与 9.3；两种采样模式共用同一配置口径。
        sample_cfg = copy.deepcopy(state.config)
        sample_cfg["CFG-04"] = "calendar_day"
        sample_cfg["CFG-07"] = {"unit": "day", "n": 1}
        sample_cfg["CFG-06"] = "workday"
        workday_points = [point["at"][:10] for point in pm_config.sample_points("2026-01-05", "2026-01-11", sample_cfg)["points"]]
        sample_cfg["CFG-06"] = "calendar"
        calendar_points = [point["at"][:10] for point in pm_config.sample_points("2026-01-05", "2026-01-11", sample_cfg)["points"]]
        check(
            "固定间隔按 workday 排除周末",
            workday_points,
            ["2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08", "2026-01-09"],
        )
        check(
            "固定间隔按 calendar 不排除",
            calendar_points,
            ["2026-01-05", "2026-01-06", "2026-01-07", "2026-01-08", "2026-01-09", "2026-01-10", "2026-01-11"],
        )
        sample_cfg.pop("CFG-06")
        basis_error = ""
        try:
            pm_config.sample_points("2026-01-05", "2026-01-07", sample_cfg)
        except RuntimeError as exc:
            basis_error = str(exc)
        check("固定间隔缺 CFG-06 即拒绝", "CFG-06" in basis_error, True)

        # 依据：条款：D6-4.3-XCHECKS（工件契约强制 x-checks）与 `pm_schema.py`
        # 文件头“关键字闭集”：未实现关键字出现在任何分支都必须拒绝。
        keyword_errors = []
        for schema in (
            {"type": "object", "properties": {"x": {"type": "string", "format": "email"}}},
            {"type": "array", "items": {"type": "string", "format": "email"}},
        ):
            try:
                pm_schema.validate({}, schema)
            except pm_schema.SchemaError:
                keyword_errors.append(True)
            else:
                keyword_errors.append(False)
        check("未实现关键字在任意分支均拒绝", keyword_errors, [True, True])

        # 依据：条款：D6-9.4-DIGEST、D6-9.4-ITEM（逐项摘要用于可比性）与
        # 批次 0097 外复核一：整体摘要之外，逐项摘要的单条/缺项/加塞/换序都必须拦。
        base_items = read(INPUTS / "schedule.json")["config_ref"]["item_digests"]
        items_cases = {
            "单条篡改": dict(
                base_items,
                **{sorted(base_items)[0]: "0" * 64},
            ),
            "删除一条": {key: base_items[key] for key in sorted(base_items)[1:]},
            "新增一条": dict(base_items, **{"CFG-99": "0" * 64}),
            "调换顺序": dict(reversed(list(base_items.items()))),
        }
        expected_items_codes = {
            "单条篡改": 1,
            "删除一条": 1,
            "新增一条": 2,
            "调换顺序": 1,
        }
        for label, items in items_cases.items():
            artifact = mutate(
                INPUTS / "schedule.json",
                temp / f"schedule-items-{label}.json",
                lambda body, value=items: body["config_ref"].__setitem__("item_digests", value),
            )
            check(
                f"工件逐项摘要{label} → {expected_items_codes[label]}",
                pm_check.validate_artifact(read(artifact), state)["exit_code"],
                expected_items_codes[label],
            )

        # 依据：条款：D6-4.3-OPS（render 属闭集算子）；模板不可读属解释器资源问题（4），路径越界属输入不合法（2），出处为 GAP_LEDGER.md 外复核派生条；
        # 模板路径越出模板目录属输入不合法（2）。
        template_root = temp / "templates"
        template_root.mkdir()
        (template_root / "bad.md").write_bytes(b"\xff\xfe\x00")
        (template_root / "ok.md").write_text("{{payload}}", encoding="utf-8")
        original_template_dir = pm_check.TEMPLATE_DIR
        pm_check.TEMPLATE_DIR = template_root
        try:
            render_proc = procedure(
                "procedure-template.json",
                [{"id": "S1", "op": "render", "template": "bad.md", "input": "audit.json", "out": "x.md"}],
            )
            check(
                "非 UTF-8 模板 → 4",
                pm_check.main(
                    [
                        "--procedure",
                        str(render_proc),
                        "--inputs",
                        str(INPUTS),
                        "--config",
                        str(CONFIG),
                        "--lock",
                        str(LOCK),
                        "--out-dir",
                        str(temp / "out-template"),
                    ]
                ),
                4,
            )
            for label, name in (
                ("绝对路径", str(template_root / "ok.md")),
                ("上跳目录", "../ok.md"),
            ):
                render_proc.write_text(
                    json.dumps(
                        {
                            "procedure": "procedure-template",
                            "version": 1,
                            "steps": [
                                {
                                    "id": "S1",
                                    "op": "render",
                                    "template": name,
                                    "input": "audit.json",
                                    "out": "x.md",
                                }
                            ],
                        }
                    ),
                    encoding="utf-8",
                )
                check(
                    f"模板{label} → 2",
                    pm_check.main(
                        [
                            "--procedure",
                            str(render_proc),
                            "--inputs",
                            str(INPUTS),
                            "--config",
                            str(CONFIG),
                            "--lock",
                            str(LOCK),
                            "--out-dir",
                            str(temp / "out-template"),
                        ]
                    ),
                    2,
                )
        finally:
            pm_check.TEMPLATE_DIR = original_template_dir

        # 依据：条款：D6-9.1-NO-DEFAULT、D6-9.2-DEFAULT、D6-8.3-RG10（判定性项无默认；偏差阈值 CAP-16）与 9.2
        # CFG-01/CFG-03/CFG-13 行；批次 0097 外复核三。
        lagless = read(INPUTS / "schedule.json")
        for dep in lagless["data"]["dependencies"]:
            dep.pop("lag", None)
        check(
            "依赖缺 lag → cannot_evaluate",
            pm_caps.compute_cpm(lagless["data"])["status"],
            "cannot_evaluate",
        )
        no_dimension_cfg = {key: value for key, value in state.config.items() if key != "CFG-01"}
        check(
            "缺 CFG-01 的 deviation.dimensions → cannot_evaluate",
            [
                item["status"]
                for item in pm_caps.run_checks(
                    ["deviation.dimensions"],
                    {"work_packages": []},
                    {"config": no_dimension_cfg, "artifacts": {}},
                )
            ],
            ["cannot_evaluate"],
        )
        no_metric_cfg = {key: value for key, value in state.config.items() if key != "CFG-03"}
        check(
            "缺 CFG-03 的 deviation.custom_metric → cannot_evaluate",
            [
                item["status"]
                for item in pm_caps.run_checks(
                    ["deviation.custom_metric"],
                    {"work_packages": []},
                    {"config": no_metric_cfg, "artifacts": {}},
                )
            ],
            ["cannot_evaluate"],
        )
        empty_rule, empty_reason = pm_caps._ev_rule({"CFG-13": {}})
        check("CFG-13 缺 rule → 无规则且有理由", (empty_rule, bool(empty_reason)), (None, True))

        print("[解释器不可用]")
        original = pm_check.ARTIFACT_DIR
        pm_check.ARTIFACT_DIR = Path("/nonexistent/artifacts")
        try:
            code = pm_check.main(["--artifact", str(INPUTS / "schedule.json")])
        finally:
            pm_check.ARTIFACT_DIR = original
        check("契约目录缺失 → 4", code, 4)

        print("[可复现性]")
        digest_a = pm_caps.compute_cpm(read(INPUTS / "schedule.json")["data"])
        digest_b = pm_caps.compute_cpm(read(INPUTS / "schedule.json")["data"])
        check("CPM 两次结果一致", digest_a, digest_b)
        check(
            "EAC 三法显式",
            pm_caps.compute_evm({**read(INPUTS / "evm.json")["data"], "eac_method": "cpi_spi"}, state.config)["status"],
            "pass",
        )
    finally:
        shutil.rmtree(temp, ignore_errors=True)

    print(f"\n通过 {PASSED} 项；失败 {len(FAILED)} 项")
    if FAILED:
        for item in FAILED:
            print(f" - {item}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
