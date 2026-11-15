#!/usr/bin/env python3
"""规格区段绑定的负例/正例测试（可重复执行，只读仓库工作区）。

SP01 改 A.2 但不更新区段指纹 → 必须阻断；
SP02 更新指纹但不附非同源复核记录 → 必须阻断；
SP03 更新指纹并附合格复核记录（依据指向仓库外产物 + sha256 + 基线）→ 必须通过；
SP04 复核记录的结论词不合格 → 必须阻断；
SP05 只改 coverage.json 的引用关系、不改 A.1 样例 → 必须按指纹阻断；
SP06 复核记录把仓库内转录件当依据 → 必须阻断（与 checker-pins 同一标准）；
SP07 `contracts/schema/` 下出现未登记的文件 → 必须阻断（自动发现）。

外部复核产物在系统临时目录中生成，不写入仓库。用法：
  python3 scripts/test_spec_pins.py [--root DIR]
退出码：0 = 七例全部符合预期；1 = 至少一例不符。
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_spec_pins import SECTIONS, evaluate, fingerprint, valid_basis  # noqa: E402

TARGET = "spec/methods/deterministic-checker.md#A.2"

RECORD = """非同源复核：独立复核者（测试）
区段：{key}
复核产物：{artifact}
sha256：{sha}
复核基线：3664b64
结论：实质收敛
"""


def pin(sha: str) -> dict:
    return {"sha256": sha, "path": "", "basis": "初始登记"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="仓库根目录；默认由脚本位置推断")
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]

    current = {spec["key"]: (root / spec["path"]).read_text(encoding="utf-8") for spec in SECTIONS}
    spec = next(item for item in SECTIONS if item["key"] == TARGET)
    pins = {
        item["key"]: pin(fingerprint(current[item["key"]], item["start"], item["end"]))
        for item in SECTIONS
    }

    mutated = dict(current)
    mutated[TARGET] = current[TARGET].replace(
        "至少一个 `Actor`", "至少一个 `HumanActor`", 1
    )
    if mutated[TARGET] == current[TARGET]:
        print("[错误] 变异锚点未命中，测试无意义。")
        return 1
    mutated_pins = dict(pins)
    mutated_pins[TARGET] = pin(fingerprint(mutated[TARGET], spec["start"], spec["end"]))

    failures = 0
    print("| 编号 | 场景 | 预期 | 实际 | 证据 |")
    print("|---|---|---|---|---|")

    def run(case_id, label, cur, head, pin_map, reviews, expected, test_root=None):
        nonlocal failures
        errors = evaluate(test_root or root, cur, head, pin_map, reviews)
        if expected is None:
            ok = not errors
            actual = "通过" if ok else "阻断"
            evidence = "；".join(errors[:1]) if errors else "无问题"
        else:
            ok = any(expected in error for error in errors)
            actual = "阻断" if errors else "通过"
            evidence = next((error for error in errors if expected in error), "未命中预期证据")
        failures += 0 if ok else 1
        print(f"| {case_id} | {label} | {'通过' if expected is None else '阻断'} | {actual} | {evidence} |")

    with tempfile.TemporaryDirectory() as tmp:
        artifact = Path(tmp) / "REPORT.md"
        artifact.write_text("外部复核产物（测试用，不写入仓库）。\n", encoding="utf-8")
        sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
        record = RECORD.format(key=TARGET, artifact=artifact, sha=sha)
        in_repo = root / "validation/reviews/2026-11-15-admission-r2-review.md"
        in_repo_sha = hashlib.sha256(in_repo.read_bytes()).hexdigest()
        in_repo_record = record.replace(str(artifact), str(in_repo)).replace(sha, in_repo_sha)

        run("SP01", "改 A.2 不更新指纹", mutated, current, pins, [], "指纹未更新")
        run("SP02", "更新指纹但不附复核记录", mutated, current, mutated_pins, [], "缺少合格的非同源复核记录")
        run("SP03", "更新指纹并附合格复核记录", mutated, current, mutated_pins, [record], None)
        run(
            "SP04",
            "复核记录结论词不合格",
            mutated,
            current,
            mutated_pins,
            [record.replace("结论：实质收敛", "结论：待定")],
            "缺少合格的非同源复核记录",
        )

        coverage_key = "validation/checker-prototype/coverage.json"
        mutated_coverage = dict(current)
        anchor = '"sample": "A.1.6-1"'
        if current[coverage_key].count(anchor) != 1:
            print("[错误] coverage.json 变异锚点不唯一，测试无意义。")
            return 1
        mutated_coverage[coverage_key] = current[coverage_key].replace(
            anchor, '"sample": "A.1.6-3"', 1
        )
        run("SP05", "只改 coverage.json 引用关系、不改样例", mutated_coverage, current, pins, [], "指纹未更新")

        run(
            "SP06",
            "把仓库内转录件当依据",
            mutated,
            current,
            mutated_pins,
            [in_repo_record],
            "缺少合格的非同源复核记录",
        )
        ok, why = valid_basis(root, in_repo_record)
        rejected = not ok and "转录件只作索引" in why
        failures += 0 if rejected else 1
        print(
            f"| SP06b | 依据指向仓库内产物 | 阻断 | {'阻断' if rejected else '通过'} | {why} |"
        )

        fake_root = Path(tmp) / "fake-root"
        (fake_root / "contracts/schema").mkdir(parents=True)
        (fake_root / "contracts/schema/extra.schema.json").write_text(
            '{"$schema": "x", "type": "object"}\n', encoding="utf-8"
        )
        run(
            "SP07",
            "contracts/schema 下出现未登记文件",
            current,
            current,
            pins,
            [record],
            "未登记为规格区段",
            test_root=fake_root,
        )

        sub_root = Path(tmp) / "fake-sub"
        (sub_root / "contracts/schema/sub").mkdir(parents=True)
        (sub_root / "contracts/schema/sub/deep.schema.json").write_text(
            '{"$schema": "x", "type": "object"}\n', encoding="utf-8"
        )
        run(
            "SP08",
            "contracts/schema 子目录中的 schema 未登记",
            current,
            current,
            pins,
            [record],
            "未登记为规格区段",
            test_root=sub_root,
        )

    print()
    print(f"规格区段绑定测试 9 条，符合预期 {9 - failures} 条。")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
