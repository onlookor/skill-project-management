#!/usr/bin/env python3
"""check_dependency_pins.py 的负例：版本、逐文件安装树、影子包与分发产物被替换都要被发现。"""

import base64
import hashlib
import os
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_dependency_pins as cdp  # noqa: E402

FAILS = []
FILES = {
    "jsonschema/__init__.py": b"# genuine\n__version__ = '4.26.0'\n",
    "jsonschema/_keywords.py": b"def genuine():\n    return 1\n",
}
WHEEL_NAME = "jsonschema-4.26.0-py3-none-any.whl"


def check(label, condition, detail=""):
    status = "通过" if condition else "失败"
    print(f"[{status}] {label}{('：' + detail) if detail else ''}")
    if not condition:
        FAILS.append(label)


def build_wheel(path):
    lines = []
    with zipfile.ZipFile(path, "w") as archive:
        for rel, data in FILES.items():
            archive.writestr(rel, data)
            digest = base64.urlsafe_b64encode(
                hashlib.sha256(data).digest()
            ).rstrip(b"=").decode()
            lines.append(f"{rel},sha256={digest},{len(data)}")
        lines.append("jsonschema-4.26.0.dist-info/RECORD,,")
        archive.writestr(
            "jsonschema-4.26.0.dist-info/RECORD", "\n".join(lines) + "\n"
        )


def write_tree(root, files=None):
    files = files if files is not None else FILES
    for rel, data in files.items():
        target = Path(root) / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return Path(root) / "jsonschema/__init__.py"


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
    digest_a, count_a = cdp.digest_record(record_a)
    digest_b, count_b = cdp.digest_record(record_b)
    check("DP-T01 记录顺序不影响摘要", digest_a == digest_b and count_a == count_b == 2)
    check(
        "DP-T02 任一文件被替换即改变摘要",
        cdp.digest_record(record_a.replace("sha256=BBB", "sha256=CCC"))[0] != digest_a,
    )

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        wheel = tmp / WHEEL_NAME
        build_wheel(wheel)
        _, entries = cdp.wheel_entries(wheel)
        site = tmp / "site-packages"
        origin = write_tree(site)

        pin = {
            "packages": {
                "jsonschema": {
                    "version": "4.26.0",
                    "artifact": {"filename": WHEEL_NAME,
                                 "sha256": cdp.sha256_file(wheel)},
                    "installed": {"record_sha256": digest_a, "files": 2},
                }
            }
        }
        state = {"jsonschema": {"version": "4.26.0", "root": str(site),
                                "import_file": str(origin),
                                "record_sha256": digest_a, "files": 2}}
        tree = {"jsonschema": (entries, site, origin)}

        errors, _ = cdp.evaluate(pin, state, [], tree)
        check(
            "DP-T03 产物缺席按无法评估阻断",
            any(line.startswith("[无法评估]") and "DP-ARTIFACT" in line for line in errors),
        )

        errors, _ = cdp.evaluate(
            pin, {"jsonschema": dict(state["jsonschema"], version="4.25.0")}, [wheel], tree
        )
        check("DP-T04 版本不符被发现", any("DP-VERSION" in line for line in errors))

        tampered = tmp / "tampered"
        tampered_origin = write_tree(
            tampered, {**FILES, "jsonschema/_keywords.py": b"def genuine():\n    return 2\n"}
        )
        errors, _ = cdp.evaluate(
            pin, state, [wheel], {"jsonschema": (entries, tampered, tampered_origin)}
        )
        check(
            "DP-T05 改安装树而保留原 RECORD 被发现",
            any("DP-TREE" in line and "_keywords.py" in line for line in errors),
        )

        errors, _ = cdp.evaluate(pin, {"jsonschema": None}, [wheel], tree)
        check(
            "DP-T06 依赖缺失按无法评估处理",
            any(line.startswith("[无法评估]") and "未安装" in line for line in errors),
        )

        fake = tmp / "fake" / WHEEL_NAME
        fake.parent.mkdir()
        fake.write_bytes(b"not-the-registered-wheel")
        errors, _ = cdp.evaluate(pin, state, [fake], tree)
        check("DP-T07 同名假 wheel 的 sha256 不符被发现",
              any("DP-ARTIFACT" in line for line in errors))

        errors, _ = cdp.evaluate(pin, state, [wheel], tree)
        check("DP-T08 产物与逐文件安装树一致时通过", not errors,
              "；".join(errors[:1]))

        bad_registry = {"packages": {**pin["packages"], "extra": {}}}
        errors, _ = cdp.evaluate(bad_registry, state, [wheel], tree)
        check("DP-T09 登记表出现未使用依赖被发现",
              any("未使用依赖" in line for line in errors))

        shadow = tmp / "shadow"
        shadow_origin = write_tree(shadow)
        errors, _ = cdp.evaluate(
            pin, {"jsonschema": dict(state["jsonschema"], import_file=str(shadow_origin))},
            [wheel], {"jsonschema": (entries, site, shadow_origin)},
        )
        check(
            "DP-T11 影子包（PYTHONPATH 劫持）被发现",
            any("DP-IMPORT" in line for line in errors),
        )

        injected = tmp / "injected"
        injected_origin = write_tree(injected)
        (injected / "jsonschema/extra_hook.py").write_text("X = 1\n", encoding="utf-8")
        errors, _ = cdp.evaluate(
            pin, state, [wheel], {"jsonschema": (entries, injected, injected_origin)}
        )
        check(
            "DP-T12 保留 RECORD 的注入文件被发现",
            any("wheel 未收录" in line for line in errors),
        )

        errors, _ = cdp.evaluate(pin, state, [wheel], {})
        check(
            "DP-T13 缺少逐文件数据时按无法评估阻断",
            any(line.startswith("[无法评估]") and "DP-TREE" in line for line in errors),
        )

    saved = os.environ.pop(cdp.ARTIFACT_ENV, None)
    try:
        candidates = cdp.artifact_candidates({"artifact": {"filename": WHEEL_NAME}}, None)
    finally:
        if saved is not None:
            os.environ[cdp.ARTIFACT_ENV] = saved
    check("DP-T10 默认从持久目录读取分发产物",
          cdp.ARTIFACT_DIR / WHEEL_NAME in candidates)

    print(f"\n{13 - len(FAILS)}/13 项通过")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
