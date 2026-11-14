## 术语表

**权威关系**：本文件是**立法层的支撑文件**，与 `GRAMMAR.md`、`SOURCE_LEDGER.md` 并列。它落实 `CONSTITUTION.md` 第 7.1 级（术语自包含）与第 11 条（术语治理与引用规则）。本文件的修改遵循 `CONSTITUTION.md` 第 11.2 条（术语准入条件）。

### 0. 本文件的地位与分工

本文件是**人类可读的术语登记**，覆盖全仓库使用的术语。它与 `knowledge/anchored-entries.jsonl` 的分工如下：

| 文件 | 覆盖范围 | 形态 | 权威性 |
|---|---|---|---|
| `GLOSSARY.md`（本文件） | 全部术语：领域无关核心概念、框架自创机制术语、编译域术语、治理术语、行业缩写、接口契约术语 | 人类可读的 Markdown 条目 | 术语定义的权威源；当与 `anchored-entries.jsonl` 冲突时，**领域无关核心概念**以 `anchored-entries.jsonl` 为准，其余以本文件为准 |
| `knowledge/anchored-entries.jsonl` | 仅领域无关核心概念（`Project`、`Actor`、`Commitment` 等） | 机器可查询的 JSONL 条目 | 规则判定中谓词/槽位定义的权威源 |

**二者的关系**：`anchored-entries.jsonl` 是领域无关核心概念在**规则判定形态**下的投影；本文件是同一概念在**人类阅读形态**下的定义。二者不是重复，是同一概念的两个投影。本文件 A 类条目的 `anchored_entry` 字段指向 `anchored-entries.jsonl` 中的对应条目；冲突时以 JSONL 为准，本文件相应修订（见 `CONSTITUTION.md` 第 11.5 条）。

### 1. 字段说明

每个术语条目包含以下字段：

| 字段 | 含义 | 必填 |
|---|---|---|
| `term_id` | 稳定标识，格式 `T-{分类字母}-{序号}`；一经发布永不复用 | 是 |
| `term` | 术语名（人类可读） | 是 |
| `category` | 分类：A 领域无关核心概念 / B 框架自创机制 / C 编译域 / D 治理 / E 行业缩写与标准 / F 接口契约 | 是 |
| `definition` | 一句话定义（自足，不依赖其他术语才能理解；若依赖，被依赖术语必须先定义） | 是 |
| `relations` | 与其他术语的关系（可选） | 否 |
| `grounding_ref` | 指向 `SOURCE_LEDGER.md` 的条目 ID（若有外部来源） | 否 |
| `anchored_entry` | 指向 `knowledge/anchored-entries.jsonl` 的条目（仅 A 类） | 仅 A 类必填 |
| `provenance_note` | 形式化边界说明（哪些来自来源，哪些是技能自身贡献） | 否 |
| `status` | `active` / `deprecated`（附被谁取代）/ `merged`（附合并到哪条） | 是 |
| `first_used_in` | 首次使用的文件与条款 | 是 |

### 2. 术语的引用格式

- **文档内引用**：术语首次出现时用 `术语名`（代码格式），后跟括号内联一句话定义，或后跟 `（见 GLOSSARY.md#term_id）`。**机制术语（B、C、D 类）必须使用本文件中的定义义，不得另创同义词。**
- **跨文件引用**：`GLOSSARY.md#T-B-001` 形式（term_id 作为锚点）。
- **JSONL 条目中引用**：用 `term` 字段的值，必须与本文件的 `term` 字段一致。
- **行业缩写（E 类）首次出现**：必须内联展开全称（如 `WBS（Work Breakdown Structure，工作分解结构）`），并登记入本文件。

### 3. 术语条目

#### A. 领域无关核心概念

> 本类条目与 `knowledge/anchored-entries.jsonl` 对应。定义以 JSONL 为准；此处是人类可读的摘要。

**T-A-001 Project**
- 定义：由一组经协调的、有开始和结束日期的活动组成的独特过程，以达成受约束的 `Outcome`。在本技能中是根节点；存在条件见 G-A1。
- `anchored_entry`：`Project`
- `grounding_ref`：`ProjectCO-2024`；`ISO21502-2020`
- `first_used_in`：`GRAMMAR.md` G-A1
- `status`：`active`

**T-A-002 Actor**
- 定义：参与项目的实体。子类包括 `HumanActor`、`LegalEntity`、`AIActor`。可承担 `Responsible`；`Accountable` 仅限 `HumanActor` 或 `LegalEntity`（G-E1）。
- `anchored_entry`：`Actor`
- `grounding_ref`：`ProjectCO-2024`
- `first_used_in`：`GRAMMAR.md` G-A1
- `status`：`active`

**T-A-003 Commitment**
- 定义：`Actor` 对 `Outcome` 的承诺。项目范围基线的组成单元；必须关联 `Accountable` 与 `Responsible`（G-E1），变更必须追溯到 `Constraint`（G-D1）。
- `anchored_entry`：`Commitment`
- `grounding_ref`：`ProjectCO-2024`
- `first_used_in`：`GRAMMAR.md` G-A1
- `status`：`active`

**T-A-004 Deliverable**
- 定义：项目产出的可识别工件。必须至少关联一条 `Assertion`（G-C1）。领域形态由接口契约的 `deliverable_forms` 槽位填充。
- `anchored_entry`：`Deliverable`
- `grounding_ref`：`ProjectCO-2024`
- `first_used_in`：`GRAMMAR.md` G-C1
- `status`：`active`

**T-A-005 Constraint**
- 定义：作用于 `Outcome` 或 `Commitment` 的限制。通用分类为 `goal`（目标类）、`environment`（环境类）、`solution`（方案类）。领域子类由接口契约的 `constraint_domains` 槽位声明。
- `anchored_entry`：`Constraint`
- `grounding_ref`：`ProjectCO-2024`
- `first_used_in`：`GRAMMAR.md` G-A1
- `status`：`active`

**T-A-006 Outcome**
- 定义：`Actor` 通过 `Commitment` 期望达成的结果。`Constraint` 的作用对象之一。
- `anchored_entry`：`Outcome`
- `grounding_ref`：`ProjectCO-2024`
- `first_used_in`：`GRAMMAR.md` G-A1
- `status`：`active`

**T-A-007 Assertion**
- 定义：关于实体（Particulars）与类型（Universals）的人类陈述，是本体中可验证性的最小单元。在本技能中是 `Deliverable` 可验证性的载体（G-C1），也是 `assumption` 与 `grounded` 分离的基础。
- `anchored_entry`：`Assertion`
- `grounding_ref`：`ThingFO-2021`
- `first_used_in`：`GRAMMAR.md` G-C1
- `status`：`active`

**T-A-008 Accountable**
- 定义：对 `Commitment` 承担最终责任的唯一角色。必须是 `HumanActor` 或 `LegalEntity`；不得为 `AIActor`（G-E1）。
- `anchored_entry`：`Accountable`
- `grounding_ref`：`PRINCE2-2023`
- `first_used_in`：`GRAMMAR.md` G-E1
- `status`：`active`

**T-A-009 Responsible**
- 定义：执行 `Commitment` 的角色。可以是 `HumanActor`、`LegalEntity` 或 `AIActor`。与 `Accountable` 可以重合，但重合时须携带 `role_merge_declaration`（G-E1）。
- `anchored_entry`：`Responsible`
- `grounding_ref`：`PRINCE2-2023`
- `first_used_in`：`GRAMMAR.md` G-E1
- `status`：`active`

**T-A-010 Subject**
- 定义：断言所关于的对象。在 G-C2（断言的可区分性）中，互斥判定以“同一 `Subject` 的同一属性”为基准。领域类型由接口契约的 `subject_type` 槽位填充。
- `anchored_entry`：`Subject`
- `grounding_ref`：`ThingFO-2021`
- `first_used_in`：`GRAMMAR.md` G-C2
- `status`：`active`

