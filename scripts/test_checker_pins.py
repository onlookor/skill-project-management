#!/usr/bin/env python3
"""检查器绑定的负例/正例测试（可重复执行，只读工作区）。

CP01 改普通检查器但不更新登记 → 阻断；
CP02 更新登记但不给 basis → 拒绝（退出 2）；
CP03 `--write --basis "测试"`（自由文本）→ 拒绝（退出 2）；
CP04 更新登记并给出合格的非同源复核记录 → 通过；
CP05 把根检查器（验收原型）换成空壳 → 阻断；
CP06 删除 pre-commit 里的一条检查行 → 阻断；
CP07 验收检查器与快照不一致 → 阻断（漂移检测）。

用法：python3 scripts/test_checker_pins.py [--root DIR]
退出码：0 = 全部符合预期；1 = 至少一例不符。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKER = Path("scripts/check_checker_pins.py")
VALID_BASIS = (
    "非同源复核：基线 d8bf413；复核产物：validation/reviews/review.md；"
    "复核基线：d8bf413；结论：认可"
)


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
        base = Path(tmp)
        (base / "scripts").mkdir()
        (base / ".githooks").mkdir()
        (base / "validation" / "checker-prototype").mkdir(parents=True)
        (base / "validation" / "pinned").mkdir(parents=True)
        (base / "validation" / "reviews").mkdir(parents=True)
        sample = base / "scripts" / "check_sample.py"
        sample.write_text("print('checker v1')\n", encoding="utf-8")
        precommit = base / ".githooks" / "pre-commit"
        precommit.write_text(
            "#!/bin/sh\npython3 scripts/check_state.py\npython3 scripts/check_anchors.py\n",
            encoding="utf-8",
        )
        source = base / "validation" / "checker-prototype" / "checker.py"
        snapshot = base / "validation" / "pinned" / "checker.py"
        source.write_text("# acceptance checker v1\n", encoding="utf-8")
        snapshot.write_bytes(source.read_bytes())
        (base / "validation" / "reviews" / "review.md").write_text(
            "非同源复核：基线 d8bf413\n", encoding="utf-8"
        )

        baseline = run(root, base, "--write", "--basis", VALID_BASIS)
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
        expected = "缺少 `非同源复核：` 前缀"
        ok = result.returncode == 2 and expected in result.stdout
        failures += 0 if ok else 1
        rows.append(("CP02", "更新登记但不给 basis", "拒绝" if ok else "未拒绝",
                     str(result.returncode), evidence(result.stdout, expected)))

        result = run(root, base, "--write", "--basis", "测试")
        ok = result.returncode == 2 and expected in result.stdout
        failures += 0 if ok else 1
        rows.append(("CP03", "basis 写成自由文本“测试”", "拒绝" if ok else "未拒绝",
                     str(result.returncode), evidence(result.stdout, expected)))

        result = run(root, base, "--write", "--basis", VALID_BASIS)
        ok = result.returncode == 0
        if ok:
            result = run(root, base)
            ok = result.returncode == 0
        failures += 0 if ok else 1
        rows.append(("CP04", "合格复核记录更新登记", "通过" if ok else "未通过",
                     str(result.returncode), "登记与工作区一致" if ok else result.stdout.strip()))

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
