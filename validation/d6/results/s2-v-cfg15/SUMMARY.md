# S2 变体运行记录：V-CFG15

- 变体配置摘要：`sha256:330f78279880fee03c7feab67d77fcf02bfeb856e08a537767c5ef7971de50c5`
- 基准配置：`primary`；独立运行，**不计入主运行**
- 题数：5；差异统计：{"unchanged": 3, "pass_to_violation": 1, "pass_to_cannot_evaluate": 0, "violation_to_pass": 0, "cannot_evaluate_to_pass": 0, "changed_other": 1}
- 模型臂：`not_executed`

| 题号 | 主运行退出码 | 变体退出码 | 失败项（变体） | 差异类型 |
|---|---|---|---|---|
| D6-PUB-04 | 0 | 0 | — | unchanged |
| D6-PUB-11 | 0 | 0 | — | unchanged |
| D6-SYN-04 | 0 | 1 | budget.accounts_registered | pass_to_violation |
| D6-SYN-05 | 1 | 1 | budget.accounts_registered, budget.total_conserved, budget.time_phased_sum | changed_other |
| D6-SYN-08 | 0 | 0 | — | unchanged |

## 逐题差异原因（不构成达标结论）

- **D6-PUB-04**（unchanged）：结论不变：状态件测量科目为 1000/1100，移除 2100 不影响 status.account_registered。
- **D6-PUB-11**（unchanged）：结论不变：状态件测量科目为 1000/1100，移除 2100 不影响 status.account_registered。
- **D6-SYN-04**（pass_to_violation）：科目表移除 2100（采购）后，采购工作包仍记在该科目，budget.accounts_registered 判“未登记成本科目 ['2100']”。
- **D6-SYN-05**（changed_other）：退出码不变（主运行已是 violation），变体下失败项集合扩大：追加 budget.accounts_registered；原失败项 budget.total_conserved / budget.time_phased_sum 保留。
- **D6-SYN-08**（unchanged）：结论不变：状态件测量科目为 1000/1100，移除 2100 不影响 status.account_registered。

## 观察

- 三题（含两题状态件）不变：状态件测量科目为 1000/1100，移除 2100 不影响；SYN-04 与 SYN-05 的采购工作包记在 2100，故被检出。
- SYN-05 主运行已是 violation，变体下失败项集合扩大（追加 accounts_registered），退出码仍为 1。
