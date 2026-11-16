#!/usr/bin/env python3
"""七项机械能力的实现与检查注册表（批次 0095）。

能力与来源缺口编号（`spec/D6_REBASELINE_PROPOSAL.md` 8.3）：

| 能力 | CAP | RG | 本模块落点 |
|---|---|---|---|
| 依赖图 | CAP-13 / CAP-15 | RG-06 | `CHECK_REGISTRY` 的 `dep.*`、`schedule.critical_path`；`COMPUTE_REGISTRY["schedule.cpm"]` |
| 预算汇总 | CAP-19 | RG-07 | `budget.*`；`COMPUTE_REGISTRY["budget.rollup"]` |
| 风险登记册 | CAP-25 / CAP-23 | RG-08 | `risk.*`；`COMPUTE_REGISTRY["risk.ranking"]` |
| 状态采集 | CAP-35 | RG-09 | `status.*`；`COMPUTE_REGISTRY["status.collect"]` |
| 偏差阈值 | CAP-16 | RG-10 | `deviation.*`；`COMPUTE_REGISTRY["deviation.map"]` |
| 挣值 | CAP-20 | RG-11 | `evm.*`；`COMPUTE_REGISTRY["evm.metrics"]` |
| 审计留痕 | CAP-42 | RG-12 | `audit.*`；`COMPUTE_REGISTRY["audit.append"]` |

边界（与提案一致）：

- 阈值、采样口径、刻度、成本科目一律从配置读取，本模块不内置默认值；
  配置缺项时对应检查返回 `cannot_evaluate`，不回落到“通过”。
- 只能机械判定的部分在此实现；语义好坏（拆法是否合理、风险识别是否穷尽）
  不在本模块，由人类签字或外复核承接。
- 每个检查返回 `{check, status, detail, path}`；`status` 取
  `pass` / `violation` / `cannot_evaluate`。

零第三方依赖：只用标准库。
"""

from __future__ import annotations

import hashlib
import json
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

from pm_config import band_for, sample_points
from pm_schema import canonical_bytes

PASS = "pass"
VIOLATION = "violation"
CANNOT = "cannot_evaluate"


def _finding(check: str, status: str, detail: str, path: str = "") -> dict:
    return {"check": check, "status": status, "detail": detail, "path": path}


def _ok(check: str, detail: str = "通过", path: str = "") -> dict:
    return _finding(check, PASS, detail, path)


def _bad(check: str, detail: str, path: str = "") -> dict:
    return _finding(check, VIOLATION, detail, path)


def _unknown(check: str, detail: str, path: str = "") -> dict:
    return _finding(check, CANNOT, detail, path)


def _require_config(check: str, config: dict, keys: tuple[str, ...], purpose: str):
    missing = [key for key in keys if key not in config]
    if missing:
        return _unknown(check, f"{purpose} 需要 {missing}，配置未给出")
    return None


def _round(value: float, config: dict) -> float:
    """按 CFG-10 舍入；缺项时判定层已返回 cannot_evaluate，这里不会走到。"""
    settings = config.get("CFG-10") or {}
    decimals = settings.get("decimals", 2)
    rounding = ROUND_HALF_UP if settings.get("rounding") == "half_up" else ROUND_HALF_EVEN
    quantum = Decimal(1).scaleb(-int(decimals))
    return float(Decimal(repr(float(value))).quantize(quantum, rounding=rounding))


# ---------------------------------------------------------------- 依赖图


def _topological(data: dict) -> tuple[list[str], set[str]]:
    """Kahn 拓扑排序；返回 (顺序, 参与环的节点)。"""
    ids = [item["id"] for item in data.get("activities", [])]
    indegree = {key: 0 for key in ids}
    outgoing: dict[str, list[str]] = {key: [] for key in ids}
    for dep in data.get("dependencies", []):
        if dep["from"] in indegree and dep["to"] in indegree:
            outgoing[dep["from"]].append(dep["to"])
            indegree[dep["to"]] += 1
    ready = sorted(key for key, count in indegree.items() if count == 0)
    order: list[str] = []
    while ready:
        node = ready.pop(0)
        order.append(node)
        for child in outgoing[node]:
            indegree[child] -= 1
            if indegree[child] == 0:
                ready.append(child)
        ready.sort()
    cyclic = {key for key, count in indegree.items() if count > 0}
    return order, cyclic


