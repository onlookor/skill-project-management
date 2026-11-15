#!/usr/bin/env python3
"""规格区段绑定：GRAMMAR.md 全文、A.2、A.1、schema §2bis/§3/§4、全部数据 schema、coverage.json。

规则：
  1. 任一区段当前指纹与 scripts/spec-pins.json 不一致 → 阻断（先 --write）；
  2. `contracts/schema/` 下任何文件未登记为区段 → 阻断（自动发现，取代人工清单）；
  3. 区段相对 HEAD 有改动时，同一提交必须附合格的非同源复核记录，否则阻断；
  4. 复核标准与 `check_checker_pins.py` 对齐：依据必须指向**仓库外**的复核产物，
     并给出 `sha256：<64 位>`、`复核基线：<提交号>`、`区段：<所绑区段>` 与结论词；
     仓库内转录件只作索引，不作依据。**默认读取模式同样校验这些字段**，只改 basis
     文本会被阻断；`初始登记` 前缀表示无复核声明的历史登记项，不参与字段校验。
  5. `--write` 新增或变更的区段必须附 `--basis`（同样要求外部产物 + sha256），
     登记项逐区段保存 basis；未变更的旧登记项保留原值或标为“初始登记”。

记录文件放在 validation/reviews/ 下并在同一提交暂存；也可用 --review 指定。
这不是“签收人身份验证”：机器只能核对记录的存在与字段，不能验证复核者是谁。

用法：
  python3 scripts/check_spec_pins.py
  python3 scripts/check_spec_pins.py --write --basis "非同源复核：... 复核产物：/abs/report.md sha256：<64hex> 复核基线：3664b64"
  python3 scripts/check_spec_pins.py --review validation/reviews/20261114-xxx.md
退出码：0 = 一致；1 = 指纹未更新或缺少复核记录；2 = 解析/登记缺失或 basis 不合格。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

PINS = Path("scripts/spec-pins.json")
METHOD = "spec/methods/deterministic-checker.md"
SCHEMA = "spec/CHECKER_INPUT_SCHEMA.md"
SCHEMA_DIR = "contracts/schema"
CONCLUSIONS = ("实质收敛", "认可", "通过")

SECTIONS = (
    {"key": "GRAMMAR.md", "path": "GRAMMAR.md", "start": None, "end": None},
    {"key": f"{METHOD}#A.2", "path": METHOD, "start": "### A.2 ", "end": "### A.1 "},
    {"key": f"{METHOD}#A.1", "path": METHOD, "start": "### A.1 ", "end": None},
    {"key": f"{SCHEMA}#2bis", "path": SCHEMA, "start": "## 2bis. ", "end": "## 3. "},
    {"key": f"{SCHEMA}#3", "path": SCHEMA, "start": "## 3. ", "end": "## 3bis. "},
    {"key": f"{SCHEMA}#4", "path": SCHEMA, "start": "## 4. ", "end": "## 5. "},
    {
        "key": "validation/checker-prototype/coverage.json",
        "path": "validation/checker-prototype/coverage.json",
        "start": None,
        "end": None,
    },
    {
        "key": "contracts/schema/knowledge-entry.schema.json",
        "path": "contracts/schema/knowledge-entry.schema.json",
        "start": None,
        "end": None,
    },
    {
        "key": "contracts/schema/pilot-conflict.schema.json",
        "path": "contracts/schema/pilot-conflict.schema.json",
        "start": None,
        "end": None,
    },
    {
        "key": "contracts/schema/pm-slot-contract.schema.json",
        "path": "contracts/schema/pm-slot-contract.schema.json",
        "start": None,
        "end": None,
    },
    {
        "key": "contracts/schema/package-manifest.schema.json",
        "path": "contracts/schema/package-manifest.schema.json",
        "start": None,
        "end": None,
    },
    {
        "key": "contracts/schema/ontology-fixtures-manifest.schema.json",
        "path": "contracts/schema/ontology-fixtures-manifest.schema.json",
        "start": None,
        "end": None,
    },
    {
        "key": "contracts/schema/pilot-artifact.schema.json",
        "path": "contracts/schema/pilot-artifact.schema.json",
        "start": None,
        "end": None,
    },
    {
        "key": "contracts/schema/pilot-id-map.schema.json",
        "path": "contracts/schema/pilot-id-map.schema.json",
        "start": None,
        "end": None,
    },
    {
        "key": "spec/ACCESS_ZONES.md",
        "path": "spec/ACCESS_ZONES.md",
        "start": None,
        "end": None,
    },
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def discover_schema_files(root: Path) -> list[str]:
    """`contracts/schema/` 下全部文件（含子目录）；未登记为区段即视为漏钉。"""
    directory = root / SCHEMA_DIR
    if not directory.is_dir():
        return []
    return sorted(
        path.relative_to(root).as_posix()
        for path in directory.rglob("*")
        if path.is_file()
    )


def valid_basis(root: Path, text: str, key: str) -> tuple[bool, str]:
    """默认模式与 --write 共用：basis 必须指向仓库外产物、sha256 一致且区段正确。

    `初始登记`（含 `初始登记：...`）明确表示“无复核声明”，只保留历史指针，
    不参与复核字段校验；除此之外一律按完整字段核对。
    """
    text = text.strip()
    if text == "初始登记" or text.startswith("初始登记："):
        return True, ""
    if "非同源复核：" not in text:
        return False, "缺少 `非同源复核：` 前缀"
    artifact = re.search(r"复核产物：`?([^`\s；，、]+)`?", text)
    if artifact is None:
        return False, "缺少 `复核产物：<路径>`"
    artifact_path = Path(artifact.group(1))
    if not artifact_path.exists():
        return False, f"复核产物不存在：{artifact_path}"
    try:
        artifact_path.resolve().relative_to(root.resolve())
    except ValueError:
        pass
    else:
        return False, "复核产物位于本仓库内；转录件只作索引，不能作为 basis"
    if re.search(r"复核基线：`?[0-9a-f]{7,40}`?", text) is None:
        return False, "缺少 `复核基线：<提交号>`"
    recorded = re.search(r"sha256：`?([0-9a-f]{64})`?", text)
    if recorded is None:
        return False, "缺少 `sha256：<64 位十六进制>`"
    if digest(artifact_path) != recorded.group(1):
        return False, "`sha256` 与复核产物不一致"
    if re.search(rf"区段：`?{re.escape(key)}`?", text) is None:
        return False, f"缺少 `区段：{key}` 或与所绑区段不一致"
    if not any(word in text for word in CONCLUSIONS):
        return False, f"缺少结论词（{'/'.join(CONCLUSIONS)}）"
    return True, ""



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


def valid_review(root: Path, reviews: list[str], key: str) -> bool:
    pattern = re.compile(rf"区段：`?{re.escape(key)}`?")
    for text in reviews:
        if pattern.search(text) is None:
            continue
        if not any(word in text for word in CONCLUSIONS):
            continue
        ok, _ = valid_basis(root, text, key)
        if ok:
            return True
    return False


def evaluate(
    root: Path,
    current: dict[str, str],
    head: dict[str, str | None],
    pins: dict[str, dict],
    reviews: list[str],
) -> list[str]:
    errors: list[str] = []
    for spec in SECTIONS:
        key = spec["key"]
        if key not in current:
            errors.append(f"{key}：当前文件缺失")
            continue
        actual = fingerprint(current[key], spec["start"], spec["end"])
        entry = pins.get(key)
        if isinstance(entry, str):
            entry = {"sha256": entry}
        registered = entry.get("sha256") if isinstance(entry, dict) else None
        if registered is None:
            errors.append(f"{key}：指纹未登记（运行 --write）")
        elif registered != actual:
            errors.append(
                f"{key}：指纹未更新（当前 {actual[:12]}，登记 {registered[:12]}）"
            )
        if isinstance(entry, dict):
            basis = entry.get("basis")
            if not basis:
                errors.append(f"{key}：登记项缺少 basis 裁定依据")
            else:
                ok, why = valid_basis(root, basis, key)
                if not ok:
                    errors.append(f"{key}：basis 不合格：{why}")
        head_text = head.get(key)
        changed = head_text is None or fingerprint(head_text, spec["start"], spec["end"]) != actual
        if changed and not valid_review(root, reviews, key):
            errors.append(
                f"{key}：区段已改动但同一提交缺少合格的非同源复核记录"
                f"（需含 `区段：{key}`、结论词 {'/'.join(CONCLUSIONS)}，"
                "且 `复核产物：` 指向仓库外文件、`sha256：` 与之一致、含 `复核基线：`）"
            )
    declared = {spec["path"] for spec in SECTIONS}
    for path in discover_schema_files(root):
        if path not in declared:
            errors.append(
                f"{path}：`{SCHEMA_DIR}/` 下的文件未登记为规格区段（自动发现；"
                "新增 schema 必须同批登记）"
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
    parser.add_argument(
        "--basis",
        action="append",
        default=[],
        help="非同源复核记录（新增或变更区段时必填；可重复，按 `区段：` 匹配对应区段）",
    )
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    pins_path = Path(args.pins) if args.pins else root / PINS

    try:
        current = {
            spec["key"]: (root / spec["path"]).read_text(encoding="utf-8")
            for spec in SECTIONS
        }
        pins = load_pins(pins_path)
        previous = pins.get("sections", {})
        if args.write:
            sections = {}
            changed: list[str] = []
            chosen: dict[str, str] = {}
            for spec in SECTIONS:
                key = spec["key"]
                actual = fingerprint(current[key], spec["start"], spec["end"])
                old = previous.get(key)
                if isinstance(old, str):
                    old = {"sha256": old}
                old_sha = old.get("sha256") if isinstance(old, dict) else None
                if old_sha != actual:
                    changed.append(key)
                    match = next(
                        (text for text in args.basis if valid_basis(root, text, key)[0]),
                        None,
                    )
                    if match is None:
                        why = (
                            valid_basis(root, args.basis[0], key)[1]
                            if args.basis
                            else "缺少 --basis"
                        )
                        print(f"[错误] 区段 {key} 有新增或变更，但 --basis 不合格：{why}")
                        return 2
                    chosen[key] = match.strip()
                sections[key] = {
                    "sha256": actual,
                    "path": spec["path"],
                    "basis": (
                        chosen[key]
                        if old_sha != actual
                        else (old or {}).get("basis") or "初始登记"
                    ),
                }
            pins = {
                "version": 1,
                "note": (
                    "规格区段指纹。区段新增或改动必须 --write --basis 并同批附非同源复核记录；"
                    "basis 必须指向仓库外复核产物并与其 sha256 一致。指纹只证明内容一致，不证明签收人身份。"
                ),
                "sections": sections,
            }
            pins_path.write_text(
                json.dumps(pins, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            print(
                f"[完成] 已登记 {len(sections)} 个规格区段指纹"
                f"（本次新增或变更 {len(changed)} 个）。"
            )
            return 0
        head = {spec["key"]: read_head(root, spec["path"]) for spec in SECTIONS}
        reviews = [
            Path(path).read_text(encoding="utf-8") for path in args.review
        ] or staged_reviews(root)
        errors = evaluate(root, current, head, previous, reviews)
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
