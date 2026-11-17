# S2 变体运行记录：V-CFG09-GBP-CFG05

- 变体配置摘要：`sha256:00e0ce9002ae21e26bcd2fa3827dadc9b84b34cc557ec13bb3baf1fa30b2d8c7`
- 基准配置：`V-CFG09-GBP`；独立运行，**不计入主运行**
- 题数：2；差异统计：{"unchanged": 0, "pass_to_violation": 2, "pass_to_cannot_evaluate": 0, "violation_to_pass": 0, "cannot_evaluate_to_pass": 0, "changed_other": 0}
- 模型臂：`not_executed`

| 题号 | 主运行退出码 | 变体退出码 | 失败项（变体） | 差异类型 |
|---|---|---|---|---|
| D6-PUB-17 | 0 | 1 | status.sample_grid | pass_to_violation |
| D6-PUB-19 | 0 | 1 | status.sample_grid | pass_to_violation |

## 逐题差异原因（不构成达标结论）

- **D6-PUB-17**（pass_to_violation）：CFG-05 由 [0.5, 1.0] 收为 [1.0] 后，工件在周期 50% 时点的采集/采样时刻不再落在网格上，status.sample_grid 判 violation；工件内容除 config_ref 同步为变体快照外未改，不是 config_drift。
- **D6-PUB-19**（pass_to_violation）：CFG-05 由 [0.5, 1.0] 收为 [1.0] 后，工件在周期 50% 时点的采集/采样时刻不再落在网格上，status.sample_grid 判 violation；工件内容除 config_ref 同步为变体快照外未改，不是 config_drift。

## 观察

- 两题基于 V-CFG09-GBP（主运行口径），变体只再收采样分数，避免币种差异混入。
- 结论与主运行一致地翻转：期中采样不再在网格上。
