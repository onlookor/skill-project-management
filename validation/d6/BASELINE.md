# D6 验收基准：模型档位、阈值、配置随题与敏感性口径

**状态**：阶段 1 已定义；模型双臂**尚未执行**（本机无对应权重），机械臂（`pm_check` 运行时）待任务输入就绪后执行。
**依据**：`ROADMAP.md` D6 验收要件 1–5；`spec/D6_REBASELINE_PROPOSAL.md` 2.3（V1–V3）、7.2–7.5、9.4；`TODO.md` T-150。
**边界**：本文件只定义验收口径，不定义技能规则；阈值是**本次验收配置的取值**，不是技能内置常量。

## 1. 基准模型档位（三要素）

同一模型族、不同规模；每档必须同时写明**模型族 + 量化位宽 + 上下文长度**。

| 档位 | 模型族 | 规模 | 量化位宽 | 上下文长度 | 角色 |
|---|---|---|---|---|---|
| 弱档 | Qwen2.5-Instruct | 7B | Q4_K_M（4-bit，GGUF） | 32768 tokens | 被测对象；挂载本技能 |
| 对照档 | Qwen2.5-Instruct | 72B | Q4_K_M（4-bit，GGUF） | 32768 tokens | 同族更大规模；挂载同一技能 |
| 无技能臂 | Qwen2.5-Instruct | 7B | Q4_K_M（4-bit，GGUF） | 32768 tokens | 弱档模型；**不提供**任务卡/工序/schema/模板 |

**执行状态**：`defined_not_executed`。当前环境未安装上述权重，本轮不产出模型通过率；不得把机械臂结果冒充模型臂结果。

**重测纪律**：每次大版本重测一次；档位变更（模型族、规模、量化位宽、上下文长度任一变化）记 `CHANGELOG.md`，旧结果不得用于宣称新档位达标。

## 2. 阈值（验收配置实例）

写入 `validation/d6/acceptance.json#/thresholds`，并随任务集与结果表记录。

| 指标 | 取值 | 说明 |
|---|---|---|
| 机械项通过率 | ≥ 90% | 分母为**可运行**任务数；`cannot_evaluate` 不计为通过 |
| 人评项通过率 | ≥ 70% | 分母为声明了人评项的任务数 |
| 控制臂差值 | ≥ 20 个百分点 | 弱档挂技能 − 弱档无技能；同一任务集、同一配置快照 |
| 未配置阈值 | `cannot_evaluate` | 缺阈值时不得给出通过/不通过结论 |
| 错题清单 | 必须随报告 | 题号、失败项、失败原因；不得只报通过率 |

**五值结果口径**（与运行时退出码对齐）：

| 结果 | 含义 | 计入机械通过 |
|---|---|---|
| `pass` | 期望结论与实际一致，且全部绑定检查通过 | 是 |
| `violation` | 检查按预期判失败，且失败项与期望一致 | 是（负例题） |
| `cannot_evaluate` | 因缺配置/缺输入/缺人签，无法机械判定 | 否，单独计数 |
| `invalid` | 输入/工序/工件契约不合法 | 否 |
| `gap` | 对应能力尚无工件契约或检查项，无法运行 | 否，记入实现缺口 |
| `not_run` | 本轮未执行（模型臂、待核验素材） | 否，不计入分母 |

**多值同时成立时的聚合口径**：一件工件内多个检查可同时给出不同结论，聚合退出码按 `scripts/pm_check.py` 的 `PRECEDENCE` 取最高优先级，顺序为 `4 > 2 > 3 > 1 > 0`。因此**违规与 `cannot_evaluate` 同时成立时判 3**（如 D6-SYN-02：`dep.acyclic` 违规、`schedule.critical_path` 因成环无法判定）。该口径为 2026-11-17 裁定；`expected.outcome` 仍按任务的判定目的标注（上述题目记 `violation`），退出码按聚合结果记录。裁定前 D6-SYN-02 的期望为 1，属期望值与实现不一致，已改为 3 并重跑。

## 3. 配置随题的方式

1. **主运行锁同一快照**：任务集主运行的全部题目引用 `acceptance-config.json` 与 `acceptance-config.lock.json`，结果表逐题记录 `config_digest = sha256:228bcbd6c6bd4f95869de18650e5dc0acd3de204ffc49ad2846ddb3af10abe8c`。
2. **逐题留痕**：每张任务卡含 `config_ref`；缺 `config_ref` 的题目不得进入主运行。
3. **变体题单列**：任何改变 CFG-01～CFG-15 取值的题目记为 `config_variant`，使用独立的配置快照与摘要，**不计入主运行通过率**，也不与主运行拼比。
4. **跨配置不可比**：`config_digest` 不同的两次结果只能并列为“敏感性观察”，不得合并统计；报告缺摘要即不得用于验收或对外宣称。

