#!/usr/bin/env python3
"""T-107 最小原型：按附录 A 判定列执行 A.1 的 60 个样例。

只使用标准库。输入为 spec/methods/deterministic-checker.md 中 A.1 的
YAML 谓词快照；输出 check_id / source_rule / severity / rule_status /
verdict / reason，并与样例的“期望输出”逐项比对。

判定依据是附录 A 的“判定”列与 A.2 子句表。ADR-0013 已把原 5 处“未覆盖
规则正文”全部纳入判定列，故 COVERAGE_GAPS 为空；G-004 通过 A.2 的子句
severity（G-E1#3 为 warn）承接，不再把合法产物按 block 判死。
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from itertools import permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
METHOD = Path("spec/methods/deterministic-checker.md")
SCHEMA = Path("spec/CHECKER_INPUT_SCHEMA.md")

# ---------------------------------------------------------------- 注册表常量

SPEC: dict[str, tuple[str, str, str]] = {
    "PROJECT_MINIMAL_EXISTENCE": ("G-A1", "block", "active"),
    "CONSTRAINT_ANCHOR_REQUIRED": ("G-A2", "block", "active"),
    "DELIVERABLE_ASSERTION_LINK": ("G-C1", "block", "active"),
    "CHANGE_CONSTRAINT_LINK": ("G-D1", "block", "active"),
    "ROLE_MINIMAL_COMPLETENESS": ("G-E1", "block", "active"),
    "DUAL_DIMENSION_ANNOTATION": ("G-B1", "advisory", "active"),
    "DIMENSION_VALUE_CLOSED": ("G-B2", "advisory", "active"),
    "ASSERTION_MUTUAL_EXCLUSION": ("G-C2", "warn", "active"),
    "ALL_IMPROVEMENT_ASSUMPTION": ("G-D2", "warn", "active"),
    "AI_AUTONOMY_DELEGATION_AUDITABLE": ("G-E2", "warn", "active"),
    "PROJECT_CHARTER_EXISTENCE": ("G-F1", "advisory", "assumption"),
    "CLOSURE_ACCEPTANCE_LINK": ("G-F2", "advisory", "assumption"),
    "PROCUREMENT_CONTRACT_ANCHOR": ("G-F3", "advisory", "assumption"),
    "SCHEDULE_EVIDENCE_LINK": ("G-F4", "advisory", "assumption"),
    "TAILORING_RECORD_EXISTENCE": ("G-G1", "advisory", "assumption"),
    "TAILORING_NON_TRIMMABLE_SET": ("G-G2", "advisory", "assumption"),
    "TAILORING_REASSESSMENT_CONDITION": ("G-G3", "advisory", "assumption"),
}

PROCESS_GROUPS = {
    "pre-project",
    "overseeing",
    "directing",
    "initiating",
    "controlling",
    "managing-delivery",
    "closing",
    "post-project",
}
# ISO 21502:2020 第 7 章 7.2–7.18 的 17 项管理实践，按 schema §4 完整物化。
# subject_group_extension 只用于领域特化，不再承担补全基础枚举的职责。
BASE_SUBJECT_GROUPS = {
    "planning",
    "benefits-management",
    "scope-management",
    "resources-management",
    "schedule-management",
    "cost-management",
    "risk-management",
    "issues-management",
    "change-control",
    "quality-management",
    "stakeholder-engagement",
    "communication-management",
    "organizational-and-societal-change",
    "reporting",
    "information-and-documentation-management",
    "procurement",
    "lessons-learned",
}
CHANGE_RELATIONS = {"mitigates", "exacerbates", "trades_off"}
EXTENSION_RELATIONS = {"specializes", "cross_cuts", "orthogonal_to"}
CHANGE_TARGET_TYPES = {"Commitment", "Deliverable"}
STATEMENT_KINDS = {"what", "state", "condition"}
ASSERTION_KINDS = {"fact", "assumption", "decision"}
NON_TRIMMABLE = {"G-A1", "G-A2", "G-C1", "G-D1", "G-E1"}
ACCEPTANCE_STATEMENTS = {"已验收", "已移交"}

# ADR-0013 已把原 5 处“未覆盖规则正文”全部纳入判定列，本表保持为空是
# 有意为之：原型不再存在“声明未覆盖但仍输出 pass”的暗区。
COVERAGE_GAPS: dict[str, str] = {}

# ---------------------------------------------------------------- schema 生成
# 输入域与引用规则只从 spec/CHECKER_INPUT_SCHEMA.md 派生，代码不保留第二份清单。
# §3 的“必需顶层键”列生成 REQUIRED_KEYS；§2bis.1 的标注表生成 REFERENCE_RULES。


def split_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def parse_required_keys(text: str) -> dict[str, tuple[str, ...]]:
    """从 schema §3 解析每个 check_id 的必需顶层键。"""
    required: dict[str, tuple[str, ...]] = {}
    in_section = False
    for line in text.splitlines():
        if line.startswith("## 3."):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        cells = split_row(line)
        if not cells or len(cells) < 2:
            continue
        match = re.fullmatch(r"`([A-Z_]+)`", cells[0])
        if not match:
            continue
        declared = cells[1].split("（可选")[0]
        required[match.group(1)] = tuple(
            re.findall(r"`([a-z][a-z0-9_]*)`", declared)
        )
    return required


def parse_reference_rules(text: str) -> list[dict]:
    """从 schema §2bis.1 解析引用字段标注，生成原型唯一的引用规则表。"""
    rules: list[dict] = []
    in_section = False
    for line in text.splitlines():
        if line.startswith("### 2bis.1"):
            in_section = True
            continue
        if line.startswith("### 2bis.2"):
            break
        if not in_section:
            continue
        cells = split_row(line)
        if not cells or len(cells) != 4 or not cells[0].startswith("`"):
            continue
        path = cells[0].strip("`")
        field = cells[1].strip("`")
        target_cell = cells[2].strip("`")
        form = cells[3].strip("`")
        if "→" in target_cell:
            targets: object = {}
            for part in re.split(r"[、,，]", target_cell):
                kind, collection = part.strip("` ").split("→")
                targets[kind.strip()] = collection.strip()
            form = "type"
        elif "∪" in target_cell:
            targets = [part.strip("` ") for part in target_cell.split("∪")]
        elif target_cell == "any":
            targets = ["*"]
        else:
            targets = [target_cell]
        rules.append({"path": path, "field": field, "targets": targets, "form": form})
    return rules


_SCHEMA_TEXT = (ROOT / SCHEMA).read_text(encoding="utf-8")
REQUIRED_KEYS = parse_required_keys(_SCHEMA_TEXT)
REFERENCE_RULES = parse_reference_rules(_SCHEMA_TEXT)

_METHOD_TEXT = (ROOT / METHOD).read_text(encoding="utf-8")


def parse_clauses(text: str) -> tuple[dict, dict, dict, dict]:
    """按 A.2 行序登记子句：索引、所属 check_id、severity、原因码。

    子句级结果是判定与覆盖闸门的共同依据：每条结果带 clause id，
    覆盖闸门据此判定“这条负例确实触发了声明的子句”，不再依赖共享 reason。
    """
    index: dict[str, int] = {}
    check_of: dict[str, str] = {}
    severity: dict[str, str] = {}
    reasons: dict[str, list[str]] = {}
    for line in text.splitlines():
        cells = split_row(line)
        if not cells or len(cells) < 8:
            continue
        if not (cells[0].startswith("`G-") and cells[0].endswith("`")):
            continue
        clause = cells[0].strip("`")
        index[clause] = len(index)
        check_of[clause] = cells[4].strip("`")
        severity[clause] = cells[5].strip("`")
        reasons[clause] = re.findall(r"[a-z][a-z0-9_]+", cells[3])
    return index, check_of, severity, reasons


CLAUSE_INDEX, CLAUSE_CHECK, CLAUSE_SEVERITY, CLAUSE_REASONS = parse_clauses(_METHOD_TEXT)


def clause_of(check_id: str, reason: str | None) -> str | None:
    """唯一可判定的原因码回退到子句；多子句共享原因码时返回 None（须显式带 clause）。"""
    if not reason:
        return None
    matches = [
        clause
        for clause, reasons in CLAUSE_REASONS.items()
        if CLAUSE_CHECK[clause] == check_id and reason in reasons
    ]
    return matches[0] if len(matches) == 1 else None


VERDICT_RANK = {"pass": 0, "cannot_evaluate": 1, "fail": 2}
SEVERITY_RANK = {"advisory": 0, "warn": 1, "block": 2}


def aggregate(
    check_id: str, results: list[tuple], default_severity: str
) -> tuple[str, str | None, str]:
    """顺序无关聚合：fail > cannot_evaluate > pass；reason 按 A.2 行序取首条。

    - verdict 取所有子句结论的最高级，与子句求值顺序无关；
    - reason 只在胜出 verdict 的子句里按 A.2 行序取首条，与输入顺序无关；
    - severity 取胜出子句在 A.2 登记的 severity 最高级，缺省用 check 的默认 severity。
    """
    if not results:
        return "pass", None, default_severity
    verdict = max((item[0] for item in results), key=lambda value: VERDICT_RANK[value])
    winners = [item for item in results if item[0] == verdict]
    enriched = []
    for item in winners:
        reason = item[1]
        clause = item[2] if len(item) > 2 else None
        clause = clause or clause_of(check_id, reason)
        order = CLAUSE_INDEX.get(clause, 10**6)
        enriched.append((order, reason, clause))
    enriched.sort(key=lambda item: (item[0], item[1] or ""))
    _, reason, clause = enriched[0]
    severities = [CLAUSE_SEVERITY[item[2]] for item in enriched if item[2]]
    severity = (
        max(severities, key=lambda value: SEVERITY_RANK[value])
        if severities
        else default_severity
    )
    return verdict, reason, severity


def failed_clauses(check_id: str, data: dict) -> list[str]:
    """返回该输入实际触发的子句 id（按 A.2 行序）。供覆盖闸门机械核对。"""
    violation = enum_violation(data)
    if violation and violation[1]:
        # 枚举在入口拦截，子句归属仍可判定（node_type → G-A2#2，relation → G-B2#2）。
        return [violation[1]]
    results = CHECKS[check_id](data)
    seen = []
    for item in results:
        clause = item[2] if len(item) > 2 else None
        clause = clause or clause_of(check_id, item[1])
        if clause and clause not in seen:
            seen.append(clause)
    seen.sort(key=lambda clause: CLAUSE_INDEX.get(clause, 10**6))
    return seen



def ids(items) -> set:
    return {item.get("id") for item in items if isinstance(item, dict)}


def resolve_path(data: dict, path: str) -> list[dict]:
    """按 schema §2bis 的路径语法取值；`[]` 表示逐元素展开。"""
    nodes: list[object] = [data]
    for segment in path.split("."):
        many = segment.endswith("[]")
        key = segment[:-2] if many else segment
        found: list[object] = []
        for node in nodes:
            if not isinstance(node, dict):
                continue
            value = node.get(key)
            if value is None:
                continue
            if many:
                if isinstance(value, list):
                    found.extend(item for item in value if isinstance(item, dict))
            elif isinstance(value, dict):
                found.append(value)
        nodes = found
    return [node for node in nodes if isinstance(node, dict)]


def target_ids_for(data: dict, collections) -> tuple[set, str | None]:
    """返回目标集合的 id 并集；目标集合缺失时返回缺失集合名。"""
    if collections == ["*"]:
        merged: set = set()
        for value in data.values():
            if isinstance(value, list):
                merged |= ids(value)
        return merged, None
    merged = set()
    for collection in collections:
        if collection not in data or data[collection] is None:
            return set(), collection
        merged |= ids(data[collection])
    return merged, None


def iter_rule_refs(data: dict, rule: dict):
    """逐个产出 (引用值列表, 目标集合列表)；空值不产出。"""
    for item in resolve_path(data, rule["path"]):
        ref = item.get(rule["field"])
        if ref in (None, "", []):
            continue
        refs = ref if isinstance(ref, list) else [ref]
        if rule["form"] == "type":
            target = rule["targets"].get(item.get("type"))
            if target is None:
                continue
            yield refs, [target]
        else:
            yield refs, rule["targets"]


def referenced_collections(data: dict) -> set[str]:
    """返回解析当前快照引用所需的全部目标集合（供输入域闭包检查使用）。"""
    needed: set[str] = set()
    for rule in REFERENCE_RULES:
        for _refs, collections in iter_rule_refs(data, rule):
            if collections == ["*"]:
                continue
            needed.update(collections)
    return needed


def validate_references(data: dict) -> tuple[str, str | None] | None:
    """全局引用完整性：按 schema §2bis 的标注逐字段解析引用。

    规则表由 schema 生成，代码不维护第二份字段清单。返回 None 表示无问题；
    目标集合缺失 → cannot_evaluate / missing_input；目标 id 不存在 →
    fail / dangling_reference。该检查在 check 返回 pass 时统一执行。
    """
    for rule in REFERENCE_RULES:
        for refs, collections in iter_rule_refs(data, rule):
            target_ids, missing = target_ids_for(data, collections)
            for ref_id in refs:
                if not isinstance(ref_id, str):
                    return "cannot_evaluate", "undefined_object_type"
                if missing:
                    return "cannot_evaluate", "missing_input"
                if ref_id not in target_ids:
                    return "fail", "dangling_reference"
    return None


# ---------------------------------------------------------------- YAML 子集解析
# 只覆盖 A.1 样例使用的构造：块映射、块序列、流映射/流序列、引号标量、
# null/true/false、空集合。不实现锚点、多文档、块标量等。


class YamlError(ValueError):
    pass


def _strip_comment(line: str) -> str:
    in_double = in_single = False
    for index, char in enumerate(line):
        if char == '"' and not in_single:
            in_double = not in_double
        elif char == "'" and not in_double:
            in_single = not in_single
        elif char == "#" and not in_double and not in_single:
            if index == 0 or line[index - 1].isspace():
                return line[:index].rstrip()
    return line.rstrip()


def _balanced(text: str) -> bool:
    depth = 0
    in_double = in_single = False
    for char in text:
        if char == '"' and not in_single:
            in_double = not in_double
        elif char == "'" and not in_double:
            in_single = not in_single
        elif not in_double and not in_single:
            if char in "[{":
                depth += 1
            elif char in "]}":
                depth -= 1
    return depth == 0


def _split_key(text: str) -> tuple[str, str]:
    in_double = in_single = False
    depth = 0
    for index, char in enumerate(text):
        if char == '"' and not in_single:
            in_double = not in_double
        elif char == "'" and not in_double:
            in_single = not in_single
        elif not in_double and not in_single:
            if char in "[{":
                depth += 1
            elif char in "]}":
                depth -= 1
            elif char == ":" and depth == 0:
                return text[:index].strip(), text[index + 1 :].strip()
    raise YamlError(f"无法解析键值行：{text!r}")


def _looks_like_mapping(text: str) -> bool:
    try:
        _split_key(text)
    except YamlError:
        return False
    return True


def _parse_quoted(text: str, pos: int) -> tuple[str, int]:
    quote = text[pos]
    pos += 1
    out: list[str] = []
    while pos < len(text):
        char = text[pos]
        if char == "\\" and quote == '"' and pos + 1 < len(text):
            out.append(text[pos + 1])
            pos += 2
            continue
        if char == quote:
            return "".join(out), pos + 1
        out.append(char)
        pos += 1
    raise YamlError(f"未闭合的引号：{text!r}")


def _parse_flow(text: str, pos: int = 0) -> tuple[object, int]:
    pos = _skip_space(text, pos)
    if pos >= len(text):
        raise YamlError("流式集合意外结束")
    if text[pos] == "{":
        obj: dict[str, object] = {}
        pos += 1
        while True:
            pos = _skip_space(text, pos)
            if pos < len(text) and text[pos] == "}":
                return obj, pos + 1
            key, pos = _parse_flow_scalar(text, pos)
            pos = _skip_space(text, pos)
            if pos >= len(text) or text[pos] != ":":
                raise YamlError(f"流式映射缺少冒号：{text!r}")
            value, pos = _parse_flow(text, pos + 1)
            obj[str(key)] = value
            pos = _skip_space(text, pos)
            if pos < len(text) and text[pos] == ",":
                pos += 1
                continue
            if pos < len(text) and text[pos] == "}":
                return obj, pos + 1
            raise YamlError(f"流式映射缺少分隔符：{text!r}")
    if text[pos] == "[":
        seq: list[object] = []
        pos += 1
        while True:
            pos = _skip_space(text, pos)
            if pos < len(text) and text[pos] == "]":
                return seq, pos + 1
            value, pos = _parse_flow(text, pos)
            seq.append(value)
            pos = _skip_space(text, pos)
            if pos < len(text) and text[pos] == ",":
                pos += 1
                continue
            if pos < len(text) and text[pos] == "]":
                return seq, pos + 1
            raise YamlError(f"流式序列缺少分隔符：{text!r}")
    return _parse_flow_scalar(text, pos)


def _skip_space(text: str, pos: int) -> int:
    while pos < len(text) and text[pos] in " \t\n":
        pos += 1
    return pos


def _parse_flow_scalar(text: str, pos: int) -> tuple[object, int]:
    pos = _skip_space(text, pos)
    if pos >= len(text):
        raise YamlError("流式标量意外结束")
    if text[pos] in "{[":
        return _parse_flow(text, pos)
    if text[pos] in "\"'":
        return _parse_quoted(text, pos)
    start = pos
    while pos < len(text) and text[pos] not in ",]}:":
        pos += 1
    return _convert_scalar(text[start:pos].strip()), pos


def _convert_scalar(token: str) -> object:
    if token in ("", "null", "~", "None"):
        return None
    if token == "true":
        return True
    if token == "false":
        return False
    if re.fullmatch(r"-?\d+", token):
        return int(token)
    if re.fullmatch(r"-?\d+\.\d+", token):
        return float(token)
    return token


class _Lines:
    def __init__(self, text: str) -> None:
        self.items: list[tuple[int, str]] = []
        for raw in text.splitlines():
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            line = _strip_comment(raw)
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip(" "))
            self.items.append((indent, line.strip()))
        self.index = 0

    def peek(self) -> tuple[int, str] | None:
        if self.index >= len(self.items):
            return None
        return self.items[self.index]

    def take(self) -> tuple[int, str]:
        item = self.items[self.index]
        self.index += 1
        return item


def _parse_value(lines: _Lines, rest: str, parent_indent: int) -> object:
    if rest.startswith(("[", "{")):
        parts = [rest]
        while not _balanced(" ".join(parts)):
            if lines.index >= len(lines.items):
                raise YamlError("流式集合未闭合")
            parts.append(lines.take()[1])
        value, end = _parse_flow(" ".join(parts))
        if " ".join(parts)[end:].strip():
            raise YamlError("流式集合后存在多余内容")
        return value
    if rest:
        if rest.startswith(("\"", "'")):
            return _parse_quoted(rest, 0)[0]
        return _convert_scalar(rest)
    peeked = lines.peek()
    if peeked is not None and peeked[0] > parent_indent:
        return _parse_block(lines, peeked[0])
    return None


def _parse_map_item(lines: _Lines, map_indent: int, first: str) -> dict[str, object]:
    obj: dict[str, object] = {}
    key, rest = _split_key(first)
    obj[key] = _parse_value(lines, rest, map_indent)
    while True:
        peeked = lines.peek()
        if peeked is None or peeked[0] != map_indent or peeked[1].startswith("-"):
            return obj
        content = lines.take()[1]
        key, rest = _split_key(content)
        obj[key] = _parse_value(lines, rest, map_indent)


def _parse_seq(lines: _Lines, indent: int) -> list[object]:
    seq: list[object] = []
    while True:
        peeked = lines.peek()
        if peeked is None or peeked[0] != indent or not peeked[1].startswith("-"):
            return seq
        content = lines.take()[1][1:].strip()
        if not content:
            nxt = lines.peek()
            seq.append(_parse_block(lines, nxt[0]) if nxt and nxt[0] > indent else None)
        elif _looks_like_mapping(content) and not content.startswith(("{", "[")):
            seq.append(_parse_map_item(lines, indent + 2, content))
        else:
            seq.append(_parse_value(lines, content, indent))


def _parse_block(lines: _Lines, indent: int) -> object:
    peeked = lines.peek()
    if peeked is None or peeked[0] != indent:
        return None
    if peeked[1].startswith("-"):
        return _parse_seq(lines, indent)
    obj: dict[str, object] = {}
    while True:
        peeked = lines.peek()
        if peeked is None or peeked[0] != indent or peeked[1].startswith("-"):
            return obj
        content = lines.take()[1]
        key, rest = _split_key(content)
        obj[key] = _parse_value(lines, rest, indent)


def load_yaml(text: str) -> object:
    lines = _Lines(text)
    if not lines.items:
        return None
    value = _parse_block(lines, lines.items[0][0])
    if lines.index != len(lines.items):
        raise YamlError(f"存在未消费的行：{lines.items[lines.index]!r}")
    return value


# ---------------------------------------------------------------- 判定实现
# 每个函数返回子句级结果列表 [(verdict, reason[, severity])]；空列表表示 pass。
# 聚合由 aggregate() 完成，函数内不得提前 return 首个失败。


def check_project_minimal_existence(data: dict) -> list[tuple]:
    results = []
    actor_ids = {item.get("id") for item in data["actors"]}
    outcome_ids = {item.get("id") for item in data["outcomes"]}
    if not data["actors"]:
        results.append(("fail", "missing_actor", "G-A1#1"))
    if not data["outcomes"]:
        results.append(("fail", "missing_outcome", "G-A1#2"))
    if not data["commitments"]:
        results.append(("fail", "missing_commitment", "G-A1#3"))
    if not data["constraints"]:
        results.append(("fail", "missing_constraint", "G-A1#4"))
    commitment_ids = {item.get("id") for item in data["commitments"]}
    for commitment in data["commitments"]:
        if commitment.get("by") not in actor_ids or commitment.get("to") not in outcome_ids:
            results.append(("fail", "broken_commitment_endpoint", "G-A1#5"))
    for constraint in data["constraints"]:
        target = constraint.get("constrains")
        if not target or target not in (outcome_ids | commitment_ids):
            results.append(("fail", "constraint_not_applied", "G-A1#6"))
    return results


def check_constraint_anchor(data: dict) -> list[tuple]:
    results = []
    constraint_ids = {item.get("id") for item in data["constraints"]}
    for item in list(data["commitments"]) + list(data["deliverables"]):
        # 非法 node_type 由入口的全局枚举归一化（undefined_enum_value / G-A2#2）拦截。
        refs = item.get("constrained_by") or []
        if not refs or any(ref not in constraint_ids for ref in refs):
            results.append(("fail", "unanchored_management_item", "G-A2#1"))
    return results


def check_deliverable_assertion(data: dict) -> list[tuple]:
    results = []
    assertion_by_id = {item.get("id"): item for item in data["assertions"]}
    for deliverable in data["deliverables"]:
        deliverable_id = deliverable.get("id")
        refs = deliverable.get("asserted_by") or []
        if any(ref not in assertion_by_id for ref in refs):
            results.append(("fail", "dangling_reference", "G-C1#1"))
        about_ids = [aid for aid, item in assertion_by_id.items() if item.get("about") == deliverable_id]
        if not refs and not about_ids:
            results.append(("fail", "deliverable_without_assertion", "G-C1#1"))
        for assertion_id in list(dict.fromkeys(list(refs) + sorted(about_ids))):
            assertion = assertion_by_id.get(assertion_id)
            if assertion is None:
                continue
            if not assertion.get("statement") or assertion.get("statement_kind") not in STATEMENT_KINDS:
                results.append(("fail", "assertion_without_content", "G-C1#2"))
            if assertion.get("about") != deliverable_id:
                results.append(("fail", "assertion_about_mismatch", "G-C1#3"))
    return results


def check_change_constraint(data: dict) -> list[tuple]:
    results = []
    constraint_ids = {item.get("id") for item in data["constraints"]}
    commitment_ids = {item.get("id") for item in data.get("commitments") or []}
    deliverable_ids = {item.get("id") for item in data.get("deliverables") or []}
    for change in data["changes"]:
        if change.get("constraint") not in constraint_ids:
            results.append(("fail", "missing_constraint_link", "G-D1#2"))
        if change.get("relation") not in CHANGE_RELATIONS:
            results.append(("fail", "invalid_change_relation", "G-D1#3"))
        target = change.get("target")
        if not isinstance(target, dict) or not target.get("type") or not target.get("id"):
            results.append(("fail", "missing_change_target", "G-D1#1"))
            continue
        if target["type"] not in CHANGE_TARGET_TYPES:
            results.append(("fail", "invalid_change_target", "G-D1#1"))
            continue
        known = commitment_ids if target["type"] == "Commitment" else deliverable_ids
        if target["id"] not in known:
            results.append(("fail", "invalid_change_target", "G-D1#1"))
    return results


def check_role_minimal(data: dict) -> list[tuple]:
    results = []
    actors = {item.get("id"): item for item in data["actors"]}
    for commitment in data["commitments"]:
        accountable = commitment.get("accountable_by")
        if not accountable:
            results.append(("fail", "missing_accountable", "G-E1#1"))
        elif isinstance(accountable, list):
            results.append(("fail", "multiple_accountable", "G-E1#1"))
        else:
            actor = actors.get(accountable)
            if actor is None:
                results.append(("fail", "unknown_accountable", "G-E1#1"))
            elif actor.get("type") not in ("HumanActor", "LegalEntity"):
                results.append(("fail", "accountable_not_human", "G-E1#1"))
        responsible = commitment.get("responsible_by") or []
        if not responsible:
            results.append(("fail", "missing_responsible", "G-E1#2"))
        if accountable and accountable in responsible and not commitment.get("role_merge_declaration"):
            results.append(("fail", "missing_role_merge_declaration", "G-E1#3"))
    return results


def check_dual_dimension(data: dict) -> list[tuple]:
    results = []
    for item in data["management_items"]:
        # 两个维度分属 G-B1#1/#2；共享 missing_dimension 不能作为子句证据。
        if not item.get("process_group"):
            results.append(("fail", "missing_dimension", "G-B1#1"))
        if not item.get("subject_group"):
            results.append(("fail", "missing_dimension", "G-B1#2"))
    return results


def extension_valid(entry: dict) -> bool:
    """G-B2#2：relation 封闭；非 orthogonal_to 必须有基础归属，orthogonal_to 可不声明。"""
    value = entry.get("value")
    relation = entry.get("relation")
    if not isinstance(value, str) or relation not in EXTENSION_RELATIONS:
        return False
    if value in BASE_SUBJECT_GROUPS:
        return False
    if relation == "orthogonal_to":
        base = entry.get("base")
        return base is None or base in BASE_SUBJECT_GROUPS
    return entry.get("base") in BASE_SUBJECT_GROUPS


