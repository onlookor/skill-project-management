## 执行约定

**本文件不构成立法**。它记录的是**每次运行时的操作约定**：怎么找资料、怎么留痕、怎么维护项目自身的文档、怎么分工、怎么不把操作噪声写进项目文件。约定本身不携带规则内容，也不改变 `CHARTER.md`、`CONSTITUTION.md`、`GRAMMAR.md`、`SOURCE_LEDGER.md` 的任何语义。约定可以被调整，不需要 ADR；一旦某条约定被证明具有规范意义，它应当被上收到对应的立法文件，而不是留在这里。

本文件同时是**目录结构的唯一权威**（第 4 条）。`README.md` 中的文件地图只是面向读者的导航指针，与本节冲突时以本节为准。

### 1. 资料获取纪律：本地优先，联网为兜底

编译与使用本技能时，参考资料的获取顺序是**固定**的：

1. **本地资源目录优先**。本技能约定的本地参考资料根目录为 `resources/`（与本技能目录同级或按部署约定挂载）。任何需要查阅来源、核对版本、提取方法元数据的动作，**第一步必须是本地检索**。
2. **本地缺失才联网**。只有在本地资源目录中确认不存在该来源（或存在但版本不足以支撑当前断言）时，才允许联网检索。
3. **联网结果一律留痕**。联网检索必须记录：检索目标、使用的检索入口、命中的权威页面地址、访问日期、核验结论。留痕写入当次运行的临时台账，**不写入任何项目文件**。
4. **联网发现的新来源不自动登记**。若联网检索发现了本地没有、但值得长期使用的来源，正确动作是提出 `SOURCE_LEDGER.md` 的新增提案（走 ADR），而不是当场把它塞进登记表或成文法。
5. **本地有更新版本时使用更新版本**。同一来源的多个本地版本并存时，以版权页/版本声明为准取最新，旧版本在引用时标注为历史版本，不得作为当前断言的唯一依据。

**为什么这些规则写在这里而不写进项目文件**：资料获取是**每次运行的环境事实**，不是技能的规范内容。把它写进 `CONSTITUTION.md` 或 `GRAMMAR.md` 会让“立法文件”混入操作细节，稀释立法文件的权威性，并使立法文件随环境变化而无谓变更。写在这里，它约束的是执行者，不约束技能本身。

### 2. 检查机械化：谁执行什么

| 动作 | 执行者 | 禁止事项 |
|---|---|---|
| 槽位填充（领域语义的实例化） | 生成模型（含小型本地 LLM） | 不得自行发明槽位名或填充来源未声明的内容 |
| 局部判断（“这条断言与这条规则是否相容”） | 生成模型 | 不得代替确定性校验器宣称“检查通过” |
| 自然语言表述（面向人类层的解释） | 生成模型 | 不得在表述中引入未登记的来源或断言 |
| 规则检查（`validation/CHECKLIST.md` 的逐项执行） | **确定性校验器**（由宿主提供，可以是 Datalog 规则、JSON 条件清单或 PACT 准入规则） | **生成模型不得“读清单逐条核对”后宣称合规** |
| 契约解析（槽位合并、`null` 处理、必填校验） | **宿主运行时** | 生成模型不得参与优先级判断或合并裁决 |
| 批准状态写入、`assumption` 与 `grounded` 的边界裁定 | 人类批准角色 / 运行时机械规则 | 生成模型不得写入批准状态，不得把 `assumption` 表述为事实 |

**统一理由**：凡是“几个 B 的模型无法稳定正确执行、且可以用确定性程序执行”的动作，一律外化。生成模型保留的是它仍然擅长的部分：**局部判断与自然语言表述**。这条分工的理由与 `CONSTITUTION.md` 第 1 条的执行职能定义一致。

### 3. Schedule 纪律：CHANGELOG.md 与 TODO.md

技能项目自身有两个**常驻文档**，其存在不构成立法，但其纪律对本仓库的执行者具有约束力。

#### 3.1 CHANGELOG.md —— 变更历史的唯一登记处

