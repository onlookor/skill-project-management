#!/usr/bin/env python3
"""条款依据检查器（批次 0098）。

检查三件事：

1. 用例引用的条款必须存在于 `spec/clause-registry.json`；
2. 标记为 `judgmental` 的条款至少被一条用例以 `条款：<id>` 引用；
3. 登记表条目指向的源文件、章节与原文必须对得上——原文由 `--write`
   从源文件逐字提取，运行期重新提取并与登记值比对，任何不一致即报错。

定位方式（`locator`）：

- `heading`：`section` 是 Markdown 标题编号（如 `9.3`），条款原文取该章节内
  含 `anchor` 的那一整行；`anchor` 在该章节内必须唯一。
- `bold`：`section` 是术语表条目编号（如 `T-F-015`），章节范围到下一个
  `**T-` 条目为止。
- `pointer`：`section` 是 JSON Pointer，条款原文取该指针指向的字符串值。

用例引用只认 `条款：<id>` 标记；出现 `依据：` 却没有标记的行一律报错，
防止再用自由文本编造依据。登记表只证明“文字与源文件一致”，不构成认可。

退出码：0 通过、1 有缺陷、2 登记表本身不可解析。

零第三方依赖：只用标准库。
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "spec" / "clause-registry.json"
CASE_GLOBS = ("scripts/test_*.py", "validation/test-cases/*.md")
CITE = re.compile(r"条款：([A-Za-z0-9][A-Za-z0-9_.\-]*(?:、[A-Za-z0-9][A-Za-z0-9_.\-]*)*)")
KINDS = ("judgmental", "textual", "external")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _heading_span(lines: list[str], section: str) -> tuple[int, int] | None:
    token = re.compile(r"^(#{1,6})\s+" + re.escape(section) + r"(?=\s|$)")
    for index, line in enumerate(lines):
        match = token.match(line)
        if not match:
            continue
        level = len(match.group(1))
        end = index + 1
        while end < len(lines):
            other = re.match(r"^(#{1,6})\s+", lines[end])
            if other and len(other.group(1)) <= level:
                break
            end += 1
        return index, end
    return None


def _bold_span(lines: list[str], section: str) -> tuple[int, int] | None:
    start = None
    for index, line in enumerate(lines):
        if line.startswith("**" + section):
            start = index
            break
    if start is None:
        return None
    end = start + 1
    while end < len(lines) and not re.match(r"^\*\*T-", lines[end]):
        end += 1
    return start, end


def _pointer_get(document: object, pointer: str) -> object:
    node = document
    for token in pointer.split("/")[1:]:
        token = token.replace("~1", "/").replace("~0", "~")
        if isinstance(node, list):
            node = node[int(token)]
        elif isinstance(node, dict):
            node = node[token]
        else:
            raise KeyError(pointer)
    return node


def _derive(entry: dict, root: Path) -> str:
    """按定位信息从源文件取回条款原文。取不到即抛错。"""
    source = root / entry["source"]
    if not source.is_file():
        raise ValueError(f"源文件不存在：{entry['source']}")
    locator = entry["locator"]
    if locator == "pointer":
        document = json.loads(_read(source))
        value = _pointer_get(document, entry["section"])
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"指针不是非空字符串：{entry['section']}")
        return value
    lines = _read(source).splitlines()
    span = _heading_span(lines, entry["section"]) if locator == "heading" else _bold_span(lines, entry["section"])
    if span is None:
        raise ValueError(f"章节不存在：{entry['source']}#{entry['section']}（locator={locator}）")
    anchor = entry.get("anchor", "")
    if not anchor:
        raise ValueError("heading/bold 定位必须给出 anchor")
    hits = [line.strip() for line in lines[span[0] : span[1]] if anchor in line]
    if len(hits) != 1:
        raise ValueError(
            f"锚点在该章节命中 {len(hits)} 行（应为 1）：{entry['source']}#{entry['section']} :: {anchor}"
        )
    return hits[0]


def _registry_errors(registry: dict, root: Path) -> list[str]:
    errors: list[str] = []
    clauses = registry.get("clauses")
    if not isinstance(clauses, list) or not clauses:
        return ["clauses 必须是非空数组"]
    seen: set[str] = set()
    for entry in clauses:
        if not isinstance(entry, dict):
            errors.append("clauses 中存在非对象条目")
            continue
        clause_id = str(entry.get("id", "")).strip()
        if not clause_id:
            errors.append("条款缺少 id")
            continue
        if clause_id in seen:
            errors.append(f"{clause_id}：id 重复")
        seen.add(clause_id)
        kind = entry.get("kind")
        if kind not in KINDS:
            errors.append(f"{clause_id}：kind 必须是 {KINDS} 之一，实际 {kind!r}")
            continue
        if kind in ("textual", "external") and not str(entry.get("why", "")).strip():
            errors.append(f"{clause_id}：kind={kind} 必须用 why 说明依据")
        if kind == "external":
            witness = str(entry.get("witness", "")).strip()
            if not witness:
                errors.append(f"{clause_id}：kind=external 必须给出 witness")
            elif not (root / witness).exists():
                errors.append(f"{clause_id}：witness 指向的路径不存在：{witness}")
        try:
            derived = _derive(entry, root)
        except (OSError, ValueError, KeyError, IndexError, json.JSONDecodeError) as exc:
            errors.append(f"{clause_id}：{exc}")
            continue
        if entry.get("quote") != derived:
            errors.append(
                f"{clause_id}：登记原文与源文件不一致（登记 {entry.get('quote')!r} / 源文件 {derived!r}）"
            )
    return errors


def _case_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in CASE_GLOBS:
        files.extend(sorted(root.glob(pattern)))
    return files


def _citation_errors(root: Path, files: list[Path], known: set[str]) -> tuple[list[str], dict[str, int]]:
    errors: list[str] = []
    counts: dict[str, int] = {}
    for path in files:
        for number, line in enumerate(_read(path).splitlines(), 1):
            groups = CITE.findall(line)
            if "依据：" in line and not groups:
                errors.append(f"{path.relative_to(root)}:{number}：依据行缺少 `条款：<id>` 标记")
            for group in groups:
                for clause_id in group.split("、"):
                    if clause_id not in known:
                        errors.append(f"{path.relative_to(root)}:{number}：引用了登记表没有的条款 {clause_id}")
                        continue
                    counts[clause_id] = counts.get(clause_id, 0) + 1
    return errors, counts


def evaluate(root: Path, registry_path: Path) -> list[str]:
    try:
        registry = json.loads(_read(registry_path))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"登记表不可读：{registry_path}：{exc}")
    errors = _registry_errors(registry, root)
    clauses = [entry for entry in registry.get("clauses", []) if isinstance(entry, dict)]
    known = {str(entry.get("id", "")).strip() for entry in clauses}
    citation_errors, counts = _citation_errors(root, _case_files(root), known)
    errors.extend(citation_errors)
    for entry in clauses:
        clause_id = str(entry.get("id", "")).strip()
        if entry.get("kind") == "judgmental" and counts.get(clause_id, 0) == 0:
            errors.append(f"{clause_id}：判定性条款没有任何用例以 `条款：{clause_id}` 引用")
    return errors


def _write(root: Path, registry_path: Path) -> int:
    registry = json.loads(_read(registry_path))
    changed = 0
    errors: list[str] = []
    for entry in registry.get("clauses", []):
        try:
            derived = _derive(entry, root)
        except (OSError, ValueError, KeyError, IndexError, json.JSONDecodeError) as exc:
            errors.append(f"{entry.get('id')}：{exc}")
            continue
        if entry.get("quote") != derived:
            entry["quote"] = derived
            changed += 1
    if errors:
        print("\n".join(errors))
        return 1
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已刷新 {changed} 条条款原文；未改动 {len(registry.get('clauses', [])) - changed} 条")
    return 0


def _self_test() -> int:
    """正负例：编造条款、原文漂移、无覆盖、依据行缺标记。"""
    temp = Path(tempfile.mkdtemp(prefix="clause-basis-"))
    try:
        (temp / "spec").mkdir()
        (temp / "scripts").mkdir()
        (temp / "spec" / "src.md").write_text(
            "# 源文件\n\n## 1 规则\n\n- **规则一**：必须拒绝。\n\n## 2 说明\n\n正文。\n",
            encoding="utf-8",
        )
        registry = {
            "clauses": [
                {
                    "id": "SRC-1-A",
                    "source": "spec/src.md",
                    "locator": "heading",
                    "section": "1",
                    "anchor": "**规则一**",
                    "kind": "judgmental",
                    "why": "",
                    "quote": "- **规则一**：必须拒绝。",
                },
                {
                    "id": "SRC-2-T",
                    "source": "spec/src.md",
                    "locator": "heading",
                    "section": "2",
                    "anchor": "正文。",
                    "kind": "textual",
                    "why": "说明性文字，无判定条件。",
                    "quote": "正文。",
                },
            ]
        }
        registry_path = temp / "spec" / "registry.json"
        registry_path.write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")
        case = temp / "scripts" / "test_demo.py"
        case.write_text("# 依据：条款：SRC-1-A\n", encoding="utf-8")

        results: list[tuple[str, bool, str]] = []

        errors = evaluate(temp, registry_path)
        results.append(("正例：引用登记内条款", not errors, str(errors)))

        case.write_text("# 依据：条款：SRC-1-BOGUS\n", encoding="utf-8")
        errors = evaluate(temp, registry_path)
        results.append(
            ("负例：编造条款被拒", any("SRC-1-BOGUS" in item and "没有的条款" in item for item in errors), str(errors))
        )

        case.write_text("# 依据：条款：SRC-1-A\n", encoding="utf-8")
        registry["clauses"][0]["quote"] = "- **规则一**：必须放行。"
        registry_path.write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")
        errors = evaluate(temp, registry_path)
        results.append(
            ("负例：原文与源文件不一致被拒", any("不一致" in item for item in errors), str(errors))
        )

        registry["clauses"][0]["quote"] = "- **规则一**：必须拒绝。"
        registry_path.write_text(json.dumps(registry, ensure_ascii=False), encoding="utf-8")
        case.write_text("# 无引用\n", encoding="utf-8")
        errors = evaluate(temp, registry_path)
        results.append(
            ("负例：判定性条款无覆盖被拒", any("没有任何用例" in item for item in errors), str(errors))
        )

        case.write_text("# 依据：见提案 4.3(1)\n", encoding="utf-8")
        errors = evaluate(temp, registry_path)
        results.append(
            ("负例：依据行无条款标记被拒", any("缺少 `条款：<id>` 标记" in item for item in errors), str(errors))
        )
    finally:
        shutil.rmtree(temp, ignore_errors=True)

    failed = 0
    for name, ok, detail in results:
        print(f"{'通过' if ok else '失败'}：{name}" + ("" if ok else f"（{detail}）"))
        failed += 0 if ok else 1
    print(f"自测 {len(results) - failed}/{len(results)} 通过")
    return 0 if failed == 0 else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="检查用例的条款依据与登记表一致性")
    parser.add_argument("--write", action="store_true", help="从源文件重新提取条款原文")
    parser.add_argument("--self-test", action="store_true", help="运行内置正负例")
    args = parser.parse_args(argv)
    if args.self_test:
        return _self_test()
    if args.write:
        return _write(ROOT, REGISTRY)
    errors = evaluate(ROOT, REGISTRY)
    for error in errors:
        print(error)
    print(f"条款登记 {len(json.loads(_read(REGISTRY)).get('clauses', []))} 条；缺陷 {len(errors)} 项")
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