**T-A-011 HumanActor**
- 定义：`Actor` 的子类，人类参与者。可承担 `Accountable` 与 `Responsible`。
- `anchored_entry`：`HumanActor`（待补充独立条目，见 `TODO.md` T-028）
- `grounding_ref`：无（技能自身对 `Actor` 的子类化，依据 `CHARTER.md` 承诺 C5）
- `first_used_in`：`CHARTER.md` 承诺 C5
- `status`：`active`

**T-A-012 LegalEntity**
- 定义：`Actor` 的子类，法人实体。可承担 `Accountable` 与 `Responsible`。
- `anchored_entry`：`LegalEntity`（待补充独立条目，见 `TODO.md` T-028）
- `grounding_ref`：无（技能自身对 `Actor` 的子类化，依据 `CHARTER.md` 承诺 C5）
- `first_used_in`：`CHARTER.md` 承诺 C5
- `status`：`active`

**T-A-013 AIActor**
- 定义：`Actor` 的子类，AI 参与者。只能承担 `Responsible` 或经显式委托链的 `delegated_to` 位置；不得承担 `Accountable`（G-E1、G-E2）。
- `anchored_entry`：`AIActor`（待补充独立条目，见 `TODO.md` T-028）
- `grounding_ref`：无（技能自身对 `Actor` 的子类化，依据 `CHARTER.md` 承诺 C5）
- `first_used_in`：`CHARTER.md` 承诺 C5
- `status`：`active`

**T-A-014 Contract**
- 定义：外部采购承诺的锚定节点。至少声明交付物形态、验收判据、约束锚定、`Accountable` 签署（G-F3）。
- `anchored_entry`：`Contract`（待补充条目，见 `TODO.md` T-029）
- `grounding_ref`：`ISO21502-2020`
- `first_used_in`：`GRAMMAR.md` G-F3
- `status`：`active`

**T-A-015 ProjectCharter**
- 定义：项目启动授权节点。至少关联 `Outcome` 初始陈述、`Constraint`、`Accountable`、启动授权 `Assertion`（G-F1）。
- `anchored_entry`：`ProjectCharter`（待补充条目，见 `TODO.md` T-029）
- `grounding_ref`：`PRINCE2-2023`
- `first_used_in`：`GRAMMAR.md` G-F1
- `status`：`active`

**T-A-016 TailoringRecord**
- 定义：规则集裁剪的记录。至少声明被裁剪规则 ID、裁剪理由、适用范围、批准者（G-G1）。不得裁剪不可裁剪集（G-G2）。
- `anchored_entry`：`TailoringRecord`（待补充条目，见 `TODO.md` T-029）
- `grounding_ref`：`PRINCE2-2023`
- `first_used_in`：`GRAMMAR.md` G-G1
- `status`：`active`

#### B. 框架自创机制术语

**T-B-001 grounded**
- 定义：输出中携带非空 `grounding_ref`（指向 `SOURCE_LEDGER.md` 的 `active` 条目）的命题区块。`grounded` 命题不得依赖 `assumption` 作为前提而不显式标注。
- `first_used_in`：`AGENTS.md` 第 5 条
- `status`：`active`

**T-B-002 assumption**
- 定义：输出中携带 `grounding_ref: null` 且附带可检验验证条件的命题区块。两种合法用途：用途 A（保守假设，验证条件为可推翻指标）、用途 B（待对齐映射，验证条件为对齐条件）。格式与纪律见 `spec/ASSUMPTION_PROTOCOL.md`。
- `relations`：与 `grounded` 物理分离；不得被 `GRAMMAR.md` 引用；不得编译为阻断检查
- `first_used_in`：`CONSTITUTION.md` 第 6 条
- `status`：`active`

**T-B-003 grounding_ref**
- 定义：命题或规则携带的来源标识，指向 `SOURCE_LEDGER.md` 的条目 ID。为 `null` 时表示该命题是 `assumption`。
- `first_used_in`：`CONSTITUTION.md` 第 2 条
- `status`：`active`

**T-B-004 保守假设（conservative assumption）**
- 定义：`assumption` 的用途 A。信息不足时，取向“避免不可逆错误”一侧的保守值（对风险取上界、对能力取下界），并登记可推翻指标。
- `first_used_in`：`spec/ASSUMPTION_PROTOCOL.md` 第 1 节
- `status`：`active`

**T-B-005 可推翻指标（refutable indicator）**
- 定义：保守假设登记的可观测判据：一个可观测的量 + 阈值 + 观测方式 + 命中时的动作。指标命中即触发重审提议。
- `first_used_in`：`spec/ASSUMPTION_PROTOCOL.md` 第 3 节
- `status`：`active`

**T-B-006 待对齐映射（alignment mapping）**
- 定义：`assumption` 的用途 B。两个体系（如本技能的约束分类与某个领域技能提供的本体）之间的对应关系，以假设形式存在，验证条件为“与目标文档的指定章节一致”。
- `first_used_in`：`spec/ASSUMPTION_PROTOCOL.md` 第 4 节
- `status`：`active`

**T-B-007 三值逻辑**
- 定义：检查条件求值的结果为 `true` / `false` / `unknown`。`unknown` 不得静默当作 `false`；处置按 `ASSUMPTION_PROTOCOL.md` 第 5 节的统一原理（选向避免不可逆错误的一侧）。
- `first_used_in`：`spec/ASSUMPTION_PROTOCOL.md` 第 5 节
- `status`：`active`

**T-B-008 槽位（slot）**
- 定义：本技能消费或产出的领域无关接口位置。输入槽位包括 `subject_type`、`deliverable_forms`、`constraint_domains`、`assertion_vocabulary`、`actor_roles`、`subject_group_extension`；输出槽位包括 `assertion`、`commitment_baseline`、`change_record`、`role_assignment`、`tailoring_record`。定义见 `spec/INTERFACE_CONTRACT_SPEC.md` 第 2 节。
- `first_used_in`：`spec/INTERFACE_CONTRACT_SPEC.md` 第 2 节
- `status`：`active`

**T-B-009 连接实例（connection instance）**
- 定义：两个技能之间的具体信息流声明（如“需求工程技能的 `Requirement` 集合映射为 `Commitment` 集合”）。是可声明、可验证、可替换的部署配置，**不是成文法规则**，不享有任何领域组合的特殊地位。定义见 `spec/INTERFACE_CONTRACT_SPEC.md` 第 3 节。
- `first_used_in`：`spec/INTERFACE_CONTRACT_SPEC.md` 第 3 节
- `status`：`active`

**T-B-010 契约（contract）**
- 定义：领域技能向本技能填充槽位的声明文件（`*.pm-contract.yaml` 或 `*.pm-contract.json`），与领域技能的 `SKILL.md` 并列。schema 见 `contracts/schema/pm-slot-contract.schema.json`。
- `first_used_in`：`spec/INTERFACE_CONTRACT_SPEC.md` 第 4 节
- `status`：`active`

**T-B-011 不可裁剪集（non-trimmable set）**
- 定义：`GRAMMAR.md` 中不得被任何 `TailoringRecord` 裁剪的规则集合：G-A1、G-A2、G-C1、G-D1、G-E1。理由：它们是项目存在、交付物可验证性、变更可追溯性、问责结构的最小条件（G-G2）。
- `first_used_in`：`GRAMMAR.md` G-G2
- `status`：`active`

**T-B-012 规则状态（rule status）**
- 定义：`GRAMMAR.md` 每条规则的状态：`active`（正常执行）/ `pending_reanchor`（来源待重新锚定，降级为 `advisory`）/ `assumption`（规则以假设身份存在，降级为 `advisory` 并附验证条件）。定义见 `CONSTITUTION.md` 第 9 条。
- `first_used_in`：`CONSTITUTION.md` 第 9 条
- `status`：`active`

**T-B-013 出处门槛**
- 定义：事实与数据的合法性审查：有出处、可观测、无争议。无出处的事实不得作为决策依据（`CHARTER.md` 承诺 C2 与 `GRAMMAR.md` G-D1 的联动）。具体形态见 `CONSTITUTION.md` 第 2 条与 `spec/ASSUMPTION_PROTOCOL.md` 第 5 节。
- `first_used_in`：`CONSTITUTION.md` 第 2 条
- `status`：`active`

