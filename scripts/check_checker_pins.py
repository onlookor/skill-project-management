#!/usr/bin/env python3
"""检查器绑定：受保护脚本的哈希必须与 registry 登记一致。

受保护对象包括：
  - scripts/ 下全部检查器脚本（含 check_checker_pins.py 自身，不再自排除）；
  - .githooks/pre-commit（钩子本身就是验证链的一环）；
  - validation/checker-prototype/checker.py（验收用原型）。

改动任何一个都必须 `--write --basis "<非同源复核记录>"` 更新登记。basis 不是自由文本：
必须含 `非同源复核：`、`复核产物：<仓库外存在的文件>`、`sha256：<64 位>`、
`复核基线：<仓库内存在的提交>`、唯一一条 `区段：<所绑对象>` 与结论词，否则拒绝写入。
**默认读取模式同样校验这些字段**，只改 basis 文本（例如把“未审查本批”改成“结论：认可”）
会被阻断。“无复核声明”只对代码内冻结的 `UNREVIEWED_KEYS` 成立：历史基文必须**逐字**
相等，本批改动必须是结构化 `待复核：批次 NNNN …；无复核声明，不构成认可`；
`初始登记：<任意>` 之类前缀文本一律拒绝。`--write` 不接受冻结的历史基文，
只接受复核记录或结构化待复核声明，防止用旧状态覆盖新改动。

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
CHECKER_GLOBS = ("check_*.py", "test_*.py", "validate_*.py")
EXTRA_PATHS = (".githooks/pre-commit", "validation/checker-prototype/checker.py")
SNAPSHOT = Path("validation/pinned/checker.py")
SOURCE = Path("validation/checker-prototype/checker.py")
CONCLUSIONS = ("实质收敛", "认可", "通过")
# 结构化“待复核”声明：批次号 + 说明 + 固定否定尾句。只有白名单对象可用。
PENDING_RE = re.compile(r"^待复核：批次 \d{4} [^；]+；无复核声明，不构成认可$")
# 冻结白名单：对象 → 唯一允许的**历史**“无复核声明”文本（逐字匹配）。
# 值为 None 表示该对象只允许结构化 `待复核：批次 NNNN …`。
# 不做前缀判定：`初始登记：<任意>`、`无复核声明：<任意>` 一律无效。
_FROZEN_D8BF413 = (
    "无复核声明：历史指针——原依据：基线 d8bf413 复核清单第 1 项"
    "（根检查器与 pre-commit 纳入保护、basis 强度）；"
    "历史指针（仓内转录件）：validation/reviews/2026-11-14-d8bf413-review.md；"
    "复核基线：d8bf413；非权威，不构成认可"
)
UNREVIEWED_KEYS: dict[str, str | None] = {
    "scripts/check_anchors.py": (
        "无复核声明：历史指针——原依据：用户裁定（parent session "
        "6af45947fead009e7bdd1e76，批次 0048），2026-11-14；区段：GRAMMAR.md；"
        "历史指针（仓内转录件）：validation/reviews/2026-11-14-t139-user-adjudication.md；"
        "复核基线：563c26c；非权威，不构成认可"
    ),
    "scripts/check_gap_ledger.py": (
        "无复核声明：历史指针——原依据：外部复核基线 48128a8，产物 "
        "/tmp/verify-4812/REPORT_48128a8.md；"
        "历史指针（仓内转录件）：validation/reviews/2026-11-14-48128a8-external.md；"
        "复核基线：48128a8；非权威，不构成认可"
    ),
    "scripts/check_glossary_usage.py": _FROZEN_D8BF413,
    "scripts/check_ledger_landings.py": _FROZEN_D8BF413,
    "scripts/check_state.py": _FROZEN_D8BF413,
    "scripts/check_three_table.py": _FROZEN_D8BF413,
    "scripts/check_checker_pins.py": None,
    "scripts/check_spec_pins.py": None,
    "scripts/test_checker_pins.py": None,
    "scripts/test_spec_pins.py": None,
    "scripts/check_dependency_pins.py": None,
    "scripts/test_dependency_pins.py": None,
    "scripts/validate_ontology.py": None,
}


def unreviewed_ok(text: str, key: str) -> bool:
    """白名单内：逐字等于冻结基文，或符合结构化“待复核”声明；其余一律不放行。"""
    if key not in UNREVIEWED_KEYS:
        return False
    if PENDING_RE.match(text) is not None:
        return True
    return UNREVIEWED_KEYS[key] == text


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


def valid_basis(root: Path, text: str, key: str, allow_unreviewed=None) -> tuple[bool, str]:
    """默认模式与 --write 共用：basis 必须指向仓库外产物、sha256 一致且区段正确。

    “无复核声明”只对 `UNREVIEWED_KEYS` 白名单内的对象成立，且必须逐字等于冻结基文
    或符合结构化“待复核”声明；不再按 `初始登记：` 前缀放行。
    """
    text = text.strip()
    if allow_unreviewed is None:
        allow_unreviewed = key in UNREVIEWED_KEYS
    if allow_unreviewed and unreviewed_ok(text, key):
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
    baseline = re.search(r"复核基线：`?([0-9a-f]{7,40})`?", text)
    if baseline is None:
        return False, "缺少 `复核基线：<提交号>`"
    exists = subprocess.run(
        ["git", "cat-file", "-e", f"{baseline.group(1)}^{{commit}}"],
        cwd=root,
        capture_output=True,
    )
    if exists.returncode != 0:
        return False, f"复核基线不存在：{baseline.group(1)}"
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
    if re.search(rf"结论：\s*(?:{'|'.join(CONCLUSIONS)})(?=$|[\s；;，,。）（()])", text) is None:
        return False, f"缺少结论词（{'/'.join(CONCLUSIONS)}）"
    return True, ""


def writable(root: Path, text: str, key: str) -> tuple[bool, str]:
    """`--write` 的放行口径：合格复核记录，或白名单对象的**结构化**待复核声明。

    冻结的历史“无复核声明”文本不得用来覆盖新改动——那是旧状态，不是新授权。
    """
    if key in UNREVIEWED_KEYS and PENDING_RE.match(text.strip()) is not None:
        return True, ""
    return valid_basis(root, text, key, allow_unreviewed=False)


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
        basis = entry.get("basis")
        if not basis:
            errors.append(f"{name}：登记项缺少 basis 裁定依据")
            continue
        ok, why = valid_basis(root, basis, name)
        if not ok:
            errors.append(f"{name}：basis 不合格：{why}")

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
