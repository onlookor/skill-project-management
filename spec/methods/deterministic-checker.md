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
- **退化形态**：无谓词求值能力时，检查清单由人类评审执行，结论为 `符合` / `不符合` / `不适用`（见第 4.2 节）。

### 4.2 P3（结论封闭性）

**封闭枚举**：

| 运行时形态 | 结论枚举 |
|---|---|
| 确定性校验器（主形态） | `{pass, fail, cannot_evaluate}` |
| 退化形态（人类评审） | `{符合, 不符合, 不适用}` |

**封闭性论证**：

- `pass` / `fail` / `cannot_evaluate` 覆盖全部求值结果：条件式为真 → `pass`；为假 → `fail`；输入缺失或谓词不可求值 → `cannot_evaluate`。不存在第四种状态。
- `cannot_evaluate` **不等于 `pass`**。宿主不得把缺失输入当作通过（META P3 + `ASSUMPTION_PROTOCOL.md` 第 5 节）。
- 退化形态的三值同构：`符合` ↔ `pass`、`不符合` ↔ `fail`、`不适用` ↔ `cannot_evaluate`。退化形态的“不适用”必须附带缺失输入说明。

**禁止的中间态**：`待定`、`基本通过`、`大致符合`、`部分满足` 均不在封闭枚举内，不得作为结论输出。

### 4.3 severity 与规则状态的映射

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
- `grounding_ref` 保留在 `GRAMMAR.md` 中，不进入检查清单的执行路径——它是合法性锚点，不是执行前提（与 `CONSTITUTION.md` 第 7.2 级一致）。

**P5 与 `CONSTITUTION.md` 第 7 条的关系**：第 7 条约束 `GRAMMAR.md` 的规则陈述；P5 约束本方法的产物。二者是同一纪律在立法层与执行层的两次落实。

## 7. 假设与事实分离（P6）

### 7.1 产物中的表示

本方法的产物中，`grounded` 与 `assumption` 的分离通过**字段级标记**实现：

- 每个 `check_id` 规格携带 `grounding_refs` 字段，列出该检查项所依据的 `SOURCE_LEDGER.md` 条目 ID；
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

| check_id | 规则 | 输入 | 判定 | 规则状态 |
|---|---|---|---|---|
| `PROJECT_MINIMAL_EXISTENCE` | G-A1 | `Project`、`Actor`、`Outcome`、`Commitment`、`Constraint` 节点 | 四类节点均存在且 `Commitment` 的 `by` 指向 `Actor`、`to` 指向 `Outcome` | `active` |
| `CONSTRAINT_ANCHOR_REQUIRED` | G-A2 | 管理活动/产物节点、`Constraint` 节点 | 每个管理活动/产物至少有一条 `constrained_by` 边指向已登记 `Constraint` | `active` |
| `DUAL_DIMENSION_ANNOTATION` | G-B1 | 管理项节点 | 每个管理项携带 `process_group` 与 `subject_group` 两个标签且值在枚举内 | `active` |
| `DIMENSION_VALUE_CLOSED` | G-B2 | 管理项的标签值 | 标签值 ∈ 所锚定标准的枚举 ∪ 契约声明的 `subject_group_extension` | `active` |
| `DELIVERABLE_ASSERTION_LINK` | G-C1 | `Deliverable` 节点、`Assertion` 节点 | 每个 `Deliverable` 至少有一条 `asserted_by` 边指向 `Assertion` | `active` |
| `ASSERTION_MUTUAL_EXCLUSION` | G-C2 | 同一 `Deliverable` 的多条 `Assertion` | 不存在两条 `active` 断言对同一 `Subject` 同一属性给出不相容值 | `active`（`warn`） |
| `CHANGE_CONSTRAINT_LINK` | G-D1 | 变更提议节点、`Constraint` 节点 | 每个变更提议至少有一条边指向 `Constraint`，且边类型 ∈ {`mitigates`, `exacerbates`, `trades_off`} | `active` |
| `ALL_IMPROVEMENT_ASSUMPTION` | G-D2 | 变更提议的关系类型集合 | 若全部关系为 `mitigates` 而无 `trades_off`/`exacerbates`，则变更被标记为 `assumption` 且携带验证条件 | `active`（`warn`） |
| `ROLE_MINIMAL_COMPLETENESS` | G-E1 | `Commitment` 节点、`Accountable`/`Responsible` 关系 | 每个决策类 `Commitment` 有唯一 `accountable_by` 指向 `HumanActor`/`LegalEntity`，且至少一个 `responsible_by`；重合时有 `role_merge_declaration` | `active` |
| `AI_AUTONOMY_DELEGATION_AUDITABLE` | G-E2 | `AIActor` 的自治权节点、`delegated_from` 链 | 自治权节点有 `delegated_from` 链终至 `Accountable`，且链上有 `Assertion` 声明范围/边界/撤销条件 | `active`（`warn`） |
| `PROJECT_CHARTER_EXISTENCE` | G-F1 | `Project` 节点、`ProjectCharter` 节点 | 进入执行阶段的 `Project` 有 `ProjectCharter`，且关联 Outcome 陈述、Constraint、Accountable、启动授权 Assertion | `assumption` |
| `CLOSURE_ACCEPTANCE_LINK` | G-F2 | 收尾阶段的 `Deliverable`、`Assertion` | 每个 `Deliverable` 有“已验收”或“已移交”断言且关联 `Accountable` 确认 | `assumption` |
| `PROCUREMENT_CONTRACT_ANCHOR` | G-F3 | 外部采购类 `Commitment`、`Contract` 节点 | 每个外部采购承诺有 `Contract` 节点，声明交付物形态、验收判据、约束锚定、Accountable 签署 | `assumption` |
| `SCHEDULE_EVIDENCE_LINK` | G-F4 | 带 `deadline`/`milestone` 的 `Commitment`、`Assertion` | 每个时间承诺至少关联一条依据断言（估算方法/历史数据/外部强加出处） | `assumption` |
| `TAILORING_RECORD_EXISTENCE` | G-G1 | 裁剪动作、`TailoringRecord` | 每次裁剪有 `TailoringRecord`，声明被裁剪规则、理由、适用范围、批准者 | `assumption` |
| `TAILORING_NON_TRIMMABLE_SET` | G-G2 | `TailoringRecord` 的目标规则 | 目标规则 ∉ {G-A1, G-A2, G-C1, G-D1, G-E1} | `assumption` |
| `TAILORING_REASSESSMENT_CONDITION` | G-G3 | `TailoringRecord` | 每条记录关联至少一条重新评估条件断言，或显式声明“永久”并附理由 | `assumption` |

