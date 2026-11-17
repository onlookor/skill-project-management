# S2 变体运行记录：V-CFG14

- 变体配置摘要：`sha256:a02cda6228eb9c013690e7828265fc00a0b7c76298d4fa294ed83b28f2f92799`
- 基准配置：`primary`；独立运行，**不计入主运行**
- 题数：5；差异统计：{"unchanged": 5, "pass_to_violation": 0, "pass_to_cannot_evaluate": 0, "violation_to_pass": 0, "cannot_evaluate_to_pass": 0, "changed_other": 0}
- 模型臂：`not_executed`

| 题号 | 主运行退出码 | 变体退出码 | 失败项（变体） | 差异类型 |
|---|---|---|---|---|
| D6-PUB-10 | 0 | 0 | — | unchanged |
| D6-PUB-16 | 0 | 0 | — | unchanged |
| D6-PUB-22 | 0 | 0 | — | unchanged |
| D6-SYN-06 | 0 | 0 | — | unchanged |
| D6-SYN-07 | 1 | 1 | risk.residual_le_initial | unchanged |

## 逐题差异原因（不构成达标结论）

- **D6-PUB-10**（unchanged）：结论不变：概率/影响取值 1–3 仍在 5×5 刻度内；band_consistent 只要求初始评分落入连续分档，不比对档位标签。
- **D6-PUB-16**（unchanged）：结论不变：概率/影响取值 1–3 仍在 5×5 刻度内；band_consistent 只要求初始评分落入连续分档，不比对档位标签。
- **D6-PUB-22**（unchanged）：结论不变：概率/影响取值 1–3 仍在 5×5 刻度内；band_consistent 只要求初始评分落入连续分档，不比对档位标签。
- **D6-SYN-06**（unchanged）：结论不变：概率/影响取值 1–3 仍在 5×5 刻度内；band_consistent 只要求初始评分落入连续分档，不比对档位标签。
- **D6-SYN-07**（unchanged）：结论不变：概率/影响取值 1–3 仍在 5×5 刻度内；band_consistent 只要求初始评分落入连续分档，不比对档位标签。

## 观察

- 五题结论全部不变。工件概率/影响取值为 1–3，仍在 5×5 刻度内；risk.band_consistent 只校验初始评分落在连续分档内，不比对档位标签，故 3×3→5×5 不改变结论。
- 这说明题集没有覆盖“刻度尺寸”这一维度；变体无翻转不等于该配置无风险。
