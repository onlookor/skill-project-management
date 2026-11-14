# 确定性校验器方法（CM-DET-CHECKER）

## 0. 定位

本方法是**确定性校验器方法**：把 `GRAMMAR.md` 的每条规则翻译为可被确定性程序执行的检查条件，产出可运行的检查清单与检查项规格。本方法**不编译**：规则的自然语言解释、`provenance_note`、`applicability` 的语义判断（后者由宿主运行时提供求值结果）。本方法与 `spec/COMPILATION_META.md` 的关系：META 定义“什么是合法的编译”（P1–P6、准入条件）；本方法声明“以确定性程序为运行时，如何满足 P1–P6”。

## 1. 适用范围

### 1.1 覆盖的规则组

| 规则组 | 覆盖状态 | 产物形态 |
|---|---|---|
| A（项目存在条件） | 完整覆盖 | 检查项规格 + 检查清单 |
| B（过程组/主题组双标签） | 完整覆盖；规则状态为 `active`（ADR-0008），`severity` 保持 `advisory`，产物携带 `rule_status`；升级为 `block` 需样例契约证据（T-118） | 检查项规格（带状态标记） |
| C（交付物可断言） | 完整覆盖 | 检查项规格 + 检查清单 |
| D（变更追溯） | 完整覆盖 | 检查项规格 + 检查清单 |
| E（角色最小完备性） | 完整覆盖 | 检查项规格 + 检查清单 |
| F（阶段闭合） | 完整覆盖，但规则状态为 `assumption`；产物携带 `rule_status`，按 P6 降级为 `advisory` | 检查项规格（带状态标记 + `assumption_basis`） |
| G（适用性裁剪） | 完整覆盖，但规则状态为 `assumption`；产物携带 `rule_status`，按 P6 降级为 `advisory` | 检查项规格（带状态标记 + `assumption_basis`） |

### 1.2 不可映射项

**本方法无不可映射项。** 全部规则组均可被本方法编译为检查条件。规则状态（当前为 F、G 组的 `assumption`）导致的降级不是“不可映射”，是 META P6 的合规执行——产物仍被编译，只是携带状态标记并被宿主按 `advisory` 处理。

**唯一的方法层限制**：`check_id` 的判定逻辑依赖宿主提供的谓词求值能力（Datalog / JSON 条件求值 / SQL / 其他）。若宿主无法提供任何谓词求值能力，本方法退化为“检查清单 + 人工执行”——此时本方法的 P2（可判定性）由人类评审承担，P4（证据保全）由人工记录承担；方法的其余性质不变。这一退化路径是 META 第 3.7 条“无插件完备性”的合法形态，登记于本文件第 10 节。

## 2. 运行时目标

**主运行时**：宿主提供的确定性校验器。可识别的运行时形态：

- Datalog 引擎；
- JSON 条件清单求值器（如基于 JSON Schema + 自定义谓词函数的执行器）；
- SQL 查询引擎；
- 其他可执行形态（Prolog、规则引擎等）。

**运行时标识**：`runtime: deterministic-checker`。宿主在装配时声明其具体引擎类型；本方法不绑定具体引擎。

**退化运行时**：无谓词求值能力时，退化为“检查清单 + 人类评审”形态。运行时标识为 `runtime: deterministic-checker/human-fallback`。

## 3. 忠实性论证（P1）

### 3.1 P1a（不引入）

**论证方式**：逐条翻译说明。

**论证**：每个 `check_id` 在 `validation/CHECKLIST.md` 中对应一行，该行的“规则”字段指向 `GRAMMAR.md` 的具体规则编号；检查项的判定条件由该规则的陈述翻译而来。翻译过程中**不引入**源未登记的新规则——任何在翻译中出现的谓词，必须在 `knowledge/anchored-entries.jsonl` 中有定义；任何在翻译中出现的槽位，必须在 `spec/INTERFACE_CONTRACT_SPEC.md` 中有定义。

**检查方式**：编译产物的每个 `check_id` 必须携带 `source_rule` 字段（指向 `GRAMMAR.md` 的规则编号）与 `predicates_used` 字段（列出判定条件中使用的谓词名）。编译自检：`source_rule` 必须存在；`predicates_used` 中的每个谓词必须在 `knowledge/` 中有定义。未通过者拒绝发布。

**不可编译内容的处理**：若某条规则的陈述无法翻译为可判定条件（如包含无法形式化的模糊判断），本方法**不编译该规则**，将其列入“本方法不可编译清单”，并升级为 META 第 6 条 F-C1（源缺口）或 F-C2（方法不可行）的判别对象。当前 v0.1 无此类规则（全部规则组的陈述均已形式化到可翻译程度）。

### 3.2 P1b（不丢失）

**论证方式**：覆盖清单。

**论证**：本文件第 1.1 节列出覆盖的规则组与规则；`validation/CHECKLIST.md` 是覆盖清单的产物。编译自检：`GRAMMAR.md` 的每条规则必须出现在 `CHECKLIST.md` 中，或被列入“本方法不可编译清单”。两者皆无 → 拒绝发布。

**与 META P1b 的关系**：META 要求“每条规则必须被至少一个启用的编译方法覆盖”。本方法作为 v0.1 唯一启用的方法，覆盖全部规则；未来若启用其他方法，某条规则可由其他方法覆盖，本方法的覆盖清单相应调整（走 CHANGELOG）。

### 3.3 P1c（不扭曲）

**论证方式**：逐条对照 + 反例检验。

**论证**：每条规则的翻译说明（`check_id` 注册表中的“判定”列）陈述自然语言条件式与逻辑条件之间的对应关系。对照的检验方式：

1. **正向对照**：逻辑条件满足时，规则陈述的语义是否被满足；
2. **反向对照**：规则陈述的语义被违反时，逻辑条件是否失败；
3. **反例检验**：为每条规则设计至少一个“应通过”用例与一个“应失败”用例，检验逻辑条件的判定与语义判断一致。

反例检验的用例登记在 `validation/test-cases/`（待补充，登记于 `TODO.md`）。在用例完备前，P1c 的论证状态为“论证完成，检验待执行”；这一状态在 `CHANGELOG.md` 中登记，不阻塞方法启用（因为论证本身已完成），但登记为跟进项。

### 3.4 P1c 的具体风险点与处置

**风险点一：量词翻译的遗漏**。规则的“每个”“至少一个”“不存在”若翻译时遗漏量词，会扭曲语义。处置：翻译说明中量词必须显式标注；反例检验中必须包含量词边界用例（空集、单元素、多元素）。

**风险点二：否定与例外的遗漏**。规则的“除非”“除……外”若翻译为简单的逻辑否定，会扭曲语义。处置：翻译说明中例外条件必须显式标注为分支；反例检验中必须包含例外触发用例。

**风险点三：`unknown` 的静默处理**。三值逻辑中 `unknown` 若被静默当作 `false`，会扭曲语义。处置：检查器必须输出 `cannot_evaluate`（见第 4.2 节），不得输出 `fail`；`cannot_evaluate` 的处理按 `ASSUMPTION_PROTOCOL.md` 第 5 节。

## 4. 可判定性与结论封闭性（P2 / P3）

### 4.1 P2（可判定性）

**论证**：本方法的产物是检查项规格，每个 `check_id` 的判定条件是一个可在宿主谓词求值能力上执行的条件式。执行形态：

- **可判定**：条件式的求值结果为 `true` / `false` / `unknown`（三值），由宿主的谓词求值器产出；
- **执行者**：确定性校验器程序；
- **退化形态**：无谓词求值能力时，检查清单由人类评审执行，结论为 `符合` / `不符合` / `不适用` / `未触发`（见第 4.2 节）。

### 4.2 P3（结论封闭性）

**封闭枚举**：

| 运行时形态 | 结论枚举 |
|---|---|
| 确定性校验器（主形态） | `{pass, fail, cannot_evaluate, not_applicable}` |
| 退化形态（人类评审） | `{符合, 不符合, 不适用, 未触发}` |

**封闭性论证**：

- 四值覆盖全部求值结果：条件式为真 → `pass`；为假 → `fail`；输入缺失或谓词不可求值 → `cannot_evaluate`；规则的 `applicability` 判定为不适用 → `not_applicable`。不存在第五种状态。
- `cannot_evaluate` **不等于** `pass`，也**不等于** `not_applicable`。前者是“缺输入”，后者是“规则明确不作用于该对象”。
- `not_applicable` 必须由 `applicability.state = inapplicable` 触发（见 4.4），不得由检查器自行推断“看起来不适用”。
- 退化形态的四值同构：`符合` ↔ `pass`、`不符合` ↔ `fail`、`不适用` ↔ `cannot_evaluate`、`未触发` ↔ `not_applicable`。退化形态的“不适用”必须附带缺失输入说明。

**禁止的中间态**：`待定`、`基本通过`、`大致符合`、`部分满足` 均不在封闭枚举内，不得作为结论输出。

### 4.4 适用性状态机（ADR-0013 P7）

规则的 `applicability` 求值由宿主提供（本方法不解释其语义），但求值结果的**状态迁移与结论映射**由本节固定：

| 状态 | 含义 | 结论 |
|---|---|---|
| `applicable` | 适用条件成立 | 进入判定，输出 `pass` / `fail` / `cannot_evaluate` |
| `inapplicable` | 适用条件明确不成立 | 输出 `not_applicable`，`reason` 为 `null` |
| `pending` | 适用条件尚不可判定 | 输出 `cannot_evaluate`，`reason: applicability_pending` |

**迁移约束**：`pending` 不得静默转为 `applicable`；状态只能由宿主根据适用条件的求值结果迁移，不得由生成模型或检查器推断。输入 schema 以 `applicability.state` 承载该状态（`spec/CHECKER_INPUT_SCHEMA.md` 第 4 节）。

### 4.5 severity 与规则状态的映射

本方法不改变 `GRAMMAR.md` 声明的 severity，只按规则状态做降级：

| 规则状态 | 产物中的实际 severity | 说明 |
|---|---|---|
| `active` | 按 `GRAMMAR.md` 声明的 severity | 正常执行 |
| `pending_reanchor` | 降级为 `advisory` | 来源待重新锚定；产物携带 `rule_status: pending_reanchor` |
| `assumption` | 降级为 `advisory`，附 `assumption_basis` | 规则以假设身份存在；产物携带 `rule_status: assumption` |

**severity 不得运行时改级**：宿主不得自行把 `block` 降为 `warn`，生成模型不得声称“这条可以放宽”。任何改变 severity 的动作 = 成文法变更 = ADR + 批准。

## 5. 证据保全（P4）

### 5.1 证据形态

本方法的证据为**检查执行记录**，七要素齐备：