**T-B-014 自包含三级**
- 定义：`CONSTITUTION.md` 第 7 条定义的三级自包含：7.1 术语自包含（规则术语必须有定义）、7.2 执行自包含（规则执行不要求查阅外部原文）、7.3 结构自包含（规则集内部引用不得形成未登记的循环）。
- `first_used_in`：`CONSTITUTION.md` 第 7 条
- `status`：`active`

**T-B-015 论断级映射（claim_mapping）**
- 定义：`SOURCE_LEDGER.md` 条目携带的字段，声明该来源支持 `GRAMMAR.md` 或 `knowledge/` 中的哪些**具体**规则/条目。禁止“支持整份文档”式的笼统授权。用于拦截“来源存在但不支持论断”的错误形态。
- `first_used_in`：`CONSTITUTION.md` 第 2 条
- `status`：`active`

**T-B-016 权威层级（authority_tier）**
- 定义：`SOURCE_LEDGER.md` 条目携带的字段，标识来源的权威级别：`international_standard` / `national_standard` / `peer_reviewed` / `preprint` / `official_doc`。厂商博客、非官方镜像 PDF 原则上不入表（`CONSTITUTION.md` 第 2.3 条）。
- `first_used_in`：`CONSTITUTION.md` 第 2 条
- `status`：`active`

**T-B-017 核验状态（verification_method）**
- 定义：`SOURCE_LEDGER.md` 条目携带的字段，记录来源的最近一次核验方式：`local_copy_check`（本地版本核对）/ `authority_page`（权威页面访问）/ `cross_reference`（交叉印证）/ `pending`（待核验）。
- `first_used_in`：`CONSTITUTION.md` 第 2 条
- `status`：`active`

**T-B-018 来源状态**
- 定义：`SOURCE_LEDGER.md` 条目的状态：`active`（可作新规则锚定）/ `deprecated`（已废止，附被谁取代；已有规则可继续引用但标 `pending_reanchor`；新规则不得引入）/ `superseded`（被新条目取代）。
- `first_used_in`：`CONSTITUTION.md` 第 2.2、2.4 条
- `status`：`active`

**T-B-019 检查机械化**
- 定义：规则检查由确定性校验器执行，生成模型只负责槽位填充、局部判断与自然语言表述。理由：对参数量受限的模型，把“记住规则并自觉遵守”当作执行机制是幻觉的主要来源。定义见 `CONSTITUTION.md` 第 1 条与 `AGENTS.md` 第 2 条。
- `first_used_in`：`CONSTITUTION.md` 第 1 条
- `status`：`active`

**T-B-020 可选插件**
- 定义：不构成技能完备性前提的组件：PACT、外部领域本体、任何外部本体框架、任何编译方法（`CONSTITUTION.md` 第 8 条、第 10.3 条）。插件的存在增强能力，缺失不构成技能不完整。
- `first_used_in`：`CONSTITUTION.md` 第 8 条
- `status`：`active`

#### C. 编译域术语

> 编译域的完整定义见 `spec/COMPILATION_META.md` 与 `spec/COMPILATION_METHODS.md`。此处是核心术语的摘要。

**T-C-001 编译元框架（compilation meta-framework）**
- 定义：`spec/COMPILATION_META.md`。定义“什么是合法的编译”（与具体编译方法无关）：编译接口、编译产物必须满足的性质（P1–P6）、编译方法准入条件、选择/共存/替换、失败分类、编译治理。与“项目管理元框架”同构。
- `first_used_in`：`spec/COMPILATION_META.md` 第 0 条
- `status`：`active`

**T-C-002 编译方法（compilation method）**
- 定义：一种具体的编译实现（确定性校验器、技能卡片、人类检查单、PACT 规则、神经符号编译）。可选插件，不构成技能完备性的前提。每种方法用独立声明文件（`spec/methods/{method-id}.md`）声明自己。
- `first_used_in`：`spec/COMPILATION_METHODS.md`
- `status`：`active`

**T-C-003 P1–P6（编译产物必须满足的性质）**
- 定义：`spec/COMPILATION_META.md` 第 2 条定义的六条性质：P1 忠实性（不引入/不丢失/不扭曲）、P2 可判定性、P3 结论封闭性、P4 证据保全、P5 自包含、P6 假设与事实分离。任何编译方法都必须论证其产物满足这六条。
- `first_used_in`：`spec/COMPILATION_META.md` 第 2 条
- `status`：`active`

**T-C-004 F-C1～F-C5（编译失败分类）**
- 定义：`spec/COMPILATION_META.md` 第 6 条定义的编译域失败分类：F-C1 源缺口（所有方法都编不了，走 ADR 修订成文法）、F-C2 方法不可行（某方法编不了但其他方法可以，在方法声明中登记）、F-C3 忠实性失败（产物拒绝发布）、F-C4 执行失败（记录并升级为方法缺陷）、F-C5 假设未闭合（按 `ASSUMPTION_PROTOCOL.md` 第 6 节处置）。
- `first_used_in`：`spec/COMPILATION_META.md` 第 6 条
- `status`：`active`

**T-C-005 check_id**
- 定义：检查项标识，每条规则的 `check` 字段的值。注册于 `spec/methods/deterministic-checker.md` 附录 A。`check_id` 的判定条件由规则陈述翻译而来，翻译须遵循方法声明文件附录 B 的翻译规范。
- `first_used_in`：`GRAMMAR.md` 使用说明
- `status`：`active`

**T-C-006 severity**
- 定义：检查项的严重级别：`block`（违反即不合规，阻断）/ `warn`（违反需记录并说明）/ `advisory`（提示级，不阻断）。规则状态为 `pending_reanchor` 或 `assumption` 时，实际 severity 降级为 `advisory`。定义见 `spec/methods/deterministic-checker.md` 第 4.5 节。
- `first_used_in`：`GRAMMAR.md` 使用说明
- `status`：`active`

**T-C-007 规则状态携带（rule_status）**
- 定义：编译产物中携带的字段，标识对应规则的状态（`active` / `pending_reanchor` / `assumption`）。宿主据此决定是否仅记录而不阻断（P6 的合规执行）。
- `first_used_in`：`spec/methods/deterministic-checker.md` 第 4.5 节
- `status`：`active`

**T-C-008 忠实性（fidelity）**
- 定义：P1 的三条子性质：P1a 不引入（产物不引入源未登记的规则）、P1b 不丢失（每条规则被至少一个方法覆盖或显式声明不可编译）、P1c 不扭曲（产物语义与源语义一致）。论证方式由方法声明文件规定（形式化证明 / 结构同构 / 逐条对照 / 反例检验）。
- `first_used_in`：`spec/COMPILATION_META.md` 第 2 条
- `status`：`active`

**T-C-009 可判定性（decidability）**
- 定义：P2。编译产物必须能被执行或检查，且执行/检查的结论必须落在某个封闭枚举内。执行形态可以是确定性程序执行、人类评审执行、或混合执行。
- `first_used_in`：`spec/COMPILATION_META.md` 第 2 条
- `status`：`active`

**T-C-010 结论封闭性**
- 定义：P3。执行/检查的结论必须是封闭枚举，不得有中间态（“待定”“基本通过”等）。封闭枚举的具体取值由方法声明（如确定性校验器的 `{pass, fail, cannot_evaluate}`，人类检查单的 `{符合, 不符合, 不适用}`）。
- `first_used_in`：`spec/COMPILATION_META.md` 第 2 条
- `status`：`active`

**T-C-011 证据保全（evidence preservation）**
- 定义：P4。执行/检查必须产出可重放的证据。证据的最少要素：执行时的输入快照、执行者标识、执行时间戳、结论、结论依据。不可重放的“证据”降级为线索，不获得引用资格。
- `first_used_in`：`spec/COMPILATION_META.md` 第 2 条
- `status`：`active`

