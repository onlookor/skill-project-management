# D6 验收批次 phase4-public-hs2（运行记录，非权威）

**性质**：本文件是 `pm_check` 的实际运行记录，不构成 D6 达标结论，也不构成任何认可依据。

- 题目数：6
- 通过：6；不符：0
- 模型臂：not_executed（无权重）

| 题号 | 案例 | 期望 | 实际 | 失败/不能判定项 | 结论 | 说明 |
|---|---|---|---|---|---|---|
| D6-PUB-12 | NAO-HS2 | 0 | 0 | — | pass | — |
| D6-PUB-13 | NAO-HS2 | 1 | 1 | dep.endpoints_exist | pass | — |
| D6-PUB-14 | NAO-HS2 | 0 | 0 | — | pass | 配置变体 V-CFG09-GBP |
| D6-PUB-15 | NAO-HS2 | 1 | 1 | budget.total_conserved, budget.time_phased_sum | pass | 配置变体 V-CFG09-GBP |
| D6-PUB-16 | NAO-HS2 | 0 | 0 | — | pass | — |
| D6-PUB-17 | NAO-HS2 | 0 | 0 | — | pass | 配置变体 V-CFG09-GBP |
## 观察（不构成达标结论）

- D6-PUB-13 为悬挂依赖负例：依赖指向已取消的 PH2-CIVL，dep.endpoints_exist 命中，关键路径计算忽略该端点后其余 5 项通过，聚合退出 1。
- D6-PUB-15 同时命中 budget.total_conserved 与 budget.time_phased_sum（分时段按下界 87.7bn、工作包按上界 102.7bn），期望只要求前者；后者是一致性检查的连带命中，未视为额外放宽。
- 区间成本 87.7bn–102.7bn 在工件中取上界并显式标注口径（provenance），未用平均值或区间中值掩盖口径选择。
- 币种口径缺口已从 observation 升级为缺口台账 G-023（状态与挣值工件无 currency 字段，CFG-09 仅由 budget.currency_match 消费）；due_day 上限记为 G-024（待裁定，未改受钉扎 schema）；风险类别闭集记为 G-025（登记不扩）。
- 模型弱档/对照档/无技能臂仍未执行（无权重/需外部 API）。
