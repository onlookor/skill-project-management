#!/usr/bin/env python3
"""覆盖闸门：A.2 每个子句至少 1 个正例 + 1 个负例，且样例方向与原因码可机械核对。

覆盖矩阵登记在 validation/checker-prototype/coverage.json：
  clause id -> {check_id, positive: [样例编号], negative: [样例编号]}

核对项：
  1. 矩阵必须与 A.2 的子句集合完全一致（缺条目、多余条目都阻断）；
  2. 每个子句至少 1 个正例、1 个负例，缺一即阻断；
  3. 正例：样例存在、check_id 一致、期望 verdict=pass；
  4. 负例：样例存在、check_id 一致、期望 verdict≠pass、期望 reason 属于该子句原因码；
  5. 每个样例都必须被至少一个子句引用（防止用未登记样例充数）。

用法：python3 scripts/check_coverage_gate.py [--root DIR] [--method FILE] [--manifest FILE]
退出码：0 = 覆盖矩阵合格；1 = 存在缺口；2 = 解析失败。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

METHOD = Path("spec/methods/deterministic-checker.md")
MANIFEST = Path("validation/checker-prototype/coverage.json")


def split_row(line: str) -> list[str] | None:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return None
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def parse_clauses(text: str) -> dict[str, dict]:
    """从 A.2 解析 clause id -> {check_id, reasons}。"""
    clauses: dict[str, dict] = {}
    for line in text.splitlines():
        cells = split_row(line)
        if not cells or len(cells) < 8:
            continue
        if not (cells[0].startswith("`G-") and cells[0].endswith("`")):
            continue
        clause = cells[0].strip("`")
        clauses[clause] = {
            "check_id": cells[4].strip("`"),
            "reasons": set(re.findall(r"[a-z][a-z0-9_]+", cells[3])),
        }
    return clauses


def parse_samples(text: str) -> dict[str, dict]:
    """从 A.1 解析样例编号 -> {check_id, verdict, reason}。"""
    headings = list(re.finditer(r"^#### A\.1\.(\d+) ", text, re.M))
    samples: dict[str, dict] = {}
    for order, heading in enumerate(headings):
        number = int(heading.group(1))
        start = heading.end()
        end = headings[order + 1].start() if order + 1 < len(headings) else len(text)
        blocks = re.findall(r"```yaml\n(.*?)```", text[start:end], re.S)
        if len(blocks) < 2 or len(blocks) % 2:
            raise ValueError(f"A.1.{number} 的 YAML 块应为偶数且不少于 2，实际 {len(blocks)}")
        for index in range(0, len(blocks), 2):
            expected = blocks[index + 1]
            check = re.search(r"^check_id:\s*(\S+)\s*$", expected, re.M)
            verdict = re.search(r"^verdict:\s*(\S+)\s*$", expected, re.M)
            reason = re.search(r"^reason:\s*(\S+)\s*$", expected, re.M)
            if not (check and verdict):
                raise ValueError(f"A.1.{number}-{index // 2 + 1} 缺少 check_id 或 verdict")
            samples[f"A.1.{number}-{index // 2 + 1}"] = {
                "check_id": check.group(1),
                "verdict": verdict.group(1),
                "reason": None
                if reason is None or reason.group(1) in ("null", "None", "~")
                else reason.group(1),
            }
    return samples


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", help="仓库根目录；默认由脚本位置推断")
    parser.add_argument("--method", help="方法文件；默认 spec/methods/deterministic-checker.md")
    parser.add_argument("--manifest", help="覆盖矩阵；默认 validation/checker-prototype/coverage.json")
    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parents[1]
    method_path = Path(args.method) if args.method else root / METHOD
    manifest_path = Path(args.manifest) if args.manifest else root / MANIFEST

    try:
        clauses = parse_clauses(method_path.read_text(encoding="utf-8"))
        samples = parse_samples(method_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[错误] 解析失败：{exc}")
        return 2
    entries = manifest.get("clauses", {})

    errors: list[str] = []
    missing = sorted(set(clauses) - set(entries))
    extra = sorted(set(entries) - set(clauses))
    for clause in missing:
        errors.append(f"{clause}：矩阵缺少条目")
    for clause in extra:
        errors.append(f"{clause}：矩阵存在 A.2 未定义的子句")

    referenced: set[str] = set()
    positives = 0
    negatives = 0
    for clause, spec in clauses.items():
        entry = entries.get(clause)
        if entry is None:
            continue
        if entry.get("check_id") != spec["check_id"]:
            errors.append(
                f"{clause}：矩阵 check_id={entry.get('check_id')} 与 A.2={spec['check_id']} 不一致"
            )
        positive = entry.get("positive") or []
        negative = entry.get("negative") or []
        if not positive:
            errors.append(f"{clause}：缺少正例")
        if not negative:
            errors.append(f"{clause}：缺少负例")
        for sample_id in positive:
            referenced.add(sample_id)
            sample = samples.get(sample_id)
            if sample is None:
                errors.append(f"{clause}：正例 {sample_id} 不存在")
                continue
            positives += 1
            if sample["check_id"] != spec["check_id"]:
                errors.append(f"{clause}：正例 {sample_id} 的 check_id 不匹配")
            if sample["verdict"] != "pass":
                errors.append(
                    f"{clause}：正例 {sample_id} 期望 verdict={sample['verdict']}，不是 pass"
                )
        for sample_id in negative:
            referenced.add(sample_id)
            sample = samples.get(sample_id)
            if sample is None:
                errors.append(f"{clause}：负例 {sample_id} 不存在")
                continue
            negatives += 1
            if sample["check_id"] != spec["check_id"]:
                errors.append(f"{clause}：负例 {sample_id} 的 check_id 不匹配")
            if sample["verdict"] == "pass":
                errors.append(f"{clause}：负例 {sample_id} 期望 verdict=pass，负例被改成正例")
            elif sample["reason"] not in spec["reasons"]:
                errors.append(
                    f"{clause}：负例 {sample_id} 的 reason={sample['reason']} 不属于该子句"
                )

    for sample_id in sorted(set(samples) - referenced):
        errors.append(f"{sample_id}：样例未被任何子句引用")

    for error in errors:
        print(f"[错误] {error}")
    print(
        f"覆盖矩阵：子句 {len(clauses)}，矩阵条目 {len(entries)}，"
        f"正例 {positives}，负例 {negatives}，样例 {len(samples)}，问题 {len(errors)}"
    )
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