### A.1 参考样例（T-011）

> 用途：作为 T-107 最小原型的验收输入。样例只按 A 表“判定”列执行，**不新增谓词、不改判定**；输入为谓词快照（YAML），输出为第 4.2 节三值枚举中的 `verdict` 与稳定原因码 `reason`。原因码只用于样例断言，不构成新的规范词汇。
>
> **范围**：仅 A 表中规则状态 `active` 且 severity 为 `block` 的 5 个 `check_id`。这 5 项当前均为 `active` / `block`（A 表与 `validation/CHECKLIST.md` 一致）；下列期望输出省略 `rule_status: active` 与 `severity: block`，原型断言时一并校验。
>
> **输入约定**：`commitments`、`deliverables` 等键即该 `check_id` 的量化域；样例假定输入已按规则适用范围筛选（例如 G-E1 的快照只含决策类 `Commitment`，G-A2 的快照只含管理活动/产物），检查本身不再做类型筛选。输入缺键或键不可求值时，原型应输出 `cannot_evaluate`，不得当作 `pass`。

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

> 边界说明：G-A1 正文还要求 `Constraint` “作用于该 `Outcome` 或 `Commitment`”，A 表判定列只要求四类节点存在，未包含该边检查。上述样例不覆盖“`Constraint` 存在但未作用于任何 `Outcome`/`Commitment`”的情形；该子句是否纳入判定需另行裁定（T-130），本轮不改判定。

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
assertions: [{ id: "S-1" }, { id: "S-2" }, { id: "S-3" }]
```

期望输出：

```yaml
check_id: DELIVERABLE_ASSERTION_LINK
source_rule: G-C1
verdict: pass
reason: null
```

#### A.1.4 `CHANGE_CONSTRAINT_LINK`（G-D1，`block`）

**判定依据**：A 表“每个变更提议至少有一条边指向 `Constraint`，且边类型 ∈ {`mitigates`, `exacerbates`, `trades_off`}”。

**样例 1（触发 → `fail`）**：变更使用了枚举外的关系类型。

```yaml
changes: [{ id: "CH-1", constraint: "K-1", relation: "affects" }]
constraints: [{ id: "K-1" }]
```

期望输出：

```yaml
check_id: CHANGE_CONSTRAINT_LINK
source_rule: G-D1
verdict: fail
reason: invalid_change_relation
```

**样例 2（不触发 → `pass`）**：每个变更都锚定约束且关系类型合法。

```yaml
changes: [
  { id: "CH-1", constraint: "K-1", relation: "mitigates" },
  { id: "CH-2", constraint: "K-2", relation: "trades_off" }
]
constraints: [{ id: "K-1" }, { id: "K-2" }]
```

期望输出：

```yaml
check_id: CHANGE_CONSTRAINT_LINK
source_rule: G-D1
verdict: pass
reason: null
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

> 边界说明：`Accountable` 与 `Responsible` 重合但缺 `role_merge_declaration` 的子情形不纳入本组 `block` 样例。该子情形的 warn/block 拆分已登记为 T-100（ERRATA E-004），在裁定前不改变判定。

### B. 翻译规范（方法有关）

从规则陈述到检查条件的翻译，遵循以下六条：

**B.1 谓词化**：把陈述中的名词映射为谓词/槽位，把条件映射为逻辑表达式。映射关系登记在 `knowledge/anchored-entries.jsonl`（谓词定义）与 `spec/INTERFACE_CONTRACT_SPEC.md`（槽位定义）。

**B.2 三值逻辑**：检查条件的求值结果可以是 `true` / `false` / `unknown`。`unknown` 的处理按 `ASSUMPTION_PROTOCOL.md` 第 5 节执行，不得静默当作 `false`。

**B.3 量词显式化**：规则中的“每个”“至少一个”“不存在”必须显式翻译为全称/存在量词，不得依赖自然语言的隐含理解。

**B.4 否定与例外显式化**：规则中的“除非”“除……外”必须显式翻译为例外条件分支，不得留作自然语言的模糊地带。

**B.5 翻译说明**：每条检查项规格必须附一条翻译说明，说明自然语言陈述与逻辑条件之间的对应关系。翻译说明是 `spec/methods/deterministic-checker.md` 的一部分，不进入 `GRAMMAR.md`。

**B.6 不可翻译的处置**：若某条规则的陈述无法被翻译为可判定条件，该规则**不得**进入检查清单。正确动作是：(i) 修订规则陈述使其可判定（走 ADR）；或 (ii) 把该规则降级为 `assumption` 并附带验证条件（走 ADR）。**不得**由本方法自行“补写”逻辑条件——这是编译期幻觉的主要入口。

---