- **登记范围**：规范层（`CHARTER.md`、`CONSTITUTION.md`、`GRAMMAR.md`、`SOURCE_LEDGER.md`）的任何实质变更；执行层（`spec/`、`contracts/`、`validation/`）中改变已有规则编译结果的结构性变更；知识层（`knowledge/`）条目的新增、删除或语义变更；`adr/` 中 ADR 的新增与状态迁移。
- **不登记**：错别字修正、排版调整、`README.md` 与 `AGENTS.md` 自身的措辞微调（除非改变其约束范围）。
- **格式**：按批次追加。每批包含：`{批次号, 日期, 涉及文件, 变更摘要, 关联 ADR 编号（若有）}`。
- **纪律**：**禁止改写已登记批次**。发现登记错误时，追加一条更正条目并引用原批次，不改原批次。批次号一经发布永不复用。
- **版本载体**：文件不写版本号、不携带版本头；包版本只有一个，以 annotated tag 声明发布点（ADR-0003）。外部引用读根目录 `manifest.json`。
- **与 ADR 的分工**：ADR 记录的是“为什么这样治理”；CHANGELOG 记录的是“什么时候、哪些文件、以什么批次被修改了”。一条实质性变更通常同时产生一条 ADR 和一个 CHANGELOG 批次；CHANGELOG 批次引用 ADR 编号，ADR 不引用 CHANGELOG 批次号（避免双向维护）。

#### 3.2 TODO.md —— 后续工作的唯一登记处

- **登记范围**：尚未完成的工作项，包括方法注册表种子条目填充、`pending_reanchor` 条目的重新锚定、`spec/` 尚未定稿的章节、样例契约的补充、验证套件的第一轮执行、已识别的缺口与待办。
- **不登记**：已完成的工作（完成时移出 TODO，进入 CHANGELOG 对应批次）；纯想法（想法先进入 `adr/` 的 `proposed` 状态，被接受后才进入 TODO 作为执行项）。
- **格式**：每条包含 `{编号, 性质, 治理路径, 前置依赖, 完成状态}`。编号一经分配续用，**删除条目保留编号并标记 `[done]` 或 `[dropped]`，不重排**。
- **性质分类**：`规范层补丁` / `执行层补丁` / `知识层填充` / `样例与示例` / `验证` / `治理`。每类对应的治理路径不同（规范层走 ADR，执行层走结构性变更判定，知识层走来源治理，样例走随样例更新，验证走结果登记）。
- **纪律**：每项工作开始时登记状态为 `in-progress`，完成或放弃时更新状态并说明原因。**不得静默删除工作项**；工作项若不再需要，标记 `[dropped]` 并附理由。

#### 3.3 两者的写入权限

- **CHANGELOG.md**：任何执行者可在完成一次实质性变更后追加批次。追加即生效，不需批准；但如果对应变更本身需要 ADR（`CONSTITUTION.md` 第 4 条），则在 ADR 被 `accepted` 之前，CHANGELOG 批次标记为 `pending-adr`，不得声称变更已生效。
- **TODO.md**：任何执行者可登记工作项与更新状态。**关闭**（标记 `[done]`）需要附完成证据（对应的 CHANGELOG 批次号、ADR 编号或验证结果指针）。

### 4. 目录结构（唯一权威）

本技能目录的完整结构如下。**本节是目录结构的唯一权威**；`README.md` 中的文件地图只是导航，与本节冲突时以本节为准。

