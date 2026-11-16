#!/usr/bin/env python3
"""配置解释器：按 CFG-01～CFG-15 求值，不设默认、不关闭检查（批次 0095）。

职责边界（`spec/D6_REBASELINE_PROPOSAL.md` 9.1–9.4）：

- 只消费配置，不发明配置。判定性项缺失即 `cannot_evaluate`（退出码 3），
  不回落为通过；只有 CFG-10/CFG-11 允许取 schema 里的默认值，并在
  `config_used.defaulted` 中登记。
- 结构性错误（类型、越界、未注册键、未注册摘要）→ `config_invalid`（2）；
  项间矛盾（采样口径与采样集不匹配、分档不连续等）→ `config_incomplete`（2）；
  与 `config.lock.json` 摘要不一致 → `config_drift`（1）。
- 配置只能调严或调宽：本模块不提供任何关闭检查的入口，遇到 `disable`
  类字段由 schema 拒绝。
- 采样口径（CFG-04/05/06/07/08）是“使用技能时约定”的配置项：本模块只
  按已给出的口径计算采样点，不内置任何默认周期或默认采样集。

零第三方依赖：只用标准库（`datetime`、`zoneinfo`、`fractions`）。

用法：
  python3 scripts/pm_config.py --check <config.json> [--lock <config.lock.json>]
  python3 scripts/pm_config.py --digest <config.json>
  python3 scripts/pm_config.py --sample <config.json> --start 2026-01-01 --end 2026-01-15
  python3 scripts/pm_config.py --self-check
退出码：与解释器一致（0/1/2/3/4）。
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import config_codes
from pm_schema import validate

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "contracts/schema/runtime-config.schema.json"
LOCK_SCHEMA_PATH = ROOT / "contracts/schema/runtime-config-lock.schema.json"

CFG_IDS = tuple(f"CFG-{index:02d}" for index in range(1, 16))
NON_JUDGMENTAL = ("CFG-10", "CFG-11")
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

EXIT_OK = 0
EXIT_VIOLATION = 1
EXIT_INVALID = 2
EXIT_CANNOT = 3


class ConfigUnavailable(Exception):
    """解释器自身不可用（schema 缺失、schema 非法）：退出码 4。"""


@dataclass
class ConfigState:
    path: str
    raw: dict
    config: dict
    schema: dict
    snapshot: dict
    findings: list[dict] = field(default_factory=list)
    defaulted: tuple[str, ...] = ()

    @property
    def exit_code(self) -> int:
        return exit_for_findings(self.findings)

    def has(self, *keys: str) -> bool:
        return all(key in self.config for key in keys)

    def require(self, keys: tuple[str, ...], purpose: str) -> list[dict]:
        """能力求值前的配置门槛：缺项一律 cannot_evaluate，不取默认。"""
        missing = [key for key in keys if key not in self.config]
        if not missing:
            return []
        return [
            {
                "check": "config.required",
                "status": "cannot_evaluate",
                "detail": f"{purpose} 需要 {missing}，配置未给出",
                "exit_code": EXIT_CANNOT,
            }
        ]


def _finding(code: str, detail: str) -> dict:
    return {"code": code, "detail": detail, "exit_code": config_codes.classify(code)}


def exit_for_findings(findings: list[dict]) -> int:
    """求值优先级：结构非法(2) > 漂移/矛盾(1) > 不可判定(3) > 通过(0)。

    `config_incomplete` 的退出码是 2（见 9.3），因此与结构非法同档。
    """
    codes = {item.get("code") for item in findings if item.get("code")}
    if codes & {"config_invalid", "config_incomplete"}:
        return EXIT_INVALID
    if "config_drift" in codes:
        return EXIT_VIOLATION
    if "cannot_evaluate" in codes:
        return EXIT_CANNOT
    return EXIT_OK


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigUnavailable(f"{path}：不可读取：{exc}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigUnavailable(f"{path}：不可解析：{exc}") from exc


def load_schema(path: Path) -> dict:
    return load_json(path)


def _apply_defaults(value: object, schema: dict) -> tuple[object, bool]:
    """按 schema 的 `default` 递归补足缺失子字段；返回 (值, 是否使用了默认)。"""
    used = False
    if isinstance(value, dict) and isinstance(schema.get("properties"), dict):
        result = dict(value)
        for name, child in schema["properties"].items():
            if name in result:
                filled, child_used = _apply_defaults(result[name], child)
                result[name] = filled
                used = used or child_used
            elif isinstance(child, dict) and "default" in child:
                result[name] = child["default"]
                used = True
        return result, used
    return value, used


def effective_config(raw: dict, schema: dict) -> tuple[dict, tuple[str, ...]]:
    """产出实际参与判定的配置：只有非判定性项会被补默认值。"""
    config = raw.get("config", raw)
    config = dict(config) if isinstance(config, dict) else {}
    properties = (
        schema.get("properties", {}).get("config", {}).get("properties", {})
    )
    defaulted: list[str] = []
    for key in NON_JUDGMENTAL:
        child = properties.get(key)
        if not isinstance(child, dict):
            continue
        if key not in config:
            filled, _ = _apply_defaults({}, child)
            if filled:
                config[key] = filled
                defaulted.append(key)
        else:
            filled, used = _apply_defaults(config[key], child)
            config[key] = filled
            if used:
                defaulted.append(key)
    return config, tuple(sorted(defaulted))


def _interpreter_findings(config: dict) -> list[dict]:
    """schema 覆盖不到的“项间关系”：分档连续性、采样集、刻度、科目表。"""
    findings: list[dict] = []

    # CFG-03：分档边界必须按 order 升序、无重叠、连续覆盖、标签不降级。
    bands = config.get("CFG-03", {})
    if isinstance(bands, dict) and isinstance(bands.get("boundaries"), list):
        rows = bands["boundaries"]
        ordered = sorted(rows, key=lambda row: row.get("order", 0))
        if [row.get("order") for row in ordered] != list(range(1, len(rows) + 1)):
            findings.append(_finding("config_invalid", "CFG-03.order 必须是 1..n 的排列"))
        previous_upper = None
        labels = [row.get("label") for row in ordered]
        if len(set(labels)) != len(labels):
            findings.append(_finding("config_invalid", "CFG-03 档位标签重复"))
        for index, row in enumerate(ordered):
            lower, upper = row.get("lower"), row.get("upper")
            if not isinstance(lower, (int, float)) or not isinstance(upper, (int, float)):
                continue
            if lower >= upper:
                findings.append(
                    _finding("config_invalid", f"CFG-03 第 {index + 1} 档 lower 不小于 upper")
                )
            if previous_upper is not None and abs(lower - previous_upper) > 1e-9:
                findings.append(
                    _finding(
                        "config_incomplete",
                        f"CFG-03 第 {index + 1} 档从 {lower} 开始，与上一档上界 {previous_upper} 不连续",
                    )
                )
            previous_upper = upper
        levels = config.get("CFG-02", {}).get("levels")
        if isinstance(levels, int) and levels != len(rows):
            findings.append(
                _finding(
                    "config_incomplete",
                    f"CFG-02.levels={levels} 与 CFG-03 边界数 {len(rows)} 不等",
                )
            )
        labels = config.get("CFG-02", {}).get("labels")
        if isinstance(labels, list) and [row.get("label") for row in ordered] != labels:
            findings.append(
                _finding("config_incomplete", "CFG-02.labels 与 CFG-03 逐档标签不一致")
            )

    # CFG-05：分数 ∈ (0,1]、分母 ≤10、去重升序、必含 1。
    fractions = config.get("CFG-05")
    if isinstance(fractions, list):
        if any(not (0 < value <= 1) for value in fractions):
            findings.append(_finding("config_invalid", "CFG-05 分数必须落在 (0,1]"))
        if fractions != sorted(set(fractions)):
            findings.append(_finding("config_invalid", "CFG-05 必须去重且升序"))
        if not any(abs(value - 1.0) < 1e-12 for value in fractions):
            findings.append(_finding("config_incomplete", "CFG-05 必须含 1（周期末必采）"))
        for value in fractions:
            denominator = round(1 / value) if value else 0
            if denominator < 1 or denominator > 10 or abs(value - 1 / denominator) > 1e-9:
                findings.append(
                    _finding("config_invalid", f"CFG-05 分数 {value} 的分母超过 10")
                )

    # CFG-14：刻度尺寸、标签数一致、分档连续覆盖 1..scale²。
    risk = config.get("CFG-14")
    if isinstance(risk, dict):
        size = {"3x3": 3, "5x5": 5}.get(risk.get("scale"))
        if size is not None:
            if len(risk.get("probability_labels", [])) != size:
                findings.append(_finding("config_incomplete", "CFG-14 概率标签数与刻度不符"))
            if len(risk.get("impact_labels", [])) != size:
                findings.append(_finding("config_incomplete", "CFG-14 影响标签数与刻度不符"))
            bands = risk.get("bands", [])
            ordered = sorted(bands, key=lambda row: row.get("order", 0))
            if [row.get("order") for row in ordered] != list(range(1, len(bands) + 1)):
                findings.append(_finding("config_invalid", "CFG-14.bands.order 必须是 1..n"))
            previous = 0
            for row in ordered:
                lower, upper = row.get("lower"), row.get("upper")
                if isinstance(lower, int) and lower != previous + 1:
                    findings.append(
                        _finding("config_incomplete", "CFG-14 分档未连续覆盖评分区间")
                    )
                if isinstance(upper, int):
                    previous = upper
            if previous != size * size:
                findings.append(
                    _finding(
                        "config_incomplete",
                        f"CFG-14 分档上界 {previous} 未覆盖 {size * size}",
                    )
                )

    # CFG-15：编码唯一、父科目存在、无环。
    ledger = config.get("CFG-15")
    if isinstance(ledger, dict) and isinstance(ledger.get("accounts"), list):
        accounts = ledger["accounts"]
        codes = [item.get("code") for item in accounts if isinstance(item, dict)]
        duplicates = sorted({code for code in codes if codes.count(code) > 1})
        if duplicates:
            findings.append(_finding("config_invalid", f"CFG-15 科目编码重复：{duplicates}"))
        parents = {
            item.get("code"): item.get("parent_code")
            for item in accounts
            if isinstance(item, dict)
        }
        for code, parent in parents.items():
            if parent is not None and parent not in parents:
                findings.append(
                    _finding("config_invalid", f"CFG-15 上级科目不存在：{code} → {parent}")
                )
        for code in parents:
            seen = {code}
            cursor = parents.get(code)
            while cursor is not None:
                if cursor in seen:
                    findings.append(_finding("config_invalid", f"CFG-15 科目表成环：{code}"))
                    break
                seen.add(cursor)
                cursor = parents.get(cursor)

    # CFG-08：节假日区间合法、时区存在。
    calendar = config.get("CFG-08")
    if isinstance(calendar, dict):
        for item in calendar.get("holidays", []):
            if isinstance(item, dict) and item.get("from", "") > item.get("to", ""):
                findings.append(_finding("config_invalid", "CFG-08 节假日 from 晚于 to"))
        try:
            ZoneInfo(calendar.get("timezone", ""))
        except (ZoneInfoNotFoundError, ValueError):
            findings.append(
                _finding("config_invalid", f"CFG-08 时区不可用：{calendar.get('timezone')}")
            )
    return findings


def evaluate(
    config_path: Path,
    lock_path: Path | None = None,
    schema_path: Path = SCHEMA_PATH,
) -> ConfigState:
    """加载并求值配置；结构性失败也返回状态，由调用方按退出码分流。"""
    schema = load_schema(schema_path)
    raw = load_json(config_path)
    lock = load_json(lock_path) if lock_path is not None else None
    findings: list[dict] = []

    for error in validate(raw, schema):
        path = str(error.get("path", ""))
        # 判定性项缺失按 9.1 归 cannot_evaluate（3），不按“缺槽=输入非法”（2）处理。
        if error.get("message") == "必填字段缺失" and path.startswith("$.config."):
            if path.rsplit(".", 1)[-1] in config_codes.JUDGMENTAL_REQUIRED:
                continue
        findings.append(_finding("config_invalid", f"{path}：{error['message']}"))

    config, defaulted = effective_config(raw, schema)
    findings.extend(
        item
        for item in config_codes.config_findings(config, lock, schema)
        if item.get("code")
    )
    findings.extend(_interpreter_findings(config))
    # 同一缺陷可能被结构分类与项间关系各报一次，按 (类别, 说明) 去重。
    unique: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for item in findings:
        key = (item.get("code"), item.get("detail"))
        if key in seen:
            continue
        seen.add(key)
        item["exit_code"] = config_codes.EXIT_BY_CLASS[item["code"]]
        unique.append(item)

    snapshot = config_codes.build_snapshot(config, defaulted)
    return ConfigState(
        path=str(config_path),
        raw=raw,
        config=config,
        schema=schema,
        snapshot=snapshot,
        findings=unique,
        defaulted=defaulted,
    )


def comparability(left: dict, right: dict) -> dict:
    """按 9.4 比较两份配置快照：摘要不同即 `incomparable`。"""
    left_items = left.get("item_digests", {})
    right_items = right.get("item_digests", {})
    differing = sorted(
        key
        for key in set(left_items) | set(right_items)
        if left_items.get(key) != right_items.get(key)
    )
    return {
        "comparable": not differing,
        "differing": differing,
        "defaulted": sorted(set(left.get("defaulted", [])) | set(right.get("defaulted", []))),
        "config_digest_left": left.get("config_digest"),
        "config_digest_right": right.get("config_digest"),
    }


def _parse_moment(text: str, tz: ZoneInfo) -> datetime:
    try:
        if len(text) == 10:
            return datetime.combine(date.fromisoformat(text), datetime.min.time(), tz)
        moment = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return moment if moment.tzinfo else moment.replace(tzinfo=tz)
    except ValueError as exc:
        raise ValueError(f"不可解析的时间：{text}") from exc


def _calendar(calendar: dict, start: date, end: date) -> tuple[list[date], set[str]]:
    holidays: set[str] = set()
    for item in calendar.get("holidays", []):
        cursor = date.fromisoformat(item["from"])
        last = date.fromisoformat(item["to"])
        while cursor <= last:
            holidays.add(cursor.isoformat())
            cursor += timedelta(days=1)
    days = []
    cursor = start
    while cursor <= end:
        days.append(cursor)
        cursor += timedelta(days=1)
    return days, holidays


def sample_points(start: str, end: str, config: dict) -> dict:
    """按 CFG-04/05/06/07/08 计算采样点；缺配置即抛 `RuntimeError`（映射为 3）。"""
    required = ("CFG-04", "CFG-08")
    missing = [key for key in required if key not in config]
    if missing:
        raise RuntimeError(f"采样需要 {missing}，配置未给出")
    calendar = config["CFG-08"]
    tz = ZoneInfo(calendar["timezone"])
    first = _parse_moment(start, tz)
    last = _parse_moment(end, tz)
    if last < first:
        raise ValueError("采样区间的终点早于起点")
    workdays = set(calendar.get("workdays", WEEKDAYS))
    days, holidays = _calendar(calendar, first.date(), last.date())
    eligible = [
        day for day in days if WEEKDAYS[day.weekday()] in workdays and day.isoformat() not in holidays
    ]
    if not eligible:
        raise RuntimeError("采样区间内没有符合项目日历的采样日")
    mode = config["CFG-04"]

    def stamp(day: date) -> str:
        return datetime.combine(day, first.time(), tz).isoformat()

    points: list[dict] = []
    if mode == "milestone_fraction":
        basis = config.get("CFG-06")
        if basis is None:
            raise RuntimeError("CFG-04=milestone_fraction 需要 CFG-06")
        domain = eligible if basis == "workday" else days
        total = len(domain)
        for fraction in config.get("CFG-05", []):
            index = max(1, math.ceil(fraction * total))
            points.append(
                {"label": f"{round(fraction * 100)}%", "at": stamp(domain[index - 1])}
            )
    else:
        step = config.get("CFG-07")
        if not isinstance(step, dict):
            raise RuntimeError("固定间隔采样需要 CFG-07")
        unit, size = step["unit"], step["n"]
        cursor = first
        while cursor <= last:
            if WEEKDAYS[cursor.date().weekday()] in workdays:
                points.append({"label": f"{size}{unit}", "at": cursor.isoformat()})
            if unit == "hour":
                cursor += timedelta(hours=size)
            elif unit == "day":
                cursor += timedelta(days=size)
            elif unit == "week":
                cursor += timedelta(weeks=size)
            else:
                month_index = cursor.month - 1 + size
                year = cursor.year + month_index // 12
                month = month_index % 12 + 1
                day = min(cursor.day, 28)
                cursor = cursor.replace(year=year, month=month, day=day)
    return {"mode": mode, "points": points}


def band_for(value: float, config: dict) -> dict:
    """按 CFG-03 把偏差点映射为状态标签；不在覆盖区间即 `cannot_evaluate`。"""
    bands = config.get("CFG-03", {}).get("boundaries", [])
    for row in sorted(bands, key=lambda item: item.get("order", 0)):
        if row["lower"] <= value <= row["upper"]:
            return {"status": "pass", "label": row["label"], "band": row["order"]}
    return {
        "status": "cannot_evaluate",
        "detail": f"偏差点 {value} 不在 CFG-03 覆盖区间内",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="运行期配置解释器")
    parser.add_argument("--check", metavar="CONFIG", help="对配置实例求值")
    parser.add_argument("--lock", metavar="LOCK", help="config.lock.json 路径")
    parser.add_argument("--digest", metavar="CONFIG", help="输出配置快照")
    parser.add_argument("--sample", metavar="CONFIG", help="计算采样点")
    parser.add_argument("--start", help="采样区间起点（YYYY-MM-DD 或 ISO 时间）")
    parser.add_argument("--end", help="采样区间终点")
    parser.add_argument("--self-check", action="store_true", help="核验配置 schema 设计约束")
    args = parser.parse_args(argv)

    if args.self_check:
        return config_codes.main(["--self-check"])
    try:
        if args.digest:
            state = evaluate(Path(args.digest), Path(args.lock) if args.lock else None)
            print(json.dumps(state.snapshot, ensure_ascii=False, indent=2, sort_keys=True))
            return state.exit_code
        if args.check:
            state = evaluate(Path(args.check), Path(args.lock) if args.lock else None)
            print(json.dumps(state.findings, ensure_ascii=False, indent=2, sort_keys=True))
            return state.exit_code
        if args.sample:
            if not args.start or not args.end:
                print("[错误] --sample 需要 --start 与 --end")
                return EXIT_INVALID
            state = evaluate(Path(args.sample))
            if state.exit_code in (EXIT_INVALID, EXIT_VIOLATION):
                print(json.dumps(state.findings, ensure_ascii=False, indent=2))
                return state.exit_code
            print(json.dumps(sample_points(args.start, args.end, state.config), ensure_ascii=False, indent=2))
            return EXIT_OK
    except ConfigUnavailable as exc:
        print(f"[错误] 配置解释器不可用：{exc}")
        return 4
    except (RuntimeError, ValueError) as exc:
        print(f"[不可判定] {exc}")
        return EXIT_CANNOT
    parser.print_help()
    return EXIT_INVALID


if __name__ == "__main__":
    sys.exit(main())
