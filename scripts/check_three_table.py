#!/usr/bin/env python3
"""三表机械对照：GRAMMAR.md 规则正文 ↔ 附录 A 判定列 ↔ 输入 schema。

覆盖三对关系与两类闭合检查（ADR-0013 / P1、P2、P8）：

1. 正文 → 判定列：每条规则有承接的 `check_id`；判定列的 `source_rule` 都存在。
2. 判定列 → schema：`check_id` 集合一致；判定列引用的字段名在 schema 出现过。
3. 正文 → schema：规则陈述中的机制术语在 schema 出现过（未定义即报错）。
4. 子句闭合：A.2 的 clause 均被某个 `check_id` 覆盖，或标 `not-checked` 并写理由；
   判定列引用的 clause 都存在于 A.2。
5. 枚举封闭：判定列中的小写枚举集合必须来自 schema 第 4 节。

用法：python3 scripts/check_three_table.py [--root DIR]
退出码：0 = 通过；1 = 存在错误；2 = 结构无法解析。
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

GRAMMAR = "GRAMMAR.md"
METHOD = "spec/methods/deterministic-checker.md"
SCHEMA = "spec/CHECKER_INPUT_SCHEMA.md"

RULE_RE = re.compile(r"\*\*(G-[A-G]\d)（")
CLAUSE_RE = re.compile(r"^`(G-[A-G]\d#\d+)`$")
CHECK_RE = re.compile(r"^`([A-Z_]{3,})`$")
FIELD_RE = re.compile(r"`([a-z][a-z0-9_]{2,})`")
TERM_RE = re.compile(r"`([A-Z][A-Za-z]{1,})`")
CLAUSE_ID_RE = re.compile(r"G-[A-G]\d#\d+")
CLAUSE_RANGE_RE = re.compile(r"`(G-[A-G]\d)#(\d+)`\s*[–\-]\s*`G-[A-G]\d#(\d+)`")
GLOSSARY = "GLOSSARY.md"


def repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("[错误] 当前目录不在 git 仓库中，无法定位三表文件。")
        sys.exit(2)
    return Path(result.stdout.strip())


def split_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def parse_grammar(text: str) -> dict[str, str]:
    """返回 {规则号: 规则陈述正文}。"""
    rules: dict[str, str] = {}
    matches = list(RULE_RE.finditer(text))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        rules[match.group(1)] = text[match.end() : end]
    return rules


def parse_method(text: str):
    """返回 (A 表 {check_id: {...}}, A.2 子句 {clause: {...}})。"""
    checks: dict[str, dict] = {}
    clauses: dict[str, dict] = {}
    for line in text.splitlines():
        cells = split_row(line)
        if not cells:
            continue
        first = cells[0]
        check_match = CHECK_RE.match(first)
        rule_match = CLAUSE_RE.match(first)
        if check_match and len(cells) >= 5 and re.fullmatch(r"G-[A-G]\d", cells[1]):
            checks[check_match.group(1)] = {
                "rule": cells[1],
                "clauses": cells[2],
                "verdict": cells[4],
            }
        elif rule_match and len(cells) == 6:
            clauses[rule_match.group(1)] = {
                "rule": cells[1],
                "clause": cells[2],
                "check": cells[3].strip("`"),
                "severity": cells[4],
                "status": cells[5],
            }
    return checks, clauses


def expand_clauses(cell: str) -> list[str]:
    """把“`G-A1#1`–`G-A1#6`”展开为全部 clause id，并合并单独的 id。"""
    found: list[str] = []
    for prefix, start, end in CLAUSE_RANGE_RE.findall(cell):
        for number in range(int(start), int(end) + 1):
            found.append(f"{prefix}#{number}")
    for clause in CLAUSE_ID_RE.findall(cell):
        if clause not in found:
            found.append(clause)
    return found


def parse_schema(text: str):
    """返回 (schema 中 check_id 集合, schema 词汇集合, schema 枚举值集合)。"""
    checks: set[str] = set()
    for line in text.splitlines():
        cells = split_row(line)
        if cells and len(cells) >= 3 and CHECK_RE.match(cells[0]):
            checks.add(CHECK_RE.match(cells[0]).group(1))
    vocab = set(re.findall(r"`([A-Za-z][A-Za-z0-9_\-]*)`", text))
    enums = set()
    in_enum = False
    for line in text.splitlines():
        if line.startswith("## 4."):
            in_enum = True
            continue
        if in_enum and line.startswith("## "):
            break
        if in_enum:
            cells = split_row(line)
            if cells and len(cells) >= 2:
                for value in re.findall(r"`([a-z][a-z0-9\-]*)`", cells[1]):
                    enums.add(value)
    return checks, vocab, enums


def parse_glossary(text: str) -> set[str]:
    """术语表中的机制术语也是合法判定对象（见 knowledge/anchored-entries.jsonl）。"""
    terms = set(re.findall(r"\*\*T-[A-F]-\d{3}\s+([^*]+?)\*\*", text))
    return terms | set(TERM_RE.findall(text))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="仓库根目录；默认由 git 推断")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else repo_root()
    try:
        grammar_text = (root / GRAMMAR).read_text(encoding="utf-8")
        method_text = (root / METHOD).read_text(encoding="utf-8")
        schema_text = (root / SCHEMA).read_text(encoding="utf-8")
        glossary_text = (root / GLOSSARY).read_text(encoding="utf-8")
    except FileNotFoundError as error:
        print(f"[错误] 缺少三表文件：{error.filename}")
        return 2

    rules = parse_grammar(grammar_text)
    checks, clauses = parse_method(method_text)
    schema_checks, vocab, enums = parse_schema(schema_text)
    vocab |= parse_glossary(glossary_text)
    if not rules or not checks or not clauses or not schema_checks:
        print("[错误] 三表解析结果为空，结构无法解析。")
        return 2

    errors: list[str] = []

    # 1. 正文 → 判定列
    covered_rules = {item["rule"] for item in checks.values()}
    for rule in sorted(set(rules) - covered_rules):
        errors.append(f"[错误] 规则 {rule} 在附录 A 没有承接的 check_id")
    for rule in sorted(covered_rules - set(rules)):
        errors.append(f"[错误] 附录 A 引用了 GRAMMAR 中不存在的规则 {rule}")

    # 2. 判定列 → schema
    for check_id in sorted(set(checks) - schema_checks):
        errors.append(f"[错误] check_id {check_id} 在输入 schema 第 3 节没有输入域")
    for check_id in sorted(schema_checks - set(checks)):
        errors.append(f"[错误] 输入 schema 第 3 节多出附录 A 未注册的 {check_id}")

    # 3. 正文 → schema（机制术语必须已定义）
    for rule, body in rules.items():
        for term in sorted(set(TERM_RE.findall(body))):
            if term not in vocab:
                errors.append(f"[错误] 规则 {rule} 使用机制术语 `{term}`，输入 schema 未定义")

    # 4. 子句闭合
    referenced: set[str] = set()
    for check_id, item in checks.items():
        declared = expand_clauses(item["clauses"])
        if not declared:
            errors.append(f"[错误] {check_id} 的“子句”列没有 clause id")
        for clause in declared:
            if clause not in clauses:
                errors.append(f"[错误] {check_id} 引用了 A.2 中不存在的子句 {clause}")
            referenced.add(clause)
    for clause, item in clauses.items():
        if item["status"].startswith("not-checked"):
            if "理由" not in item["clause"] and len(item["clause"]) < 8:
                errors.append(f"[错误] 子句 {clause} 标为 not-checked 但未写理由")
            continue
        if clause not in referenced:
            errors.append(f"[错误] 子句 {clause} 未被任何 check_id 的“子句”列引用")

    # 5. 枚举封闭（只检查全小写集合；规则号集合跳过）
    for check_id, item in checks.items():
        for group in re.findall(r"\{([^{}]+)\}", item["verdict"]):
            values = [value.strip().strip("`") for value in group.split(",")]
            if all(re.fullmatch(r"[a-z][a-z0-9\-]*", value) for value in values):
                for value in values:
                    if value not in enums:
                        errors.append(
                            f"[错误] {check_id} 的判定列使用未封闭枚举值 `{value}`"
                        )

    print(
        f"三表对照：正文 {len(rules)} 条规则，判定列 {len(checks)} 个 check_id / "
        f"{len(clauses)} 个子句，schema {len(schema_checks)} 个输入域。"
    )
    if errors:
        for error in errors:
            print(error)
        print(f"[失败] {len(errors)} 项错误。")
        return 1
    print("[通过] 正文、判定列、schema 三表一致；子句覆盖完整；枚举闭合。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
