# D6 验收批次 phase3-public-uc（运行记录，非权威）

**性质**：本文件是 `pm_check` 的实际运行记录，不构成 D6 达标结论，也不构成任何认可依据。

- 题目数：5
- 通过：5；不符：0
- 模型臂：not_executed（无权重）

| 题号 | 案例 | 期望 | 实际 | 失败/不能判定项 | 结论 | 说明 |
|---|---|---|---|---|---|---|
| D6-PUB-07 | NAO-UNIVERSAL-CREDIT | 0 | 0 | — | pass | — |
| D6-PUB-08 | NAO-UNIVERSAL-CREDIT | 3 | 3 | schedule.critical_path | pass | — |
| D6-PUB-09 | NAO-UNIVERSAL-CREDIT | 0 | 0 | — | pass | 配置变体 V-CFG09-GBP |
| D6-PUB-10 | NAO-UNIVERSAL-CREDIT | 0 | 0 | — | pass | — |
| D6-PUB-11 | NAO-UNIVERSAL-CREDIT | 0 | 0 | — | pass | — |
## 观察（不构成达标结论）

- D6-PUB-08 按设计返回 3：依赖省略 lag 时 schedule.critical_path 判 cannot_evaluate，其余 5 项通过；固定了“未声明滞后不等于 0”的运行时口径。
- dependency-graph 的 due_day 上限为 3650 天，无法表达 15 年周期（2013 重置 → 2028 完成），故 D6-PUB-07 不设里程碑期限，只验证网络与关键路径可算；长周期期限表达记为实现缺口，未为凑通过而缩放年限。
- 风险类别取值受 schema 闭集限制（technical/resource/external/organizational/scope），“治理”类问题按 organizational 登记，未新增类别。
- 成本与状态件不读 CFG-09 的只有状态件（成本件走 V-CFG09-GBP 变体）；状态件的金额仍为 GBP 数值，主配置为 CNY，属未覆盖项。
- 模型弱档/对照档/无技能臂仍未执行（无权重/需外部 API）。