```json
{
  "check_id": "...",
  "source_rule": "G-XX",
  "rule_status": "active | pending_reanchor | assumption",
  "input_snapshot": {
    "predicates": { "<谓词名>": "<值>" },
    "version_vector": "<快照版本>"
  },
  "checker_version": "<校验器版本>",
  "verdict": "pass | fail | cannot_evaluate",
  "reason": "<fail 或 cannot_evaluate 的原因>",
  "executed_at": "<时间戳>",
  "executor": "<校验器标识>"
}
```

### 5.2 可重放性保证

- `input_snapshot` 记录执行时的谓词取值与快照版本；同一快照 + 同一 `checker_version` 重执行必得同一结论。
- 若谓词取值依赖外部事实（如数据库查询），`input_snapshot` 必须记录事实的来源标识与查询时间；无法保证确定性的检查项，降级为“不可重放”，证据降级为线索，不获得引用资格。
- 检查器版本与 `GRAMMAR.md` 版本、`SOURCE_LEDGER.md` 版本对齐（见第 9 节）。

### 5.3 保存期限

证据保存期限 = 所支撑决策的存续期 + `SOURCE_LEDGER.md` 相关条目的合规留存要求（若有）。无合规要求时，默认保存期为决策存续期 + 1 年（注册表默认值，变更走 CHANGELOG）。

## 6. 自包含（P5）

**论证**：本方法的产物（检查清单 + 检查项规格）不依赖外部文档即可执行。

- 检查清单的每行携带 `check_id`、规则编号、severity、规则状态、输入摘要、判定摘要；执行者（程序或人类）凭清单即可执行，不需要查阅 `GRAMMAR.md` 原文。
- 判定摘要使用 `knowledge/` 中定义的谓词名与槽位名；这些名称在 `knowledge/anchored-entries.jsonl` 与 `spec/INTERFACE_CONTRACT_SPEC.md` 中有定义，执行者不需要查阅外部来源。
- `grounding_ref` 保留在 `GRAMMAR.md` 中并指向 `SOURCE_LEDGER.md` 条目，不进入检查清单的执行路径——它是合法性锚点，不是执行前提（与 `CONSTITUTION.md` 第 7.2 级一致）。

**P5 与 `CONSTITUTION.md` 第 7 条的关系**：第 7 条约束 `GRAMMAR.md` 的规则陈述；P5 约束本方法的产物。二者是同一纪律在立法层与执行层的两次落实。

## 7. 假设与事实分离（P6）

### 7.1 产物中的表示

本方法的产物中，`grounded` 与 `assumption` 的分离通过**字段级标记**实现：

- 每个 `check_id` 规格携带 `grounding_refs` 字段，列出该检查项所依据的 `SOURCE_LEDGER.md` 条目 ID；该字段名与知识条目的 `grounding_ref` 不同，后者只用于本体或规则到知识条目的绑定；
- 若规则状态为 `assumption`，规格额外携带 `assumption_basis` 字段，指向 `GRAMMAR.md` 中对应规则的 `assumption_verification`；
- 检查执行记录的 `rule_status` 字段区分三种状态。

### 7.2 与 ASSUMPTION_PROTOCOL.md 的对应

`ASSUMPTION_PROTOCOL.md` 第 8 节规定“规则状态为 assumption 的检查项，编译产物中必须携带 `assumption_basis` 字段”。本方法的实现：

- 检查项规格：`assumption_basis` 字段存在，值为 `GRAMMAR.md` 中对应规则的 `assumption_verification` 字段的引用；
- 检查执行记录：`rule_status: assumption`，且 `reason` 字段在 `fail` 时说明“未满足（假设级）”而非“违规”；
- 人类可读投影：`CHECKLIST.md` 中该行标注 `[assumption]`。

### 7.3 禁止事项

- 不得把 `assumption` 级检查项的 `fail` 输出为 `block`；
- 不得在检查项规格中省略 `assumption_basis`；
- 不得在人类可读投影中把 `assumption` 级检查项表述为“合规要求”。

## 8. 失败处理

### 8.1 编译期失败（F-C3 忠实性失败）

| 失败类型 | 检测方式 | 处置 |
|---|---|---|
| 检查项引入源未登记的谓词/槽位 | 编译自检：`predicates_used` / `slots_used` 必须存在于 `knowledge/` / `INTERFACE_CONTRACT_SPEC.md` | 产物拒绝发布；缺陷登记；修复后重编译 |
| 检查项丢失源已登记的规则 | 编译自检：`CHECKLIST.md` 必须覆盖全部规则或列入不可编译清单 | 同上 |
| 检查项扭曲源语义 | 反例检验（第 3.3 节）失败 | 同上 |

### 8.2 执行期失败（F-C4 执行失败）

| 失败类型 | 含义 | 处置 |
|---|---|---|
| `checker_error` | 校验器内部错误 | 记录；重试；持续失败则升级为方法缺陷（走 CHANGELOG） |
| `input_missing` | 必需输入缺失 | 输出 `cannot_evaluate` + `missing_input` 清单；按 `ASSUMPTION_PROTOCOL.md` 第 5 节处理 |
| `schema_mismatch` | 输入不符合谓词/槽位 schema | 记录；输出 `cannot_evaluate`；不当作通过 |
| `rule_status_unknown` | 规则状态未登记 | 执行层缺陷；阻断该检查项执行直至状态补登 |

### 8.3 与 META 第 6 条失败分类的对应

| META 分类 | 本方法的对应 |
|---|---|
| F-C1（源缺口） | 若某规则无法被本方法编译且无其他方法承担 → 升级为 F-C1，走 ADR 修订成文法 |
| F-C2（方法不可行） | 本方法当前无此类（第 1.2 节） |
| F-C3（忠实性失败） | 第 8.1 节 |
| F-C4（执行失败） | 第 8.2 节 |
| F-C5（假设未闭合） | 本方法不承担；由 `ASSUMPTION_PROTOCOL.md` 第 6 节处置 |

## 9. 基线纪律

- **方法版本**：本方法不声明文件版本号；其变更历史记入 `CHANGELOG.md`，包版本以 annotated tag 声明（ADR-0003）。若变更改变已有 `check_id` 的判定逻辑，升级为结构性变更，需 ADR。
- **产物基线**：`validation/CHECKLIST.md` 与检查项规格必须记录生成时的 `source_commit`，即 `GRAMMAR.md`、`SOURCE_LEDGER.md`、本方法声明、`knowledge/` 谓词定义所在的那次 git 提交（ADR-0004）。
- **对齐检查**：宿主装配时比对产物的 `source_commit` 与当前源提交；不一致 → 拒绝运行过期产物（META 第 7.5 条）。
- **脏工作区**：若任一源文件相对 `source_commit` 存在未提交改动（`git status --porcelain` 中涉及该源文件），产物**直接判定过期**，不得以“提交号相同”放行。
- **无 git 环境**：无法取得提交标识时，不得假定产物有效；按过期处理并报告部署缺陷。
- **重编译触发**：`GRAMMAR.md` 规则增删改、`SOURCE_LEDGER.md` 条目状态变更、本方法声明变更、`knowledge/` 谓词定义变更，均触发重编译；重编译后产物记录新的 `source_commit`。

## 10. 无插件完备性

### 10.1 依赖的插件

**无强制依赖。** 本方法不要求 PACT、任何外部领域本体、任何外部本体框架存在。

**可选增强**：

| 插件 | 存在时的增强 | 缺失时的退路 |
|---|---|---|
| PACT | 可将部分检查项映射为 PACT 准入规则（见第 10.3 节） | 本方法独立执行全部检查项 |
| 外部领域本体 | 可将约束分类映射为领域本体维度（仅限该领域契约，见 `INTERFACE_CONTRACT_SPEC.md` 第 7 节的软件工程样例） | 使用通用分类（目标/环境/方案） |

### 10.2 退化路径（无谓词求值能力）

若宿主无法提供任何谓词求值能力，本方法退化为“检查清单 + 人类评审”：

- 产物形态不变（`CHECKLIST.md` + 检查项规格）；
- 执行者从确定性校验器变为人类评审者；
- 结论枚举从 `{pass, fail, cannot_evaluate}` 变为 `{符合, 不符合, 不适用}`（同构映射，见第 4.2 节）；
- 证据形态从程序记录变为人工评审记录（七要素中 `executor` 为人类署名，`checker_version` 为清单版本）；
- P1–P6 的全部要求仍然满足（P2 的“执行”由人类承担，P4 的“可重放”由人工记录的完备性保证）。

**退化路径的准入**：退化不构成方法变更，不要求 ADR；但宿主必须在装配时声明 `runtime: deterministic-checker/human-fallback`，并登记于 `CHANGELOG.md`（因为它是部署形态的实质变化）。

### 10.3 PACT 适配（可选）

若宿主安装 PACT，本方法可将以下检查项映射为 PACT 准入规则（详细映射见 `contracts/resolver.md` 第 3 节）：

| check_id | PACT 映射形态 |
|---|---|
| `PROJECT_MINIMAL_EXISTENCE` | 产生 `ProjectToken` 的前置条件：存在 `ActorToken`、`OutcomeToken`、`CommitmentToken`、`ConstraintToken` |
| `CONSTRAINT_ANCHOR_REQUIRED` | 产生任何管理产物 Token 的前置条件：存在 `ConstraintToken` 且被引用 |
| `DELIVERABLE_ASSERTION_LINK` | 产生 `DeliverableToken` 的前置条件：存在 `AssertionToken` 作为见证 |
| `CHANGE_CONSTRAINT_LINK` | 产生 `ChangeRequestToken` 的前置条件：存在 `ConstraintToken` 且关系类型已声明 |
| `ROLE_MINIMAL_COMPLETENESS` | 产生决策类 `CommitmentToken` 的前置条件：存在 `AccountableToken`（类型受限）与 `ResponsibleToken` |

**不可映射项**（由本方法自身承担，不进入 PACT）：`DUAL_DIMENSION_ANNOTATION`、`ASSERTION_MUTUAL_EXCLUSION`、`ALL_IMPROVEMENT_ASSUMPTION`、`AI_AUTONOMY_DELEGATION_AUDITABLE`、G-F 组全部、G-G 组全部。

**适配纪律**：可映射项映射；不可映射项由本方法自身执行；**PACT 缺失时本方法完备**（META 第 3.7 条）。

## 11. 方法声明文件自身的一致性检查

本文件声明的性质（P1–P6、适用范围、不可映射项、运行时目标）与 `spec/COMPILATION_METHODS.md` 中 `CM-DET-CHECKER` 条目的登记一致。不一致时以 `COMPILATION_METHODS.md` 为准（注册表是权威），本文件修订。

