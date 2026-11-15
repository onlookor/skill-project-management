#!/usr/bin/env python3
"""check_dependency_pins.py 的负例：版本、安装树与分发产物被替换都要被发现。"""

import hashlib
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_dependency_pins as cdp  # noqa: E402

FAILS = []


def check(label, condition, detail=""):
    status = "通过" if condition else "失败"
    print(f"[{status}] {label}{('：' + detail) if detail else ''}")
    if not condition:
        FAILS.append(label)


def main():
    record_a = (
        "jsonschema/__init__.py,sha256=AAA,120\n"
        "jsonschema/_keywords.py,sha256=BBB,900\n"
        "jsonschema-4.26.0.dist-info/RECORD,,\n"
    )
    record_b = (
        "jsonschema-4.26.0.dist-info/RECORD,,\n"
        "jsonschema/_keywords.py,sha256=BBB,900\n"
        "jsonschema/__init__.py,sha256=AAA,120\n"
    )
    record_tampered = record_a.replace("sha256=BBB", "sha256=CCC")

    digest_a, count_a = cdp.digest_record(record_a)
    digest_b, count_b = cdp.digest_record(record_b)
    check("DP-T01 记录顺序不影响摘要", digest_a == digest_b and count_a == count_b == 2)
    check("DP-T02 任一文件被替换即改变摘要",
          cdp.digest_record(record_tampered)[0] != digest_a)

    pin = {
        "packages": {
            "jsonschema": {
                "version": "4.26.0",
                "artifact": {"filename": "jsonschema-4.26.0-py3-none-any.whl",
                             "sha256": "f" * 64},
                "installed": {"record_sha256": digest_a, "files": 2},
            }
        }
    }
    good = {"jsonschema": {"version": "4.26.0", "record_sha256": digest_a, "files": 2}}
    errors, warnings = cdp.evaluate(pin, good, [])
    check("DP-T03 产物缺席按无法评估阻断，不再只警告",
          any(line.startswith("[无法评估]") and "DP-ARTIFACT" in line for line in errors)
          and not warnings)

    bad_version = {"jsonschema": {"version": "4.25.0", "record_sha256": digest_a, "files": 2}}
    errors, _ = cdp.evaluate(pin, bad_version, [])
    check("DP-T04 版本不符被发现", any("DP-VERSION" in line for line in errors))

    bad_tree = {"jsonschema": {"version": "4.26.0", "record_sha256": "0" * 64, "files": 2}}
    errors, _ = cdp.evaluate(pin, bad_tree, [])
    check("DP-T05 安装树被替换被发现", any("DP-TREE" in line for line in errors))

    missing = {"jsonschema": None}
    errors, _ = cdp.evaluate(pin, missing, [])
    check("DP-T06 依赖缺失按无法评估处理",
          any(line.startswith("[无法评估]") and "未安装" in line for line in errors))

    wheel = Path(__file__).resolve().parent / ".dp-test.whl"
    wheel.write_bytes(b"not-a-real-wheel")
    actual = hashlib.sha256(wheel.read_bytes()).hexdigest()
    try:
        errors, _ = cdp.evaluate(pin, good, [wheel])
        check("DP-T07 产物 sha256 不符被发现", any("DP-ARTIFACT" in line for line in errors))
        pin["packages"]["jsonschema"]["artifact"]["sha256"] = actual
        errors, _ = cdp.evaluate(pin, good, [wheel])
        check("DP-T08 产物 sha256 吻合时通过", not errors)
    finally:
        wheel.unlink()

    bad_registry = {"packages": {"jsonschema": pin["packages"]["jsonschema"], "extra": {}}}
    errors, _ = cdp.evaluate(bad_registry, good, [])
    check("DP-T09 登记表出现未使用依赖被发现",
          any("未使用依赖" in line for line in errors))

    saved = os.environ.pop(cdp.ARTIFACT_ENV, None)
    try:
        candidates = cdp.artifact_candidates(
            {"artifact": {"filename": "jsonschema-4.26.0-py3-none-any.whl"}}, None
        )
    finally:
        if saved is not None:
            os.environ[cdp.ARTIFACT_ENV] = saved
    check("DP-T10 默认从持久目录读取分发产物",
          cdp.ARTIFACT_DIR / "jsonschema-4.26.0-py3-none-any.whl" in candidates)

    print(f"\n{10 - len(FAILS)}/10 项通过")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
