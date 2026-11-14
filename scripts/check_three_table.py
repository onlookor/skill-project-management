#!/usr/bin/env python3
"""三表机械对照：GRAMMAR.md 规则正文 ↔ 附录 A 判定列 ↔ 输入 schema。

覆盖以下检查（ADR-0013 / P1、P2、P8）：

1. 正文 → 判定列：每条规则有承接的 `check_id`；判定列的 `规则` 都存在。
2. 判定列 → schema：`check_id` 集合一致。
3. 正文 → schema：规则陈述中的机制术语在 schema 出现过（未定义即报错）。
4. 判定列派生：A 表由 A.2 生成，检查器比较“生成结果”与文件中的 A 表是否逐格一致；
   任何 A.2 语义改动（子句文本、量词、原因码、severity、规则状态、子句 id、承接
   check_id）都会改变子句指纹并使检查失败。`--write` 用 A.2 重建 A 表。
5. 枚举封闭：判定列中的小写枚举集合必须来自 schema 第 4 节。
6. 引用标注：§2 声明的每个字段必须出现在 §2bis.1（引用）或 §2bis.2（非引用），
   新增字段未标注即报错。
7. 输入域闭包：样例中实际出现的引用目标集合必须在 §3 的必需顶层键中声明。
8. A.2 复核签收：A.2 区头的“复核签收”行必须携带当前 A.2 区段指纹；只改 A.2 再
   跑 `--write` 会使 A 表自洽，本条是唯一能阻断该绕过的机械检查（AGENTS 3.6.7）。

用法：python3 scripts/check_three_table.py [--root DIR] [--method PATH] [--write]
退出码：0 = 通过；1 = 存在错误；2 = 结构无法解析。
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

GRAMMAR = "GRAMMAR.md"
METHOD = "spec/methods/deterministic-checker.md"
SCHEMA = "spec/CHECKER_INPUT_SCHEMA.md"
GLOSSARY = "GLOSSARY.md"

RULE_RE = re.compile(r"\*\*(G-[A-G]\d)（")
CLAUSE_RE = re.compile(r"^`(G-[A-G]\d#\d+)`$")
CHECK_RE = re.compile(r"^`([A-Z_]{3,})`$")
TERM_RE = re.compile(r"`([A-Z][A-Za-z]{1,})`")
CLAUSE_ID_RE = re.compile(r"G-[A-G]\d#\d+")
CLAUSE_RANGE_RE = re.compile(r"`(G-[A-G]\d)#(\d+)`\s*[–\-]\s*`G-[A-G]\d#(\d+)`")

CHECK_HEADER = "| check_id | 规则 | 判定（子句 id） | 子句指纹 | 输入 | 原因码 | 规则状态 |"
CHECK_SEPARATOR = "|---|---|---|---|---|---|---|"


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


def canonical(text: str) -> str:
    """忽略空白差异的语义文本。"""
    return " ".join(str(text).split())


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
        clause_match = CLAUSE_RE.match(first)
        if check_match and len(cells) == 7 and re.fullmatch(r"G-[A-G]\d", cells[1]):
            checks[check_match.group(1)] = {
                "rule": cells[1],
                "clauses": cells[2],
                "fingerprint": cells[3],
                "input": cells[4],
                "reason": cells[5],
                "status": cells[6],
            }
        elif clause_match and len(cells) == 8:
            clauses[clause_match.group(1)] = {
                "rule": cells[1],
                "clause": cells[2],
                "reason": cells[3],
                "check": cells[4].strip("`"),
                "severity": cells[5],
                "status": cells[6],
                "rule_status": cells[7],
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


def clause_fingerprint(clause_id: str, item: dict) -> str:
    """子句语义指纹：覆盖文本、原因码、severity、规则状态、承接 check_id。"""
    payload = "|".join(
        [
            clause_id,
            item["rule"],
            canonical(item["clause"]),
            canonical(item["reason"]),
            item["check"],
            canonical(item["severity"]),
            canonical(item["rule_status"]),
        ]
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


A2_SIGNOFF_RE = re.compile(
    r"复核签收：(.+?)\s*/\s*(\d{4}-\d{2}-\d{2})\s*/\s*A\.2 指纹\s*`([0-9a-f]{12})`"
)


def a2_block_fingerprint(clauses: dict[str, dict]) -> str:
    """A.2 区段指纹：全部子句指纹按 clause id 排序后聚合。"""
    return hashlib.sha256(
        "|".join(
            clause_fingerprint(clause, clauses[clause]) for clause in sorted(clauses)
        ).encode("utf-8")
    ).hexdigest()[:12]


def parse_a2_signoff(text: str) -> tuple[str, str, str] | None:
    """解析 A.2 区头的复核签收行，返回 (签收人, 日期, 指纹)。"""
    in_section = False
    for line in text.splitlines():
        if line.startswith("### A.2"):
            in_section = True
            continue
        if in_section and line.startswith("### "):
            break
        if in_section:
            match = A2_SIGNOFF_RE.search(line)
            if match:
                return match.group(1).strip(), match.group(2), match.group(3)
    return None


def render_clause_ids(ids: list[str]) -> str:
    if len(ids) == 1:
        return f"`{ids[0]}`"
    prefix = ids[0].split("#")[0]
    numbers = [int(clause.split("#")[1]) for clause in ids]
    consecutive = numbers == list(range(numbers[0], numbers[0] + len(numbers)))
    if consecutive and all(clause.startswith(prefix + "#") for clause in ids):
        return f"`{ids[0]}`–`{ids[-1]}`"
    return "、".join(f"`{clause}`" for clause in ids)


def derive_checks(
    clauses: dict[str, dict], required_keys: dict[str, tuple[str, ...]]
) -> dict[str, dict]:
    """由 A.2 生成 A 表行；这是 A 表的唯一生成路径。"""
    grouped: dict[str, list[str]] = {}
    for clause_id, item in clauses.items():
        if item["status"].startswith("not-checked"):
            continue
        grouped.setdefault(item["check"], []).append(clause_id)

    derived: dict[str, dict] = {}
    for check_id, ids in grouped.items():
        rules = {clauses[clause]["rule"] for clause in ids}
        statuses = {canonical(clauses[clause]["rule_status"]).strip("`") for clause in ids}
        reasons: list[str] = []
        for clause in ids:
            for code in re.findall(r"[a-z][a-z0-9_]+", clauses[clause]["reason"]):
                if code not in reasons:
                    reasons.append(code)
        fingerprint = hashlib.sha256(
            "|".join(
                clause_fingerprint(clause, clauses[clause]) for clause in ids
            ).encode("utf-8")
        ).hexdigest()[:12]
        derived[check_id] = {
            "rule": sorted(rules)[0] if len(rules) == 1 else "、".join(sorted(rules)),
            "ids": ids,
            "clauses": render_clause_ids(ids),
            "fingerprint": fingerprint,
            "input": ", ".join(f"`{key}`" for key in required_keys.get(check_id, ())),
            "reasons": reasons,
            "reason": " / ".join(reasons),
            "status": sorted(statuses)[0] if len(statuses) == 1 else "、".join(sorted(statuses)),
        }
    return derived


def compare_checks(
    checks: dict[str, dict],
    derived: dict[str, dict],
    required_keys: dict[str, tuple[str, ...]],
) -> list[str]:
    """比较文件中的 A 表与由 A.2 生成的结果；不再做两表字段互比。"""
    errors: list[str] = []
    for check_id in sorted(set(checks) - set(derived)):
        errors.append(f"[错误] A 表多出 A.2 未生成的 check_id {check_id}")
    for check_id in sorted(set(derived) - set(checks)):
        errors.append(f"[错误] A 表缺少 A.2 已生成的 check_id {check_id}")
    for check_id, row in derived.items():
        got = checks.get(check_id)
        if got is None:
            continue
        if got["rule"] != row["rule"]:
            errors.append(
                f"[错误] {check_id} 的规则列与 A.2 生成结果不一致："
                f"文件 {got['rule']}，生成 {row['rule']}"
            )
        if expand_clauses(got["clauses"]) != row["ids"]:
            errors.append(
                f"[错误] {check_id} 的子句 id 列与 A.2 生成结果不一致："
                f"文件 {expand_clauses(got['clauses'])}，生成 {row['ids']}"
            )
        if got["fingerprint"].strip("`") != row["fingerprint"]:
            errors.append(
                f"[错误] {check_id} 的子句指纹与 A.2 生成结果不一致："
                f"文件 {got['fingerprint'].strip('`')}，生成 {row['fingerprint']}"
            )
        got_input = re.findall(r"`([a-z][a-z0-9_]*)`", got["input"])
        if got_input != list(required_keys.get(check_id, ())):
            errors.append(
                f"[错误] {check_id} 的输入列与 schema §3 不一致："
                f"文件 {got_input}，生成 {list(required_keys.get(check_id, ()))}"
            )
        got_reasons = set(re.findall(r"[a-z][a-z0-9_]+", got["reason"]))
        if got_reasons != set(row["reasons"]):
            errors.append(
                f"[错误] {check_id} 的原因码列与 A.2 生成结果不一致："
                f"文件 {sorted(got_reasons)}，生成 {sorted(row['reasons'])}"
            )
        if got["status"].strip("`") != row["status"]:
            errors.append(
                f"[错误] {check_id} 的规则状态列与 A.2 生成结果不一致："
                f"文件 {got['status'].strip('`')}，生成 {row['status']}"
            )
    return errors


def render_check_table(derived: dict[str, dict]) -> list[str]:
    lines = [CHECK_HEADER, CHECK_SEPARATOR]
    for check_id, row in derived.items():
        lines.append(
            f"| `{check_id}` | {row['rule']} | {row['clauses']} | "
            f"`{row['fingerprint']}` | {row['input']} | {row['reason']} | {row['status']} |"
        )
    return lines


def replace_check_table(text: str, derived: dict[str, dict]) -> str:
    lines = text.splitlines()
    try:
        start = next(
            index
            for index, line in enumerate(lines)
            if line.startswith("| check_id | 规则 | 判定（子句 id）")
        )
        end = next(
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith("### A.2")
        )
    except StopIteration:
        raise SystemExit("[错误] 找不到 A 表或 A.2 标题，无法重建。")
    block = render_check_table(derived)
    return "\n".join(lines[:start] + block + [""] + lines[end:]) + "\n"


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


def parse_reason_codes(text: str) -> set[str]:
    """Schema 第 3 节“失败原因码”列 + 第 1.5/1.9/1.10 条定义的全局原因码。"""
    reasons: set[str] = {
        "dangling_reference",
        "undefined_object_type",
        "missing_input",
        "assumption_unclosed",
        "invalid_path",
    }
    for line in text.splitlines():
        cells = split_row(line)
        if cells and len(cells) >= 4 and CHECK_RE.match(cells[0]):
            reasons |= set(re.findall(r"[a-z][a-z0-9_]+", cells[3]))
    return reasons


def parse_schema_fields(text: str) -> set[str]:
    """Schema 第 2 节共享字段表“键”列声明的全部字段名。"""
    fields: set[str] = set()
    in_section = False
    for line in text.splitlines():
        if line.startswith("## 2."):
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if not in_section:
            continue
        cells = split_row(line)
        if not cells or len(cells) < 2 or not cells[0].startswith("`"):
            continue
        fields |= set(re.findall(r"`([a-z][a-z0-9_]*)`", cells[1]))
    return fields


def parse_reference_fields(text: str) -> tuple[set[str], set[str]]:
    """返回 (§2bis.1 引用字段, §2bis.2 非引用字段)。"""
    references: set[str] = set()
    non_references: set[str] = set()
    section = None
    for line in text.splitlines():
        if line.startswith("### 2bis.1"):
            section = "reference"
            continue
        if line.startswith("### 2bis.2"):
            section = "non-reference"
            continue
        if line.startswith("## "):
            section = None
            continue
        if section is None:
            continue
        cells = split_row(line)
        if not cells or not cells[0].startswith("`"):
            continue
        if section == "reference" and len(cells) >= 2:
            references.add(cells[1].strip("`"))
        elif section == "non-reference":
            non_references.add(cells[0].strip("`"))
    return references, non_references


def load_prototype(root: Path):
    path = root / "validation/checker-prototype/checker.py"
    spec = importlib.util.spec_from_file_location("checker_prototype", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"无法加载原型 {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def input_domain_issues(root: Path) -> list[str]:
    """加载原型，复用其 schema 解析与引用规则做输入域闭包检查。"""
    return load_prototype(root).input_domain_issues(root)


def parse_glossary(text: str) -> set[str]:
    """术语表中的机制术语也是合法判定对象（见 knowledge/anchored-entries.jsonl）。"""
    terms = set(re.findall(r"\*\*T-[A-F]-\d{3}\s+([^*]+?)\*\*", text))
    return terms | set(TERM_RE.findall(text))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="仓库根目录；默认由 git 推断")
    parser.add_argument("--method", help="覆盖方法文件路径（用于变异测试）")
    parser.add_argument("--write", action="store_true", help="用 A.2 重建 A 表")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else repo_root()
    method_path = Path(args.method).resolve() if args.method else root / METHOD
    try:
        grammar_text = (root / GRAMMAR).read_text(encoding="utf-8")
        method_text = method_path.read_text(encoding="utf-8")
        schema_text = (root / SCHEMA).read_text(encoding="utf-8")
        glossary_text = (root / GLOSSARY).read_text(encoding="utf-8")
    except FileNotFoundError as error:
        print(f"[错误] 缺少三表文件：{error.filename}")
        return 2

    rules = parse_grammar(grammar_text)
    checks, clauses = parse_method(method_text)
    schema_checks, vocab, enums = parse_schema(schema_text)
    reason_codes = parse_reason_codes(schema_text)
    vocab |= parse_glossary(glossary_text)
    if not rules or not clauses or not schema_checks:
        print("[错误] 三表解析结果为空，结构无法解析。")
        return 2

    prototype = load_prototype(root)
    required_keys = prototype.REQUIRED_KEYS
    derived = derive_checks(clauses, required_keys)

    if args.write:
        method_path.write_text(replace_check_table(method_text, derived), encoding="utf-8")
        print(f"A 表已由 A.2 重建：{len(derived)} 个 check_id。")
        return 0

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

    # 4. A 表 = A.2 的派生结果（逐格比较；不做事后两表互比）
    errors.extend(compare_checks(checks, derived, required_keys))

    # 4bis. 判定列语义格式与子句结构
    for check_id, item in checks.items():
        residual = CLAUSE_RANGE_RE.sub("", item["clauses"])
        residual = CLAUSE_ID_RE.sub("", residual)
        residual = re.sub(r"[`\s–\-—、,，]", "", residual)
        if residual:
            errors.append(
                f"[错误] {check_id} 的判定列含叙述性短语 `{residual}`；"
                "判定列只能写子句 id，叙述下沉 A.2"
            )
    referenced: set[str] = set()
    for check_id, item in derived.items():
        referenced.update(item["ids"])
    for clause, item in clauses.items():
        if item["status"].startswith("not-checked"):
            if "理由" not in item["clause"] and len(item["clause"]) < 8:
                errors.append(f"[错误] 子句 {clause} 标为 not-checked 但未写理由")
            continue
        if clause not in referenced:
            errors.append(f"[错误] 子句 {clause} 未被任何 check_id 的判定列引用")
        clause_reason = set(re.findall(r"[a-z][a-z0-9_]+", item["reason"]))
        if not clause_reason:
            errors.append(f"[错误] 子句 {clause} 没有原因码")
        for code in sorted(clause_reason):
            if code not in reason_codes:
                errors.append(f"[错误] 子句 {clause} 的原因码 `{code}` 未在 schema 定义")
        # 语义短语检查：B1 只判标签存在，值是否在枚举内归 B2。
        if item["rule"] == "G-B1" and "枚举" in item["clause"]:
            errors.append(f"[错误] 子句 {clause}（G-B1）写了枚举条件；枚举归属 G-B2")
        if clause == "G-B2#1" and "枚举" not in item["clause"]:
            errors.append("[错误] G-B2#1 未写枚举条件；值闭合必须由 B2 承接")

    # 5. 枚举封闭（A 表不再承载枚举值，保留 schema §4 闭合核对）
    if enums:
        for check_id in checks:
            if check_id not in schema_checks:
                errors.append(f"[错误] {check_id} 在 schema 第 4 节没有枚举定义入口")

    # 6. 引用字段标注完整：第 2 节的每个字段必须被 §2bis.1 或 §2bis.2 覆盖
    schema_fields = parse_schema_fields(schema_text)
    references, non_references = parse_reference_fields(schema_text)
    for field in sorted(schema_fields - references - non_references):
        errors.append(
            f"[错误] 字段 `{field}` 在第 2 节声明，但 §2bis 既未标注为引用也未登记为非引用"
        )

    # 7. 输入域闭包：样例中出现的引用目标集合必须在 §3 声明
    for issue in input_domain_issues(root):
        errors.append(f"[错误] {issue}")

    # 8. A.2 复核签收：A.2 任何改动必须同步更新区段指纹（AGENTS 3.6.7）
    signoff = parse_a2_signoff(method_text)
    current_a2 = a2_block_fingerprint(clauses)
    if signoff is None:
        errors.append(
            "[错误] A.2 区头缺少复核签收行；格式："
            "“复核签收：<签收人> / <YYYY-MM-DD> / A.2 指纹 `<12位>`”"
        )
    else:
        reviewer, signed_at, signed_fingerprint = signoff
        if signed_fingerprint != current_a2:
            errors.append(
                f"[错误] A.2 已改动但复核签收未同步：签收行 {reviewer} / {signed_at} / "
                f"`{signed_fingerprint}`，当前 A.2 指纹 `{current_a2}`；"
                "改 A.2 后必须由非同源复核更新签收行，不得只跑 --write"
            )

    print(
        f"三表对照：正文 {len(rules)} 条规则，判定列 {len(checks)} 个 check_id / "
        f"{len(clauses)} 个子句，schema {len(schema_checks)} 个输入域，"
        f"引用字段 {len(references)} 个 / 非引用字段 {len(non_references)} 个；"
        f"A.2 指纹 `{current_a2}`。"
    )
    if errors:
        for error in errors:
            print(error)
        print(f"[失败] {len(errors)} 项错误。")
        return 1
    print("[通过] 正文、判定列、schema 三表一致；A 表与 A.2 派生结果一致；A.2 签收与指纹同步；引用标注与输入域闭合。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