---

## 附：check_id 注册表与翻译规范

> 本节是原编译规范（已拆分）第 2 节（check_id 注册表）与第 5 节（翻译规范）的移植，作为本方法的**方法有关**内容。

### A. check_id 注册表

| check_id | 规则 | 判定（子句 id） | 子句指纹 | 输入 | 原因码 | 规则状态 |
|---|---|---|---|---|---|---|
| `PROJECT_MINIMAL_EXISTENCE` | G-A1 | `G-A1#1`–`G-A1#6` | `6a4f8c0ad633` | `project`, `actors`, `outcomes`, `commitments`, `constraints` | missing_actor / missing_outcome / missing_commitment / missing_constraint / broken_commitment_endpoint / constraint_not_applied | active |
| `CONSTRAINT_ANCHOR_REQUIRED` | G-A2 | `G-A2#1`–`G-A2#2` | `92b655760009` | `commitments`, `deliverables`, `constraints` | unanchored_management_item / undefined_enum_value | active |
| `DUAL_DIMENSION_ANNOTATION` | G-B1 | `G-B1#1`–`G-B1#2` | `2cde52fd3961` | `management_items` | missing_dimension | active |
| `DIMENSION_VALUE_CLOSED` | G-B2 | `G-B2#1`–`G-B2#2` | `b50cfc085765` | `management_items` | dimension_value_out_of_enum / invalid_subject_group_extension / undefined_enum_value | active |
| `DELIVERABLE_ASSERTION_LINK` | G-C1 | `G-C1#1`–`G-C1#3` | `f2a5638c6328` | `deliverables`, `assertions` | deliverable_without_assertion / dangling_reference / assertion_without_content / assertion_about_mismatch | active |
| `ASSERTION_MUTUAL_EXCLUSION` | G-C2 | `G-C2#1`–`G-C2#2` | `e099e1ee877a` | `assertions`, `deliverables` | mutually_exclusive_active_assertions / missing_input / undefined_enum_value | active |
| `CHANGE_CONSTRAINT_LINK` | G-D1 | `G-D1#1`–`G-D1#3` | `3e473f8ea1e8` | `changes`, `constraints`, `commitments`, `deliverables` | missing_change_target / invalid_change_target / missing_constraint_link / invalid_change_relation | active |
| `ALL_IMPROVEMENT_ASSUMPTION` | G-D2 | `G-D2#1`–`G-D2#3` | `c1573c1eb236` | `changes`, `actors` | all_improvement_without_verification / approval_basis_before_verification / assumption_unclosed | active |
| `ROLE_MINIMAL_COMPLETENESS` | G-E1 | `G-E1#1`–`G-E1#3` | `a707061b238f` | `actors`, `commitments` | missing_accountable / multiple_accountable / unknown_accountable / accountable_not_human / missing_responsible / missing_role_merge_declaration | active |
| `AI_AUTONOMY_DELEGATION_AUDITABLE` | G-E2 | `G-E2#1`–`G-E2#3` | `0b227c8dc644` | `actors`, `autonomy_grants`, `assertions` | delegation_chain_not_accountable / accountable_not_human / invalid_path / dangling_reference / assertion_incomplete / assumption_unclosed | active |
| `PROJECT_CHARTER_EXISTENCE` | G-F1 | `G-F1#1`–`G-F1#2` | `a40c88e331b9` | `projects`, `charters`, `outcomes`, `constraints`, `actors`, `assertions` | missing_charter / incomplete_charter | assumption |
| `CLOSURE_ACCEPTANCE_LINK` | G-F2 | `G-F2#1`–`G-F2#2` | `1c157ebdf8ff` | `deliverables`, `actors` | missing_acceptance_assertion | assumption |
| `PROCUREMENT_CONTRACT_ANCHOR` | G-F3 | `G-F3#1`–`G-F3#2` | `3b6f71eed103` | `commitments`, `contracts`, `constraints`, `actors` | missing_contract / incomplete_contract | assumption |
| `SCHEDULE_EVIDENCE_LINK` | G-F4 | `G-F4#1` | `3a1c2ec19e7e` | `commitments` | missing_schedule_evidence | assumption |
| `TAILORING_RECORD_EXISTENCE` | G-G1 | `G-G1#1`–`G-G1#2` | `3e7dc444affc` | `tailoring_actions`, `tailoring_records`, `actors` | missing_tailoring_record / incomplete_tailoring_record | assumption |
| `TAILORING_NON_TRIMMABLE_SET` | G-G2 | `G-G2#1` | `76a53059e6a6` | `tailoring_records` | non_trimmable_rule | assumption |
| `TAILORING_REASSESSMENT_CONDITION` | G-G3 | `G-G3#1`–`G-G3#2` | `c4a47f27fec9` | `tailoring_records` | missing_reassessment_condition | assumption |

### A.2 子句表（规则正文 → 判定列的逐子句覆盖）

> 用途：解决“一规则一句导致子条件被压缩”（ADR-0013 的问题 P1）。每条规则正文的规范性条件拆为 clause id；A 表每个 `check_id` 的“判定（子句 id）”列只列它覆盖的 clause，**不再写叙述性短语**；条件的自然语言表述与原因码统一放在本表。一个 `check_id` 可承载多个子句，逐子句独立求值、聚合为单一 verdict（任一 `fail` → `fail`；否则任一 `cannot_evaluate` → `cannot_evaluate`；否则 `pass`）。未覆盖的子句必须标 `not-checked` 并写理由，`scripts/check_three_table.py` 机械核对覆盖完整性与“A 表不含叙述性短语”。
>
> 复核签收：外部复核基线 `48128a8`（产物 `/tmp/verify-4812/REPORT_48128a8.md`，sha256 `d0f8275f9931f36da93c640ad8a070c8af7200929d0a4a685e5309268356c4e7`；本轮按其清单第 1–6 项修订，修订后版本待下一轮复核） / 2026-11-14 / A.2 指纹 `55c96288c69f`

| clause | 规则 | 子句（判定条件） | 原因码 | 承接 check_id | 子句 severity | 覆盖状态 | 规则状态 |
|---|---|---|---|---|---|---|---|
| `G-A1#1` | G-A1 | 至少一个 `Actor` | `missing_actor` | `PROJECT_MINIMAL_EXISTENCE` | `block` | checked | active |
| `G-A1#2` | G-A1 | 至少一个 `Outcome` | `missing_outcome` | `PROJECT_MINIMAL_EXISTENCE` | `block` | checked | active |
| `G-A1#3` | G-A1 | 该 `Actor` 对 `Outcome` 的 `Commitment` 存在 | `missing_commitment` | `PROJECT_MINIMAL_EXISTENCE` | `block` | checked | active |
| `G-A1#4` | G-A1 | 至少一个 `Constraint` | `missing_constraint` | `PROJECT_MINIMAL_EXISTENCE` | `block` | checked | active |
| `G-A1#5` | G-A1 | `Commitment` 的 `by`/`to` 指向已登记的 `Actor`/`Outcome` | `broken_commitment_endpoint` | `PROJECT_MINIMAL_EXISTENCE` | `block` | checked | active |
| `G-A1#6` | G-A1 | `Constraint` 作用于该 `Outcome` 或 `Commitment` | `constraint_not_applied` | `PROJECT_MINIMAL_EXISTENCE` | `block` | checked | active |
| `G-A2#1` | G-A2 | 每个管理活动/产物至少一条 `constrained_by` 指向已登记 `Constraint` | `unanchored_management_item` | `CONSTRAINT_ANCHOR_REQUIRED` | `block` | checked | active |
| `G-A2#2` | G-A2 | “管理活动/产物”为已定义节点类型 | `undefined_enum_value` | `CONSTRAINT_ANCHOR_REQUIRED` | `block` | checked（`node_type` 可选；提供时须 ∈ `management_node_type`） | active |
| `G-B1#1` | G-B1 | 每个管理项有 `process_group` 标签 | `missing_dimension` | `DUAL_DIMENSION_ANNOTATION` | `advisory` | checked | active |
| `G-B1#2` | G-B1 | 每个管理项有 `subject_group` 标签 | `missing_dimension` | `DUAL_DIMENSION_ANNOTATION` | `advisory` | checked | active |
| `G-B2#1` | G-B2 | 标签值在锚定枚举或契约扩展内 | `dimension_value_out_of_enum` | `DIMENSION_VALUE_CLOSED` | `advisory` | checked | active |
| `G-B2#2` | G-B2 | 扩展项声明 `relation ∈ subject_group_extension_relation`；`specializes`/`cross_cuts` 的 `base` ∈ 17 项基础枚举，`orthogonal_to` 可不声明 `base`；`value` 不与基础枚举重名 | `invalid_subject_group_extension / undefined_enum_value` | `DIMENSION_VALUE_CLOSED` | `advisory` | checked | active |
| `G-C1#1` | G-C1 | 每个 `Deliverable` 至少一条见证断言（`asserted_by` 正向或 `about` 反向） | `deliverable_without_assertion / dangling_reference` | `DELIVERABLE_ASSERTION_LINK` | `block` | checked | active |
| `G-C1#2` | G-C1 | 断言内容是“是什么/什么状态/满足什么条件”的明确陈述 | `assertion_without_content` | `DELIVERABLE_ASSERTION_LINK` | `block` | checked | active |
| `G-C1#3` | G-C1 | 断言 `about` 指向该交付物 | `assertion_about_mismatch` | `DELIVERABLE_ASSERTION_LINK` | `block` | checked | active |
| `G-C2#1` | G-C2 | 同一 `Subject` 同一属性不得有不相容值 | `mutually_exclusive_active_assertions` | `ASSERTION_MUTUAL_EXCLUSION` | `warn` | checked | active |
| `G-C2#2` | G-C2 | 只对 `active` 断言判不相容 | `mutually_exclusive_active_assertions` / `missing_input` / `undefined_enum_value` | `ASSERTION_MUTUAL_EXCLUSION` | `warn` | checked | active |
| `G-D1#1` | G-D1 | 变更对象是 `Commitment` 或 `Deliverable` | `missing_change_target / invalid_change_target` | `CHANGE_CONSTRAINT_LINK` | `block` | checked | active |
| `G-D1#2` | G-D1 | 变更提议至少一条边指向 `Constraint` | `missing_constraint_link` | `CHANGE_CONSTRAINT_LINK` | `block` | checked | active |
| `G-D1#3` | G-D1 | 边类型 ∈ `relation` 枚举 | `invalid_change_relation` | `CHANGE_CONSTRAINT_LINK` | `block` | checked | active |
| `G-D2#1` | G-D2 | 全部为 `mitigates` 时标 `assumption` 并附验证条件 | `all_improvement_without_verification` | `ALL_IMPROVEMENT_ASSUMPTION` | `warn` | checked | active |
| `G-D2#2` | G-D2 | 验证条件满足前不得作为批准依据 | `approval_basis_before_verification` | `ALL_IMPROVEMENT_ASSUMPTION` | `warn` | checked（`approval_basis`） | active |
| `G-D2#3` | G-D2 | `assumption` 为 `pending` 时须有 `approved_by`；`expired` 不得作为有效依据 | `assumption_unclosed` | `ALL_IMPROVEMENT_ASSUMPTION` | `warn` | checked（§1.9） | active |
| `G-E1#1` | G-E1 | 唯一 `accountable_by` 且指向 `HumanActor`/`LegalEntity` | `missing_accountable / multiple_accountable / unknown_accountable / accountable_not_human` | `ROLE_MINIMAL_COMPLETENESS` | `block` | checked | active |
| `G-E1#2` | G-E1 | 至少一个 `responsible_by` | `missing_responsible` | `ROLE_MINIMAL_COMPLETENESS` | `block` | checked | active |
| `G-E1#3` | G-E1 | 角色重合时有 `role_merge_declaration` | `missing_role_merge_declaration` | `ROLE_MINIMAL_COMPLETENESS` | `warn` | checked | active |
| `G-E2#1` | G-E2 | `delegated_from` 路径终至 `Accountable`，且终点类型为 `HumanActor`/`LegalEntity` | `delegation_chain_not_accountable / accountable_not_human / invalid_path / dangling_reference` | `AI_AUTONOMY_DELEGATION_AUDITABLE` | `warn` | checked | active |
| `G-E2#2` | G-E2 | 路径上断言覆盖范围/边界/撤销条件 | `assertion_incomplete` | `AI_AUTONOMY_DELEGATION_AUDITABLE` | `warn` | checked | active |
| `G-E2#3` | G-E2 | 该断言以 `assumption` 形式存在并附验证条件 | `assertion_incomplete / assumption_unclosed / dangling_reference` | `AI_AUTONOMY_DELEGATION_AUDITABLE` | `warn` | checked | active |
| `G-F1#1` | G-F1 | 执行阶段 `Project` 有 `ProjectCharter` | `missing_charter` | `PROJECT_CHARTER_EXISTENCE` | `advisory` | checked | assumption |
| `G-F1#2` | G-F1 | 章程关联 Outcome 陈述、Constraint、Accountable、启动授权 | `incomplete_charter` | `PROJECT_CHARTER_EXISTENCE` | `advisory` | checked | assumption |
| `G-F2#1` | G-F2 | 每个 `Deliverable` 有验收/移交断言 | `missing_acceptance_assertion` | `CLOSURE_ACCEPTANCE_LINK` | `advisory` | checked | assumption |
| `G-F2#2` | G-F2 | 断言关联 `Accountable` 确认 | `missing_acceptance_assertion` | `CLOSURE_ACCEPTANCE_LINK` | `advisory` | checked | assumption |
| `G-F3#1` | G-F3 | 外部采购承诺有 `Contract` 节点 | `missing_contract` | `PROCUREMENT_CONTRACT_ANCHOR` | `advisory` | checked | assumption |
| `G-F3#2` | G-F3 | 契约声明四项内容 | `incomplete_contract` | `PROCUREMENT_CONTRACT_ANCHOR` | `advisory` | checked | assumption |
| `G-F4#1` | G-F4 | 时间承诺关联依据断言 | `missing_schedule_evidence` | `SCHEDULE_EVIDENCE_LINK` | `advisory` | checked | assumption |
| `G-G1#1` | G-G1 | 每次裁剪有 `TailoringRecord` | `missing_tailoring_record` | `TAILORING_RECORD_EXISTENCE` | `advisory` | checked | assumption |
| `G-G1#2` | G-G1 | 记录声明四项内容 | `incomplete_tailoring_record` | `TAILORING_RECORD_EXISTENCE` | `advisory` | checked | assumption |
| `G-G2#1` | G-G2 | 目标规则不在不可裁剪集 | `non_trimmable_rule` | `TAILORING_NON_TRIMMABLE_SET` | `advisory` | checked | assumption |
| `G-G3#1` | G-G3 | 记录关联重新评估条件或声明“永久” | `missing_reassessment_condition` | `TAILORING_REASSESSMENT_CONDITION` | `advisory` | checked | assumption |
| `G-G3#2` | G-G3 | 声明“永久”时附理由 | `missing_reassessment_condition` | `TAILORING_REASSESSMENT_CONDITION` | `advisory` | checked | assumption |

