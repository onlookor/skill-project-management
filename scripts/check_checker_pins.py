#!/usr/bin/env python3
"""检查器绑定：受保护脚本的哈希必须与 registry 登记一致。

受保护对象包括：
  - 全仓全部 `.py`（`git ls-files --cached --others` 发现，`PY_EXCLUDE` 当前为空），
    含本脚本自身；新增 helper 脚本默认受保护，不再依赖文件名 glob；
  - `.githooks/pre-commit`（钩子本身就是验证链的一环）；
  - `scripts/no-review-declarations.json`（无复核例外登记表，改表需复核或例外留痕）。

basis 只有两种合法形态：
  1. 合格的非同源复核记录：含 `非同源复核：`、`复核产物：<仓库外存在的文件>`、
     `sha256：<64 位>`（与产物实算一致）、`复核基线：<HEAD 的祖先提交>`、
     唯一一条精确等值的 `区段：`，以及**行尾**结论词（`实质收敛`/`认可`/`通过`，
     后面不得跟括号补充）；
  2. 固定字面量 `无复核声明（不构成认可，不放行）`——它**不构成认可、也不放行**，
     登记项会持续报错，只能以 `git commit --no-verify` 提交，并须在
     `scripts/no-review-declarations.json` 与 `TODO.md` 到期项中留痕（AGENTS.md 3.5.3）。
不存在“待复核”之类的自我声明通行证：任何自我声明都不会让检查器返回 0。

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
import subprocess
import sys
from pathlib import Path

PINS = Path("scripts/checker-pins.json")
REGISTRY = Path("scripts/no-review-declarations.json")
# 全仓 .py 的排除项；当前为空——新增 helper 脚本默认受保护。
PY_EXCLUDE: frozenset[str] = frozenset()
EXTRA_PATHS = (".githooks/pre-commit", str(REGISTRY))
SNAPSHOT = Path("validation/pinned/checker.py")
SOURCE = Path("validation/checker-prototype/checker.py")
CONCLUSIONS = ("实质收敛", "认可", "通过")
# 唯一允许的“无复核”字面量：它记录事实，但不构成认可、也不放行。
DECLARATION = "无复核声明（不构成认可，不放行）"
REGISTRY_FIELDS = ("reason", "missing_review", "due", "owner", "todo")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_registry(root: Path) -> dict:
    path = root / REGISTRY
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("checker", {}) if isinstance(data, dict) else {}


def discover(root: Path) -> list[str]:
    """全仓 `.py`（含未跟踪但未被忽略者）+ 显式附加对象，减去 `PY_EXCLUDE`。"""
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "*.py"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if listed.returncode == 0:
        candidates = listed.stdout.split()
    else:
        candidates = [
            path.relative_to(root).as_posix()
            for path in root.rglob("*.py")
            if ".git" not in path.parts
        ]
    names = {name for name in candidates if name not in PY_EXCLUDE}
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


def valid_basis(root: Path, text: str, key: str) -> tuple[bool, str]:
    """basis 只接受合格的非同源复核记录；“无复核声明”记录事实但永不通过。

    五要素：`非同源复核：`、仓库外 `复核产物：`、与产物一致的 `sha256：`、
    `复核基线：`（HEAD 的祖先提交）、唯一且等值的 `区段：`、行尾结论词。
    """
    text = text.strip()
    if text == DECLARATION:
        return False, (
            "无复核声明：不构成认可，也不放行（例外只能 --no-verify 提交，并须在 "
            "scripts/no-review-declarations.json 与 TODO.md 到期项中留痕）"
        )
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
    baseline = re.search(r"复核基线：`?([0-9a-f]{7,40})`?", text)
    if baseline is None:
        return False, "缺少 `复核基线：<提交号>`"
    sha = baseline.group(1)
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=root, capture_output=True
    )
    if exists.returncode != 0:
        return False, f"复核基线不存在：{sha}"
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", sha, "HEAD"],
        cwd=root,
        capture_output=True,
    )
    if ancestor.returncode != 0:
        return False, f"复核基线不是 HEAD 的祖先提交（无关提交）：{sha}"
    recorded = re.search(r"sha256：`?([0-9a-f]{64})`?", text)
    if recorded is None:
        return False, "缺少 `sha256：<64 位十六进制>`"
    if digest(artifact_path) != recorded.group(1):
        return False, "`sha256` 与复核产物不一致"
    segments = re.findall(r"区段：\s*`?([^`\s；，、]+)`?", text)
    if segments != [key]:
        return False, f"`区段：` 必须精确等于 {key} 且只出现一次"
    if re.search(r"结论：\s*(?:不|未|无法)", text) is not None:
        return False, "结论词被否定（`不予`/`未`/`无法` 前缀）"
    if re.search(
        rf"结论：\s*(?:{'|'.join(CONCLUSIONS)})(?=[ \t]*(?:$|[；;。]))", text, re.M
    ) is None:
        return False, (
            f"缺少结论词或其后紧跟补充说明（{'/'.join(CONCLUSIONS)}）；"
            "结论词后只允许行尾或 `；`/`。` 分隔，不得跟括号"
        )
    return True, ""


def writable(root: Path, text: str, key: str) -> tuple[bool, str]:
    """`--write` 放行口径：合格复核记录，或无复核字面量（后者写入后仍会报错）。"""
    if text.strip() == DECLARATION:
        return True, ""
    return valid_basis(root, text, key)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="仓库根目录；默认由脚本位置推断")
    parser.add_argument("--pins", help="登记文件；默认 <root>/scripts/checker-pins.json")
    parser.add_argument("--snapshot", help="验收检查器快照；默认 validation/pinned/checker.py")
    parser.add_argument("--source", help="工作区验收检查器；默认 validation/checker-prototype/checker.py")
    parser.add_argument("--write", action="store_true", help="按当前哈希重写登记")
    parser.add_argument(
        "--basis",
        action="append",
        default=[],
        help="非同源复核记录（--write 且哈希有变化时必填；可重复，按 `区段：` 匹配对应对象）",
    )
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    pins_path = Path(args.pins) if args.pins else root / PINS
    snapshot = Path(args.snapshot) if args.snapshot else root / SNAPSHOT
    source = Path(args.source) if args.source else root / SOURCE

    pins = load_pins(pins_path)
    entries = pins.setdefault("scripts", {})
    names = discover(root)
    changed: list[str] = []
    changed_keys: list[str] = []
    for name in names:
        actual = digest(root / name)
        entry = entries.get(name)
        if entry is None:
            changed.append(f"{name}：未登记")
            changed_keys.append(name)
        elif entry.get("sha256") != actual:
            changed.append(
                f"{name}：哈希不一致（登记 {entry.get('sha256', '')[:12]}，工作区 {actual[:12]}）"
            )
            changed_keys.append(name)

    if args.write:
        if changed and not args.basis:
            print("[错误] 检查器有改动，但未提供 --basis")
            for item in changed:
                print(f"  - {item}")
            return 2
        chosen: dict[str, str] = {}
        for key in changed_keys:
            match = next(
                (text for text in args.basis if writable(root, text, key)[0]), None
            )
            if match is None:
                why = writable(root, args.basis[0], key)[1] if args.basis else "缺少 --basis"
                print(f"[错误] {key} 的 --basis 不合格：{why}")
                return 2
            chosen[key] = match.strip()
        for name in names:
            actual = digest(root / name)
            entry = entries.setdefault(name, {})
            if entry.get("sha256") != actual:
                entry["sha256"] = actual
                entry["basis"] = chosen[name]
            else:
                entry.setdefault("sha256", actual)
                entry.setdefault("basis", DECLARATION)
        for name in sorted(set(entries) - set(names)):
            del entries[name]
        pins["version"] = 1
        pins["note"] = (
            "受保护脚本的哈希登记：全仓 .py（含本脚本）、.githooks/pre-commit、"
            "validation/checker-prototype/checker.py 与 scripts/no-review-declarations.json。"
            "改动必须 --write --basis 并附非同源复核记录；无复核时只能写固定声明并以 "
            "--no-verify 提交。本文件与快照检测都不提供权限分离。"
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
        basis = entry.get("basis")
        if not basis:
            errors.append(f"{name}：登记项缺少 basis 裁定依据")
            continue
        ok, why = valid_basis(root, basis, name)
        if not ok:
            errors.append(f"{name}：basis 不合格：{why}")

    try:
        registry = load_registry(root)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[错误] 无法解析 {REGISTRY}：{exc}")
        return 2
    for name, entry in sorted(entries.items()):
        if entry.get("basis") == DECLARATION and name not in registry:
            errors.append(
                f"{name}：无复核声明未在 {REGISTRY} 登记"
                "（须含缺哪份复核、到期里程碑、责任人）"
            )
    for name, info in sorted(registry.items()):
        if name not in entries:
            errors.append(f"{REGISTRY}：登记项 {name} 不是受保护对象")
            continue
        if entries[name].get("basis") != DECLARATION:
            errors.append(f"{REGISTRY}：{name} 已有复核记录，应删除该例外登记")
        if not isinstance(info, dict):
            errors.append(f"{REGISTRY}：{name} 的登记项必须是对象")
            continue
        missing = [field for field in REGISTRY_FIELDS if not info.get(field)]
        if missing:
            errors.append(f"{REGISTRY}：{name} 缺少字段 {', '.join(missing)}")

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