## 4. 敏感性对照口径

敏感性分三层，互不替代：

| 层 | 对照 | 固定量 | 观察量 |
|---|---|---|---|
| S0 模型敏感性 | 弱档 vs 对照档，均挂技能 | 同一任务集、同一配置快照 | 两档通过率差；差值过大说明任务仍依赖模型规模 |
| S1 技能敏感性（控制臂） | 弱档挂技能 vs 弱档无技能 | 同一任务集、同一配置快照 | 通过率差值（验收要求 ≥20 个百分点） |
| S2 配置敏感性 | 主配置 vs 单项变体配置 | 同一模型档位、同一任务集 | 结果翻转清单；只允许出现在任务卡 `expected.sensitivity_flip` 中声明的题 |

**S2 变体清单（2026-11-17 实际建成并运行）**：

| 变体 | 变更项 | 实际影响面 | 运行结果 | 记录 |
|---|---|---|---|---|
| V-CFG03 | CFG-03 偏差分档边界整体位移（档数与标签不变） | 偏差分档题（`deviation.*`） | 全题集无 `deviation.*` 消费者，0 题可跑 | `validation/d6/results/s2-v-cfg03/run.json` |
| V-CFG05 | CFG-05 采样分数 `[0.5, 1.0]` → `[1.0]` | 状态采样题（`status.sample_grid`） | 3 题 pass→violation | `validation/d6/results/s2-v-cfg05/run.json` |
| V-CFG14 | CFG-14 风险刻度 3×3 → 5×5（分档连续覆盖 1..25） | 风险题（`risk.*`） | 5 题结论全部不变 | `validation/d6/results/s2-v-cfg14/run.json` |
| V-CFG15 | CFG-15 科目表移除 2100（采购） | 成本题（`budget.accounts_registered`） | 1 题 pass→violation，1 题失败项扩大 | `validation/d6/results/s2-v-cfg15/run.json` |
| V-CFG09-GBP | CFG-09 币种 CNY → GBP | 成本题（`budget.currency_match`） | 主运行的基础变体（6 题） | `validation/d6/results/phase2-public-crossrail/run.json` 等 |
| V-CFG09-GBP-CFG05 | 在 V-CFG09-GBP 上再改采样分数 | GBP 基准的状态题 | 2 题 pass→violation | `validation/d6/results/s2-v-cfg09-gbp-cfg05/run.json` |
| V-CFG09-GBP-CFG15 | 在 V-CFG09-GBP 上再移除科目 2100 | GBP 基准的成本/状态题 | 4 题 pass→violation，1 题失败项扩大，2 题不变 | `validation/d6/results/s2-v-cfg09-gbp-cfg15/run.json` |

**变体运行的隔离方式**：变体工件是主运行工件的副本，除 `config_ref`（`config_digest` 与 `item_digests`）同步为变体快照外内容完全相同，避免 `config_drift` 混入敏感性观察。所有变体运行独立成 `validation/d6/results/s2-*/run.json`，**不计入主运行通过率**。

**未预先声明翻转的处理**：上表 5 个 pass→violation 翻转（PUB-04、PUB-11、PUB-17、PUB-19、SYN-08 的 `status.sample_grid`）与 5 个（PUB-03、PUB-09、PUB-14、PUB-18、SYN-04 的 `budget.accounts_registered`）均未在任务卡 `expected.sensitivity_flip` 中预先声明。按本节稳定性判据，记为**未声明翻转（不稳定）**，逐题原因已写入对应 `validation/d6/results/s2-*/run.json` 的 `explanation`：采样分数收窄使期中采样点脱离网格；科目表移除使采购工作包无对应科目。**未回溯修改任务卡期望**，也未把变体结果并入主运行。

**稳定性判据**：若某题在主配置下为 `pass`、在变体配置下翻转，而该题未在 `expected.sensitivity_flip` 中声明，记为**不稳定**，必须查因；不得靠调整期望值掩盖。

## 5. 报告必须包含

1. 任务集版本、题目总数、公开案例改造数、合成数；
2. 配置快照指纹（`config_digest`）与阈值快照；
3. 逐题结果表（题号、结果、实际退出码、失败项、`cannot_evaluate` 原因、`gap` 原因）；
4. 错题清单（题号、失败项、失败原因）；
5. 机械项/人评项通过率与分母；
6. S0/S1/S2 三层敏感性结果（未执行则明确写 `not_run`）；
7. 实现缺口清单（无工件契约/无检查项的能力）。

**禁止**：以“检查器沉默”当作通过；以 `cannot_evaluate` 充作通过；跨配置拼比；用旧模型结果宣称新档位达标。
