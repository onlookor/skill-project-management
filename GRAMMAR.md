## 成文法

**权威关系**：本文件是立法文件。其修改须遵循 `CONSTITUTION.md` 第 4 条（ADR）与第 3 条（准入条件）。本文件不包含执行细节；执行细节见 `spec/COMPILATION_SPEC.md`。

### 使用说明

每条规则以 `G-{组}{序号}` 编号，编号一经发布永不复用（`CONSTITUTION.md` 第 7.3 级结构自包含的编号纪律）。每条规则携带以下字段：

| 字段 | 含义 |
|---|---|
| **陈述** | 自足的条件式陈述（满足 `CONSTITUTION.md` 第 7.1、7.2 级自包含） |
| `grounding_ref` | 指向 `SOURCE_LEDGER.md` 的条目 ID，且该条目的 `claim_mapping` 必须包含本条规则 |
| `provenance_note` | 形式化边界说明：哪些内容是来源的，哪些是技能自身的形式化贡献 |
| `check` | 在 `spec/COMPILATION_SPEC.md` 中注册的检查项标识 |
| `severity` | `block`（阻断）/ `warn`（告警）/ `advisory`（提示） |
| `applicability` | 规则适用条件（`CONSTITUTION.md` 第 3.5 条）。不适用时降级为 `advisory`，不失效 |

**术语**：本文件使用的机制术语（`Project`、`Actor`、`Commitment`、`Deliverable`、`Constraint`、`Outcome`、`Assertion`、`Subject`、`Accountable`、`Responsible`）在 `knowledge/anchored-entries.jsonl` 中有明确定义；`knowledge/` 条目携带各自的 `grounding_ref`。本文件的规则**不要求读者查阅外部原文即可理解**（`CONSTITUTION.md` 第 7.2 级）。

---

### 规则组 A：项目存在的充要条件

**G-A1（项目的最小本体条件）**

> 一个 `Project` 节点存在，当且仅当以下四个槽位同时被填充：至少一个 `Actor`；至少一个 `Outcome`；该 `Actor` 对 `Outcome` 的 `Commitment`；至少一个作用于该 `Outcome` 或 `Commitment` 的 `Constraint`。

- `grounding_ref`：`ProjectCO-2024`；`ISO21502-2020`
- `provenance_note`：ProjectCO 将 `Project`、`Actor`、`Commitment`、`Constraint` 置于核心层并明确其领域无关定位；ISO 21502:2020 将项目定义为受约束的、有开始和结束的独特过程。本规则将二者合取为最小存在条件，合取形式为技能自身贡献。
- `check`：`PROJECT_MINIMAL_EXISTENCE`
- `severity`：`block`
- `applicability`：任何被声明为“项目管理”的活动。无例外。

**G-A2（约束的显式登记）**

> 任何被声明为“项目管理”的活动或产物，必须关联至少一个已登记的 `Constraint` 节点。不允许存在“无约束锚定”的管理活动。

- `grounding_ref`：`ISO21502-2020`；`ProjectCO-2024`
- `provenance_note`：ISO 21502:2020 将约束管理置于项目管理的核心关注；ProjectCO 核心层包含 `Constraint`。将“约束存在”从本体条件收紧为运行时检查条件，为技能自身贡献。
- `check`：`CONSTRAINT_ANCHOR_REQUIRED`
- `severity`：`block`
- `applicability`：任何生成管理产物的活动。

---

### 规则组 B：过程组与主题组的正交标注

> **规则组 B 的整体状态：`pending_reanchor`。** 原锚点 ISO 21500:2012 已于 2021-03-16 被撤回，由 ISO 21502:2020（指南）与 ISO 21500:2021（概述）取代。规则组 B 的“五过程组 × 十主题组”矩阵结构在 ISO 21502:2020 中是否保留、以何种形态保留，尚待核验（见 `SOURCE_LEDGER.md` 的 `ISO21502-2020` 条目 `verification_status` 字段）。**在重新锚定完成前，本组规则不编译为阻断性检查，仅输出 `advisory`。** 重新锚定登记于 `TODO.md`。

**G-B1（双维度标注）**

