## 编译方法注册表

**权威关系**：本文件是编译方法的注册表，登记有哪些方法、当前启用哪个、为什么。方法本身的规格在 `spec/methods/{method-id}.md`。本文件的变更（方法的启用/淘汰/替换）需 ADR；注册表格式调整不需 ADR（但需 CHANGELOG）。

### 字段说明

| 字段 | 含义 |
|---|---|
| `method_id` | 方法标识，格式 `CM-{缩写}` |
| `name` | 方法名 |
| `status` | `enabled`（当前启用）/ `candidate`（已注册未启用）/ `retired`（已淘汰） |
| `spec` | 方法声明文件路径 |
| `scope` | 覆盖的规则组（摘要） |
| `runtime_target` | 运行时目标 |
| `unmappable` | 不可映射项（摘要，详见方法声明文件） |
| `enabled_by` | 启用该方法的 ADR 编号（`enabled` 时必填） |
| `enabled_date` | 启用日期 |

### 方法列表

#### CM-DET-CHECKER（确定性校验器方法）

| 字段 | 内容 |
|---|---|
| `method_id` | `CM-DET-CHECKER` |
| `name` | 确定性校验器方法 |
| `status` | `enabled` |
| `spec` | `spec/methods/deterministic-checker.md`（下一轮交付；当前暂以原 `COMPILATION_SPEC.md` 的方法有关部分为内容来源） |
| `scope` | 规则组 A、C、D、E（`active`）；规则组 B（`pending_reanchor`，产物携带状态）；规则组 F、G（`assumption`，产物携带状态）；**不可映射**：无（全部规则组可被本方法编译，但 B/F/G 组的产物按规则状态降级） |
| `runtime_target` | 宿主提供的确定性校验器（Datalog / JSON 条件清单 / SQL / 其他可执行形态） |
| `unmappable` | 无（本方法覆盖全部规则组；规则状态导致的降级不是不可映射，是 P6 的合规执行） |
| `enabled_by` | ADR-0002（本次拆分决策同时确认本方法为 v0.1 的默认启用方法） |
| `enabled_date` | 2026-11-11 |

**选择理由**：v0.1 的部署目标是小型本地 LLM 与可审计的团队。确定性校验器方法在这两个目标上都成立——它把“记住规则并自觉遵守”外化为“机械检查”，符合 `CHARTER.md` 承诺 C1、C6。

#### CM-SKILL-CARD（技能卡片方法）

| 字段 | 内容 |
|---|---|
| `method_id` | `CM-SKILL-CARD` |
| `name` | 技能卡片方法 |
| `status` | `candidate` |
| `spec` | `spec/methods/skill-card.md`（待编写） |
| `scope` | 待定（预期覆盖规则组 A、C、D、E 的“活动规程”形态） |
| `runtime_target` | 技能卡片宿主（AI 执行活动规程） |
| `unmappable` | 待定（预期：需要跨卡片语义比对的规则可能不可映射） |
| `enabled_by` | 未启用 |
| `enabled_date` | — |

**候选理由**：技能卡片方法适合“规则需要被执行而非被检查”的场景（如“如何执行一次变更追溯”）。与 CM-DET-CHECKER 互补，不竞争。

#### CM-HUMAN-CHECK（人类检查单方法）

| 字段 | 内容 |
|---|---|
| `method_id` | `CM-HUMAN-CHECK` |
| `name` | 人类检查单方法 |
| `status` | `candidate` |
| `spec` | `spec/methods/human-checklist.md`（待编写） |
| `scope` | 待定（预期覆盖规则组 F、G 的“需要判断而非计算”的检查项） |
| `runtime_target` | 人类评审流程（评审点、检查单、评审记录） |
| `unmappable` | 待定（预期：需要机器执行的检查项不可映射） |
| `enabled_by` | 未启用 |
| `enabled_date` | — |