def check_dimension_value(data: dict) -> list[tuple]:
    results = []
    extension: set[str] = set()
    for entry in data.get("subject_group_extension") or []:
        if extension_valid(entry):
            extension.add(entry["value"])
    for item in data["management_items"]:
        if item.get("process_group") not in PROCESS_GROUPS:
            results.append(("fail", "dimension_value_out_of_enum", "G-B2#1"))
        subject = item.get("subject_group")
        if subject not in BASE_SUBJECT_GROUPS and subject not in extension:
            results.append(("fail", "dimension_value_out_of_enum", "G-B2#1"))
    for entry in data.get("subject_group_extension") or []:
        if not extension_valid(entry):
            results.append(("fail", "invalid_subject_group_extension", "G-B2#2"))
    return results


def check_assertion_mutual_exclusion(data: dict) -> list[tuple]:
    results = []
    seen: dict[tuple, set] = {}
    for assertion in data["assertions"]:
        if assertion.get("state") != "active":
            continue
        key = (assertion.get("subject"), assertion.get("property"))
        seen.setdefault(key, set()).add(assertion.get("value"))
    if any(len(values) > 1 for values in seen.values()):
        results.append(("fail", "mutually_exclusive_active_assertions", "G-C2#1"))
    return results


def check_all_improvement(data: dict) -> list[tuple]:
    results = []
    for change in data["changes"]:
        relations = change.get("relations") or []
        assumption = change.get("assumption")
        status = assumption.get("status") if isinstance(assumption, dict) else None
        assumption_condition = (
            assumption.get("verification_condition") if isinstance(assumption, dict) else None
        )
        if relations and all(item == "mitigates" for item in relations):
            if not assumption or not (change.get("verification_condition") or assumption_condition):
                results.append(("fail", "all_improvement_without_verification", "G-D2#1"))
            elif status == "expired" or (
                status == "pending" and not assumption.get("approved_by")
            ):
                results.append(("cannot_evaluate", "assumption_unclosed", "G-D2#3"))
        if change.get("approval_basis") and status != "satisfied":
            results.append(("fail", "approval_basis_before_verification", "G-D2#2"))
    return results


