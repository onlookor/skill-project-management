## 接口契约规范

**权威关系**：本文件是执行层文件。它落实 `CONSTITUTION.md` 第 8 条（可选插件条款）与 `CHARTER.md` 第 5 条（与领域技能的横向关系）。它**不得**修改成文法，也不得把任何领域组合写成成文法规则。

### 1. 定位：横向槽位，不是上下游链条

本技能与**任何领域技能**（需求工程、软件工程、建筑施工，以及未来任何领域技能）都是**横向对等关系**（`CHARTER.md` 第 5 条）。没有任何领域技能享有特殊地位。

因此，本规范定义的是**槽位**（slot）——本技能消费什么、产出什么，以什么形态、满足什么条件。它**不定义**“某个具体技能是上游还是下游”，也**不定义**“需求→软件”这类链条是技能本体的组成部分。

**技能间的具体连接**（某领域技能的产物如何成为另一技能的输入）是**部署时配置或契约样例**，登记在 `contracts/examples/` 或部署配置中，**不进入成文法**。理由：连接形态随领域组合变化；把它写成规则就是把它绑定到特定组合，违反 `CHARTER.md` 承诺 C2（领域真空）。

### 2. 槽位定义

槽位分两类：**输入槽位**（本技能消费）与**输出槽位**（本技能产出）。

#### 2.1 输入槽位

| 槽位名 | 类别 | 必填 | 形态约束 | 断言条件 |
|---|---|---|---|---|
| `subject_type` | 输入 | 是 | 字符串，领域技能声明的 `Subject` 类型名 | 必须非空；类型名在领域技能中有定义 |
| `deliverable_forms` | 输入 | 是 | 字符串列表，领域交付物的形态名 | 至少一项；每项在领域技能中有定义 |
| `constraint_domains` | 输入 | 是 | 字符串列表，领域约束的子类名 | 至少一项；每项须声明与通用约束分类（目标/环境/方案）的关系（`specializes` / `cross_cuts` / `orthogonal_to`） |
| `assertion_vocabulary` | 输入 | 是 | 字符串列表，领域断言的词汇表 | 至少一项；每项须可映射到“是什么/什么状态/满足什么条件”三类之一 |
| `actor_roles` | 输入 | 否 | 字符串列表，领域角色名 | 若填写，每项须声明是否可承担 `Accountable`（仅 `HumanActor`/`LegalEntity` 可）；缺省时本技能使用通用角色 |
| `subject_group_extension` | 输入 | 否 | 对象列表，扩展的主题组声明 | 若填写，每项须声明与基础主题组的关系（见 G-B2）；缺省时不扩展 |

**必填槽位的缺失处置**：阻断并报告缺失项，**不做推断**（`ASSUMPTION_PROTOCOL.md` 第 5 节：槽位填充遇 unknown 一律阻断）。

#### 2.2 输出槽位

| 槽位名 | 类别 | 形态 | 说明 |
|---|---|---|---|
| `assertion` | 输出 | 断言节点（含 `grounding_ref` 或 `assumption` 标记） | 每个交付物的状态与验收条件 |
| `commitment_baseline` | 输出 | 承诺基线（`Commitment` 集合 + 其约束锚定） | 项目范围基线 |
| `change_record` | 输出 | 变更记录（含 `Constraint` 锚定与关系类型） | G-D1 的产出 |
| `role_assignment` | 输出 | 角色分配（含 `Accountable` 锚点与委托链） | G-E1、G-E2 的产出 |
| `tailoring_record` | 输出 | 裁剪记录（若发生裁剪） | G-G1 的产出 |

**输出槽位的消费方**：输出槽位不绑定特定领域技能。任何领域技能都可以选择消费这些产出；本技能不规定“谁应该消费”。

### 3. 技能间信息流（连接实例，不是规则）

**本节定义的是连接实例的声明方式，不是连接本身的合法性。** 任何两个技能之间的具体信息流，都是**一个可声明的连接实例**，登记在 `contracts/examples/` 或部署配置中。

#### 3.1 连接实例的声明格式

```yaml
# 连接实例声明（示例性格式，具体字段见 contracts/schema/）
connection:
  id: <唯一标识>
  from_skill: <产出方技能标识>
  to_skill: <消费方技能标识>
  flow:
    - from_slot: <产出方槽位名>
      to_slot: <消费方槽位名>
      mapping: <映射规则：直接对应 / 变换规则 / 条件映射>
      assertion: <该映射的断言条件（在什么条件下该映射成立）>
  status: <active | assumption | deprecated>
  verification:
    type: <alignment_check | runtime_check>
    ...
```

#### 3.2 连接实例的性质

- **连接实例不是成文法规则**。它不进入 `GRAMMAR.md`，不受 `CONSTITUTION.md` 第 3 条准入条件约束（它不宣称“合法项目管理断言”）。
- **连接实例是部署时配置**。它的合法性取决于：产出方槽位的断言条件是否满足、消费方槽位的形态约束是否满足、映射规则是否可执行。
- **连接实例的失败不构成成文法违规**，但构成部署配置缺陷，须记录并修复。
- **任何连接实例都不享有特殊地位**。需求→软件、需求→建筑、建筑→运维，在声明格式与验证方式上完全对等。