**原因码映射**：`原因码` 列是子句与稳定 `reason` 的唯一映射表。原型只能返回本列列出的原因码；`scripts/check_three_table.py` 校验每个原因码都在 schema 第 3 节或第 1.5/1.9/1.10 条有定义，且每个 checked 子句至少有一个原因码。`G-B1` 只负责两个标签是否存在；标签值闭合由 `G-B2#1` 承接，扩展项声明合法性由 `G-B2#2` 承接，两者不得互相写入。`G-B2` 按行序判定：先看标签值是否落在基础枚举或**合法**扩展的取值域，再看每个扩展项自身是否声明合法。非法扩展的 `value` 不计入合法取值域，因此被标签引用时先命中 `G-B2#1`（`dimension_value_out_of_enum`）；未被引用或与基础枚举重名时命中 `G-B2#2`（`invalid_subject_group_extension`）。

**severity 聚合规则**：一个 `check_id` 的 verdict 由其全部子句聚合；`severity` 取失败子句中的最高级（`advisory` < `warn` < `block`），`pass` 时取 A 表声明的 severity。`reason` 取首条失败子句的原因码；verdict 聚合顺序为 `fail > cannot_evaluate > pass`，与 schema 第 1.14 条一致。这解决了 G-004：`G-E1#3` 缺失只产生 `warn`，不再把合法产物按 `block` 判死。

**悬空引用原因归属（规则子句原因优先）**：悬空引用落在规则子句的判定对象内时，返回该子句登记的原因码；只有子句原因码列显式列出 `dangling_reference` 时才返回该码（当前为 `G-C1#1`、`G-E2#1`、`G-E2#3`）。无子句承接的引用由 `validate_references()` 在全部子句 `pass` 后兜底，返回 `dangling_reference`。消费方以“check_id + reason”判别，不得只凭 `dangling_reference` 推断规则语义。

| check_id | 子句 | 悬空引用对象 | 返回 reason |
|---|---|---|---|
| `CONSTRAINT_ANCHOR_REQUIRED` | `G-A2#1` | `constrained_by` → `constraints` | `unanchored_management_item` |
| `DELIVERABLE_ASSERTION_LINK` | `G-C1#1` | `asserted_by` → `assertions` | `dangling_reference` |
| `CHANGE_CONSTRAINT_LINK` | `G-D1#1` | `target.id` → `commitments` / `deliverables` | `invalid_change_target` |
| `CHANGE_CONSTRAINT_LINK` | `G-D1#2` | `constraint` → `constraints` | `missing_constraint_link` |
| `ROLE_MINIMAL_COMPLETENESS` | `G-E1#1` | `accountable_by` → `actors` | `unknown_accountable` |
| `AI_AUTONOMY_DELEGATION_AUDITABLE` | `G-E2#1` | `delegated_from.steps[].target_id` → `actors` | `dangling_reference` |
| `AI_AUTONOMY_DELEGATION_AUDITABLE` | `G-E2#3` | `assertions` → `assertions` | `dangling_reference` |
| 其他 `check_id` | 无子句承接 | 2bis.1 中剩余引用 | `dangling_reference`（全局兜底） |

**G-A2#2 可达性**：schema 第 2、3 节已为 `commitments[]` / `deliverables[]` 声明可选 `node_type`。提供且不在 `management_node_type` 内 → `cannot_evaluate` / `undefined_object_type`；未提供视为“未断言节点类型”，不触发本子句，也不影响 `G-A2#1`。这样该子句在声明输入域内可达，且不需要把 `node_type` 变成所有样例的必填键。

### A.1 参考样例（T-011）

> 用途：作为 T-107 最小原型的验收输入。样例只按 A 表“判定（子句 id）”列执行，**不新增谓词、不改判定**；输入为谓词快照（YAML），输出为第 4.2 节三值枚举中的 `verdict` 与稳定原因码 `reason`（原因码取自 A.2 的“原因码”列）。
>
> **范围**：A 表全部 17 个 `check_id`，按 severity 分批补齐。`block` 级样例省略 `severity` / `rule_status`（原型按 `block` / `active` 校验）；`warn` 级与 `assumption` 级样例在期望输出中显式给出 `severity` 与 `rule_status`，实际 severity 以 `validation/CHECKLIST.md` 为准。
>
> **输入约定**：`commitments`、`deliverables` 等键即该 `check_id` 的量化域；样例假定输入已按规则适用范围筛选（例如 G-E1 的快照只含决策类 `Commitment`，G-A2 的快照只含管理活动/产物），检查本身不再做类型筛选。输入缺键或键不可求值时，原型应输出 `cannot_evaluate`，不得当作 `pass`。
>
> **输入 schema**：字段名与量化域由 `spec/CHECKER_INPUT_SCHEMA.md` 固定。本组样例是该 schema 的首批实例；此后新增或修改的样例必须遵循该文件，不得自行引入新字段。

**样例基线（跨轮横比锚点）**：本轮样例基线为提交 `1a42b8b`（批次 0034《复核推翻后重开缺口并修订判定层》），共 34 个样例。批次 0040 为覆盖闸门增补 23 个负例，样例数 34 → 57；批次 0042 为复核清单第 2/3/5/7 项增补 3 个样例（A.1.7-4、A.1.8-3、A.1.10-5），样例数 57 → 60。既有 34 例的输入与期望输出均未改动。此后报告的“60/60”相对批次 0042 的新基线（提交号见该批次），换基线必须在此登记新提交号与全部输入改动。相对 `1a42b8b` 的输入块改动如下，**期望输出零改动**：

