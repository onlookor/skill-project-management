#!/usr/bin/env python3
"""检查器绑定的负例/正例测试（可重复执行，只读工作区）。

CP01 改检查器但不更新登记 → 必须阻断；
CP02 更新登记但不给裁定依据 → 必须拒绝；
CP03 更新登记并给出裁定依据 → 必须通过；
CP04 验收检查器与快照不一致 → 必须阻断（漂移检测）。

用法：python3 scripts/test_checker_pins.py [--root DIR]
退出码：0 = 四例全部符合预期；1 = 至少一例不符。
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

CHECKER = Path("scripts/check_checker_pins.py")


def run(root: Path, scripts: Path, pins: Path, source: Path, snapshot: Path,
        *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable,
            str(root / CHECKER),
            "--scripts-dir",
            str(scripts),
            "--pins",
            str(pins),
            "--source",
            str(source),
            "--snapshot",
            str(snapshot),
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
        scripts = base / "scripts"
        scripts.mkdir()
        sample = scripts / "check_sample.py"
        sample.write_text("print('checker v1')\n", encoding="utf-8")
        pins = base / "checker-pins.json"
        source = base / "checker.py"
        snapshot = base / "pinned" / "checker.py"
        source.write_text("# acceptance checker v1\n", encoding="utf-8")
        snapshot.parent.mkdir()
        snapshot.write_bytes(source.read_bytes())

        baseline = run(
            root, scripts, pins, source, snapshot, "--write", "--basis", "测试初始登记"
        )
        if baseline.returncode != 0:
            print("[错误] 绑定基线未建立。")
            print(baseline.stdout + baseline.stderr)
            return 1

        sample.write_text("print('checker v2')\n", encoding="utf-8")

        result = run(root, scripts, pins, source, snapshot)
        expected = "哈希不一致"
        ok = result.returncode == 1 and expected in result.stdout
        failures += 0 if ok else 1
        rows.append(("CP01", "改检查器不更新登记", "阻断" if ok else "未阻断",
                     str(result.returncode), evidence(result.stdout, expected)))

        result = run(root, scripts, pins, source, snapshot, "--write")
        expected = "未提供 --basis"
        ok = result.returncode == 2 and expected in result.stdout
        failures += 0 if ok else 1
        rows.append(("CP02", "更新登记但不给裁定依据", "拒绝" if ok else "未拒绝",
                     str(result.returncode), evidence(result.stdout, expected)))

        result = run(
            root, scripts, pins, source, snapshot, "--write", "--basis", "测试：升级到 v2"
        )
        ok = result.returncode == 0
        if ok:
            result = run(root, scripts, pins, source, snapshot)
            ok = result.returncode == 0
        failures += 0 if ok else 1
        rows.append(("CP03", "更新登记并给出裁定依据", "通过" if ok else "未通过",
                     str(result.returncode), "登记与工作区一致" if ok else result.stdout.strip()))

        snapshot.write_text("# acceptance checker v2 (drifted)\n", encoding="utf-8")
        result = run(root, scripts, pins, source, snapshot)
        expected = "快照不一致"
        ok = result.returncode == 1 and expected in result.stdout
        failures += 0 if ok else 1
        rows.append(("CP04", "验收检查器与快照不一致", "阻断" if ok else "未阻断",
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
