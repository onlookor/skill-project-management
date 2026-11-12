#!/usr/bin/env python3
"""核对 SOURCE_LEDGER.md 的编译落点。

检查每个 active 来源条目是否声明了 `compilation_landing`，以及落点是否真实存在：
  rule:<规则号>       -> GRAMMAR.md 的规则标题
  knowledge:<术语>    -> knowledge/anchored-entries.jsonl 的 term
  method:<方法号>     -> knowledge/methods/registry-skeleton.md 的 method_id
  check:<check_id>    -> validation/CHECKLIST.md 或 spec/methods/deterministic-checker.md
  pending:<TODO 编号> -> 记为待落点（警告，不构成错误）

退出码：0 通过（可有警告）；1 存在错误；2 无法解析登记表。
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "SOURCE_LEDGER.md"
GRAMMAR = ROOT / "GRAMMAR.md"
JSONL = ROOT / "knowledge" / "anchored-entries.jsonl"
METHODS = ROOT / "knowledge" / "methods" / "registry-skeleton.md"
CHECK_SOURCES = [
    ROOT / "validation" / "CHECKLIST.md",
    ROOT / "spec" / "methods" / "deterministic-checker.md",
]

LANDING_RE = re.compile(r"(rule|knowledge|method|check|pending):([A-Za-z0-9_.-]+)")


def fail_parse(message):
    print(f"[无法解析] {message}")
    sys.exit(2)


def read(path):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def parse_entries(text):
    if "### 条目表" not in text:
        fail_parse("未找到“### 条目表”小节")
    body = text.split("### 条目表", 1)[1]
    body = body.split("### 废止", 1)[0]
    entries = []
    for block in re.split(r"^#### ", body, flags=re.M)[1:]:
        lines = block.splitlines()
        ident = lines[0].strip()
        fields = {}
        for line in lines:
            match = re.match(r"\|\s*`?([A-Za-z_]+)`?\s*\|\s*(.*?)\s*\|\s*$", line)
            if match:
                fields[match.group(1)] = match.group(2)
        entries.append({"id": ident, "fields": fields})
    if not entries:
        fail_parse("条目表为空")
    return entries


def load_terms():
    terms = set()
    for line in read(JSONL).splitlines():
        if not line.strip():
            continue
        try:
            terms.add(json.loads(line)["term"])
        except (json.JSONDecodeError, KeyError):
            fail_parse("anchored-entries.jsonl 无法解析")
    return terms


def target_exists(kind, value, grammar, terms, methods, checks):
    if kind == "rule":
        return re.search(r"^\*\*" + re.escape(value) + r"（", grammar, re.M) is not None
    if kind == "knowledge":
        return value in terms
    if kind == "method":
        return value in methods
    if kind == "check":
        return any(value in text for text in checks)
    if kind == "pending":
        return bool(re.fullmatch(r"T-\d+", value))
    return False


def main():
    text = read(LEDGER)
    if not text:
        fail_parse("SOURCE_LEDGER.md 不存在或为空")
    entries = parse_entries(text)

    grammar = read(GRAMMAR)
    terms = load_terms()
    methods_text = read(METHODS)
    methods = set(re.findall(r"`(M-[A-Z]+-\d+)`", methods_text))
    checks = [read(path) for path in CHECK_SOURCES]

    errors = []
    warnings = []
    active_count = 0

    for entry in entries:
        ident = entry["id"]
        fields = entry["fields"]
        status = fields.get("status", "")
        if not status.startswith("`active`") and "active" not in status:
            continue
        active_count += 1
        landing = fields.get("compilation_landing", "")
        if not landing:
            errors.append(f"{ident}：active 条目缺少 compilation_landing")
            continue
        tokens = LANDING_RE.findall(landing)
        if not tokens:
            errors.append(f"{ident}：compilation_landing 中没有可识别的落点记号")
            continue
        for kind, value in tokens:
            if kind == "pending":
                if not target_exists(kind, value, grammar, terms, methods, checks):
                    errors.append(f"{ident}：pending 记号 {value} 不是 TODO 编号")
                else:
                    warnings.append(f"{ident}：落点待定（{value}），正文取得前不得被 grounding_ref 引用")
            elif not target_exists(kind, value, grammar, terms, methods, checks):
                errors.append(f"{ident}：落点 {kind}:{value} 不存在")

    for message in warnings:
        print(f"[警告] {message}")
    for message in errors:
        print(f"[错误] {message}")
    print(
        f"编译落点核对：{len(entries)} 个条目，{active_count} 个 active，"
        f"{len(errors)} 个错误，{len(warnings)} 个警告"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