```
project-management-grounding/
│
├── README.md                       # 入口导航：定位、文件地图（指针）、阅读路径
├── QUICKSTART.md                   # 快速开始：最小走查样例 + LLM 接合示例
├── AGENTS.md                       # 本文件：执行约定、目录结构权威、schedule 纪律
├── CHANGELOG.md                    # 变更历史唯一登记处（第 3.1 条）
├── TODO.md                         # 后续工作唯一登记处（第 3.2 条）
├── ERRATA.md                       # 幻觉更正台账
├── STATE.md                        # 逐文件当前状态台账
├── manifest.json                   # 包版本与契约 schema 版本（供外部技能引用）
├── .gitignore                      # Git 忽略规则
│
├── CHARTER.md                      # 意图层：可检验设计承诺 C1–C6、与领域技能的关系
├── CONSTITUTION.md                 # 治理层：三权分立、来源封闭性、自包含三级、可选插件、编译治理总纲（第 10 条）、术语治理（第 11 条）、接地治理（第 12 条）
├── GRAMMAR.md                      # 立法层：成文法规则组 A–G
├── SOURCE_LEDGER.md                # 立法层：封闭来源登记表（含论断级映射）
├── GLOSSARY.md                     # 立法层（支撑）：术语表与术语治理
│
├── spec/
│   ├── COMPILATION_META.md         # 编译元框架（方法无关）：P1–P6、准入条件、选择/共存/替换
│   ├── COMPILATION_METHODS.md      # 编译方法注册表：方法列表、启用状态、替换历史
│   ├── CONTEXT_ASSEMBLY.md         # 上下文装配规范：四场景加载集、token 预算、装配清单
│   ├── GROUNDING_CRITERIA.md       # 接地完成判据：六条判据、状态语义、判据记录
│   ├── methods/
│   │   └── deterministic-checker.md  # CM-DET-CHECKER 方法声明（含 check_id 注册表、翻译规范）
│   ├── ASSUMPTION_PROTOCOL.md      # assumption 协议（方法无关）
│   └── INTERFACE_CONTRACT_SPEC.md  # 槽位定义、v1 单层解析、技能间信息流（方法无关）
│
├── contracts/
│   ├── schema/
│   │   └── pm-slot-contract.schema.json   # 接口契约的 JSON Schema
│   ├── resolver.md                 # 单层解析规则 + 多层合并语义（定义但不启用）+ PACT 适配节
│   └── examples/
│       ├── construction.pm-contract.yaml
│       └── software-engineering.pm-contract.yaml
│
├── knowledge/
│   ├── anchored-entries.jsonl      # 本体条目（term/definition/relations/grounding_ref）
│   └── methods/
│       └── registry-skeleton.md    # 方法注册表（估算、WBS、风险、挣值、采购；首批 5 条）
│
├── adr/
│   ├── ADR-TEMPLATE.md             # 治理决策模板（Nygard 五要素 + 扩展字段）
│   ├── 0001-separate-grammar-from-governance.md
│   ├── 0002-compilation-meta-vs-methods.md
│   ├── 0003-version-and-state-governance.md
│   └── 0004-artifact-baseline-by-commit.md
│
├── scripts/
│   ├── README.md                   # 辅助脚本目录说明
│   ├── check_glossary_sync.md      # GLOSSARY/JSONL 同步检查规格
│   └── check_state.py              # STATE 与 git 跟踪文件的对账脚本（可运行）
│
└── validation/
    ├── CHECKLIST.md                # CM-DET-CHECKER 的产物：检查清单（生成依据见正文）
    └── test-cases/
        ├── README.md               # 反例检验用例库说明
        ├── TC-A1-02.md
        ├── TC-C1-03.md
        └── TC-E1-04.md
```

**维护责任与更新频率**：