#### 3.3 为什么放在这里而不是成文法

若把“需求工程技能的产物是软件工程技能的输入”写成 `GRAMMAR.md` 的规则，就等于：
- 把成文法绑定到“需求”与“软件”这两个领域对象（违反承诺 C2 领域真空）；
- 把一条**随组合变化**的协作配置写成**普适规则**；
- 使未来任何新的领域组合都需要修改成文法。

放在接口契约层，连接实例是**可声明、可验证、可替换**的配置；成文法保持领域真空。

#### 3.4 连接实例的验证

连接实例的验证由宿主运行时执行，不进入 `validation/CHECKLIST.md` 的成文法检查项。验证内容：

- 产出方槽位的断言条件是否满足（如产出方是否声明了 `assertion` 且其 `grounding_ref` 非空）；
- 消费方槽位的形态约束是否满足（如消费方的 `constraint_domains` 是否声明了与通用分类的关系）；
- 映射规则是否可执行（如直接对应时类型是否匹配）。

验证失败 → 连接实例标 `blocked`，不执行该连接，记录缺陷。**不影响两个技能各自的完备性**。

### 4. 契约文件格式

领域技能向本技能填充槽位的方式：在领域技能目录下放置一个**独立契约文件**（`*.pm-contract.yaml` 或 `*.pm-contract.json`），与领域技能自身的 `SKILL.md` 并列。

```yaml
# 示例：software-engineering.pm-contract.yaml
skill_id: software-engineering
pm_contract_version: "0.1"
slots:
  subject_type: "SoftwareComponent"
  deliverable_forms:
    - "CodeModule"
    - "DeploymentPackage"
    - "TestReport"
    - "ArchitectureDecisionRecord"
  constraint_domains:
    - name: "quality_attribute"
      relation_to_generic: "specializes"   # 目标类约束的特化
      generic_class: "goal"
    - name: "existing_system_state"
      relation_to_generic: "specializes"
      generic_class: "environment"
    - name: "solution_constraint"
      relation_to_generic: "specializes"
      generic_class: "solution"
  assertion_vocabulary:
    - name: "implemented"
      maps_to: "what_state"       # 是什么状态
    - name: "tested"
      maps_to: "what_condition"   # 满足什么条件
    - name: "documented"
      maps_to: "what_is"          # 是什么
  actor_roles:
    - name: "tech_lead"
      can_be_accountable: true    # 人类角色可承担 Accountable
    - name: "ai_coding_agent"
      can_be_accountable: false   # AI 角色只能承担 Responsible
  subject_group_extension: []     # 不扩展主题组
grounding_ref: null               # 契约文件本身不携带 grounding_ref（它声明的是领域技能的自我描述，不是外部来源）
assumption_refs:
  - id: "A-CONTRACT-SE-01"
    statement: "software-engineering 技能的 subject_type 与 deliverable_forms 在其 SKILL.md 中有定义"
    verification:
      type: "alignment_check"
      target_document: "software-engineering/SKILL.md"
      alignment_criterion: "类型名与形态名在该文档中存在"
```

**约束**：

- 契约文件只声明**槽位填充**，不声明“本技能是上游/下游”。
- 契约文件的 `grounding_ref` 为 `null`（它是领域技能的自我描述，不是外部来源）；若某槽位值有外部来源依据（如法规强制的交付物形态），在槽位级别声明 `grounding_ref`。
- 契约文件中的 `assumption_refs` 遵循 `ASSUMPTION_PROTOCOL.md`。

### 5. v1 单层解析

**v1 只启用一个权威位置**：领域技能目录下的独立契约文件。

**为什么不做多层**：评审指出，对当前两三个技能的生态，多层来源 + 字段级合并是过度设计（YAGNI）。v1 用单层，等真实需求出现再加。

**解析规则**：

1. 宿主在启动时扫描已挂载领域技能的契约文件；
2. 对每个契约文件，校验 schema（`contracts/schema/pm-slot-contract.schema.json`）；
3. 校验通过 → 槽位可被本技能消费；校验失败 → 该领域技能标 `contract_invalid`，不参与协作，记录缺陷；
4. 必填槽位缺失 → 该领域技能标 `contract_incomplete`，不参与协作，报告缺失项；
5. 解析结果是一份**扁平快照**，每个槽位携带来源标识（哪个契约文件）。

**解析由宿主运行时执行，生成模型不参与**（`CONSTITUTION.md` 第 1 条）。

### 6. 多层合并语义（定义但不启用）

若未来启用多层（`SKILL.md` 内嵌 < 独立契约文件 < 注册表条目），语义定义如下，**v1 不实现**：

