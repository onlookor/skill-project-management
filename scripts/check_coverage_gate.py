#!/usr/bin/env python3
"""覆盖闸门：A.2 每个子句至少 1 个正例 + 1 个负例，且用**生产路径**取证归属。

覆盖矩阵登记在 validation/checker-prototype/coverage.json：
  clause id -> {check_id, positive: [样例编号],
                negative: [{sample, expected_clause}]}
  global_normalization -> [{sample, check_id, expected_verdict,
                            expected_reason, expected_clause: null}]

核对项：
  1. 矩阵必须与 A.2 的子句集合完全一致（缺条目、多余条目都阻断）；
  2. 每个子句至少 1 个正例、1 个负例，缺一即阻断；
  3. 正例：样例存在、check_id 一致、期望 verdict=pass，且生产路径确实 pass；
  4. 负例：必须声明单一 `expected_clause`，且与所在子句一致；生产路径
     `evaluate_trace()` 的 verdict/reason 必须与样例期望一致、归属子句必须
     命中该声明。这是“归属是真的”，不是“归属非空”：
     `cannot_evaluate` 的全局归一化不得冒充某个 `fail` 子句的负例。
  5. `(reason, clause)` 登记：负例样例声明的 reason 必须出现在 A.2 该子句的
     原因码列；正例不得声明 reason。
  6. 全局归一化分区：入口归一化（必需键缺失、`null`、嵌套缺键）与无子句的
     全局枚举样例登记在此，声明 `expected_clause: null`，由生产路径核对
     verdict/reason；这类样例不挂子句，但必须被本分区消费。
  7. 每个样例必须被子句或全局归一化分区之一引用（防止用未登记样例充数）；
     同一编号不得同时出现在两处。

用法：python3 scripts/check_coverage_gate.py [--root DIR] [--method FILE] [--manifest FILE]
退出码：0 = 覆盖矩阵合格；1 = 存在缺口；2 = 解析失败或无法加载原型。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

METHOD = Path("spec/methods/deterministic-checker.md")
MANIFEST = Path("validation/checker-prototype/coverage.json")
PROTOTYPE = Path("validation/checker-prototype")


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
    """从 A.1 解析样例编号 -> {check_id, verdict, reason, input}。"""
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


def load_prototype(root: Path):
    """加载原型 checker，用它的生产路径求值结果做子句级核对。"""
    prototype = str((root / PROTOTYPE).resolve())
    if prototype not in sys.path:
        sys.path.insert(0, prototype)
    import checker  # noqa: PLC0415 - 依赖 --root 动态定位

    return checker


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
        text = method_path.read_text(encoding="utf-8")
        clauses = parse_clauses(text)
        samples = parse_samples(text)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        checker = load_prototype(root)
        checker_cases = {
            f"{case['section']}-{case['case']}": case
            for case in checker.extract_cases(text)
        }
    except (OSError, ValueError, json.JSONDecodeError, ImportError) as exc:
        print(f"[错误] 解析失败：{exc}")
        return 2
    entries = manifest.get("clauses", {})
    globals_ = manifest.get("global_normalization", [])

    errors: list[str] = []
    missing = sorted(set(clauses) - set(entries))
    extra = sorted(set(entries) - set(clauses))
    for clause in missing:
        errors.append(f"{clause}：矩阵缺少条目")
    for clause in extra:
        errors.append(f"{clause}：矩阵存在 A.2 未定义的子句")

    clause_referenced: set[str] = set()
    positives = 0
    negatives = 0
    for clause, spec in clauses.items():
        entry = entries.get(clause)
        if entry is None:
            continue
        check_id = spec["check_id"]
        if entry.get("check_id") != check_id:
            errors.append(
                f"{clause}：矩阵 check_id={entry.get('check_id')} 与 A.2={check_id} 不一致"
            )
        positive = entry.get("positive") or []
        negative = entry.get("negative") or []
        if not positive:
            errors.append(f"{clause}：缺少正例")
        if not negative:
            errors.append(f"{clause}：缺少负例")
        for sample_id in positive:
            clause_referenced.add(sample_id)
            sample = samples.get(sample_id)
            if sample is None:
                errors.append(f"{clause}：正例 {sample_id} 不存在")
                continue
            positives += 1
            if sample["check_id"] != check_id:
                errors.append(f"{clause}：正例 {sample_id} 的 check_id 不匹配")
            if sample["verdict"] != "pass" or sample["reason"] is not None:
                errors.append(
                    f"{clause}：正例 {sample_id} 期望 verdict={sample['verdict']} / "
                    f"reason={sample['reason']}，不是无 reason 的 pass"
                )
            trace = _trace(checker, checker_cases, sample_id, check_id, clause, errors)
            if trace is not None and trace["verdict"] != "pass":
                errors.append(
                    f"{clause}：正例 {sample_id} 生产路径返回 {trace['verdict']}/"
                    f"{trace['reason']}，不是 pass"
                )
        for item in negative:
            if not isinstance(item, dict):
                errors.append(f"{clause}：负例 {item} 必须声明 sample 与 expected_clause")
                clause_referenced.add(str(item))
                continue
            sample_id = item.get("sample")
            declared = item.get("expected_clause")
            clause_referenced.add(sample_id or "")
            sample = samples.get(sample_id)
            if sample is None:
                errors.append(f"{clause}：负例 {sample_id} 不存在")
                continue
            negatives += 1
            if not isinstance(declared, str) or not declared:
                errors.append(f"{clause}：负例 {sample_id} 缺少 expected_clause")
                continue
            if declared != clause:
                errors.append(
                    f"{clause}：负例 {sample_id} 声明的子句 {declared} 与所在条目不一致"
                )
            if sample["check_id"] != check_id:
                errors.append(f"{clause}：负例 {sample_id} 的 check_id 不匹配")
            if sample["verdict"] == "pass":
                errors.append(f"{clause}：负例 {sample_id} 期望 verdict=pass，负例被改成正例")
            if sample["reason"] is None:
                errors.append(f"{clause}：负例 {sample_id} 未声明 reason，无法核对登记")
            elif sample["reason"] not in spec["reasons"]:
                errors.append(
                    f"{clause}：负例 {sample_id} 的 reason={sample['reason']} "
                    f"未登记在该子句的 A.2 原因码列 {sorted(spec['reasons'])}"
                )
            trace = _trace(checker, checker_cases, sample_id, check_id, clause, errors)
            if trace is None:
                continue
            if trace["verdict"] != sample["verdict"] or trace["reason"] != sample["reason"]:
                errors.append(
                    f"{clause}：负例 {sample_id} 生产路径返回 "
                    f"{trace['verdict']}/{trace['reason']}，与样例期望 "
                    f"{sample['verdict']}/{sample['reason']} 不一致"
                )
            if trace["clause"] != declared:
                errors.append(
                    f"{clause}：负例 {sample_id} 生产路径触发 {trace['clause']}，"
                    f"未命中声明的 {declared}"
                )

    global_referenced: set[str] = set()
    global_count = 0
    for item in globals_:
        if not isinstance(item, dict):
            errors.append(f"全局归一化条目 {item} 必须是对象")
            continue
        sample_id = item.get("sample")
        global_referenced.add(sample_id or "")
        sample = samples.get(sample_id)
        if sample is None:
            errors.append(f"全局归一化：样例 {sample_id} 不存在")
            continue
        global_count += 1
        check_id = item.get("check_id")
        if sample["check_id"] != check_id:
            errors.append(f"全局归一化：样例 {sample_id} 的 check_id 与登记不一致")
            continue
        if item.get("expected_clause") is not None:
            errors.append(f"全局归一化：样例 {sample_id} 的 expected_clause 必须为 null")
        expected_verdict = item.get("expected_verdict")
        expected_reason = item.get("expected_reason")
        trace = _trace(checker, checker_cases, sample_id, check_id, "全局归一化", errors)
        if trace is None:
            continue
        if trace["verdict"] != expected_verdict or trace["reason"] != expected_reason:
            errors.append(
                f"全局归一化：样例 {sample_id} 生产路径返回 "
                f"{trace['verdict']}/{trace['reason']}，与登记 "
                f"{expected_verdict}/{expected_reason} 不一致"
            )
        if trace["clause"] is not None:
            errors.append(
                f"全局归一化：样例 {sample_id} 生产路径归属 {trace['clause']}，"
                "应改登记在对应子句下"
            )

    for sample_id in sorted(clause_referenced & global_referenced):
        errors.append(f"{sample_id}：同时登记在子句与全局归一化分区")

    referenced = clause_referenced | global_referenced
    for sample_id in sorted(set(samples) - referenced):
        errors.append(f"{sample_id}：样例未被任何子句或全局归一化条目引用")

    for error in errors:
        print(f"[错误] {error}")
    print(
        f"覆盖矩阵：子句 {len(clauses)}，矩阵条目 {len(entries)}，"
        f"正例 {positives}，负例 {negatives}，全局归一化 {global_count}，"
        f"样例 {len(samples)}，问题 {len(errors)}"
    )
    return 0 if not errors else 1


def _trace(
    checker,
    checker_cases: dict,
    sample_id: str,
    check_id: str,
    label: str,
    errors: list[str],
) -> dict | None:
    """用生产 evaluate_trace() 取证；样例无法解析时记错并返回 None。"""
    case = checker_cases.get(sample_id)
    if case is None:
        errors.append(f"{label}：{sample_id} 无法被原型解析")
        return None
    return checker.evaluate_trace(check_id, case["input"] or {})


if __name__ == "__main__":
    sys.exit(main())