| 样例 | 输入块改动 | 原因 |
|---|---|---|
| A.1.9-1 | `assumption: null` + `verification_condition: null` → `assumption: {}`；补 `actors: []` | 入口 null 归一化会把语义性 `null` 判成 `cannot_evaluate`；缺内容应由 `G-D2` 内容判定为 `fail`，且 §3 要求 `actors` |
| A.1.9-2 | 补 `actors: []` | §3 要求 `actors` |
| A.1.11-1 | 补 `outcomes: []`、`constraints: []`、`actors: []`、`assertions: []` | §3 要求这四个顶层键 |
| A.1.12-1 | 补 `actors: []` | §3 要求 `actors` |
| A.1.13-1 | 删除 `contract: null`；补 `constraints: []`、`actors: []` | 入口 null 归一化会把 `contract: null` 判成 `cannot_evaluate`；缺合同应由 `G-F3#1` 判 `fail`，且 §3 要求这两个键 |
| A.1.15-1 | 删除 `record: null`；补 `actors: []` | 同上：缺记录应由 `G-G1#1` 判 `fail`；§3 要求 `actors` |
| A.1.17-1 | 删除 `reassessment_condition: null` | 缺条件应由 `G-G3#1` 判 `fail`，不得被 null 归一化截成 `cannot_evaluate` |

#### A.1.1 `PROJECT_MINIMAL_EXISTENCE`（G-A1，`block`）

**判定依据**：A 表“四类节点均存在且 `Commitment` 的 `by` 指向 `Actor`、`to` 指向 `Outcome`”。

**样例 1（触发 → `fail`）**：`Constraint` 集为空。

```yaml
project: { id: "P-1" }
actors: [{ id: "A-1", type: "HumanActor" }]
outcomes: [{ id: "O-1" }]
commitments: [{ id: "C-1", by: "A-1", to: "O-1" }]
constraints: []
```

期望输出：

```yaml
check_id: PROJECT_MINIMAL_EXISTENCE
source_rule: G-A1
verdict: fail
reason: missing_constraint
```

**样例 2（不触发 → `pass`）**：四类节点齐备，承诺端点有效。

```yaml
project: { id: "P-2" }
actors: [{ id: "A-1", type: "HumanActor" }]
outcomes: [{ id: "O-1" }]
commitments: [{ id: "C-1", by: "A-1", to: "O-1" }]
constraints: [{ id: "K-1", constrains: "O-1" }]
```

期望输出：

```yaml
check_id: PROJECT_MINIMAL_EXISTENCE
source_rule: G-A1
verdict: pass
reason: null
```

> 边界说明：G-A1 正文要求 `Constraint` “作用于该 `Outcome` 或 `Commitment`”，该子句已由 `G-A1#6` 纳入判定（ADR-0013 / G-002）。样例 2 的 `constrains: "O-1"` 满足该子句；样例 1 在更早的“约束集为空”处即失败，故不改变本组预期。

**样例 3（触发 `G-A1#1` → `fail`）**：`Actor` 集为空。

```yaml
project: { id: "P-3" }
actors: []
outcomes: [{ id: "O-1" }]
commitments: []
constraints: [{ id: "K-1", constrains: "O-1" }]
```

期望输出：

```yaml
check_id: PROJECT_MINIMAL_EXISTENCE
source_rule: G-A1
verdict: fail
reason: missing_actor
```

**样例 4（触发 `G-A1#2` → `fail`）**：`Outcome` 集为空。

```yaml
project: { id: "P-4" }
actors: [{ id: "A-1", type: "HumanActor" }]
outcomes: []
commitments: []
constraints: []
```

期望输出：

```yaml
check_id: PROJECT_MINIMAL_EXISTENCE
source_rule: G-A1
verdict: fail
reason: missing_outcome
```

**样例 5（触发 `G-A1#3` → `fail`）**：三类节点齐备但没有任何 `Commitment`。

```yaml
project: { id: "P-5" }
actors: [{ id: "A-1", type: "HumanActor" }]
outcomes: [{ id: "O-1" }]
commitments: []
constraints: [{ id: "K-1", constrains: "O-1" }]
```

期望输出：

```yaml
check_id: PROJECT_MINIMAL_EXISTENCE
source_rule: G-A1
verdict: fail
reason: missing_commitment
```

**样例 6（触发 `G-A1#5` → `fail`）**：`Commitment.to` 指向未登记的 `Outcome`。

```yaml
project: { id: "P-6" }
actors: [{ id: "A-1", type: "HumanActor" }]
outcomes: [{ id: "O-1" }]
commitments: [{ id: "C-1", by: "A-1", to: "O-9" }]
constraints: [{ id: "K-1", constrains: "C-1" }]
```

期望输出：

```yaml
check_id: PROJECT_MINIMAL_EXISTENCE
source_rule: G-A1
verdict: fail
reason: broken_commitment_endpoint
```

**样例 7（触发 `G-A1#6` → `fail`）**：`Constraint` 未作用于任何已登记的 `Outcome`/`Commitment`。

```yaml
project: { id: "P-7" }
actors: [{ id: "A-1", type: "HumanActor" }]
outcomes: [{ id: "O-1" }]
commitments: [{ id: "C-1", by: "A-1", to: "O-1" }]
constraints: [{ id: "K-1", constrains: "C-9" }]
```

期望输出：

```yaml
check_id: PROJECT_MINIMAL_EXISTENCE
source_rule: G-A1
verdict: fail
reason: constraint_not_applied
```

#### A.1.2 `CONSTRAINT_ANCHOR_REQUIRED`（G-A2，`block`）

**判定依据**：A 表“每个管理活动/产物至少有一条 `constrained_by` 边指向已登记 `Constraint`”。

**样例 1（触发 → `fail`）**：一个管理产物没有约束锚定。

```yaml
commitments: [{ id: "C-1", constrained_by: ["K-1"] }]
deliverables: [{ id: "D-1", constrained_by: [] }]
constraints: [{ id: "K-1" }]
```

期望输出：

```yaml
check_id: CONSTRAINT_ANCHOR_REQUIRED
source_rule: G-A2
verdict: fail
reason: unanchored_management_item
```

**样例 2（不触发 → `pass`）**：每个管理活动/产物都有非空约束锚定。

```yaml
commitments: [{ id: "C-1", constrained_by: ["K-1", "K-2"] }]
deliverables: [{ id: "D-1", constrained_by: ["K-1"] }]
constraints: [{ id: "K-1" }, { id: "K-2" }]
```

期望输出：

```yaml
check_id: CONSTRAINT_ANCHOR_REQUIRED
source_rule: G-A2
verdict: pass
reason: null
```

**样例 3（触发 `G-A2#2` → `cannot_evaluate`）**：管理产物声明了未定义的节点类型。

```yaml
commitments: [{ id: "C-1", constrained_by: ["K-1"] }]
deliverables: [{ id: "D-1", node_type: "MysteryNode", constrained_by: ["K-1"] }]
constraints: [{ id: "K-1" }]
```

期望输出：

```yaml
check_id: CONSTRAINT_ANCHOR_REQUIRED
source_rule: G-A2
verdict: cannot_evaluate
reason: undefined_enum_value
```

#### A.1.3 `DELIVERABLE_ASSERTION_LINK`（G-C1，`block`）

**判定依据**：A 表“每个 `Deliverable` 至少有一条 `asserted_by` 边指向 `Assertion`”。

**样例 1（触发 → `fail`）**：交付物没有任何断言。

```yaml
deliverables: [{ id: "D-1", asserted_by: [] }]
assertions: [{ id: "S-1", about: "D-2" }]
```

期望输出：

```yaml
check_id: DELIVERABLE_ASSERTION_LINK
source_rule: G-C1
verdict: fail
reason: deliverable_without_assertion
```

**样例 2（不触发 → `pass`）**：每个交付物至少关联一条断言。

```yaml
deliverables: [
  { id: "D-1", asserted_by: ["S-1"] },
  { id: "D-2", asserted_by: ["S-2", "S-3"] }
]
assertions: [
  { id: "S-1", about: "D-1", statement_kind: "what", statement: "交付物为可执行的验收报告" },
  { id: "S-2", about: "D-2", statement_kind: "state", statement: "交付物处于已审核状态" },
  { id: "S-3", about: "D-2", statement_kind: "condition", statement: "交付物满足全部验收判据" }
]
```

期望输出：

```yaml
check_id: DELIVERABLE_ASSERTION_LINK
source_rule: G-C1
verdict: pass
reason: null
```

> 边界说明（ADR-0013 / G-005）：原样例 2 的断言只有 `id`、无任何内容，仍期望 `pass`；该期望与 G-C1 正文不一致，已按裁定推翻。现在被引用断言必须满足 `G-C1#2`（`statement` 非空且 `statement_kind ∈ statement_kind`）与 `G-C1#3`（`about` 指向该交付物）。`G-C1#1` 的见证断言可由 `asserted_by` 正向边或 `about` 反向边任一成立（D5）。

**样例 3（触发 `G-C1#2` → `fail`）**：被引用的断言没有任何内容。

```yaml
deliverables: [{ id: "D-1", asserted_by: ["S-1"] }]
assertions: [{ id: "S-1", about: "D-1" }]
```

期望输出：

```yaml
check_id: DELIVERABLE_ASSERTION_LINK
source_rule: G-C1
verdict: fail
reason: assertion_without_content
```

**样例 4（触发 `G-C1#3` → `fail`）**：断言的内容指向另一交付物。

```yaml
deliverables: [{ id: "D-1", asserted_by: ["S-1"] }]
assertions: [
  { id: "S-1", about: "D-2", statement_kind: "what", statement: "交付物为可执行的验收报告" }
]
```

期望输出：

```yaml
check_id: DELIVERABLE_ASSERTION_LINK
source_rule: G-C1
verdict: fail
reason: assertion_about_mismatch
```

#### A.1.4 `CHANGE_CONSTRAINT_LINK`（G-D1，`block`）

**判定依据**：A 表“变更的 `target.type ∈ change_target_type` 且 `target.id` 解析到对应集合；至少有一条边指向 `Constraint`，且边类型 ∈ `relation`”。

**样例 1（触发 → `fail`）**：变更使用了枚举外的关系类型。

```yaml
changes: [
  { id: "CH-1", target: { type: "Deliverable", id: "D-1" }, constraint: "K-1", relation: "affects" }
]
constraints: [{ id: "K-1" }]
commitments: []
deliverables: [{ id: "D-1" }]
```

期望输出：

```yaml
check_id: CHANGE_CONSTRAINT_LINK
source_rule: G-D1
verdict: fail
reason: invalid_change_relation
```

**样例 2（不触发 → `pass`）**：每个变更都锚定约束、对象类型合法且关系类型合法。

```yaml
changes: [
  { id: "CH-1", target: { type: "Commitment", id: "C-1" }, constraint: "K-1", relation: "mitigates" },
  { id: "CH-2", target: { type: "Deliverable", id: "D-1" }, constraint: "K-2", relation: "trades_off" }
]
commitments: [{ id: "C-1" }]
deliverables: [{ id: "D-1" }]
constraints: [{ id: "K-1" }, { id: "K-2" }]
```

期望输出：

```yaml
check_id: CHANGE_CONSTRAINT_LINK
source_rule: G-D1
verdict: pass
reason: null
```

