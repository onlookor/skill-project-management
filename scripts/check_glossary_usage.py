#!/usr/bin/env python3
"""核查 GLOSSARY.md 术语在仓库中的使用位置，并生成机器可核对的使用清单。

用法：python3 scripts/check_glossary_usage.py [--write] [--root DIR]
退出码：0 = 通过；1 = 使用位置陈旧或生成块被手改；2 = 结构无法解析或不在 git 仓库中。
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

GLOSSARY = "GLOSSARY.md"
BASELINE = "knowledge/glossary-usage.json"
BEGIN = "<!-- BEGIN GLOSSARY USAGE -->"
END = "<!-- END GLOSSARY USAGE -->"
SCAN_SUFFIXES = (".md", ".jsonl")

TERM_RE = re.compile(r"^\*\*(T-[A-F]-\d{3})\s+(.+?)\*\*$")
GLOSSARY_LINK_RE = re.compile(r"GLOSSARY\.md#(T-[A-F]-\d{3})")
TERM_ID_RE = re.compile(r"(?<![\w-])T-[A-F]-\d{3}(?![\w-])")
DETAIL_LIMIT = 20


def repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("[错误] 当前目录不在 git 仓库中，无法核查术语使用位置。")
        sys.exit(2)
    return Path(result.stdout.strip())


def tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, capture_output=True, text=True
    )
    if result.returncode != 0:
        print("[错误] git ls-files 执行失败，无法确定扫描范围。")
        sys.exit(2)
    return [name for name in result.stdout.split("\0") if name]


def parse_glossary(text: str) -> dict[str, str]:
    terms: dict[str, str] = {}
    for line in text.splitlines():
        match = TERM_RE.match(line.strip())
        if match:
            terms[match.group(1)] = match.group(2)
    return terms


def code_pattern(term: str) -> re.Pattern:
    # 行内代码紧邻形式：前后各一个反引号，且不与更长的反引号串相连。
    return re.compile("(?<!`)" + "`" + re.escape(term) + "`" + "(?!`)")


def line_contains_term(code_re: re.Pattern, line: str, term_id: str) -> bool:
    if code_re.search(line):
        return True
    if f"GLOSSARY.md#{term_id}" in line:
        return True
    return re.search(r"(?<![\w-])" + re.escape(term_id) + r"(?![\w-])", line) is not None


def scan(root: Path, terms: dict[str, str]) -> dict[str, list[dict]]:
    """扫描全部 .md/.jsonl，返回 term_id -> 排序后的位置列表。"""
    code_res = {term_id: code_pattern(term) for term_id, term in terms.items()}
    excluded = {GLOSSARY, BASELINE}
    usage: dict[str, set[tuple[str, int, str]]] = {term_id: set() for term_id in terms}

    for name in tracked_files(root):
        if name in excluded or not name.endswith(SCAN_SUFFIXES):
            continue
        path = root / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), start=1):
            line_forms: dict[str, set[str]] = {}

            for term_id, code_re in code_res.items():
                if code_re.search(line):
                    line_forms.setdefault(term_id, set()).add("code")

            anchor_spans = []
            for match in GLOSSARY_LINK_RE.finditer(line):
                anchor_spans.append(match.span())
                line_forms.setdefault(match.group(1), set()).add("glossary_link")

            for match in TERM_ID_RE.finditer(line):
                if any(start <= match.start() < end for start, end in anchor_spans):
                    continue
                if match.group(0) in terms:
                    line_forms.setdefault(match.group(0), set()).add("term_id")

            for term_id, forms in line_forms.items():
                for form in forms:
                    usage[term_id].add((name, line_no, form))

    return {
        term_id: [
            {"file": file, "line": line, "form": form}
            for file, line, form in sorted(records, key=lambda r: (r[0], r[1], r[2]))
        ]
        for term_id, records in usage.items()
    }


def escape_cell(text: str) -> str:
    return text.replace("|", "\\|")


def render_block(terms: dict[str, str], usage: dict[str, list[dict]]) -> list[str]:
    lines = [BEGIN, "| term_id | term | 使用位置 |", "|---|---|---|"]
    for term_id in sorted(terms):
        files = sorted({loc["file"] for loc in usage.get(term_id, [])})
        if files:
            cell = "、".join(f"[`{file}`]({file})" for file in files)
        else:
            cell = "（无）"
        lines.append(f"| {term_id} | {escape_cell(terms[term_id])} | {cell} |")
    lines.append(END)
    return lines


def find_block(lines: list[str]):
    begins = [i for i, line in enumerate(lines) if line.strip() == BEGIN]
    ends = [i for i, line in enumerate(lines) if line.strip() == END]
    if not begins and not ends:
        return None
    if len(begins) != 1 or len(ends) != 1 or begins[0] > ends[0]:
        return "malformed"
    return (begins[0], ends[0])


def baseline_payload(terms: dict[str, str], usage: dict[str, list[dict]]) -> dict:
    return {
        "generated_by": "scripts/check_glossary_usage.py",
        "terms": {
            term_id: {"term": terms[term_id], "locations": usage.get(term_id, [])}
            for term_id in sorted(terms)
        },
    }


def write_outputs(root: Path, terms: dict[str, str], usage: dict[str, list[dict]]) -> None:
    glossary_path = root / GLOSSARY
    text = glossary_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    block = render_block(terms, usage)
    block_info = find_block(lines)

    if block_info == "malformed":
        print("[错误] GLOSSARY.md 的术语使用位置标记块不完整，结构无法解析。")
        sys.exit(2)

    if block_info is None:
        if not text.endswith("\n"):
            text += "\n"
        text += (
            "\n## 4. 术语使用位置（生成）\n\n"
            "本表由 `scripts/check_glossary_usage.py` 生成，勿手改。"
            "修改术语定义或引用后请运行 "
            "`python3 scripts/check_glossary_usage.py --write` 重新生成。\n\n"
            + "\n".join(block)
            + "\n"
        )
    else:
        begin, end = block_info
        text = "\n".join(lines[:begin] + block + lines[end + 1 :]) + "\n"

    baseline_path = root / BASELINE
    baseline_path.parent.mkdir(parents=True, exist_ok=True)
    baseline_path.write_text(
        json.dumps(baseline_payload(terms, usage), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    glossary_path.write_text(text, encoding="utf-8")


def load_baseline(root: Path) -> dict:
    path = root / BASELINE
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[错误] 无法解析 {BASELINE}：{exc}")
        sys.exit(2)
    terms = payload.get("terms")
    if not isinstance(terms, dict):
        print(f"[错误] {BASELINE} 缺少 terms 对象，结构无法解析。")
        sys.exit(2)
    return terms


def check(root: Path, terms: dict[str, str], usage: dict[str, list[dict]]) -> int:
    errors: list[str] = []
    warnings: list[str] = []
    baseline = load_baseline(root)

    if not baseline:
        errors.append(f"[错误] 缺少基线 {BASELINE}，请运行 --write 生成。")
        baseline = {}

    # 术语集合必须与基线键集合一致。
    if set(terms) != set(baseline):
        added = sorted(set(terms) - set(baseline))
        removed = sorted(set(baseline) - set(terms))
        detail = []
        if added:
            detail.append("新增：" + "、".join(added))
        if removed:
            detail.append("删除：" + "、".join(removed))
        errors.append(
            "[错误] 术语条目与基线键集合不一致（新增/删除术语未重新生成）：" + "；".join(detail)
        )

    # 逐项比较使用位置。
    stale = False
    details: list[str] = []
    for term_id in sorted(set(terms) & set(baseline)):
        current = {
            (loc["file"], loc["line"], loc["form"]) for loc in usage.get(term_id, [])
        }
        recorded = set()
        for loc in baseline[term_id].get("locations", []):
            try:
                recorded.add((loc["file"], loc["line"], loc["form"]))
            except (KeyError, TypeError):
                errors.append(f"[错误] 基线中 {term_id} 的位置条目结构非法。")
        if current != recorded:
            stale = True
            for item in sorted(current - recorded):
                if len(details) < DETAIL_LIMIT:
                    details.append(f"[差异] 新增位置：{term_id} / {item[0]}:{item[1]}（{item[2]}）")
            for item in sorted(recorded - current):
                if len(details) < DETAIL_LIMIT:
                    details.append(f"[差异] 消失位置：{term_id} / {item[0]}:{item[1]}（{item[2]}）")
    if stale:
        errors.append("[错误] 术语使用位置已陈旧，请运行 --write")
        errors.extend(details)

    # 校验基线中的每个位置仍然有效。
    code_res = {term_id: code_pattern(term) for term_id, term in terms.items()}
    for term_id in sorted(set(terms) & set(baseline)):
        term = terms[term_id]
        for loc in baseline[term_id].get("locations", []):
            try:
                file, line_no = loc["file"], loc["line"]
            except (KeyError, TypeError):
                continue
            path = root / file
            if not path.is_file():
                errors.append(f"[错误] 陈旧位置 {term_id} {file}:{line_no}：文件不存在")
                continue
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
            if not isinstance(line_no, int) or not (1 <= line_no <= len(lines)):
                errors.append(
                    f"[错误] 陈旧位置 {term_id} {file}:{line_no}：行号超出范围（1–{len(lines)}）"
                )
                continue
            if not line_contains_term(code_res[term_id], lines[line_no - 1], term_id):
                errors.append(
                    f"[错误] 陈旧位置 {term_id} {file}:{line_no}：该行不含术语 `{term}`"
                )

    # 生成块必须与重新生成的内容逐字一致。
    glossary_path = root / GLOSSARY
    if not glossary_path.is_file():
        print("[错误] 缺少 GLOSSARY.md，无法核对生成块。")
        return 2
    lines = glossary_path.read_text(encoding="utf-8").splitlines()
    block_info = find_block(lines)
    if block_info == "malformed":
        print("[错误] GLOSSARY.md 的术语使用位置标记块不完整，结构无法解析。")
        return 2
    if block_info is None:
        errors.append("[错误] GLOSSARY.md 缺少术语使用位置标记块，请运行 --write")
    else:
        begin, end = block_info
        expected = render_block(terms, usage)
        if lines[begin : end + 1] != expected:
            errors.append("[错误] GLOSSARY.md 的术语使用位置生成块与重新生成的内容不一致，请运行 --write")

    # 零使用术语只警告，不阻断。
    for term_id in sorted(terms):
        if not usage.get(term_id):
            warnings.append(f"[警告] 术语 {term_id}（{terms[term_id]}）无使用位置")

    total = sum(len(locations) for locations in usage.values())
    print(
        f"术语使用核对：{len(terms)} 条术语，{total} 个使用位置；"
        f"{len(errors)} 个错误，{len(warnings)} 个警告。"
    )

    for warning in warnings:
        print(warning)
    if errors:
        for error in errors:
            print(error)
        print(f"[失败] {len(errors)} 项错误。")
        return 1
    print("[通过] 术语使用位置与基线一致，生成块未被手改。")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="重新生成基线与 GLOSSARY 使用位置块")
    parser.add_argument("--root", help="仓库根目录；默认由 git 推断")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else repo_root()
    glossary_path = root / GLOSSARY
    if not glossary_path.is_file():
        print("[错误] 缺少 GLOSSARY.md，无法核查术语使用位置。")
        return 2

    terms = parse_glossary(glossary_path.read_text(encoding="utf-8"))
    if not terms:
        print("[错误] 未能从 GLOSSARY.md 解析出任何术语条目，结构无法解析。")
        return 2

    usage = scan(root, terms)

    if args.write:
        write_outputs(root, terms, usage)
        total = sum(len(locations) for locations in usage.values())
        print(f"[写入] 已生成 {BASELINE} 并更新 GLOSSARY.md 使用位置表。")
        print(f"术语使用核对：{len(terms)} 条术语，{total} 个使用位置；0 个错误，0 个警告。")
        for term_id in sorted(terms):
            if not usage.get(term_id):
                print(f"[警告] 术语 {term_id}（{terms[term_id]}）无使用位置")
        return 0

    return check(root, terms, usage)


if __name__ == "__main__":
    sys.exit(main())
