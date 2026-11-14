#!/usr/bin/env python3
"""核查 GAP_LEDGER.md 的结构、覆盖、到期与 TODO 交叉引用。

用法：python3 scripts/check_gap_ledger.py [--staged] [--root DIR]
退出码：0 = 通过；1 = 存在错误（含到期未裁定）；2 = 结构无法解析。
"""

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

LEDGER = "GAP_LEDGER.md"
METHOD = "spec/methods/deterministic-checker.md"
TODO = "TODO.md"

LEVEL_MAX = {"L1": 1, "L2": 2, "L3": 2}
CAUSES = {
    "undefined-object",
    "rule-stricter",
    "severity-mismatch",
    "representation-defect",
    "implementation-defect",
}
STATUSES = {"open", "closed"}
RESOLUTIONS = {"rule-change", "check-change", "doc-only", "accepted"}
CLOSURE_PREFIXES = ("外部复核：",)
EXTERNAL_RE = re.compile(r"^外部复核：([^；\s]+)；sha256：([0-9a-f]{64})(?:；|$)")
SAME_SOURCE_MARKERS = (
    "同源自查",
    "同源运行",
    "自家原型",
    "自家脚本",
    "样例与实现同源",
    "自查通过",
    "退出 0 即",
    "原型通过即",
)

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


def external_closure_errors(root: Path, closure: str) -> list[str]:
    """核对关闭依据的外部产物：路径存在且 sha256 一致。

    这是对“路径 + 哈希”的机械核对，不验证复核者身份，也不验证报告内容；
    哈希由复核方下一轮复核。
    """
    match = EXTERNAL_RE.match(closure.strip())
    if match is None:
        return ["关闭依据必须写成 `外部复核：<路径>；sha256：<64位小写十六进制>`"]
    path_text, expected = match.groups()
    path = Path(path_text)
    if not path.is_absolute():
        path = root / path
    if not path.exists():
        return [f"外部复核路径不存在：{path_text}"]
    if not path.is_file():
        return [f"外部复核路径不是文件：{path_text}"]
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        return [
            f"外部复核 sha256 不符：登记 {expected[:12]}…，实际 {actual[:12]}…"
        ]
    return []


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
        if len(cells) == 13 and cells[-1] == "":
            cells = cells[:12]
        if len(cells) == 12 and GAP_ID_RE.match(first):
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
                "closure": cells[11],
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


def self_test() -> int:
    """关闭依据字段的正负例：路径存在 + 哈希一致才通过。"""
    import tempfile

    with tempfile.TemporaryDirectory(prefix="pm-closure-") as tmp:
        root = Path(tmp)
        report = root / "report.md"
        report.write_text("external review report\n", encoding="utf-8")
        digest = hashlib.sha256(report.read_bytes()).hexdigest()
        cases = [
            (
                "E01",
                "路径存在、哈希一致",
                f"外部复核：{report}；sha256：{digest}",
                None,
            ),
            (
                "E02",
                "路径不存在",
                f"外部复核：{root / 'missing.md'}；sha256：{digest}",
                "路径不存在",
            ),
            (
                "E03",
                "哈希不符",
                f"外部复核：{report}；sha256：{'0' * 64}",
                "sha256 不符",
            ),
            (
                "E04",
                "伪造路径（不是文件）",
                f"外部复核：{root}；sha256：{digest}",
                "不是文件",
            ),
            (
                "E05",
                "缺少 sha256 字段",
                f"外部复核：{report}",
                "必须写成",
            ),
        ]
        print("| 编号 | 场景 | 预期 | 实际 | 证据 |")
        print("|---|---|---|---|---|")
        failures = 0
        for case_id, label, closure, expected in cases:
            errors = external_closure_errors(root, closure)
            if expected is None:
                ok = not errors
                actual = "通过" if ok else "报错"
                evidence = "无问题" if ok else errors[0]
            else:
                ok = any(expected in error for error in errors)
                actual = "报错" if errors else "未报错"
                evidence = next(
                    (error for error in errors if expected in error), "未命中预期"
                )
            failures += 0 if ok else 1
            print(
                f"| {case_id} | {label} | {'通过' if expected is None else '报错'} | "
                f"{actual} | {evidence} |"
            )
    print()
    print(f"关闭依据字段测试 {len(cases)} 条，符合预期 {len(cases) - failures} 条。")
    return 0 if not failures else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true", help="检查暂存区是否同步更新台账")
    parser.add_argument("--root", help="仓库根目录；默认由 git 推断")
    parser.add_argument("--self-test", action="store_true", help="关闭依据字段正负例")
    args = parser.parse_args()

    if args.self_test:
        return self_test()

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
            # 关闭依据必须是外部产物路径 + sha256；转录件与同源自证一律拒绝。
            closure = gap["closure"]
            if not closure:
                errors.append(
                    f"[错误] {gap_id} 已关闭但“关闭依据”为空；"
                    "必须有 `外部复核：<路径>；sha256：<64hex>`（AGENTS.md 3.6.6）"
                )
            elif not closure.startswith(CLOSURE_PREFIXES):
                errors.append(
                    f"[错误] {gap_id} 的关闭依据 `{closure}` 不是外部复核记录；"
                    "转录件、同源运行结果均不得关闭缺口"
                )
            else:
                errors.extend(
                    f"[错误] {gap_id} {problem}"
                    for problem in external_closure_errors(root, closure)
                )
            for marker in SAME_SOURCE_MARKERS:
                if marker in closure or marker in gap["description"]:
                    errors.append(
                        f"[错误] {gap_id} 的关闭依据或说明出现同源自证措辞 `{marker}`；"
                        "同源运行结果不得关闭缺口"
                    )
        elif gap["resolution"]:
            errors.append(f"[错误] {gap_id} 仍为 open，但已填写处置出口")
        elif gap["closure"]:
            errors.append(f"[错误] {gap_id} 仍为 open，但已填写关闭依据")

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