**T-C-012 退化路径（degradation path）**
- 定义：方法声明文件中规定的、在缺少某依赖（如谓词求值能力、PACT、外部领域本体）时的退路。退路必须满足 P1–P6。确定性校验器的退化路径为“检查清单 + 人类评审”（`runtime: deterministic-checker/human-fallback`）。
- `first_used_in`：`spec/methods/deterministic-checker.md` 第 10 节
- `status`：`active`

**T-C-013 运行时目标（runtime target）**
- 定义：编译方法声明文件中规定的、其产物在什么运行时上执行。可识别标识如 `deterministic-checker`、`deterministic-checker/human-fallback`、`pact-runtime`、`skill-card-host`。
- `first_used_in`：`spec/COMPILATION_META.md` 第 3.3 条
- `status`：`active`

**T-C-014 不可映射项（unmappable item）**
- 定义：某编译方法无法编译的规则或规则子句。方法必须诚实列出，并声明其归宿（由其他方法承担 / 由人类评审承担 / 走 ADR 修订成文法 / 标记为永久不可编译并附理由）。不允许“不可映射项无人承担”的静默状态（`COMPILATION_META.md` 第 5.5 条）。
- `first_used_in`：`spec/COMPILATION_META.md` 第 3.5 条
- `status`：`active`

**T-C-015 编译产物版本对齐**
- 定义：编译产物的版本必须与 `GRAMMAR.md` 版本、`SOURCE_LEDGER.md` 版本、方法版本三者对齐。任一变化触发重编译。Agent 不得运行过期编译产物（`CONSTITUTION.md` 第 10.6 条）。
- `first_used_in`：`spec/COMPILATION_META.md` 第 7.5 条
- `status`：`active`

#### D. 治理术语

**T-D-001 CHARTER**
- 定义：`CHARTER.md`。意图层文件：技能为什么存在、服务谁、可检验设计承诺 C1–C6、与领域技能的横向关系。修改需 ADR，且 ADR 须论证具体技能失败。
- `first_used_in`：`CHARTER.md` 第 0 条
- `status`：`active`

**T-D-002 CONSTITUTION**
- 定义：`CONSTITUTION.md`。治理层文件：成文法由谁修改、如何修改；来源封闭性；自包含三级定义；可选插件条款；编译治理总纲（第 10 条）；术语治理（第 11 条）。修改需更严格 ADR（第 5 条）。
- `first_used_in`：`CONSTITUTION.md` 第 0 条
- `status`：`active`

**T-D-003 GRAMMAR**
- 定义：`GRAMMAR.md`。立法层文件：成文法规则组 A–G。每条规则携带 `grounding_ref`、`provenance_note`、`check`、`severity`、`applicability`。修改需 ADR + `SOURCE_LEDGER.md` 支撑。
- `first_used_in`：`GRAMMAR.md` 使用说明
- `status`：`active`

**T-D-004 SOURCE_LEDGER**
- 定义：`SOURCE_LEDGER.md`。立法层文件：封闭来源登记表。每条目携带 `id`、`citation`、`version`、`status`、`authority_tier`、`verified_date`、`verification_method`、`allowed_uses`、`claim_mapping`。修改需 ADR。
- `first_used_in`：`CONSTITUTION.md` 第 2 条
- `status`：`active`

**T-D-005 ADR**
- 定义：Architecture Decision Record，治理决策记录。格式可选 Nygard、MADR、Y-Statement 三种之一（见 `adr/README.md`），并扩展 `serves_charter`、`grounding_refs`、`affected_files` 字段。状态：`proposed` / `accepted` / `deprecated` / `superseded`。只有 `accepted` 状态的 ADR 才能作为修改立法文件的依据。模板见 `adr/ADR-TEMPLATE.md`。
- `first_used_in`：`CONSTITUTION.md` 第 4 条
- `status`：`active`

**T-D-006 CHANGELOG**
- 定义：`CHANGELOG.md`。变更历史的唯一登记处。按批次追加，禁止改写已登记批次。登记规则见 `AGENTS.md` 第 3.1 条。
- `first_used_in`：`AGENTS.md` 第 3.1 条
- `status`：`active`

**T-D-007 TODO**
- 定义：`TODO.md`。后续工作的唯一登记处。编号续用，不重排；删除条目保留编号并标记 `[done]` 或 `[dropped]`。登记规则见 `AGENTS.md` 第 3.2 条。
- `first_used_in`：`AGENTS.md` 第 3.2 条
- `status`：`active`

**T-D-008 四层结构**
- 定义：技能的物理结构分层：意图层（`CHARTER.md`）/ 治理层（`CONSTITUTION.md` + `adr/`）/ 立法层（`GRAMMAR.md` + `SOURCE_LEDGER.md` + `GLOSSARY.md`）/ 执行层（`spec/` + `contracts/` + `validation/`）。层间修改权限不同；反向修改只能通过 ADR 通道（ADR-0001）。
- `first_used_in`：`adr/0001-separate-grammar-from-governance.md`
- `status`：`active`

**T-D-009 三权分立**
- 定义：`CONSTITUTION.md` 第 1 条定义的职能分离：立法（定义什么算合法的项目管理断言）/ 治理（决定立法文件如何被修改）/ 执行（将立法翻译为可运行的检查与准入条件）。任何单一职能不得同时承担另外两个。
- `first_used_in`：`CONSTITUTION.md` 第 1 条
- `status`：`active`

**T-D-010 来源封闭性**
- 定义：`CONSTITUTION.md` 第 2 条定义的约束：`SOURCE_LEDGER.md` 是 `grounding_ref` 的封闭枚举；规则不得引入未登记的外部引用。新增条目需 ADR 且满足准入条件。
- `first_used_in`：`CONSTITUTION.md` 第 2 条
- `status`：`active`

**T-D-011 pending_reanchor**
- 定义：规则或来源的状态标记：来源待重新锚定。规则处于此状态时，实际 severity 降级为 `advisory`，不得编译为阻断检查。解除条件：完成重新锚定（走 ADR）。
- `first_used_in`：`CONSTITUTION.md` 第 9 条
- `status`：`active`

**T-D-012 deprecated**
- 定义：来源或规则的状态标记：已废止。附被谁取代。已有规则可继续引用但标 `pending_reanchor`；新规则不得引入。`SOURCE_LEDGER.md` 条目不得被删除（`CONSTITUTION.md` 第 2.4 条）。
- `first_used_in`：`CONSTITUTION.md` 第 2.2、2.4 条
- `status`：`active`

**T-D-013 superseded**
- 定义：ADR 或来源条目的状态标记：已被新条目取代。保留历史，不删除。
- `first_used_in`：`CONSTITUTION.md` 第 4 条
- `status`：`active`

#### E. 行业缩写与标准术语

> 本类条目是描述性的，不是规范性锚点（规范性锚点在 `SOURCE_LEDGER.md`）。首次出现必须内联展开。

**T-E-001 PMBOK**
- 定义：Project Management Body of Knowledge，PMI 发布的项目管理知识体系指南。当前 8th Edition (2025-11)，本技能以本地副本作原则层交叉验证（`SOURCE_LEDGER.md` 的 `PMBOK8-2025` 条目）。
- `grounding_ref`：`PMBOK8-2025`（仅原则层交叉验证，不作规则锚定）
- `first_used_in`：`SOURCE_LEDGER.md`
- `status`：`active`

**T-E-002 PRINCE2**
- 定义：Projects IN Controlled Environments，AXELOS 发布的项目管理方法论。7th Edition (2023)。七项原则：持续业务验证、从经验中学习、定义角色与职责、按阶段管理、例外管理、关注产品、根据环境裁剪。
- `grounding_ref`：`PRINCE2-2023`
- `first_used_in`：`GRAMMAR.md` G-C1
- `status`：`active`

**T-E-003 ISO 21502:2020**
- 定义：国际标准化组织发布的《Project, programme and portfolio management — Guidance on project management》。本技能采用 2020 版；其过程组/主题组结构尚待核对（`TODO.md` T-113）。
- `grounding_ref`：`ISO21502-2020`
- `first_used_in`：`SOURCE_LEDGER.md`
- `status`：`active`