def compute_cpm(data: dict) -> dict:
    """四类逻辑关系的前推/后推；返回关键路径与总浮时。

    只按活动间逻辑关系计算，不引入日历单位换算（`duration_days` 为口径单位）。
    存在环时返回 `{"status": "cannot_evaluate"}`，由调用方转成结论。
    """
    for dep in data.get("dependencies", []):
        if "lag" not in dep:
            return {
                "status": CANNOT,
                "detail": (
                    f"依赖 {dep.get('from')}→{dep.get('to')} 未给出 lag，"
                    "无法区分“无滞后”与“滞后期为 0”"
                ),
            }
    order, cyclic = _topological(data)
    if cyclic:
        return {"status": CANNOT, "detail": f"依赖图成环：{sorted(cyclic)}"}
    activities = {item["id"]: item for item in data["activities"]}
    incoming: dict[str, list[dict]] = {key: [] for key in activities}
    outgoing: dict[str, list[dict]] = {key: [] for key in activities}
    for dep in data.get("dependencies", []):
        if dep["from"] in activities and dep["to"] in activities:
            incoming[dep["to"]].append(dep)
            outgoing[dep["from"]].append(dep)

    es = {key: 0.0 for key in activities}
    ef = {key: float(activities[key]["duration_days"]) for key in activities}
    for node in order:
        duration = float(activities[node]["duration_days"])
        for dep in incoming[node]:
            lag = float(dep["lag"])
            kind = dep["type"]
            if kind == "FS":
                es[node] = max(es[node], ef[dep["from"]] + lag)
            elif kind == "SS":
                es[node] = max(es[node], es[dep["from"]] + lag)
            elif kind == "FF":
                es[node] = max(es[node], ef[dep["from"]] + lag - duration)
            else:  # SF
                es[node] = max(es[node], es[dep["from"]] + lag - duration)
        ef[node] = es[node] + duration

    finish = max(ef.values()) if ef else 0.0
    ls = {key: finish for key in activities}
    lf = {key: finish for key in activities}
    for node in reversed(order):
        duration = float(activities[node]["duration_days"])
        for dep in outgoing[node]:
            lag = float(dep["lag"])
            kind = dep["type"]
            child = dep["to"]
            if kind == "FS":
                lf[node] = min(lf[node], ls[child] - lag)
            elif kind == "SS":
                ls[node] = min(ls[node], ls[child] - lag)
            elif kind == "FF":
                lf[node] = min(lf[node], lf[child] - lag)
            else:  # SF
                ls[node] = min(ls[node], lf[child] - lag)
        ls[node] = min(ls[node], lf[node] - duration)

    rows = {}
    for node in order:
        total_float = round(ls[node] - es[node], 6)
        rows[node] = {
            "es": round(es[node], 6),
            "ef": round(ef[node], 6),
            "ls": round(ls[node], 6),
            "lf": round(lf[node], 6),
            "total_float": total_float,
            "critical": abs(total_float) < 1e-9,
        }
    critical_path = [node for node in order if rows[node]["critical"]]
    return {
        "status": PASS,
        "project_duration": round(finish, 6),
        "activities": rows,
        "critical_path": critical_path,
        "topological_order": order,
    }


def _check_dep_ids_unique(data: dict, ctx: dict) -> list[dict]:
    ids = [item["id"] for item in data.get("activities", [])]
    duplicates = sorted({key for key in ids if ids.count(key) > 1})
    if duplicates:
        return [_bad("dep.ids_unique", f"活动 id 重复：{duplicates}")]
    return [_ok("dep.ids_unique", f"{len(ids)} 个活动 id 唯一")]


def _check_dep_endpoints(data: dict, ctx: dict) -> list[dict]:
    ids = {item["id"] for item in data.get("activities", [])}
    dangling = [
        f"{dep['from']}→{dep['to']}"
        for dep in data.get("dependencies", [])
        if dep["from"] not in ids or dep["to"] not in ids
    ]
    if dangling:
        return [_bad("dep.endpoints_exist", f"悬挂依赖：{dangling}")]
    return [_ok("dep.endpoints_exist", f"{len(data.get('dependencies', []))} 条依赖端点闭合")]


def _check_dep_acyclic(data: dict, ctx: dict) -> list[dict]:
    _, cyclic = _topological(data)
    if cyclic:
        return [_bad("dep.acyclic", f"存在环：{sorted(cyclic)}")]
    return [_ok("dep.acyclic", "DAG 无环")]


def _check_dep_types(data: dict, ctx: dict) -> list[dict]:
    wrong = [
        f"{dep['from']}→{dep['to']}:{dep.get('type')}"
        for dep in data.get("dependencies", [])
        if dep.get("type") not in ("FS", "SS", "FF", "SF")
    ]
    if wrong:
        return [_bad("dep.types_valid", f"非法逻辑关系：{wrong}")]
    return [_ok("dep.types_valid", "依赖类型均在 FS/SS/FF/SF 内")]


def _check_dep_wbs(data: dict, ctx: dict) -> list[dict]:
    nodes = data.get("wbs_node_ids")
    if not nodes:
        return [_unknown("dep.wbs_mapping", "未注入 WBS 节点清单，活动↔工作包映射无法判定")]
    missing = sorted(
        {item["wbs_ref"] for item in data.get("activities", []) if item["wbs_ref"] not in nodes}
    )
    if missing:
        return [_bad("dep.wbs_mapping", f"活动引用不存在的 WBS 节点：{missing}")]
    return [_ok("dep.wbs_mapping", "活动↔工作包映射完整")]


def _check_schedule_critical(data: dict, ctx: dict) -> list[dict]:
    result = compute_cpm(data)
    if result["status"] != PASS:
        return [_unknown("schedule.critical_path", result["detail"])]
    findings = [
        _ok(
            "schedule.critical_path",
            f"总工期 {result['project_duration']}；关键活动 {result['critical_path']}",
        )
    ]
    rows = result["activities"]
    for activity in data.get("activities", []):
        due = activity.get("due_day")
        if due is not None and rows[activity["id"]]["ef"] > float(due) + 1e-9:
            findings.append(
                _bad(
                    "schedule.critical_path",
                    f"里程碑 {activity['id']} 最早完成 {rows[activity['id']]['ef']} 晚于期限 {due}",
                    f"activities.{activity['id']}.due_day",
                )
            )
    return findings