> 边界说明（ADR-0013 / G-006）：G-D1 正文把变更提议限定为对 `Commitment` 或 `Deliverable` 的提议，原判定列缺少该对象类型谓词，任何变更提议都判 `pass`。现由 `G-D1#1` 承接：`target.type` 越界或 `target.id` 解析失败 → `invalid_change_target`；缺 `target` → `missing_change_target`。

**样例 3（触发 `G-D1#1` → `fail`）**：变更没有 `target`。

```yaml
changes: [{ id: "CH-1", constraint: "K-1", relation: "mitigates" }]
commitments: []
deliverables: []
constraints: [{ id: "K-1" }]
```

期望输出：

```yaml
check_id: CHANGE_CONSTRAINT_LINK
source_rule: G-D1
verdict: fail
reason: missing_change_target
```

**样例 4（触发 `G-D1#2` → `fail`）**：变更没有指向任何已登记 `Constraint` 的边。

```yaml
changes: [
  { id: "CH-1", target: { type: "Deliverable", id: "D-1" }, constraint: "K-9", relation: "mitigates" }
]
commitments: []
deliverables: [{ id: "D-1" }]
constraints: [{ id: "K-1" }]
```

期望输出：

```yaml
check_id: CHANGE_CONSTRAINT_LINK
source_rule: G-D1
verdict: fail
reason: missing_constraint_link
```

#### A.1.5 `ROLE_MINIMAL_COMPLETENESS`（G-E1，`block`）

**判定依据**：A 表“每个决策类 `Commitment` 有唯一 `accountable_by` 指向 `HumanActor`/`LegalEntity`，且至少一个 `responsible_by`；重合时有 `role_merge_declaration`”。

**样例 1（触发 → `fail`）**：`Accountable` 落在 `AIActor` 上。

```yaml
actors: [
  { id: "A-1", type: "AIActor" },
  { id: "A-2", type: "HumanActor" }
]
commitments: [
  { id: "C-1", accountable_by: "A-1", responsible_by: ["A-2"] }
]
```

期望输出：

```yaml
check_id: ROLE_MINIMAL_COMPLETENESS
source_rule: G-E1
verdict: fail
reason: accountable_not_human
```

**样例 2（不触发 → `pass`）**：唯一人类 `Accountable` 与至少一个 `Responsible`，二者不重合。

```yaml
actors: [
  { id: "A-1", type: "HumanActor" },
  { id: "A-2", type: "AIActor" }
]
commitments: [
  { id: "C-1", accountable_by: "A-1", responsible_by: ["A-2"] }
]
```

期望输出：

```yaml
check_id: ROLE_MINIMAL_COMPLETENESS
source_rule: G-E1
verdict: pass
reason: null
```

> 边界说明：`Accountable` 与 `Responsible` 重合但缺 `role_merge_declaration` 的子情形，按 A.2 的 `G-E1#3` 判 `warn`，不再与本组 `block` 样例混判（ADR-0013 / G-004）。该子情形样例待 T-100 关闭时补充；在此之前，本组两个样例的预期不变。

**样例 3（触发 `G-E1#2` → `fail`）**：承诺没有 `Responsible`。

```yaml
actors: [{ id: "A-1", type: "HumanActor" }]
commitments: [{ id: "C-1", accountable_by: "A-1", responsible_by: [] }]
```

期望输出：

```yaml
check_id: ROLE_MINIMAL_COMPLETENESS
source_rule: G-E1
verdict: fail
reason: missing_responsible
```

**样例 4（触发 `G-E1#3` → `fail`，`warn`）**：`Accountable` 与 `Responsible` 重合且未声明。

```yaml
actors: [{ id: "A-1", type: "HumanActor" }]
commitments: [{ id: "C-1", accountable_by: "A-1", responsible_by: ["A-1"] }]
```

期望输出：

```yaml
check_id: ROLE_MINIMAL_COMPLETENESS
source_rule: G-E1
severity: warn
verdict: fail
reason: missing_role_merge_declaration
```

#### A.1.6 `DUAL_DIMENSION_ANNOTATION`（G-B1，`advisory` / `active`）

**判定依据**：A 表“每个管理项携带 `process_group` 与 `subject_group` 两个标签且值在枚举内”。本组样例只针对**标签缺失**这一触发条件；值集违法由 A.1.7（G-B2）覆盖，避免两组样例重复同一条件，两项的判定列均不改动。

**样例 1（触发 → `fail`）**：第二个管理项缺 `subject_group`。

```yaml
management_items:
  - { id: "M-1", process_group: "managing-delivery", subject_group: "planning" }
  - { id: "M-2", process_group: "closing" }
```

期望输出：

```yaml
check_id: DUAL_DIMENSION_ANNOTATION
source_rule: G-B1
severity: advisory
rule_status: active
verdict: fail
reason: missing_dimension
```

**样例 2（不触发 → `pass`）**：两个管理项均携带双标签。

```yaml
management_items:
  - { id: "M-1", process_group: "managing-delivery", subject_group: "planning" }
  - { id: "M-2", process_group: "closing", subject_group: "lessons-learned" }
```

期望输出：

```yaml
check_id: DUAL_DIMENSION_ANNOTATION
source_rule: G-B1
severity: advisory
rule_status: active
verdict: pass
reason: null
```

**样例 3（触发 `G-B1#1` → `fail`）**：第二个管理项缺 `process_group`。

```yaml
management_items:
  - { id: "M-1", process_group: "managing-delivery", subject_group: "planning" }
  - { id: "M-2", subject_group: "lessons-learned" }
```

期望输出：

```yaml
check_id: DUAL_DIMENSION_ANNOTATION
source_rule: G-B1
severity: advisory
rule_status: active
verdict: fail
reason: missing_dimension
```

#### A.1.7 `DIMENSION_VALUE_CLOSED`（G-B2，`advisory` / `active`）

**判定依据**：A 表“标签值 ∈ 所锚定标准的枚举 ∪ 契约声明的 `subject_group_extension`”。本组样例覆盖“基础枚举内 / 枚举外”两种；`subject_group_extension` 分支依赖接口契约的槽位声明，不在此二例中固化。

**样例 1（触发 → `fail`）**：`subject_group` 使用了基础枚举外的自定义值。

```yaml
management_items:
  - { id: "M-1", process_group: "managing-delivery", subject_group: "innovation" }
```

期望输出：

```yaml
check_id: DIMENSION_VALUE_CLOSED
source_rule: G-B2
severity: advisory
rule_status: active
verdict: fail
reason: dimension_value_out_of_enum
```

**样例 2（不触发 → `pass`）**：两个标签值均在基础枚举内。

```yaml
management_items:
  - { id: "M-1", process_group: "initiating", subject_group: "planning" }
  - { id: "M-2", process_group: "closing", subject_group: "lessons-learned" }
```

期望输出：

```yaml
check_id: DIMENSION_VALUE_CLOSED
source_rule: G-B2
severity: advisory
rule_status: active
verdict: pass
reason: null
```

**样例 3（触发 `G-B2#2` → `fail`）**：`subject_group_extension` 缺少合法的 `base` 归属。

```yaml
management_items:
  - { id: "M-1", process_group: "initiating", subject_group: "planning" }
subject_group_extension:
  - { value: "innovation", relation: "specializes" }
```

期望输出：

```yaml
check_id: DIMENSION_VALUE_CLOSED
source_rule: G-B2
severity: advisory
rule_status: active
verdict: fail
reason: invalid_subject_group_extension
```

**样例 4（`orthogonal_to` 合法 → `pass`）**：正交扩展不要求 `base` 归属，且 `value` 不与基础枚举重名。

```yaml
management_items:
  - { id: "M-1", process_group: "initiating", subject_group: "innovation" }
subject_group_extension:
  - { value: "innovation", relation: "orthogonal_to" }
```

期望输出：

```yaml
check_id: DIMENSION_VALUE_CLOSED
source_rule: G-B2
severity: advisory
rule_status: active
verdict: pass
reason: null
```

#### A.1.8 `ASSERTION_MUTUAL_EXCLUSION`（G-C2，`warn` / `active`）

**判定依据**：A 表“不存在两条 `active` 断言对同一 `Subject` 同一属性给出不相容值”；G-C2 要求冲突时同时呈现两条断言，不得静默择一。

**样例 1（触发 → `fail`）**：同一交付物的两条 `active` 断言对 `status` 给出不相容值。

```yaml
deliverables: [{ id: "D-1" }]
assertions:
  - { id: "S-1", deliverable: "D-1", subject: "D-1", property: "status", value: "accepted", state: "active" }
  - { id: "S-2", deliverable: "D-1", subject: "D-1", property: "status", value: "rejected", state: "active" }
```

期望输出：

```yaml
check_id: ASSERTION_MUTUAL_EXCLUSION
source_rule: G-C2
severity: warn
rule_status: active
verdict: fail
reason: mutually_exclusive_active_assertions
```

**样例 2（不触发 → `pass`）**：两条 `active` 断言描述不同属性，不构成互斥。

```yaml
deliverables: [{ id: "D-1" }]
assertions:
  - { id: "S-1", deliverable: "D-1", subject: "D-1", property: "status", value: "accepted", state: "active" }
  - { id: "S-2", deliverable: "D-1", subject: "D-1", property: "acceptance_date", value: "2026-11-14", state: "active" }
```

期望输出：

```yaml
check_id: ASSERTION_MUTUAL_EXCLUSION
source_rule: G-C2
severity: warn
rule_status: active
verdict: pass
reason: null
```

**样例 3（`G-C2#2` 守卫 → `pass`）**：同 `Subject` 同属性取值冲突，但其中一条断言为 `inactive`，不参与互斥判定。

```yaml
deliverables: [{ id: "D-1" }]
assertions:
  - { id: "S-1", deliverable: "D-1", subject: "D-1", property: "status", value: "accepted", state: "active" }
  - { id: "S-2", deliverable: "D-1", subject: "D-1", property: "status", value: "rejected", state: "inactive" }
```

期望输出：

```yaml
check_id: ASSERTION_MUTUAL_EXCLUSION
source_rule: G-C2
severity: warn
rule_status: active
verdict: pass
reason: null
```

**样例 4（触发 `G-C2#2` → `cannot_evaluate`）**：断言缺少 `state`，无法判定是否参与互斥。

```yaml
deliverables: [{ id: "D-1" }]
assertions:
  - { id: "S-1", deliverable: "D-1", subject: "D-1", property: "status", value: "accepted", state: "active" }
  - { id: "S-2", deliverable: "D-1", subject: "D-1", property: "status", value: "rejected" }
```

期望输出：