- 优先级从低到高：`SKILL.md` 内嵌 < 独立契约文件 < 注册表条目；
- 合并是**字段级**的，不是整文件替换；
- 字段状态三值：未声明（继承低层级）、声明值（覆盖低层级）、显式移除（`null`，覆盖为“无”，不允许低层级回填）；
- 列表字段默认**替换**，不追加；追加需显式声明 `merge: append`；
- 同级冲突必须报错（`contract_conflict`），不得静默取值；
- `null` 作用于 `required: true` 的槽位 → `contract_violation`，契约不可满足，阻断；
- `immutable: true` 字段不允许高层级覆盖，覆盖报 `contract_violation`。

**启用条件**：需要 ADR 论证真实需求出现（如三个以上技能、或同一技能在不同部署中有不同槽位填充）。

### 7. 三空间映射的 assumption 形态

三空间本体（问题/事实/解）与软件工程技能严格绑定（`CHARTER.md` 第 5 条）。本技能**不依赖**三空间；但若宿主启用了三空间插件，需要声明映射关系。

**映射以 `assumption` 形式存在**（`ASSUMPTION_PROTOCOL.md` 第 4 节，用途 B）：

```
A-SP-01: 本技能的约束分类（目标/环境/方案）与三空间（问题/事实/解）存在对应关系：
         目标↔问题空间、环境↔事实空间、方案↔解空间
verification:
  type: alignment_check
  target_document: 软件工程元框架成文法
  target_section: 三空间本体论相关章节
  alignment_criterion: 语义等价
  on_mismatch: 修订本技能的三类约束定义，或放弃该映射并退回通用分类
expires_at: 与 SE 技能原文对齐核验完成时
```

**无三空间时的退路**：约束分类退回通用分类（目标 / 环境 / 方案）。这是 v1 的默认形态；三空间插件是可选的语义扩展（`CONSTITUTION.md` 第 8 条）。

**禁止**：把三空间映射写成 `grounded`（未与 SE 技能原文对齐前，它是假设，不是事实）。

### 8. PACT 不可映射项声明

PACT 是可选插件（`CONSTITUTION.md` 第 8 条）。若宿主安装 PACT，本规范规定：

**可映射的契约槽位**：

| 槽位 | PACT 映射 |
|---|---|
| `deliverable_forms` | 映射为 PACT 的工件类型（`Token` 类型）；每个形态对应一个 Token 类型 |
| `constraint_domains` | 映射为 PACT 的约束 Token 类型；约束关系映射为 Token 间关系 |
| `assertion_vocabulary` | 映射为 `AssertionToken` 的元数据字段；断言映射为“产生交付物 Token 需有 AssertionToken 作为见证”的前置条件 |

**不可映射的契约要素**：

| 要素 | 不可映射原因 |
|---|---|
| `actor_roles` 的 `can_be_accountable` 约束 | PACT 的 Gate 是“参与者 × 工件类型”的能力，不是角色属性的字段级约束；问责约束须在技能自身校验器执行 |
| `subject_group_extension` 的关系声明 | PACT 无“与基础分类的关系”概念 |
| 连接实例的映射规则 | PACT 管理单技能内的工件流，不管理跨技能的槽位映射 |
| 契约的 `assumption_refs` | PACT 无 assumption 概念 |

**适配纪律**（同本文件第 8 节）：可映射项映射；不可映射项由技能自身校验器执行；**PACT 缺失时技能完备**。

### 9. 无插件模式的完整路径

本节确认 `CHARTER.md` 承诺 C4 的落地：

| 组件 | 有插件时 | 无插件时（v1 默认） |
|---|---|---|
| 检查执行 | PACT 执行可映射项；技能校验器执行不可映射项 | 技能校验器执行全部检查项 |
| 契约解析 | 宿主运行时执行单层解析 | 同左（不依赖 PACT） |
| 约束分类 | 三空间插件提供分类 | 通用分类（目标/环境/方案） |
| 技能间连接 | 连接实例声明 + 宿主验证 | 同左（不依赖 PACT） |
| 槽位填充 | 领域技能契约文件 | 同左 |
| 输出结构 | `grounded`/`assumption` 分离 | 同左 |

**结论**：无 PACT、无三空间时，本技能的全部规则、全部检查、全部槽位填充路径可完整执行。插件的价值是**增强**（更丰富的分类、运行时准入），不是**前提**。

### 10. 与领域技能的横向关系（重申）

- 本规范定义槽位，不定义“谁是谁的上游/下游”。
- 任何领域技能都可以选择填充槽位；不填充不构成违规，只构成“该领域技能不参与本技能的协作”。
- 本技能不修改任何领域技能的内部结构；领域技能也不需要为适配本技能而改造自身（只需提供契约文件）。
- 依赖方向是单方面的：领域技能依赖本技能的槽位定义，本技能不依赖任何特定领域技能。

### 11. 不做的事

- 不在本规范中写入任何领域特有对象名；
- 不定义“某个领域组合是标准配置”；
- 不要求领域技能为适配本技能而改造自身；
- 不把连接实例写成成文法规则；
- 不把三空间映射写成 `grounded`；
- 不在 PACT 中硬塞不可映射项；
- 不让生成模型参与契约解析或槽位合并裁决。