# ---------------------------------------------------------------- 预算汇总


def _account_map(config: dict) -> dict[str, str | None]:
    ledger = config.get("CFG-15") or {}
    return {
        item["code"]: item.get("parent_code")
        for item in ledger.get("accounts", [])
        if isinstance(item, dict) and "code" in item
    }


def _account_depths(accounts: dict[str, str | None]) -> dict[str, int]:
    """按 parent 链计算每个科目的深度；成环时停在已见节点（配置层已判非法）。"""
    depths: dict[str, int] = {}
    for code in accounts:
        depth, seen, cursor = 0, {code}, accounts.get(code)
        while cursor is not None and cursor not in seen:
            seen.add(cursor)
            depth += 1
            cursor = accounts.get(cursor)
        depths[code] = depth
    return depths


def compute_budget(data: dict, config: dict) -> dict:
    """按成本科目树与 WBS 双向汇总；科目树来自 CFG-15。"""
    accounts = _account_map(config)
    by_wbs: dict[str, float] = {}
    by_period: dict[str, float] = {}
    direct: dict[str, float] = {code: 0.0 for code in accounts}
    for package in data.get("work_packages", []):
        amount = float(package["amount"])
        by_wbs[package["wbs_ref"]] = by_wbs.get(package["wbs_ref"], 0.0) + amount
        code = package.get("account_code")
        if code in direct:
            direct[code] += amount
        for period in package.get("periods", []):
            by_period[period["period"]] = by_period.get(period["period"], 0.0) + float(
                period["amount"]
            )
    rolled = dict(direct)
    # 深度降序上卷：叶子先于父节点处理，父节点被累加时其子树已完整。
    # 单趟按“(是否根, code)”排序不够——A←B←C 时 B 可能排在 C 之前。
    depths = _account_depths(accounts)
    for code in sorted(accounts, key=lambda item: (-depths[item], item)):
        parent = accounts[code]
        if parent in rolled:
            rolled[parent] += rolled[code]
    return {
        "total": round(sum(by_wbs.values()), 6),
        "by_account": {key: round(value, 6) for key, value in sorted(rolled.items())},
        "by_account_direct": {key: round(value, 6) for key, value in sorted(direct.items())},
        "by_wbs": {key: round(value, 6) for key, value in sorted(by_wbs.items())},
        "by_period": {key: round(value, 6) for key, value in sorted(by_period.items())},
        "period_total": round(sum(by_period.values()), 6),
    }


def _check_budget_accounts(data: dict, ctx: dict) -> list[dict]:
    blocked = _require_config("budget.accounts_registered", ctx["config"], ("CFG-15",), "科目表核对")
    if blocked:
        return [blocked]
    accounts = _account_map(ctx["config"])
    missing = sorted(
        {
            package["account_code"]
            for package in data.get("work_packages", [])
            if package.get("account_code") not in accounts
        }
    )
    if missing:
        return [_bad("budget.accounts_registered", f"未登记成本科目：{missing}")]
    return [_ok("budget.accounts_registered", "全部工作包科目均在 CFG-15 内")]


def _check_budget_unique(data: dict, ctx: dict) -> list[dict]:
    ids = [item["id"] for item in data.get("work_packages", [])]
    duplicates = sorted({key for key in ids if ids.count(key) > 1})
    if duplicates:
        return [_bad("budget.package_unique", f"工作包 id 重复：{duplicates}")]
    return [_ok("budget.package_unique", f"{len(ids)} 个工作包 id 唯一")]


def _subtree_expected(
    accounts: dict[str, str | None], direct: dict[str, float]
) -> dict[str, float]:
    """按子树递归求每个科目的应有金额（与上卷实现独立，用于交叉核验）。"""
    children: dict[str | None, list[str]] = {}
    for code, parent in accounts.items():
        children.setdefault(parent, []).append(code)
    memo: dict[str, float] = {}

    def total(code: str) -> float:
        if code not in memo:
            memo[code] = direct.get(code, 0.0) + sum(
                total(child) for child in children.get(code, [])
            )
        return memo[code]

    return {code: total(code) for code in accounts}


def _check_budget_total(data: dict, ctx: dict) -> list[dict]:
    rollup = compute_budget(data, ctx["config"])
    findings: list[dict] = []
    # 每个节点单独核对：总数相等不代表父节点正确（A←B←C 曾出现 A=0）。
    accounts = _account_map(ctx["config"])
    if accounts:
        expected = _subtree_expected(accounts, rollup["by_account_direct"])
        wrong = [
            code
            for code in accounts
            if abs(rollup["by_account"].get(code, 0.0) - expected[code]) > 1e-6
        ]
        if wrong:
            findings.append(
                _bad(
                    "budget.total_conserved",
                    f"科目汇总与子树合计不等：{sorted(wrong)}（总数相等不覆盖单节点）",
                )
            )
    if rollup["period_total"] == 0:
        findings.append(
            _unknown("budget.total_conserved", "未提供分时段预算，总额守恒无法判定")
        )
    elif abs(rollup["period_total"] - rollup["total"]) > 1e-6:
        findings.append(
            _bad(
                "budget.total_conserved",
                f"分时段合计 {rollup['period_total']} 与工作包合计 {rollup['total']} 不等",
            )
        )
    evm = ctx["artifacts"].get("evm_record")
    if isinstance(evm, dict) and "bac" in evm:
        if abs(float(evm["bac"]) - rollup["total"]) > 1e-6:
            findings.append(
                _bad(
                    "budget.total_conserved",
                    f"预算合计 {rollup['total']} 与挣值基线 BAC {evm['bac']} 不等",
                )
            )
    if findings:
        return findings
    return [_ok("budget.total_conserved", f"每个科目与总额均守恒，合计 {rollup['total']}")]