> 任何生成的管理项必须同时携带一个 `process_group` 标签和一个 `subject_group` 标签。缺少任一维度即判定为元框架违规。

- `grounding_ref`：`ISO21502-2020`（状态：`pending_reanchor`）
- `provenance_note`：ISO 21500:2012 将项目管理过程划分为五个过程组和十个主题组，二者是正交分类维度。ISO 21502:2020 是否保留该结构尚待核验。本规则将“正交性”收紧为强制性标注要求，为技能自身贡献。
- `check`：`DUAL_DIMENSION_ANNOTATION`
- `severity`：`block`（`pending_reanchor` 期间降级为 `advisory`）
- `applicability`：任何生成管理项的活动。重新锚定后复评。

**G-B2（标签值集的封闭性）**

> `process_group` 和 `subject_group` 的合法值**只能**来自 G-B1 所锚定标准中的枚举。不允许引入自定义值来“扩充”分类。如果领域技能需要表达该标准未覆盖的管理关注点，它应当通过接口契约新增 `subject_group_extension` 槽位，并在该槽位中显式声明其与基础主题组的关系（`specializes` / `cross_cuts` / `orthogonal_to`），而不是污染基础枚举。

- `grounding_ref`：`ISO21502-2020`（状态：`pending_reanchor`）
- `provenance_note`：值集取自所锚定标准的主题组分类；扩展机制的形式为技能自身贡献，目的是在保持基础分类封闭的同时允许领域特化。
- `check`：`DIMENSION_VALUE_CLOSED`
- `severity`：`block`（`pending_reanchor` 期间降级为 `advisory`）
- `applicability`：同 G-B1。

---

### 规则组 C：交付物的可断言性

**G-C1（交付物必须可断言）**

> 每个 `Deliverable` 节点必须至少有一条出边指向 `Assertion` 节点。`Assertion` 的内容必须是关于该交付物“是什么、处于什么状态、满足什么条件”的明确陈述。不存在“已被识别但不可断言”的交付物。

- `grounding_ref`：`ThingFO-2021`；`PRINCE2-2023`
- `provenance_note`：ThingFO 将 `Assertion` 定义为“人类关于 Particulars 和 Universals 不同方面的陈述”，是本体中可验证性的最小单元。PRINCE2 的“关注产品”原则要求每个产品有产品描述。将二者合取为“交付物—断言”的必要关联，为技能自身贡献。
- `check`：`DELIVERABLE_ASSERTION_LINK`
- `severity`：`block`
- `applicability`：任何声明了 `Deliverable` 的活动。

**G-C2（断言的可区分性）**

> 同一个 `Deliverable` 的多条 `Assertion` 如果内容互斥，不得同时处于 `active` 状态而不触发冲突标记。互斥的判定标准是：两条断言对同一 `Subject` 的同一属性给出了不相容的值。冲突时，输出必须同时呈现两条断言及其 `grounding_ref`，不得静默选择其一。

- `grounding_ref`：`ThingFO-2021`
- `provenance_note`：ThingFO 将 `Assertion` 作为可区分的人类陈述。将区分性用于运行时一致性检查，为技能自身贡献。
- `check`：`ASSERTION_MUTUAL_EXCLUSION`
- `severity`：`warn`
- `applicability`：任何存在多条 `Assertion` 指向同一 `Deliverable` 的场景。

---

### 规则组 D：变更必须追溯到约束

**G-D1（变更的约束锚定）**

> 任何对 `Commitment` 或 `Deliverable` 的变更提议，必须显式声明它作用于哪个已登记的 `Constraint` 节点，并说明该变更是 `mitigates`（缓解）、`exacerbates`（加剧）还是 `trades_off`（权衡）该约束。不允许“无约束锚定”的变更。

- `grounding_ref`：`ISO21502-2020`；`ProjectCO-2024`
- `provenance_note`：这是对“范围—时间—成本”约束关系的本体化重述。ISO 21502:2020 将约束管理置于核心；ProjectCO 核心层包含 `Constraint` 与变更相关的关系。三种变更—约束关系类型（`mitigates` / `exacerbates` / `trades_off`）为技能自身贡献。
- `check`：`CHANGE_CONSTRAINT_LINK`
- `severity`：`block`
- `applicability`：任何变更提议。