def check_ai_autonomy(data: dict) -> list[tuple]:
    """G-E2：路径子句（#1）与断言子句（#2/#3）分别收集，聚合时 fail 胜出。"""
    results = []
    actors = {item.get("id"): item for item in data["actors"]}
    assertions = {item.get("id"): item for item in data["assertions"]}
    for grant in data["autonomy_grants"]:
        actor_id = grant.get("actor")
        if actor_id not in actors:
            results.append(("fail", "dangling_reference", "G-E2#1"))
        path = grant.get("delegated_from")
        if not isinstance(path, dict):
            results.append(("cannot_evaluate", "invalid_path", "G-E2#1"))
        else:
            start = path.get("start") or actor_id
            steps = path.get("steps")
            reach = path.get("reach")
            if start not in actors or not isinstance(steps, list) or not steps:
                results.append(("cannot_evaluate", "invalid_path", "G-E2#1"))
            else:
                cursor = start
                path_ok = True
                for step in steps:
                    if not isinstance(step, dict):
                        results.append(("cannot_evaluate", "invalid_path", "G-E2#1"))
                        path_ok = False
                        break
                    if step.get("relation") != "delegated_from" or step.get("direction") != "out":
                        results.append(("cannot_evaluate", "invalid_path", "G-E2#1"))
                        path_ok = False
                        break
                    if step.get("target_type") != "Actor":
                        results.append(("cannot_evaluate", "undefined_object_type", "G-E2#1"))
                        path_ok = False
                        break
                    target_id = step.get("target_id")
                    if not target_id:
                        results.append(("cannot_evaluate", "invalid_path", "G-E2#1"))
                        path_ok = False
                        break
                    if target_id not in actors:
                        results.append(("fail", "dangling_reference", "G-E2#1"))
                        path_ok = False
                        break
                    cursor = target_id
                if path_ok and reach != "accountable":
                    results.append(("cannot_evaluate", "invalid_path", "G-E2#1"))
                    path_ok = False
                if path_ok:
                    terminal = actors[cursor]
                    if terminal.get("accountable") is not True:
                        results.append(("fail", "delegation_chain_not_accountable", "G-E2#1"))
                    elif terminal.get("type") not in ("HumanActor", "LegalEntity"):
                        # 链终点必须能承担问责：AI 节点即使标 accountable 也不能作为终点。
                        results.append(("fail", "accountable_not_human", "G-E2#1"))
        covers: set = set()
        for assertion_id in grant.get("assertions") or []:
            assertion = assertions.get(assertion_id)
            if assertion is None:
                results.append(("fail", "dangling_reference", "G-E2#3"))
                continue
            covers.update(assertion.get("covers") or [])
            if assertion.get("kind") not in ASSERTION_KINDS:
                results.append(("cannot_evaluate", "undefined_object_type", "G-E2#3"))
                continue
            if assertion.get("kind") != "assumption" or not assertion.get("verification_condition"):
                results.append(("fail", "assertion_incomplete", "G-E2#3"))
            assumption = assertion.get("assumption")
            if isinstance(assumption, dict) and (
                assumption.get("status") == "expired"
                or (
                    assumption.get("status") == "pending"
                    and not assumption.get("approved_by")
                )
            ):
                results.append(("cannot_evaluate", "assumption_unclosed", "G-E2#3"))
        if not {"scope", "boundary", "revocation"} <= covers:
            results.append(("fail", "assertion_incomplete", "G-E2#2"))
    return results