def _check_budget_periods(data: dict, ctx: dict) -> list[dict]:
    mismatched = []
    for package in data.get("work_packages", []):
        periods = package.get("periods")
        if not periods:
            mismatched.append(package["id"])
            continue
        if abs(sum(float(item["amount"]) for item in periods) - float(package["amount"])) > 1e-6:
            mismatched.append(package["id"])
    if mismatched:
        return [
            _bad(
                "budget.time_phased_sum",
                f"分时段金额与工作包金额不一致或缺分时段：{mismatched}",
            )
        ]
    return [_ok("budget.time_phased_sum", "每个工作包的分时段金额之和等于总额")]


def _check_budget_currency(data: dict, ctx: dict) -> list[dict]:
    blocked = _require_config("budget.currency_match", ctx["config"], ("CFG-09",), "货币核对")
    if blocked:
        return [blocked]
    if data.get("currency") != ctx["config"]["CFG-09"]:
        return [
            _bad(
                "budget.currency_match",
                f"工件货币 {data.get('currency')} 与 CFG-09={ctx['config']['CFG-09']} 不一致",
            )
        ]
    return [_ok("budget.currency_match", "货币与 CFG-09 一致")]


# ---------------------------------------------------------------- 风险登记册


def _risk_scale(config: dict) -> tuple[int | None, str]:
    risk = config.get("CFG-14")
    if not isinstance(risk, dict):
        return None, "CFG-14 缺失"
    size = {"3x3": 3, "5x5": 5}.get(risk.get("scale"))
    if size is None:
        return None, "CFG-14.scale 未登记"
    return size, ""


def _risk_initial_score(risk: dict, config: dict) -> tuple[int | None, str]:
    settings = config.get("CFG-14") or {}
    if settings.get("score_rule") == "matrix":
        return None, "CFG-14.score_rule=matrix，但配置未提供矩阵取值，初始评分无法计算"
    return int(risk["probability"]) * int(risk["impact"]), ""


def _check_risk_required(data: dict, ctx: dict) -> list[dict]:
    required = (
        "id",
        "category",
        "probability",
        "impact",
        "trigger",
        "response_strategy",
        "owner_role",
        "status",
        "residual_score",
        "objective_refs",
    )
    missing = [
        f"{risk.get('id', '?')}.{field}"
        for risk in data.get("risks", [])
        for field in required
        if field not in risk
    ]
    if missing:
        return [_bad("risk.required_fields", f"必填字段缺失：{sorted(set(missing))}")]
    return [_ok("risk.required_fields", f"{len(data.get('risks', []))} 条风险字段齐备")]


def _check_risk_scale(data: dict, ctx: dict) -> list[dict]:
    size, why = _risk_scale(ctx["config"])
    if size is None:
        return [_unknown("risk.scale_in_range", why)]
    bad = [
        risk["id"]
        for risk in data.get("risks", [])
        if not (1 <= int(risk["probability"]) <= size and 1 <= int(risk["impact"]) <= size)
    ]
    if bad:
        return [_bad("risk.scale_in_range", f"概率/影响超出 {size}×{size} 刻度：{bad}")]
    return [_ok("risk.scale_in_range", f"概率与影响均在 {size}×{size} 内")]


def _check_risk_residual(data: dict, ctx: dict) -> list[dict]:
    bad = []
    unknown = []
    for risk in data.get("risks", []):
        score, why = _risk_initial_score(risk, ctx["config"])
        if score is None:
            unknown.append(why)
            continue
        if int(risk["residual_score"]) > score:
            bad.append(risk["id"])
    findings = []
    if bad:
        findings.append(_bad("risk.residual_le_initial", f"残余评分高于初始评分：{bad}"))
    if unknown:
        findings.append(_unknown("risk.residual_le_initial", sorted(set(unknown))[0]))
    if not findings:
        findings.append(_ok("risk.residual_le_initial", "残余评分均不高于初始评分"))
    return findings


def _check_risk_owner(data: dict, ctx: dict) -> list[dict]:
    roles = set(data.get("roles", []))
    missing = sorted({risk["owner_role"] for risk in data.get("risks", []) if risk["owner_role"] not in roles})
    if missing:
        return [_bad("risk.owner_registered", f"责任人角色未登记：{missing}")]
    return [_ok("risk.owner_registered", "风险责任人角色均已登记")]


def _check_risk_band(data: dict, ctx: dict) -> list[dict]:
    settings = ctx["config"].get("CFG-14")
    if not isinstance(settings, dict) or not settings.get("bands"):
        return [_unknown("risk.band_consistent", "CFG-14.bands 缺失，风险分档无法判定")]
    out_of_range = []
    for risk in data.get("risks", []):
        score, why = _risk_initial_score(risk, ctx["config"])
        if score is None:
            return [_unknown("risk.band_consistent", why)]
        if band_for(float(score), {"CFG-03": {"boundaries": settings["bands"]}})["status"] != PASS:
            out_of_range.append(risk["id"])
    if out_of_range:
        return [_bad("risk.band_consistent", f"初始评分无对应分档：{out_of_range}")]
    return [_ok("risk.band_consistent", "初始评分均落在 CFG-14 分档内")]


