#!/usr/bin/env python3
"""配置层错误分类、配置摘要与配置 schema 自检（批次 0083）。

本模块只固定**分类与退出码**，不执行配置求值（求值属下一批的解释器）。
依据：`spec/D6_REBASELINE_PROPOSAL.md` 9.1（四条安全边界）、9.2（13 项配置，另有责任方批次 0084 裁定的 CFG-14/CFG-15，共 15 项）、
9.3（缺失与非法值）、9.4（配置快照与可比性）。

四类配置结果与退出码：

| 类别 | 含义 | 退出码 |
|---|---|---|
| `cannot_evaluate` | 判定性配置项缺失或无法判定 | 3 |
| `config_invalid` | 类型错误、取值越界/越界枚举、lock 含未注册项摘要、判定性项进入 `defaulted` | 2 |
| `config_incomplete` | 项存在但相互矛盾（如 CFG-04=milestone_fraction 而 CFG-05 缺失） | 2 |
| `config_drift` | 配置实例与 `config.lock.json` 摘要不一致 | 1 |

这些类别与既有 `0` 通过 / `1` 违规 / `2` 输入不合法 / `3` 无法机械判定 的语义
一致，检查器按退出码即可分流，不需要理解配置细节。

用法：
  python3 scripts/config_codes.py --self-check
  python3 scripts/config_codes.py --classify config_incomplete
  python3 scripts/config_codes.py --digest <project>/config.json
退出码：0 自检通过；1 配置 schema 违反设计约束；2 文件缺失或不可解析。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA_PATH = Path("contracts/schema/runtime-config.schema.json")
LOCK_SCHEMA_PATH = Path("contracts/schema/runtime-config-lock.schema.json")
SCHEMA_VERSION = "config.schema/1"
CONFIG_KEY_PATTERN = "^CFG-(0[1-9]|1[0-5])$"

# 四类归属（9.1）。只有 project_parameter 能出现在 config.json：
# 判据、验收参数与能力开关分别由 ADR、验收装置与技能级开关承载。
CLASSES = (
    "project_parameter",
    "skill_criterion",
    "acceptance_parameter",
    "capability_switch",
)
PRESENT_CLASS = "project_parameter"

# 缺失时的三种语义：判定性缺失不可判定；非判定性取默认；
# 人审关口缺失等价于“不额外放宽”（mandatory gate 仍全量启用）。
ABSENT_BEHAVIORS = ("cannot_evaluate", "use_default", "conservative_no_relaxation")

EXIT_OK = 0
EXIT_CONFIG_DRIFT = 1
EXIT_CONFIG_INVALID = 2
EXIT_CONFIG_INCOMPLETE = 2
EXIT_CANNOT_EVALUATE = 3

ERROR_CLASSES = (
    "cannot_evaluate",
    "config_invalid",
    "config_incomplete",
    "config_drift",
)
EXIT_BY_CLASS = {
    "cannot_evaluate": EXIT_CANNOT_EVALUATE,
    "config_invalid": EXIT_CONFIG_INVALID,
    "config_incomplete": EXIT_CONFIG_INCOMPLETE,
    "config_drift": EXIT_CONFIG_DRIFT,
}
MEANING_BY_CLASS = {
    "cannot_evaluate": "判定性配置项缺失或无法判定；不得回落为通过",
    "config_invalid": "类型错误、取值越界、lock 含未注册项摘要，或判定性项进入 defaulted",
    "config_incomplete": "配置项存在但相互矛盾（如采样口径与采样集不匹配）",
    "config_drift": "配置实例与 config.lock.json 的摘要不一致，阻断判定",
}

# 安全边界 B3 的机械落点：没有任何字段可以关闭检查。
# 只要 schema 中出现这些词干命名的属性，即视为提供了“关闭开关”。
OFF_SWITCH = re.compile(
    r"(?i)(disable|enable|skip|ignore|waive|bypass|toggle|turn_?off)"
)

CFG_IDS = tuple(f"CFG-{index:02d}" for index in range(1, 16))
# 仅这两项是非判定性项，允许有默认值；其余一律判定性、无默认。
NON_JUDGMENTAL = ("CFG-10", "CFG-11")
JUDGMENTAL = tuple(key for key in CFG_IDS if key not in NON_JUDGMENTAL)
JUDGMENTAL_REQUIRED = ("CFG-01", "CFG-02", "CFG-03", "CFG-04", "CFG-09")
# 条件必填的判定性项：CFG-15 在按 cost_account 分档/汇总时必填；
# CFG-14 的触发条件在任务卡（是否执行风险方法），不在配置内部，故无结构规则。
JUDGMENTAL_CONDITIONAL = ("CFG-05", "CFG-06", "CFG-07", "CFG-08", "CFG-13", "CFG-14", "CFG-15")

COMMENT_KEYS = ("cfg", "class", "defaultable", "absent")


class ConfigError(Exception):
    """带分类的配置错误。`code` 必须是 `ERROR_CLASSES` 之一。"""

    def __init__(self, code: str, detail: str = ""):
        if code not in EXIT_BY_CLASS:
            raise ValueError(f"未登记的配置错误类别：{code}")
        super().__init__(detail or code)
        self.code = code
        self.detail = detail

    @property
    def exit_code(self) -> int:
        return EXIT_BY_CLASS[self.code]


def classify(code: str) -> int:
    """把配置错误类别映射为退出码；未知类别按“输入不合法”处理。"""
    return EXIT_BY_CLASS.get(code, EXIT_CONFIG_INVALID)


def canonical_bytes(value: object) -> bytes:
    """规范化 JSON：键排序、无多余空白、保留非 ASCII，用于摘要计算。"""
    return json.dumps(
        value, sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")


def item_digest(value: object) -> str:
    """单个配置项的摘要（64 位小写十六进制，不含前缀）。"""
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def config_digest(config: object) -> str:
    """全量配置的摘要，形态为 `sha256:<64 位小写十六进制>`。"""
    return "sha256:" + hashlib.sha256(canonical_bytes(config)).hexdigest()


def build_snapshot(config: dict, defaulted: tuple[str, ...] = ()) -> dict:
    """生成工件与判定记录里携带的配置快照（9.4）。"""
    items = {
        key: item_digest(value)
        for key, value in sorted(config.items())
        if key in CFG_IDS
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "config_digest": config_digest(config),
        "item_digests": items,
        "defaulted": sorted(defaulted),
    }


def parse_comment(text: str) -> dict:
    """解析 `$comment` 里的 `k=v` 元数据；未出现的键不出现在结果中。"""
    meta = {}
    for chunk in str(text).split(";"):
        if "=" not in chunk:
            continue
        key, value = chunk.split("=", 1)
        meta[key.strip()] = value.strip()
    return meta


def _iter_properties(schema: dict):
    """递归产出 (属性名, 子 schema)，覆盖 properties 之外的分支。

    `items`、`if`/`then`/`else`、`additionalProperties`、`anyOf`/`oneOf` 里同样可能
    藏有属性名或嵌套对象，只扫 properties 会漏掉“关闭开关”与未封闭对象。
    """
    if not isinstance(schema, dict):
        return
    properties = schema.get("properties")
    if isinstance(properties, dict):
        for name, subschema in properties.items():
            yield name, subschema
            yield from _iter_properties(subschema)
    items = schema.get("items")
    if isinstance(items, dict):
        yield from _iter_properties(items)
    for keyword in ("if", "then", "else", "additionalProperties"):
        child = schema.get(keyword)
        if isinstance(child, dict):
            yield from _iter_properties(child)
    for keyword in ("allOf", "anyOf", "oneOf"):
        for subschema in schema.get(keyword, []):
            yield from _iter_properties(subschema)
    for subschema in schema.get("$defs", {}).values():
        yield from _iter_properties(subschema)


def _has_default(schema: dict) -> bool:
    if not isinstance(schema, dict):
        return False
    if "default" in schema:
        return True
    return any(_has_default(child) for child in schema.values())


TYPE_CHECKS = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
}


def _value_errors(value: object, schema: dict, path: str) -> list[tuple[str, str]]:
    """按 schema 的 type/enum/required/范围校验单个值，返回 (类别, 说明) 清单。

    类别只有两种：`missing` 是判定性必填子字段缺失（对应 cannot_evaluate，
    退出码 3，不得回落为通过）；`invalid` 是类型错误、未注册字段或取值越界
    （对应 config_invalid，退出码 2）。只覆盖 config 用到的关键字。
    """
    errors: list[tuple[str, str]] = []
    if not isinstance(schema, dict):
        return errors
    expected = schema.get("type")
    if expected in TYPE_CHECKS:
        wanted = TYPE_CHECKS[expected]
        bad = not isinstance(value, wanted) or (
            expected in ("integer", "number") and isinstance(value, bool)
        )
        if bad:
            errors.append(("invalid", f"{path} 应为 {expected}，实得 {type(value).__name__}"))
            return errors
    if "enum" in schema:
        try:
            if value not in schema["enum"]:
                errors.append(("invalid", f"{path} 不在允许取值 {schema['enum']} 内"))
        except TypeError:
            errors.append(("invalid", f"{path} 的类型不可与枚举比较"))
    if "const" in schema and value != schema["const"]:
        errors.append(("invalid", f"{path} 必须为 {schema['const']!r}"))
    if expected == "object" and isinstance(value, dict):
        for name in schema.get("required", []):
            if name not in value:
                errors.append(("missing", f"{path}.{name} 缺失"))
        children = schema.get("properties", {})
        for name, child_value in value.items():
            if name in children:
                errors.extend(_value_errors(child_value, children[name], f"{path}.{name}"))
            elif schema.get("additionalProperties") is False:
                errors.append(("invalid", f"{path}.{name} 是未注册字段"))
    if expected == "array" and isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            errors.append(("invalid", f"{path} 至少 {schema['minItems']} 项，实得 {len(value)}"))
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            errors.append(("invalid", f"{path} 至多 {schema['maxItems']} 项，实得 {len(value)}"))
        if isinstance(schema.get("items"), dict):
            for index, item in enumerate(value):
                errors.extend(_value_errors(item, schema["items"], f"{path}[{index}]"))
    if isinstance(value, str):
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(("invalid", f"{path} 长度超过 {schema['maxLength']}"))
        if "pattern" in schema and re.fullmatch(schema["pattern"], value) is None:
            errors.append(("invalid", f"{path} 不匹配 {schema['pattern']}"))
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(("invalid", f"{path} 小于下限 {schema['minimum']}"))
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(("invalid", f"{path} 大于上限 {schema['maximum']}"))
    return errors


def policy_errors(schema: dict) -> list[str]:
    """核验四条设计约束在 schema 中的机械落点。返回错误清单。"""
    errors: list[str] = []

    if schema.get("type") != "object" or schema.get("additionalProperties") is not False:
        errors.append("顶层必须是 additionalProperties=false 的对象")

    config = schema.get("properties", {}).get("config")
    if not isinstance(config, dict):
        errors.append("缺少 properties.config")
        return errors

    if config.get("additionalProperties") is not False:
        errors.append("config 必须是 additionalProperties=false 的对象")
    pattern = config.get("propertyNames", {}).get("pattern")
    if pattern != CONFIG_KEY_PATTERN:
        errors.append(f"config 的 propertyNames.pattern 必须是 {CONFIG_KEY_PATTERN}")

    properties = config.get("properties", {})
    if sorted(properties) != sorted(CFG_IDS):
        errors.append(
            f"config.properties 必须恰好覆盖 CFG-01～{CFG_IDS[-1]}；实得 {sorted(properties)}"
        )

    required = config.get("required", [])
    missing_required = [key for key in JUDGMENTAL_REQUIRED if key not in required]
    if missing_required:
        errors.append(f"判定性必填项未列入 required：{missing_required}")

    # 约束一：四类归属可区分。本文件只承载项目参数，另三类必须被具名排除。
    top_comment = parse_comment(schema.get("$comment", ""))
    declared_classes = set(filter(None, top_comment.get("classes", "").split("|")))
    for name in CLASSES:
        if name not in declared_classes:
            errors.append(f"顶层 $comment 未声明归属类别：{name}")
    if top_comment.get("present_class") != PRESENT_CLASS:
        errors.append(f"顶层 $comment 的 present_class 必须是 {PRESENT_CLASS}")

    for key in sorted(properties):
        subschema = properties[key]
        meta = parse_comment(subschema.get("$comment", ""))
        for field in COMMENT_KEYS:
            if field not in meta:
                errors.append(f"{key}：$comment 缺少 {field}=")
        if meta.get("cfg") != key:
            errors.append(f"{key}：$comment 的 cfg={meta.get('cfg')} 与键名不一致")
        if meta.get("class") not in CLASSES:
            errors.append(f"{key}：class={meta.get('class')} 不在四类归属内")
        elif meta["class"] != PRESENT_CLASS:
            errors.append(
                f"{key}：class={meta['class']} 不能写进项目配置文件"
                "（判据/验收参数/能力开关各有承载位置）"
            )
        if meta.get("defaultable") not in ("true", "false"):
            errors.append(f"{key}：defaultable 必须是 true 或 false")
        if meta.get("absent") not in ABSENT_BEHAVIORS:
            errors.append(
                f"{key}：absent={meta.get('absent')} 不在 {list(ABSENT_BEHAVIORS)}"
            )

        # 约束二：只有非判定性项有默认值；判定性项一律无默认（含任何子字段）。
        if meta.get("defaultable") == "true":
            if not _has_default(subschema):
                errors.append(f"{key}：defaultable=true 但没有任何 default")
            if key not in NON_JUDGMENTAL:
                errors.append(f"{key}：只有 {list(NON_JUDGMENTAL)} 允许 defaultable=true")
        elif _has_default(subschema):
            errors.append(
                f"{key}：判定性项不得有任何 default（含子字段）；"
                "缺该项即 cannot_evaluate，不取默认"
            )
        if meta.get("absent") == "use_default" and meta.get("defaultable") != "true":
            errors.append(f"{key}：absent=use_default 要求 defaultable=true")

        if subschema.get("type") == "object" and "additionalProperties" not in subschema:
            errors.append(f"{key}：对象必须显式声明 additionalProperties")

    # 约束三：不得关闭检查——无关闭开关字段，且每层对象封闭。
    for name, subschema in _iter_properties(schema):
        if OFF_SWITCH.search(name):
            errors.append(f"属性 {name} 形似关闭开关；配置只能调严或调宽，不得关闭检查")
        if isinstance(subschema, dict) and subschema.get("type") == "object":
            if "additionalProperties" not in subschema:
                errors.append(f"属性 {name}：对象必须显式声明 additionalProperties")

    # 约束四：配置不可改变工件必填字段集合——本 schema 不得注入 required 到工件。
    for name, _ in _iter_properties(schema):
        if name in ("required_fields", "mandatory_fields", "artifact_required"):
            errors.append(f"属性 {name} 试图改写工件必填字段集合")

    return errors


def lock_policy_errors(schema: dict) -> list[str]:
    """核验 lock schema 是否覆盖 9.4 要求的五个字段与摘要形态。"""
    errors: list[str] = []
    required = set(schema.get("required", []))
    for field in ("schema_version", "config_digest", "item_digests", "defaulted", "history"):
        if field not in required:
            errors.append(f"config.lock 缺少必填字段 {field}")
    digest = schema.get("properties", {}).get("config_digest", {})
    if digest.get("pattern") != "^sha256:[0-9a-f]{64}$":
        errors.append("config_digest 必须约束为 sha256:<64 位小写十六进制>")
    items = schema.get("properties", {}).get("item_digests", {})
    if items.get("propertyNames", {}).get("pattern") != CONFIG_KEY_PATTERN:
        errors.append(f"item_digests 的键必须约束为 CFG-01～{CFG_IDS[-1]}")

    # defaulted 只允许列出非判定性项：判定性项被塞进该列表意味着“缺项按默认值放行”，
    # 与 absent=cannot_evaluate 直接冲突，必须在 schema 层就堵死。
    defaulted = schema.get("properties", {}).get("defaulted", {})
    allowed = (defaulted.get("items") or {}).get("enum")
    if allowed != list(NON_JUDGMENTAL):
        errors.append(
            f"defaulted 的允许取值必须恰为 {list(NON_JUDGMENTAL)}（只有非判定性项可默认）；实得 {allowed}"
        )
    if defaulted.get("maxItems") != len(NON_JUDGMENTAL):
        errors.append(
            f"defaulted 的 maxItems 必须为 {len(NON_JUDGMENTAL)}；实得 {defaulted.get('maxItems')}"
        )
    if schema.get("additionalProperties") is not False:
        errors.append("config.lock 顶层必须 additionalProperties=false")
    for name, subschema in _iter_properties(schema):
        if OFF_SWITCH.search(name):
            errors.append(f"属性 {name} 形似关闭开关")
        if isinstance(subschema, dict) and subschema.get("type") == "object":
            if "additionalProperties" not in subschema:
                errors.append(f"属性 {name}：对象必须显式声明 additionalProperties")
    return errors


# 结构层面的分类只回答“能不能开始判定”，不产出任何判定结论。
PRECEDENCE = ("config_invalid", "config_incomplete", "config_drift", "cannot_evaluate")


def config_findings(
    config: dict, lock: dict | None = None, schema: dict | None = None
) -> list[dict]:
    """对配置实例做结构分类，返回带类别与退出码的发现清单。

    不做配置求值：不解释阈值、不采样、不判定工件。它只区分四类情形——
    未注册键、类型错误、取值越界（config_invalid）、跨项矛盾
    （config_incomplete）、摘要漂移（config_drift）与判定性项缺失
    （cannot_evaluate）。`schema` 用于逐项校验取值形状；`lock` 用于核对摘要。
    """
    findings: list[dict] = []
    if not isinstance(config, dict):
        return [{"code": "config_invalid", "detail": "config 必须是对象"}]

    unknown = sorted(key for key in config if key not in CFG_IDS)
    if unknown:
        findings.append(
            {"code": "config_invalid", "detail": f"未注册配置项：{unknown}"}
        )

    # 类型错误与取值越界：按 schema 逐项校验已出现的键。
    # 判定性项的子字段缺失记 cannot_evaluate（缺项不取默认），其余记 config_invalid。
    if isinstance(schema, dict):
        children = schema.get("properties", {}).get("config", {}).get("properties", {})
        for key in sorted(config):
            subschema = children.get(key)
            if not isinstance(subschema, dict):
                continue
            for kind, message in _value_errors(config[key], subschema, f"config.{key}"):
                code = "cannot_evaluate" if kind == "missing" else "config_invalid"
                findings.append({"code": code, "detail": message})

    missing = [key for key in JUDGMENTAL_REQUIRED if key not in config]
    if missing:
        findings.append(
            {"code": "cannot_evaluate", "detail": f"判定性配置项缺失：{missing}"}
        )

    sampler = config.get("CFG-04")
    if sampler == "milestone_fraction":
        lacking = [key for key in ("CFG-05", "CFG-06") if key not in config]
    elif sampler in ("calendar_day", "week", "month", "hour"):
        lacking = [key for key in ("CFG-07",) if key not in config]
    else:
        lacking = []
    if lacking:
        findings.append(
            {
                "code": "config_incomplete",
                "detail": f"CFG-04={sampler} 时缺少 {lacking}",
            }
        )
    if sampler is not None and "CFG-08" not in config:
        findings.append(
            {"code": "cannot_evaluate", "detail": "涉及周期换算时缺少 CFG-08（项目日历）"}
        )

    bands = config.get("CFG-02")
    if isinstance(bands, dict):
        levels, labels = bands.get("levels"), bands.get("labels")
        if isinstance(levels, int) and isinstance(labels, list) and len(labels) != levels:
            findings.append(
                {
                    "code": "config_incomplete",
                    "detail": f"CFG-02 档数 {levels} 与标签数 {len(labels)} 不等长",
                }
            )

    boundaries = config.get("CFG-03")
    if isinstance(boundaries, dict) and boundaries.get("metric") == "custom":
        if not boundaries.get("custom_metric"):
            findings.append(
                {"code": "config_incomplete", "detail": "CFG-03.metric=custom 缺少 custom_metric"}
            )

    risk = config.get("CFG-14")
    if isinstance(risk, dict):
        expected = {"3x3": 3, "5x5": 5}.get(risk.get("scale"))
        if expected is not None:
            for field in ("probability_labels", "impact_labels"):
                labels = risk.get(field)
                if isinstance(labels, list) and len(labels) != expected:
                    findings.append(
                        {
                            "code": "config_incomplete",
                            "detail": f"CFG-14.scale={risk.get('scale')} 时 {field} 应为 {expected} 个标签，实得 {len(labels)}",
                        }
                    )

    dimensions = config.get("CFG-01")
    if isinstance(dimensions, list) and "cost_account" in dimensions:
        if "CFG-15" not in config:
            findings.append(
                {
                    "code": "config_incomplete",
                    "detail": "CFG-01 含 cost_account 但缺少 CFG-15（成本科目表）",
                }
            )

    if lock is not None:
        if not isinstance(lock, dict):
            findings.append(
                {"code": "config_invalid", "detail": "config.lock 必须是对象"}
            )
        else:
            digests = lock.get("item_digests")
            if isinstance(digests, dict):
                unregistered = sorted(key for key in digests if key not in CFG_IDS)
                if unregistered:
                    findings.append(
                        {
                            "code": "config_invalid",
                            "detail": f"config.lock 含未注册项摘要：{unregistered}",
                        }
                    )
            defaulted = lock.get("defaulted")
            if isinstance(defaulted, list):
                illegal = sorted({key for key in defaulted if key not in NON_JUDGMENTAL})
                if illegal:
                    findings.append(
                        {
                            "code": "config_invalid",
                            "detail": (
                                "config.lock 的 defaulted 含不允许默认的项："
                                f"{illegal}；只有 {list(NON_JUDGMENTAL)} 可默认"
                            ),
                        }
                    )
            expected = lock.get("config_digest")
            actual = config_digest(config)
            if expected != actual:
                findings.append(
                    {
                        "code": "config_drift",
                        "detail": f"config.lock 摘要不符：登记 {expected}，实得 {actual}",
                    }
                )

    for finding in findings:
        finding["exit_code"] = EXIT_BY_CLASS[finding["code"]]
    return findings


def overall_exit_code(findings: list[dict]) -> int:
    """按结构优先级取退出码：先结构非法，其次矛盾，再漂移，最后不可判定。"""
    present = {finding["code"] for finding in findings}
    for code in PRECEDENCE:
        if code in present:
            return EXIT_BY_CLASS[code]
    return EXIT_OK


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError("config_invalid", f"{path}：不可解析：{exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="配置层错误分类与配置摘要工具")
    parser.add_argument("--self-check", action="store_true", help="核验配置 schema 的设计约束")
    parser.add_argument("--schema", default=str(SCHEMA_PATH), help="配置实例 schema 路径")
    parser.add_argument("--lock-schema", default=str(LOCK_SCHEMA_PATH), help="配置 lock schema 路径")
    parser.add_argument("--classify", metavar="CLASS", help="输出该配置错误类别的退出码")
    parser.add_argument("--digest", metavar="CONFIG_JSON", help="输出配置实例的快照摘要")
    parser.add_argument("--check", metavar="CONFIG_JSON", help="对配置实例做结构分类（不求值）")
    parser.add_argument("--lock", metavar="LOCK_JSON", help="与 --check 配合，核对 config.lock 摘要")
    args = parser.parse_args(argv)

    if args.classify:
        if args.classify not in EXIT_BY_CLASS:
            print(f"[错误] 未登记的配置错误类别：{args.classify}；允许 {list(ERROR_CLASSES)}")
            return EXIT_CONFIG_INVALID
        print(f"{args.classify} → {EXIT_BY_CLASS[args.classify]}（{MEANING_BY_CLASS[args.classify]}）")
        return EXIT_OK

    if args.digest:
        try:
            data = _load_json(Path(args.digest))
        except ConfigError as exc:
            print(f"[错误] {exc.code}：{exc.detail}")
            return exc.exit_code
        config = data.get("config", data)
        print(json.dumps(build_snapshot(config), ensure_ascii=False, indent=2, sort_keys=True))
        return EXIT_OK

    if args.check:
        try:
            data = _load_json(Path(args.check))
            lock = _load_json(Path(args.lock)) if args.lock else None
        except ConfigError as exc:
            print(f"[错误] {exc.code}：{exc.detail}")
            return exc.exit_code
        schema_path = Path(args.schema)
        schema = None
        if schema_path.is_file():
            try:
                schema = _load_json(schema_path)
            except ConfigError as exc:
                print(f"[错误] {exc.code}：{exc.detail}")
                return exc.exit_code
        findings = config_findings(data.get("config", data), lock, schema)
        print(json.dumps(findings, ensure_ascii=False, indent=2, sort_keys=True))
        return overall_exit_code(findings)

    if not args.self_check:
        parser.print_help()
        return EXIT_CONFIG_INVALID

    try:
        schema = _load_json(Path(args.schema))
        lock_schema = _load_json(Path(args.lock_schema))
    except ConfigError as exc:
        print(f"[错误] {exc.code}：{exc.detail}")
        return exc.exit_code

    errors = policy_errors(schema) + lock_policy_errors(lock_schema)
    classes = " / ".join(f"{name}={EXIT_BY_CLASS[name]}" for name in ERROR_CLASSES)
    count = len(schema.get("properties", {}).get("config", {}).get("properties", {}))
    print(f"配置 schema 自检：{count} 项（CFG-01～{CFG_IDS[-1]}），类别 {classes}")
    if errors:
        for message in errors:
            print(f"[错误] {message}")
        print(f"[失败] {len(errors)} 项违反配置层设计约束")
        return EXIT_CONFIG_DRIFT
    print(
        "[通过] 四类归属可区分；"
        f"仅 {list(NON_JUDGMENTAL)} 有默认、其余 {len(JUDGMENTAL)} 项无默认；"
        "无关闭开关；摘要字段齐备"
    )
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