```yaml
check_id: ASSERTION_MUTUAL_EXCLUSION
source_rule: G-C2
severity: warn
rule_status: active
verdict: cannot_evaluate
reason: missing_input
```

#### A.1.9 `ALL_IMPROVEMENT_ASSUMPTION`（G-D2，`warn` / `active`）

**判定依据**：A 表“若全部关系为 `mitigates` 而无 `trades_off`/`exacerbates`，则变更被标记为 `assumption` 且携带验证条件”。样例用变更节点上的 `assumption` 与 `verification_condition` 表示该标记；字段位置为样例约定，判定条件本身不变。

**样例 1（触发 → `fail`）**：全改善声明未附验证条件。

```yaml
changes:
  - id: "CH-1"
    relations: ["mitigates", "mitigates"]
    assumption: {}
actors: []
```

期望输出：

```yaml
check_id: ALL_IMPROVEMENT_ASSUMPTION
source_rule: G-D2
severity: warn
rule_status: active
verdict: fail
reason: all_improvement_without_verification
```

**样例 2（不触发 → `pass`）**：全改善声明已降级为 `assumption` 并附验证条件。

```yaml
changes:
  - id: "CH-1"
    relations: ["mitigates", "mitigates"]
    assumption: "全改善声明"
    verification_condition: "独立复核显示没有约束被恶化"
actors: []
```

期望输出：

```yaml
check_id: ALL_IMPROVEMENT_ASSUMPTION
source_rule: G-D2
severity: warn
rule_status: active
verdict: pass
reason: null
```

**样例 3（触发 `G-D2#2` → `fail`）**：验证未完成即把该变更写入批准依据。

```yaml
changes:
  - id: "CH-1"
    relations: ["mitigates"]
    assumption:
      status: "pending"
      approved_by: "A-1"
      verification_condition: "独立复核显示没有约束被恶化"
    verification_condition: "独立复核显示没有约束被恶化"
    approval_basis: "以该变更作为批准依据"
actors: [{ id: "A-1", type: "HumanActor" }]
```

期望输出：

```yaml
check_id: ALL_IMPROVEMENT_ASSUMPTION
source_rule: G-D2
severity: warn
rule_status: active
verdict: fail
reason: approval_basis_before_verification
```

**样例 4（触发 `G-D2#3` → `cannot_evaluate`）**：assumption 已过期。

```yaml
changes:
  - id: "CH-1"
    relations: ["mitigates"]
    assumption:
      status: "expired"
      verification_condition: "独立复核显示没有约束被恶化"
    verification_condition: "独立复核显示没有约束被恶化"
actors: []
```

期望输出：

```yaml
check_id: ALL_IMPROVEMENT_ASSUMPTION
source_rule: G-D2
severity: warn
rule_status: active
verdict: cannot_evaluate
reason: assumption_unclosed
```

#### A.1.10 `AI_AUTONOMY_DELEGATION_AUDITABLE`（G-E2，`warn` / `active`）

**判定依据**：A 表“自治权节点有 `delegated_from` 路径终至 `Accountable`，且链上有 `Assertion` 声明范围/边界/撤销条件”。路径用 schema 第 1.10 条的对象表示，`steps[].target_id` 指向下一节点；单跳链是 `steps` 长度为 1 的合法情形。不再接受扁平字符串写法。

**样例 1（触发 → `fail`）**：委托链终止在另一个 `AIActor`，未到达 `Accountable`。

```yaml
actors:
  - { id: "A-1", type: "AIActor" }
  - { id: "A-2", type: "AIActor" }
autonomy_grants:
  - id: "AG-1"
    actor: "A-1"
    delegated_from:
      start: "A-1"
      steps:
        - { relation: "delegated_from", direction: "out", target_type: "Actor", target_id: "A-2" }
      reach: "accountable"
    assertions: ["S-1"]
assertions:
  - { id: "S-1", covers: ["scope", "boundary", "revocation"] }
```

期望输出：

```yaml
check_id: AI_AUTONOMY_DELEGATION_AUDITABLE
source_rule: G-E2
severity: warn
rule_status: active
verdict: fail
reason: delegation_chain_not_accountable
```

**样例 2（不触发 → `pass`）**：链终点为 `Accountable`，且断言覆盖范围、边界与撤销条件。

```yaml
actors:
  - { id: "A-1", type: "AIActor" }
  - { id: "A-2", type: "HumanActor", accountable: true }
autonomy_grants:
  - id: "AG-1"
    actor: "A-1"
    delegated_from:
      start: "A-1"
      steps:
        - { relation: "delegated_from", direction: "out", target_type: "Actor", target_id: "A-2" }
      reach: "accountable"
    assertions: ["S-1"]
assertions:
  - { id: "S-1", covers: ["scope", "boundary", "revocation"], kind: "assumption", verification_condition: "季度审计确认委托边界未被突破" }
```

期望输出：

```yaml
check_id: AI_AUTONOMY_DELEGATION_AUDITABLE
source_rule: G-E2
severity: warn
rule_status: active
verdict: pass
reason: null
```

> 边界说明（ADR-0013 / G-003）：G-E2 正文要求该 `Assertion` 以 `assumption` 形式存在并附验证条件。原判定列只检查 `covers`，样例 2 因此缺 `kind` 仍期望 `pass`；现由 `G-E2#3` 承接，样例 2 已补 `kind: assumption` 与 `verification_condition`。路径可达性由 `G-E2#1` 用 schema 第 1.10 条的路径表示承接，不再依赖“终至”的自然语言表述。

**样例 3（触发 `G-E2#2` → `fail`）**：断言只覆盖范围与边界，缺撤销条件。

```yaml
actors:
  - { id: "A-1", type: "AIActor" }
  - { id: "A-2", type: "HumanActor", accountable: true }
autonomy_grants:
  - id: "AG-1"
    actor: "A-1"
    delegated_from:
      start: "A-1"
      steps:
        - { relation: "delegated_from", direction: "out", target_type: "Actor", target_id: "A-2" }
      reach: "accountable"
    assertions: ["S-1"]
assertions:
  - { id: "S-1", covers: ["scope", "boundary"], kind: "assumption", verification_condition: "季度审计确认委托边界未被突破" }
```

期望输出：

```yaml
check_id: AI_AUTONOMY_DELEGATION_AUDITABLE
source_rule: G-E2
severity: warn
rule_status: active
verdict: fail
reason: assertion_incomplete
```

**样例 4（触发 `G-E2#3` → `cannot_evaluate`）**：断言所依赖的 assumption 已过期。

```yaml
actors:
  - { id: "A-1", type: "AIActor" }
  - { id: "A-2", type: "HumanActor", accountable: true }
autonomy_grants:
  - id: "AG-1"
    actor: "A-1"
    delegated_from:
      start: "A-1"
      steps:
        - { relation: "delegated_from", direction: "out", target_type: "Actor", target_id: "A-2" }
      reach: "accountable"
    assertions: ["S-1"]
assertions:
  - id: "S-1"
    covers: ["scope", "boundary", "revocation"]
    kind: "assumption"
    verification_condition: "季度审计确认委托边界未被突破"
    assumption: { status: "expired" }
```

期望输出：

```yaml
check_id: AI_AUTONOMY_DELEGATION_AUDITABLE
source_rule: G-E2
severity: warn
rule_status: active
verdict: cannot_evaluate
reason: assumption_unclosed
```

**样例 5（触发 `G-E2#1` → `fail`）**：委托链终点是 `AIActor`，即使标注 `accountable: true` 也不能承担问责。

```yaml
actors:
  - { id: "A-1", type: "AIActor" }
  - { id: "A-2", type: "AIActor", accountable: true }
autonomy_grants:
  - id: "AG-1"
    actor: "A-1"
    delegated_from:
      start: "A-1"
      steps:
        - { relation: "delegated_from", direction: "out", target_type: "Actor", target_id: "A-2" }
      reach: "accountable"
    assertions: ["S-1"]
assertions:
  - id: "S-1"
    covers: ["scope", "boundary", "revocation"]
    kind: "assumption"
    verification_condition: "季度审计确认委托边界未被突破"
```

期望输出：

```yaml
check_id: AI_AUTONOMY_DELEGATION_AUDITABLE
source_rule: G-E2
severity: warn
rule_status: active
verdict: fail
reason: accountable_not_human
```

#### A.1.11 `PROJECT_CHARTER_EXISTENCE`（G-F1，`advisory` / `assumption`）

**判定依据**：A 表“进入执行阶段的 `Project` 有 `ProjectCharter`，且关联 Outcome 陈述、`Constraint`、`Accountable`、启动授权 `Assertion`”。样例假定输入只含已进入执行阶段的项目；`assumption` 期间输出 `advisory`。

**样例 1（触发 → `fail`）**：执行阶段项目没有任何 `ProjectCharter`。

```yaml
projects:
  - { id: "P-1", stage: "executing" }
charters: []
outcomes: []
constraints: []
actors: []
assertions: []
```

期望输出：

```yaml
check_id: PROJECT_CHARTER_EXISTENCE
source_rule: G-F1
severity: advisory
rule_status: assumption
verdict: fail
reason: missing_charter
```

**样例 2（不触发 → `pass`）**：章程存在且四项最小关联齐备。

```yaml
projects:
  - { id: "P-1", stage: "executing" }
charters:
  - id: "PC-1"
    project: "P-1"
    outcomes: ["O-1"]
    constraints: ["K-1"]
    accountable: "A-1"
    authorizing_assertion: "S-1"
outcomes:
  - { id: "O-1" }
constraints:
  - { id: "K-1" }
actors:
  - { id: "A-1", type: "HumanActor" }
assertions:
  - { id: "S-1" }
```

期望输出：

```yaml
check_id: PROJECT_CHARTER_EXISTENCE
source_rule: G-F1
severity: advisory
rule_status: assumption
verdict: pass
reason: null
```

**样例 3（触发 `G-F1#2` → `fail`）**：章程缺少启动授权断言。

```yaml
projects:
  - { id: "P-1", stage: "executing" }
charters:
  - id: "PC-1"
    project: "P-1"
    outcomes: ["O-1"]
    constraints: ["K-1"]
    accountable: "A-1"
outcomes: [{ id: "O-1" }]
constraints: [{ id: "K-1" }]
actors: [{ id: "A-1", type: "HumanActor" }]
assertions: []
```

期望输出：

```yaml
check_id: PROJECT_CHARTER_EXISTENCE
source_rule: G-F1
severity: advisory
rule_status: assumption
verdict: fail
reason: incomplete_charter
```

#### A.1.12 `CLOSURE_ACCEPTANCE_LINK`（G-F2，`advisory` / `assumption`）

