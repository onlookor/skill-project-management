# D6 验收件（任务集 / 基准档位 / 阈值 / 运行记录）

本目录是 `ROADMAP.md` D6 验收要件的落地位置。验收口径见 [BASELINE.md](BASELINE.md)，机器可读的阈值与档位见 [acceptance.json](acceptance.json)。

## 当前状态（阶段 1）

| 件 | 状态 | 说明 |
|---|---|---|
| 任务集骨架 `tasks/task-set.json` | 已建（32 题：公开案例改造 22 + 合成 10） | 逐题含出处、期望结果、绑定检查项；真实案例素材核验状态逐题标注 |
| 基准档位 `BASELINE.md` / `acceptance.json` | 已定义 | 三档均写明模型族、规模、量化位宽、上下文长度；模型臂 `not_executed` |
| 配置快照 `acceptance-config.json` + `acceptance-config.lock.json` | 已冻结 | `config_digest = sha256:228bcbd6…abe8c`；未取默认值 |
| 机械臂运行 | 批次 1 合成题已跑；真实案例题待素材改造 | 结果见 `results/` |
| 模型双臂（弱档 / 对照档 / 无技能臂） | `not_executed` | 本机无对应权重，不得以机械臂结果替代 |

**不得宣称**：本目录当前不构成 D6 达标结论；阶段 1 只交付骨架、档位、阈值与首批合成题运行记录。

## 目录

```
validation/d6/
  README.md                    本文件
  BASELINE.md                  档位、阈值、配置随题、敏感性口径
  acceptance.json              机器可读的验收配置（档位/阈值/敏感性）
  acceptance-config.json       运行时配置快照（CFG-01～CFG-15）
  acceptance-config.lock.json  配置摘要与逐项摘要
  tasks/task-set.json          32 题任务集（含期望结果与绑定检查）
  cases/                       真实案例改造输入（按 ADR-0020 的案例目录约定）
  results/                     逐轮运行记录（JSON + 摘要 Markdown）
```

## 复跑方式

单题（工件模式）：

```bash
python3 scripts/pm_check.py \
  --config validation/d6/acceptance-config.json \
  --lock validation/d6/acceptance-config.lock.json \
  --artifact validation/d6/cases/<case>/inputs/<artifact>.json
```

单题（工序模式）：

```bash
python3 scripts/pm_check.py \
  --config validation/d6/acceptance-config.json \
  --lock validation/d6/acceptance-config.lock.json \
  --procedure runtime/procedures/<procedure>.json \
  --inputs validation/d6/cases/<case>/inputs \
  --out-dir validation/d6/results/<run-id>/out
```

批量运行按 `tasks/task-set.json` 逐题执行；结果写入 `results/<run-id>/`，并逐题记录 `config_digest`。

## 题目标记

- `origin`：`public_case`（公开案例改造）或 `synthetic`（合成）。
- `expected.outcome`：`pass` / `violation` / `cannot_evaluate` / `invalid` / `gap`。
- `expected.exit_code`：与运行时五值一致（0 通过，1 违规，2 输入不合法，3 不能判定，4 运行时/规则不可用）。
- `checks`：绑定的 `pm_caps` 检查 id；`gap` 题允许为空，但必须写 `gap_reason`。
- `source`：案例出处（机构、报告号、URL、章节/页、许可、访问日期）；未核验写 `pending_verification`，不得当作已核实素材。
- `input_status`：`ready` / `planned` / `blocked_external`。

## 治理边界

1. 外部案例只入**改造后的场景事实**（自写 JSON），不复制原文、图表或大段表格；案例台账见 `validation/cases/MANIFEST.md`。
2. 不自行填写“认可/通过”类外部依据；受钉扎对象未动时不需要 `--no-verify`，动到时按既有欠账登记办法处理。
3. `cannot_evaluate` 与 `gap` 如实计数，不计入通过率分子。
4. 任何达标宣称必须同时给出任务集版本、`config_digest`、逐题错题清单与模型档位；缺一不可。
