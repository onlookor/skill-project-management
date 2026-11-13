> 中文 | [English](README.en.md)

## 项目管理接地编译技能

**一句话定位**：把通用项目管理知识编译为**可判定、可溯源、可由小型本地 LLM 执行**的规则与条目，使“项目管理”在不依赖特定领域技能的前提下获得与需求工程、软件工程技能对等的可组合性。

### 这个技能是什么

- 一份**领域真空**的成文法（`GRAMMAR.md`）：只定义任何项目都不可还原的元概念（`Project`、`Actor`、`Commitment`、`Deliverable`、`Constraint`、`Outcome`、`Assertion`），规则中不出现任何领域特有对象。
- 一套**治理结构**（`CHARTER.md` + `CONSTITUTION.md` + `adr/`）：定义成文法由谁修改、如何修改、什么算合法修改；把“初衷”和“元规则”从规则文本中物理分离。
- 一份**封闭的来源登记表**（`SOURCE_LEDGER.md`）：`grounding_ref` 的合法取值被封闭枚举，每条来源携带版本、状态（现行/废止/被取代）、权威层级、核验日期与**论断级映射**（这条来源支持哪条具体规则）。
- 一个**方法注册表**（`knowledge/`）：本体条目与方法条目分置。方法条目（估算、WBS 分解、风险识别、挣值计算、采购流程……）是本地小模型知识饥饿的直接补足物；本体条目（核心术语与关系）是成文法可判定的语义基础。
- 一套**编译与验证规范**（`spec/` + `validation/`）：把规则翻译为**确定性校验器**可执行的检查清单，并规定 `assumption` 的格式与验证条件。
- 一份**接口契约规范**（`contracts/`）：定义领域技能向项目管理技能填充槽位的方式，v1 只启用**单层权威位置**（独立契约文件），多层的合并语义已定义但不启用。

### 这个技能不是什么

- **不是 PMBOK 的摘编**。PMBOK 的过程与知识领域是特定方法论的产物；本技能的本体基元锚定在领域无关的核心层（ProjectCO 核心概念与 ISO 21502:2020 的概念框架），具体方法论以方法条目存在，不进入成文法。
- **不是知识库的替代品**。方法注册表是**可确定性检索**的知识载体，不是供模型通读的教科书。
- **不是某个宿主运行时的绑定**。PACT、外部领域本体、任何外部协调引擎或本体框架都是**可选插件**；没有它们，技能仍然完备（见 `CHARTER.md` 承诺 C4）。
- **不是一个会“思考”的项目经理**。它提供合法性判据、知识条目与检查清单；决策权重、批准责任与人类评审点不可让渡（`CONSTITUTION.md` 第 1 条、`CHARTER.md` 承诺 C5）。

## 文件地图（导航指针，**以 `AGENTS.md` 第 4 条为权威**）

| 文件 | 层 | 作用 |
|---|---|---|
| `README.md` | 入口 | 本文件：定位、导航、阅读路径 |
| `README.en.md` | 入口 | 英文版：与中文版结构对应 |
| `manifest.json` | 入口 | 包版本与契约 schema 版本（供外部技能引用） |
| **`QUICKSTART.md`** | **入口** | **快速开始：最小走查样例 + LLM 接合示例** |
| `AGENTS.md` | 执行 | 执行约定：资料获取（本地优先）、schedule 纪律、目录结构权威、检查机械化 |
| `CHANGELOG.md` | 调度 | 变更历史的唯一登记处（规则见 `AGENTS.md` 第 3.1 条） |
| `TODO.md` | 调度 | 后续工作的唯一登记处（规则见 `AGENTS.md` 第 3.2 条） |
| `STATE.md` | 调度 | 逐文件当前状态的唯一登记处 |
| **`ERRATA.md`** | **调度** | **幻觉更正台账：编制错误、外部评审处置、待核验表述** |
| `CHARTER.md` | 意图 | 技能为什么存在、服务谁、可检验承诺 C1–C6、与领域技能的横向关系 |
| `CONSTITUTION.md` | 治理 | 成文法由谁修改、如何修改；来源封闭性；自包含三级；可选插件条款；编译治理总纲（第 10 条）；术语治理与引用规则（第 11 条）；**接地治理（第 12 条）** |
| `GRAMMAR.md` | 立法 | 成文法规则组 A–G |
| `SOURCE_LEDGER.md` | 立法 | 封闭来源登记表（含版本、状态、权威层级、论断级映射） |
| **`GLOSSARY.md`** | **立法（支撑）** | **术语表：领域无关核心概念、框架自创机制术语、编译域术语、治理术语、行业缩写、接口契约术语；含术语治理与引用规则** |
| **`spec/COMPILATION_META.md`** | **编译元框架** | **什么是合法的编译：P1–P6、准入条件、选择/共存/替换、失败分类、编译治理** |
| **`spec/COMPILATION_METHODS.md`** | **编译方法注册表** | **有哪些编译方法、当前启用哪个、为什么、替换历史** |
| **`spec/CONTEXT_ASSEMBLY.md`** | **执行** | **上下文装配规范：四场景加载集、token 预算、装配清单** |
| **`spec/GROUNDING_CRITERIA.md`** | **执行** | **接地完成判据：六条判据、状态语义、判据记录** |
| **`spec/ANCHOR_SPEC.md`** | **规范** | **锚点与引用规范：稳定 ID、标题路径、指纹基线、失效显式报错** |
| `spec/ONTOLOGY_FEASIBILITY.md` | 评估 | 自建本体的可行性评估与方案对比（非规范，不改变规则） |
| **`spec/methods/deterministic-checker.md`** | **具体编译方法** | **确定性校验器方法的声明：覆盖范围、P1–P6 论证、check_id 注册表、翻译规范** |
| `spec/ASSUMPTION_PROTOCOL.md` | 执行 | `assumption` 区块的格式与验证条件规范（方法无关） |
| `spec/INTERFACE_CONTRACT_SPEC.md` | 执行 | 槽位定义；**技能间信息流**；v1 单层解析；PACT 不可映射项声明（方法无关） |
| `contracts/` | 执行 | 契约 schema、解析规则、两个领域样例（建筑施工、软件工程） |
| `knowledge/` | 知识 | 本体条目与方法注册表（可确定性查询，不供通读） |
| `ontology/` | 派生工件 | 自建本体（`active`：92 类 / 35 对象属性 / 40 过程 / 124 工件 / 185 工具与技术 / 24 条形状；非规范、非来源，边界见 `CONSTITUTION.md` 第 13.6 条） |
| `adr/` | 治理 | ADR 格式说明与治理决策记录（ADR-0001–ADR-0010） |
| **`scripts/`** | **辅助** | **辅助检查脚本：STATE 对账、来源编译落点、锚点解析与校验、GLOSSARY/JSONL 同步规格** |
| `validation/CHECKLIST.md` | 执行 | 由 `COMPILATION_META.md` + `spec/methods/deterministic-checker.md` 生成的检查清单 |
| **`validation/test-cases/`** | **执行** | **反例检验用例库（当前 3 个已落盘）** |