**T-E-004 GB/T 37507—2025**
- 定义：中国国家标准《项目、项目群和项目组合管理 项目管理指南》，等同采用 ISO 21502:2020。中文环境部署时优先引用。
- `grounding_ref`：`GB-T-37507-2025`
- `first_used_in`：`SOURCE_LEDGER.md`
- `status`：`active`

**T-E-005 WBS**
- 定义：Work Breakdown Structure，工作分解结构。把项目范围分解为可管理的工作包的方法。登记为方法条目 `M-DEC-01`。
- `grounding_ref`：`PMBOK8-2025`（仅原则层交叉验证；方法条目待补充更精确来源，见 `TODO.md` T-004）
- `first_used_in`：`knowledge/methods/registry-skeleton.md` M-DEC-01
- `status`：`active`

**T-E-006 PERT**
- 定义：Program Evaluation and Review Technique，计划评审技术。三点估算方法（乐观/最可能/悲观）。登记为方法条目 `M-EST-01`。
- `grounding_ref`：无（通用运筹学方法；方法条目待补充来源，见 `TODO.md` T-004）
- `first_used_in`：`knowledge/methods/registry-skeleton.md` M-EST-01
- `status`：`active`

**T-E-007 EVM / EVA**
- 定义：Earned Value Management / Earned Value Analysis，挣值管理/挣值分析。量化进度与成本偏差的方法，核心指标：PV、EV、AC、SV、CV、SPI、CPI。登记为方法条目 `M-EV-01`。
- `grounding_ref`：`PMBOK8-2025`（仅原则层交叉验证；方法条目待补充更精确来源，见 `TODO.md` T-004）
- `first_used_in`：`knowledge/methods/registry-skeleton.md` M-EV-01
- `status`：`active`

**T-E-008 RACI**
- 定义：Responsible / Accountable / Consulted / Informed，角色分配矩阵。本技能采用其 `Accountable` 与 `Responsible` 的区分（G-E1），但不强制使用完整 RACI 四角色。
- `grounding_ref`：无（通用实践；G-E1 的锚定为 PRINCE2-2023）
- `first_used_in`：`GRAMMAR.md` G-E1 的 `provenance_note`
- `status`：`active`

**T-E-009 SOW / RFQ / RFP**
- 定义：Statement of Work（工作说明书）/ Request for Quotation（询价书）/ Request for Proposal（建议书邀请）。采购流程中使用的文档类型。登记于方法条目 `M-PROC-01`。
- `grounding_ref`：`ISO21502-2020`（采购主题组的领域无关表述）
- `first_used_in`：`knowledge/methods/registry-skeleton.md` M-PROC-01
- `status`：`active`

**T-E-010 MTTR**
- 定义：Mean Time To Recovery，平均恢复时长。可用性/可靠性指标。
- `grounding_ref`：无（通用可靠性工程术语；本技能不将其作为规则锚定）
- `first_used_in`：`GLOSSARY.md`（本条目）
- `status`：`active`

#### F. 接口契约术语

**T-F-001 subject_type**
- 定义：输入槽位。领域技能声明的 `Subject` 类型名。必填，非空。定义见 `spec/INTERFACE_CONTRACT_SPEC.md` 第 2.1 节。
- `first_used_in`：`spec/INTERFACE_CONTRACT_SPEC.md` 第 2.1 节
- `status`：`active`

**T-F-002 deliverable_forms**
- 定义：输入槽位。领域交付物的形态名列表。必填，至少一项。定义见 `spec/INTERFACE_CONTRACT_SPEC.md` 第 2.1 节。
- `first_used_in`：`spec/INTERFACE_CONTRACT_SPEC.md` 第 2.1 节
- `status`：`active`

**T-F-003 constraint_domains**
- 定义：输入槽位。领域约束的子类名列表。必填，至少一项；每项须声明与通用约束分类（`goal` / `environment` / `solution`）的关系（`specializes` / `cross_cuts` / `orthogonal_to`）。定义见 `spec/INTERFACE_CONTRACT_SPEC.md` 第 2.1 节。
- `first_used_in`：`spec/INTERFACE_CONTRACT_SPEC.md` 第 2.1 节
- `status`：`active`

**T-F-004 assertion_vocabulary**
- 定义：输入槽位。领域断言的词汇表。必填，至少一项；每项须映射到“是什么（`what_is`）/ 什么状态（`what_state`）/ 满足什么条件（`what_condition`）”三类之一。定义见 `spec/INTERFACE_CONTRACT_SPEC.md` 第 2.1 节。
- `first_used_in`：`spec/INTERFACE_CONTRACT_SPEC.md` 第 2.1 节
- `status`：`active`

**T-F-005 actor_roles**
- 定义：输入槽位（可选）。领域角色名列表。若填写，每项须声明是否可承担 `Accountable`（仅 `HumanActor`/`LegalEntity` 可）；缺省时本技能使用通用角色。定义见 `spec/INTERFACE_CONTRACT_SPEC.md` 第 2.1 节。
- `first_used_in`：`spec/INTERFACE_CONTRACT_SPEC.md` 第 2.1 节
- `status`：`active`

**T-F-006 subject_group_extension**
- 定义：输入槽位（可选）。扩展的主题组声明。若填写，每项须声明与基础主题组的关系（`specializes` / `cross_cuts` / `orthogonal_to`）；缺省时不扩展基础枚举（G-B2）。定义见 `spec/INTERFACE_CONTRACT_SPEC.md` 第 2.1 节。
- `first_used_in`：`spec/INTERFACE_CONTRACT_SPEC.md` 第 2.1 节
- `status`：`active`

**T-F-007 扁平快照（flat snapshot）**
- 定义：契约解析的产出形态：每个槽位携带来源标识（哪个契约文件）的扁平对象。幂等：同一契约文件 + 同一 resolver 版本 → 同一快照。解析由宿主运行时执行，生成模型不参与。定义见 `contracts/resolver.md` 第 1 节。
- `first_used_in`：`contracts/resolver.md` 第 1 节
- `status`：`active`

**T-F-008 契约解析失败状态**
- 定义：四种失败状态：`contract_invalid`（schema 校验失败）、`contract_incomplete`（必填槽位缺失或语义校验失败）、`contract_conflict`（同级冲突，多层时）、`contract_violation`（`null` 作用于必填槽位，或 `immutable` 字段被覆盖）。定义见 `contracts/resolver.md` 第 4 节。
- `first_used_in`：`contracts/resolver.md` 第 4 节
- `status`：`active`

### 4. 与 `knowledge/anchored-entries.jsonl` 的同步规则

- **A 类条目**（领域无关核心概念）必须与 `anchored-entries.jsonl` 中的对应条目**定义一致**。本文件 A 类条目的 `anchored_entry` 字段指向 JSONL 条目名。
- **冲突处置**：若本文件 A 类条目的定义与 JSONL 条目冲突，以 JSONL 为准（因为 JSONL 是规则判定的依据），本文件相应修订。冲突本身按 `CONSTITUTION.md` 第 11.5 条处置（走 ADR 或 CHANGELOG）。
- **B、C、D、E、F 类条目**不要求在 JSONL 中有对应条目；JSONL 只承载领域无关核心概念。
- **同步检查**：登记为 `TODO.md` 工作项（T-090）。

### 5. 与 `SOURCE_LEDGER.md` 的关系

- 术语的 `grounding_ref` 字段（若有）必须指向 `SOURCE_LEDGER.md` 的 `active` 条目，且该条目的 `claim_mapping` 必须包含本术语。
- 术语的定义若来自外部来源（如 `Assertion` 来自 ThingFO），`provenance_note` 须说明“哪些是来源的内容，哪些是技能自身的形式化贡献”。
- 术语表本身**不扩展** `SOURCE_LEDGER.md` 的封闭枚举；它只引用已登记的来源。

### 6. 待补充

以下术语已识别但首批未收录，登记于 `TODO.md` T-091：

