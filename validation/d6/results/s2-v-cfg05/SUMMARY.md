# S2 变体运行记录：V-CFG05

- 变体配置摘要：`sha256:23e183a81f786b7656db833b6cd19988d3cfdaf76d0182c7c4ce117eb5f160c1`
- 基准配置：`primary`；独立运行，**不计入主运行**
- 题数：3；差异统计：{"unchanged": 0, "pass_to_violation": 3, "pass_to_cannot_evaluate": 0, "violation_to_pass": 0, "cannot_evaluate_to_pass": 0, "changed_other": 0}
- 模型臂：`not_executed`

| 题号 | 主运行退出码 | 变体退出码 | 失败项（变体） | 差异类型 |
|---|---|---|---|---|
| D6-PUB-04 | 0 | 1 | status.sample_grid | pass_to_violation |
| D6-PUB-11 | 0 | 1 | status.sample_grid | pass_to_violation |
| D6-SYN-08 | 0 | 1 | status.sample_grid | pass_to_violation |

## 逐题差异原因（不构成达标结论）

- **D6-PUB-04**（pass_to_violation）：CFG-05 由 [0.5, 1.0] 收为 [1.0] 后，工件在周期 50% 时点的采集/采样时刻不再落在网格上，status.sample_grid 判 violation；工件内容除 config_ref 同步为变体快照外未改，不是 config_drift。
- **D6-PUB-11**（pass_to_violation）：CFG-05 由 [0.5, 1.0] 收为 [1.0] 后，工件在周期 50% 时点的采集/采样时刻不再落在网格上，status.sample_grid 判 violation；工件内容除 config_ref 同步为变体快照外未改，不是 config_drift。
- **D6-SYN-08**（pass_to_violation）：CFG-05 由 [0.5, 1.0] 收为 [1.0] 后，工件在周期 50% 时点的采集/采样时刻不再落在网格上，status.sample_grid 判 violation；工件内容除 config_ref 同步为变体快照外未改，不是 config_drift。

## 观察

- 三题均为正例，变体下全部变为 violation：采样时刻（周期 50%）不在 [1.0] 网格上。
- 该变体说明状态工件对采样分数敏感；若真实部署改用“仅周期末采样”，现有的期中采样件会被判违规。
