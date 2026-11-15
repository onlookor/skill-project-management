#!/usr/bin/env python3
"""外部校验依赖指纹：锁定版本、分发产物 sha256，并按 wheel RECORD 逐文件核对安装树。

依据：ADR-0019。`scripts/check_no_raw_material.py` 的数据区校验改用成熟实现
`jsonschema`；本检查器保证“依赖被替换能被发现”，而不是只锁版本号。

判定轴（任一命中即非零退出）：
  DP-VERSION   已安装版本与登记不符（未安装按“无法评估”退出 2）
  DP-IMPORT    实际导入的模块不在分发目录内（影子包、PYTHONPATH 劫持）
  DP-TREE      安装树与 wheel RECORD 的逐文件 sha256 / 大小不符，或出现未收录文件
  DP-ARTIFACT  未找到分发产物，或找到但 sha256 与登记不符，或 wheel 内 RECORD 不可读
  DP-REGISTRY  登记表缺项、多项或结构非法

三重核对都是强制项：版本、安装树逐文件内容哈希、分发产物 wheel 的 sha256。
wheel 默认从持久路径 `~/.local/share/pm-governance/wheels/` 读取（`JSONSCHEMA_WHEEL`
或 `--artifact` 可覆盖）。找不到产物即“无法评估”退出 2，不降级为只核对安装树——
永远只报警的检查等于没有。依赖缺失同样按“无法评估”处理，绝不降级为通过。

威胁模型（见 ADR-0019）：本检查能发现误装、版本漂移、非恶意不一致与非针对性
替换；**不构成对有权写本机 Python 环境者的防护**（`PYTHONPATH` 注入、
`sitecustomize`、直接改 `site-packages` 均在被信任边界之外，同 ADR-0015）。

获取 wheel（放在仓库外，不提交进 git）：
  python3 -m pip download --no-deps --no-cache-dir \
      jsonschema==4.26.0 -d ~/.local/share/pm-governance/wheels

用法：
  python3 scripts/check_dependency_pins.py
  python3 scripts/check_dependency_pins.py --write --artifact <wheel 路径>
  JSONSCHEMA_WHEEL=<wheel 路径> python3 scripts/check_dependency_pins.py
退出码：0 = 通过；1 = 指纹不符；2 = 依赖或分发产物缺失、登记表不可解析（无法评估，不得视为通过）。
"""

import argparse
import base64
import hashlib
import importlib.metadata as metadata
import importlib.util
import json
import os
import sys
import zipfile
from pathlib import Path

PINS_FILE = "scripts/dependency-pins.json"
PACKAGES = ("jsonschema",)
ARTIFACT_ENV = "JSONSCHEMA_WHEEL"
ARTIFACT_DIR = Path.home() / ".local" / "share" / "pm-governance" / "wheels"


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def content_hash(path):
    """wheel RECORD 使用的哈希形式：sha256 的 urlsafe base64（无填充）。"""
    data = Path(path).read_bytes()
    return base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b"=").decode()


def digest_record(text):
    """对 dist-info/RECORD 做稳定摘要，返回 (sha256, 文件数)；仅作次级指纹。"""
    entries = []
    for line in text.splitlines():
        parts = line.rsplit(",", 2)
        if len(parts) != 3:
            continue
        path, digest, size = parts
        if not digest.startswith("sha256="):
            continue
        entries.append(f"{path}\t{digest[7:]}\t{size}")
    return hashlib.sha256("\n".join(sorted(entries)).encode("utf-8")).hexdigest(), len(entries)


def wheel_entries(wheel):
    """读取 wheel 内 RECORD，返回 (dist_info 前缀, {相对路径: (b64 sha256, size)})。"""
    with zipfile.ZipFile(wheel) as archive:
        record_name = next(
            (name for name in archive.namelist() if name.endswith(".dist-info/RECORD")),
            None,
        )
        if record_name is None:
            raise ValueError("wheel 内缺少 .dist-info/RECORD")
        entries = {}
        for line in archive.read(record_name).decode("utf-8").splitlines():
            parts = line.rsplit(",", 2)
            if len(parts) != 3:
                continue
            path, digest, size = parts
            if not digest.startswith("sha256="):
                continue
            entries[path] = (digest[7:], size)
        return record_name.split("/")[0] + ".dist-info", entries


def import_origin(name):
    spec = importlib.util.find_spec(name)
    if spec is None or not spec.origin:
        return None
    return Path(spec.origin).resolve()


