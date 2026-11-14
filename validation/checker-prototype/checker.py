#!/usr/bin/env python3
"""T-107 最小原型：按附录 A 判定列执行 T-011 的 34 个样例。

只使用标准库。输入为 spec/methods/deterministic-checker.md 中 A.1 的
YAML 谓词快照；输出 check_id / source_rule / severity / rule_status /
verdict / reason，并与样例的“期望输出”逐项比对。

判定依据只有附录 A 的“判定”列。规则正文严于判定列的三处（G-A1 约束
作用边、G-E2 assumption 形式、G-E1 severity 拆分）不实现，并在
COVERAGE_GAPS 中显式声明“未覆盖规则正文”。
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
# 原型物化的基础主题组：只含样例出现的值。完整 17 项依赖来源正文，
# 未物化的值可通过输入的 subject_group_extension 声明。
BASE_SUBJECT_GROUPS = {"planning", "lessons-learned"}
CHANGE_RELATIONS = {"mitigates", "exacerbates", "trades_off"}
NON_TRIMMABLE = {"G-A1", "G-A2", "G-C1", "G-D1", "G-E1"}
ACCEPTANCE_STATEMENTS = {"已验收", "已移交"}

COVERAGE_GAPS = {
    "PROJECT_MINIMAL_EXISTENCE": "未覆盖规则正文：Constraint 须作用于该 Outcome/Commitment（T-130 / G-002）",
    "CONSTRAINT_ANCHOR_REQUIRED": "未覆盖规则正文：管理活动/产物节点类型未在 schema 中枚举（G-001 / G-A2）",
    "ROLE_MINIMAL_COMPLETENESS": "未覆盖规则正文：决策类 Commitment 筛选未定义、severity 未拆分（G-001 / G-E1、G-004 / T-100）",
    "ALL_IMPROVEMENT_ASSUMPTION": "未覆盖规则正文：验证条件满足前不得作为批准依据的载体（G-001 / G-D2）",
    "AI_AUTONOMY_DELEGATION_AUDITABLE": "未覆盖规则正文：Assertion 以 assumption 形式存在并附验证条件（T-131 / G-003）",
}

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
    if any(key not in data for key in ("project", "actors", "outcomes", "commitments", "constraints")):
        return "cannot_evaluate", "missing_input"
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
    return "pass", None


def check_constraint_anchor(data: dict) -> tuple[str, str | None]:
    if any(key not in data for key in ("commitments", "deliverables", "constraints")):
        return "cannot_evaluate", "missing_input"
    constraint_ids = {item.get("id") for item in data["constraints"]}
    for item in list(data["commitments"]) + list(data["deliverables"]):
        refs = item.get("constrained_by") or []
        if not refs or any(ref not in constraint_ids for ref in refs):
            return "fail", "unanchored_management_item"
    return "pass", None


def check_deliverable_assertion(data: dict) -> tuple[str, str | None]:
    if any(key not in data for key in ("deliverables", "assertions")):
        return "cannot_evaluate", "missing_input"
    assertion_ids = {item.get("id") for item in data["assertions"]}
    for deliverable in data["deliverables"]:
        refs = deliverable.get("asserted_by") or []
        if not refs or any(ref not in assertion_ids for ref in refs):
            return "fail", "deliverable_without_assertion"
    return "pass", None


def check_change_constraint(data: dict) -> tuple[str, str | None]:
    if any(key not in data for key in ("changes", "constraints")):
        return "cannot_evaluate", "missing_input"
    constraint_ids = {item.get("id") for item in data["constraints"]}
    for change in data["changes"]:
        if change.get("constraint") not in constraint_ids:
            return "fail", "missing_constraint_link"
        if change.get("relation") not in CHANGE_RELATIONS:
            return "fail", "invalid_change_relation"
    return "pass", None


def check_role_minimal(data: dict) -> tuple[str, str | None]:
    if any(key not in data for key in ("actors", "commitments")):
        return "cannot_evaluate", "missing_input"
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
            return "fail", "missing_role_merge_declaration"
    return "pass", None


def check_dual_dimension(data: dict) -> tuple[str, str | None]:
    if "management_items" not in data:
        return "cannot_evaluate", "missing_input"
    for item in data["management_items"]:
        if not item.get("process_group") or not item.get("subject_group"):
            return "fail", "missing_dimension"
    return "pass", None


def check_dimension_value(data: dict) -> tuple[str, str | None]:
    if "management_items" not in data:
        return "cannot_evaluate", "missing_input"
    extension = {entry.get("value") for entry in data.get("subject_group_extension") or []}
    for item in data["management_items"]:
        if item.get("process_group") not in PROCESS_GROUPS:
            return "fail", "dimension_value_out_of_enum"
        subject = item.get("subject_group")
        if subject not in BASE_SUBJECT_GROUPS and subject not in extension:
            return "fail", "dimension_value_out_of_enum"
    return "pass", None


def check_assertion_mutual_exclusion(data: dict) -> tuple[str, str | None]:
    if "assertions" not in data:
        return "cannot_evaluate", "missing_input"
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
    if "changes" not in data:
        return "cannot_evaluate", "missing_input"
    for change in data["changes"]:
        relations = change.get("relations") or []
        if relations and all(item == "mitigates" for item in relations):
            if not change.get("assumption") or not change.get("verification_condition"):
                return "fail", "all_improvement_without_verification"
    return "pass", None


def check_ai_autonomy(data: dict) -> tuple[str, str | None]:
    if any(key not in data for key in ("actors", "autonomy_grants", "assertions")):
        return "cannot_evaluate", "missing_input"
    actors = {item.get("id"): item for item in data["actors"]}
    assertions = {item.get("id"): item for item in data["assertions"]}
    for grant in data["autonomy_grants"]:
        cursor = grant.get("delegated_from")
        visited: set = set()
        accountable = False
        while cursor and cursor not in visited:
            visited.add(cursor)
            actor = actors.get(cursor)
            if actor is None:
                break
            if actor.get("accountable") is True:
                accountable = True
                break
            cursor = actor.get("delegated_from")
        if not accountable:
            return "fail", "delegation_chain_not_accountable"
        covers: set = set()
        for assertion_id in grant.get("assertions") or []:
            assertion = assertions.get(assertion_id) or {}
            covers.update(assertion.get("covers") or [])
        if not {"scope", "boundary", "revocation"} <= covers:
            return "fail", "assertion_incomplete"
    return "pass", None


def check_project_charter(data: dict) -> tuple[str, str | None]:
    if any(key not in data for key in ("projects", "charters")):
        return "cannot_evaluate", "missing_input"
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
    if "deliverables" not in data:
        return "cannot_evaluate", "missing_input"
    for deliverable in data["deliverables"]:
        accepted = any(
            item.get("statement") in ACCEPTANCE_STATEMENTS and item.get("accountable_confirmation")
            for item in deliverable.get("assertions") or []
        )
        if not accepted:
            return "fail", "missing_acceptance_assertion"
    return "pass", None


def check_procurement_contract(data: dict) -> tuple[str, str | None]:
    if any(key not in data for key in ("commitments", "contracts")):
        return "cannot_evaluate", "missing_input"
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
    if "commitments" not in data:
        return "cannot_evaluate", "missing_input"
    for commitment in data["commitments"]:
        if not (commitment.get("deadline") or commitment.get("milestone")):
            continue
        evidence = commitment.get("evidence_assertions") or []
        if not evidence or any(not item.get("basis") for item in evidence):
            return "fail", "missing_schedule_evidence"
    return "pass", None


def check_tailoring_record(data: dict) -> tuple[str, str | None]:
    if any(key not in data for key in ("tailoring_actions", "tailoring_records")):
        return "cannot_evaluate", "missing_input"
    records = {item.get("id"): item for item in data["tailoring_records"]}
    for action in data["tailoring_actions"]:
        record = records.get(action.get("record"))
        if record is None:
            return "fail", "missing_tailoring_record"
        if any(not record.get(key) for key in ("trimmed_rule", "rationale", "scope", "approver")):
            return "fail", "incomplete_tailoring_record"
    return "pass", None


def check_tailoring_non_trimmable(data: dict) -> tuple[str, str | None]:
    if "tailoring_records" not in data:
        return "cannot_evaluate", "missing_input"
    for record in data["tailoring_records"]:
        if record.get("trimmed_rule") in NON_TRIMMABLE:
            return "fail", "non_trimmable_rule"
    return "pass", None


def check_tailoring_reassessment(data: dict) -> tuple[str, str | None]:
    if "tailoring_records" not in data:
        return "cannot_evaluate", "missing_input"
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
    verdict, reason = CHECKS[check_id](case["input"] or {})
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


def main() -> int:
    parser = argparse.ArgumentParser(description="T-107 最小原型：执行 T-011 的 34 个样例")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    args = parser.parse_args()
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
        for check_id, note in COVERAGE_GAPS.items():
            print(f"  - {check_id}：{note}")
    return 0 if len(passed) == len(cases) else 1


if __name__ == "__main__":
    sys.exit(main())