def check_project_charter(data: dict) -> list[tuple]:
    results = []
    charters = {item.get("project"): item for item in data["charters"]}
    for project in data["projects"]:
        if project.get("stage") != "executing":
            continue
        charter = charters.get(project.get("id"))
        if charter is None:
            results.append(("fail", "missing_charter", "G-F1#1"))
            continue
        required = ("outcomes", "constraints", "accountable", "authorizing_assertion")
        if any(not charter.get(key) for key in required):
            results.append(("fail", "incomplete_charter", "G-F1#2"))
    return results


def check_closure_acceptance(data: dict) -> list[tuple]:
    results = []
    for deliverable in data["deliverables"]:
        assertions = deliverable.get("assertions") or []
        statements = [
            item for item in assertions if item.get("statement") in ACCEPTANCE_STATEMENTS
        ]
        if not statements:
            results.append(("fail", "missing_acceptance_assertion", "G-F2#1"))
        elif not any(item.get("accountable_confirmation") for item in statements):
            results.append(("fail", "missing_acceptance_assertion", "G-F2#2"))
    return results


def check_procurement_contract(data: dict) -> list[tuple]:
    results = []
    contracts = {item.get("id"): item for item in data["contracts"]}
    for commitment in data["commitments"]:
        if commitment.get("procurement") != "external":
            continue
        contract = contracts.get(commitment.get("contract"))
        if contract is None:
            results.append(("fail", "missing_contract", "G-F3#1"))
            continue
        required = ("deliverable_form", "acceptance_criteria", "constrained_by", "accountable_signature")
        if any(not contract.get(key) for key in required):
            results.append(("fail", "incomplete_contract", "G-F3#2"))
    return results


