# D6 验收批次 phase5-public-npfit（运行记录，非权威）

**性质**：本文件是 `pm_check` 的实际运行记录，不构成 D6 达标结论，也不构成任何认可依据。

- 题目数：5
- 通过：5；不符：0
- 模型臂：not_executed（无权重）

| 题号 | 案例 | 期望 | 实际 | 失败/不能判定项 | 结论 | 说明 |
|---|---|---|---|---|---|---|
| D6-PUB-18 | NAO-NPFIT | 0 | 0 | — | pass | 配置变体 V-CFG09-GBP |
| D6-PUB-19 | NAO-NPFIT | 0 | 0 | — | pass | 配置变体 V-CFG09-GBP |
| D6-PUB-20 | NAO-NPFIT | 0 | 0 | — | pass | — |
| D6-PUB-21 | NAO-NPFIT | 1 | 1 | audit.sequence_strict | pass | — |
| D6-PUB-22 | NAO-NPFIT | 0 | 0 | — | pass | — |
## 观察（不构成达标结论）

- D6-PUB-21 为审计序号负例：删除中间记录后保留第 1、3 条，prev_digest 仍与第 1 条摘要相接（链闭合），仅 audit.sequence_strict 命中，退出 1；符合“链对但序号断”的设计。
- NPfIT 无官方 EVM 三值，故本案例不设挣值题；成本按公开总额 11.4bn 拆包，拆分为改造值。
- 本批成本与状态件均按 GBP 建立并跑在 V-CFG09-GBP 变体下，未出现币种与配置不一致；审计与风险件无金额字段，不涉及 G-023 的未覆盖面。
- 模型弱档/对照档/无技能臂仍未执行（无权重/需外部 API）。