def compute_risk(data: dict, config: dict) -> dict:
    rows = []
    for risk in data.get("risks", []):
        score, why = _risk_initial_score(risk, config)
        if score is None:
            return {"status": CANNOT, "detail": why}
        band = band_for(float(score), {"CFG-03": {"boundaries": (config.get("CFG-14") or {}).get("bands", [])}})
        rows.append(
            {
                "id": risk["id"],
                "score": score,
                "residual_score": int(risk["residual_score"]),
                "band": band.get("label"),
                "band_status": band["status"],
            }
        )
    rows.sort(key=lambda row: (-row["score"], row["id"]))
    return {"status": PASS, "ranking": rows}


# ---------------------------------------------------------------- 状态采集


def _point_key(at: str, mode: str) -> str:
    """采样时点比对粒度：小时口径比到小时，其余口径比到自然日。"""
    return at[:13] if mode == "hour" else at[:10]


def compute_status(data: dict, config: dict) -> dict:
    """按采样口径核对时点，并把每个科目/指标的最后一个有效值汇总。"""
    grid = sample_points(data["period"]["start"], data["period"]["end"], config)
    allowed = {_point_key(point["at"], grid["mode"]) for point in grid["points"]}
    latest: dict[tuple[str, str], float] = {}
    missing: list[str] = []
    for sample in data.get("samples", []):
        for item in sample.get("measurements", []):
            key = (item["account_code"], item["metric"])
            if item.get("value") is None:
                missing.append(f"{sample['id']}:{key[0]}:{key[1]}")
                continue
            latest[key] = float(item["value"])
    return {
        "status": PASS,
        "mode": grid["mode"],
        "grid": grid["points"],
        "allowed_prefixes": sorted(allowed),
        "latest": {f"{account}:{metric}": value for (account, metric), value in sorted(latest.items())},
        "missing": missing,
    }


def _check_status_dictionary(data: dict, ctx: dict) -> list[dict]:
    entries = data.get("dictionary", [])
    metrics = [entry["metric"] for entry in entries]
    duplicates = sorted({key for key in metrics if metrics.count(key) > 1})
    used = {
        item["metric"]
        for sample in data.get("samples", [])
        for item in sample.get("measurements", [])
    }
    undeclared = sorted(used - set(metrics))
    if duplicates or undeclared:
        return [
            _bad(
                "status.dictionary_fields",
                f"字典重复 {duplicates}；测量使用未登记指标 {undeclared}",
            )
        ]
    return [_ok("status.dictionary_fields", "数据字典齐备且测量指标均已登记")]


def _check_status_no_zero(data: dict, ctx: dict) -> list[dict]:
    silent = []
    for sample in data.get("samples", []):
        for item in sample.get("measurements", []):
            if "value" not in item:
                silent.append(f"{sample['id']}:{item['account_code']}:{item['metric']}")
            elif item.get("value") is None and not item.get("unavailable_reason"):
                silent.append(f"{sample['id']}:{item['account_code']}:{item['metric']}")
    if silent:
        return [
            _bad(
                "status.no_implicit_zero",
                f"缺数未显式说明（不得以空值代替）：{silent}",
            )
        ]
    return [_ok("status.no_implicit_zero", "缺数均显式登记了 unavailable_reason")]


def _check_status_grid(data: dict, ctx: dict) -> list[dict]:
    needed = ("CFG-04", "CFG-08")
    blocked = _require_config("status.sample_grid", ctx["config"], needed, "采样时点核对")
    if blocked:
        return [blocked]
    try:
        grid = sample_points(data["period"]["start"], data["period"]["end"], ctx["config"])
    except (RuntimeError, ValueError) as exc:
        return [_unknown("status.sample_grid", f"采样口径不可求值：{exc}")]
    allowed = {_point_key(point["at"], grid["mode"]) for point in grid["points"]}
    deviating = sorted(
        {
            sample["at"]
            for sample in data.get("samples", [])
            if _point_key(sample["at"], grid["mode"]) not in allowed
        }
    )
    if deviating:
        return [_bad("status.sample_grid", f"采样时点不在 CFG-04 计算的网格上：{deviating}")]
    return [_ok("status.sample_grid", f"{len(allowed)} 个采样点均与配置口径一致")]


def _check_status_account(data: dict, ctx: dict) -> list[dict]:
    blocked = _require_config("status.account_registered", ctx["config"], ("CFG-15",), "科目核对")
    if blocked:
        return [blocked]
    accounts = _account_map(ctx["config"])
    missing = sorted(
        {
            item["account_code"]
            for sample in data.get("samples", [])
            for item in sample.get("measurements", [])
            if item["account_code"] not in accounts
        }
    )
    if missing:
        return [_bad("status.account_registered", f"测量引用未登记科目：{missing}")]
    return [_ok("status.account_registered", "测量科目均在 CFG-15 内")]


# ---------------------------------------------------------------- 偏差阈值


