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
import copy
import json
import re
import sys
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
EXTENSION_RELATIONS = {"specializes", "cross_cuts"}
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
# 每个函数返回 (verdict, reason)。reason 为稳定原因码；pass 时为 None。


def check_project_minimal_existence(data: dict) -> tuple[str, str | None]:
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
    for item in data["management_items"]:
        if not item.get("process_group") or not item.get("subject_group"):
            return "fail", "missing_dimension"
    return "pass", None


def check_dimension_value(data: dict) -> tuple[str, str | None]:
    extension: set[str] = set()
    for entry in data.get("subject_group_extension") or []:
        value = entry.get("value")
        if (
            isinstance(value, str)
            and entry.get("relation") in EXTENSION_RELATIONS
            and entry.get("base") in BASE_SUBJECT_GROUPS
            and value not in BASE_SUBJECT_GROUPS
        ):
            extension.add(value)
    for item in data["management_items"]:
        if item.get("process_group") not in PROCESS_GROUPS:
            return "fail", "dimension_value_out_of_enum"
        subject = item.get("subject_group")
        if subject not in BASE_SUBJECT_GROUPS and subject not in extension:
            return "fail", "dimension_value_out_of_enum"
    for entry in data.get("subject_group_extension") or []:
        value = entry.get("value")
        if (
            not isinstance(value, str)
            or entry.get("relation") not in EXTENSION_RELATIONS
            or entry.get("base") not in BASE_SUBJECT_GROUPS
            or value in BASE_SUBJECT_GROUPS
        ):
            return "fail", "invalid_subject_group_extension"
    return "pass", None


def check_assertion_mutual_exclusion(data: dict) -> tuple[str, str | None]:
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
    for deliverable in data["deliverables"]:
        accepted = any(
            item.get("statement") in ACCEPTANCE_STATEMENTS and item.get("accountable_confirmation")
            for item in deliverable.get("assertions") or []
        )
        if not accepted:
            return "fail", "missing_acceptance_assertion"
    return "pass", None


def check_procurement_contract(data: dict) -> tuple[str, str | None]:
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
    for commitment in data["commitments"]:
        if not (commitment.get("deadline") or commitment.get("milestone")):
            continue
        evidence = commitment.get("evidence_assertions") or []
        if not evidence or any(not item.get("basis") for item in evidence):
            return "fail", "missing_schedule_evidence"
    return "pass", None


def check_tailoring_record(data: dict) -> tuple[str, str | None]:
    records = {item.get("id"): item for item in data["tailoring_records"]}
    for action in data["tailoring_actions"]:
        record = records.get(action.get("record"))
        if record is None:
            return "fail", "missing_tailoring_record"
        if any(not record.get(key) for key in ("trimmed_rule", "rationale", "scope", "approver")):
            return "fail", "incomplete_tailoring_record"
    return "pass", None


def check_tailoring_non_trimmable(data: dict) -> tuple[str, str | None]:
    for record in data["tailoring_records"]:
        if record.get("trimmed_rule") in NON_TRIMMABLE:
            return "fail", "non_trimmable_rule"
    return "pass", None


def check_tailoring_reassessment(data: dict) -> tuple[str, str | None]:
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


def evaluate(check_id: str, data: dict) -> tuple[str, str | None, str]:
    """全部 check 的唯一入口：适用性 → null 归一化 → 判定 → 全局引用校验。"""
    severity = SPEC[check_id][1]
    applicability = data.get("applicability") or {}
    state = applicability.get("state") if isinstance(applicability, dict) else None
    if state == "inapplicable":
        return "not_applicable", None, severity
    if state == "pending":
        return "cannot_evaluate", "applicability_pending", severity
    # 一次归一化覆盖三种情形，各 check 函数不再各自打补丁。
    if find_null(data) is not None:
        return "cannot_evaluate", "missing_input", severity
    result = CHECKS[check_id](data)
    verdict, reason = result[0], result[1]
    if len(result) > 2 and result[2]:
        severity = result[2]
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


def null_sweep(root: Path) -> int:
    """负例实测：顶层键、嵌套对象键、数组元素为 null 都必须 cannot_evaluate。"""
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
    for case in extract_cases(method):
        check_id = case["check_id"]
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
    parser = argparse.ArgumentParser(description="T-107 最小原型：执行 T-011 的 34 个样例")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    parser.add_argument(
        "--null-sweep", action="store_true", help="负例：任意层级取 null 时不得抛异常"
    )
    parser.add_argument(
        "--input-domain",
        action="store_true",
        help="检查样例中出现的引用目标集合是否都已在 schema §3 声明",
    )
    args = parser.parse_args()
    root = Path(args.root)
    if args.null_sweep:
        return null_sweep(root)
    if args.input_domain:
        issues = input_domain_issues(root)
        for issue in issues:
            print(f"[FAIL] {issue}")
        print(f"输入域闭包：{len(issues)} 处缺口")
        return 0 if not issues else 1
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
