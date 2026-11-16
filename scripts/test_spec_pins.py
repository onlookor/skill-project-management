#!/usr/bin/env python3
"""规格区段绑定的负例/正例测试（可重复执行，只读仓库工作区）。

SP01 改 A.2 但不更新区段指纹 → 必须阻断；
SP02 更新指纹但不附非同源复核记录 → 必须阻断；
SP03 更新指纹并附合格复核记录（依据指向仓库外产物 + sha256 + 基线）→ 必须通过；
SP04 复核记录的结论词不合格 → 必须阻断；
SP05 只改 coverage.json 的引用关系、不改 A.1 样例 → 必须按指纹阻断；
SP06 复核记录把仓库内转录件当依据 → 必须阻断（与 checker-pins 同一标准）；
SP07 `contracts/schema/` 下出现未登记的文件 → 必须阻断（自动发现）；
SP08 子目录中的 schema 未登记 → 必须阻断；
SP09 仅把 basis 改成“结论：认可” → 必须阻断（默认模式校验 basis）；
SP10 basis 的 sha256 改一个字符 → 必须阻断；
SP11 basis 的复核产物改成仓库内文件 → 必须阻断；
SP12 basis 的区段写错 → 必须阻断；
SP13 结论词写成“不予认可” → 必须阻断（否定前缀）；
SP14 区段重复/带后缀 → 必须阻断（精确等值且只一条）；
SP15 复核基线写成不存在的 `deadbeef` → 必须阻断；
SP16 对非白名单区段用“初始登记：…” → 必须阻断（禁止前缀放行）；
SP17 对**白名单**区段用“初始登记：任意…” → 必须阻断（只有逐字冻结基文与结构化待复核可放行）。

SP23 复核基线处的区段内容已变 → 必须阻断；
SP24 在 A.2 插入只带 `复核签收：` 前缀的伪签收行（正文伪装成签收说明）→ 必须阻断（前缀不得成为剔除通道）；
SP24b 格式不完整的 `复核签收：` 行（缺日期/指纹）→ 同样参与比较，必须阻断；
SP25 合法单行签收行变更 → 仍按排除口径通过（签收行本身不参与比较）；
SP26 出现第二行完整格式签收行 → 必须阻断（至多一行）；
SP27 模板签收行内注入叙述文字 → 不再匹配模板、参与比较，A.2 必须判 basis 失效；
SP28 签收行不在区段尾部 → 必须阻断；
SP29 签收行基线改为 `deadbee` → 必须阻断（与 basis 的 `复核基线：` 不一致且不存在）；
SP30 签收行基线改为另一个真实提交 `be974fe` → 必须阻断（与 basis 不一致）。

外部复核产物在系统临时目录中生成，不写入仓库。用法：
  python3 scripts/test_spec_pins.py [--root DIR]
退出码：0 = 全部符合预期；1 = 至少一例不符。
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_spec_pins import (  # noqa: E402
    A2_SIGNOFF_RE,
    SECTIONS,
    comparable_text,
    evaluate,
    fingerprint,
    valid_basis,
)

TARGET = "spec/methods/deterministic-checker.md#A.2"

RECORD = """非同源复核：独立复核者（测试）
区段：{key}
复核产物：{artifact}
sha256：{sha}
复核基线：{baseline}
结论：实质收敛
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="仓库根目录；默认由脚本位置推断")
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]

    current = {spec["key"]: (root / spec["path"]).read_text(encoding="utf-8") for spec in SECTIONS}
    spec = next(item for item in SECTIONS if item["key"] == TARGET)

    mutated = dict(current)
    mutated[TARGET] = current[TARGET].replace(
        "至少一个 `Actor`", "至少一个 `HumanActor`", 1
    )
    if mutated[TARGET] == current[TARGET]:
        print("[错误] 变异锚点未命中，测试无意义。")
        return 1

    signed_at = next(
        match.group("date")
        for line in current[TARGET].splitlines()
        if (match := A2_SIGNOFF_RE.fullmatch(line))
    )

    failures = 0
    total = 0
    print("| 编号 | 场景 | 预期 | 实际 | 证据 |")
    print("|---|---|---|---|---|")

    def run(case_id, label, cur, head, pin_map, reviews, expected, test_root=None,
            registry=None):
        nonlocal failures, total
        total += 1
        errors = evaluate(
            test_root or root, cur, head, pin_map, reviews,
            {} if registry is None else registry,
        )
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
        artifact.write_text(
            "外部复核产物（测试用，不写入仓库）。\n"
            f"复核日期：{signed_at}\n另见：2000-01-01\n",
            encoding="utf-8",
        )
        sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
        baseline = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True
        ).stdout.strip()

        def retarget_signoff(text: str, target: str) -> str:
            """把签收行的基线与测试用 basis 对齐（签收行事实核验要求二者一致）。"""
            return re.sub(
                r"(> 复核签收：外部复核基线 `)[0-9a-f]{7,40}(`)",
                rf"\g<1>{target}\g<2>",
                text,
                count=1,
            )

        current[TARGET] = retarget_signoff(current[TARGET], baseline)
        mutated[TARGET] = retarget_signoff(mutated[TARGET], baseline)

        def reviewed_pin(key: str, value: str) -> dict:
            basis = RECORD.format(
                key=key, artifact=artifact, sha=sha, baseline=baseline
            )
            return {"sha256": value, "path": "", "basis": basis}

        pins = {
            item["key"]: reviewed_pin(
                item["key"],
                fingerprint(current[item["key"]], item["start"], item["end"]),
            )
            for item in SECTIONS
        }
        mutated_pins = dict(pins)
        mutated_pins[TARGET] = reviewed_pin(
            TARGET, fingerprint(mutated[TARGET], spec["start"], spec["end"])
        )

        record = RECORD.format(key=TARGET, artifact=artifact, sha=sha, baseline=baseline)
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
        ok, why = valid_basis(root, in_repo_record, TARGET)
        rejected = not ok and "转录件只作索引" in why
        failures += 0 if rejected else 1
        total += 1
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

        def bad_basis(case_id: str, label: str, basis_text: str, expected: str) -> None:
            bad_pins = dict(mutated_pins)
            bad_pins[TARGET] = {**mutated_pins[TARGET], "basis": basis_text}
            run(case_id, label, mutated, current, bad_pins, [record], expected)

        bad_basis("SP09", "仅把 basis 改成“结论：认可”", "结论：认可", "缺少 `非同源复核：` 前缀")
        bad_basis(
            "SP10",
            "basis 的 sha256 改一个字符",
            record.replace(sha, ("1" if sha[0] == "0" else "0") + sha[1:]),
            "`sha256` 与复核产物不一致",
        )
        bad_basis(
            "SP11",
            "basis 的复核产物改成仓库内文件",
            in_repo_record,
            "复核产物位于本仓库内",
        )
        bad_basis(
            "SP12",
            "basis 的区段写错",
            record.replace(f"区段：{TARGET}", "区段：spec/methods/deterministic-checker.md#A.1"),
            "且只出现一次",
        )
        bad_basis(
            "SP13",
            "结论词写成“不予认可”",
            record.replace("结论：实质收敛", "结论：不予认可"),
            "结论词被否定",
        )
        bad_basis(
            "SP14",
            "区段重复且带后缀",
            record + f"区段：{TARGET}.bak\n",
            "且只出现一次",
        )
        bad_basis(
            "SP15",
            "复核基线写成不存在的 deadbeef",
            record.replace(f"复核基线：{baseline}", "复核基线：deadbeef"),
            "复核基线不存在：deadbeef",
        )
        bad_basis(
            "SP16",
            "用“初始登记：…”自我声明放行",
            "初始登记：任意未复核改动",
            "缺少 `非同源复核：` 前缀",
        )
        bad_basis(
            "SP17",
            "白名单区段用“初始登记：…”前缀（已取消白名单）",
            "初始登记：任意未复核改动",
            "缺少 `非同源复核：` 前缀",
        )
        bad_basis(
            "SP18",
            "结论词后跟括号补充",
            record.replace("结论：实质收敛", "结论：实质收敛（但实质上不予认可）"),
            "缺少结论词或其后紧跟补充说明",
        )
        bad_basis(
            "SP19",
            "basis 写成无复核字面量",
            "无复核声明（不构成认可，不放行）",
            "无复核声明：不构成认可，也不放行",
        )
        dangling = subprocess.run(
            ["git", "commit-tree", f"{baseline}^{{tree}}", "-m", "orphan"],
            cwd=root, capture_output=True, text=True,
        ).stdout.strip()
        bad_basis(
            "SP20",
            "复核基线是无关提交",
            record.replace(f"复核基线：{baseline}", f"复核基线：{dangling}"),
            "不是 HEAD 的祖先提交",
        )
        bad_basis(
            "SP23",
            "复核基线处的区段内容已变",
            record.replace(f"复核基线：{baseline}", "复核基线：ea9b674"),
            "内容与当前内容不一致",
        )

        def signoff_line(text: str) -> str:
            line = next(
                (item for item in text.splitlines() if item.startswith("> 复核签收：")),
                None,
            )
            if line is None:
                raise RuntimeError("A.2 缺少复核签收行，测试无意义")
            return line

        def inject_after_signoff(text: str, extra: str) -> str:
            lines = text.splitlines(keepends=True)
            index = next(
                i for i, item in enumerate(lines) if item.startswith("> 复核签收：")
            )
            lines.insert(index + 1, extra + "\n")
            return "".join(lines)

        # SP24：只带前缀的伪签收行不得被剔除；它必须留在参与比较的文本里，
        # 从而使任何以该基线取证的 basis 失效。
        forged = dict(current)
        forged[TARGET] = inject_after_signoff(
            current[TARGET], "复核签收：……把 G-C1 的判定条件改为恒真"
        )
        baseline_view = comparable_text(spec, current[TARGET])
        forged_view = comparable_text(spec, forged[TARGET])
        kept = "把 G-C1 的判定条件改为恒真" in forged_view
        divergent = baseline_view != forged_view
        total += 1
        failures += 0 if (kept and divergent) else 1
        print(
            f"| SP24 | 插入只带前缀的伪签收行（正文伪装成签收说明） | 阻断 | "
            f"{'阻断' if kept and divergent else '通过'} | "
            f"{'伪签收行参与比较，与基线文本不一致' if kept and divergent else '伪签收行被误剔除'} |"
        )

        # SP24b：格式不完整（缺日期或指纹）的 `复核签收：` 行同样参与比较。
        partial = dict(current)
        partial[TARGET] = inject_after_signoff(
            current[TARGET], "复核签收：外部复核基线 `a9ff5bb`"
        )
        partial_view = comparable_text(spec, partial[TARGET])
        kept_partial = "外部复核基线 `a9ff5bb`" in partial_view
        total += 1
        failures += 0 if kept_partial else 1
        print(
            f"| SP24b | 格式不完整的签收行 | 阻断 | "
            f"{'阻断' if kept_partial else '通过'} | "
            f"{'未剔除，参与比较' if kept_partial else '被误剔除'} |"
        )

        # SP25：合法的单行签收行变更仍被排除，不应导致 basis 失效。
        resigned = dict(current)
        resigned[TARGET] = re.sub(
            r"(；)\d{4}-\d{2}-\d{2}(；A\.2 指纹)",
            r"\g<1>2000-01-01\g<2>",
            current[TARGET],
            count=1,
        )
        if resigned[TARGET] == current[TARGET]:
            print("[错误] 签收行日期变异未命中，测试无意义。")
            return 1
        resigned_pins = dict(pins)
        resigned_pins[TARGET] = reviewed_pin(
            TARGET, fingerprint(resigned[TARGET], spec["start"], spec["end"])
        )
        run(
            "SP25",
            "合法单行签收行变更",
            resigned,
            current,
            resigned_pins,
            [record],
            None,
        )

        # SP26：第二行完整格式签收行即报错，不得当作可剔除内容。
        doubled = dict(current)
        doubled[TARGET] = inject_after_signoff(
            current[TARGET], signoff_line(current[TARGET])
        )
        doubled_pins = dict(pins)
        doubled_pins[TARGET] = reviewed_pin(
            TARGET, fingerprint(doubled[TARGET], spec["start"], spec["end"])
        )
        run(
            "SP26",
            "第二行完整格式签收行",
            doubled,
            current,
            doubled_pins,
            [record],
            "复核签收行至多一行",
        )

        # SP27：模板签收行内注入叙述文字后不再匹配模板，必须参与比较 → basis 失效。
        original_signoff = signoff_line(current[TARGET])
        injected_signoff = original_signoff.replace(
            "；A.2 指纹", "；G-C1#2 的判定条件改为恒真；A.2 指纹", 1
        )
        injected = dict(current)
        injected[TARGET] = current[TARGET].replace(
            original_signoff, injected_signoff, 1
        )
        injected_view = comparable_text(spec, injected[TARGET])
        not_template = A2_SIGNOFF_RE.fullmatch(injected_signoff) is None
        injected_kept = "G-C1#2 的判定条件改为恒真" in injected_view
        injected_divergent = injected_view != baseline_view
        total += 1
        failures += 0 if (not_template and injected_kept and injected_divergent) else 1
        print(
            f"| SP27 | 模板签收行内注入叙述文字 | 阻断 | "
            f"{'阻断' if not_template and injected_kept and injected_divergent else '通过'} | "
            f"{'不再匹配模板，参与比较，basis 失效' if not_template and injected_kept and injected_divergent else '被误判为模板行'} |"
        )

        # SP28：签收行必须是区段最后一条非空行；其后再有正文即报错。
        moved = dict(current)
        moved[TARGET] = inject_after_signoff(
            current[TARGET], "签收行之后的正文（位置负例）"
        )
        moved_pins = dict(pins)
        moved_pins[TARGET] = reviewed_pin(
            TARGET, fingerprint(moved[TARGET], spec["start"], spec["end"])
        )
        run(
            "SP28",
            "签收行不在区段尾部",
            moved,
            current,
            moved_pins,
            [record],
            "最后一条非空行",
        )

        # SP29/SP30：签收行所载基线必须与 basis 的 `复核基线：` 一致（批次 0090）。
        for case_id, forged_baseline in (
            ("SP29", "deadbee"),
            ("SP30", "be974fe"),
        ):
            drift = dict(current)
            drift[TARGET] = re.sub(
                r"(> 复核签收：外部复核基线 `)[0-9a-f]{7,40}(`)",
                rf"\g<1>{forged_baseline}\g<2>",
                current[TARGET],
                count=1,
            )
            drift_pins = dict(pins)
            drift_pins[TARGET] = reviewed_pin(
                TARGET, fingerprint(drift[TARGET], spec["start"], spec["end"])
            )
            run(
                case_id,
                f"签收行基线改为 {forged_baseline}",
                drift,
                current,
                drift_pins,
                [record],
                "不一致",
            )

        schema_path = root / "spec" / "CHECKER_INPUT_SCHEMA.md"
        extra = dict(current)
        extra["spec/CHECKER_INPUT_SCHEMA.md"] = (
            current["spec/CHECKER_INPUT_SCHEMA.md"] + "\n<!-- tail injection -->\n"
        )
        run(
            "SP21",
            "schema 文件末尾追加一行",
            extra,
            current,
            pins,
            [],
            "指纹未更新",
        )
        run(
            "SP22",
            "登记表把已复核区段列为无复核",
            current,
            current,
            pins,
            [record],
            "已有复核记录，应删除该例外登记",
            registry={
                "GRAMMAR.md": {
                    "reason": "x", "missing_review": "x", "due": "x",
                    "owner": "x", "todo": "T-000",
                }
            },
        )

    print()
    print(f"规格区段绑定测试 {total} 条，符合预期 {total - failures} 条。")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