def _deviation_values(evm: dict, config: dict) -> tuple[list[dict], str]:
    # metric 是判定性项：不回落 SPI，未给出即无法判定。
    metric = (config.get("CFG-03") or {}).get("metric")
    if metric not in ("SPI", "CPI", "custom"):
        return [], "CFG-03.metric 未给出，偏差点算法无法判定"
    rows = []
    for point in evm.get("measurements", []):
        pv, ev, ac = float(point["pv"]), float(point["ev"]), float(point["ac"])
        if metric == "CPI":
            if ac == 0:
                return [], f"{point['period']} 的 AC 为 0，CPI 无法计算"
            value = ev / ac
        elif metric == "SPI":
            if pv == 0:
                return [], f"{point['period']} 的 PV 为 0，SPI 无法计算"
            value = ev / pv
        else:
            return [], "CFG-03.metric=custom 但未登记自定义偏差点算法"
        rows.append({"period": point["period"], "value": _round(value, config)})
    return rows, ""


def compute_deviation(evm: dict, config: dict) -> dict:
    """把每个测量期的偏差点映射为 CFG-03 的分档标签；不内置任何阈值。"""
    needed = ("CFG-01", "CFG-02", "CFG-03")
    missing = [key for key in needed if key not in config]
    if missing:
        return {"status": CANNOT, "detail": f"偏差分档需要 {missing}，配置未给出"}
    values, why = _deviation_values(evm, config)
    if why:
        return {"status": CANNOT, "detail": why}
    rows = []
    for row in values:
        band = band_for(row["value"], config)
        if band["status"] != PASS:
            return {"status": CANNOT, "detail": band["detail"]}
        rows.append({**row, "band": band["label"], "band_order": band["band"]})
    return {"status": PASS, "metric": config["CFG-03"]["metric"], "bands": rows}


def _check_deviation_config(data: dict, ctx: dict) -> list[dict]:
    blocked = _require_config(
        "deviation.thresholds_configured",
        ctx["config"],
        ("CFG-01", "CFG-02", "CFG-03"),
        "偏差分档",
    )
    if blocked:
        return [blocked]
    dimensions = ctx["config"]["CFG-01"]
    unavailable = []
    if "cost_account" in dimensions and "CFG-15" not in ctx["config"]:
        unavailable.append("CFG-15")
    if unavailable:
        return [
            _unknown(
                "deviation.thresholds_configured",
                f"CFG-01 含 {dimensions}，但缺少 {unavailable}",
            )
        ]
    return [_ok("deviation.thresholds_configured", f"分档维度 {dimensions} 的配置齐备")]


def _check_deviation_dimensions(data: dict, ctx: dict) -> list[dict]:
    if "CFG-01" not in ctx["config"]:
        return [_unknown("deviation.dimensions", "CFG-01 缺失，分档维度无法判定")]
    dimensions = ctx["config"]["CFG-01"]
    missing = []
    if "cost_account" in dimensions and not data.get("work_packages"):
        missing.append("cost_account")
    if "wbs_node" in dimensions and not any(
        item.get("wbs_ref") for item in data.get("work_packages", [])
    ):
        missing.append("wbs_node")
    if missing:
        return [
            _bad(
                "deviation.dimensions",
                f"CFG-01 要求按 {missing} 分档，但工件没有对应字段",
            )
        ]
    return [_ok("deviation.dimensions", "工件含配置要求的分档维度字段")]


def _check_deviation_unsupported(data: dict, ctx: dict) -> list[dict]:
    settings = ctx["config"].get("CFG-03")
    if not isinstance(settings, dict) or "metric" not in settings:
        return [
            _unknown(
                "deviation.custom_metric",
                "CFG-03.metric 缺失，偏差点算法无法判定",
            )
        ]
    if settings["metric"] == "custom":
        return [_unknown("deviation.custom_metric", "CFG-03.metric=custom 无机械算法")]
    return [_ok("deviation.custom_metric", "偏差点使用 SPI/CPI，可机械计算")]


# ---------------------------------------------------------------- 挣值


def _ev_rule(config: dict) -> tuple[str | None, str]:
    settings = config.get("CFG-13")
    if not isinstance(settings, dict):
        return None, "CFG-13 缺失，挣值计量规则无法确定"
    rule = settings.get("rule")
    if rule not in ("0/100", "50/50", "percent_complete", "weighted_milestone"):
        return None, "CFG-13 未给出可识别的 rule，挣值计量规则无法确定"
    return rule, ""


def _earned_value(data: dict, config: dict) -> tuple[float | None, str]:
    rule, why = _ev_rule(config)
    if rule is None:
        return None, why
    if rule == "weighted_milestone":
        return None, "CFG-13=weighted_milestone，但工件未提供里程碑权重，EV 无法复算"
    total = 0.0
    for package in data.get("work_packages", []):
        budget = float(package["budget"])
        status = package["status"]
        if rule == "0/100":
            total += budget if status == "complete" else 0.0
        elif rule == "50/50":
            total += budget * (1.0 if status == "complete" else 0.5 if status == "in_progress" else 0.0)
        else:
            # percent_complete 是判定性输入：缺省 0 会把“没填”算成“没干”，
            # 不取默认，缺失即无法判定。
            if package.get("percent_complete") is None:
                return None, f"{package.get('id')} 缺少 percent_complete，EV 无法复算"
            percent = float(package["percent_complete"])
            total += budget * max(0.0, min(100.0, percent)) / 100.0
    return total, ""


