#!/usr/bin/env python3
"""核查 GAP_LEDGER.md 的结构、覆盖、到期与 TODO 交叉引用。

用法：python3 scripts/check_gap_ledger.py [--staged] [--root DIR]
退出码：0 = 通过；1 = 存在错误（含到期未裁定）；2 = 结构无法解析。
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

LEDGER = "GAP_LEDGER.md"
METHOD = "spec/methods/deterministic-checker.md"
TODO = "TODO.md"

LEVEL_MAX = {"L1": 1, "L2": 2, "L3": 2}
CAUSES = {"undefined-object", "rule-stricter", "severity-mismatch"}
STATUSES = {"open", "closed"}
RESOLUTIONS = {"rule-change", "check-change", "doc-only", "accepted"}

MILESTONE_RE = re.compile(r"^M([0-7])$")
GAP_ID_RE = re.compile(r"^G-\d{3}$")
TODO_ID_RE = re.compile(r"^T-\d{3}$")


def repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("[错误] 当前目录不在 git 仓库中，无法核查缺口台账。")
        sys.exit(2)
    return Path(result.stdout.strip())


def split_row(line: str):
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def parse_ledger(text: str):
    match = re.search(r"\*\*当前里程碑\*\*：\s*(M[0-7])", text)
    current = match.group(1) if match else None

    audit = {}
    gaps = {}
    for line in text.splitlines():
        cells = split_row(line)
        if not cells:
            continue
        first = cells[0].strip("`")
        if first in ("编号", "check_id"):
            continue
        if len(cells) == 11 and GAP_ID_RE.match(first):
            gaps[first] = {
                "status": cells[1],
                "cause": cells[2],
                "level": cells[3],
                "impact": cells[4],
                "blocking": cells[5],
                "owner": cells[6],
                "registered": cells[7],
                "resolution": cells[8],
                "todo": cells[9],
                "description": cells[10],
            }
        elif len(cells) == 4 and re.fullmatch(r"[A-Z_]+", first):
            audit[first] = {"conclusion": cells[2], "reviewed": cells[3]}
    return current, audit, gaps


def parse_checks(text: str):
    checks = {}
    for line in text.splitlines():
        cells = split_row(line)
        if cells and len(cells) >= 5 and cells[0].startswith("`"):
            check_id = cells[0].strip("`")
            if re.fullmatch(r"[A-Z_]+", check_id) and re.fullmatch(r"G-[A-G]\d", cells[1]):
                checks[check_id] = cells[1]
    return checks


def parse_todo_gap_items(text: str):
    items = set()
    for line in text.splitlines():
        cells = split_row(line)
        if cells and len(cells) >= 3 and TODO_ID_RE.match(cells[0]):
            if cells[2] == "判定口径裁定":
                items.add(cells[0])
    return items


def milestone_number(value: str):
    match = MILESTONE_RE.match(value)
    return int(match.group(1)) if match else None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true", help="检查暂存区是否同步更新台账")
    parser.add_argument("--root", help="仓库根目录；默认由 git 推断")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else repo_root()
    ledger_text = read(root / LEDGER)
    method_text = read(root / METHOD)
    todo_text = read(root / TODO)
    if not ledger_text or not method_text:
        print("[错误] 无法读取 GAP_LEDGER.md 或方法注册表，结构无法解析。")
        return 2

    current, audit, gaps = parse_ledger(ledger_text)
    checks = parse_checks(method_text)
    todo_items = parse_todo_gap_items(todo_text)

    errors: list[str] = []
    if current is None:
        errors.append("[错误] GAP_LEDGER.md 缺少 `**当前里程碑**：M#` 头部")
    if not checks:
        errors.append("[错误] 未能从方法注册表解析出任何 check_id")

    # 覆盖矩阵：A 表 check_id 与核查矩阵必须一一对应。
    if set(audit) != set(checks):
        missing = sorted(set(checks) - set(audit))
        extra = sorted(set(audit) - set(checks))
        if missing:
            errors.append(f"[错误] 核查矩阵缺少 check_id：{', '.join(missing)}")
        if extra:
            errors.append(f"[错误] 核查矩阵含注册表外的 check_id：{', '.join(extra)}")
    for check_id, rule in checks.items():
        row = audit.get(check_id)
        if row and row["conclusion"] not in ("`consistent`", "consistent"):
            for token in re.findall(r"G-\d{3}", row["conclusion"]):
                if token not in gaps:
                    errors.append(f"[错误] {check_id} 引用了不存在的缺口 {token}")

    # 缺口字段与状态机。
    referenced = set()
    for row in audit.values():
        referenced.update(re.findall(r"G-\d{3}", row["conclusion"]))
    for gap_id, gap in gaps.items():
        if gap["cause"] not in CAUSES:
            errors.append(f"[错误] {gap_id} 的成因 `{gap['cause']}` 非法")
        if gap["level"] not in LEVEL_MAX:
            errors.append(f"[错误] {gap_id} 的等级 `{gap['level']}` 非法")
        if gap["status"] not in STATUSES:
            errors.append(f"[错误] {gap_id} 的状态 `{gap['status']}` 非法")
        if milestone_number(gap["registered"]) is None:
            errors.append(f"[错误] {gap_id} 的登记里程碑 `{gap['registered']}` 非法")
        for field in ("impact", "blocking", "owner", "description"):
            if not gap[field]:
                errors.append(f"[错误] {gap_id} 的 `{field}` 为空")
        if gap["status"] == "closed":
            if gap["resolution"] not in RESOLUTIONS:
                errors.append(f"[错误] {gap_id} 已关闭但处置出口 `{gap['resolution']}` 非法")
            if gap["resolution"] == "accepted" and "理由" not in gap["description"]:
                errors.append(f"[错误] {gap_id} 选择 accepted 但说明未写“理由：”")
            if gap["resolution"] == "doc-only" and "不检查" not in gap["description"]:
                errors.append(f"[错误] {gap_id} 选择 doc-only 但说明未注明“不检查”")
        elif gap["resolution"]:
            errors.append(f"[错误] {gap_id} 仍为 open，但已填写处置出口")

        for token in re.findall(r"T-\d{3}", gap["todo"]):
            if not re.search(rf"\|\s*{token}\s*\|", todo_text):
                errors.append(f"[错误] {gap_id} 关联的 {token} 不存在于 TODO.md")

    for gap_id, gap in gaps.items():
        # 只有 open 缺口必须被核查矩阵锚定；closed 缺口已记录处置出口，
        # 再强制锚定会使其永远无法让矩阵达到 17/17 consistent（撤除条件）。
        if gap["status"] == "open" and gap_id not in referenced:
            errors.append(f"[错误] {gap_id} 未被任何影响面或核查矩阵引用")

    tracked_todo = set()
    for gap in gaps.values():
        tracked_todo.update(re.findall(r"T-\d{3}", gap["todo"]))
    for item in sorted(todo_items - tracked_todo):
        errors.append(f"[错误] TODO.md 的判定口径裁定项 {item} 未进入缺口台账")

    # 到期计算。
    overdue = []
    if current is not None:
        current_num = milestone_number(current)
        for gap_id, gap in gaps.items():
            if gap["status"] != "open" or gap["level"] not in LEVEL_MAX:
                continue
            registered = milestone_number(gap["registered"])
            if registered is None:
                continue
            due = min(registered + LEVEL_MAX[gap["level"]], 7)
            if current_num >= due:
                overdue.append(gap_id)
                errors.append(
                    f"[错误] {gap_id} 已到期未裁定（登记 {gap['registered']}，"
                    f"{gap['level']} 上限 {LEVEL_MAX[gap['level']]}，到期 M{due}，当前 {current}）"
                )

    # 暂存同步：规则或判定列变更必须同批更新台账。
    if args.staged:
        staged = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=root,
            capture_output=True,
            text=True,
        )
        names = set(staged.stdout.split())
        if ("GRAMMAR.md" in names or METHOD in names) and LEDGER not in names:
            errors.append(
                "[错误] GRAMMAR.md 或方法判定列已暂存，但 GAP_LEDGER.md 未同批更新；"
                "规则/判定变更必须先过缺口复核（AGENTS.md 3.6）"
            )

    levels = {level: 0 for level in LEVEL_MAX}
    for gap in gaps.values():
        if gap["level"] in levels:
            levels[gap["level"]] += 1
    open_count = sum(1 for gap in gaps.values() if gap["status"] == "open")
    closed_count = len(gaps) - open_count
    consistent = sum(
        1 for row in audit.values() if row["conclusion"] in ("`consistent`", "consistent")
    )
    print(
        f"缺口台账核查：{len(gaps)} 条（open {open_count} / closed {closed_count}）；"
        f"L1 {levels['L1']} / L2 {levels['L2']} / L3 {levels['L3']}；"
        f"到期 {len(overdue)}；核查矩阵 {consistent}/{len(checks)} consistent。"
    )

    if errors:
        for error in errors:
            print(error)
        print(f"[失败] {len(errors)} 项错误。")
        return 1
    print("[通过] 缺口台账结构完整，无到期未裁定条目。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
