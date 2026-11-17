# S2 变体运行记录：V-CFG09-GBP-CFG15

- 变体配置摘要：`sha256:7baaf0c296a3e310f5412d77c626069385d83c5d1153cb923f9d433cdf75b287`
- 基准配置：`V-CFG09-GBP`；独立运行，**不计入主运行**
- 题数：7；差异统计：{"unchanged": 2, "pass_to_violation": 4, "pass_to_cannot_evaluate": 0, "violation_to_pass": 0, "cannot_evaluate_to_pass": 0, "changed_other": 1}
- 模型臂：`not_executed`

| 题号 | 主运行退出码 | 变体退出码 | 失败项（变体） | 差异类型 |
|---|---|---|---|---|
| D6-PUB-03 | 0 | 1 | budget.accounts_registered | pass_to_violation |
| D6-PUB-09 | 0 | 1 | budget.accounts_registered | pass_to_violation |
| D6-PUB-14 | 0 | 1 | budget.accounts_registered | pass_to_violation |
| D6-PUB-15 | 1 | 1 | budget.accounts_registered, budget.total_conserved, budget.time_phased_sum | changed_other |
| D6-PUB-17 | 0 | 0 | — | unchanged |
| D6-PUB-18 | 0 | 1 | budget.accounts_registered | pass_to_violation |
| D6-PUB-19 | 0 | 0 | — | unchanged |

## 逐题差异原因（不构成达标结论）

- **D6-PUB-03**（pass_to_violation）：科目表移除 2100（采购）后，采购工作包仍记在该科目，budget.accounts_registered 判“未登记成本科目 ['2100']”。
- **D6-PUB-09**（pass_to_violation）：科目表移除 2100（采购）后，采购工作包仍记在该科目，budget.accounts_registered 判“未登记成本科目 ['2100']”。
- **D6-PUB-14**（pass_to_violation）：科目表移除 2100（采购）后，采购工作包仍记在该科目，budget.accounts_registered 判“未登记成本科目 ['2100']”。
- **D6-PUB-15**（changed_other）：退出码不变（主运行已是 violation），变体下失败项集合扩大：追加 budget.accounts_registered；原失败项 budget.total_conserved / budget.time_phased_sum 保留。
- **D6-PUB-17**（unchanged）：结论不变。
- **D6-PUB-18**（pass_to_violation）：科目表移除 2100（采购）后，采购工作包仍记在该科目，budget.accounts_registered 判“未登记成本科目 ['2100']”。
- **D6-PUB-19**（unchanged）：结论不变。

## 观察

- 七题基于 V-CFG09-GBP，变体只再移除科目 2100；五题预算件的采购工作包记在 2100，全部转为 violation。
- 两题状态件不受影响（测量科目为 1000/1100）。PUB-15 主运行已是 violation，变体下失败项集合扩大。