| 文件/目录 | 维护责任 | 更新触发 | 变更权限 |
|---|---|---|---|
| `README.md` | 交付方 | 文件地图变化、定位变化 | 随交付更新，不需 ADR |
| `manifest.json` | 交付方 | 包版本或契约 schema 版本变化 | 随发布更新；版本以 tag 为准（ADR-0003） |
| `AGENTS.md` | 交付方 | 执行约定变化、目录结构变化 | 随工作流调整，不需 ADR |
| `CHANGELOG.md` | 任何执行者 | 实质性变更发生时（第 3.1 条） | 追加即生效；需 ADR 的变更标 `pending-adr` |
| `TODO.md` | 任何执行者 | 工作项开始/完成/放弃时（第 3.2 条） | 登记即生效；关闭需完成证据 |
| `STATE.md` | 任何执行者 | 文件新增、删除或状态变化时 | 随文件状态更新，不需 ADR |
| `QUICKSTART.md` | 交付方 | 走查样例更新、接合示例更新 | 随交付更新 |
| `ERRATA.md` | 任何执行者 | 发现错误、外部评审、待核验表述登记 | 追加即生效；标记 `closed` 需附修正证据 |
| `CHARTER.md` | 人类责任方 | 承诺调整（需 ADR，见 `CHARTER.md` 第 6 条） | ADR `accepted` |
| `CONSTITUTION.md` | 人类责任方 | 治理规则调整（需 ADR，见第 5 条） | ADR `accepted` |
| `GRAMMAR.md` | 人类责任方 | 规则增删改（需 ADR + `SOURCE_LEDGER.md` 支撑） | ADR `accepted` |
| `SOURCE_LEDGER.md` | 人类责任方 | 来源新增/弃用/状态变更（需 ADR） | ADR `accepted` |
| **`GLOSSARY.md`** | **人类责任方** | **术语增删改（A 类需 ADR + JSONL 同步；B/C/D 类需 ADR；E/F 类需 CHANGELOG）** | **ADR `accepted`（A/B/C/D 类）；CHANGELOG（E/F 类）** |
| **`spec/COMPILATION_META.md`** | **人类责任方** | **编译元框架调整（需 ADR，且 ADR 须论证具体编译失败）** | **ADR `accepted`** |
| **`spec/COMPILATION_METHODS.md`** | **人类责任方** | **方法的启用/淘汰/替换（需 ADR）；格式调整（需 CHANGELOG）** | **ADR `accepted`（启用/淘汰/替换）；CHANGELOG（格式）** |
| **`spec/methods/{method-id}.md`** | **交付方** | **方法声明调整** | **CHANGELOG；改变已有规则编译结果时升级为结构性变更（需 ADR）** |
| `spec/ASSUMPTION_PROTOCOL.md` | 交付方 | 协议调整 | 随协议调整；改变已有 assumption 处理结果时需 ADR |
| `spec/INTERFACE_CONTRACT_SPEC.md` | 交付方 | 槽位定义变化、连接实例格式变化 | 结构性变更需 ADR |
| `spec/CONTEXT_ASSEMBLY.md` | 交付方 | 装配场景变化、切片规则变化 | 结构性变更需 ADR；切片调整需 CHANGELOG |
| `spec/GROUNDING_CRITERIA.md` | 人类责任方 | 判据新增需 ADR；可查方式调整需 CHANGELOG | ADR（新增判据）；CHANGELOG（可查方式） |
| `contracts/` | 交付方 | 槽位定义变化、样例更新 | 结构性变更需 ADR |
| `knowledge/` | 任何执行者 | 条目新增/变更（受 `CONSTITUTION.md` 第 2、3 条约束） | 随来源治理 |
| `adr/` | 任何执行者 | 治理决策发生 | 状态 `proposed` 即时登记，`accepted` 需人类责任方 |
| `validation/` | 交付方 | 规则变化时由 `spec/COMPILATION_META.md` + 启用的方法声明重建 | 随规则演进 |
| `validation/test-cases/` | 交付方 | 用例新增/修正 | 随用例更新 |
| `scripts/` | 交付方 | 脚本规格变化 | 随规格更新 |

**为什么目录结构的权威放在本文件而非 README**：目录结构不是“给新读者的介绍”，而是“对执行者的约束”——它规定了哪些文件可以被修改、由谁修改、更新频率如何。这些属于执行约定，与第 1 条的资料获取纪律、第 2 条的检查机械化同层。`README.md` 的职责是**让读者尽快找到入口**，它保留一份导航表即可；两份文档的职责边界因此清晰：**README 回答“我该读什么”，AGENTS 回答“这个仓库怎么运转”**。

### 5. 输出结构约定

每次产出必须物理分离为两个区块：

- **`grounded` 区块**：每个命题携带非空 `grounding_ref`，指向 `SOURCE_LEDGER.md` 中的条目 ID。
- **`assumption` 区块**：每个命题携带 `grounding_ref: null`，并附带一个**可检验的验证条件**（在什么条件下该假设可以被确认为真或假），格式按 `spec/ASSUMPTION_PROTOCOL.md`。

**禁止**：把无来源断言写进 `grounded` 区块；把 `assumption` 当作事实前提继续推理；在 `assumption` 区块省略验证条件。

### 5bis. 术语引用纪律

输出中涉及术语时，遵循以下纪律：

1. **机制术语（`GLOSSARY.md` B、C、D 类）**：必须使用 `GLOSSARY.md` 中的定义义，不得另创同义词。首次出现时内联一句话定义，或指向 `GLOSSARY.md#term_id`。
2. **行业缩写（E 类）**：首次出现必须内联展开全称。
3. **领域无关核心概念（A 类）**：使用 `GLOSSARY.md` 或 `knowledge/anchored-entries.jsonl` 中的定义；二者冲突时以 JSONL 为准。
4. **不得使用未登记的同义词**：若某概念已有术语条目，不得用另一个词表达同一概念。
5. **术语定义缺失时**：阻断并报告缺失项，**不得自行推断或编造定义**（与槽位填充的纪律一致）。

**违反术语引用纪律的输出**：不构成成文法违规，但构成执行层缺陷，记录并修正。若某术语的定义在 `GLOSSARY.md` 中缺失而输出中使用了该术语，视为 `GLOSSARY.md` 的缺口，登记于 `TODO.md`。

