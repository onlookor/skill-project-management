#!/usr/bin/env python3
"""检查器绑定：scripts/ 下每个检查器脚本的哈希必须与 registry 登记一致。

目的：把“静默改检查器”变成“显式改且留痕”。改动脚本时必须同时运行
`--write --basis "裁定依据"` 更新登记值，否则提交被阻断。

附带漂移检测：validation/pinned/checker.py 是验收用检查器的只读快照，
默认模式校验它与 validation/checker-prototype/checker.py 字节一致。
注意：这只是**漂移检测**，不是权限分离——两份文件都在同一工作区，同一方
可以同改；真正的分离需要 CI 或受保护分支（见 ADR-0014）。

用法：
  python3 scripts/check_checker_pins.py
  python3 scripts/check_checker_pins.py --write --basis "批次 0041：新增 X 检查"
退出码：0 = 一致；1 = 哈希不一致/未登记；2 = 登记缺失或参数错误。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

PINS = Path("scripts/checker-pins.json")
CHECKER_GLOBS = ("check_*.py", "test_*.py", "validate_*.py")
SNAPSHOT = Path("validation/pinned/checker.py")
SOURCE = Path("validation/checker-prototype/checker.py")
IGNORED = {"check_checker_pins.py"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def discover(scripts_dir: Path) -> list[str]:
    names: set[str] = set()
    for pattern in CHECKER_GLOBS:
        for path in scripts_dir.glob(pattern):
            if path.is_file() and path.name not in IGNORED:
                names.add(path.name)
    return sorted(names)


def load_pins(path: Path) -> dict:
    if not path.exists():
        return {"version": 1, "scripts": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def write_pins(path: Path, pins: dict) -> None:
    path.write_text(
        json.dumps(pins, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="仓库根目录；默认由脚本位置推断")
    parser.add_argument("--scripts-dir", help="脚本目录；默认 <root>/scripts")
    parser.add_argument("--pins", help="登记文件；默认 <root>/scripts/checker-pins.json")
    parser.add_argument("--snapshot", help="验收检查器快照；默认 validation/pinned/checker.py")
    parser.add_argument("--source", help="工作区验收检查器；默认 validation/checker-prototype/checker.py")
    parser.add_argument("--write", action="store_true", help="按当前哈希重写登记")
    parser.add_argument("--basis", default="", help="改动检查器的裁定依据（--write 时必填）")
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    scripts_dir = Path(args.scripts_dir) if args.scripts_dir else root / "scripts"
    pins_path = Path(args.pins) if args.pins else root / PINS
    snapshot = Path(args.snapshot) if args.snapshot else root / SNAPSHOT
    source = Path(args.source) if args.source else root / SOURCE

    pins = load_pins(pins_path)
    entries = pins.setdefault("scripts", {})
    names = discover(scripts_dir)
    changed: list[str] = []
    for name in names:
        actual = digest(scripts_dir / name)
        entry = entries.get(name)
        if entry is None:
            changed.append(f"{name}：未登记")
        elif entry.get("sha256") != actual:
            changed.append(
                f"{name}：哈希不一致（登记 {entry.get('sha256', '')[:12]}，工作区 {actual[:12]}）"
            )

    if args.write:
        if changed and not args.basis.strip():
            print("[错误] 检查器有改动但未提供 --basis 裁定依据：")
            for item in changed:
                print(f"  - {item}")
            return 2
        for name in names:
            actual = digest(scripts_dir / name)
            entry = entries.setdefault(name, {})
            if entry.get("sha256") != actual:
                entry["sha256"] = actual
                entry["basis"] = args.basis.strip() or entry.get("basis", "")
            else:
                entry.setdefault("sha256", actual)
                entry.setdefault("basis", "初始登记")
        for name in sorted(set(entries) - set(names)):
            del entries[name]
        pins["version"] = 1
        pins["note"] = (
            "scripts/ 下检查器脚本的哈希登记。改动脚本必须 --write --basis 更新，"
            "使“改检查器”显式留痕；本文件不提供权限分离。"
        )
        write_pins(pins_path, pins)
        if source.exists() and snapshot != source:
            snapshot.parent.mkdir(parents=True, exist_ok=True)
            snapshot.write_bytes(source.read_bytes())
        print(f"[完成] 已登记 {len(entries)} 个检查器脚本；快照已同步。")
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