def check_schedule_evidence(data: dict) -> list[tuple]:
    results = []
    for commitment in data["commitments"]:
        if not (commitment.get("deadline") or commitment.get("milestone")):
            continue
        evidence = commitment.get("evidence_assertions") or []
        if not evidence or any(not item.get("basis") for item in evidence):
            results.append(("fail", "missing_schedule_evidence", "G-F4#1"))
    return results


def check_tailoring_record(data: dict) -> list[tuple]:
    results = []
    records = {item.get("id"): item for item in data["tailoring_records"]}
    for action in data["tailoring_actions"]:
        record = records.get(action.get("record"))
        if record is None:
            results.append(("fail", "missing_tailoring_record", "G-G1#1"))
            continue
        if any(not record.get(key) for key in ("trimmed_rule", "rationale", "scope", "approver")):
            results.append(("fail", "incomplete_tailoring_record", "G-G1#2"))
    return results


def check_tailoring_non_trimmable(data: dict) -> list[tuple]:
    results = []
    for record in data["tailoring_records"]:
        if record.get("trimmed_rule") in NON_TRIMMABLE:
            results.append(("fail", "non_trimmable_rule", "G-G2#1"))
    return results


def check_tailoring_reassessment(data: dict) -> list[tuple]:
    results = []
    for record in data["tailoring_records"]:
        if record.get("reassessment_condition"):
            continue
        if record.get("permanent") is True:
            if not record.get("reason"):
                results.append(("fail", "missing_reassessment_condition", "G-G3#2"))
            continue
        results.append(("fail", "missing_reassessment_condition", "G-G3#1"))
    return results


CHECKS = {
    "PROJECT_MINIMAL_EXISTENCE": check_project_minimal_existence,
    "CONSTRAINT_ANCHOR_REQUIRED": check_constraint_anchor,
    "DELIVERABLE_ASSERTION_LINK": check_deliverable_assertion,
    "CHANGE_CONSTRAINT_LINK": check_change_constraint,
    "ROLE_MINIMAL_COMPLETENESS": check_role_minimal,
    "DUAL_DIMENSION_ANNOTATION": check_dual_dimension,
    "DIMENSION_VALUE_CLOSED": check_dimension_value,
    "ASSERTION_MUTUAL_EXCLUSION": check_assertion_mutual_exclusion,
    "ALL_IMPROVEMENT_ASSUMPTION": check_all_improvement,
    "AI_AUTONOMY_DELEGATION_AUDITABLE": check_ai_autonomy,
    "PROJECT_CHARTER_EXISTENCE": check_project_charter,
    "CLOSURE_ACCEPTANCE_LINK": check_closure_acceptance,
    "PROCUREMENT_CONTRACT_ANCHOR": check_procurement_contract,
    "SCHEDULE_EVIDENCE_LINK": check_schedule_evidence,
    "TAILORING_RECORD_EXISTENCE": check_tailoring_record,
    "TAILORING_NON_TRIMMABLE_SET": check_tailoring_non_trimmable,
    "TAILORING_REASSESSMENT_CONDITION": check_tailoring_reassessment,
}


# ---------------------------------------------------------------- 样例抽取与执行


