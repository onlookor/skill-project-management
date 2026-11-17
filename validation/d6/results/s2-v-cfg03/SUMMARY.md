# S2 变体运行记录：V-CFG03

- 变体配置摘要：`sha256:b7b6b79988e107cdad9247495b6399cd5e410b0878001cac397aed14e0e27c19`
- 基准配置：`primary`；独立运行，**不计入主运行**
- 题数：0；差异统计：{"unchanged": 0, "pass_to_violation": 0, "pass_to_cannot_evaluate": 0, "violation_to_pass": 0, "cannot_evaluate_to_pass": 0, "changed_other": 0}
- 模型臂：`not_executed`

| 题号 | 主运行退出码 | 变体退出码 | 失败项（变体） | 差异类型 |
|---|---|---|---|---|

## 逐题差异原因（不构成达标结论）

- 本变体只改 CFG-03 的 SPI 分档边界（档数与标签不变）。全题集检查项中没有任何 `deviation.*` 消费者（对 task-set.json 的 checks 枚举为 0 条），因此无题可跑、差异为空。
- 这是覆盖缺口，不是敏感性为 0：说明现有 32 题没有一题检验偏差分档口径，改 CFG-03 不会暴露任何结果变化。已写入运行记录，未据此宣称配置安全。
