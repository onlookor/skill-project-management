#!/usr/bin/env python3
"""解析并校验本仓库的锚点（spec/ANCHOR_SPEC.md）。

检查内容：
  1. 活跃文件中不得出现行号 locator（`file.md:123`、`#L123`、`@m:123`、`第 123 行`）；
     冻结文件（adr/、CHANGELOG.md、ERRATA.md）中的行号只提示，按 as-of 证据保留。
  2. 文件引用必须存在（排除通配符与占位符）；`resources/` 按部署外部资源处理。
  3. 稳定 ID 必须可解析：rule / check / knowledge / method / source / term / todo / adr。
  4. 章节引用（`` `X.md` 第 N 条/节 ``）的编号必须在目标文件中存在。
  5. GRAMMAR 规则的 check 与 grounding_ref、CHECKLIST 的规则列、JSONL 的 grounding_ref 必须解析。
  6. rule 与 source 文本块的指纹必须与 scripts/anchor_baseline.json 一致（只报漂移，不自动修改）。

退出码：0 通过（可有警告/提示）；1 存在错误；2 结构或基线无法解析。
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent.parent
BASELINE_REL = Path("scripts") / "anchor_baseline.json"
HISTORICAL_FILES = {"CHANGELOG.md", "ERRATA.md"}
# 规范自身含禁止形态的示例，只作 sandbox，不参与行号 locator 判定
SANDBOX_FILES = {"spec/ANCHOR_SPEC.md"}
# 引用的是宿主技能的入口文件，不在本仓库内
EXTERNAL_NAMES = {"SKILL.md"}
EXAMPLE_MARKERS = ("例如", "命名规则", "示例", "形如")
PLANNED_MARKERS = ("待编写", "待交付", "下一轮交付", "尚未创建", "计划创建")

FILE_REF_RE = re.compile(
    r"`((?:[A-Za-z0-9_.\-]+/)*[A-Za-z0-9_.\-]+\.(?:md|py|json|jsonl|yaml|yml|pdf))`"
)
LINE_REF_RE = re.compile(
    r"`[^`\n]+?\.(?:md|py|json|jsonl|yaml|yml):\d+(?:-\d+)?`|#L\d+|@m:\d+|第\s*\d+\s*行"
)
SECTION_REF_RE = re.compile(
    r"`([A-Za-z0-9_.\-/]+\.md)`\s*第\s*([0-9]+(?:\.[0-9]+)*)\s*([条节])"
)
RULE_ID_RE = re.compile(r"\bG-[A-G]\d\b")
EXPLICIT_RE = {
    "rule": re.compile(r"\brule:([A-G]-[A-G]\d)\b"),
    "check": re.compile(r"\bcheck:([A-Z][A-Z_]{2,})\b"),
    "knowledge": re.compile(r"\bknowledge:([A-Za-z][A-Za-z0-9_]*)\b"),
    "method": re.compile(r"\bmethod:([A-Za-z0-9_.-]+-[A-Z]+-\d+)\b"),
    "source": re.compile(r"\bsource:([A-Za-z0-9][A-Za-z0-9.\-]*[A-Za-z0-9])\b"),
    "term": re.compile(r"\bterm:(T-[A-Z]-\d+)\b"),
    "todo": re.compile(r"\btodo:(T-\d+)\b"),
    "adr": re.compile(r"\badr:(\d{4})\b"),
}
DOC_ANCHOR_RE = re.compile(r"doc:([^#\s`]+)#(sec-[^`\n]+|clause-[0-9.]+)")


def is_historical(rel):
    return rel.startswith("adr/") or rel in HISTORICAL_FILES


def read(path):
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def normalize_block(text):
    lines = []
    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line.strip())
        if line:
            lines.append(line)
    return "\n".join(lines)


def fingerprint(text):
    return hashlib.sha256(normalize_block(text).encode("utf-8")).hexdigest()


def markdown_files(root):
    return sorted(
        p for p in root.rglob("*.md") if ".git" not in p.parts and "__pycache__" not in p.parts
    )


def resolve_doc(root, name):
    """返回 (path, error)。先按确切路径，再按唯一文件名。"""
    candidate = root / name
    if candidate.is_file():
        return candidate, None
    matches = [p for p in root.rglob(Path(name).name) if ".git" not in p.parts]
    if len(matches) == 1:
        return matches[0], None
    if not matches:
        return None, "E-FILE-MISSING"
    return None, "E-AMBIGUOUS"


def has_number(text, number, kind):
    n = re.escape(number)
    boundary = r"(?![0-9.])"
    patterns = [
        rf"^#{{2,4}}\s*(?:第\s*)?{n}\s*(?:条|[.．、])\s*" + boundary,
        rf"^#{{2,4}}\s*第\s*{n}\s*{kind}",
        rf"^#{{2,4}}\s*(?:第\s*)?{n}(?:\s|$)",
        rf"\*\*第\s*{n}\s*{kind}",
        rf"\*\*{n}\s",
    ]
    return any(re.search(p, text, re.M) for p in patterns)


def parse_rule_blocks(text):
    """返回 {rule_id: block_text}。"""
    lines = text.splitlines()
    starts = [
        (i, re.match(r"^\*\*(G-[A-G]\d)（", line).group(1))
        for i, line in enumerate(lines)
        if re.match(r"^\*\*(G-[A-G]\d)（", line)
    ]
    blocks = {}
    for idx, (start, rid) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        for j in range(start + 1, end):
            if re.match(r"^#{2,4}\s", lines[j]) or lines[j].strip() == "---":
                end = j
                break
        blocks[rid] = "\n".join(lines[start:end])
    return blocks


def parse_stackblocks(text, heading_re):
    lines = text.splitlines()
    starts = [
        (i, m.group(1)) for i, line in enumerate(lines) for m in [heading_re.match(line)] if m
    ]
    blocks = {}
    for idx, (start, key) in enumerate(starts):
        end = starts[idx + 1][0] if idx + 1 < len(starts) else len(lines)
        for j in range(start + 1, end):
            if re.match(r"^#{1,3}\s", lines[j]) or lines[j].strip() == "---":
                end = j
                break
        blocks[key] = "\n".join(lines[start:end])
    return blocks


def main():
    parser = argparse.ArgumentParser(description="校验本仓库的锚点")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--baseline", type=Path, default=None)
    parser.add_argument("--write-baseline", action="store_true", help="重冻指纹基线")
    args = parser.parse_args()

    root = args.root.resolve()
    baseline_path = args.baseline or (root / BASELINE_REL)
    if not (root / "GRAMMAR.md").is_file() or not (root / "SOURCE_LEDGER.md").is_file():
        print("[无法解析] 根目录下缺少 GRAMMAR.md 或 SOURCE_LEDGER.md")
        return 2

    files = markdown_files(root)
    texts = {p: read(p) for p in files}
    rel = lambda p: str(p.relative_to(root))

    # --- 索引：目标集合 ---
    grammar_text = read(root / "GRAMMAR.md")
    ledger_text = read(root / "SOURCE_LEDGER.md")
    glossary_text = read(root / "GLOSSARY.md")
    todo_text = read(root / "TODO.md")
    checker_text = read(root / "spec" / "methods" / "deterministic-checker.md")
    checklist_text = read(root / "validation" / "CHECKLIST.md")
    methods_text = read(root / "knowledge" / "methods" / "registry-skeleton.md")

    rule_blocks = parse_rule_blocks(grammar_text)
    source_blocks = parse_stackblocks(ledger_text, re.compile(r"^#### ([A-Za-z0-9][A-Za-z0-9.\-]*)\s*$"))
    source_ids = set(source_blocks)

    terms = set()
    jsonl_entries = []
    for line in read(root / "knowledge" / "anchored-entries.jsonl").splitlines():
        if line.strip():
            try:
                entry = json.loads(line)
                terms.add(entry["term"])
                jsonl_entries.append(entry)
            except (json.JSONDecodeError, KeyError):
                print("[无法解析] knowledge/anchored-entries.jsonl")
                return 2

    checks = set(re.findall(r"^\| `([A-Z][A-Z_]{2,})` \|", checker_text, re.M))
    checks |= set(re.findall(r"^\| `([A-Z][A-Z_]{2,})` \|", checklist_text, re.M))
    methods = set(re.findall(r"`(M-[A-Z]+-\d+)`", methods_text))
    glossary_terms = set(re.findall(r"^\*\*(T-[A-Z]-\d+) ", glossary_text, re.M))
    todos = set(re.findall(r"^\| (T-\d+) \|", todo_text, re.M))
    adrs = {m.group(1) for p in (root / "adr").glob("*.md") for m in [re.match(r"(\d{4})-", p.name)] if m}

    errors, warnings, infos = [], [], []

    def add(bucket, code, where, detail):
        bucket.append(f"[{code}] {where}：{detail}")

    # --- 1) 行号 locator ---
    for path, text in texts.items():
        r = rel(path)
        if r in SANDBOX_FILES:
            continue
        for m in LINE_REF_RE.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            # 展示用行号只出现在报错里，不写回文件
            if is_historical(r):
                infos.append(f"[I-AS-OF] {r}:{line_no}：{m.group(0)}（冻结证据，按 as-of 保留）")
            else:
                add(errors, "E-LINE-LOCATOR", f"{r}:{line_no}", f"{m.group(0)} 不得作为定位锚点")

    # --- 2) 文件引用 ---
    for path, text in texts.items():
        r = rel(path)
        for m in FILE_REF_RE.finditer(text):
            target = m.group(1)
            if any(ch in target for ch in "*{<>") or "NNNN" in target:
                continue
            line_no = text.count("\n", 0, m.start()) + 1
            line = text.splitlines()[line_no - 1] if line_no <= len(text.splitlines()) else ""
            if target.startswith("resources/") or target in EXTERNAL_NAMES:
                if target.startswith("resources/") and not (root.parent / target).exists():
                    infos.append(f"[I-EXTERNAL] {r}:{line_no}：{target}（部署外部资源，未随仓交付）")
                elif target in EXTERNAL_NAMES:
                    infos.append(f"[I-EXTERNAL] {r}:{line_no}：{target}（宿主技能入口，不在本仓库）")
                continue
            if any(mark in line for mark in EXAMPLE_MARKERS):
                infos.append(f"[I-EXAMPLE] {r}:{line_no}：{target}（命名示例，不要求存在）")
                continue
            if any(mark in line for mark in PLANNED_MARKERS):
                infos.append(f"[I-PLANNED] {r}:{line_no}：{target}（计划项，尚未创建）")
                continue
            _, err = resolve_doc(root, target)
            if err and is_historical(r):
                infos.append(f"[I-AS-OF] {r}:{line_no}：{target}（冻结文件按当时版本保留）")
            elif err and r == "TODO.md":
                infos.append(f"[I-PLANNED] {r}:{line_no}：{target}（计划项，尚未创建）")
            elif err:
                add(errors, err, f"{r}:{line_no}", target)

    # --- 3) 稳定 ID ---
    for path, text in texts.items():
        r = rel(path)
        for kind, regex in EXPLICIT_RE.items():
            for m in regex.finditer(text):
                value = m.group(1)
                ok = {
                    "rule": value in rule_blocks,
                    "check": value in checks,
                    "knowledge": value in terms,
                    "method": value in methods,
                    "source": value in source_ids,
                    "term": value in glossary_terms,
                    "todo": value in todos,
                    "adr": value in adrs,
                }[kind]
                if not ok:
                    line_no = text.count("\n", 0, m.start()) + 1
                    add(errors, "E-NO-TARGET", f"{r}:{line_no}", f"{kind}:{value}")

    # --- 4) 章节引用 ---
    for path, text in texts.items():
        r = rel(path)
        for m in SECTION_REF_RE.finditer(text):
            name, number, kind = m.groups()
            target_path, err = resolve_doc(root, name)
            line_no = text.count("\n", 0, m.start()) + 1
            if err:
                if is_historical(r) or r == "TODO.md":
                    infos.append(f"[I-AS-OF] {r}:{line_no}：`{name}` 第 {number} {kind}（目标按当时/计划版本保留）")
                else:
                    add(errors, err, f"{r}:{line_no}", f"`{name}` 第 {number} {kind}")
                continue
            if not has_number(read(target_path), number, kind):
                if is_historical(r) or r == "TODO.md":
                    infos.append(f"[I-AS-OF] {r}:{line_no}：`{name}` 第 {number} {kind}（目标按当时/计划版本保留）")
                else:
                    add(errors, "E-NO-TARGET", f"{r}:{line_no}", f"`{name}` 第 {number} {kind}")

    # --- 5) 标题路径 ---
    for path, text in texts.items():
        r = rel(path)
        for m in DOC_ANCHOR_RE.finditer(text):
            name, sub = m.groups()
            if any(ch in name for ch in "<>{}*") or "..." in sub:
                continue
            target_path, err = resolve_doc(root, name)
            line_no = text.count("\n", 0, m.start()) + 1
            if err:
                add(errors, err, f"{r}:{line_no}", f"doc:{name}#{sub}")
                continue
            target_text = read(target_path)
            if sub.startswith("clause-"):
                number = sub[len("clause-"):]
                if not has_number(target_text, number, "条"):
                    add(errors, "E-NO-TARGET", f"{r}:{line_no}", f"doc:{name}#{sub}")
            else:
                heading = sub[len("sec-"):].strip()
                headings = [h.strip() for h in re.findall(r"^#{1,6}\s+(.+)$", target_text, re.M)]
                count = sum(1 for h in headings if h == heading)
                if count == 0:
                    add(errors, "E-NO-TARGET", f"{r}:{line_no}", f"doc:{name}#{sub}")
                elif count > 1:
                    add(errors, "E-AMBIGUOUS", f"{r}:{line_no}", f"doc:{name}#{sub}")

    # --- 6) 结构化交叉引用 ---
    for rid, block in rule_blocks.items():
        for m in re.finditer(r"-\s*`check`：`([A-Z][A-Z_]{2,})`", block):
            if m.group(1) not in checks:
                add(errors, "E-NO-TARGET", f"GRAMMAR.md#{rid}", f"check:{m.group(1)}")
        for m in re.finditer(r"-\s*`grounding_ref`：(.+)", block):
            for sid in re.findall(r"`([A-Za-z0-9][A-Za-z0-9.\-]*)`", m.group(1)):
                if sid not in source_ids:
                    add(errors, "E-NO-TARGET", f"GRAMMAR.md#{rid}", f"source:{sid}")

    for line in checklist_text.splitlines():
        m = re.match(r"^\| `[A-Z][A-Z_]{2,}` \| `?(G-[A-G]\d)`? \|", line)
        if m and m.group(1) not in rule_blocks:
            add(errors, "E-NO-TARGET", "validation/CHECKLIST.md", f"rule:{m.group(1)}")

    active_sources = set()
    for sid, block in source_blocks.items():
        status = re.search(r"^\|\s*`status`\s*\|\s*(.+?)\s*\|", block, re.M)
        if status and "active" in status.group(1):
            active_sources.add(sid)
    for entry in jsonl_entries:
        ref = entry.get("grounding_ref")
        if ref not in active_sources:
            add(errors, "E-NO-TARGET", "knowledge/anchored-entries.jsonl", f"{entry.get('term')} -> {ref}")

    for sid, block in source_blocks.items():
        mapping = re.search(r"^\|\s*`claim_mapping`\s*\|\s*(.+?)\s*\|$", block, re.M)
        if mapping:
            for rid in RULE_ID_RE.findall(mapping.group(1)):
                if rid not in rule_blocks:
                    add(errors, "E-NO-TARGET", f"SOURCE_LEDGER.md#{sid}", f"rule:{rid}")

    # --- 7) 指纹基线 ---
    current = {}
    for rid, block in rule_blocks.items():
        current[f"rule:{rid}"] = {"path": "GRAMMAR.md", "heading": rid, "sha256": fingerprint(block)}
    for sid, block in source_blocks.items():
        current[f"source:{sid}"] = {"path": "SOURCE_LEDGER.md", "heading": sid, "sha256": fingerprint(block)}

    baseline = {}
    if baseline_path.is_file():
        try:
            baseline = json.loads(read(baseline_path)).get("anchors", {})
        except json.JSONDecodeError:
            print("[无法解析] 基线不是合法 JSON")
            return 2

    if args.write_baseline:
        payload = {
            "version": 1,
            "algorithm": "sha256(normalize(lines))",
            "anchors": dict(sorted(current.items())),
        }
        baseline_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        added = sorted(set(current) - set(baseline))
        removed = sorted(set(baseline) - set(current))
        changed = sorted(k for k in set(current) & set(baseline) if current[k]["sha256"] != baseline[k]["sha256"])
        print(f"基线已写入 {baseline_path}：{len(current)} 个锚点（新增 {len(added)}，删除 {len(removed)}，变更 {len(changed)}）")
        for k in added:
            print(f"  + {k}")
        for k in removed:
            print(f"  - {k}")
        for k in changed:
            print(f"  ~ {k}")
        return 0

    for key, meta in baseline.items():
        if key not in current:
            add(errors, "E-NO-TARGET", meta.get("path", "?"), f"{key}（基线中存在，当前缺失）")
        elif current[key]["sha256"] != meta.get("sha256"):
            warnings.append(
                f"[W-FINGERPRINT-DRIFT] {current[key]['path']}：{key} 文本已变更，需人工复核后重冻基线"
            )
    for key in sorted(set(current) - set(baseline)):
        warnings.append(f"[W-BASELINE-MISSING] {current[key]['path']}：{key} 未登记基线")

    for message in infos:
        print(message)
    for message in warnings:
        print(message)
    for message in errors:
        print(message)
    print(
        f"锚点核对：{len(files)} 个 Markdown 文件，{len(rule_blocks)} 条规则，"
        f"{len(source_ids)} 个来源，{len(baseline)} 个基线锚点；"
        f"{len(errors)} 个错误，{len(warnings)} 个警告，{len(infos)} 个提示"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