def extract_cases(method_text: str) -> list[dict]:
    headings = list(re.finditer(r"(?m)^#### (A\.1\.\d+) `([A-Z_]+)`（(G-[A-Z]\d)，", method_text))
    cases: list[dict] = []
    for order, match in enumerate(headings):
        section = match.group(1)
        check_id = match.group(2)
        rule = match.group(3)
        start = match.end()
        end = headings[order + 1].start() if order + 1 < len(headings) else len(method_text)
        chunk = method_text[start:end]
        blocks = re.findall(r"```yaml\n(.*?)```", chunk, re.S)
        if len(blocks) < 4 or len(blocks) % 2:
            raise SystemExit(f"[失败] {section} 的 YAML 块应为 4 的倍数，实际 {len(blocks)} 个")
        for index in range(0, len(blocks), 2):
            cases.append(
                {
                    "section": section,
                    "case": index // 2 + 1,
                    "check_id": check_id,
                    "source_rule": rule,
                    "input": load_yaml(blocks[index]),
                    "expected": load_yaml(blocks[index + 1]),
                }
            )
    return cases


def find_null(value, path: str = "<root>") -> str | None:
    """入口归一化：递归定位顶层键、嵌套对象键、数组元素中的 null。"""
    if value is None:
        return path
    if isinstance(value, dict):
        for key, item in value.items():
            hit = find_null(item, f"{path}.{key}")
            if hit:
                return hit
    elif isinstance(value, list):
        for index, item in enumerate(value):
            hit = find_null(item, f"{path}[{index}]")
            if hit:
                return hit
    return None


ENTITY_COLLECTIONS = (
    "actors",
    "outcomes",
    "commitments",
    "constraints",
    "deliverables",
    "assertions",
    "changes",
    "projects",
    "charters",
    "contracts",
    "tailoring_actions",
    "tailoring_records",
    "management_items",
    "autonomy_grants",
)

APPLICABILITY_STATES = {"applicable", "inapplicable", "pending"}
ASSUMPTION_STATUSES = {"pending", "satisfied", "expired"}
MANAGEMENT_NODE_TYPES = {"ManagementActivity", "ManagementArtifact"}


def nested_missing(data: dict) -> str | None:
    """嵌套归一化：实体集合的每个元素必须有 id，缺失与顶层缺键同出口。"""
    for name in ENTITY_COLLECTIONS:
        value = data.get(name)
        if not isinstance(value, list):
            continue
        for index, item in enumerate(value):
            if isinstance(item, dict) and "id" not in item:
                return f"{name}[{index}].id"
    return None


def enum_violation(data: dict) -> tuple[str, str | None] | None:
    """封闭枚举全局强制：非法值一律 cannot_evaluate/undefined_enum_value。

    可归属到 A.2 子句的两项（node_type、subject_group.relation）带回 clause，
    使覆盖闸门仍能按子句取证；适用性与 assumption.status 无独立 A.2 子句。
    """
    applicability = data.get("applicability")
    if isinstance(applicability, dict):
        state = applicability.get("state")
        if state is not None and state not in APPLICABILITY_STATES:
            return "applicability.state", None
    for collection in ("changes", "assertions"):
        for item in data.get(collection) or []:
            if not isinstance(item, dict):
                continue
            assumption = item.get("assumption")
            if isinstance(assumption, dict) and assumption.get("status") is not None:
                if assumption["status"] not in ASSUMPTION_STATUSES:
                    return "assumption.status", None
    for collection in ("commitments", "deliverables"):
        for item in data.get(collection) or []:
            if not isinstance(item, dict):
                continue
            node_type = item.get("node_type")
            if node_type is not None and node_type not in MANAGEMENT_NODE_TYPES:
                return "node_type", "G-A2#2"
    for entry in data.get("subject_group_extension") or []:
        if not isinstance(entry, dict):
            continue
        relation = entry.get("relation")
        if relation is not None and relation not in EXTENSION_RELATIONS:
            return "subject_group.relation", "G-B2#2"
    return None


def evaluate(check_id: str, data: dict) -> tuple[str, str | None, str]:
    """全部 check 的唯一入口：适用性 → 缺键/null/枚举归一化 → 判定 → 全局引用校验。"""
    severity = SPEC[check_id][1]
    applicability = data.get("applicability") or {}
    state = applicability.get("state") if isinstance(applicability, dict) else None
    if state == "inapplicable":
        return "not_applicable", None, severity
    if state == "pending":
        return "cannot_evaluate", "applicability_pending", severity
    # 入口归一化：键缺失与值为 null 走同一出口，不依赖 check 函数内的守卫。
    missing = [key for key in REQUIRED_KEYS.get(check_id, ()) if key not in data]
    if missing:
        return "cannot_evaluate", "missing_input", severity
    if find_null(data) is not None:
        return "cannot_evaluate", "missing_input", severity
    if nested_missing(data) is not None:
        return "cannot_evaluate", "missing_input", severity
    violation = enum_violation(data)
    if violation:
        return "cannot_evaluate", "undefined_enum_value", severity
    verdict, reason, severity = aggregate(
        check_id, CHECKS[check_id](data), SPEC[check_id][1]
    )
    # 引用完整性全局生效：check 自身判 pass 时，再统一校验所有已知引用。
    if verdict == "pass":
        reference_issue = validate_references(data)
        if reference_issue:
            verdict, reason = reference_issue
    return verdict, reason, severity


def run_case(case: dict) -> dict:
    check_id = case["check_id"]
    expected = case["expected"] or {}
    rule_status = SPEC[check_id][2]
    data = case["input"] or {}
    verdict, reason, severity = evaluate(check_id, data)
    actual = {
        "check_id": check_id,
        "source_rule": SPEC[check_id][0],
        "severity": severity,
        "rule_status": rule_status,
        "verdict": verdict,
        "reason": reason,
    }
    mismatches = []
    for key in ("check_id", "source_rule", "verdict", "reason"):
        if expected.get(key) != actual[key]:
            mismatches.append(f"{key}: 期望 {expected.get(key)!r}，实际 {actual[key]!r}")
    for key in ("severity", "rule_status"):
        if key in expected and expected[key] != actual[key]:
            mismatches.append(f"{key}: 期望 {expected[key]!r}，实际 {actual[key]!r}")
    return {**case, "actual": actual, "mismatches": mismatches}


def _walk_paths(value, prefix: tuple = ()):
    """产出 (路径元组, 节点) 覆盖全部嵌套结构。"""
    if isinstance(value, dict):
        for key, item in value.items():
            path = prefix + (key,)
            yield path, item
            yield from _walk_paths(item, path)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            path = prefix + (index,)
            yield path, item
            yield from _walk_paths(item, path)


def _render_path(path: tuple) -> str:
    rendered = ""
    for part in path:
        if isinstance(part, int):
            rendered += "[]"
        else:
            rendered = f"{rendered}.{part}" if rendered else part
    return rendered


def _assign(data, path: tuple, value) -> None:
    cursor = data
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value


def _expect_missing(kind: str, check_id: str, data: dict, failures: list) -> bool:
    try:
        verdict, reason, _ = evaluate(check_id, data)
    except Exception as exc:  # noqa: BLE001 - 负例就是要捕获崩溃
        failures.append(f"{kind} [{check_id}] 抛 {type(exc).__name__}: {exc}")
        return False
    if (verdict, reason) != ("cannot_evaluate", "missing_input"):
        failures.append(
            f"{kind} [{check_id}] 期望 cannot_evaluate/missing_input，实际 {verdict}/{reason}"
        )
        return False
    return True