def installed_state(name):
    try:
        dist = metadata.distribution(name)
    except metadata.PackageNotFoundError:
        return None
    root = Path(dist.locate_file("")).resolve()
    origin = import_origin(name)
    record = dist.read_text("RECORD")
    if record is None:
        return {
            "version": dist.version,
            "root": str(root),
            "import_file": str(origin) if origin else None,
            "record_sha256": None,
            "files": 0,
        }
    digest, count = digest_record(record)
    return {
        "version": dist.version,
        "root": str(root),
        "import_file": str(origin) if origin else None,
        "record_sha256": digest,
        "files": count,
    }


def tree_errors(entries, root, import_file, package="jsonschema"):
    """按 wheel RECORD 逐文件核对安装树，并断言导入路径落在分发目录内。"""
    errors = []
    root = Path(root)
    package_root = root / package
    expected = {
        path: value for path, value in entries.items() if path.startswith(f"{package}/")
    }
    if import_file is None:
        errors.append(
            f"[错误] DP-IMPORT 无法定位 {package} 的导入路径；依赖可能不可用"
        )
    else:
        try:
            Path(import_file).resolve().relative_to(package_root.resolve())
        except ValueError:
            errors.append(
                f"[错误] DP-IMPORT 实际导入 {import_file} 不在分发目录 {package_root} 下；"
                "影子包或 PYTHONPATH 劫持会让校验器与钉扎对象不一致"
            )
    if package_root.is_dir():
        installed = {
            path.relative_to(root).as_posix()
            for path in package_root.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
    else:
        installed = set()
    for rel, (digest, size) in sorted(expected.items()):
        target = root / rel
        if not target.is_file():
            errors.append(f"[错误] DP-TREE 安装树缺少 wheel 收录的文件 {rel}")
            continue
        actual = content_hash(target)
        if actual != digest or str(target.stat().st_size) != size:
            errors.append(
                f"[错误] DP-TREE {rel} 内容与 wheel RECORD 不符"
                f"（实际 {actual[:12]}…，登记 {digest[:12]}…）；依赖可能被改动"
            )
    for rel in sorted(installed - set(expected)):
        errors.append(
            f"[错误] DP-TREE 安装树存在 wheel 未收录的文件 {rel}；"
            "保留原 RECORD 的注入物会在这里暴露"
        )
    return errors


def artifact_candidates(pin, override):
    if override:
        return [Path(override)]
    env = os.environ.get(ARTIFACT_ENV)
    if env:
        return [Path(env)]
    filename = (pin.get("artifact") or {}).get("filename")
    if not filename:
        return []
    candidates = [ARTIFACT_DIR / filename]
    cache = Path.home() / ".cache" / "pip"
    if cache.is_dir():
        candidates.extend(sorted(cache.rglob(filename))[:3])
    return candidates


def evaluate(pins, states, artifacts, trees=None):
    """返回 (errors, warnings)。纯函数，供自测调用。

    `trees` 为 {包名: (wheel RECORD 条目, 分发根, 导入文件)}；缺少逐文件数据即
    “无法评估”，不允许退化成只比较 RECORD 文本。
    """
    errors, warnings = [], []
    trees = trees or {}
    registry = pins.get("packages")
    if not isinstance(registry, dict):
        return ["[错误] DP-REGISTRY 登记表缺少 packages 对象"], warnings
    for name in PACKAGES:
        if name not in registry:
            errors.append(f"[错误] DP-REGISTRY 登记表缺少 {name}")
    for name in registry:
        if name not in PACKAGES:
            errors.append(f"[错误] DP-REGISTRY 登记表含未使用依赖 {name}")
    for name in PACKAGES:
        pin = registry.get(name)
        if not isinstance(pin, dict):
            continue
        state = states.get(name)
        if state is None:
            errors.append(
                f"[无法评估] DP-VERSION 依赖 {name} 未安装；请运行 "
                f"`python3 -m pip install --user {name}=={pin.get('version')}`；"
                "依赖缺失不得降级为跳过校验"
            )
            continue
        if state["version"] != pin.get("version"):
            errors.append(
                f"[错误] DP-VERSION {name} 版本 {state['version']} 与登记 "
                f"{pin.get('version')} 不符"
            )
        installed = pin.get("installed") or {}
        if state["record_sha256"] != installed.get("record_sha256"):
            errors.append(
                f"[错误] DP-TREE {name} RECORD 摘要与登记不符"
                f"（实际 {state['record_sha256']}，登记 {installed.get('record_sha256')}）；"
                "依赖可能被替换或改动"
            )
        if state["files"] != installed.get("files"):
            errors.append(
                f"[错误] DP-TREE {name} 安装文件数 {state['files']} 与登记 "
                f"{installed.get('files')} 不符"
            )
        tree = trees.get(name)
        if tree is None:
            errors.append(
                f"[无法评估] DP-TREE {name} 缺少 wheel 逐文件数据，"
                "无法核对实际安装树；不得退化为只比较 RECORD 文本"
            )
        else:
            entries, root, import_file = tree
            errors.extend(tree_errors(entries, root, import_file, name))
        artifact = pin.get("artifact") or {}
        if not artifacts:
            errors.append(
                f"[无法评估] DP-ARTIFACT 未找到 {name} 的分发产物"
                f"（{artifact.get('filename')}）；分发产物核对是强制项，"
                f"请放到 {ARTIFACT_DIR} 或设置 {ARTIFACT_ENV}=<wheel 路径>："
                "python3 -m pip download --no-deps --no-cache-dir "
                f"{name}=={pin.get('version')} -d {ARTIFACT_DIR}"
            )
            continue
        for path in artifacts:
            actual = sha256_file(path)
            if actual != artifact.get("sha256"):
                errors.append(
                    f"[错误] DP-ARTIFACT {path} 的 sha256 {actual} 与登记 "
                    f"{artifact.get('sha256')} 不符"
                )
    return errors, warnings


def build_trees(pins, artifacts):
    """按包读取 wheel RECORD，绑到该包的实际分发根与导入路径。"""
    trees = {}
    by_name = {}
    for name in PACKAGES:
        pin = (pins.get("packages") or {}).get(name) or {}
        filename = (pin.get("artifact") or {}).get("filename")
        by_name[name] = next(
            (path for path in artifacts if path.name == filename), None
        )
    for name in PACKAGES:
        wheel = by_name.get(name)
        state = installed_state(name)
        if wheel is None or state is None:
            continue
        try:
            _, entries = wheel_entries(wheel)
        except (OSError, ValueError, zipfile.BadZipFile):
            continue
        trees[name] = (entries, state["root"], state["import_file"])
    return trees


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--artifact", default=None)
    args = parser.parse_args()
    root = Path(args.root)
    pins_path = root / PINS_FILE

    states = {name: installed_state(name) for name in PACKAGES}
    if args.write:
        if any(state is None for state in states.values()):
            print("[无法评估] 依赖未安装，不能登记指纹", file=sys.stderr)
            return 2
        old = {}
        if pins_path.is_file():
            try:
                old = json.loads(pins_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                old = {}
        packages = {}
        for name in PACKAGES:
            previous = (old.get("packages") or {}).get(name) or {}
            artifact = previous.get("artifact") or {}
            if args.artifact:
                wheel = Path(args.artifact)
                artifact = {"filename": wheel.name, "sha256": sha256_file(wheel)}
            if not artifact.get("sha256"):
                print(
                    f"[无法评估] 缺少 {name} 的分发产物 sha256；请用 --artifact <wheel> 登记",
                    file=sys.stderr,
                )
                return 2
            state = states[name]
            packages[name] = {
                "version": state["version"],
                "artifact": artifact,
                "installed": {
                    "record_sha256": state["record_sha256"],
                    "files": state["files"],
                },
                "reason": "ADR-0019",
            }
        pins_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "note": "外部校验依赖指纹；版本、wheel sha256 与按 RECORD 逐文件核对的安装树须同时匹配",
                    "packages": packages,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"已登记 {PINS_FILE}：{', '.join(PACKAGES)}")
        return 0

    try:
        pins = json.loads(pins_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[无法评估] 不能读取或解析 {PINS_FILE}：{exc}", file=sys.stderr)
        return 2

    artifacts = []
    for name in PACKAGES:
        pin = (pins.get("packages") or {}).get(name) or {}
        artifacts.extend(path for path in artifact_candidates(pin, args.artifact) if path.is_file())

    trees = build_trees(pins, artifacts)
    errors, warnings = evaluate(pins, states, artifacts, trees)
    for line in warnings:
        print(line)
    for line in errors:
        print(line)
    if errors:
        if any(line.startswith("[无法评估]") for line in errors):
            return 2
        return 1
    total = sum(state["files"] for state in states.values() if state)
    checked = sum(len(entries) for entries, _, _ in trees.values())
    print(f"[通过] 依赖指纹 {len(PACKAGES)} 个包、{total} 个文件；"
          f"分发产物 sha256 核对 {len(artifacts)} 个；"
          f"按 wheel RECORD 逐文件核对 {checked} 项")
    return 0


if __name__ == "__main__":
    sys.exit(main())