**关于领域技能的地位**：本技能与任何领域技能（需求工程、软件工程、建筑施工……）都是**横向对等关系**，没有任何领域技能享有特殊地位。技能间的具体连接实例（如需求→软件的产物流动）登记在 `contracts/examples/` 或部署配置中，**不进入成文法**，定义见 `spec/INTERFACE_CONTRACT_SPEC.md` 的“技能间信息流”章节。

**关于编译方法的地位**：编译方法本身是可选插件，不构成技能完备性的前提（`CONSTITUTION.md` 第 10.3 条）。当前启用 `CM-DET-CHECKER`；其他方法（技能卡片、人类检查单、PACT 规则）登记为候选，启用走 ADR。

## 版本与发布

- 包版本只有一个，以 annotated git tag 声明发布点（ADR-0003）；tag 说明即发布说明。当前发布点：`v0.4.0`。
- 文件不承载版本号，也不承载文件级状态；当前状态查 `STATE.md`，变更历史查 `CHANGELOG.md`。
- 外部技能引用本包时读根目录 `manifest.json`；`pm_contract_version` 是契约文件的数据字段，不随包版本走。
- 版本递增：规范条文或契约 schema 不兼容 → major；新增规范或文件 → minor；纯澄清与 errata → patch。
- 编译产物的过期判定以生成基线的 `source_commit` 为准（ADR-0004），不以版本号比较。

## 三条阅读路径

**首次接触（想知道这是什么）**：本文件 → `QUICKSTART.md` → `CHARTER.md` 的“可检验的设计承诺”一节 → `GRAMMAR.md` 的规则组 A → 遇到不熟悉的术语时查 `GLOSSARY.md`。

**日常使用（要把技能接进一个项目）**：`AGENTS.md` 第 6、6bis 条 → `spec/CONTEXT_ASSEMBLY.md` → `spec/INTERFACE_CONTRACT_SPEC.md` 的槽位定义 → `contracts/examples/` 里最接近的样例 → 在自己的领域技能目录放置契约文件 → `validation/CHECKLIST.md` → 部署前按 `spec/GROUNDING_CRITERIA.md` 判定。

**治理修改（要改动成文法、来源或编译）**：`CONSTITUTION.md` 全文 → `adr/0001-*.md`、`adr/0002-*.md`、`adr/0003-*.md`、`adr/0004-*.md`、`adr/0005-*.md`、`adr/0006-*.md`、`adr/0007-*.md` → `adr/ADR-TEMPLATE.md` → `SOURCE_LEDGER.md` 的登记规则 → 若涉及术语，读 `GLOSSARY.md` 第 4、5 节与 `CONSTITUTION.md` 第 11 条 → 若涉及编译，读 `spec/COMPILATION_META.md` 与 `spec/COMPILATION_METHODS.md` → 若涉及引用或锚点，读 `spec/ANCHOR_SPEC.md` 并运行 `scripts/check_anchors.py` → 变更完成后追加 `CHANGELOG.md` 批次、更新 `TODO.md` 状态；发现错误登记 `ERRATA.md`。