**判定依据**：A 表“每个 `Deliverable` 有‘已验收’或‘已移交’断言且关联 `Accountable` 确认”。样例假定输入只含进入收尾阶段的项目产物；确认记录用断言上的 `accountable_confirmation` 表示。

**样例 1（触发 → `fail`）**：交付物没有任何验收或移交断言。

```yaml
deliverables:
  - { id: "D-1", assertions: [] }
actors: []
```

期望输出：

```yaml
check_id: CLOSURE_ACCEPTANCE_LINK
source_rule: G-F2
severity: advisory
rule_status: assumption
verdict: fail
reason: missing_acceptance_assertion
```

**样例 2（不触发 → `pass`）**：存在“已验收”断言且关联 `Accountable` 确认。

```yaml
deliverables:
  - id: "D-1"
    assertions:
      - { id: "S-1", statement: "已验收", accountable_confirmation: "A-1" }
actors:
  - { id: "A-1", type: "HumanActor" }
```

期望输出：

```yaml
check_id: CLOSURE_ACCEPTANCE_LINK
source_rule: G-F2
severity: advisory
rule_status: assumption
verdict: pass
reason: null
```

**样例 3（触发 `G-F2#2` → `fail`）**：存在“已验收”断言，但没有 `Accountable` 确认。

```yaml
deliverables:
  - id: "D-1"
    assertions:
      - { id: "S-1", statement: "已验收" }
actors:
  - { id: "A-1", type: "HumanActor" }
```

期望输出：

```yaml
check_id: CLOSURE_ACCEPTANCE_LINK
source_rule: G-F2
severity: advisory
rule_status: assumption
verdict: fail
reason: missing_acceptance_assertion
```

#### A.1.13 `PROCUREMENT_CONTRACT_ANCHOR`（G-F3，`advisory` / `assumption`）

**判定依据**：A 表“每个外部采购承诺有 `Contract` 节点，声明交付物形态、验收判据、约束锚定、`Accountable` 签署”。样例以 `procurement: external` 标记外部采购承诺。

**样例 1（触发 → `fail`）**：外部采购承诺没有合同锚定。

```yaml
commitments:
  - { id: "C-1", procurement: "external" }
contracts: []
constraints: []
actors: []
```

期望输出：

```yaml
check_id: PROCUREMENT_CONTRACT_ANCHOR
source_rule: G-F3
severity: advisory
rule_status: assumption
verdict: fail
reason: missing_contract
```

**样例 2（不触发 → `pass`）**：合同存在且四项最小声明齐备。

```yaml
commitments:
  - { id: "C-1", procurement: "external", contract: "CT-1" }
contracts:
  - id: "CT-1"
    deliverable_form: "硬件交付"
    acceptance_criteria: "验收测试通过"
    constrained_by: ["K-1"]
    accountable_signature: "A-1"
constraints:
  - { id: "K-1" }
actors:
  - { id: "A-1", type: "HumanActor" }
```

期望输出：

```yaml
check_id: PROCUREMENT_CONTRACT_ANCHOR
source_rule: G-F3
severity: advisory
rule_status: assumption
verdict: pass
reason: null
```

**样例 3（触发 `G-F3#2` → `fail`）**：合同存在但缺少约束锚定与签署。

```yaml
commitments:
  - { id: "C-1", procurement: "external", contract: "CT-1" }
contracts:
  - id: "CT-1"
    deliverable_form: "硬件交付"
    acceptance_criteria: "验收测试通过"
constraints: []
actors: []
```

期望输出：

```yaml
check_id: PROCUREMENT_CONTRACT_ANCHOR
source_rule: G-F3
severity: advisory
rule_status: assumption
verdict: fail
reason: incomplete_contract
```

#### A.1.14 `SCHEDULE_EVIDENCE_LINK`（G-F4，`advisory` / `assumption`）

**判定依据**：A 表“每个时间承诺至少关联一条依据断言（估算方法/历史数据/外部强加出处）”。样例以 `deadline` 触发适用性，以 `evidence_assertions` 表示依据。

**样例 1（触发 → `fail`）**：带截止日期的时间承诺没有依据断言。

```yaml
commitments:
  - { id: "C-1", deadline: "2026-12-31", evidence_assertions: [] }
```

期望输出：

```yaml
check_id: SCHEDULE_EVIDENCE_LINK
source_rule: G-F4
severity: advisory
rule_status: assumption
verdict: fail
reason: missing_schedule_evidence
```

**样例 2（不触发 → `pass`）**：时间承诺关联一条历史数据依据。

```yaml
commitments:
  - id: "C-1"
    deadline: "2026-12-31"
    evidence_assertions:
      - { id: "S-1", basis: "historical_data", source: "过往三个同类项目" }
```

期望输出：

```yaml
check_id: SCHEDULE_EVIDENCE_LINK
source_rule: G-F4
severity: advisory
rule_status: assumption
verdict: pass
reason: null
```

#### A.1.15 `TAILORING_RECORD_EXISTENCE`（G-G1，`advisory` / `assumption`）

**判定依据**：A 表“每次裁剪有 `TailoringRecord`，声明被裁剪规则、理由、适用范围、批准者”。

**样例 1（触发 → `fail`）**：存在裁剪动作，但没有对应记录。

```yaml
tailoring_actions:
  - { id: "TA-1" }
tailoring_records: []
actors: []
```

期望输出：

```yaml
check_id: TAILORING_RECORD_EXISTENCE
source_rule: G-G1
severity: advisory
rule_status: assumption
verdict: fail
reason: missing_tailoring_record
```

**样例 2（不触发 → `pass`）**：裁剪动作有记录，且四项声明齐备。

```yaml
tailoring_actions:
  - { id: "TA-1", record: "TR-1" }
tailoring_records:
  - id: "TR-1"
    trimmed_rule: "G-B1"
    rationale: "受监管环境需要双维标签"
    scope: "本项目全部管理项"
    approver: "A-1"
actors:
  - { id: "A-1", type: "HumanActor" }
```

期望输出：

```yaml
check_id: TAILORING_RECORD_EXISTENCE
source_rule: G-G1
severity: advisory
rule_status: assumption
verdict: pass
reason: null
```

**样例 3（触发 `G-G1#2` → `fail`）**：裁剪记录存在但缺少适用范围与批准者。

```yaml
tailoring_actions:
  - { id: "TA-1", record: "TR-1" }
tailoring_records:
  - id: "TR-1"
    trimmed_rule: "G-B1"
    rationale: "受监管环境需要双维标签"
actors: []
```

期望输出：

```yaml
check_id: TAILORING_RECORD_EXISTENCE
source_rule: G-G1
severity: advisory
rule_status: assumption
verdict: fail
reason: incomplete_tailoring_record
```

#### A.1.16 `TAILORING_NON_TRIMMABLE_SET`（G-G2，`advisory` / `assumption`）

**判定依据**：A 表“目标规则 ∉ {G-A1, G-A2, G-C1, G-D1, G-E1}”。

**样例 1（触发 → `fail`）**：裁剪目标落在不可裁剪集合内。

```yaml
tailoring_records:
  - { id: "TR-1", trimmed_rule: "G-A1" }
```

期望输出：

```yaml
check_id: TAILORING_NON_TRIMMABLE_SET
source_rule: G-G2
severity: advisory
rule_status: assumption
verdict: fail
reason: non_trimmable_rule
```

**样例 2（不触发 → `pass`）**：裁剪目标在不可裁剪集合之外。

```yaml
tailoring_records:
  - { id: "TR-1", trimmed_rule: "G-B1" }
```

期望输出：

```yaml
check_id: TAILORING_NON_TRIMMABLE_SET
source_rule: G-G2
severity: advisory
rule_status: assumption
verdict: pass
reason: null
```

#### A.1.17 `TAILORING_REASSESSMENT_CONDITION`（G-G3，`advisory` / `assumption`）

**判定依据**：A 表“每条记录关联至少一条重新评估条件断言，或显式声明‘永久’并附理由”。本组样例覆盖“条件断言”分支；`permanent` 分支的字段表示待原型按同一判定执行，不改变判定列。

**样例 1（触发 → `fail`）**：既无重新评估条件，也未声明永久。

```yaml
tailoring_records:
  - { id: "TR-1", permanent: false }
```

期望输出：

```yaml
check_id: TAILORING_REASSESSMENT_CONDITION
source_rule: G-G3
severity: advisory
rule_status: assumption
verdict: fail
reason: missing_reassessment_condition
```

**样例 2（不触发 → `pass`）**：关联一条重新评估条件。

```yaml
tailoring_records:
  - { id: "TR-1", reassessment_condition: "监管要求变化时", permanent: false }
```

期望输出：

```yaml
check_id: TAILORING_REASSESSMENT_CONDITION
source_rule: G-G3
severity: advisory
rule_status: assumption
verdict: pass
reason: null
```

**样例 3（触发 `G-G3#2` → `fail`）**：声明“永久”但没有附理由。

```yaml
tailoring_records:
  - { id: "TR-1", permanent: true }
```

期望输出：

```yaml
check_id: TAILORING_REASSESSMENT_CONDITION
source_rule: G-G3
severity: advisory
rule_status: assumption
verdict: fail
reason: missing_reassessment_condition
```

### B. 翻译规范（方法有关）

从规则陈述到检查条件的翻译，遵循以下六条：

**B.1 谓词化**：把陈述中的名词映射为谓词/槽位，把条件映射为逻辑表达式。映射关系登记在 `knowledge/anchored-entries.jsonl`（谓词定义）与 `spec/INTERFACE_CONTRACT_SPEC.md`（槽位定义）。

**B.2 三值逻辑**：检查条件的求值结果可以是 `true` / `false` / `unknown`。`unknown` 的处理按 `ASSUMPTION_PROTOCOL.md` 第 5 节执行，不得静默当作 `false`。

**B.3 量词显式化**：规则中的“每个”“至少一个”“不存在”必须显式翻译为全称/存在量词，不得依赖自然语言的隐含理解。

**B.4 否定与例外显式化**：规则中的“除非”“除……外”必须显式翻译为例外条件分支，不得留作自然语言的模糊地带。

**B.5 翻译说明**：每条检查项规格必须附一条翻译说明，说明自然语言陈述与逻辑条件之间的对应关系。翻译说明是 `spec/methods/deterministic-checker.md` 的一部分，不进入 `GRAMMAR.md`。

**B.6 不可翻译的处置**：若某条规则的陈述无法被翻译为可判定条件，该规则**不得**进入检查清单。正确动作是：(i) 修订规则陈述使其可判定（走 ADR）；或 (ii) 把该规则降级为 `assumption` 并附带验证条件（走 ADR）。**不得**由本方法自行“补写”逻辑条件——这是编译期幻觉的主要入口。

---