**候选理由**：规则组 F、G 的部分检查项（如“立项章程的充分性”“裁剪理由的合理性”）需要人类判断而非机械计算。人类检查单方法是这些检查项的合法归宿。

#### CM-PACT（PACT 规则方法）

| 字段 | 内容 |
|---|---|
| `method_id` | `CM-PACT` |
| `name` | PACT 规则方法（部分编译） |
| `status` | `candidate` |
| `spec` | `spec/methods/pact-rules.md`（待编写） |
| `scope` | 可映射项：`PROJECT_MINIMAL_EXISTENCE`、`CONSTRAINT_ANCHOR_REQUIRED`、`DELIVERABLE_ASSERTION_LINK`、`CHANGE_CONSTRAINT_LINK`、`ROLE_MINIMAL_COMPLETENESS`；**不可映射**：OR 分支、时钟相关规则、字段级问责写入、跨 Token 语义比对 |
| `runtime_target` | PACT 运行时（Token + Precondition + Gate） |
| `unmappable` | 见上；不可映射项由 CM-DET-CHECKER 承担 |
| `enabled_by` | 未启用 |
| `enabled_date` | — |

**候选理由**：PACT 方法是可选插件（`CONSTITUTION.md` 第 8 条）。启用它是部署决策，不是技能完备性的前提。启用时，不可映射项必须由 CM-DET-CHECKER 承担（`spec/INTERFACE_CONTRACT_SPEC.md` 第 8 节已声明）。

#### CM-NEURO-SYMB（神经符号编译方法）

| 字段 | 内容 |
|---|---|
| `method_id` | `CM-NEURO-SYMB` |
| `name` | 神经符号编译方法 |
| `status` | `candidate` |
| `spec` | `spec/methods/neuro-symbolic.md`（待编写） |
| `scope` | 待定 |
| `runtime_target` | 待定 |
| `unmappable` | 待定 |
| `enabled_by` | 未启用 |
| `enabled_date` | — |

**候选理由**：留作未来方法形态的占位。**不在 v0.1 的评估范围内**；登记它只是为了让注册表的结构支持“未来方法”，而不是暗示它应该被启用。

### 启用状态与共存关系

**v0.1 启用**：`CM-DET-CHECKER`。

**共存原则**（`COMPILATION_META.md` 第 5.2 条）：
- 多个方法可共存，各自承担不同产物。
- 共存时，每个方法声明自己的适用范围，方法之间不重叠；重叠时由启用的方法集合的 ADR 声明优先级。
- 共存不要求修改成文法——只要每个方法满足 `COMPILATION_META.md` 第 3 条。

**推荐的演进路径**（非规范，仅供参考）：
1. v0.1：CM-DET-CHECKER 独用。
2. v0.2：若部署需要“人类判断类检查项”的明确归宿，启用 CM-HUMAN-CHECK，与 CM-DET-CHECKER 共存。
3. v0.3：若部署安装了 PACT，启用 CM-PACT，不可映射项由 CM-DET-CHECKER 承担。
4. 未来：CM-SKILL-CARD 在“AI 执行活动规程”场景下启用。

### 方法替换历史

| 日期 | 方法 | 动作 | ADR |
|---|---|---|---|
| 2026-11-11 | `CM-DET-CHECKER` | 注册并启用 | ADR-0002 |

### 与 `validation/CHECKLIST.md` 的关系

`validation/CHECKLIST.md` 是 `CM-DET-CHECKER` 的产物（检查清单）。若未来启用其他方法，其产物在各自的目录下（如 `validation/pact-rules/`、`validation/human-checklist/`），与 `CHECKLIST.md` 并列。

**产物目录的命名约定**（非规范，供参考）：`validation/{method-id}/`。`CM-DET-CHECKER` 的产物当前放在 `validation/CHECKLIST.md`（单文件），未来若产物增多，迁移至 `validation/CM-DET-CHECKER/`。
