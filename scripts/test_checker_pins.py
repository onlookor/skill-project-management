#!/usr/bin/env python3
"""检查器绑定的负例/正例测试（可重复执行，只读工作区）。

CP01 改普通检查器但不更新登记 → 阻断；
CP02 更新登记但不给 basis → 拒绝（退出 2）；
CP03 `--write --basis "测试"`（自由文本）→ 拒绝（退出 2）；
CP04 更新登记并给出合格的非同源复核记录 → 通过；
CP05 把根检查器（验收原型）换成空壳 → 阻断；
CP06 删除 pre-commit 里的一条检查行 → 阻断；
CP07 验收检查器与快照不一致 → 阻断（漂移检测）；
CP08 仅把 basis 改成“结论：认可” → 阻断（默认模式校验 basis）；
CP09 basis 的 sha256 改一个字符 → 阻断；
CP10 basis 的复核产物改成仓库内文件 → 阻断；
CP11 basis 的区段写错 → 阻断；
CP12 结论词写成“不予认可” → 阻断（否定前缀）；
CP13 区段重复/带后缀 → 阻断（必须精确等值且只一条）；
CP14 复核基线写成不存在的 `deadbeef` → 阻断；
CP15 对非白名单对象用“初始登记：任意未复核改动” → 阻断（禁止前缀放行）；
CP16 对**白名单内**对象（check_state.py）用同一前缀 --write → 拒绝（退出 2，只有冻结基文或结构化待复核可放行）；
CP17 用冻结历史基文“初始登记”覆盖白名单对象的新改动 → 拒绝（旧状态不是新授权）。

用法：python3 scripts/test_checker_pins.py [--root DIR]
退出码：0 = 全部符合预期；1 = 至少一例不符。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKER = Path("scripts/check_checker_pins.py")


def run(root: Path, base: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(root / CHECKER),
            "--root",
            str(base),
            "--pins",
            str(base / "scripts" / "checker-pins.json"),
            "--source",
            str(base / "validation" / "checker-prototype" / "checker.py"),
            "--snapshot",
            str(base / "validation" / "pinned" / "checker.py"),
            *extra,
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

    rows: list[tuple[str, str, str, str, str]] = []
    failures = 0
    with tempfile.TemporaryDirectory(prefix="pm-checker-pins-") as tmp:
        outer = Path(tmp)
        base = outer / "repo"
        base.mkdir()
        (base / "scripts").mkdir()
        (base / ".githooks").mkdir()
        (base / "validation" / "checker-prototype").mkdir(parents=True)
        (base / "validation" / "pinned").mkdir(parents=True)
        (base / "validation" / "reviews").mkdir(parents=True)
        sample = base / "scripts" / "check_sample.py"
        sample.write_text("print('checker v1')\n", encoding="utf-8")
        guarded = base / "scripts" / "check_state.py"
        guarded.write_text("print('state v1')\n", encoding="utf-8")
        precommit = base / ".githooks" / "pre-commit"
        precommit.write_text(
            "#!/bin/sh\npython3 scripts/check_state.py\npython3 scripts/check_anchors.py\n",
            encoding="utf-8",
        )
        source = base / "validation" / "checker-prototype" / "checker.py"
        snapshot = base / "validation" / "pinned" / "checker.py"
        source.write_text("# acceptance checker v1\n", encoding="utf-8")
        snapshot.write_bytes(source.read_bytes())
        subprocess.run(["git", "init", "-q"], cwd=base, check=True)
        subprocess.run(["git", "add", "-A"], cwd=base, check=True)
        subprocess.run(
            ["git", "-c", "user.email=t@example.com", "-c", "user.name=t",
             "commit", "-qm", "base"],
            cwd=base,
            check=True,
        )
        baseline_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=base, capture_output=True, text=True
        ).stdout.strip()
        # basis 必须指向仓库外产物并与 sha256 一致；复核记录放在 base 之外。
        artifact = outer / "review.md"
        artifact.write_text("非同源复核：基线已提交\n", encoding="utf-8")
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()

        def basis_for(key: str) -> str:
            return (
                "非同源复核：基线已提交；"
                f"复核产物：{artifact}；"
                f"sha256：{digest}；"
                f"复核基线：{baseline_sha}；区段：{key}；结论：认可"
            )

        valid_basis = basis_for("scripts/check_sample.py")
        baseline = run(
            root,
            base,
            "--write",
            "--basis",
            basis_for("scripts/check_sample.py"),
            "--basis",
            basis_for(".githooks/pre-commit"),
            "--basis",
            basis_for("validation/checker-prototype/checker.py"),
            "--basis",
            basis_for("scripts/check_state.py"),
        )
        if baseline.returncode != 0:
            print("[错误] 绑定基线未建立。")
            print(baseline.stdout + baseline.stderr)
            return 1

        sample.write_text("print('checker v2')\n", encoding="utf-8")
        result = run(root, base)
        expected = "scripts/check_sample.py：哈希不一致"
        ok = result.returncode == 1 and expected in result.stdout
        failures += 0 if ok else 1
        rows.append(("CP01", "改检查器不更新登记", "阻断" if ok else "未阻断",
                     str(result.returncode), evidence(result.stdout, expected)))

        result = run(root, base, "--write")
        expected = "未提供 --basis"
        ok = result.returncode == 2 and expected in result.stdout
        failures += 0 if ok else 1
        rows.append(("CP02", "更新登记但不给 basis", "拒绝" if ok else "未拒绝",
                     str(result.returncode), evidence(result.stdout, expected)))

        result = run(root, base, "--write", "--basis", "测试")
        expected = "缺少 `非同源复核：` 前缀"
        ok = result.returncode == 2 and expected in result.stdout
        failures += 0 if ok else 1
        rows.append(("CP03", "basis 写成自由文本“测试”", "拒绝" if ok else "未拒绝",
                     str(result.returncode), evidence(result.stdout, expected)))

        result = run(root, base, "--write", "--basis", valid_basis)
        ok = result.returncode == 0
        if ok:
            result = run(root, base)
            ok = result.returncode == 0
        failures += 0 if ok else 1
        rows.append(("CP04", "合格复核记录更新登记", "通过" if ok else "未通过",
                     str(result.returncode), "登记与工作区一致" if ok else result.stdout.strip()))

        # 默认读取模式也必须校验 basis 内容（CP08–CP11 只改 basis 文本，不动哈希）。
        pins_path = base / "scripts" / "checker-pins.json"

        def mutate_basis(text: str) -> None:
            pins = json.loads(pins_path.read_text(encoding="utf-8"))
            pins["scripts"]["scripts/check_sample.py"]["basis"] = text
            pins_path.write_text(
                json.dumps(pins, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )

        recorded_sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
        inside = base / "review.md"
        inside.write_text("仓库内转录件\n", encoding="utf-8")
        basis_cases = [
            ("CP08", "仅把 basis 改成“结论：认可”", "结论：认可", "缺少 `非同源复核：` 前缀"),
            (
                "CP09",
                "basis 的 sha256 改一个字符",
                valid_basis.replace(recorded_sha, ("1" if recorded_sha[0] == "0" else "0") + recorded_sha[1:]),
                "`sha256` 与复核产物不一致",
            ),
            (
                "CP10",
                "basis 的复核产物改成仓库内文件",
                valid_basis.replace(str(artifact), str(inside)),
                "复核产物位于本仓库内",
            ),
            (
                "CP11",
                "basis 的区段写错",
                valid_basis.replace("区段：scripts/check_sample.py", "区段：scripts/other.py"),
                "且只出现一次",
            ),
            (
                "CP12",
                "结论词写成“不予认可”",
                valid_basis.replace("结论：认可", "结论：不予认可"),
                "结论词被否定",
            ),
            (
                "CP13",
                "区段重复且带后缀",
                valid_basis + "；区段：scripts/check_sample.py.bak",
                "且只出现一次",
            ),
            (
                "CP14",
                "复核基线写成不存在的 deadbeef",
                valid_basis.replace(f"复核基线：{baseline_sha}", "复核基线：deadbeef"),
                "复核基线不存在：deadbeef",
            ),
            (
                "CP15",
                "非白名单对象用“初始登记：…”放行",
                "初始登记：任意未复核改动",
                "缺少 `非同源复核：` 前缀",
            ),
        ]
        for number, scene, basis_text, expected in basis_cases:
            mutate_basis(basis_text)
            result = run(root, base)
            ok = result.returncode == 1 and expected in result.stdout
            failures += 0 if ok else 1
            rows.append((number, scene, "阻断" if ok else "未阻断",
                         str(result.returncode), evidence(result.stdout, expected)))
        mutate_basis(valid_basis)

        # 白名单内对象：前缀文本与冻结旧状态都不能覆盖新改动（--write 侧收口）。
        guarded.write_text("print('state v2')\n", encoding="utf-8")
        for number, label, text in (
            ("CP16", "白名单对象用“初始登记：任意未复核改动”--write", "初始登记：任意未复核改动"),
            ("CP17", "白名单对象用冻结旧状态“初始登记”覆盖新改动", "初始登记"),
        ):
            result = run(root, base, "--write", "--basis", text)
            expected = "缺少 `非同源复核：` 前缀"
            ok = result.returncode == 2 and expected in result.stdout
            failures += 0 if ok else 1
            rows.append((number, label, "拒绝" if ok else "未拒绝",
                         str(result.returncode), evidence(result.stdout, expected)))
        guarded.write_text("print('state v1')\n", encoding="utf-8")

        source.write_text("# empty shell\n", encoding="utf-8")
        result = run(root, base)
        expected = "validation/checker-prototype/checker.py：哈希不一致"
        ok = result.returncode == 1 and expected in result.stdout
        failures += 0 if ok else 1
        rows.append(("CP05", "根检查器换成空壳", "阻断" if ok else "未阻断",
                     str(result.returncode), evidence(result.stdout, expected)))
        source.write_text("# acceptance checker v2\n", encoding="utf-8")

        precommit.write_text("#!/bin/sh\npython3 scripts/check_state.py\n", encoding="utf-8")
        result = run(root, base)
        expected = ".githooks/pre-commit：哈希不一致"
        ok = result.returncode == 1 and expected in result.stdout
        failures += 0 if ok else 1
        rows.append(("CP06", "删除 pre-commit 检查行", "阻断" if ok else "未阻断",
                     str(result.returncode), evidence(result.stdout, expected)))

        snapshot.write_text("# acceptance checker drifted\n", encoding="utf-8")
        result = run(root, base)
        expected = "快照不一致"
        ok = result.returncode == 1 and expected in result.stdout
        failures += 0 if ok else 1
        rows.append(("CP07", "验收检查器与快照不一致", "阻断" if ok else "未阻断",
                     str(result.returncode), evidence(result.stdout, expected)))

    print("| 编号 | 场景 | 预期 | 实际 | 证据 |")
    print("|---|---|---|---|---|")
    for row in rows:
        print("| " + " | ".join(row) + " |")
    print()
    print(f"检查器绑定测试 {len(rows)} 条，符合预期 {len(rows) - failures} 条。")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