**G-D2（全改善声明的审查）**

> 如果一条变更提议声称同时 `mitigates` 所有已识别的 `Constraint`，而没有任何 `trades_off` 或 `exacerbates`，该声明不得被直接接受。它必须被降级为 `assumption`，并附带一个验证条件：在什么证据出现时该“全改善”声明可以被确认为真。在验证条件被满足之前，它不得作为变更批准的依据。

- `grounding_ref`：`ISO21502-2020`
- `provenance_note`：约束之间通常存在权衡关系；声称无权衡的“全改善”是对默认假设的偏离。本规则不宣称“全改善不可能”，只要求它承担举证责任。形式为技能自身贡献。
- `check`：`ALL_IMPROVEMENT_ASSUMPTION`
- `severity`：`warn`
- `applicability`：任何声称同时改善全部约束的变更提议。

---

### 规则组 E：角色的最小完备性

**G-E1（问责锚定与执行分离）**

> 任何涉及决策的 `Commitment` 必须关联一个 `accountable_by` 指向的 `Accountable`（唯一最终责任人）和至少一个 `responsible_by` 指向的 `Responsible`（执行者）。
>
> **`Accountable` 必须是 `HumanActor` 或 `LegalEntity`。`AIActor` 只能出现在 `responsible_by` 或显式委托链的 `delegated_to` 位置。**
>
> `Accountable` 与 `Responsible` 可以重合，但重合时必须携带 `role_merge_declaration`，说明合并理由并记录为 `assumption` 附带验证条件（如“项目参与者少于 N 人”）。

- `grounding_ref`：`PRINCE2-2023`；`ProjectCO-2024`
- `provenance_note`：PRINCE2 7 将“定义角色与职责”作为七项原则之一，其角色模型区分最终责任与执行责任，且最终责任不可委托。ProjectCO 核心层包含 `Actor` 及其职责关系。**“问责永远锚定人类或法人，AI 只承担执行或经显式委托链连接”这一约束，为技能自身对 PRINCE2 问责原则在 AI 环境下的治理性表达**——PRINCE2 原文并未涉及 AI，该约束是技能的形式化贡献，其合理性依据在 `CHARTER.md` 承诺 C5。RACI 与 PRINCE2 实践允许小项目角色合并，故不采用“Accountable 与 Responsible 不得同一”的更严版本。
- `check`：`ROLE_MINIMAL_COMPLETENESS`
- `severity`：`block`
- `applicability`：任何涉及决策的 `Commitment`。

**G-E2（执行自治声明的可审查性）**

> 当 `AIActor` 在某个决策上具有执行自治权时，该自治权必须通过一条显式的委托链 `delegated_from` 连接到某个 `Accountable`（人类或法人）。委托链本身必须关联至少一个 `Assertion`，说明“该自治权的范围、边界与撤销条件”。该 `Assertion` 以 `assumption` 形式存在，并附带验证条件。

- `grounding_ref`：`PRINCE2-2023`
- `provenance_note`：PRINCE2 的问责原则以人类治理为默认背景；将其扩展到 AI 执行自治需要显式的委托链声明。形式为技能自身贡献。
- `check`：`AI_AUTONOMY_DELEGATION_AUDITABLE`
- `severity`：`warn`
- `applicability`：任何存在 `AIActor` 执行自治权的场景。

---

### 规则组 F：阶段闭合（立项、收尾、采购、时间证据）

> **规则组 F 的整体状态：`assumption` 级。** 本组规则的锚定来源（ISO 21502:2020 的过程覆盖、PRINCE2 的阶段管理原则）在具体条款上尚待逐条核验；在核验完成前，本组规则以 `assumption` 形式存在，**不编译为阻断性检查**，只输出 `advisory` 并附带验证条件。核验登记于 `TODO.md`。

**G-F1（立项章程的存在性）**

> 任何 `Project` 在进入执行阶段前，必须存在一个 `ProjectCharter` 节点，该节点至少关联：`Outcome` 的初始陈述、至少一个 `Constraint`、`Accountable` 的指派、以及一个 `Assertion` 说明“本项目被授权启动”。缺少 `ProjectCharter` 而进入执行阶段的活动，判定为立项缺失。