def compute_evm(data: dict, config: dict) -> dict:
    """PV/EV/AC 派生指标与 EAC 三法；EAC 方法必须由工件显式给出。"""
    bac = float(data["bac"])
    method = data.get("eac_method")
    if method not in ("cpi", "cpi_spi", "atypical"):
        return {"status": CANNOT, "detail": "未显式给出 EAC 方法（cpi / cpi_spi / atypical）"}
    rows = []
    for point in data.get("measurements", []):
        pv, ev, ac = float(point["pv"]), float(point["ev"]), float(point["ac"])
        row = {
            "period": point["period"],
            "pv": pv,
            "ev": ev,
            "ac": ac,
            "sv": _round(ev - pv, config),
            "cv": _round(ev - ac, config),
            "spi": None,
            "cpi": None,
            "eac": None,
        }
        if pv == 0:
            return {"status": CANNOT, "detail": f"{point['period']} 的 PV 为 0，SPI 无法计算"}
        if ac == 0:
            return {"status": CANNOT, "detail": f"{point['period']} 的 AC 为 0，CPI 无法计算"}
        spi = ev / pv
        cpi = ev / ac
        row["spi"] = _round(spi, config)
        row["cpi"] = _round(cpi, config)
        if method == "cpi":
            row["eac"] = _round(bac / cpi, config)
        elif method == "cpi_spi":
            row["eac"] = _round(ac + (bac - ev) / (cpi * spi), config)
        else:
            row["eac"] = _round(ac + (bac - ev), config)
        rows.append(row)
    return {"status": PASS, "method": method, "rows": rows}


def _check_evm_formulas(data: dict, ctx: dict) -> list[dict]:
    result = compute_evm(data, ctx["config"])
    if result["status"] != PASS:
        return [_unknown("evm.formulas", result["detail"])]
    bad = [
        row["period"]
        for row in result["rows"]
        if row["spi"] is None or row["cpi"] is None or row["eac"] is None
    ]
    if bad:
        return [_bad("evm.formulas", f"派生指标缺失：{bad}")]
    return [
        _ok(
            "evm.formulas",
            f"逐期复算完成；EAC 方法 {result['method']}，共 {len(result['rows'])} 期",
        )
    ]


def _check_evm_measurement(data: dict, ctx: dict) -> list[dict]:
    computed, why = _earned_value(data, ctx["config"])
    if computed is None:
        return [_unknown("evm.ev_measurement", why)]
    if not data.get("measurements"):
        return [_unknown("evm.ev_measurement", "未提供 PV/EV/AC 测量值")]
    reported = float(data["measurements"][-1]["ev"])
    if abs(_round(computed, ctx["config"]) - _round(reported, ctx["config"])) > 1e-6:
        return [
            _bad(
                "evm.ev_measurement",
                f"按 CFG-13 复算的 EV={_round(computed, ctx['config'])} 与自报 EV={reported} 不符",
            )
        ]
    return [_ok("evm.ev_measurement", f"EV 按 CFG-13 复算一致（{ctx['config']['CFG-13']['rule']}）")]


def _check_evm_eac(data: dict, ctx: dict) -> list[dict]:
    needed = ("CFG-13",)
    blocked = _require_config("evm.eac_method", ctx["config"], needed, "挣值计量规则")
    if blocked:
        return [blocked]
    if data.get("eac_method") not in ("cpi", "cpi_spi", "atypical"):
        return [_bad("evm.eac_method", "EAC 方法未显式登记")]
    return [_ok("evm.eac_method", f"EAC 方法显式登记为 {data['eac_method']}")]


def _check_evm_budget(data: dict, ctx: dict) -> list[dict]:
    total = sum(float(package["budget"]) for package in data.get("work_packages", []))
    if abs(total - float(data["bac"])) > 1e-6:
        return [
            _bad(
                "evm.budget_consistent",
                f"BAC={data['bac']} 与工作包预算合计 {round(total, 6)} 不等",
            )
        ]
    return [_ok("evm.budget_consistent", "BAC 与工作包预算合计一致")]


def _check_evm_aliases(data: dict, ctx: dict) -> list[dict]:
    legacy = {"bcwp", "bcws", "acwp"} & {key.lower() for key in data}
    if legacy:
        return [_bad("evm.term_aliases", f"混用旧称：{sorted(legacy)}")]
    return [_ok("evm.term_aliases", "只使用 EV/PV/AC 一套主名")]


# ---------------------------------------------------------------- 审计留痕

AUDIT_FIELDS = (
    "seq",
    "run_id",
    "ts",
    "actor",
    "artifact_type",
    "artifact_digest",
    "config_digest",
    "rule_version",
    "checks_run",
    "exit_code",
    "evidence_paths",
    "prev_digest",
)


def _record_digest(record: dict) -> str:
    body = {key: value for key, value in record.items() if key != "prev_digest"}
    return "sha256:" + hashlib.sha256(canonical_bytes(body)).hexdigest()


def compute_audit_append(records: list[dict], record: dict) -> dict:
    """追加一条记录：序号递增、prev_digest 取上一条的摘要。"""
    if not records:
        base = {**record, "seq": 1, "prev_digest": "genesis"}
        return {"status": PASS, "record": base, "digest": _record_digest(base)}
    last = records[-1]
    base = {**record, "seq": int(last["seq"]) + 1, "prev_digest": _record_digest(last)}
    return {"status": PASS, "record": base, "digest": _record_digest(base)}


