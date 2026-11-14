#!/usr/bin/env python3
"""A.2 变异测试：固定变异集 + 可重复执行。

对 methods/deterministic-checker.md 的 A.2 子句表逐条施加语义变异，调用
`scripts/check_three_table.py --method <变异副本>`，要求每一处变异都被检查器
抓到（退出码 1），且证据命中预期机制。

变异集是固定的（见 MUTATIONS）；脚本只读原文件，变异副本写入临时目录，不改
工作区。重复执行结论一致。

用法：python3 scripts/test_check_table_mutations.py [--root DIR]
退出码：0 = 全部变异被抓到；1 = 至少一条未抓到；2 = 基线或结构异常。
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

METHOD = Path("spec/methods/deterministic-checker.md")

# (编号, 类别, 变异说明, 原文片段, 替换为, 预期证据)
MUTATIONS: list[tuple[str, str, str, str, str, str]] = [
    (
        "M01",
        "子句语义",
        "G-C1#1 改成“必须有 Actor 负责人”",
        "| `G-C1#1` | G-C1 | 每个 `Deliverable` 至少一条见证断言（`asserted_by` 正向或 `about` 反向） |",
        "| `G-C1#1` | G-C1 | 必须有 `Actor` 负责人 |",
        "DELIVERABLE_ASSERTION_LINK 的子句指纹",
    ),
    (
        "M02",
        "量词",
        "G-A1#1 的“至少一个”改为“恰好一个”",
        "| `G-A1#1` | G-A1 | 至少一个 `Actor` |",
        "| `G-A1#1` | G-A1 | 恰好一个 `Actor` |",
        "PROJECT_MINIMAL_EXISTENCE 的子句指纹",
    ),
    (
        "M03",
        "原因码删除",
        "G-E1#1 删除原因码 `multiple_accountable`",
        "| `G-E1#1` | G-E1 | 唯一 `accountable_by` 且指向 `HumanActor`/`LegalEntity` | `missing_accountable / multiple_accountable / unknown_accountable / accountable_not_human` |",
        "| `G-E1#1` | G-E1 | 唯一 `accountable_by` 且指向 `HumanActor`/`LegalEntity` | `missing_accountable / unknown_accountable / accountable_not_human` |",
        "ROLE_MINIMAL_COMPLETENESS 的子句指纹",
    ),
    (
        "M04",
        "枚举归属",
        "把枚举条件写进 G-B1#2（应由 G-B2#1 承接）",
        "| `G-B1#2` | G-B1 | 每个管理项有 `subject_group` 标签 |",
        "| `G-B1#2` | G-B1 | 每个管理项有 `subject_group` 标签且在枚举内 |",
        "枚举归属 G-B2",
    ),
    (
        "M05",
        "枚举归属",
        "从 G-B2#1 删除枚举条件",
        "| `G-B2#1` | G-B2 | 标签值在锚定枚举或契约扩展内 |",
        "| `G-B2#1` | G-B2 | 标签值在锚定集合或契约扩展内 |",
        "G-B2#1 未写枚举条件",
    ),
    (
        "M06",
        "承接规则",
        "把 G-C1#1 的承接 check_id 改指向 CHANGE_CONSTRAINT_LINK",
        "| `G-C1#1` | G-C1 | 每个 `Deliverable` 至少一条见证断言（`asserted_by` 正向或 `about` 反向） | `deliverable_without_assertion / dangling_reference` | `DELIVERABLE_ASSERTION_LINK` |",
        "| `G-C1#1` | G-C1 | 每个 `Deliverable` 至少一条见证断言（`asserted_by` 正向或 `about` 反向） | `deliverable_without_assertion / dangling_reference` | `CHANGE_CONSTRAINT_LINK` |",
        "CHANGE_CONSTRAINT_LINK 的规则列",
    ),
    (
        "M07",
        "子句 id",
        "把 G-C1#1 的子句 id 改为 G-D1#4（指向别的规则）",
        "| `G-C1#1` | G-C1 |",
        "| `G-D1#4` | G-C1 |",
        "DELIVERABLE_ASSERTION_LINK 的子句 id 列",
    ),
    (
        "M08",
        "severity",
        "把 G-E1#3 的子句 severity 由 warn 改为 block",
        "| `G-E1#3` | G-E1 | 角色重合时有 `role_merge_declaration` | `missing_role_merge_declaration` | `ROLE_MINIMAL_COMPLETENESS` | `warn` |",
        "| `G-E1#3` | G-E1 | 角色重合时有 `role_merge_declaration` | `missing_role_merge_declaration` | `ROLE_MINIMAL_COMPLETENESS` | `block` |",
        "ROLE_MINIMAL_COMPLETENESS 的子句指纹",
    ),
    (
        "M09",
        "规则状态",
        "把 G-B1#2 的规则状态由 active 改为 assumption",
        "| `G-B1#2` | G-B1 | 每个管理项有 `subject_group` 标签 | `missing_dimension` | `DUAL_DIMENSION_ANNOTATION` | `advisory` | checked | active |",
        "| `G-B1#2` | G-B1 | 每个管理项有 `subject_group` 标签 | `missing_dimension` | `DUAL_DIMENSION_ANNOTATION` | `advisory` | checked | assumption |",
        "DUAL_DIMENSION_ANNOTATION 的子句指纹",
    ),
    (
        "M10",
        "子句删除",
        "删除 G-E1#3 整行",
        "| `G-E1#3` | G-E1 | 角色重合时有 `role_merge_declaration` | `missing_role_merge_declaration` | `ROLE_MINIMAL_COMPLETENESS` | `warn` | checked | active |\n",
        "",
        "ROLE_MINIMAL_COMPLETENESS 的子句 id 列",
    ),
    (
        "M11",
        "原因码篡改",
        "把 G-D1#3 的原因码改为未定义的 `invalid_relation`",
        "| `G-D1#3` | G-D1 | 边类型 ∈ `relation` 枚举 | `invalid_change_relation` |",
        "| `G-D1#3` | G-D1 | 边类型 ∈ `relation` 枚举 | `invalid_relation` |",
        "CHANGE_CONSTRAINT_LINK 的子句指纹",
    ),
]


def repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print("[错误] 当前目录不在 git 仓库中，无法定位方法文件。")
        sys.exit(2)
    return Path(result.stdout.strip())


def run_checker(root: Path, method: Path, write: bool = False) -> subprocess.CompletedProcess:
    command = [
        sys.executable,
        str(root / "scripts/check_three_table.py"),
        "--root",
        str(root),
        "--method",
        str(method),
    ]
    if write:
        command.append("--write")
    return subprocess.run(command, capture_output=True, text=True)


def evidence(output: str, expected: str) -> str:
    """挑出含预期证据的错误行，最多两行。"""
    hits = [
        line.strip()
        for line in output.splitlines()
        if line.startswith("[错误]") and expected in line
    ]
    if hits:
        return "；".join(hits[:2])
    if expected in output:
        return next(line.strip() for line in output.splitlines() if expected in line)
    fallback = [line.strip() for line in output.splitlines() if line.startswith("[错误]")]
    return "；".join(fallback[:2]) if fallback else "（无错误输出）"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="仓库根目录；默认由 git 推断")
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else repo_root()
    source = root / METHOD
    original = source.read_text(encoding="utf-8")

    baseline = run_checker(root, source)
    if baseline.returncode != 0:
        print("[错误] 基线未通过，变异测试无意义。")
        print(baseline.stdout)
        return 2

    rows: list[tuple[str, str, str, str, str, str]] = []
    failures = 0
    with tempfile.TemporaryDirectory(prefix="pm-mutation-") as tmp:
        for mutation_id, category, description, find, replace, expected in MUTATIONS:
            occurrences = original.count(find)
            if occurrences != 1:
                rows.append(
                    (
                        mutation_id,
                        category,
                        description,
                        "变异锚点不唯一",
                        "-",
                        f"原文片段出现 {occurrences} 次，期望 1 次",
                    )
                )
                failures += 1
                continue
            mutated = original.replace(find, replace)
            target = Path(tmp) / f"{mutation_id}.md"
            target.write_text(mutated, encoding="utf-8")
            result = run_checker(root, target)
            caught = result.returncode == 1 and expected in result.stdout
            if not caught:
                failures += 1
            rows.append(
                (
                    mutation_id,
                    category,
                    description,
                    "是" if caught else "否",
                    str(result.returncode),
                    evidence(result.stdout, expected)
                    if caught
                    else evidence(result.stdout, expected)
                    + f"（预期证据缺失：{expected}）",
                )
            )

    print("| 编号 | 类别 | 变异内容 | 抓到 | 退出码 | 证据 |")
    print("|---|---|---|---|---|---|")
    for row in rows:
        print("| " + " | ".join(row) + " |")
    print()
    print(f"变异集 {len(MUTATIONS)} 条，抓到 {len(MUTATIONS) - failures} 条，未抓到 {failures} 条。")

    # A.2 签收纪律正负例（AGENTS 3.6.7）：只改 A.2 + --write 必须被拦；更新签收后必须通过。
    signoff_failures = 0
    signoff_rows: list[tuple[str, str, str, str, str, str]] = []
    with tempfile.TemporaryDirectory(prefix="pm-signoff-") as tmp:
        anchor = "| `G-A1#1` | G-A1 | 至少一个 `Actor` |"
        replacement = "| `G-A1#1` | G-A1 | 至少有一个 `Actor` |"
        if original.count(anchor) != 1:
            signoff_rows.append(("S01", "只改 A.2 + --write，不更新签收", "阻断", "未执行", "-", "变异锚点不唯一"))
            signoff_rows.append(("S02", "改 A.2 并更新签收", "通过", "未执行", "-", "变异锚点不唯一"))
            signoff_failures = 2
        else:
            mutated = original.replace(anchor, replacement)
            target = Path(tmp) / "signoff.md"
            target.write_text(mutated, encoding="utf-8")
            write_result = run_checker(root, target, write=True)
            if write_result.returncode != 0:
                signoff_rows.append(("S01", "只改 A.2 + --write，不更新签收", "阻断", "未执行", str(write_result.returncode), "A 表重建失败"))
                signoff_rows.append(("S02", "改 A.2 并更新签收", "通过", "未执行", "-", "A 表重建失败"))
                signoff_failures = 2
            else:
                negative = run_checker(root, target)
                negative_ok = (
                    negative.returncode == 1
                    and "A.2 已改动但复核签收未同步" in negative.stdout
                )
                signoff_failures += 0 if negative_ok else 1
                signoff_rows.append(
                    (
                        "S01",
                        "只改 A.2 + --write，不更新签收",
                        "阻断",
                        "阻断" if negative_ok else "未阻断",
                        str(negative.returncode),
                        evidence(negative.stdout, "A.2 已改动但复核签收未同步"),
                    )
                )
                match = re.search(r"当前 A\.2 指纹 `([0-9a-f]{12})`", negative.stdout)
                if match is None:
                    signoff_rows.append(("S02", "改 A.2 并更新签收", "通过", "未执行", "-", "未取得新 A.2 指纹"))
                    signoff_failures += 1
                else:
                    after_write = target.read_text(encoding="utf-8")
                    updated = re.sub(
                        r"复核签收：[^\n]*",
                        f"复核签收：测试复核者 / 2026-11-14 / A.2 指纹 `{match.group(1)}`",
                        after_write,
                    )
                    target.write_text(updated, encoding="utf-8")
                    positive = run_checker(root, target)
                    positive_ok = positive.returncode == 0
                    signoff_failures += 0 if positive_ok else 1
                    signoff_rows.append(
                        (
                            "S02",
                            "改 A.2 并更新签收",
                            "通过",
                            "通过" if positive_ok else "未通过",
                            str(positive.returncode),
                            evidence(positive.stdout, "[通过]"),
                        )
                    )

    print("| 编号 | 场景 | 预期 | 实际 | 退出码 | 证据 |")
    print("|---|---|---|---|---|---|")
    for row in signoff_rows:
        print("| " + " | ".join(row) + " |")
    print()
    print(f"A.2 签收正负例 2 条，符合预期 {2 - signoff_failures} 条。")
    if failures or signoff_failures:
        print("[失败] 存在未被检查器抓到或不符合预期的用例，第三层不通过。")
        return 1
    print("[通过] 全部变异被检查器抓到；A.2 签收正负例符合预期；脚本可重复执行。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
