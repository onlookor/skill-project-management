# D6 验收批次 phase2-public-crossrail（运行记录，非权威）

**性质**：本文件是 `pm_check` 的实际运行记录，不构成 D6 达标结论，也不构成任何认可依据。

- 题目数：6
- 通过：6；不符：0
- 模型臂：not_executed（无权重）

| 题号 | 案例 | 期望 | 实际 | 失败/不能判定项 | 结论 | 说明 |
|---|---|---|---|---|---|---|
| D6-PUB-01 | NAO-CROSSRAIL | 0 | 0 | — | pass | — |
| D6-PUB-02 | NAO-CROSSRAIL | 1 | 1 | schedule.critical_path | pass | — |
| D6-PUB-03 | NAO-CROSSRAIL | 0 | 0 | — | pass | 配置变体 V-CFG09-GBP |
| D6-PUB-04 | NAO-CROSSRAIL | 0 | 0 | — | pass | — |
| D6-PUB-05 | NAO-CROSSRAIL | 0 | 0 | — | pass | 配置变体 V-CFG09-GBP |
| D6-PUB-06 | NAO-CROSSRAIL | 1 | 1 | evm.budget_consistent | pass | 配置变体 V-CFG09-GBP |
## 观察（不构成达标结论）

- 本批 6 题全部由公开报告摘要级事实改造，原文未入库；EVM 为按公开总额与完成度推导，标 derived_not_official_evm。
- 成本与挣值 3 题使用变体快照 V-CFG09-GBP（sha256:9c08d7c3…f548，仅 CFG-09 由 CNY 改为 GBP），单列、不计入主运行；主配置仍为 sha256:228bcbd6…abe8c。
- 状态快照不参与货币核对（status 的 4 项检查均不读 CFG-09），其金额仍是公开报告的 GBP 数值；主配置为 CNY 属未覆盖项，不影响本题判定，记为实现缺口而非通过依据。
- 依赖图缺 lag 即判 cannot_evaluate 的口径在本批未触发（6 件均显式 lag: 0）；该口径仍由 D6-PUB-08 承接。
- 模型弱档/对照档/无技能臂仍未执行（本机无权重，需外部 API 或权重），S0/S1 无数据。
