#!/usr/bin/env python3
"""运行期解释器与七项能力的正反例自测（批次 0095）。

覆盖：
- 配置求值：0（齐备）、2（结构非法）、3（判定性项缺失）、1（摘要漂移）、
  CFG-10/11 缺省时登记 defaulted；
- 六份工件契约：各 1 例通过 + 1 例可机械判定的违规或结构违规；
- 五条工序：无模型跑通；缺签字 → 3；拒绝签字 → 1；未知算子/跳步 → 2；
- 解释器不可用 → 4（运行契约目录缺失时为 4，不降级为“通过”）。

用法：python3 scripts/test_pm_runtime.py
退出码：0 全部通过；1 有用例失败。
"""

from __future__ import annotations

import copy
import json
import shutil
import sys
import tempfile
from pathlib import Path

import pm_caps
import pm_check
import pm_config

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "runtime/demo"
INPUTS = DEMO / "inputs"
CONFIG = DEMO / "config.json"
LOCK = DEMO / "config.lock.json"

PASSED = 0
FAILED: list[str] = []


def check(label: str, actual: object, expected: object) -> None:
    global PASSED
    if actual == expected:
        PASSED += 1
        print(f"  ok   {label}")
    else:
        FAILED.append(label)
        print(f"  FAIL {label}：期望 {expected!r}，实得 {actual!r}")


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, body: dict) -> None:
    path.write_text(json.dumps(body, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def mutate(source: Path, target: Path, change) -> Path:
    body = copy.deepcopy(read(source))
    change(body)
    write(target, body)
    return target


def main() -> int:
    temp = Path(tempfile.mkdtemp(prefix="pm-runtime-test-"))
    try:
        print("[配置求值]")
        state = pm_config.evaluate(CONFIG, LOCK)
        check("齐备配置退出码", state.exit_code, 0)
        check("未取默认值", state.defaulted, ())
        check(
            "默认值登记",
            pm_config.effective_config(
                {"config": {key: value for key, value in state.raw["config"].items() if key not in ("CFG-10", "CFG-11")}},
                state.schema,
            )[1],
            ("CFG-10", "CFG-11"),
        )

        missing = mutate(
            CONFIG,
            temp / "config-missing.json",
            lambda body: body["config"].pop("CFG-01"),
        )
        check("判定性项缺失 → 3", pm_config.evaluate(missing, None).exit_code, 3)

        broken = mutate(
            CONFIG,
            temp / "config-broken.json",
            lambda body: body["config"].__setitem__("CFG-04", "fortnightly"),
        )
        check("非法枚举 → 2", pm_config.evaluate(broken, None).exit_code, 2)

        drifted = mutate(
            CONFIG,
            temp / "config-drift.json",
            lambda body: body["config"].__setitem__("CFG-09", "USD"),
        )
        check("摘要漂移 → 1", pm_config.evaluate(drifted, LOCK).exit_code, 1)

        gap = mutate(
            CONFIG,
            temp / "config-gap.json",
            lambda body: body["config"]["CFG-03"]["boundaries"][1].__setitem__("lower", 0.85),
        )
        check("分档不连续 → 2", pm_config.evaluate(gap, None).exit_code, 2)

        print("[工件契约：正例]")
        for name in ("schedule", "budget", "risk", "status", "evm", "audit"):
            result = pm_check.validate_artifact(read(INPUTS / f"{name}.json"), state)
            check(f"{name} 通过", result["exit_code"], 0)

        print("[工件契约：反例]")
        cyclic = mutate(
            INPUTS / "schedule.json",
            temp / "schedule-cycle.json",
            lambda body: body["data"]["dependencies"].append({"from": "D", "to": "A", "type": "FS"}),
        )
        check("依赖成环 → 1", pm_check.validate_artifact(read(cyclic), state)["exit_code"], 1)

        residual = mutate(
            INPUTS / "risk.json",
            temp / "risk-residual.json",
            lambda body: body["data"]["risks"][0].__setitem__("residual_score", 9),
        )
        check("残余高于初始 → 1", pm_check.validate_artifact(read(residual), state)["exit_code"], 1)

        implicit = mutate(
            INPUTS / "status.json",
            temp / "status-implicit.json",
            lambda body: body["data"]["samples"][1]["measurements"][0].pop("value"),
        )
        check("隐式缺数 → 1", pm_check.validate_artifact(read(implicit), state)["exit_code"], 1)

        wrong_ev = mutate(
            INPUTS / "evm.json",
            temp / "evm-wrong.json",
            lambda body: body["data"]["measurements"][0].__setitem__("ev", 4000),
        )
        check("EV 与 CFG-13 不符 → 1", pm_check.validate_artifact(read(wrong_ev), state)["exit_code"], 1)

        chain = mutate(
            INPUTS / "audit.json",
            temp / "audit-chain.json",
            lambda body: body["data"]["records"][1].__setitem__("prev_digest", "sha256:" + "3" * 64),
        )
        check("摘要链断 → 1", pm_check.validate_artifact(read(chain), state)["exit_code"], 1)

        provenance = mutate(
            INPUTS / "schedule.json",
            temp / "schedule-no-provenance.json",
            lambda body: body["provenance"].pop("schedule.dependencies"),
        )
        check("缺来源引用 → 2", pm_check.validate_artifact(read(provenance), state)["exit_code"], 2)

        wrong_type = mutate(
            INPUTS / "schedule.json",
            temp / "schedule-wrong-type.json",
            lambda body: body.__setitem__("artifact_type", "unknown-artifact"),
        )
        check("未注册工件类型 → 2", pm_check.main(["--artifact", str(wrong_type)]), 2)

        print("[工序：正例]")
        for name in ("schedule_baseline", "cost_baseline", "risk_review", "status_review", "audit_review"):
            out = temp / f"out-{name}"
            code = pm_check.main(
                [
                    "--procedure",
                    str(ROOT / "runtime/procedures" / f"{name}.json"),
                    "--inputs",
                    str(INPUTS),
                    "--config",
                    str(CONFIG),
                    "--lock",
                    str(LOCK),
                    "--out-dir",
                    str(out),
                ]
            )
            check(f"{name} 跑通", code, 0)
        check("任务目录通过", pm_check.main(["--catalog", "--config", str(CONFIG), "--lock", str(LOCK)]), 0)

        print("[工序：反例]")
        no_approval = temp / "inputs-no-approval"
        shutil.copytree(INPUTS, no_approval)
        (no_approval / "approval.json").unlink()
        check(
            "缺人类签字 → 3",
            pm_check.main(
                ["--procedure", str(ROOT / "runtime/procedures/schedule_baseline.json"), "--inputs", str(no_approval), "--config", str(CONFIG), "--lock", str(LOCK), "--out-dir", str(temp / "out-na")]
            ),
            3,
        )

        rejected = temp / "inputs-rejected"
        shutil.copytree(INPUTS, rejected)
        records = json.loads((rejected / "approval.json").read_text(encoding="utf-8"))
        records[0]["decision"] = "reject"
        (rejected / "approval.json").write_text(
            json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        check(
            "签字拒绝 → 1",
            pm_check.main(
                ["--procedure", str(ROOT / "runtime/procedures/schedule_baseline.json"), "--inputs", str(rejected), "--config", str(CONFIG), "--lock", str(LOCK), "--out-dir", str(temp / "out-rj")]
            ),
            1,
        )

        unknown_op = mutate(
            ROOT / "runtime/procedures/schedule_baseline.json",
            temp / "procedure-unknown-op.json",
            lambda body: body["steps"][1].__setitem__("op", "summon"),
        )
        check(
            "算子越界 → 2",
            pm_check.main(["--procedure", str(unknown_op), "--inputs", str(INPUTS), "--config", str(CONFIG), "--lock", str(LOCK)]),
            2,
        )

        skipped = mutate(
            ROOT / "runtime/procedures/schedule_baseline.json",
            temp / "procedure-skip.json",
            lambda body: body["steps"][2].__setitem__("needs", ["S9"]),
        )
        check(
            "跳步/乱序 → 2",
            pm_check.main(["--procedure", str(skipped), "--inputs", str(INPUTS), "--config", str(CONFIG), "--lock", str(LOCK)]),
            2,
        )

        print("[解释器不可用]")
        original = pm_check.ARTIFACT_DIR
        pm_check.ARTIFACT_DIR = Path("/nonexistent/artifacts")
        try:
            code = pm_check.main(["--artifact", str(INPUTS / "schedule.json")])
        finally:
            pm_check.ARTIFACT_DIR = original
        check("契约目录缺失 → 4", code, 4)

        print("[可复现性]")
        digest_a = pm_caps.compute_cpm(read(INPUTS / "schedule.json")["data"])
        digest_b = pm_caps.compute_cpm(read(INPUTS / "schedule.json")["data"])
        check("CPM 两次结果一致", digest_a, digest_b)
        check(
            "EAC 三法显式",
            pm_caps.compute_evm({**read(INPUTS / "evm.json")["data"], "eac_method": "cpi_spi"}, state.config)["status"],
            "pass",
        )
    finally:
        shutil.rmtree(temp, ignore_errors=True)

    print(f"\n通过 {PASSED} 项；失败 {len(FAILED)} 项")
    if FAILED:
        for item in FAILED:
            print(f" - {item}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