- `grounding_ref`：`PRINCE2-2023`（“持续业务验证”与“定义角色与职责”原则的组合）
- `provenance_note`：PRINCE2 将项目启动授权作为阶段管理的起点；本规则将其形式化为 `ProjectCharter` 节点的最小关联集。**最小关联集的具体字段（Outcome 陈述、Constraint、Accountable、启动授权 Assertion）为技能自身的形式化贡献**，PRINCE2 原文未以该字段集形态表述。待核验后决定是否升级为 `block`。
- `check`：`PROJECT_CHARTER_EXISTENCE`
- `severity`：`advisory`（`assumption` 期间；核验后复评）
- `applicability`：任何进入执行阶段的 `Project`。
- `assumption_verification`：ISO 21502:2020 与 PRINCE2 7 对“项目授权”的最小要素集是否与本规则一致；核验后升级或修订。

**G-F2（收尾验收的闭合）**

> 任何 `Project` 进入收尾阶段时，每个 `Deliverable` 必须至少有一条 `Assertion` 声明其“已验收”或“已移交”，且该 `Assertion` 必须关联一个 `Accountable` 的确认记录。缺少验收断言的 `Deliverable` 不得随项目收尾而关闭。

- `grounding_ref`：`PRINCE2-2023`（“关注产品”原则与阶段收尾）
- `provenance_note`：PRINCE2 的产品验收与阶段收尾原则的组合。将“验收断言必须关联 Accountable 确认”形式化，为技能自身贡献。待核验后决定是否升级为 `block`。
- `check`：`CLOSURE_ACCEPTANCE_LINK`
- `severity`：`advisory`（`assumption` 期间）
- `applicability`：任何进入收尾阶段的 `Project`。
- `assumption_verification`：与 ISO 21502:2020 的收尾过程要素核验一致后升级。

**G-F3（外部采购的合同锚定）**

> 任何涉及外部采购的 `Commitment`，必须关联一个 `Contract` 节点，该节点至少声明：交付物形态、验收判据、约束锚定（该合同缓解或引入哪些 `Constraint`）、以及 `Accountable` 的合同签署确认。缺少 `Contract` 锚定的外部采购承诺，判定为采购治理缺失。

- `grounding_ref`：`ISO21502-2020`（采购主题组的领域无关表述）
- `provenance_note`：ISO 21502:2020 将采购作为项目管理的主题之一；本规则将其形式化为 `Contract` 节点的最小声明集。**最小声明集的具体字段为技能自身贡献**。待核验后决定是否升级为 `block`。
- `check`：`PROCUREMENT_CONTRACT_ANCHOR`
- `severity`：`advisory`（`assumption` 期间）
- `applicability`：任何涉及外部采购的 `Commitment`。
- `assumption_verification`：与 ISO 21502:2020 采购主题组的过程要素核验一致后升级。

**G-F4（时间与进度证据的存在性）**

> 任何声明了 `deadline` 或 `milestone` 的 `Commitment`，必须关联至少一条 `Assertion`，说明该时间承诺的依据（估算方法、历史数据、或外部强加的日期及其出处）。无依据的时间承诺不得作为进度基线的组成部分。

- `grounding_ref`：`ISO21502-2020`（时间主题组）
- `provenance_note`：ISO 21502:2020 将时间作为项目管理主题之一；本规则将“时间承诺必须有依据”形式化为 `Assertion` 关联要求。**“依据”的具体形态（估算方法 / 历史数据 / 外部强加出处）为技能自身贡献**。待核验后决定是否升级为 `block`。
- `check`：`SCHEDULE_EVIDENCE_LINK`
- `severity`：`advisory`（`assumption` 期间）
- `applicability`：任何声明了时间承诺的 `Commitment`。
- `assumption_verification`：与 ISO 21502:2020 时间主题组的过程要素核验一致后升级。

---

### 规则组 G：适用性裁剪

> **规则组 G 的整体状态：`assumption` 级。** 本组规则定义“规则集本身如何被裁剪”，其锚定来源（PRINCE2 的“根据环境裁剪”原则）在裁剪的**最小不可裁剪集**上尚待核验；在核验完成前，本组规则以 `assumption` 形式存在，只输出 `advisory`。核验登记于 `TODO.md`。

