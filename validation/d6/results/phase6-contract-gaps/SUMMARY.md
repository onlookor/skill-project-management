# D6 验收批次 phase6-contract-gaps（运行记录，非权威）

**性质**：本文件是 `pm_check` 的实际运行记录，不构成 D6 达标结论，也不构成任何认可依据。

- 题目数：2
- 通过：2；不符：0
- 模型臂：not_executed（provider 与模型标识待填）

| 题号 | 案例 | 期望 | 实际 | 失败/不能判定项 | 结论 | 说明 |
|---|---|---|---|---|---|---|
| D6-PUB-23 | NAO-UNIVERSAL-CREDIT | 0 | 0 | — | pass | 新增 deviation-report 契约首跑 |
| D6-PUB-24 | NAO-HS2 | 1 | 1 | risk.scale_in_range | pass | 概率 4、影响 1，3×3 下越界 |

## 观察（不构成达标结论）

- D6-PUB-23 是 G-027 方案 B 的 deviation-report 契约首跑：CFG-01 维度（cost_account/wbs_node）与 CFG-03.metric 进入 thresholds_configured/dimensions，CFG-03.boundaries 与 CFG-02.labels 由新增 `deviation.band_consistent` 消费；主配置 SPI 0.88 映射为 amber，四项全部通过。
- D6-PUB-24 是 G-028 的刻度尺寸观测题：概率 4、影响 1，初始评分 4；3×3 下仅 `risk.scale_in_range` 违规（退出 1），5×5 下全部通过。`band` 标签仅展示、不参与判定，本批未改动 `risk-register.schema.json`。
- 既有 32 题未改动；本批两题均为公开案例改造，合成题仍为 10 道。
- 模型弱档/对照档/无技能臂仍未执行（provider 与模型标识待填）。