- 编译域：`checker_error`、`input_missing`、`schema_mismatch`、`rule_status_unknown`（执行失败分类）
- 治理域：`proposed`、`accepted`、`retired`（ADR 状态与编译方法状态）
- 接口契约：`merge: append`、`immutable` 标记
- 行业缩写：`SLA`、`SLO`、`RPO`、`RTO`、`CI/CD`、`API`、`IDL`

## 4. 术语使用位置（生成）

本表由 `scripts/check_glossary_usage.py` 生成，勿手改。修改术语定义或引用后请运行 `python3 scripts/check_glossary_usage.py --write` 重新生成。

<!-- BEGIN GLOSSARY USAGE -->
| term_id | term | 使用位置 |
|---|---|---|
| T-A-001 | Project | [`CONSTITUTION.md`](CONSTITUTION.md)、[`ERRATA.md`](ERRATA.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`README.en.md`](README.en.md)、[`README.md`](README.md)、[`SOURCE_LEDGER.md`](SOURCE_LEDGER.md)、[`TODO.md`](TODO.md)、[`adr/0007-anchor-discipline.md`](adr/0007-anchor-discipline.md)、[`spec/ANCHOR_SPEC.md`](spec/ANCHOR_SPEC.md)、[`spec/CHECKER_INPUT_SCHEMA.md`](spec/CHECKER_INPUT_SCHEMA.md)、[`spec/M3_M4_PLAN.md`](spec/M3_M4_PLAN.md)、[`spec/ONTOLOGY_FEASIBILITY.md`](spec/ONTOLOGY_FEASIBILITY.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md)、[`validation/independent-review-package.md`](validation/independent-review-package.md) |
| T-A-002 | Actor | [`CHANGELOG.md`](CHANGELOG.md)、[`CHARTER.md`](CHARTER.md)、[`CONSTITUTION.md`](CONSTITUTION.md)、[`ERRATA.md`](ERRATA.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`README.en.md`](README.en.md)、[`README.md`](README.md)、[`SOURCE_LEDGER.md`](SOURCE_LEDGER.md)、[`TODO.md`](TODO.md)、[`adr/0008-reanchor-dimension-rules.md`](adr/0008-reanchor-dimension-rules.md)、[`adr/0013-unified-adjudication-of-check-semantics.md`](adr/0013-unified-adjudication-of-check-semantics.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md)、[`validation/independent-review-package.md`](validation/independent-review-package.md) |
| T-A-003 | Commitment | [`CHANGELOG.md`](CHANGELOG.md)、[`CHARTER.md`](CHARTER.md)、[`CONSTITUTION.md`](CONSTITUTION.md)、[`ERRATA.md`](ERRATA.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`README.en.md`](README.en.md)、[`README.md`](README.md)、[`SOURCE_LEDGER.md`](SOURCE_LEDGER.md)、[`TODO.md`](TODO.md)、[`adr/0008-reanchor-dimension-rules.md`](adr/0008-reanchor-dimension-rules.md)、[`adr/0012-gap-ledger-and-adjudication.md`](adr/0012-gap-ledger-and-adjudication.md)、[`adr/0013-unified-adjudication-of-check-semantics.md`](adr/0013-unified-adjudication-of-check-semantics.md)、[`spec/CHECKER_INPUT_SCHEMA.md`](spec/CHECKER_INPUT_SCHEMA.md)、[`spec/INTERFACE_CONTRACT_SPEC.md`](spec/INTERFACE_CONTRACT_SPEC.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md)、[`validation/independent-review-package.md`](validation/independent-review-package.md) |
| T-A-004 | Deliverable | [`AGENTS.md`](AGENTS.md)、[`CHANGELOG.md`](CHANGELOG.md)、[`CHARTER.md`](CHARTER.md)、[`CONSTITUTION.md`](CONSTITUTION.md)、[`ERRATA.md`](ERRATA.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`README.en.md`](README.en.md)、[`README.md`](README.md)、[`SOURCE_LEDGER.md`](SOURCE_LEDGER.md)、[`TODO.md`](TODO.md)、[`spec/CHECKER_INPUT_SCHEMA.md`](spec/CHECKER_INPUT_SCHEMA.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md)、[`validation/independent-review-package.md`](validation/independent-review-package.md) |
| T-A-005 | Constraint | [`AGENTS.md`](AGENTS.md)、[`CHANGELOG.md`](CHANGELOG.md)、[`CHARTER.md`](CHARTER.md)、[`CONSTITUTION.md`](CONSTITUTION.md)、[`ERRATA.md`](ERRATA.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`README.en.md`](README.en.md)、[`README.md`](README.md)、[`SOURCE_LEDGER.md`](SOURCE_LEDGER.md)、[`TODO.md`](TODO.md)、[`adr/0008-reanchor-dimension-rules.md`](adr/0008-reanchor-dimension-rules.md)、[`spec/CHECKER_INPUT_SCHEMA.md`](spec/CHECKER_INPUT_SCHEMA.md)、[`spec/INTERFACE_CONTRACT_SPEC.md`](spec/INTERFACE_CONTRACT_SPEC.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md)、[`validation/independent-review-package.md`](validation/independent-review-package.md) |
| T-A-006 | Outcome | [`CHANGELOG.md`](CHANGELOG.md)、[`CONSTITUTION.md`](CONSTITUTION.md)、[`ERRATA.md`](ERRATA.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`README.en.md`](README.en.md)、[`README.md`](README.md)、[`SOURCE_LEDGER.md`](SOURCE_LEDGER.md)、[`TODO.md`](TODO.md)、[`adr/0013-unified-adjudication-of-check-semantics.md`](adr/0013-unified-adjudication-of-check-semantics.md)、[`spec/CHECKER_INPUT_SCHEMA.md`](spec/CHECKER_INPUT_SCHEMA.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md)、[`validation/independent-review-package.md`](validation/independent-review-package.md) |
| T-A-007 | Assertion | [`AGENTS.md`](AGENTS.md)、[`CHARTER.md`](CHARTER.md)、[`CONSTITUTION.md`](CONSTITUTION.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`QUICKSTART.md`](QUICKSTART.md)、[`README.en.md`](README.en.md)、[`README.md`](README.md)、[`SOURCE_LEDGER.md`](SOURCE_LEDGER.md)、[`TODO.md`](TODO.md)、[`spec/CHECKER_INPUT_SCHEMA.md`](spec/CHECKER_INPUT_SCHEMA.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md)、[`validation/independent-review-package.md`](validation/independent-review-package.md) |
| T-A-008 | Accountable | [`CHANGELOG.md`](CHANGELOG.md)、[`CHARTER.md`](CHARTER.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`SOURCE_LEDGER.md`](SOURCE_LEDGER.md)、[`spec/INTERFACE_CONTRACT_SPEC.md`](spec/INTERFACE_CONTRACT_SPEC.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md) |
| T-A-009 | Responsible | [`CHARTER.md`](CHARTER.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`SOURCE_LEDGER.md`](SOURCE_LEDGER.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md) |
| T-A-010 | Subject | [`AGENTS.md`](AGENTS.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`spec/INTERFACE_CONTRACT_SPEC.md`](spec/INTERFACE_CONTRACT_SPEC.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md) |
| T-A-011 | HumanActor | [`CHANGELOG.md`](CHANGELOG.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`TODO.md`](TODO.md)、[`spec/INTERFACE_CONTRACT_SPEC.md`](spec/INTERFACE_CONTRACT_SPEC.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md) |
| T-A-012 | LegalEntity | [`CHANGELOG.md`](CHANGELOG.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`TODO.md`](TODO.md)、[`spec/INTERFACE_CONTRACT_SPEC.md`](spec/INTERFACE_CONTRACT_SPEC.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md) |
| T-A-013 | AIActor | [`GAP_LEDGER.md`](GAP_LEDGER.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`TODO.md`](TODO.md)、[`contracts/resolver.md`](contracts/resolver.md)、[`spec/CHECKER_INPUT_SCHEMA.md`](spec/CHECKER_INPUT_SCHEMA.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md)、[`validation/reviews/2026-11-14-d8bf413-review.md`](validation/reviews/2026-11-14-d8bf413-review.md) |
| T-A-014 | Contract | [`GRAMMAR.md`](GRAMMAR.md)、[`TODO.md`](TODO.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md) |
| T-A-015 | ProjectCharter | [`GRAMMAR.md`](GRAMMAR.md)、[`TODO.md`](TODO.md)、[`adr/0013-unified-adjudication-of-check-semantics.md`](adr/0013-unified-adjudication-of-check-semantics.md)、[`spec/M3_M4_PLAN.md`](spec/M3_M4_PLAN.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md) |
| T-A-016 | TailoringRecord | [`GRAMMAR.md`](GRAMMAR.md)、[`TODO.md`](TODO.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md) |
| T-B-001 | grounded | [`AGENTS.md`](AGENTS.md)、[`CONSTITUTION.md`](CONSTITUTION.md)、[`QUICKSTART.md`](QUICKSTART.md)、[`spec/ASSUMPTION_PROTOCOL.md`](spec/ASSUMPTION_PROTOCOL.md)、[`spec/COMPILATION_META.md`](spec/COMPILATION_META.md)、[`spec/CONTEXT_ASSEMBLY.md`](spec/CONTEXT_ASSEMBLY.md)、[`spec/GROUNDING_CRITERIA.md`](spec/GROUNDING_CRITERIA.md)、[`spec/INTERFACE_CONTRACT_SPEC.md`](spec/INTERFACE_CONTRACT_SPEC.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md) |
| T-B-002 | assumption | [`AGENTS.md`](AGENTS.md)、[`CHANGELOG.md`](CHANGELOG.md)、[`CHARTER.md`](CHARTER.md)、[`CONSTITUTION.md`](CONSTITUTION.md)、[`ERRATA.md`](ERRATA.md)、[`GAP_LEDGER.md`](GAP_LEDGER.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`QUICKSTART.md`](QUICKSTART.md)、[`README.en.md`](README.en.md)、[`README.md`](README.md)、[`ROADMAP.md`](ROADMAP.md)、[`TODO.md`](TODO.md)、[`adr/0005-source-ledger-scope.md`](adr/0005-source-ledger-scope.md)、[`adr/0012-gap-ledger-and-adjudication.md`](adr/0012-gap-ledger-and-adjudication.md)、[`adr/0013-unified-adjudication-of-check-semantics.md`](adr/0013-unified-adjudication-of-check-semantics.md)、[`contracts/resolver.md`](contracts/resolver.md)、[`spec/ASSUMPTION_PROTOCOL.md`](spec/ASSUMPTION_PROTOCOL.md)、[`spec/CHECKER_INPUT_SCHEMA.md`](spec/CHECKER_INPUT_SCHEMA.md)、[`spec/COMPILATION_META.md`](spec/COMPILATION_META.md)、[`spec/COMPILATION_METHODS.md`](spec/COMPILATION_METHODS.md)、[`spec/CONTEXT_ASSEMBLY.md`](spec/CONTEXT_ASSEMBLY.md)、[`spec/GROUNDING_CRITERIA.md`](spec/GROUNDING_CRITERIA.md)、[`spec/INTERFACE_CONTRACT_SPEC.md`](spec/INTERFACE_CONTRACT_SPEC.md)、[`spec/M3_M4_PLAN.md`](spec/M3_M4_PLAN.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md)、[`spec/pilot/pilot-artifact.md`](spec/pilot/pilot-artifact.md)、[`validation/CHECKLIST.md`](validation/CHECKLIST.md) |
| T-B-003 | grounding_ref | [`AGENTS.md`](AGENTS.md)、[`CHANGELOG.md`](CHANGELOG.md)、[`CONSTITUTION.md`](CONSTITUTION.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`README.en.md`](README.en.md)、[`README.md`](README.md)、[`ROADMAP.md`](ROADMAP.md)、[`SOURCE_LEDGER.md`](SOURCE_LEDGER.md)、[`TODO.md`](TODO.md)、[`adr/0001-separate-grammar-from-governance.md`](adr/0001-separate-grammar-from-governance.md)、[`adr/0005-source-ledger-scope.md`](adr/0005-source-ledger-scope.md)、[`adr/0006-knowledge-sources-vs-normative-basis.md`](adr/0006-knowledge-sources-vs-normative-basis.md)、[`adr/0007-anchor-discipline.md`](adr/0007-anchor-discipline.md)、[`adr/0010-self-authored-ontology-in-git.md`](adr/0010-self-authored-ontology-in-git.md)、[`knowledge/methods/registry-skeleton.md`](knowledge/methods/registry-skeleton.md)、[`ontology/README.md`](ontology/README.md)、[`scripts/README.md`](scripts/README.md)、[`scripts/check_glossary_sync.md`](scripts/check_glossary_sync.md)、[`spec/ANCHOR_SPEC.md`](spec/ANCHOR_SPEC.md)、[`spec/ASSUMPTION_PROTOCOL.md`](spec/ASSUMPTION_PROTOCOL.md)、[`spec/COMPILATION_META.md`](spec/COMPILATION_META.md)、[`spec/GOVERNANCE_RESTRUCTURE.md`](spec/GOVERNANCE_RESTRUCTURE.md)、[`spec/INTERFACE_CONTRACT_SPEC.md`](spec/INTERFACE_CONTRACT_SPEC.md)、[`spec/M3_M4_DECISIONS.md`](spec/M3_M4_DECISIONS.md)、[`spec/M3_M4_PLAN.md`](spec/M3_M4_PLAN.md)、[`spec/ONTOLOGY_FEASIBILITY.md`](spec/ONTOLOGY_FEASIBILITY.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md)、[`spec/pilot/M3_M4_PILOT_REPORT.md`](spec/pilot/M3_M4_PILOT_REPORT.md) |
| T-B-004 | 保守假设（conservative assumption） | （无） |
| T-B-005 | 可推翻指标（refutable indicator） | （无） |
| T-B-006 | 待对齐映射（alignment mapping） | [`CHANGELOG.md`](CHANGELOG.md) |
| T-B-007 | 三值逻辑 | （无） |
| T-B-008 | 槽位（slot） | （无） |
| T-B-009 | 连接实例（connection instance） | （无） |
| T-B-010 | 契约（contract） | （无） |
| T-B-011 | 不可裁剪集（non-trimmable set） | （无） |
| T-B-012 | 规则状态（rule status） | （无） |
| T-B-013 | 出处门槛 | （无） |
| T-B-014 | 自包含三级 | （无） |
| T-B-015 | 论断级映射（claim_mapping） | （无） |
| T-B-016 | 权威层级（authority_tier） | （无） |
| T-B-017 | 核验状态（verification_method） | （无） |
| T-B-018 | 来源状态 | （无） |
| T-B-019 | 检查机械化 | （无） |
| T-B-020 | 可选插件 | [`CHANGELOG.md`](CHANGELOG.md) |
| T-C-001 | 编译元框架（compilation meta-framework） | （无） |
| T-C-002 | 编译方法（compilation method） | （无） |
| T-C-003 | P1–P6（编译产物必须满足的性质） | （无） |
| T-C-004 | F-C1～F-C5（编译失败分类） | （无） |
| T-C-005 | check_id | [`AGENTS.md`](AGENTS.md)、[`CHANGELOG.md`](CHANGELOG.md)、[`GAP_LEDGER.md`](GAP_LEDGER.md)、[`ROADMAP.md`](ROADMAP.md)、[`TODO.md`](TODO.md)、[`adr/0002-compilation-meta-vs-methods.md`](adr/0002-compilation-meta-vs-methods.md)、[`adr/0007-anchor-discipline.md`](adr/0007-anchor-discipline.md)、[`adr/0012-gap-ledger-and-adjudication.md`](adr/0012-gap-ledger-and-adjudication.md)、[`adr/0013-unified-adjudication-of-check-semantics.md`](adr/0013-unified-adjudication-of-check-semantics.md)、[`ontology/README.md`](ontology/README.md)、[`scripts/README.md`](scripts/README.md)、[`spec/ANCHOR_SPEC.md`](spec/ANCHOR_SPEC.md)、[`spec/CHECKER_INPUT_SCHEMA.md`](spec/CHECKER_INPUT_SCHEMA.md)、[`spec/CONTEXT_ASSEMBLY.md`](spec/CONTEXT_ASSEMBLY.md)、[`spec/M3_M4_PLAN.md`](spec/M3_M4_PLAN.md)、[`spec/ONTOLOGY_FEASIBILITY.md`](spec/ONTOLOGY_FEASIBILITY.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md) |
| T-C-006 | severity | [`AGENTS.md`](AGENTS.md)、[`CHANGELOG.md`](CHANGELOG.md)、[`ERRATA.md`](ERRATA.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`ROADMAP.md`](ROADMAP.md)、[`SOURCE_LEDGER.md`](SOURCE_LEDGER.md)、[`TODO.md`](TODO.md)、[`adr/0002-compilation-meta-vs-methods.md`](adr/0002-compilation-meta-vs-methods.md)、[`adr/0008-reanchor-dimension-rules.md`](adr/0008-reanchor-dimension-rules.md)、[`adr/0013-unified-adjudication-of-check-semantics.md`](adr/0013-unified-adjudication-of-check-semantics.md)、[`spec/CHECKER_INPUT_SCHEMA.md`](spec/CHECKER_INPUT_SCHEMA.md)、[`spec/COMPILATION_META.md`](spec/COMPILATION_META.md)、[`spec/COMPILATION_METHODS.md`](spec/COMPILATION_METHODS.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md)、[`validation/CHECKLIST.md`](validation/CHECKLIST.md) |
| T-C-007 | 规则状态携带（rule_status） | （无） |
| T-C-008 | 忠实性（fidelity） | （无） |
| T-C-009 | 可判定性（decidability） | （无） |
| T-C-010 | 结论封闭性 | （无） |
| T-C-011 | 证据保全（evidence preservation） | （无） |
| T-C-012 | 退化路径（degradation path） | [`CHANGELOG.md`](CHANGELOG.md) |
| T-C-013 | 运行时目标（runtime target） | （无） |
| T-C-014 | 不可映射项（unmappable item） | （无） |
| T-C-015 | 编译产物版本对齐 | （无） |
| T-D-001 | CHARTER | （无） |
| T-D-002 | CONSTITUTION | [`CHANGELOG.md`](CHANGELOG.md) |
| T-D-003 | GRAMMAR | （无） |
| T-D-004 | SOURCE_LEDGER | [`spec/M3_M4_PLAN.md`](spec/M3_M4_PLAN.md)、[`spec/ONTOLOGY_FEASIBILITY.md`](spec/ONTOLOGY_FEASIBILITY.md) |
| T-D-005 | ADR | [`CHANGELOG.md`](CHANGELOG.md) |
| T-D-006 | CHANGELOG | [`CHANGELOG.md`](CHANGELOG.md) |
| T-D-007 | TODO | [`CHANGELOG.md`](CHANGELOG.md) |
| T-D-008 | 四层结构 | （无） |
| T-D-009 | 三权分立 | （无） |
| T-D-010 | 来源封闭性 | （无） |
| T-D-011 | pending_reanchor | [`AGENTS.md`](AGENTS.md)、[`CHANGELOG.md`](CHANGELOG.md)、[`CHARTER.md`](CHARTER.md)、[`CONSTITUTION.md`](CONSTITUTION.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`ROADMAP.md`](ROADMAP.md)、[`SOURCE_LEDGER.md`](SOURCE_LEDGER.md)、[`TODO.md`](TODO.md)、[`adr/0005-source-ledger-scope.md`](adr/0005-source-ledger-scope.md)、[`adr/0008-reanchor-dimension-rules.md`](adr/0008-reanchor-dimension-rules.md)、[`adr/0011-schedule-layer-and-plan.md`](adr/0011-schedule-layer-and-plan.md)、[`spec/COMPILATION_META.md`](spec/COMPILATION_META.md)、[`spec/GROUNDING_CRITERIA.md`](spec/GROUNDING_CRITERIA.md)、[`spec/M3_M4_PLAN.md`](spec/M3_M4_PLAN.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md)、[`validation/CHECKLIST.md`](validation/CHECKLIST.md) |
| T-D-012 | deprecated | [`AGENTS.md`](AGENTS.md)、[`CHANGELOG.md`](CHANGELOG.md)、[`CONSTITUTION.md`](CONSTITUTION.md)、[`SOURCE_LEDGER.md`](SOURCE_LEDGER.md)、[`adr/0005-source-ledger-scope.md`](adr/0005-source-ledger-scope.md)、[`adr/README.md`](adr/README.md)、[`spec/COMPILATION_META.md`](spec/COMPILATION_META.md) |
| T-D-013 | superseded | [`AGENTS.md`](AGENTS.md)、[`CONSTITUTION.md`](CONSTITUTION.md)、[`SOURCE_LEDGER.md`](SOURCE_LEDGER.md)、[`adr/README.md`](adr/README.md) |
| T-E-001 | PMBOK | [`CHANGELOG.md`](CHANGELOG.md) |
| T-E-002 | PRINCE2 | （无） |
| T-E-003 | ISO 21502:2020 | [`CHANGELOG.md`](CHANGELOG.md) |
| T-E-004 | GB/T 37507—2025 | （无） |
| T-E-005 | WBS | [`CHANGELOG.md`](CHANGELOG.md)、[`TODO.md`](TODO.md) |
| T-E-006 | PERT | [`TODO.md`](TODO.md) |
| T-E-007 | EVM / EVA | [`CHANGELOG.md`](CHANGELOG.md) |
| T-E-008 | RACI | （无） |
| T-E-009 | SOW / RFQ / RFP | （无） |
| T-E-010 | MTTR | （无） |
| T-F-001 | subject_type | [`contracts/resolver.md`](contracts/resolver.md)、[`spec/INTERFACE_CONTRACT_SPEC.md`](spec/INTERFACE_CONTRACT_SPEC.md) |
| T-F-002 | deliverable_forms | [`contracts/resolver.md`](contracts/resolver.md)、[`spec/INTERFACE_CONTRACT_SPEC.md`](spec/INTERFACE_CONTRACT_SPEC.md) |
| T-F-003 | constraint_domains | [`contracts/resolver.md`](contracts/resolver.md)、[`spec/INTERFACE_CONTRACT_SPEC.md`](spec/INTERFACE_CONTRACT_SPEC.md) |
| T-F-004 | assertion_vocabulary | [`contracts/resolver.md`](contracts/resolver.md)、[`spec/INTERFACE_CONTRACT_SPEC.md`](spec/INTERFACE_CONTRACT_SPEC.md) |
| T-F-005 | actor_roles | [`contracts/resolver.md`](contracts/resolver.md)、[`spec/INTERFACE_CONTRACT_SPEC.md`](spec/INTERFACE_CONTRACT_SPEC.md) |
| T-F-006 | subject_group_extension | [`CHANGELOG.md`](CHANGELOG.md)、[`GAP_LEDGER.md`](GAP_LEDGER.md)、[`GRAMMAR.md`](GRAMMAR.md)、[`adr/0008-reanchor-dimension-rules.md`](adr/0008-reanchor-dimension-rules.md)、[`adr/0013-unified-adjudication-of-check-semantics.md`](adr/0013-unified-adjudication-of-check-semantics.md)、[`contracts/resolver.md`](contracts/resolver.md)、[`spec/CHECKER_INPUT_SCHEMA.md`](spec/CHECKER_INPUT_SCHEMA.md)、[`spec/INTERFACE_CONTRACT_SPEC.md`](spec/INTERFACE_CONTRACT_SPEC.md)、[`spec/methods/deterministic-checker.md`](spec/methods/deterministic-checker.md) |
| T-F-007 | 扁平快照（flat snapshot） | （无） |
| T-F-008 | 契约解析失败状态 | （无） |
<!-- END GLOSSARY USAGE -->
