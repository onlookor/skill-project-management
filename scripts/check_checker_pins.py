#!/usr/bin/env python3
"""检查器绑定：受保护脚本的哈希必须与 registry 登记一致。

受保护对象包括：
  - scripts/ 下全部检查器脚本（含 check_checker_pins.py 自身，不再自排除）；
  - .githooks/pre-commit（钩子本身就是验证链的一环）；
  - validation/checker-prototype/checker.py（验收用原型）。

改动任何一个都必须 `--write --basis "<非同源复核记录>"` 更新登记。basis 不是自由文本：
必须含 `非同源复核：`、`复核产物：<存在的文件>`、`复核基线：<提交号>`，否则拒绝写入。

附带漂移检测：validation/pinned/checker.py 是验收原型的只读快照，默认模式校验字节一致。
注意：这只是**漂移检测**，不是权限分离——文件都在同一工作区，同一方可以同改；
真正的分离需要 CI/受保护分支（见 ADR-0014）。

用法：
  python3 scripts/check_checker_pins.py
  python3 scripts/check_checker_pins.py --write --basis "非同源复核：... 复核产物：validation/reviews/x.md 复核基线：d8bf413"
退出码：0 = 一致；1 = 哈希不一致/未登记；2 = 登记缺失或 basis 不合格。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

PINS = Path("scripts/checker-pins.json")
CHECKER_GLOBS = ("check_*.py", "test_*.py", "validate_*.py")
EXTRA_PATHS = (".githooks/pre-commit", "validation/checker-prototype/checker.py")
SNAPSHOT = Path("validation/pinned/checker.py")
SOURCE = Path("validation/checker-prototype/checker.py")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def discover(root: Path) -> list[str]:
    names: set[str] = set()
    scripts_dir = root / "scripts"
    for pattern in CHECKER_GLOBS:
        for path in scripts_dir.glob(pattern):
            if path.is_file():
                names.add(f"scripts/{path.name}")
    for name in EXTRA_PATHS:
        if (root / name).is_file():
            names.add(name)
    return sorted(names)


def load_pins(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "scripts": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def write_pins(path: Path, pins: dict) -> None:
    path.write_text(
        json.dumps(pins, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def valid_basis(root: Path, text: str) -> tuple[bool, str]:
    """basis 必须是可核对到复核产物的非同源复核记录，不接受自由文本。"""
    if "非同源复核：" not in text:
        return False, "缺少 `非同源复核：` 前缀"
    artifact = re.search(r"复核产物：`?([^`\s；，、]+)`?", text)
    if artifact is None:
        return False, "缺少 `复核产物：<路径>`"
    if not (root / artifact.group(1)).exists():
        return False, f"复核产物不存在：{artifact.group(1)}"
    if re.search(r"复核基线：`?[0-9a-f]{7,40}`?", text) is None:
        return False, "缺少 `复核基线：<提交号>`"
    return True, ""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="仓库根目录；默认由脚本位置推断")
    parser.add_argument("--pins", help="登记文件；默认 <root>/scripts/checker-pins.json")
    parser.add_argument("--snapshot", help="验收检查器快照；默认 validation/pinned/checker.py")
    parser.add_argument("--source", help="工作区验收检查器；默认 validation/checker-prototype/checker.py")
    parser.add_argument("--write", action="store_true", help="按当前哈希重写登记")
    parser.add_argument("--basis", default="", help="非同源复核记录（--write 且哈希有变化时必填）")
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    pins_path = Path(args.pins) if args.pins else root / PINS
    snapshot = Path(args.snapshot) if args.snapshot else root / SNAPSHOT
    source = Path(args.source) if args.source else root / SOURCE

    pins = load_pins(pins_path)
    entries = pins.setdefault("scripts", {})
    names = discover(root)
    changed: list[str] = []
    for name in names:
        actual = digest(root / name)
        entry = entries.get(name)
        if entry is None:
            changed.append(f"{name}：未登记")
        elif entry.get("sha256") != actual:
            changed.append(
                f"{name}：哈希不一致（登记 {entry.get('sha256', '')[:12]}，工作区 {actual[:12]}）"
            )

    if args.write:
        if changed:
            ok, why = valid_basis(root, args.basis)
            if not ok:
                print(f"[错误] 检查器有改动，但 --basis 不合格：{why}")
                for item in changed:
                    print(f"  - {item}")
                return 2
        for name in names:
            actual = digest(root / name)
            entry = entries.setdefault(name, {})
            if entry.get("sha256") != actual:
                entry["sha256"] = actual
                entry["basis"] = args.basis.strip()
            else:
                entry.setdefault("sha256", actual)
                entry.setdefault("basis", "初始登记")
        for name in sorted(set(entries) - set(names)):
            del entries[name]
        pins["version"] = 1
        pins["note"] = (
            "受保护脚本的哈希登记：scripts/ 下检查器（含本脚本）、.githooks/pre-commit、"
            "validation/checker-prototype/checker.py。改动必须 --write --basis 并附非同源复核记录；"
            "本文件与快照检测都不提供权限分离。"
        )
        write_pins(pins_path, pins)
        if source.exists() and snapshot != source:
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            snapshot.write_bytes(source.read_bytes())
        print(f"[完成] 已登记 {len(entries)} 个受保护对象；快照已同步。")
        return 0

    errors = list(changed)
    for name in sorted(set(entries) - set(names)):
        errors.append(f"{name}：登记项指向不存在的脚本")
    for name, entry in sorted(entries.items()):
        if not entry.get("basis"):
            errors.append(f"{name}：登记项缺少 basis 裁定依据")

    if source.exists() and snapshot.exists():
        if digest(source) != digest(snapshot):
            errors.append(
                "验收检查器与 validation/pinned/checker.py 快照不一致；"
                "请先复核快照再运行 --write（漂移检测，不等于权限分离）"
            )
    elif source.exists() != snapshot.exists():
        errors.append("验收检查器与快照只存在其一")

    for error in errors:
        print(f"[错误] {error}")
    print(
        f"检查器绑定：登记 {len(entries)}，工作区 {len(names)}，"
        f"快照 {'一致' if source.exists() and snapshot.exists() and digest(source) == digest(snapshot) else '不一致'}，"
        f"问题 {len(errors)}"
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