def missing_key_sweep(quiet: bool = False) -> int:
    """负例实测：43 个必需键逐一单删，都必须 cannot_evaluate/missing_input。"""
    rows: list[tuple[str, str, str, str]] = []
    failures = 0
    for check_id in sorted(REQUIRED_KEYS):
        keys = REQUIRED_KEYS[check_id]
        for missing_key in keys:
            data = {key: [] for key in keys}
            del data[missing_key]
            try:
                verdict, reason, _ = evaluate(check_id, data)
                actual = f"{verdict}/{reason}"
            except Exception as exc:  # noqa: BLE001 - 负例就是要捕获崩溃
                verdict, reason = "crash", type(exc).__name__
                actual = f"{verdict}/{reason}"
            ok = (verdict, reason) == ("cannot_evaluate", "missing_input")
            failures += 0 if ok else 1
            rows.append((check_id, missing_key, actual, "通过" if ok else "偏离"))
    if not quiet:
        print("| check_id | 删除的必需键 | 实际结论 | 判定 |")
        print("|---|---|---|---|")
        for row in rows:
            print("| " + " | ".join(row) + " |")
        print()
    print(f"缺键负例：{len(rows) - failures}/{len(rows)} 返回 cannot_evaluate/missing_input，偏离 {failures} 处")
    # 对照：绕开入口归一化直接调用 check 仍会崩溃，证明拦截在入口而非各 check 内的守卫。
    crashes = 0
    for check_id in sorted(CHECKS):
        try:
            CHECKS[check_id]({})
        except KeyError:
            crashes += 1
    print(f"对照：`{{}}` 直接进入 check 函数仍 {crashes}/{len(CHECKS)} 抛 KeyError（入口归一化负责拦截）")
    return 0 if not failures else 1


def nested_missing_sweep(root: Path, quiet: bool = False) -> int:
    """嵌套缺键全表：删除实体集合元素的 id，必须 cannot_evaluate/missing_input。"""
    method = (root / METHOD).read_text(encoding="utf-8")
    rows: list[tuple[str, str, str, str]] = []
    seen: set[tuple[str, str, int]] = set()
    failures = 0
    for case in extract_cases(method):
        check_id = case["check_id"]
        data = case["input"] or {}
        for name in ENTITY_COLLECTIONS:
            value = data.get(name)
            if not isinstance(value, list):
                continue
            for index, item in enumerate(value):
                if not isinstance(item, dict) or "id" not in item:
                    continue
                key = (check_id, name, index)
                if key in seen:
                    continue
                seen.add(key)
                clone = copy.deepcopy(data)
                del clone[name][index]["id"]
                try:
                    verdict, reason, _ = evaluate(check_id, clone)
                    actual = f"{verdict}/{reason}"
                except Exception as exc:  # noqa: BLE001 - 负例就是要捕获崩溃
                    verdict, reason = "crash", type(exc).__name__
                    actual = f"{verdict}/{reason}"
                ok = (verdict, reason) == ("cannot_evaluate", "missing_input")
                failures += 0 if ok else 1
                rows.append((check_id, f"{name}[{index}].id", actual, "通过" if ok else "偏离"))
    if not quiet:
        print("| check_id | 删除的嵌套键 | 实际结论 | 判定 |")
        print("|---|---|---|---|")
        for row in rows:
            print("| " + " | ".join(row) + " |")
        print()
    print(f"嵌套缺键负例：{len(rows) - failures}/{len(rows)} 返回 cannot_evaluate/missing_input，偏离 {failures} 处")
    return 0 if not failures else 1


def enum_sweep(quiet: bool = False) -> int:
    """封闭枚举负例：四个受控字段的非法值统一 cannot_evaluate/undefined_enum_value。"""
    cases = [
        (
            "applicability.state",
            "PROJECT_MINIMAL_EXISTENCE",
            {key: [] for key in REQUIRED_KEYS["PROJECT_MINIMAL_EXISTENCE"]}
            | {"applicability": {"state": "unknown_state"}},
        ),
        (
            "assumption.status",
            "CHANGE_CONSTRAINT_LINK",
            {
                "actors": [],
                "outcomes": [],
                "commitments": [],
                "constraints": [],
                "deliverables": [],
                "assertions": [],
                "changes": [{"id": "CH-1", "assumption": {"status": "unknown_status"}}],
            },
        ),
        (
            "node_type",
            "CONSTRAINT_ANCHOR_REQUIRED",
            {
                "commitments": [],
                "deliverables": [{"id": "D-1", "node_type": "MysteryNode"}],
                "constraints": [],
            },
        ),
        (
            "subject_group.relation",
            "DIMENSION_VALUE_CLOSED",
            {
                "management_items": [
                    {"id": "M-1", "process_group": "initiating", "subject_group": "planning"}
                ],
                "subject_group_extension": [{"value": "innovation", "relation": "sideways"}],
            },
        ),
    ]
    rows = []
    failures = 0
    for field, check_id, data in cases:
        verdict, reason, _ = evaluate(check_id, data)
        ok = (verdict, reason) == ("cannot_evaluate", "undefined_enum_value")
        failures += 0 if ok else 1
        rows.append((field, check_id, f"{verdict}/{reason}", "通过" if ok else "偏离"))
    if not quiet:
        print("| 字段 | check_id | 实际结论 | 判定 |")
        print("|---|---|---|---|")
        for row in rows:
            print("| " + " | ".join(row) + " |")
        print()
    print(f"枚举负例：{len(rows) - failures}/{len(rows)} 返回 cannot_evaluate/undefined_enum_value，偏离 {failures} 处")
    return 0 if not failures else 1


def aggregation_order_check() -> int:
    """顺序无关性证据：同一组冲突子句的全部排列必须给同一结论。"""
    # A2：fail（未锚定）与 cannot_evaluate（未定义节点类型）冲突。
    a2_items = [
        {"id": "D-1", "constrained_by": []},
        {"id": "D-2", "node_type": "MysteryNode", "constrained_by": []},
        {"id": "D-3", "constrained_by": []},
    ]
    # E2：invalid_path（cannot_evaluate）与断言不完整/链未达 Accountable（fail）冲突。
    e2_grants = [
        {"id": "AG-1", "actor": "A-1", "delegated_from": "broken", "assertions": []},
        {
            "id": "AG-2",
            "actor": "A-1",
            "delegated_from": {
                "start": "A-1",
                "steps": [
                    {
                        "relation": "delegated_from",
                        "direction": "out",
                        "target_type": "Actor",
                        "target_id": "A-2",
                    }
                ],
                "reach": "accountable",
            },
            "assertions": [],
        },
        {
            "id": "AG-3",
            "actor": "A-1",
            "delegated_from": {
                "start": "A-1",
                "steps": [
                    {
                        "relation": "delegated_from",
                        "direction": "out",
                        "target_type": "Actor",
                        "target_id": "A-3",
                    }
                ],
                "reach": "accountable",
            },
            "assertions": [],
        },
    ]
    e2_base = {
        "actors": [
            {"id": "A-1", "type": "AIActor"},
            {"id": "A-2", "type": "HumanActor", "accountable": True},
            {"id": "A-3", "type": "AIActor"},
        ],
        "assertions": [],
    }
    cases = [
        (
            "CONSTRAINT_ANCHOR_REQUIRED",
            lambda perm: {
                "commitments": [],
                "deliverables": list(perm),
                "constraints": [],
            },
            a2_items,
        ),
        (
            "AI_AUTONOMY_DELEGATION_AUDITABLE",
            lambda perm: {**copy.deepcopy(e2_base), "autonomy_grants": list(perm)},
            e2_grants,
        ),
    ]
    failures = 0
    for check_id, build, items in cases:
        conclusions = set()
        orders = 0
        for perm in permutations(items):
            orders += 1
            conclusions.add(evaluate(check_id, build(perm))[:2])
        ok = len(conclusions) == 1
        failures += 0 if ok else 1
        raw = CHECKS[check_id](build(items))
        distribution: dict[str, int] = {}
        for item in raw:
            distribution[item[0]] = distribution.get(item[0], 0) + 1
        rendered_dist = "、".join(f"{key}={value}" for key, value in sorted(distribution.items()))
        rendered = "、".join(f"{v}/{r}" for v, r in sorted(conclusions))
        print(f"{check_id}：子句结果 {rendered_dist}；排列 {orders} 种，结论 {len(conclusions)} 种（{rendered}）")
    print(f"顺序无关性：{'通过' if not failures else '未通过'}，偏离 {failures} 项")
    return 0 if not failures else 1


