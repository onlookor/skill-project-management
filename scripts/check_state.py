#!/usr/bin/env python3
"""以 git ls-files 为准核对 STATE.md：漏登、登了不存在的文件、状态值非法均报错。

用法：python3 scripts/check_state.py
退出码：0 = 通过；1 = 存在错误；2 = STATE.md 结构无法解析。
"""

import re
import subprocess
import sys
from pathlib import Path

STATE_FILE = "STATE.md"

STATE_ENTRY_RE = re.compile(r"^-\s+`([a-z_]+)`：")
TABLE_ROW_RE = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*`([^`]+)`")


def repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("[错误] 当前目录不在 git 仓库中，无法对账。")
        sys.exit(2)
    return Path(result.stdout.strip())


def tracked_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, capture_output=True, text=True
    )
    if result.returncode != 0:
        print("[错误] git ls-files 执行失败。")
        sys.exit(2)
    return [p for p in result.stdout.split("\0") if p]


def parse_state(text: str):
    allowed: list[str] = []
    defaults: list[tuple[str, str]] = []
    exceptions: list[tuple[str, str]] = []
    section = None

    for line in text.splitlines():
        if line.startswith("**状态取值**"):
            section = "allowed"
            continue
        if line.startswith("## 目录默认值"):
            section = "defaults"
            continue
        if line.startswith("## 例外"):
            section = "exceptions"
            continue
        if line.startswith("## "):
            section = None
            continue

        if section == "allowed":
            match = STATE_ENTRY_RE.match(line)
            if match:
                allowed.append(match.group(1))
        elif section in ("defaults", "exceptions"):
            match = TABLE_ROW_RE.match(line)
            if match:
                target = (defaults if section == "defaults" else exceptions)
                target.append((match.group(1), match.group(2)))
    return allowed, defaults, exceptions


def resolve(path: str, defaults: list[tuple[str, str]]):
    matches = []
    for prefix, status in defaults:
        if prefix == "./":
            if "/" not in path:
                matches.append((0, status))
        elif path.startswith(prefix):
            matches.append((len(prefix), status))
    if not matches:
        return None
    return max(matches, key=lambda item: item[0])[1]


def main() -> int:
    root = repo_root()
    state_path = root / STATE_FILE
    if not state_path.is_file():
        print(f"[错误] 未找到 {STATE_FILE}。")
        return 2

    allowed, defaults, exceptions = parse_state(state_path.read_text(encoding="utf-8"))
    if not allowed or not defaults:
        print(f"[错误] {STATE_FILE} 缺少“状态取值”或“目录默认值”，无法解析。")
        return 2

    errors: list[str] = []
    files = tracked_files(root)
    exception_map: dict[str, str] = {}

    for path, status in exceptions:
        if path in exception_map:
            errors.append(f"[错误] 例外表重复登记：{path}")
        exception_map[path] = status
        if status not in allowed:
            errors.append(f"[错误] 状态值非法：例外 {path} -> `{status}`")
        if path not in files:
            errors.append(f"[错误] 登了不存在的文件：{path}（未被 git 跟踪）")

    for prefix, status in defaults:
        if status not in allowed:
            errors.append(f"[错误] 状态值非法：默认值 `{prefix}` -> `{status}`")

    unresolved = []
    for path in files:
        status = exception_map.get(path) or resolve(path, defaults)
        if status is None:
            unresolved.append(path)
        elif status not in allowed:
            errors.append(f"[错误] 状态值非法：{path} -> `{status}`")

    for path in unresolved:
        errors.append(f"[错误] 漏登：{path}（无匹配的目录默认值，且不在例外表）")

    print(
        f"STATE 对账：{len(files)} 个跟踪文件，"
        f"{len(defaults)} 条目录默认值，{len(exceptions)} 条例外，"
        f"状态取值 {len(allowed)} 个"
    )
    if errors:
        for item in errors:
            print(item)
        print(f"[失败] {len(errors)} 项错误。")
        return 1

    print("[通过] 全部跟踪文件均有合法状态，例外表无悬空条目。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
