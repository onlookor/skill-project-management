#!/usr/bin/env python3
"""规格区段绑定：GRAMMAR.md 全文、A.2、schema §2bis/§3/§4 各自登记指纹。

规则：
  1. 任一区段当前指纹与 scripts/spec-pins.json 不一致 → 阻断（先 --write）；
  2. 区段相对 HEAD 有改动时，同一提交必须附合格的非同源复核记录，否则阻断；
  3. 复核记录须同时含：`非同源复核：`、`区段：<key>`、`复核产物：<文件名>`、
     以及结论词之一（实质收敛 / 认可 / 通过）。

记录文件放在 validation/reviews/ 下并在同一提交暂存；也可用 --review 指定。
这不是“签收人身份验证”：机器只能核对记录的存在与字段，不能验证复核者是谁。

用法：
  python3 scripts/check_spec_pins.py
  python3 scripts/check_spec_pins.py --write
  python3 scripts/check_spec_pins.py --review validation/reviews/20261114-xxx.md
退出码：0 = 一致；1 = 指纹未更新或缺少复核记录；2 = 解析/登记缺失。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

PINS = Path("scripts/spec-pins.json")
METHOD = "spec/methods/deterministic-checker.md"
SCHEMA = "spec/CHECKER_INPUT_SCHEMA.md"
CONCLUSIONS = ("实质收敛", "认可", "通过")

SECTIONS = (
    {"key": "GRAMMAR.md", "path": "GRAMMAR.md", "start": None, "end": None},
    {"key": f"{METHOD}#A.2", "path": METHOD, "start": "### A.2 ", "end": "### A.1 "},
    {"key": f"{SCHEMA}#2bis", "path": SCHEMA, "start": "## 2bis. ", "end": "## 3. "},
    {"key": f"{SCHEMA}#3", "path": SCHEMA, "start": "## 3. ", "end": "## 3bis. "},
    {"key": f"{SCHEMA}#4", "path": SCHEMA, "start": "## 4. ", "end": "## 5. "},
)


def section_text(text: str, start: str | None, end: str | None) -> str:
    lines = text.splitlines()
    if start is None:
        return "\n".join(line.rstrip() for line in lines).strip("\n")
    begin = next((i for i, line in enumerate(lines) if line.startswith(start)), None)
    if begin is None:
        raise ValueError(f"找不到区段起点 {start!r}")
    finish = len(lines)
    for index in range(begin + 1, len(lines)):
        if end is not None and lines[index].startswith(end):
            finish = index
            break
    chunk = [line.rstrip() for line in lines[begin:finish]]
    while chunk and not chunk[-1]:
        chunk.pop()
    return "\n".join(chunk)


def fingerprint(text: str, start: str | None, end: str | None) -> str:
    return hashlib.sha256(section_text(text, start, end).encode("utf-8")).hexdigest()


def load_pins(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "sections": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def valid_review(reviews: list[str], key: str, file_name: str) -> bool:
    for text in reviews:
        if "非同源复核：" not in text:
            continue
        if f"区段：{key}" not in text:
            continue
        if "复核产物：" not in text or file_name not in text:
            continue
        if not any(word in text for word in CONCLUSIONS):
            continue
        return True
    return False


def evaluate(
    current: dict[str, str],
    head: dict[str, str | None],
    pins: dict[str, str],
    reviews: list[str],
) -> list[str]:
    errors: list[str] = []
    for spec in SECTIONS:
        key = spec["key"]
        if key not in current:
            errors.append(f"{key}：当前文件缺失")
            continue
        actual = fingerprint(current[key], spec["start"], spec["end"])
        registered = pins.get(key)
        if isinstance(registered, dict):
            registered = registered.get("sha256")
        if registered is None:
            errors.append(f"{key}：指纹未登记（运行 --write）")
        elif registered != actual:
            errors.append(
                f"{key}：指纹未更新（当前 {actual[:12]}，登记 {registered[:12]}）"
            )
        head_text = head.get(key)
        changed = head_text is None or fingerprint(head_text, spec["start"], spec["end"]) != actual
        if changed and not valid_review(reviews, key, Path(spec["path"]).name):
            errors.append(
                f"{key}：区段已改动但同一提交缺少合格的非同源复核记录"
                f"（需含 `非同源复核：`、`区段：{key}`、`复核产物：{Path(spec['path']).name}`、"
                f"结论词 {'/'.join(CONCLUSIONS)}）"
            )
    for key in sorted(set(pins) - {spec["key"] for spec in SECTIONS}):
        errors.append(f"{key}：登记项指向未定义的区段")
    return errors


def read_head(root: Path, path: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"HEAD:{path}"], cwd=root, capture_output=True, text=True
    )
    return result.stdout if result.returncode == 0 else None


def staged_reviews(root: Path) -> list[str]:
    listed = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=AM"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    texts = []
    for name in listed.stdout.split():
        if name.startswith("validation/reviews/") and name.endswith(".md"):
            path = root / name
            if path.exists():
                texts.append(path.read_text(encoding="utf-8"))
    return texts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="仓库根目录；默认由脚本位置推断")
    parser.add_argument("--pins", help="登记文件；默认 scripts/spec-pins.json")
    parser.add_argument("--review", action="append", default=[], help="复核记录文件，可重复")
    parser.add_argument("--write", action="store_true", help="按当前内容重写区段指纹")
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    pins_path = Path(args.pins) if args.pins else root / PINS

    try:
        current = {
            spec["key"]: (root / spec["path"]).read_text(encoding="utf-8")
            for spec in SECTIONS
        }
        pins = load_pins(pins_path)
        if args.write:
            sections = {}
            for spec in SECTIONS:
                sections[spec["key"]] = {
                    "sha256": fingerprint(current[spec["key"]], spec["start"], spec["end"]),
                    "path": spec["path"],
                }
            pins = {
                "version": 1,
                "note": "规格区段指纹。区段改动必须 --write 并同批附非同源复核记录；指纹只证明内容一致，不证明签收人身份。",
                "sections": sections,
            }
            pins_path.write_text(
                json.dumps(pins, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            print(f"[完成] 已登记 {len(sections)} 个规格区段指纹。")
            return 0
        head = {spec["key"]: read_head(root, spec["path"]) for spec in SECTIONS}
        reviews = [
            Path(path).read_text(encoding="utf-8") for path in args.review
        ] or staged_reviews(root)
        errors = evaluate(current, head, pins.get("sections", {}), reviews)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[错误] 解析失败：{exc}")
        return 2

    for error in errors:
        print(f"[错误] {error}")
    registered = len(pins.get("sections", {}))
    print(
        f"规格区段绑定：区段 {len(SECTIONS)}，已登记 {registered}，"
        f"复核记录 {len(reviews)}，问题 {len(errors)}"
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
