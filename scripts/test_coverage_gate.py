#!/usr/bin/env python3
"""覆盖闸门负例测试：可重复执行，证明四类“改样例”动作都会被阻断。

N01 删除某子句唯一负例（从矩阵移除 negative 条目）→ 必须 “缺少负例”；
N02 把负例期望 verdict 改成 pass → 必须识别“负例被改成正例”；
N03 删除负例样例块本身 → 必须识别“负例不存在”；
N04 把 G-B1#2 的负例输入换成只触发 G-B1#1 的用例 → 必须按子句级取证拦住。

只读工作区，变异副本写入临时目录。
用法：python3 scripts/test_coverage_gate.py [--root DIR]
退出码：0 = 四条负例全部被阻断；1 = 至少一条未被阻断；2 = 基线或结构异常。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

METHOD = Path("spec/methods/deterministic-checker.md")
MANIFEST = Path("validation/checker-prototype/coverage.json")
GATE = Path("scripts/check_coverage_gate.py")

NEGATIVE_SAMPLE = "A.1.14-1"
CLAUSE = "G-F4#1"
FIND = """check_id: SCHEDULE_EVIDENCE_LINK
source_rule: G-F4
severity: advisory
rule_status: assumption
verdict: fail
reason: missing_schedule_evidence"""
REPLACE = FIND.replace("verdict: fail", "verdict: pass")
BLOCK_START = "**样例 1（触发 → `fail`）**：带截止日期的时间承诺没有依据断言。"
BLOCK_END = "reason: missing_schedule_evidence\n```\n"
B1_NEGATIVE_INPUT = """management_items:
  - { id: "M-1", process_group: "managing-delivery", subject_group: "planning" }
  - { id: "M-2", process_group: "closing" }"""
B1_OTHER_INPUT = """management_items:
  - { id: "M-1", process_group: "managing-delivery", subject_group: "planning" }
  - { id: "M-2", subject_group: "closing" }"""


def run_gate(root: Path, method: Path, manifest: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(root / GATE),
            "--root",
            str(root),
            "--method",
            str(method),
            "--manifest",
            str(manifest),
        ],
        capture_output=True,
        text=True,
    )


def evidence(output: str, expected: str) -> str:
    hits = [line.strip() for line in output.splitlines() if expected in line]
    return "；".join(hits[:2]) if hits else f"（未命中：{expected}）"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="仓库根目录；默认由脚本位置推断")
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    original_method = (root / METHOD).read_text(encoding="utf-8")
    original_manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))

    baseline = run_gate(root, root / METHOD, root / MANIFEST)
    if baseline.returncode != 0:
        print("[错误] 覆盖闸门基线未通过，负例测试无意义。")
        print(baseline.stdout)
        return 2

    rows: list[tuple[str, str, str, str, str]] = []
    failures = 0
    with tempfile.TemporaryDirectory(prefix="pm-coverage-") as tmp:
        tmpdir = Path(tmp)

        # N01：从矩阵删除该子句唯一的负例登记。
        manifest = json.loads(json.dumps(original_manifest))
        manifest["clauses"][CLAUSE]["negative"] = []
        manifest_path = tmpdir / "manifest-missing-negative.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        result = run_gate(root, root / METHOD, manifest_path)
        expected = f"{CLAUSE}：缺少负例"
        blocked = result.returncode == 1 and expected in result.stdout
        failures += 0 if blocked else 1
        rows.append(
            ("N01", "删除子句唯一负例登记", "阻断" if blocked else "未阻断",
             str(result.returncode), evidence(result.stdout, expected))
        )

        # N02：把负例期望 verdict 改成 pass。
        if original_method.count(FIND) != 1:
            rows.append(("N02", "负例期望改成 pass", "未执行", "-", "变异锚点不唯一"))
            failures += 1
        else:
            method_path = tmpdir / "method-negative-pass.md"
            method_path.write_text(
                original_method.replace(FIND, REPLACE), encoding="utf-8"
            )
            result = run_gate(root, method_path, root / MANIFEST)
            expected = f"{CLAUSE}：负例 {NEGATIVE_SAMPLE} 期望 verdict=pass"
            blocked = result.returncode == 1 and expected in result.stdout
            failures += 0 if blocked else 1
            rows.append(
                ("N02", "负例期望改成 pass", "阻断" if blocked else "未阻断",
                 str(result.returncode), evidence(result.stdout, expected))
            )

        # N03：删除负例样例块本身。
        start = original_method.find(BLOCK_START)
        end = original_method.find(BLOCK_END, start)
        if start == -1 or end == -1:
            rows.append(("N03", "删除负例样例块", "未执行", "-", "变异锚点缺失"))
            failures += 1
        else:
            end += len(BLOCK_END)
            method_path = tmpdir / "method-negative-deleted.md"
            method_path.write_text(
                original_method[:start] + original_method[end:], encoding="utf-8"
            )
            result = run_gate(root, method_path, root / MANIFEST)
            # 删除首个样例后，后续样例按位置重编号；阻断证据可能是“不存在”、
            # “负例被改成正例”，或块数不再成对（原型拒绝解析）。
            combined = result.stdout + result.stderr
            candidates = [
                f"{CLAUSE}：负例 {NEGATIVE_SAMPLE} 不存在",
                f"{CLAUSE}：负例 {NEGATIVE_SAMPLE} 期望 verdict=pass",
                "YAML 块应为",
            ]
            hit = next((item for item in candidates if item in combined), None)
            blocked = result.returncode == 1 and hit is not None
            failures += 0 if blocked else 1
            rows.append(
                ("N03", "删除负例样例块", "阻断" if blocked else "未阻断",
                 str(result.returncode), evidence(combined, hit) if hit else "（无预期证据）")
            )

        # N04：把 G-B1#2 的负例输入换成只触发 G-B1#1 的用例（期望输出不变）。
        if original_method.count(B1_NEGATIVE_INPUT) != 1:
            rows.append(("N04", "B1#2 负例换成 B1#1 用例", "未执行", "-", "变异锚点不唯一"))
            failures += 1
        else:
            method_path = tmpdir / "method-b1-clause-swap.md"
            method_path.write_text(
                original_method.replace(B1_NEGATIVE_INPUT, B1_OTHER_INPUT), encoding="utf-8"
            )
            result = run_gate(root, method_path, root / MANIFEST)
            expected = "G-B1#2：负例 A.1.6-1 实际触发 ['G-B1#1']，未触发声明的 G-B1#2"
            blocked = result.returncode == 1 and expected in result.stdout
            failures += 0 if blocked else 1
            rows.append(
                ("N04", "B1#2 负例换成 B1#1 用例", "阻断" if blocked else "未阻断",
                 str(result.returncode), evidence(result.stdout, expected))
            )

    print("| 编号 | 负例动作 | 预期 | 实际退出码 | 证据 |")
    print("|---|---|---|---|---|")
    for row in rows:
        print("| " + " | ".join(row) + " |")
    print()
    print(f"负例集 {len(rows)} 条，阻断 {len(rows) - failures} 条，未阻断 {failures} 条。")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