def null_sweep(root: Path, quick: bool = False) -> int:
    """负例实测：顶层键、嵌套对象键、数组元素为 null 都必须 cannot_evaluate。

    quick 模式只对每个 check_id 的第一个样例做嵌套/数组扫描，供 pre-commit 快检。
    """
    failures: list[str] = []

    top_total = top_ok = 0
    for check_id, keys in REQUIRED_KEYS.items():
        for null_key in keys:
            top_total += 1
            data = {key: [] for key in keys}
            data[null_key] = None
            if _expect_missing(f"顶层键 {null_key}", check_id, data, failures):
                top_ok += 1

    method = (root / METHOD).read_text(encoding="utf-8")
    array_total = array_ok = object_total = object_ok = 0
    array_paths: set[tuple[str, str]] = set()
    quick_done: set[str] = set()
    for case in extract_cases(method):
        check_id = case["check_id"]
        if quick and check_id in quick_done:
            continue
        quick_done.add(check_id)
        data = case["input"] or {}
        for path, node in list(_walk_paths(data)):
            if isinstance(node, list) and node:
                array_total += 1
                array_paths.add((check_id, _render_path(path)))
                clone = copy.deepcopy(data)
                _assign(clone, path + (0,), None)
                if _expect_missing(
                    f"数组元素 {_render_path(path)}[0]", check_id, clone, failures
                ):
                    array_ok += 1
            elif isinstance(node, dict) and len(path) > 1 and isinstance(path[-1], str):
                object_total += 1
                clone = copy.deepcopy(data)
                _assign(clone, path, None)
                if _expect_missing(
                    f"嵌套对象键 {_render_path(path)}", check_id, clone, failures
                ):
                    object_ok += 1

    for failure in failures:
        print(f"[FAIL] {failure}")
    print(f"null 负例（顶层必需键）：{top_ok}/{top_total}")
    print(
        f"null 负例（数组元素）：{array_ok}/{array_total}"
        f"，覆盖 {len(array_paths)} 条唯一非空数组路径"
    )
    print(f"null 负例（嵌套对象键）：{object_ok}/{object_total}")
    total, ok = top_total + array_total + object_total, top_ok + array_ok + object_ok
    print(f"null 负例合计：{ok}/{total} 返回 cannot_evaluate，崩溃 {len(failures)} 处")
    return 0 if not failures else 1


def input_domain_issues(root: Path) -> list[str]:
    """检查 §3 输入域是否覆盖样例中实际出现的引用目标集合。"""
    method = (root / METHOD).read_text(encoding="utf-8")
    issues: list[str] = []
    for case in extract_cases(method):
        check_id = case["check_id"]
        required = set(REQUIRED_KEYS.get(check_id, ()))
        needed = referenced_collections(case["input"] or {})
        missing = sorted(needed - required)
        if missing:
            issues.append(
                f"{case['section']}-{case['case']} {check_id}: 引用目标集合 "
                f"{missing} 未在 §3 必需顶层键中声明"
            )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="T-107 最小原型：执行 A.1 全部样例")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    parser.add_argument("--quiet", action="store_true", help="只输出汇总，不打印逐行表")
    parser.add_argument(
        "--quick", action="store_true", help="快检子集：每个 check_id 只扫第一个样例"
    )
    parser.add_argument(
        "--null-sweep", action="store_true", help="负例：任意层级取 null 时不得抛异常"
    )
    parser.add_argument(
        "--nested-missing-sweep",
        action="store_true",
        help="负例：实体集合元素缺 id 时必须 cannot_evaluate/missing_input",
    )
    parser.add_argument(
        "--enum-sweep",
        action="store_true",
        help="负例：封闭枚举非法值统一 cannot_evaluate/undefined_enum_value",
    )
    parser.add_argument(
        "--input-domain",
        action="store_true",
        help="检查样例中出现的引用目标集合是否都已在 schema §3 声明",
    )
    parser.add_argument(
        "--missing-key-sweep",
        action="store_true",
        help="负例：43 个必需键逐一单删，必须 cannot_evaluate/missing_input",
    )
    parser.add_argument(
        "--aggregation-order",
        action="store_true",
        help="顺序无关性：同一组冲突子句的全部排列给同一结论",
    )
    args = parser.parse_args()
    root = Path(args.root)
    if args.null_sweep:
        return null_sweep(root, quick=args.quick)
    if args.input_domain:
        issues = input_domain_issues(root)
        for issue in issues:
            print(f"[FAIL] {issue}")
        print(f"输入域闭包：{len(issues)} 处缺口")
        return 0 if not issues else 1
    if args.missing_key_sweep:
        return missing_key_sweep(quiet=args.quiet)
    if args.nested_missing_sweep:
        return nested_missing_sweep(root, quiet=args.quiet)
    if args.enum_sweep:
        return enum_sweep(quiet=args.quiet)
    if args.aggregation_order:
        return aggregation_order_check()
    method = (root / METHOD).read_text(encoding="utf-8")
    cases = [run_case(case) for case in extract_cases(method)]
    passed = [case for case in cases if not case["mismatches"]]
    by_check: dict[str, list[bool]] = {}
    for case in cases:
        by_check.setdefault(case["check_id"], []).append(not case["mismatches"])
    summary = {
        "total": len(cases),
        "passed": len(passed),
        "rate": round(len(passed) / len(cases), 4) if cases else 0.0,
        "checks_total": len(by_check),
        "checks_passed": sum(1 for values in by_check.values() if all(values)),
        "coverage_gaps": COVERAGE_GAPS,
        "cases": [
            {
                "section": case["section"],
                "case": case["case"],
                "check_id": case["check_id"],
                "actual": case["actual"],
                "mismatches": case["mismatches"],
            }
            for case in cases
        ],
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        for case in [] if args.quiet else cases:
            status = "ok  " if not case["mismatches"] else "FAIL"
            actual = case["actual"]
            print(
                f"[{status}] {case['section']}-{case['case']} {case['check_id']} "
                f"source_rule={actual['source_rule']} severity={actual['severity']} "
                f"rule_status={actual['rule_status']} "
                f"verdict={actual['verdict']} reason={actual['reason']}"
            )
            for mismatch in case["mismatches"]:
                print(f"       {mismatch}")
        print()
        print(f"样例通过：{summary['passed']}/{summary['total']}（{summary['rate'] * 100:.1f}%）")
        print(f"按 check_id：{summary['checks_passed']}/{summary['checks_total']} 全通过")
        print("未覆盖规则正文（原型只执行附录 A 判定列）：")
        if not COVERAGE_GAPS:
            print("  - 无（ADR-0013 已消解全部 5 项）")
        for check_id, note in COVERAGE_GAPS.items():
            print(f"  - {check_id}：{note}")
    return 0 if len(passed) == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