**G-G1（裁剪必须显式声明）**

> 任何对规则集的裁剪（将某条规则标记为不适用、降级为 `advisory`、或豁免）必须产生一条 `TailoringRecord`，该记录至少声明：被裁剪的规则 ID、裁剪理由、裁剪的适用范围（哪些活动、哪些 `Deliverable`）、以及裁剪的批准者（`Accountable`）。无 `TailoringRecord` 的裁剪视为规则未生效，相关活动按原规则检查。

- `grounding_ref`：`PRINCE2-2023`（“根据环境裁剪”原则）
- `provenance_note`：PRINCE2 将裁剪作为七项原则之一，但未规定裁剪记录的最小字段集。**`TailoringRecord` 的字段集为技能自身贡献**。待核验后决定是否升级为 `block`。
- `check`：`TAILORING_RECORD_EXISTENCE`
- `severity`：`advisory`（`assumption` 期间）
- `applicability`：任何裁剪规则集的活动。
- `assumption_verification`：与 PRINCE2 裁剪原则的实践指南核验一致后升级。

**G-G2（裁剪不得降低不可裁剪集）**

> 以下规则构成**不可裁剪集**，任何 `TailoringRecord` 不得将其标记为不适用或降级：G-A1、G-A2、G-C1、G-D1、G-E1。裁剪记录若试图裁剪不可裁剪集中的规则，判定为裁剪违规。
>
> 不可裁剪集的理由：G-A1 与 G-A2 是项目存在的最小条件；G-C1 是交付物可验证性的最小条件；G-D1 是变更可追溯性的最小条件；G-E1 是问责结构的最小条件。这五条规则是 `CHARTER.md` 承诺 C2、C5 的直接落地。

- `grounding_ref`：`PRINCE2-2023`（裁剪原则的边界）
- `provenance_note`：PRINCE2 未明确列举“不可裁剪”的规则集。**不可裁剪集的选取为技能自身贡献**，其理由基于 `CHARTER.md` 承诺 C2 与 C5。待核验后决定是否升级为 `block`。
- `check`：`TAILORING_NON_TRIMMABLE_SET`
- `severity`：`advisory`（`assumption` 期间）
- `applicability`：任何裁剪记录。
- `assumption_verification`：与 PRINCE2 裁剪原则的边界说明核验一致后升级。

**G-G3（裁剪记录的可追溯性）**

> 每条 `TailoringRecord` 必须关联至少一个 `Assertion`，说明裁剪后的规则集在什么条件下应被重新评估（如“项目规模变化”“领域技能变更”“外部约束变更”）。无重新评估条件的裁剪记录视为永久裁剪，永久裁剪必须由 `Accountable` 在记录中显式声明“永久”并附理由。

- `grounding_ref`：`PRINCE2-2023`
- `provenance_note`：将裁剪的时效性要求形式化为 `Assertion` 关联，为技能自身贡献。待核验后决定是否升级为 `block`。
- `check`：`TAILORING_REASSESSMENT_CONDITION`
- `severity`：`advisory`（`assumption` 期间）
- `applicability`：任何裁剪记录。
- `assumption_verification`：同 G-G1。

---

### 规则组状态汇总

| 组 | 规则数 | 状态 | 阻断级规则 | 说明 |
|---|---|---|---|---|
| A | 2 | `active` | 2 | 项目存在的最小条件 |
| B | 2 | `pending_reanchor` | 0（降级 `advisory`） | 锚点 ISO 21500:2012 已废止，待重新锚定 |
| C | 2 | `active` | 1（C1）+ 1 `warn`（C2） | 交付物可断言性 |
| D | 2 | `active` | 1（D1）+ 1 `warn`（D2） | 变更追溯 |
| E | 2 | `active` | 1（E1）+ 1 `warn`（E2） | 角色最小完备性 |
| F | 4 | `assumption` | 0（`advisory`） | 阶段闭合，待逐条核验后升级 |
| G | 3 | `assumption` | 0（`advisory`） | 适用性裁剪，待核验后升级 |

**不可裁剪集**（G-G2）：G-A1、G-A2、G-C1、G-D1、G-E1。