def _check_audit_fields(data: dict, ctx: dict) -> list[dict]:
    missing = [
        f"{record.get('run_id', '?')}.{field}"
        for record in data.get("records", [])
        for field in AUDIT_FIELDS
        if field not in record
    ]
    if missing:
        return [_bad("audit.required_fields", f"留痕字段缺失：{sorted(set(missing))}")]
    return [_ok("audit.required_fields", f"{len(data.get('records', []))} 条记录字段齐备")]


def _check_audit_chain(data: dict, ctx: dict) -> list[dict]:
    records = data.get("records", [])
    expected = "genesis"
    for index, record in enumerate(records):
        if record["prev_digest"] != expected:
            return [
                _bad(
                    "audit.chain_digest",
                    f"第 {index + 1} 条记录的 prev_digest 与上一条摘要不符",
                    f"records[{index}].prev_digest",
                )
            ]
        expected = _record_digest(record)
    return [_ok("audit.chain_digest", f"{len(records)} 条记录首尾相接")]


def _check_audit_sequence(data: dict, ctx: dict) -> list[dict]:
    seqs = [record["seq"] for record in data.get("records", [])]
    if seqs != list(range(1, len(seqs) + 1)):
        return [_bad("audit.sequence_strict", f"序号不是从 1 起的连续整数：{seqs}")]
    return [_ok("audit.sequence_strict", "序号严格递增且连续")]


def _check_audit_exit_code(data: dict, ctx: dict) -> list[dict]:
    bad = [
        record["run_id"]
        for record in data.get("records", [])
        if int(record["exit_code"]) not in (0, 1, 2, 3, 4)
    ]
    if bad:
        return [_bad("audit.exit_code_valid", f"退出码不在五值语义内：{bad}")]
    return [_ok("audit.exit_code_valid", "退出码均在 0–4 内")]


def _check_audit_evidence(data: dict, ctx: dict) -> list[dict]:
    missing = [
        record["run_id"]
        for record in data.get("records", [])
        if int(record["exit_code"]) != 0 and not record.get("evidence_paths")
    ]
    if missing:
        return [_bad("audit.evidence_present", f"非零结论缺少证据路径：{missing}")]
    return [_ok("audit.evidence_present", "非零结论均附证据路径")]


CHECK_REGISTRY = {
    "dep.ids_unique": _check_dep_ids_unique,
    "dep.endpoints_exist": _check_dep_endpoints,
    "dep.acyclic": _check_dep_acyclic,
    "dep.types_valid": _check_dep_types,
    "dep.wbs_mapping": _check_dep_wbs,
    "schedule.critical_path": _check_schedule_critical,
    "budget.accounts_registered": _check_budget_accounts,
    "budget.package_unique": _check_budget_unique,
    "budget.total_conserved": _check_budget_total,
    "budget.time_phased_sum": _check_budget_periods,
    "budget.currency_match": _check_budget_currency,
    "risk.required_fields": _check_risk_required,
    "risk.scale_in_range": _check_risk_scale,
    "risk.residual_le_initial": _check_risk_residual,
    "risk.owner_registered": _check_risk_owner,
    "risk.band_consistent": _check_risk_band,
    "status.dictionary_fields": _check_status_dictionary,
    "status.no_implicit_zero": _check_status_no_zero,
    "status.sample_grid": _check_status_grid,
    "status.account_registered": _check_status_account,
    "deviation.thresholds_configured": _check_deviation_config,
    "deviation.dimensions": _check_deviation_dimensions,
    "deviation.custom_metric": _check_deviation_unsupported,
    "evm.formulas": _check_evm_formulas,
    "evm.ev_measurement": _check_evm_measurement,
    "evm.eac_method": _check_evm_eac,
    "evm.budget_consistent": _check_evm_budget,
    "evm.term_aliases": _check_evm_aliases,
    "audit.required_fields": _check_audit_fields,
    "audit.chain_digest": _check_audit_chain,
    "audit.sequence_strict": _check_audit_sequence,
    "audit.exit_code_valid": _check_audit_exit_code,
    "audit.evidence_present": _check_audit_evidence,
}

COMPUTE_REGISTRY = {
    "schedule.cpm": lambda inputs, config: compute_cpm(inputs["graph"]),
    "budget.rollup": lambda inputs, config: {
        "status": PASS,
        **compute_budget(inputs["budget"], config),
    },
    "risk.ranking": lambda inputs, config: compute_risk(inputs["risk"], config),
    "status.collect": lambda inputs, config: compute_status(inputs["status"], config),
    "deviation.map": lambda inputs, config: compute_deviation(inputs["evm"], config),
    "evm.metrics": lambda inputs, config: compute_evm(inputs["evm"], config),
    "audit.append": lambda inputs, config: compute_audit_append(
        inputs["audit"].get("records", []), inputs["record"]
    ),
}


def run_checks(names: list[str], data: dict, ctx: dict) -> list[dict]:
    """按契约声明的 `x-checks` 顺序执行检查；未注册名称由调用方先行拒绝。"""
    findings: list[dict] = []
    for name in names:
        handler = CHECK_REGISTRY.get(name)
        if handler is None:
            findings.append(_unknown(name, "检查未注册"))
            continue
        findings.extend(handler(data, ctx))
    return findings
