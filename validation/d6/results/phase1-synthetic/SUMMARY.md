# 阶段 1 合成题运行记录

- 运行时间：2026-11-17T20:38:30+08:00
- 配置摘要：`sha256:228bcbd6c6bd4f95869de18650e5dc0acd3de204ffc49ad2846ddb3af10abe8c`
- 题目数：10；符合期望：10；不符：0
- 退出码分布：{'0': 4, '1': 4, '2': 0, '3': 2, '4': 0}
- 模型臂：`not_executed`（本机无权重）

| 题号 | 案例 | 期望退出码 | 实际退出码 | 失败/不能判定项 | 结论 | 不符原因 |
|---|---|---|---|---|---|---|
| D6-SYN-01 | SYN-DEP-POS | 0 | 0 | — | pass | — |
| D6-SYN-02 | SYN-DEP-CYCLE | 3 | 3 | dep.acyclic, schedule.critical_path | pass | — |
| D6-SYN-03 | SYN-DEP-NOWBS | 3 | 3 | dep.wbs_mapping | pass | — |
| D6-SYN-04 | SYN-BUD-POS | 0 | 0 | — | pass | — |
| D6-SYN-05 | SYN-BUD-TIMESUM | 1 | 1 | budget.time_phased_sum, budget.total_conserved | pass | — |
| D6-SYN-06 | SYN-RISK-POS | 0 | 0 | — | pass | — |
| D6-SYN-07 | SYN-RISK-RESIDUAL | 1 | 1 | risk.residual_le_initial | pass | — |
| D6-SYN-08 | SYN-STATUS-POS | 0 | 0 | — | pass | — |
| D6-SYN-09 | SYN-EVM-BUDGET | 1 | 1 | evm.budget_consistent | pass | — |
| D6-SYN-10 | SYN-AUDIT-SEQ | 1 | 1 | audit.sequence_strict | pass | — |

## 观察（不构成达标结论）

- 依赖图缺少 lag 字段时 schedule.critical_path 判 cannot_evaluate（无法区分“无滞后”与“未声明”）；正例需显式写 lag: 0。
- D6-SYN-02 于 2026-11-17 按裁定改期望：违规（dep.acyclic）与 cannot_evaluate（schedule.critical_path）同时成立时聚合退出码取 3（优先级 4>2>3>1>0），期望由 1 改为 3 后重跑，实际 3 与期望一致。裁定未改动受钉扎的 `spec/D6_REBASELINE_PROPOSAL.md`（§4.5 未定义 1 与 3 的优先级）。
- SYN-BUD-TIMESUM 同时触发 budget.total_conserved 与 budget.time_phased_sum；两者是不同口径的守恒检查，均保留。
- 本批 10 题全部为合成题；公开案例改造题在 phase2–phase5 运行，模型双臂 not_executed。
