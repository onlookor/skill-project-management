#!/usr/bin/env python3
"""T-107 最小原型：按附录 A 判定列执行 T-011 的 34 个样例。

只使用标准库。输入为 spec/methods/deterministic-checker.md 中 A.1 的
YAML 谓词快照；输出 check_id / source_rule / severity / rule_status /
verdict / reason，并与样例的“期望输出”逐项比对。

判定依据是附录 A 的“判定”列与 A.2 子句表。ADR-0013 已把原 5 处“未覆盖
规则正文”全部纳入判定列，故 COVERAGE_GAPS 为空；G-004 通过 A.2 的子句
severity（G-E1#3 为 warn）承接，不再把合法产物按 block 判死。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

METHOD = Path("spec/methods/deterministic-checker.md")

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
CHANGE_TARGET_TYPES = {"Commitment", "Deliverable"}
STATEMENT_KINDS = {"what", "state", "condition"}
ASSERTION_KINDS = {"fact", "assumption", "decision"}
NON_TRIMMABLE = {"G-A1", "G-A2", "G-C1", "G-D1", "G-E1"}
ACCEPTANCE_STATEMENTS = {"已验收", "已移交"}

# ADR-0013 已把原 5 处“未覆盖规则正文”全部纳入判定列，本表保持为空是
# 有意为之：原型不再存在“声明未覆盖但仍输出 pass”的暗区。
COVERAGE_GAPS: dict[str, str] = {}

# 每个 check 的必需顶层键。键存在但值为 null 与键缺失同等处理：
# 返回 cannot_evaluate / missing_input，而不是进入迭代抛 TypeError。
REQUIRED_KEYS: dict[str, tuple[str, ...]] = {
    "PROJECT_MINIMAL_EXISTENCE": ("project", "actors", "outcomes", "commitments", "constraints"),
    "CONSTRAINT_ANCHOR_REQUIRED": ("commitments", "deliverables", "constraints"),
    "DELIVERABLE_ASSERTION_LINK": ("deliverables", "assertions"),
    "CHANGE_CONSTRAINT_LINK": ("changes", "constraints"),
    "ROLE_MINIMAL_COMPLETENESS": ("actors", "commitments"),
    "DUAL_DIMENSION_ANNOTATION": ("management_items",),
    "DIMENSION_VALUE_CLOSED": ("management_items",),
    "ASSERTION_MUTUAL_EXCLUSION": ("assertions",),
    "ALL_IMPROVEMENT_ASSUMPTION": ("changes",),
    "AI_AUTONOMY_DELEGATION_AUDITABLE": ("actors", "autonomy_grants", "assertions"),
    "PROJECT_CHARTER_EXISTENCE": ("projects", "charters"),
    "CLOSURE_ACCEPTANCE_LINK": ("deliverables",),
    "PROCUREMENT_CONTRACT_ANCHOR": ("commitments", "contracts"),
    "SCHEDULE_EVIDENCE_LINK": ("commitments",),
    "TAILORING_RECORD_EXISTENCE": ("tailoring_actions", "tailoring_records"),
    "TAILORING_NON_TRIMMABLE_SET": ("tailoring_records",),
    "TAILORING_REASSESSMENT_CONDITION": ("tailoring_records",),
}


def require_fields(data: dict, keys: tuple[str, ...]) -> tuple[str, str | None] | None:
    """必需键缺失或取 null 时统一返回 cannot_evaluate。"""
    if any(key not in data or data[key] is None for key in keys):
        return "cannot_evaluate", "missing_input"
    return None


def ids(items) -> set:
    return {item.get("id") for item in items if isinstance(item, dict)}


def validate_references(data: dict) -> tuple[str, str | None] | None:
    """全局引用完整性：所有已知跨对象引用必须解析到同快照中的 id。

    返回 None 表示无问题；返回 (verdict, reason) 表示首个问题。
    目标集合在快照中缺失时无法判定 → cannot_evaluate / missing_input；
    目标 id 不存在 → fail / dangling_reference。该检查在 check 返回 pass
    时统一执行，保证引用完整性不只作用于 G-C1。
    """
    actor_ids = ids(data.get("actors") or [])
    outcome_ids = ids(data.get("outcomes") or [])
    commitment_ids = ids(data.get("commitments") or [])
    deliverable_ids = ids(data.get("deliverables") or [])
    constraint_ids = ids(data.get("constraints") or [])
    assertion_ids = ids(data.get("assertions") or [])
    contract_ids = ids(data.get("contracts") or [])
    project_ids = ids(data.get("projects") or [])
    record_ids = ids(data.get("tailoring_records") or [])

    checks: list[tuple[str, str, set | None, str | None]] = [
        ("commitments", "by", actor_ids, "actors"),
        ("commitments", "to", outcome_ids, "outcomes"),
        ("commitments", "accountable_by", actor_ids, "actors"),
        ("commitments", "responsible_by", actor_ids, "actors"),
        ("commitments", "contract", contract_ids, "contracts"),
        ("commitments", "constrained_by", constraint_ids, "constraints"),
        ("constraints", "constrains", outcome_ids | commitment_ids, "outcomes"),
        ("deliverables", "asserted_by", assertion_ids, "assertions"),
        ("deliverables", "constrained_by", constraint_ids, "constraints"),
        ("changes", "constraint", constraint_ids, "constraints"),
        ("charters", "project", project_ids, "projects"),
        ("charters", "accountable", actor_ids, "actors"),
        ("charters", "authorizing_assertion", assertion_ids, "assertions"),
        ("tailoring_actions", "record", record_ids, "tailoring_records"),
        ("autonomy_grants", "actor", actor_ids, "actors"),
        ("autonomy_grants", "assertions", assertion_ids, "assertions"),
        ("contracts", "constrained_by", constraint_ids, "constraints"),
        ("tailoring_records", "approver", actor_ids, "actors"),
    ]
    for collection, field, target_ids, target_collection in checks:
        items = data.get(collection)
        if items is None:
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            ref = item.get(field)
            if ref in (None, "", []):
                continue
            refs = ref if isinstance(ref, list) else [ref]
            for ref_id in refs:
                if not isinstance(ref_id, str):
                    return "cannot_evaluate", "undefined_object_type"
                if target_collection not in data or data[target_collection] is None:
                    return "cannot_evaluate", "missing_input"
                if ref_id not in target_ids:
                    return "fail", "dangling_reference"

    # 列表型引用：charters.outcomes / charters.constraints。
    for charter in data.get("charters") or []:
        if not isinstance(charter, dict):
            continue
        for field, target_ids, target_collection in (
            ("outcomes", outcome_ids, "outcomes"),
            ("constraints", constraint_ids, "constraints"),
        ):
            refs = charter.get(field) or []
            for ref_id in refs:
                if target_collection not in data or data[target_collection] is None:
                    return "cannot_evaluate", "missing_input"
                if ref_id not in target_ids:
                    return "fail", "dangling_reference"

    # changes.target：按 type 选择目标集合。
    for change in data.get("changes") or []:
        if not isinstance(change, dict):
            continue
        target = change.get("target")
        if not isinstance(target, dict):
            continue
        target_type, target_id = target.get("type"), target.get("id")
        if target_type == "Commitment" and target_id and target_id not in commitment_ids:
            return "fail", "dangling_reference"
        if target_type == "Deliverable" and target_id and target_id not in deliverable_ids:
            return "fail", "dangling_reference"

    # assertions 的 about/deliverable/subject 指向 Deliverable；内嵌断言同样适用。
    def check_assertion_refs(assertions) -> tuple[str, str | None] | None:
        for assertion in assertions or []:
            if not isinstance(assertion, dict):
                continue
            for field in ("about", "deliverable", "subject"):
                ref = assertion.get(field)
                if not ref:
                    continue
                if "deliverables" not in data or data["deliverables"] is None:
                    return "cannot_evaluate", "missing_input"
                if ref not in deliverable_ids:
                    return "fail", "dangling_reference"
            confirmation = assertion.get("accountable_confirmation")
            if confirmation:
                if "actors" not in data or data["actors"] is None:
                    return "cannot_evaluate", "missing_input"
                if confirmation not in actor_ids:
                    return "fail", "dangling_reference"
        return None

    issue = check_assertion_refs(data.get("assertions"))
    if issue:
        return issue
    for deliverable in data.get("deliverables") or []:
        if isinstance(deliverable, dict):
            issue = check_assertion_refs(deliverable.get("assertions"))
            if issue:
                return issue
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
# 每个函数返回 (verdict, reason)。reason 为稳定原因码；pass 时为 None。


def check_project_minimal_existence(data: dict) -> tuple[str, str | None]:
    guard = require_fields(data, REQUIRED_KEYS["PROJECT_MINIMAL_EXISTENCE"])
    if guard:
        return guard
    actor_ids = {item.get("id") for item in data["actors"]}
    outcome_ids = {item.get("id") for item in data["outcomes"]}
    if not data["actors"]:
        return "fail", "missing_actor"
    if not data["outcomes"]:
        return "fail", "missing_outcome"
    if not data["commitments"]:
        return "fail", "missing_commitment"
    if not data["constraints"]:
        return "fail", "missing_constraint"
    for commitment in data["commitments"]:
        if commitment.get("by") not in actor_ids or commitment.get("to") not in outcome_ids:
            return "fail", "broken_commitment_endpoint"
    commitment_ids = {item.get("id") for item in data["commitments"]}
    for constraint in data["constraints"]:
        target = constraint.get("constrains")
        if not target or target not in (outcome_ids | commitment_ids):
            return "fail", "constraint_not_applied"
    return "pass", None


def check_constraint_anchor(data: dict) -> tuple[str, str | None]:
    guard = require_fields(data, REQUIRED_KEYS["CONSTRAINT_ANCHOR_REQUIRED"])
    if guard:
        return guard
    constraint_ids = {item.get("id") for item in data["constraints"]}
    for item in list(data["commitments"]) + list(data["deliverables"]):
        node_type = item.get("node_type")
        if node_type is not None and node_type not in ("ManagementActivity", "ManagementArtifact"):
            return "cannot_evaluate", "undefined_object_type"
        refs = item.get("constrained_by") or []
        if not refs or any(ref not in constraint_ids for ref in refs):
            return "fail", "unanchored_management_item"
    return "pass", None


def check_deliverable_assertion(data: dict) -> tuple[str, str | None]:
    guard = require_fields(data, REQUIRED_KEYS["DELIVERABLE_ASSERTION_LINK"])
    if guard:
        return guard
    assertion_by_id = {item.get("id"): item for item in data["assertions"]}
    for deliverable in data["deliverables"]:
        deliverable_id = deliverable.get("id")
        refs = deliverable.get("asserted_by") or []
        if any(ref not in assertion_by_id for ref in refs):
            return "fail", "dangling_reference"
        about_ids = [aid for aid, item in assertion_by_id.items() if item.get("about") == deliverable_id]
        if not refs and not about_ids:
            return "fail", "deliverable_without_assertion"
        for assertion_id in list(dict.fromkeys(list(refs) + sorted(about_ids))):
            assertion = assertion_by_id[assertion_id]
            if not assertion.get("statement") or assertion.get("statement_kind") not in STATEMENT_KINDS:
                return "fail", "assertion_without_content"
            if assertion.get("about") != deliverable_id:
                return "fail", "assertion_about_mismatch"
    return "pass", None


def check_change_constraint(data: dict) -> tuple[str, str | None]:
    guard = require_fields(data, REQUIRED_KEYS["CHANGE_CONSTRAINT_LINK"])
    if guard:
        return guard
    constraint_ids = {item.get("id") for item in data["constraints"]}
    commitment_ids = {item.get("id") for item in data.get("commitments") or []}
    deliverable_ids = {item.get("id") for item in data.get("deliverables") or []}
    for change in data["changes"]:
        if change.get("constraint") not in constraint_ids:
            return "fail", "missing_constraint_link"
        if change.get("relation") not in CHANGE_RELATIONS:
            return "fail", "invalid_change_relation"
        target = change.get("target")
        if not isinstance(target, dict) or not target.get("type") or not target.get("id"):
            return "fail", "missing_change_target"
        if target["type"] not in CHANGE_TARGET_TYPES:
            return "fail", "invalid_change_target"
        known = commitment_ids if target["type"] == "Commitment" else deliverable_ids
        if target["id"] not in known:
            return "fail", "invalid_change_target"
    return "pass", None


def check_role_minimal(data: dict) -> tuple[str, str | None]:
    guard = require_fields(data, REQUIRED_KEYS["ROLE_MINIMAL_COMPLETENESS"])
    if guard:
        return guard
    actors = {item.get("id"): item for item in data["actors"]}
    for commitment in data["commitments"]:
        accountable = commitment.get("accountable_by")
        if not accountable:
            return "fail", "missing_accountable"
        if isinstance(accountable, list):
            return "fail", "multiple_accountable"
        actor = actors.get(accountable)
        if actor is None:
            return "fail", "unknown_accountable"
        if actor.get("type") not in ("HumanActor", "LegalEntity"):
            return "fail", "accountable_not_human"
        responsible = commitment.get("responsible_by") or []
        if not responsible:
            return "fail", "missing_responsible"
        if accountable in responsible and not commitment.get("role_merge_declaration"):
            return "fail", "missing_role_merge_declaration", "warn"
    return "pass", None


def check_dual_dimension(data: dict) -> tuple[str, str | None]:
    guard = require_fields(data, REQUIRED_KEYS["DUAL_DIMENSION_ANNOTATION"])
    if guard:
        return guard
    for item in data["management_items"]:
        if not item.get("process_group") or not item.get("subject_group"):
            return "fail", "missing_dimension"
    return "pass", None


def check_dimension_value(data: dict) -> tuple[str, str | None]:
    guard = require_fields(data, REQUIRED_KEYS["DIMENSION_VALUE_CLOSED"])
    if guard:
        return guard
    extension = {entry.get("value") for entry in data.get("subject_group_extension") or []}
    for item in data["management_items"]:
        if item.get("process_group") not in PROCESS_GROUPS:
            return "fail", "dimension_value_out_of_enum"
        subject = item.get("subject_group")
        if subject not in BASE_SUBJECT_GROUPS and subject not in extension:
            return "fail", "dimension_value_out_of_enum"
    return "pass", None


def check_assertion_mutual_exclusion(data: dict) -> tuple[str, str | None]:
    guard = require_fields(data, REQUIRED_KEYS["ASSERTION_MUTUAL_EXCLUSION"])
    if guard:
        return guard
    seen: dict[tuple, set] = {}
    for assertion in data["assertions"]:
        if assertion.get("state") != "active":
            continue
        key = (assertion.get("subject"), assertion.get("property"))
        seen.setdefault(key, set()).add(assertion.get("value"))
    if any(len(values) > 1 for values in seen.values()):
        return "fail", "mutually_exclusive_active_assertions"
    return "pass", None


def check_all_improvement(data: dict) -> tuple[str, str | None]:
    guard = require_fields(data, REQUIRED_KEYS["ALL_IMPROVEMENT_ASSUMPTION"])
    if guard:
        return guard
    for change in data["changes"]:
        relations = change.get("relations") or []
        assumption = change.get("assumption")
        status = assumption.get("status") if isinstance(assumption, dict) else None
        assumption_condition = (
            assumption.get("verification_condition") if isinstance(assumption, dict) else None
        )
        if relations and all(item == "mitigates" for item in relations):
            if not assumption or not (change.get("verification_condition") or assumption_condition):
                return "fail", "all_improvement_without_verification"
            if status == "expired" or (
                status == "pending" and not assumption.get("approved_by")
            ):
                return "cannot_evaluate", "assumption_unclosed"
        if change.get("approval_basis") and status != "satisfied":
            return "fail", "approval_basis_before_verification"
    return "pass", None


def check_ai_autonomy(data: dict) -> tuple[str, str | None]:
    guard = require_fields(data, REQUIRED_KEYS["AI_AUTONOMY_DELEGATION_AUDITABLE"])
    if guard:
        return guard
    actors = {item.get("id"): item for item in data["actors"]}
    assertions = {item.get("id"): item for item in data["assertions"]}
    for grant in data["autonomy_grants"]:
        actor_id = grant.get("actor")
        if actor_id not in actors:
            return "fail", "dangling_reference"
        path = grant.get("delegated_from")
        if not isinstance(path, dict):
            return "cannot_evaluate", "invalid_path"
        start = path.get("start") or actor_id
        steps = path.get("steps")
        reach = path.get("reach")
        if start not in actors or not isinstance(steps, list) or not steps:
            return "cannot_evaluate", "invalid_path"
        cursor = start
        for step in steps:
            if not isinstance(step, dict):
                return "cannot_evaluate", "invalid_path"
            if step.get("relation") != "delegated_from" or step.get("direction") != "out":
                return "cannot_evaluate", "invalid_path"
            if step.get("target_type") != "Actor":
                return "cannot_evaluate", "undefined_object_type"
            target_id = step.get("target_id")
            if not target_id:
                return "cannot_evaluate", "invalid_path"
            if target_id not in actors:
                return "fail", "dangling_reference"
            cursor = target_id
        if reach != "accountable":
            return "cannot_evaluate", "invalid_path"
        if actors[cursor].get("accountable") is not True:
            return "fail", "delegation_chain_not_accountable"
        covers: set = set()
        for assertion_id in grant.get("assertions") or []:
            assertion = assertions.get(assertion_id)
            if assertion is None:
                return "fail", "dangling_reference"
            covers.update(assertion.get("covers") or [])
            if assertion.get("kind") not in ASSERTION_KINDS:
                return "cannot_evaluate", "undefined_object_type"
            if assertion.get("kind") != "assumption" or not assertion.get("verification_condition"):
                return "fail", "assertion_incomplete"
            assumption = assertion.get("assumption")
            if isinstance(assumption, dict) and (
                assumption.get("status") == "expired"
                or (
                    assumption.get("status") == "pending"
                    and not assumption.get("approved_by")
                )
            ):
                return "cannot_evaluate", "assumption_unclosed"
        if not {"scope", "boundary", "revocation"} <= covers:
            return "fail", "assertion_incomplete"
    return "pass", None


def check_project_charter(data: dict) -> tuple[str, str | None]:
    guard = require_fields(data, REQUIRED_KEYS["PROJECT_CHARTER_EXISTENCE"])
    if guard:
        return guard
    charters = {item.get("project"): item for item in data["charters"]}
    for project in data["projects"]:
        if project.get("stage") != "executing":
            continue
        charter = charters.get(project.get("id"))
        if charter is None:
            return "fail", "missing_charter"
        required = ("outcomes", "constraints", "accountable", "authorizing_assertion")
        if any(not charter.get(key) for key in required):
            return "fail", "incomplete_charter"
    return "pass", None


def check_closure_acceptance(data: dict) -> tuple[str, str | None]:
    guard = require_fields(data, REQUIRED_KEYS["CLOSURE_ACCEPTANCE_LINK"])
    if guard:
        return guard
    for deliverable in data["deliverables"]:
        accepted = any(
            item.get("statement") in ACCEPTANCE_STATEMENTS and item.get("accountable_confirmation")
            for item in deliverable.get("assertions") or []
        )
        if not accepted:
            return "fail", "missing_acceptance_assertion"
    return "pass", None


def check_procurement_contract(data: dict) -> tuple[str, str | None]:
    guard = require_fields(data, REQUIRED_KEYS["PROCUREMENT_CONTRACT_ANCHOR"])
    if guard:
        return guard
    contracts = {item.get("id"): item for item in data["contracts"]}
    for commitment in data["commitments"]:
        if commitment.get("procurement") != "external":
            continue
        contract = contracts.get(commitment.get("contract"))
        if contract is None:
            return "fail", "missing_contract"
        required = ("deliverable_form", "acceptance_criteria", "constrained_by", "accountable_signature")
        if any(not contract.get(key) for key in required):
            return "fail", "incomplete_contract"
    return "pass", None


def check_schedule_evidence(data: dict) -> tuple[str, str | None]:
    guard = require_fields(data, REQUIRED_KEYS["SCHEDULE_EVIDENCE_LINK"])
    if guard:
        return guard
    for commitment in data["commitments"]:
        if not (commitment.get("deadline") or commitment.get("milestone")):
            continue
        evidence = commitment.get("evidence_assertions") or []
        if not evidence or any(not item.get("basis") for item in evidence):
            return "fail", "missing_schedule_evidence"
    return "pass", None


def check_tailoring_record(data: dict) -> tuple[str, str | None]:
    guard = require_fields(data, REQUIRED_KEYS["TAILORING_RECORD_EXISTENCE"])
    if guard:
        return guard
    records = {item.get("id"): item for item in data["tailoring_records"]}
    for action in data["tailoring_actions"]:
        record = records.get(action.get("record"))
        if record is None:
            return "fail", "missing_tailoring_record"
        if any(not record.get(key) for key in ("trimmed_rule", "rationale", "scope", "approver")):
            return "fail", "incomplete_tailoring_record"
    return "pass", None


def check_tailoring_non_trimmable(data: dict) -> tuple[str, str | None]:
    guard = require_fields(data, REQUIRED_KEYS["TAILORING_NON_TRIMMABLE_SET"])
    if guard:
        return guard
    for record in data["tailoring_records"]:
        if record.get("trimmed_rule") in NON_TRIMMABLE:
            return "fail", "non_trimmable_rule"
    return "pass", None


def check_tailoring_reassessment(data: dict) -> tuple[str, str | None]:
    guard = require_fields(data, REQUIRED_KEYS["TAILORING_REASSESSMENT_CONDITION"])
    if guard:
        return guard
    for record in data["tailoring_records"]:
        if record.get("reassessment_condition"):
            continue
        if record.get("permanent") is True and record.get("reason"):
            continue
        return "fail", "missing_reassessment_condition"
    return "pass", None


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
        if len(blocks) != 4:
            raise SystemExit(f"[失败] {section} 应有 4 个 YAML 块，实际 {len(blocks)} 个")
        for index in (0, 2):
            cases.append(
                {
                    "section": section,
                    "case": 1 if index == 0 else 2,
                    "check_id": check_id,
                    "source_rule": rule,
                    "input": load_yaml(blocks[index]),
                    "expected": load_yaml(blocks[index + 1]),
                }
            )
    return cases


def run_case(case: dict) -> dict:
    check_id = case["check_id"]
    expected = case["expected"] or {}
    severity, rule_status = SPEC[check_id][1], SPEC[check_id][2]
    data = case["input"] or {}
    applicability = data.get("applicability") or {}
    state = applicability.get("state") if isinstance(applicability, dict) else None
    if state == "inapplicable":
        verdict, reason = "not_applicable", None
    elif state == "pending":
        verdict, reason = "cannot_evaluate", "applicability_pending"
    else:
        result = CHECKS[check_id](data)
        verdict, reason = result[0], result[1]
        if len(result) > 2 and result[2]:
            severity = result[2]
        # 引用完整性全局生效：check 自身判 pass 时，再统一校验所有已知引用。
        if verdict == "pass":
            reference_issue = validate_references(data)
            if reference_issue:
                verdict, reason = reference_issue
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


def null_sweep() -> int:
    """负例实测：每个必需键单独取 null，必须返回 cannot_evaluate 而非崩溃。"""
    failures: list[str] = []
    total = 0
    for check_id, keys in REQUIRED_KEYS.items():
        for null_key in keys:
            total += 1
            data = {key: (None if key == null_key else []) for key in keys}
            try:
                result = CHECKS[check_id](data)
            except Exception as exc:  # noqa: BLE001 - 负例就是要捕获崩溃
                failures.append(f"{check_id}.{null_key}: 抛 {type(exc).__name__}: {exc}")
                continue
            verdict, reason = result[0], result[1]
            if (verdict, reason) != ("cannot_evaluate", "missing_input"):
                failures.append(
                    f"{check_id}.{null_key}: 期望 cannot_evaluate/missing_input，"
                    f"实际 {verdict}/{reason}"
                )
    for failure in failures:
        print(f"[FAIL] {failure}")
    print(f"null 负例：{total - len(failures)}/{total} 返回 cannot_evaluate，崩溃 {len(failures)} 处")
    return 0 if not failures else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="T-107 最小原型：执行 T-011 的 34 个样例")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    parser.add_argument(
        "--null-sweep", action="store_true", help="负例：必需键取 null 时不得抛异常"
    )
    args = parser.parse_args()
    if args.null_sweep:
        return null_sweep()
    root = Path(args.root)
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
        for case in cases:
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