### 6. 标准工作流（一次项目管理活动）

1. **输入解包**：把输入分为事实 / 目标 / 强加决策三类。每条事实检查出处（无出处者标为“待勘察”，不得作为决策依据）。
2. **槽位填充**：读取当前挂载的领域技能契约（`contracts/` 中的独立契约文件），填充 `Subject`、`Deliverable` 形态、`Constraint` 子类、`Assertion` 词汇。槽位未填充 → 阻断并报告缺失项，不做推断。
3. **规则适用性判定**：按 `GRAMMAR.md` 每条规则的 `applicability` 字段判断适用/不适用/待定。不适用降级为 `advisory`，待定按 `assumption` 处理并登记勘察义务。
4. **知识查询**：需要方法知识时，从 `knowledge/methods/` 按 `method_name` 或适用场景做确定性检索；不得凭参数记忆生成方法步骤。
5. **检查执行**：调用确定性校验器执行 `validation/CHECKLIST.md`；生成模型只负责把校验器的结论转述为人类可读表述。
6. **产出留痕**：`grounded` / `assumption` 分离；未通过检查项按 `severity` 处理（`block` 阻断、`warn` 记录、`advisory` 提示）。
7. **批准路由**：高影响产出交给批准角色；生成模型不写入批准状态。
8. **调度登记**：实质性变更追加 CHANGELOG 批次；识别出的未完成项登记 TODO。

### 6bis. 与 QUICKSTART、装配、接地的衔接

- **首次使用**：读 `QUICKSTART.md`，按第 2 节走一遍最小样例。
- **每次运行前**：宿主运行时按 `spec/CONTEXT_ASSEMBLY.md` 执行装配，产出装配清单。
- **每次运行后**：检查装配清单的 `degradations` 与 `blocked` 字段；若有降级或阻断，记录并报告。
- **部署前**：按 `spec/GROUNDING_CRITERIA.md` 执行接地判定；未接地时按 `CONSTITUTION.md` 第 12.3 条处理。
- **发现错误时**：登记 `ERRATA.md`（若属于本技能自身的表述错误）或 `CHANGELOG.md`（若属于文件变更）。

### 7. 与宿主运行时的分工

- **宿主提供**：确定性校验器、契约解析器、白板存储（若存在）、批准状态写入接口。
- **本技能提供**：规则、来源、方法条目、检查清单规格、契约 schema、`assumption` 协议。
- **PACT 若存在**：作为**可选的运行时准入层**，把本技能的规则编译为 `Token` 类型与 `Precondition`。**必须诚实声明不可映射项**（OR 分支、时钟相关规则、字段级问责写入）。无 PACT 时，技能自身完备。
- **三空间本体若存在**：作为**可选的语义扩展**，填充约束分类维度。**无三空间时，约束分类退回通用分类（目标/环境/方案）**。三空间与 SE 技能的映射关系在 `spec/INTERFACE_CONTRACT_SPEC.md` 中以 `assumption` 形式存在，附带验证条件（与 SE 技能原文一致），不冒充已确认事实。
- **任何领域技能若存在**：作为**横向对等体**，通过契约文件填充槽位。**没有任何领域技能享有特殊地位**；需求工程、软件工程、建筑施工与任何未来领域技能，都是可声明的槽位填充者。技能间的具体连接实例（如需求→软件的产物流动）登记在 `contracts/examples/` 或部署配置中，不进入成文法。

### 8. 不做的事

- 不生成 `SOURCE_LEDGER.md` 未登记的 `grounding_ref`。
- 不在 `GRAMMAR.md` 中写入领域特有对象名。
- 不在任何项目文件中记录本次运行的临时台账（检索记录、调试输出、试验数据）——临时台账只存在于当次运行，实质性结果按第 3 条登记到 CHANGELOG 或 TODO。
- 不把“检查器沉默”当作“检查通过”。
- 不以“更合理”“最佳实践”“业界共识”作为来源。
- 不在没有 ADR 的情况下修改 `CHARTER.md`、`CONSTITUTION.md`、`GRAMMAR.md`、`SOURCE_LEDGER.md` 的实质内容。
- 不静默删除 TODO 工作项；不改写已登记的 CHANGELOG 批次。
- 不给任何领域技能设置“上游/下游”的特殊地位。
