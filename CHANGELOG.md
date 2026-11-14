## 变更历史

**登记规则**：见 `AGENTS.md` 第 3.1 条。按批次追加，禁止改写已登记批次。

### 批次 0001 — 2026-11-11 — 初始交付

- **涉及文件**：`README.md`、`AGENTS.md`、`CHARTER.md`、`CONSTITUTION.md`、`GRAMMAR.md`、`SOURCE_LEDGER.md`、`spec/COMPILATION_SPEC.md`、`spec/ASSUMPTION_PROTOCOL.md`、`spec/INTERFACE_CONTRACT_SPEC.md`、`contracts/schema/pm-slot-contract.schema.json`、`contracts/resolver.md`、`contracts/examples/construction.pm-contract.yaml`、`contracts/examples/software-engineering.pm-contract.yaml`、`knowledge/anchored-entries.jsonl`、`knowledge/methods/registry-skeleton.md`、`adr/ADR-TEMPLATE.md`、`adr/0001-separate-grammar-from-governance.md`、`validation/CHECKLIST.md`、`CHANGELOG.md`、`TODO.md`
- **变更摘要**：技能 v0.1 初始交付。四层结构（意图/治理/立法/执行）建立；成文法规则组 A–G 定义（A/C/D/E 为 `active`，B 为 `pending_reanchor`，F/G 为 `assumption`）；来源登记表封闭枚举 8 个条目（含 1 个 `deprecated`）；接口契约 v1 单层解析启用，多层合并语义定义但不启用；方法注册表骨架与 5 条首批方法条目入库；治理 ADR-0001 记录规范层与执行层物理分离决策。
- **关联 ADR**：ADR-0001（accepted）
- **状态**：`pending-adr` 解除（ADR-0001 已 accepted）

---

### 批次 0002 — 2026-11-11 — 编译域拆分

- **涉及文件**：
  - 新建：`spec/COMPILATION_META.md`、`spec/COMPILATION_METHODS.md`、`spec/methods/deterministic-checker.md`
  - 删除：`spec/COMPILATION_SPEC.md`（内容上收至 META、下沉至 deterministic-checker.md）
  - 修改：`CONSTITUTION.md`（第 5 条保护清单新增项、新增第 10 条）、`README.md`（文件地图、阅读路径、状态与版本）、`AGENTS.md`（第 4 条目录结构）、`validation/CHECKLIST.md`（文件头生成依据）、`TODO.md`（新增工作项、更新引用）
  - 新建：`adr/0002-compilation-meta-vs-methods.md`
- **变更摘要**：将编译域拆分为“元框架（方法无关）/ 方法注册表 / 具体方法声明”三层，与“项目管理元框架 / 领域技能”同构。原 `spec/COMPILATION_SPEC.md` 的方法无关部分上收至 `COMPILATION_META.md`，方法有关部分下沉至 `spec/methods/deterministic-checker.md`。`CONSTITUTION.md` 新增第 10 条（编译治理总纲），第 5 条保护清单覆盖编译域基础约束。方法注册表当前启用 `CM-DET-CHECKER`，登记四个候选方法（技能卡片、人类检查单、PACT 规则、神经符号编译）。
- **关联 ADR**：ADR-0002（accepted）
- **状态**：生效

---

### 批次 0003 — 2026-11-11 — 术语表与术语治理

- **涉及文件**：
  - 新建：`GLOSSARY.md`（术语表，首批约 80 条）、`CONSTITUTION.md` 新增第 11 条（术语治理与引用规则）
  - 修改：`AGENTS.md`（新增第 5bis 条术语引用纪律；第 4 条目录结构加入 `GLOSSARY.md`）、`README.md`（文件地图加入 `GLOSSARY.md`；阅读路径补术语查询）、`TODO.md`（新增术语表相关工作项）
- **变更摘要**：新增 `GLOSSARY.md` 作为立法层的支撑文件，覆盖 A 领域无关核心概念（16 条）、B 框架自创机制术语（20 条）、C 编译域术语（15 条）、D 治理术语（13 条）、E 行业缩写（10 条）、F 接口契约术语（8 条）。`CONSTITUTION.md` 新增第 11 条，规定术语准入条件、引用纪律、废弃与合并、与 `anchored-entries.jsonl` 的同步、与 `SOURCE_LEDGER.md` 的关系、版本纪律。`AGENTS.md` 新增第 5bis 条，规定输出中的术语引用纪律。
- **关联 ADR**：无（术语表的建立是 CHANGELOG 级变更；术语治理条款的加入是 `CONSTITUTION.md` 的实质变更，但因其不降低第 5 条保护清单中的任何约束，且由本批次记录，不单独设 ADR。若未来某术语的定义变更影响规则理解，则需 ADR。）
- **状态**：生效

---

### 批次 0004 — 2026-11-11 — 状态台账与仓库初始化

- **涉及文件**：
  - 新建：`STATE.md`、`.gitignore`
  - 修改：`README.md`（移除状态与版本段及修订标记，文件地图加入 `STATE.md`）、`AGENTS.md`（目录结构与维护责任表加入 `STATE.md`）、`GLOSSARY.md`、`GRAMMAR.md`、`SOURCE_LEDGER.md`、`spec/ASSUMPTION_PROTOCOL.md`、`spec/COMPILATION_META.md`、`spec/COMPILATION_METHODS.md`、`spec/INTERFACE_CONTRACT_SPEC.md`、`contracts/resolver.md`、`knowledge/methods/registry-skeleton.md`、`validation/CHECKLIST.md`（删除文件头版本行、文件级状态行与变更记录）
- **变更摘要**：将各文件的版本与文件级状态元信息移出正文，集中登记于 `STATE.md`；`CHANGELOG.md` 继续记录批次历史，`TODO.md` 继续记录待办与任务状态。在 `project-management/` 内初始化 Git 仓库并完成初始提交。
- **关联 ADR**：无（不改变任何规范语义）
- **状态**：生效

---

### 批次 0005 — 2026-11-11 — 上下文装配、接地判据与反例用例

- **涉及文件**：
  - 新建：`QUICKSTART.md`、`ERRATA.md`、`spec/CONTEXT_ASSEMBLY.md`、`spec/GROUNDING_CRITERIA.md`、`scripts/README.md`、`scripts/check_glossary_sync.md`、`validation/test-cases/README.md`、`validation/test-cases/TC-A1-02.md`、`validation/test-cases/TC-C1-03.md`、`validation/test-cases/TC-E1-04.md`
  - 修改：`CONSTITUTION.md`（第 11.5 条末尾补同步检查的执行方式；新增第 12 条接地治理）、`AGENTS.md`（第 4 条目录结构与维护责任表；新增第 6bis 条与 QUICKSTART、装配、接地的衔接）、`README.md`（文件地图、阅读路径、`CONSTITUTION.md` 行）、`STATE.md`（新增 10 个文件登记）、`TODO.md`（新增工作项）、`CHANGELOG.md`（本批次）
- **变更摘要**：依据分享链接 2 的内容，补齐“上下文装配（`spec/CONTEXT_ASSEMBLY.md`）”“接地完成判据（`spec/GROUNDING_CRITERIA.md`）”“最小走查样例（`QUICKSTART.md`）”“幻觉更正台账（`ERRATA.md`）”“反例检验用例库（`validation/test-cases/`）”“术语同步检查规格（`scripts/`）”六个缺口；`CONSTITUTION.md` 新增第 12 条（接地治理），与第 10 条（编译治理）、第 11 条（术语治理）并列。分享链接 1 的诊断项中，装配规范、走查样例、反例库、ERRATA、接地判据、LLM 接合示例、术语同步机制已由本批次覆盖；ADR 拒绝记录、检查回放机制等未覆盖项登记于 `TODO.md`。
- **取舍说明**：
  1. **批次号顺延**：分享原文标注的批次号为 0004，与已发布的批次 0004（状态台账与仓库初始化）冲突；按第 3.1 条“批次号一经发布永不复用”，本批记为 0005。
  2. **版本头未采用**：分享原文各新文件含 `**版本**：v0.1` 行，`README.md` 含“状态与版本（修订）”段及 `v0.4` 等表述；按现行口径（文件不携带版本头与文件级状态元信息），一律不写入，文件当前状态统一登记于 `STATE.md`，版本历史由本文件批次承载。
  3. **反例用例只落正文**：分享原文表格列 13 个用例，仅 3 个提供完整正文；本批只落这 3 个，其余 10 个登记 `TODO.md` T-101，不补写推断内容。
  4. **接地判据改写**：`GROUNDING_CRITERIA` 的 G2/G3 原依赖产物版本头与版本对齐检查，现行仓库已无版本头，故改为基于 `STATE.md` 与部署配置判定；改动点登记 `ERRATA.md` E-008。
  5. **ID 冲突修复**：`QUICKSTART` 中 assumption 与 HumanActor 共用 `A-001`，assumption 改用 `AS-001`；登记 `ERRATA.md` E-009。
  6. **`partially_grounded` 的保留范围**：该词仅作为接地判定的三值结论之一保留于 `spec/GROUNDING_CRITERIA.md` 第 4 节与 `CONSTITUTION.md` 第 12.3 条，不用于声明本包当前状态。
- **关联 ADR**：无（新增文件不改变既有规则语义；`CONSTITUTION.md` 第 12 条为新增治理条款，未降低第 5 条保护清单中的任何约束，理由同批次 0003）
- **状态**：生效

---

### 批次 0006 — 2026-11-11 — 版本与状态治理决策

- **涉及文件**：
  - 新建：`adr/0003-version-and-state-governance.md`
  - 修改：`STATE.md`（登记 ADR-0003）、`TODO.md`（新增 T-109、T-110）、`CHANGELOG.md`（本批次）
- **变更摘要**：记录版本与状态治理决策：文件层不承载版本与状态、包层以 annotated tag 声明单一版本、`STATE.md` 为唯一状态来源且按目录给默认值、版本号按 major/minor/patch 递增、首个包版本取 `v0.4.0`。ADR 同时登记了由该决策引出的两项待办：产物版本链重构（T-109）与 `manifest.json` 与 tag 的一致性检查（T-110）。
- **关联 ADR**：ADR-0003（accepted）
- **状态**：生效

---

### 批次 0007 — 2026-11-11 — 落地包层版本与产物基线

- **涉及文件**：
  - 新建：`adr/0004-artifact-baseline-by-commit.md`、`manifest.json`
  - 修改：`CONSTITUTION.md`（第 9 条、第 11.7 条）、`spec/COMPILATION_META.md`（第 3.6 节、第 7 条编译产物段、第 7.5 节、第 10 条、方法声明模板第 9 节）、`spec/methods/deterministic-checker.md`（第 9 节）、`AGENTS.md`（第 3.1 条、第 4 条目录树与维护责任表）、`README.md`（文件地图、版本与发布、阅读路径）、`ERRATA.md`（E-011）、`TODO.md`（T-108、T-109 关闭；T-110 更新；新增 T-111）、`STATE.md`、`CHANGELOG.md`（本批次）
- **变更摘要**：把“版本号在文件头声明”改为“版本在包层以 annotated tag 声明，文件不承载版本”；新增根目录 `manifest.json` 记录包版本 `0.4.0` 与 `pm_contract_version`；把编译域的“产物版本 = 源文件版本函数”改为“产物记录生成基线的 `source_commit`，装配时比对当前源提交，脏工作区直接判定过期”，拒绝语义保留（ADR-0004）。
- **取舍说明**：
  1. 改动范围超出原计划的 `CONSTITUTION`/`AGENTS`/`README`/`ERRATA`/`TODO`：`spec/COMPILATION_META.md` 与 `spec/methods/deterministic-checker.md` 同样以文件版本为前提，不改会与新第 9 条直接矛盾；经用户确认后一并修改。
  2. 产物基线单立 ADR-0004 而非并入 ADR-0003：前者是运行时机制变更（改变 `validation/` 产物的生成与装配校验方式），后者是版本载体决策；两者的被否方案与代价不同，分列便于日后追溯。
  3. `manifest.json` 的包版本与 tag 可能漂移，登记 T-110 做一致性检查；`validation/CHECKLIST.md` 尚未写入 `source_commit`，登记 T-111，在此之前按“基线未记录”处理为过期。
- **关联 ADR**：ADR-0003（accepted）、ADR-0004（accepted）
- **状态**：生效

---

### 批次 0008 — 2026-11-11 — 状态台账改为目录默认值并对账

- **涉及文件**：
  - 新建：`scripts/check_state.py`
  - 修改：`STATE.md`（由逐文件登记改为“目录默认值 + 例外”）、`scripts/README.md`（脚本清单与运行方式）、`AGENTS.md`（第 4 条目录树）、`CHANGELOG.md`（本批次）
- **变更摘要**：`STATE.md` 不再逐文件登记 40 个文件，改为八条目录默认值（`./`、`spec/`、`contracts/`、`contracts/examples/`、`knowledge/`、`adr/`、`scripts/`、`validation/`）加两条例外（`adr/ADR-TEMPLATE.md` 为 `template`、`knowledge/methods/registry-skeleton.md` 为 `skeleton`）。新增 `scripts/check_state.py`，以 `git ls-files` 为准校验：漏登、登了未被跟踪的文件、状态值非法、例外重复均报错，退出码 0/1/2。
- **取舍说明**：状态默认值按最长前缀匹配，避免逐文件维护；例外表只允许承载“目录默认值不足以描述”的文件，防止例外表退化为第二份逐文件清单。`scripts/README.md` 中 `check_glossary_sync` 的实现待办原指向 `T-102`（该编号已用于 ADR 拒绝记录），一并更正为 `T-090`。
- **关联 ADR**：ADR-0003（accepted）
- **状态**：生效

---

### 批次 0009 — 2026-11-12 — 来源表收缩、本地资料入表与三空间清理

- **涉及文件**：
  - 新建：`adr/0005-source-ledger-scope.md`、`adr/README.md`
  - 修改：`SOURCE_LEDGER.md`（整体重写）、`CONSTITUTION.md`（第 2.3、2.4、3.6、4、6、8、10.3、10.7 条）、`CHARTER.md`（C4）、`GRAMMAR.md`（规则组 B 状态说明与汇总表）、`GLOSSARY.md`（T-B-006、T-B-020、T-C-012、T-D-005、T-E-001、T-E-003、T-E-005、T-E-007）、`README.md`（文件地图与定位）、`AGENTS.md`（第 4 条目录树、第 7 节）、`ERRATA.md`（删除原 E-001；E-002、E-003 改写去悬空引用）、`adr/ADR-TEMPLATE.md`、`spec/ASSUMPTION_PROTOCOL.md`、`spec/COMPILATION_META.md`、`spec/CONTEXT_ASSEMBLY.md`、`spec/methods/deterministic-checker.md`、`contracts/examples/construction.pm-contract.yaml`、`knowledge/anchored-entries.jsonl`、`knowledge/methods/registry-skeleton.md`、`TODO.md`（新增 T-112、T-113）、`CHANGELOG.md`（本批次）
- **变更摘要**：删除过期来源 `ISO21500-2012`、`PMBOK7-2021`；将 ADR 记法与 RFC 2119 移出来源表，ADR 格式移入新建的 `adr/README.md`，规范性措辞改引 BCP 14（RFC 2119 + RFC 8174，写入 `CONSTITUTION.md` 第 3.6 条）；把 `resources/pm/` 下实际存在的本地资料登记为正式来源并写明 `local_path`；新增 `SPRINGER-PMBOK-2024`（仅元数据，正文未获取）；OWL 候选保留并标注“有可靠来源但尚未获取”；删除 Jarke 三世界候选，并清理非软件工程语境的三空间叙述；放宽 `CONSTITUTION.md` 第 2.3 条的入表口径、将第 2.4 条改为允许删除并以 git 历史追溯。
- **取舍说明**：
  1. 软件工程语境（`spec/INTERFACE_CONTRACT_SPEC.md` 第 7 节与 `contracts/examples/software-engineering.pm-contract.yaml`）中的“三空间”作为该领域技能的专有概念保留，其余文档一律改为“外部领域本体”。
  2. `ERRATA.md` 原 E-001 随 Jarke 条目一并删除，条目编号不再复用；E-002、E-003 因引用已删除的来源 ID 而改写表述，事实与处置结论未变。
  3. `PRINCE2® 7th Edition（无水印）.pdf` 不作为核对依据，内容以官方水印版为准；排除的是副本，不是文献。
- **关联 ADR**：ADR-0005（accepted）
- **状态**：生效

---

### 批次 0010 — 2026-11-12 — 区分知识来源与规范依据并强制编译落点

- **涉及文件**：
  - 新建：`adr/0006-knowledge-sources-vs-normative-basis.md`、`scripts/check_ledger_landings.py`
  - 修改：`CONSTITUTION.md`（第 2 条新增两类文献区分与 `compilation_landing` 字段；第 2.1 条接第 2.6 条；新增第 2.6 条）、`SOURCE_LEDGER.md`（字段说明与 7 个 active 条目的编译落点）、`scripts/README.md`、`AGENTS.md`（第 4 条目录树）、`README.md`（文件地图）、`TODO.md`（新增 T-114、T-115）、`CHANGELOG.md`（本批次）
- **变更摘要**：把“知识来源”与“规范依据”拆为两类；来源表新增正向准入测试（领域无关 + 编译落点），每条 active 来源必须能指向 `GRAMMAR.md` 规则、`knowledge/` 条目、方法条目或检查项；新增 `check_ledger_landings.py` 机械核对落点存在性，`SPRINGER-PMBOK-2024` 因正文未获取记 `pending:T-112`。
- **取舍说明**：`compilation_landing` 与 `claim_mapping` 保留并存——前者用于机械检查、后者保留论断级的自然语言说明；两者漂移风险登记为后续缺口，未在本批次引入额外校验。
- **关联 ADR**：ADR-0006（accepted）
- **状态**：生效

---

### 批次 0011 — 2026-11-12 — 开源化：MIT 许可证与英文 README

- **涉及文件**：新增 `LICENSE`、`README.en.md`；修改 `README.md`（顶部语言互链、治理阅读路径补 ADR-0005/0006）、`CHANGELOG.md`（本批次）
- **变更摘要**：加入 MIT 许可证（版权人 `onlookor`，年份 2026）；新增与中文版结构对应的英文 README，并在两版顶部互相链接；中文版保持为默认入口，未被覆盖。
- **取舍说明**：英文版按现有中文 README 逐节翻译，未新增任何未实现的能力描述；文件地图中增加 `README.en.md` 一行以保持两版导航对称。
- **关联 ADR**：无（不改变规范语义）
- **状态**：生效

---

### 批次 0012 — 2026-11-12 — Zenodo 候选条目核查结论

- **涉及文件**：`SOURCE_LEDGER.md`（候选条目改记为已核实存在、领域不符）、`ERRATA.md`（新增 E-012）、`README.md`（文件地图补 `README.en.md`）、`CHANGELOG.md`（本批次）
- **变更摘要**：实际检索 Zenodo 与搜索引擎，确认该论文存在（Jennifer Evans，2025-12-24 预印本，DOI `10.5281/zenodo.18039274`；同日另有 `10.5281/zenodo.18043672`）。结论：**不是幻觉**，但主题为 RAG 与幻觉机制，不满足通用项目管理领域测试，仍不入表。
- **取舍说明**：两项记录题名不同、作者与日期相同，无法仅凭页面判断哪一项是评审当初所指；登记中并列两个 DOI，不擅自合并。
- **关联 ADR**：无（候选条目未入表，不改变规范）
- **状态**：生效

---

### 批次 0013 — 2026-11-12 — 按本地实际文件名修正来源表 local_path

- **涉及文件**：`SOURCE_LEDGER.md`、`CHANGELOG.md`（本批次）
- **变更摘要**：逐份核对 `resources/pm/` 的实际文件名后，修正 `ISO21502-2020`、`PRINCE2-2023`、`ProjectCO-2024`、`ThingFO-2021`、`PMBOK8-2025` 的 `local_path`，并同步修正非官方镜像的排除记录。此前登记的路径是简化写法，与磁盘上的文件不对应。
- **取舍说明**：只改路径字符串，来源条目、落点与结论不变；PMBOK 第 8 版的出版日期经 PMI 官方页面核对为 2025-11，本地文件元数据标注 2026 系该副本的版权/印刷年，不据以修改版本年份。
- **关联 ADR**：无（登记信息的准确性修正）
- **状态**：生效

---

### 批次 0014 — 2026-11-12 — 锚点稳定化：禁用行号、稳定 ID 与指纹基线

- **涉及文件**：
  - 新建：`spec/ANCHOR_SPEC.md`、`scripts/check_anchors.py`、`scripts/anchor_baseline.json`、`adr/0007-anchor-discipline.md`
  - 修复失效引用：`CONSTITUTION.md`（第 3.1、4、7.3 条）、`GRAMMAR.md`（权威关系、字段表）、`validation/CHECKLIST.md`（执行纪律第 1、5 条）、`spec/ASSUMPTION_PROTOCOL.md`（第 5、8 节）、`spec/INTERFACE_CONTRACT_SPEC.md`（第 8 节）、`spec/COMPILATION_METHODS.md`（CM-DET-CHECKER 的 `spec` 字段）、`spec/methods/deterministic-checker.md`（附录来源说明）、`TODO.md`（T-013、T-070、T-114）
  - 同步：`scripts/README.md`、`AGENTS.md`（目录树、维护责任表）、`README.md`（文件地图、治理阅读路径）、`CHANGELOG.md`（本批次）
- **变更摘要**：盘点全仓锚点形态，确认活跃文件无行号锚点（规则/检查项/来源/术语/方法/待办均为稳定 ID，另有 236 处章节号引用）；行号锚仅存在于 ADR-0006 的 7 处历史证据中，且已随来源表重写失效。新增锚点规范与检查器：禁止行号 locator，校验文件、稳定 ID、章节号与标题路径可解析，校验 `grounding_ref` 均指向 active 来源，并对 `GRAMMAR.md` 17 条规则与 `SOURCE_LEDGER.md` 7 个来源做文本块指纹比对。首轮实跑清出 11 处指向已删除 `COMPILATION_SPEC.md` 的活跃引用并全部修复（T-070 完成）。
- **取舍说明**：不引入软工技能的 `@m:`/`@d:` 前缀语法——现有引用在插行场景下本就稳定，全量改写没有定位收益。只复用其“稳定地址、行号禁用、指纹只作漂移、失效显式报错、冻结 as-of”五条原则。指纹采用“空白规范化 + sha256”，不引入 Markdown AST 依赖。
- **负例验证**：在副本中插入一行——块外插入 0 错误 0 警告；在 G-A1 块内插入仅 `rule:G-A1` 一条漂移警告，其余 16 条规则与 7 个来源不受影响。
- **关联 ADR**：ADR-0007（accepted）
- **状态**：生效

---

### 批次 0015 — 2026-11-12 — 按本地 PDF 核对来源；规则组 B 重新锚定

- **涉及文件**：
  - 修改：`GRAMMAR.md`（第 1 条说明、规则组 B 引言与 G-B1/G-B2、G-F1–G-F4 与 G-G1–G-G3 的核验注、规则组状态汇总表 B 行）、`SOURCE_LEDGER.md`（`ISO21502-2020`、`PRINCE2-2023`、`ProjectCO-2024`、`ThingFO-2021`、`PMBOK8-2025`、`SPRINGER-PMBOK-2024` 的核验状态、`claim_mapping`、`allowed_uses`；废止记录；状态汇总）、`ERRATA.md`（新增 E-013–E-016，更新 V-001–V-003）、`TODO.md`（T-113 关闭，T-112 补注，新增 T-118、T-119）、`spec/ANCHOR_SPEC.md`（外部资料页码定位的澄清）
  - 新建：`adr/0008-reanchor-dimension-rules.md`
- **变更摘要**：安装并验证 poppler（`pdftotext`/`pdfinfo`/`pdftoppm`）与 Tesseract（eng/chi_sim/chi_tra），对 `resources/pm/` 六份 PDF 逐份判定载体形态：全部具备文本层，无整本扫描件；ProjectCO 的插图页另做 300 dpi 转图 OCR 复核。核对结论：ISO 21502:2020 不含“五过程组 × 十主题组”矩阵，正文为第 6 章集成实践（八个生命周期位置）与第 7 章管理实践（十七项）；附录 A 对 ISO 21500:2012 的映射为资料性。G-B1、G-B2 据此改写并解除 `pending_reanchor`，`severity` 保持 `advisory`（ADR-0008）。PRINCE2 第 7 版七项原则名称、授权链、产品验收与收尾、问责委派已逐页核对并记入。勘误另记：SPRINGER 请求信实际未发出（SMTP 535）、ProjectCO 本地副本未见 `Actor`/`Commitment`/`Constraint` 三个术语（原文用 `Agent`）。
- **取舍说明**：未改动 `knowledge/` 条目与 G-A1/G-D1/G-E1 的规则文本——术语归属需先取得论文外部附录（T-119），规则改写需另走 ADR。中间产物（全文文本、渲染图、OCR 输出）全部落在 `/tmp/pm-extract/`，未进入仓库；`SOURCE_LEDGER.md` 只登记页码定位与自述结论，不复制原文段落。
- **验证**：`scripts/check_state.py`、`scripts/check_ledger_landings.py`、`scripts/check_anchors.py` 全部通过；锚点指纹基线已按规则文本变更重新冻结。
- **关联 ADR**：ADR-0008（accepted）
- **状态**：生效

---

### 批次 0016 — 2026-11-12 — 原始资料与提取产物禁入库，并接入阻断式检查

- **涉及文件**：
  - 修改：`CONSTITUTION.md`（新增第 13 条；第 5 条保护清单增列第 13 条）、`AGENTS.md`（新增第 7bis 条；第 4 条目录树加入 `.githooks/` 与 `check_no_raw_material.py`）、`.gitignore`（原始资料、扫描件、压缩包与提取产物命名）、`scripts/README.md`（脚本清单、运行方式、判定规则与阈值）、`TODO.md`（新增 T-120）
  - 新建：`scripts/check_no_raw_material.py`、`.githooks/pre-commit`、`adr/0009-no-raw-material-in-git.md`
- **变更摘要**：把“PDF 原文与成段摘录不得进 git”从说明升级为可阻断的纪律。第 13 条明确四类禁止内容（原始资料、提取产物、成段原文、可替代原作的改写）与四类允许形态（页码定位、来源标识、单条不超过一行或一句并附出处的最短引证、自述转述），并规定检查失败即阻断提交。检查器扫描已跟踪文件，按扩展名、体积、引用长度、连续长行、页码序列、目录点线、替换字符与控制字符判定；pre-commit 钩子调用同一脚本。
- **扫描结果**：当前 51 个跟踪文件 0 错误；全历史 `git log --all --diff-filter=A` 未发现任何文档/电子书/图片/压缩包类文件被加入过；最大跟踪文件 35 KB（`GLOSSARY.md`）；未发现贴入 Markdown 的成段原文。
- **负例验证**：在临时仓库放入伪造 PDF、600 KiB 文本、500 字符引用、8 行页码序列，检查器报出 `RM-EXT`、`RM-SIZE`、`RM-QUOTE`、`RM-PAGESEQ` 并以 1 退出；启用钩子后同一提交被拒绝（`git commit` 退出码 1），仓库只保留基线提交。
- **取舍说明**：引用块阈值按现有文档上限（343 字符）留出余量取 800 字符；连续长行阈值按现有最长连续段（6 行）取 15 行。检查器只覆盖“可机械判定”的形态，纯改写型替代无法凭文本特征识别，由第 13.1 条第 4 项与人工评审兜底，不宣称检查器能覆盖全部违规。
- **钩子接入**：`git config core.hooksPath .githooks`（当前克隆已启用；该设置不入库，克隆方需自行执行，等价命令已写入 `scripts/README.md` 与 `AGENTS.md` 第 7bis 条）。
- **关联 ADR**：ADR-0009（accepted）
- **状态**：生效

---

### 批次 0018 — 2026-11-13 — 自建本体可行性评估与受控入库

- **涉及文件**：
  - 新建：`spec/ONTOLOGY_FEASIBILITY.md`、`adr/0010-self-authored-ontology-in-git.md`、`ontology/README.md`
  - 修改：`CONSTITUTION.md`（第 13.2 条新增第 5 项；新增 13.6；第 5 条保护清单措辞）、`AGENTS.md`（第 7bis 条新增第 7 项；第 4 条目录树与维护责任表）、`scripts/check_no_raw_material.py`（本体扩展名与 `RM-ONTO-*`）、`scripts/README.md`、`STATE.md`（新增 `ontology/` 默认状态）、`README.md`（文件地图）、`TODO.md`（新增 T-122–T-123）
- **变更摘要**：对“从本地 PMBOK 8th 自建以约束为主的本体”做可行性评估，并与“手工知识条目 + 反例用例 + 全文档级编译”的基线逐项对比，给出最小原型与全量两档规模。评估结论为：技术可行，采用 SHACL-first；本体保持非规范、非来源。治理侧同步放开一条受控通道：第 13.6 条允许“自写定义 + 标准术语标签”的本体入库，原始资料、提取产物、成段原文与可替代原作的改写仍严禁；检查器新增头注释、超长字面量与超长注释检查。
- **事实更正**：本地 PMBOK 8th 正文显示该版**恢复**了过程式结构——5 个 Focus Areas、7 个绩效域、40 个非规定性过程（Governance 9、Scope 6、Schedule 3、Finance 4、Stakeholders 7、Resources 5、Risk 6），第 4 章为输入/输出、第 5 章为工具与技术。因此“第 8 版缺少过程式类层次”不成立；它缺少的是机器可读本体，不是过程层次。
- **验证**：四个检查器通过（`check_state.py` 0、`check_ledger_landings.py` 0 错误 1 警告、`check_anchors.py` 0 错误 0 警告、`check_no_raw_material.py` 0 错误）。真实负例（临时仓库，不入库）：通过 `.ttl` 通过；含 600 字符转录字面量的 `.ttl` 报 `RM-ONTO-LITERAL`；缺头注释的 `.ttl` 报 `RM-ONTO-HEADER`；600 字符注释行报 `RM-ONTO-COMMENT`；连续 15 行 100+ 字符注释报 `RM-PROSEBLOCK`；伪造 PDF 仍报 `RM-EXT`；全部以非零码退出。
- **取舍说明**：
  1. 批次号取 0018 而非 0017：0017 已在 `TODO.md` 中作为邮件登记标签出现，但未形成 CHANGELOG 条目；为避免同一编号指向两件事，本批顺延，0017 不复用。
  2. 第 13.6 条是对 13.1 第 4 项的边界澄清，不缩小 13.1 的四类禁止，也不降低 13.3 的阻断强度；不满足 13.6 的本体仍按 13.1 禁止。
  3. 未改动 `SOURCE_LEDGER.md`：`PMBOK8-2025` 的 `allowed_uses` 仍限“原则层交叉验证”，本体不得作为 `grounding_ref`；扩展来源用途另立 T-123 与 ADR。
- **关联 ADR**：ADR-0010（accepted）
- **状态**：生效

---

### 批次 0019 — 2026-11-13 — 全量本体与形状校验

- **涉及文件**：
  - 新建：`ontology/pmbok8-vocab.ttl`、`ontology/pmbok8-processes.ttl`、`ontology/pmbok8-artifacts.ttl`、`ontology/pmbok8-tools.ttl`、`ontology/pmbok8-shapes.ttl`、`ontology/fixtures/valid.ttl`、`ontology/fixtures/invalid-*.ttl`（24 个）、`ontology/fixtures/manifest.json`、`scripts/validate_ontology.py`
  - 修改：`ontology/README.md`、`STATE.md`（`ontology/` 改为 `active`）、`AGENTS.md`（第 4 条目录树、第 7bis 条状态）、`README.md`（文件地图）、`TODO.md`（T-122 关闭，新增 T-125、T-126）、`spec/ONTOLOGY_FEASIBILITY.md`（全量档）、`adr/0010-self-authored-ontology-in-git.md`（边界与结果）、`CONSTITUTION.md`（13.6 内容质量口径）
- **变更摘要**：按全量档构建本体：92 个类、35 个对象属性、7 个数据类型属性、7 个绩效域、5 个焦点区、40 个过程及其输入/输出/技术链接、124 个工件、185 个工具与技术、24 条 SHACL 形状，以及每条形状对应的违规 fixture。工件与工具个体保留术语名、类别与页码，定义状态为 `taxonomy-only`；类与属性的定义全部自写。
- **验证**：`python3 scripts/validate_ontology.py` 对本体现有全部 TTL 输出 `conforms: true`；`--matrix` 逐条运行 24 个违规 fixture，24/24 判出预期形状，`valid.ttl` 通过；缺少 `rdflib`/`pyshacl` 时退出码 2 并输出“无法评估”。`check_no_raw_material.py` 对本体文件保持通过（含 `RM-ONTO-HEADER`、`RM-ONTO-LITERAL`、`RM-ONTO-COMMENT`、`RM-PROSEBLOCK`）。
- **取舍说明**：
  1. 不修改 `GRAMMAR.md` 的 `grounding_ref`，不改任何 `check_id` 的绑定，不新增编译方法；形状只约束本体自身的结构。
  2. 本体是派生工件，不是来源；`grounding_ref` 接入建议登记为 T-125。
  3. 工件与工具的自写定义未逐条完成，登记为 T-126；不以原文改写填充。
- **关联 ADR**：ADR-0010（accepted）
- **状态**：生效

---

### 批次 0020 — 2026-11-13 — 引入计划层并给出治理结构改造提案

- **涉及文件**：
  - 新建：`ROADMAP.md`、`spec/GOVERNANCE_RESTRUCTURE.md`
  - 修改：`README.md`、`README.en.md`（文件地图各加一行 `ROADMAP.md`）
- **变更摘要**：按任务台账的实际结构给出判断：`TODO.md` 作为单点台账够用，作为排序与验收依据不足。具体缺陷九条（按批次分组导致同一目标分散、无依赖图与关键路径、无出口条件、无量级、重复与重叠、状态记号不统一、关闭规则自相矛盾、无发布 lane、无外部阻塞状态），另有两条事实缺口（规则组 B 的 `pending_reanchor` 签注已过期；`validation/CHECKLIST.md` 缺 `source_commit`）。据此新增 `ROADMAP.md`：目标 D1–D5、M0–M7 里程碑与可验证出口条件、关键路径与并行关系、全部 64 个未完成条目的唯一归属、按条目数与人工判断量给出的工作量量级、`TODO.md` 保留为台账的处置建议，以及 `v0.4.0` 之后 11 个提交按 minor 定为 `v0.5.0` 的发布安排。
- **治理提案**：`spec/GOVERNANCE_RESTRUCTURE.md` 给出诊断（各文件职责、权威边界、`STATE`/`CHANGELOG`/`TODO`/计划层四者分工与冲突、六条治理结构问题）、目标结构（五层与冲突裁决顺序）、`CONSTITUTION.md`/`AGENTS.md`/`README.md`/`STATE.md`/`TODO.md` 的逐条改法、迁移与防断链措施、代价与风险，以及最小与完整两档方案。推荐最小方案，并把 `manifest.json` 与 tag 的一致性检查并入现有脚本。
- **未提交内容**：`CONSTITUTION.md`、`AGENTS.md`、`STATE.md`、`TODO.md` 的实质改动，以及 ADR-0011，均未落库，待批准后按提案第 4 节的顺序执行。本批次只登记文档层面的新增与导航更新。
- **验证**：`scripts/check_state.py`（89 个跟踪文件，0 错误）、`scripts/check_ledger_landings.py`（0 错误 1 警告，警告为 SPRINGER-PMBOK-2024 待 T-112）、`scripts/check_anchors.py`（46 个 Markdown 文件，0 错误 0 警告）、`scripts/check_no_raw_material.py`（0 错误）。锚点基线未改动，因为规则与来源文本块未变。
- **关联 ADR**：无（治理层改动待 ADR-0011 批准）
- **状态**：生效（仅文档；治理条文改动未生效）

---

### 批次 0021 — 2026-11-13 — 落库最小治理改造：调度层、TODO 重组与发布一致性检查

- **涉及文件**：
  - 新建：`adr/0011-schedule-layer-and-plan.md`
  - 修改：`CONSTITUTION.md`（第 4 条新增调度层一句）、`AGENTS.md`（3.1、3.2、3.3、新增 3.4、第 4 条目录树与维护责任表、第 8 条）、`ROADMAP.md`（移除现状诊断，改为只保留目标、里程碑、依赖与执行内容）、`TODO.md`（按 M0–M7 重组、增加里程碑列、统一状态、补 `blocked-external`）、`STATE.md`（维护规则一句）、`README.md`、`README.en.md`（`TODO.md` 描述与 ADR 范围）、`scripts/check_state.py`（发布一致性核对）、`scripts/README.md`、`spec/GOVERNANCE_RESTRUCTURE.md`（标注为已批准的审查附件）
- **变更摘要**：
  1. 现状诊断（九条 TODO 结构缺陷、两条事实缺口、调度层重叠与治理结构问题）移入 ADR-0011；`ROADMAP.md` 不再记录判断与理由，只保留目标 D1–D5、M0–M7 与出口条件、关键路径、T-xxx 映射、工作量量级、TODO 处置与发布安排。
  2. 按最小方案落库：`CONSTITUTION.md` 第 4 条增加“调度层变更不属实质性修改”一句；第 1 条调度层说明、第 5 条第 2 项扩容、独立检查脚本三项未做。
  3. `AGENTS.md` 修正 3.2 的关闭规则冲突（保留行、标 `done`、附证据），把 TODO 收窄为单点台账；新增 3.4 定义 `ROADMAP.md`；目录树与维护责任表加入 `ROADMAP.md`；第 8 条增加两条禁止项。
  4. `TODO.md` 重组为 M0–M7 八个章节，新增里程碑列，状态统一为 `open` / `in-progress` / `blocked-external` / `done` / `dropped`；外部阻塞项（T-012、T-013、T-052、T-112、T-115、T-119、T-121）标注解锁条件；重复项加交叉引用而不合并编号；共 72 行（65 个未完成、7 个已关闭）。
  5. T-110 落地：`scripts/check_state.py` 增加 `manifest.json` 的 `package_version` / `release_tag` 与最新 annotated tag 的一致性核对，结构无法解析时以 2 退出。T-110 标记 `done`。
  6. 新增 T-127（规则组 B 签注同步）与 T-128（`v0.5.0` 发布），归入 M0。
- **验证**：`scripts/check_state.py`（92 个跟踪文件，0 错误；发布一致性 `0.4.0` ↔ `v0.4.0`）、`scripts/check_ledger_landings.py`（0 错误 1 警告，警告为 SPRINGER-PMBOK-2024 待 T-112）、`scripts/check_anchors.py`（47 个 Markdown 文件，0 错误 0 警告）、`scripts/check_no_raw_material.py`（0 错误）。锚点基线未改动。
- **关联 ADR**：ADR-0011（accepted）
- **状态**：生效

---

### 批次 0022 — 2026-11-13 — M0 收口：已决事项落库、产物基线与 v0.5.0

- **涉及文件**：
  - 修改：`adr/0011-schedule-layer-and-plan.md`（决定 10–12 与跟进事项）、`AGENTS.md`（3.2 状态归属、3.4 计划级动作）、`ROADMAP.md`（第 6 节入口、第 8 节计划级动作）、`spec/methods/deterministic-checker.md`（规则组 B 的状态与 1.2 节）、`spec/COMPILATION_METHODS.md`（`CM-DET-CHECKER` 的 `scope` 行）、`spec/ONTOLOGY_FEASIBILITY.md`（接合表一处过期事实）、`validation/CHECKLIST.md`（B 组状态与 `source_commit`）、`scripts/check_state.py`（tag 指向 `HEAD` 判断）、`scripts/README.md`、`manifest.json`（`0.5.0`）、`TODO.md`（T-111、T-127、T-128 关闭）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. 三条已决事项补入 ADR-0011：ROADMAP 允许不分配 T 编号的计划级动作（需跨里程碑追踪者先登记 T 条目）；`blocked-external` 只定义于 `AGENTS.md` 3.2，不进入 `CONSTITUTION.md` 第 9 条；TODO 重复项暂不合并，只加交叉引用，编号语义不动。
  2. T-127：规则组 B 在 `validation/CHECKLIST.md`、`spec/methods/deterministic-checker.md` 与 `spec/COMPILATION_METHODS.md` 中统一为 `active`，`severity` 保持 `advisory`（ADR-0008）；F、G 组的 `assumption` 保留。
  3. T-111：`validation/CHECKLIST.md` 增加 `source_commit`，值为方法声明最后变更所在提交 `b16e3b8`（ADR-0004）。
  4. T-128：按 minor 规则发布 `v0.5.0`（`v0.4.0` 后无规范条文或契约 schema 的向后不兼容变更）；`manifest.json` 改为 `0.5.0` / `v0.5.0`；annotated tag `v0.5.0` 指向本批次提交，仅本地创建、未 push。
  5. `scripts/check_state.py` 的发布一致性检查增加“最新 annotated tag 必须指向 `HEAD`”判断，修复只比对版本字符串与 tag 名的假通过路径。
- **验证**：四个检查器退出码均为 0；`check_state.py` 发布一致性为 `0.5.0` ↔ `v0.5.0`，tag 指向 `HEAD`。
- **关联 ADR**：ADR-0011、ADR-0008、ADR-0004
- **状态**：生效

---

### 批次 0023 — 2026-11-13 — 发布闸门开发态豁免与提交前四检查器接入

- **涉及文件**：
  - 修改：`manifest.json`（新增 `release_state`）、`scripts/check_state.py`（显式发布态与 tag 校验）、`.githooks/pre-commit`（四检查器）、`AGENTS.md`（新增 3.5、修订 7bis）、`scripts/README.md`、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. `manifest.json` 的 `release_state` 显式声明 `development` 或 `released`；字段缺失按 `released` 严格处理，非法值退出 2；不得根据分支名、提交数或口头说明自动推断。
  2. `development` 仅把“HEAD 领先于 tag”降为警告；`release_tag` / `package_version` 一致性、tag 是否为 annotated、tag 是否为 HEAD 的祖先（分叉即错误）仍严格校验。
  3. `.githooks/pre-commit` 依次运行 `check_no_raw_material.py`、`check_anchors.py`、`check_ledger_landings.py`、`check_state.py`，任一失败即阻断；每个克隆需执行 `git config core.hooksPath .githooks`。
  4. 发布引导提交（切回 `released` 并递增版本）是 `--no-verify` 的唯一例外：tag 只能指向已存在提交；该提交后必须立即打 annotated tag 并复跑四个检查器。
- **验证**：负例提交被 `check_anchors.py` 阻断（退出码 1，未产生提交）；本批次提交由四检查器放行；开发态 `check_state.py` 退出 0 并输出领先警告，移除 `release_state` 后退出 1。
- **关联 ADR**：无（操作约定，规则出处 `AGENTS.md` 3.5；不改变发布点定义与立法文件）
- **状态**：生效

---

### 批次 0024 — 2026-11-13 — 关闭 M0 并发布 v0.5.1

- **涉及文件**：
  - 修改：`TODO.md`（T-116 关闭、M0 状态）、`ROADMAP.md`（M0 关闭与证据、当前基线）、`manifest.json`（`0.5.1` / `v0.5.1` / `released`）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. T-116 关闭：`.githooks/pre-commit` 已依次运行四个检查器，任一失败阻断（批次 0023）。
  2. M0 五个出口条件复核通过，M0 正式关闭；工作项 T-070、T-110、T-111、T-114、T-116、T-127、T-128 均为 `done`。
  3. 发布 `v0.5.1`（patch）：`v0.5.0` 已推送，按发布纪律不回改已发布 tag；本次仅新增发布态豁免、提交前接入与调度收口，未新增规范文件、未改变规范条文或契约 schema。
  4. `release_state` 切回 `released`，annotated tag `v0.5.1` 指向本批次提交；本地创建，待批准后推送。
- **验证**：四个检查器 0 错误；`check_state.py` 输出 `manifest 0.5.1 ↔ v0.5.1（released）`，tag 指向 `HEAD`。
- **关联 ADR**：无（操作约定与调度收口；规则出处 `AGENTS.md` 3.5）
- **状态**：生效

---

### 批次 0025 — 2026-11-14 — 绕过通道留痕与撤除条件

- **涉及文件**：
  - 修改：`scripts/check_state.py`、`AGENTS.md`（3.5.1、3.5.2、7bis 第 5 条）、`ROADMAP.md`（M7 工作项与出口 6、发布表、当前基线）、`TODO.md`（T-129）、`manifest.json`（`release_state=development`）、`scripts/README.md`、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. 实测 git 不记录 `--no-verify`：发布提交对象只有 `tree` / `parent` / `author` / `committer` / `message`，没有旁路标记；因此改用固定 trailer 留痕：`Hook-Bypass: release-bootstrap`、`Hook-Bypass-Reason:`、`Hook-Bypass-Verified:`。
  2. `check_state.py` 对 `v0.5.2` 及以后的发布提交强制三项 trailer，缺失即错误；非发布提交携带即错误；`v0.5.1` 及以前不追溯。
  3. 撤除方向定为两段校验：pre-commit 识别 `Release-Target: <tag>` 显式待发布声明，pre-push 严格校验 tag 存在、annotated、指向 `HEAD`；登记 T-129（M7），硬约束为不晚于 `v0.5.2` 发布、机制生效后最多 1 次豁免。
  4. `manifest.json` 切回 `development`（`v0.5.1` 之后的开发态）。
- **钩子绕过**：本批次不是发布提交，未使用 `--no-verify`。
- **验证**：负例（`v9.9.9` 发布提交无 trailer）退出 1；正例（`v9.9.8` 携带三项 trailer）退出 0；主工作区四个检查器 0 错误，`check_state.py` 输出开发态警告。
- **关联 ADR**：无（操作约定，规则出处 `AGENTS.md` 3.5.1 / 3.5.2）
- **状态**：生效

---

### 批次 0026 — 2026-11-14 — 补 5 个 block 级 check_id 参考样例

- **涉及文件**：
  - 修改：`spec/methods/deterministic-checker.md`（附录 A.1）、`validation/CHECKLIST.md`（`source_commit` 推进）、`TODO.md`（T-011、T-130）
- **变更摘要**：
  1. 为 5 个 `block` 级 `check_id`（`PROJECT_MINIMAL_EXISTENCE`、`CONSTRAINT_ANCHOR_REQUIRED`、`DELIVERABLE_ASSERTION_LINK`、`CHANGE_CONSTRAINT_LINK`、`ROLE_MINIMAL_COMPLETENESS`）各补触发/不触发两组输入/输出样例，共 10 个；输入为 YAML 谓词快照，输出含 `check_id`、`source_rule`、`verdict`、`reason`。
  2. 样例只按附录 A 注册表判定列编写，未新增谓词、未改判定；`ROLE_MINIMAL_COMPLETENESS` 的角色合并子情形按 ERRATA E-004 / T-100 暂不纳入。
  3. 编写中发现 G-A1 的“约束作用于 `Outcome`/`Commitment`”子句未进入判定列，登记 T-130（M1，改判定需 ADR）。
  4. `validation/CHECKLIST.md` 的 `source_commit` 推进到样例提交 `c938c35`（ADR-0004）。
- **钩子绕过**：无。
- **验证**：四个检查器 0 错误（`check_anchors` 0 错误 0 警告；`check_ledger_landings` 1 条既有 `SPRINGER-PMBOK-2024` 警告）。
- **关联 ADR**：无（执行层补丁；T-130 若改判定另走 ADR）
- **状态**：生效

---

### 批次 0027 — 2026-11-14 — 补齐 17 个 check_id 的参考样例

- **涉及文件**：
  - 修改：`spec/methods/deterministic-checker.md`（附录 A.1.6–A.1.17）、`validation/CHECKLIST.md`（`source_commit` 推进）、`TODO.md`（T-011 关闭、T-131）
- **变更摘要**：
  1. 补齐剩余 12 个 `check_id` 的触发/不触发样例：G-B1、G-B2、G-C2、G-D2、G-E2、G-F1–F4、G-G1–G3，每个 2 例，共 24 个。
  2. 连同批次 0026 的 5 个 `block` 级样例，附录 A 现已覆盖 17/17 个 `check_id`，合计 34 个样例；`warn` / `assumption` 级样例显式标注 `severity` 与 `rule_status`。
  3. 样例只按注册表判定列编写，未新增谓词、未改判定；G-A1 约束作用边（T-130）与 G-E2 的 `assumption` 形式/验证条件（T-131）保持原判定，不在样例中固化歧义。
  4. `validation/CHECKLIST.md` 的 `source_commit` 推进到样例提交 `a72caaa`（ADR-0004）；T-011 标 `done`。
- **钩子绕过**：无。
- **验证**：四个检查器 0 错误（`check_anchors` 0 错误 0 警告；`check_ledger_landings` 1 条既有 `SPRINGER-PMBOK-2024` 警告）。
- **关联 ADR**：无（执行层补丁；T-130、T-131 若改判定另走 ADR）
- **状态**：生效

---

### 批次 0028 — 2026-11-14 — 缺口台账、到期裁定与 G 组样例修正

- **涉及文件**：
  - 新增：`GAP_LEDGER.md`、`scripts/check_gap_ledger.py`、`adr/0012-gap-ledger-and-adjudication.md`
  - 修改：`spec/methods/deterministic-checker.md`（A.1.15/A.1.16 修正）、`AGENTS.md`（新增 3.6、目录树、7bis）、`ROADMAP.md`（M1/M3 工作项与出口、D4、发布门槛）、`TODO.md`（T-132；T-100/T-130/T-131 交叉引用）、`scripts/README.md`、`.githooks/pre-commit`、`scripts/check_state.py`、`validation/CHECKLIST.md`（`source_commit` 推进）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **修正 G 组样例名称与内容**：A.1.15 由错误的 `TAILORING_DECISION_JUSTIFICATION` 改为注册表实际的 `TAILORING_RECORD_EXISTENCE`（G-G1）；A.1.16 由 `TAILORING_RATIONALE_ANCHOR` 改为 `TAILORING_NON_TRIMMABLE_SET`（G-G2）。批次 0027 报告的“17/17”在名称层面有误，本批次更正。
  2. **缺口归并**：G-D2、G-A2、G-E1 的未定义判定对象归并为 `G-001`（`undefined-object`，“规则引用了注册表中未定义的判定对象”）；T-130、T-131、T-100 保留独立编号，分别对应 `G-002`、`G-003`、`G-004`，台账注明四者同属“规则正文严于判定列”大类。
  3. **临时治理机制**：`AGENTS.md` 3.6 规定入口三条件与机械判据、L1–L3 分级与停留上限、按里程碑的例行裁定点、四处置出口、到期阻断与撤除条件；ADR-0012 记录决策与不写入 `CONSTITUTION.md` 的理由；T-132（M3）承担撤除评估。
  4. **机械核查**：`check_gap_ledger.py` 输出总数、`open`/`closed`、按级与到期计数、核查矩阵 `consistent` 比例；到期未裁定退出 1；`--staged` 要求规则/判定文件与台账同批更新。它成为第五个提交前检查器，并由 `check_state.py` 调用，使到期未裁定阻断发布。
  5. `validation/CHECKLIST.md` 的 `source_commit` 推进到 `033528f`（ADR-0004）。
- **钩子绕过**：无。
- **验证**：
  - 正面：`check_gap_ledger.py` 输出“4 条（open 4 / closed 0）；L1 1 / L2 2 / L3 1；到期 0；核查矩阵 12/17 consistent”，退出 0；五个检查器均退出 0。
  - 负例 1（到期）：副本台账改为 `M2` 后，输出 `G-004 已到期未裁定（登记 M1，L1 上限 1，到期 M2，当前 M2）`，退出 1。
  - 负例 2（暂存门）：只暂存方法判定列、不暂存台账时，输出“规则/判定变更必须先过缺口复核”，退出 1。
  - 负例 3（发布阻断）：主工作区临时改为 `M2` 后运行 `check_state.py`，输出“缺口台账核查未通过（退出码 1）……G-004 已到期未裁定”，退出 1。
- **关联 ADR**：ADR-0012
- **状态**：生效

---

### 批次 0029 — 2026-11-14 — T-107 最小原型与输入 schema

- **涉及文件**：
  - 新增：`validation/checker-prototype/checker.py`、`spec/CHECKER_INPUT_SCHEMA.md`
  - 修改：`spec/methods/deterministic-checker.md`（A.1 增加 schema 指针）、`AGENTS.md`（目录树）、`TODO.md`（T-107 标 `done`）、`GAP_LEDGER.md`（核查记录）、`validation/CHECKLIST.md`（`source_commit` 推进）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **可运行原型**：纯标准库实现，直接解析附录 A.1 的 34 个 YAML 样例，按 A 表判定列输出 `check_id` / `source_rule` / `severity` / `rule_status` / `verdict` / `reason`，并与样例期望逐项比对。
  2. **输入 schema 固定**：`spec/CHECKER_INPUT_SCHEMA.md` 定义通用约定、共享字段、17 个 `check_id` 的量化域、枚举与后续样例的遵循规则；附录 A 增加指针，后续样例不得自行引入字段。
  3. **覆盖缺口显式化**：原型在输出中逐条声明 5 处“未覆盖规则正文”（G-001 / G-002 / G-003 / G-004 对应条件），不关闭台账条目，也不宣称全保真。
  4. **依赖**：仅 Python 标准库；无第三方依赖，因此没有“缺依赖静默通过”的退化路径。
- **钩子绕过**：无。
- **验证**：
  - `python3 validation/checker-prototype/checker.py`：34/34 样例通过（100.0%），17/17 个 `check_id` 全通过，退出 0；输出含全部未覆盖项。
  - 五个检查器均退出 0；`check_gap_ledger.py` 仍为 4 条 `open`、到期 0、矩阵 12/17 `consistent`。
- **关联 ADR**：无（执行层补丁；T-100 / T-130 / T-131 的裁定仍走 ADR）
- **状态**：生效

---

### 批次 0030 — 2026-11-14 — 独立复核 TODO 与只读验收包

- **涉及文件**：新增 `validation/independent-review-package.md`；修改 `TODO.md`（T-133）、`ROADMAP.md`（M2 工作项与出口 4、映射表）、`AGENTS.md`（目录树）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **登记 T-133（M2）**：明确 T-107 的 34/34 是样例与实现同源的自证，不构成独立证据；关闭条件是“由非同源实现或人工逐条比对规则正文得出独立结论并记录差异”，不得用原型自身运行结果关闭。
  2. **只读验收包**：`validation/independent-review-package.md` 选定 `PROJECT_MINIMAL_EXISTENCE`（G-A1）、`DELIVERABLE_ASSERTION_LINK`（G-C1）、`CHANGE_CONSTRAINT_LINK`（G-D1），给出规则条款位置与陈述、6 个样例的原文位置与输入快照、原型实际判定与 `reason`、已知未覆盖项；**不包含原型源码**。
  3. **里程碑绑定**：ROADMAP M2 出口新增第 4 条，独立复核未完成不得关闭 M2。
- **钩子绕过**：无。
- **验证**：`python3 validation/checker-prototype/checker.py` 仍为 34/34（100.0%）；五个检查器均退出 0。验收包中的 6 个样例与附录 A.1.1 / A.1.3 / A.1.4 逐字一致。
- **关联 ADR**：无
- **状态**：生效

---

### 批次 0031 — 2026-11-14 — 独立复核缺口补登、T-133 部分完成与 `d3e2363` 更正

- **涉及文件**：`GAP_LEDGER.md`（新增 G-005–G-007、核查矩阵、共同成因、核查记录）、`TODO.md`（T-133 状态、新增 T-134–T-136）、`ROADMAP.md`（M2 工作项、出口 4 改写与新增出口 5、映射表）、`ERRATA.md`（E-017）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **补登缺口 G-005**（`rule-stricter`，L1，影响 G-C1，关联 T-134）：G-C1 正文要求断言内容是关于交付物“是什么、处于什么状态、满足什么条件”的明确陈述，判定列只检查 `asserted_by` 边存在；样例 A.1.3-2 的空断言仍期望 `pass`。
  2. **补登缺口 G-006**（`rule-stricter`，L1，影响 G-D1，关联 T-135）：G-D1 正文把变更提议限定为对 `Commitment` 或 `Deliverable` 的提议，判定列对任何变更提议生效，缺少 `target` 对象类型谓词。
  3. **补登缺口 G-007**（`undefined-object`，L1，影响 G-A1/G-A2/G-C1/G-D1，关联 T-136）：复核方所报 5 处“判定列语义未定明”**合并为一条**登记——端点量词、空对象语义、悬空引用的原因码、多违规时 `reason` 优先级、`about` 反向引用是否构成 G-C1 的出边。合并理由：五者同属“判定列语义未定明”，既非单一规则条款与判定列的落差，也没有各自独立的处置路径；逐条登记只会让同源问题重复占用裁定带宽，合并后用说明列逐项列举，裁定与核查仍可逐点覆盖。
  4. **到期口径**：G-005–G-007 均按 L1（停留 1 个里程碑）、登记 M1，到期 M2；`check_gap_ledger.py` 在 M1 下判定到期 0，可在 M2 内裁定，不构成必然到期。
  5. **T-133 改为部分完成**：复核已覆盖 3/17 个 `check_id`（G-A1、G-C1、G-D1 的 6 个样例，6/6 一致），剩余 14 项未复核；状态保持 `in-progress`，不因 6/6 关闭。ROADMAP M2 出口 4 由“3 个 `check_id`”改写为“全部 17 个 `check_id`”，并新增出口 5 要求 G-005–G-007 在 M2 关闭前裁定或显式降级。
  6. **`d3e2363` 矛盾更正**：见 `ERRATA.md` E-017。“文本输出补齐字段”准确；“未改动原型源码”若指该提交则不准确（实测只改 `checker.py`，+2 行），未改原型源码的是 `3defa84`。
- **钩子绕过**：无。
- **验证**：
  - `python3 scripts/check_gap_ledger.py`：7 条（open 7 / closed 0）；L1 4 / L2 2 / L3 1；到期 0；核查矩阵 10/17 `consistent`；退出 0。
  - `python3 validation/checker-prototype/checker.py`：34/34 样例通过（100.0%），17/17 个 `check_id` 全通过。
  - 五个检查器（`check_no_raw_material.py`、`check_anchors.py`、`check_ledger_landings.py`、`check_gap_ledger.py --staged`、`check_state.py`）均退出 0。
- **关联 ADR**：无（缺口登记与状态更新；G-005–G-007 的裁定若改变已有 `check_id` 判定，届时另立 ADR）
- **状态**：生效

---

### 批次 0032 — 2026-11-14 — ADR-0013 草案：单次裁定收口“判定列语义与表达能力补全”

- **涉及文件**：新增 `adr/0013-unified-adjudication-of-check-semantics.md`；修改 `ROADMAP.md`（M2 出口 5）、`GAP_LEDGER.md`（核查记录）、`STATE.md`（例外表）、`AGENTS.md`（目录树）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **起草 ADR-0013（`draft`）**：把 G-001、G-002、G-003、G-005、G-006、G-007 并为**一次裁定**的范围，逐点列出 D0–D9 待决项（子句级覆盖、端点量词、空对象语义、悬空引用原因码、多违规 `reason` 优先级、`about` 反向引用、G-C1 断言内容、G-D1 `target` 类型、G-001 未定义判定对象、G-002/G-003 是否纳入判定列），每点给候选与影响面，不预设结论。
  2. **裁定门**：T-133 全部 17 个 `check_id` 复核完成方可定稿；复核新增条目按“成因相同 + 处置路径相同 + 指向语义/表达补全”三项判据决定是否并入。G-004 明确不并入（`severity-mismatch`，按 T-100 单独裁定）。
  3. **设计层风险单列**：给出四项判断——两表结构天然漂移（缺子句级覆盖声明，现有台账只做事后探测）；输入 schema 表达力不足（量词/空值/关系路径缺失，G-007 是表达缺陷而非文档不清）；检查项粒度过粗与过细并存（切分单位应是“可判定的规则子句”）；整体可收敛，但收敛判据应改为“同源缺口零新增”。
  4. **复核期间冻结清单**：`GRAMMAR.md`、方法声明与附录 A 判定列/样例、`CHECKER_INPUT_SCHEMA.md`、原型 `checker.py`、只读验收包、`validation/test-cases/` 既有用例；本轮只改台账、调度文档、ADR 与 `STATE.md`。
  5. **状态登记**：`STATE.md` 增例外行，把该 ADR 记为 `skeleton`（文件内状态 `draft`），避免 `adr/` 目录默认值 `accepted` 误标为已接受。
- **钩子绕过**：无。
- **验证**：五个检查器均退出 0；`check_gap_ledger.py` 仍为 7 条 `open`、L1 4 / L2 2 / L3 1、到期 0、矩阵 10/17 `consistent`；原型仍 34/34（本轮未触碰冻结文件）。
- **关联 ADR**：ADR-0013（本批次创建，状态 `draft`）
- **状态**：生效（ADR 草案登记；裁定未生效，判定列与样例未改）

---

### 批次 0033 — 2026-11-14 — ADR-0013 最终裁定：判定层表示规范收口、三表机械对照与术语治理

- **涉及文件**：`adr/0013-unified-adjudication-of-check-semantics.md`（`draft` → `accepted`）、`spec/CHECKER_INPUT_SCHEMA.md`（整篇重写）、`spec/methods/deterministic-checker.md`（A 表子句列、A.2 子句表、§4.2/§4.4、样例）、`validation/checker-prototype/checker.py`、新增 `scripts/check_three_table.py`、新增 `scripts/check_glossary_usage.py`、新增 `knowledge/glossary-usage.json`、`GLOSSARY.md`（新增第 4 节生成块）、`GAP_LEDGER.md`、`TODO.md`、`ROADMAP.md`、`AGENTS.md`、`STATE.md`、`.githooks/pre-commit`、`scripts/README.md`、`scripts/check_state.py`、`scripts/check_gap_ledger.py`、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **ADR-0013 一次性裁定**：范围从“补判定列语义”扩为“判定层表示规范”，D0–D9 与独立复核报出的八条上层设计问题（P1–P8）在同一次裁定中出结论，不分批改冻结文件、不重复跑复核。
  2. **八条问题的处置**：P1 子句被压缩 → A 表新增“子句”列 + A.2 子句表（39 条）；P2 未封闭枚举与自然语言值 → schema 第 4 节具名枚举；P3 跨对象全称/相关性 → schema §1.6–1.7 与 §3bis 关系路径；P4 引用完整性全局统一 → schema §1.5（悬空 `fail` / 类型未定义 `cannot_evaluate`）；P5 assumption 时效与批准资格 → schema §1.9 `assumption` 对象；P6 链/路径/可达性 → schema §1.10；P7 适用性状态机与 `not_applicable` → 方法 §4.4 + schema 第 4 节；P8 三表无机械对照 → `scripts/check_three_table.py`。
  3. **三表机械对照作为交付物**：检查器覆盖“正文 ↔ 判定列”“判定列 ↔ schema”“正文 ↔ schema”三对关系，并核对子句闭合与枚举封闭；pre-commit 与 `check_state.py` 双重调用，退出 1 即阻断提交与发布。不接受“后续人工对照”。
  4. **判定列与 schema 同步**：A.2 子句表给出子句级 severity（`G-E1#3` 为 `warn`，关闭 G-004）；样例 A.1.1 / A.1.3–A.1.5 / A.1.10 按新表示补齐 `about`、`statement_kind`、`target`、`kind`、`verification_condition`；原型实现相应子句并在 `COVERAGE_GAPS` 为空时输出“无（ADR-0013 已消解全部 5 项）”。
  5. **缺口关闭**：G-001–G-007 全部以 `check-change` 关闭；八条设计问题合并登记为 G-008（`undefined-object`，L2，M1）并关闭。核查矩阵 17/17 `consistent`，到期 0。`check_gap_ledger.py` 的锚定规则修正为“只有 `open` 缺口必须被矩阵引用”——`closed` 缺口已记录处置出口，继续强制锚定会让矩阵永远无法达到撤除条件。
  6. **M2 重定位为“表示层收口”**：17 项复核结论作为输入；出口改为三表对照通过、子句覆盖 100%、表示规范有载体、原型重跑通过、同源缺口零新增；“补齐 17 项”与“独立复核完成”从出口移除，T-133 的非同源重跑保留为验证输入而非关闭门。
  7. **术语纳入治理**：`AGENTS.md` 新增 5bis.1，要求每次提交前扫描本次改动并判断术语新增/修改/废弃（新概念必须登记、改义必须同步、废弃标注而不删）。`check_glossary_usage.py` 以“生成 + 冻结基线 + 变更时校验”实现：扫描 `git ls-files` 的 Markdown / JSONL，匹配行内代码、`GLOSSARY.md#term_id` 与裸 `term_id`（裸术语正文不匹配），生成 `knowledge/glossary-usage.json` 与 `GLOSSARY.md` 第 4 节位置表；陈旧位置、行号越界、生成块手改、术语集合漂移均退出 1。与缺口台账分工明确：台账管“正文 ↔ 判定列”的语义裁定，本检查器管“术语条目 ↔ 仓库引用”的引用完整性。
  8. **发布阻断接入**：pre-commit 由五个检查器扩为七个，`check_state.py` 调用三表对照与术语使用位置核查。
- **钩子绕过**：无。
- **验证**：
  - `python3 validation/checker-prototype/checker.py`：34/34 样例通过（100.0%），17/17 个 `check_id` 全通过，`COVERAGE_GAPS` 为空。
  - `python3 scripts/check_three_table.py`：正文 17 条规则、判定列 17 个 `check_id` / 39 个子句、schema 17 个输入域；退出 0。
  - `python3 scripts/check_gap_ledger.py`：8 条（open 0 / closed 8）；L1 4 / L2 3 / L3 1；到期 0；矩阵 17/17 `consistent`；退出 0。
  - `python3 scripts/check_glossary_usage.py`：82 条术语、800 余个使用位置、39 个零使用警告；退出 0。负例（基线行号改为越界值、手改生成块、删除位置）均退出 1，恢复后退出 0。
  - 七个检查器均退出 0（`check_state.py` 在开发态只对“HEAD 领先 tag”告警）。
  - **复核状态**：本批次只做同源重验（原型 + 三表检查器）；独立复核会话对改动后判定列/schema 的单次非同源重跑仍待执行，结论另记，不冒充已完成。
- **关联 ADR**：ADR-0013（`accepted`）
- **状态**：生效

---

### 批次 0034 — 2026-11-14 — 复核推翻后的账务修正、原型/schema/判定列修订与样例追溯性降级

- **涉及文件**：`GAP_LEDGER.md`、`AGENTS.md`、`adr/0013-unified-adjudication-of-check-semantics.md`、`STATE.md`、`spec/CHECKER_INPUT_SCHEMA.md`、`spec/methods/deterministic-checker.md`、`validation/checker-prototype/checker.py`、`scripts/check_gap_ledger.py`、`scripts/check_three_table.py`、`scripts/README.md`、`ROADMAP.md`、`TODO.md`、`knowledge/glossary-usage.json`、`GLOSSARY.md`（生成块）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **账务回滚**：G-001–G-008 全部由 `closed` 回到 `open`，核查矩阵由 17/17 `consistent` 降为 0/17，逐行改指缺口编号；新增 G-009–G-017 九条（null 崩溃、引用完整性未全局、`assumption.pending` 缺批准者、路径缺 `target_id` 与扁平双轨、`subject_group` 17 项未物化、聚合优先级矛盾、A 表叙述性短语、A.2 缺原因码列、三表检查器只查结构）。当前 open 17 / closed 0，L1 9 / L2 7 / L3 1，到期 0。
  2. **关闭判据**：`GAP_LEDGER.md` 新增“关闭判据（硬要求）”，`AGENTS.md` 新增 3.6.6。缺口不得以同源结果（自家原型通过、自家脚本退出 0、同批改样例后自证）关闭；`closed` 必须写“关闭依据”列，且只能取 `非同源复核：<复核者>，<日期>` 或 `人工签收：<签收人>，<日期>`。`check_gap_ledger.py` 校验依据缺失、前缀非法、说明/依据含同源自证措辞；`open` 填依据同样报错。
  3. **原型**：17 个 check 函数的必需键守卫统一为 `require_fields()`，键缺失或值为 `null` 均返回 `cannot_evaluate/missing_input`；新增 `validate_references()`，在 check 返回 `pass` 时统一校验全局引用（含 `commitments.by/to`、`constraints.constrains`、`changes.target`、`charters.*`、`contracts.constrained_by/accountable_signature`、`tailoring_records.approver`、`assertions.about/deliverable/subject/accountable_confirmation`）；该调用在 pass 分支之后，只能把本应 pass 的结果改为 fail/cannot_evaluate，不推翻既有 fail。`assumption.pending` 分支补 `approved_by` 检查。`delegated_from` 改为路径对象，扁平字符串返回 `invalid_path`。
  4. **schema**：§1.10 路径补 `steps[].target_id` 并删除扁平字符串写法；`subject_group` 17 项（ISO 21502:2020 7.2–7.18）完整物化；§1.14 与 A.2 统一为 `fail > cannot_evaluate > pass`；§3 补 `assumption_unclosed` / `invalid_path` 等原因码。
  5. **判定列格式**：A 表改为 `check_id | 规则 | 判定（子句 id） | 输入 | 原因码 | 规则状态`，判定列只留子句 id，叙述下沉 A.2；A.2 增加原因码列（40 条子句），新增 `G-D2#3`（pending 须 `approved_by`）；A 表原因码集合与子句原因码集合机械一致；G-B1 不再写枚举条件。
  6. **样例追溯性修正**：A.1.11-2、A.1.12-2、A.1.13-2、A.1.15-2 四个样例自 T-107 起一直带悬空引用（章程指向未提供的 Outcome/Constraint/Actor/Assertion；验收确认与契约签署指向未提供的 Actor；契约约束指向未提供的 Constraint；裁剪批准者指向未提供的 Actor）。**只改输入块，4 个样例的期望输出均未变**；依据 schema §1.5（所有引用必须解析到同一快照）。此前的多次“34/34 通过”包含这 4 条未被发现的无效验证，是对既有绿色数字的追溯性降级，不是新缺陷；已记入台账核查记录。`validate_references()` 只在 pass 分支调用、不能推翻既有 fail 是刻意取舍：已有 fail 的样例保留其特定原因码，避免全局校验淹没规则语义。
  7. **三表检查器深度**：新增判定列叙述性短语检测、G-B1/G-B2 条件归属、原因码定义与 A 表/子句映射一致性检查。文档明确其边界：只保证结构与已列举的语义短语规则，不保证规则正文与子句表的全文语义等价；绿字不等于语义闭合。
  8. **ADR 与计划**：ADR-0013 由 `accepted` 回到 `proposed`（修订中），新增第 8 节记录首轮裁定失效原因与修订范围；`STATE.md` 加回 `skeleton` 例外。M2 出口改为“结构/枚举/子句/原因码机械一致 + 原型重跑 + 非同源复核关闭缺口”，同源结果明确不构成出口。T-100、T-130、T-131、T-134–T-136 由 `done` 回到 `in-progress`，T-133 描述更新。
- **钩子绕过**：无。
- **验证**：
  - `python3 validation/checker-prototype/checker.py`：34/34 样例通过，17/17 `check_id` 通过。
  - `python3 validation/checker-prototype/checker.py --null-sweep`：31/31 键级用例返回 `cannot_evaluate`，崩溃 0（覆盖 17 个 check 函数）。
  - 全局引用负例：G-F1 章程 `outcomes` 指向 `O-999` → `fail/dangling_reference`；改回 `O-1` → `pass`。路径负例：合法路径对象 → `pass`；扁平字符串 → `cannot_evaluate/invalid_path`；`target_id` 悬空 → `fail/dangling_reference`。`assumption.pending` 无批准者 → `cannot_evaluate/assumption_unclosed`，补 `approved_by` → `pass`。
  - `python3 scripts/check_three_table.py`：正文 17 条规则、判定列 17 个 `check_id` / 40 个子句、schema 17 个输入域；退出 0。负例：G-B1 子句写“值在枚举内”、A 表判定列写叙述性短语、原因码改为未定义值，三种均退出 1。
  - `python3 scripts/check_gap_ledger.py`：17 条（open 17 / closed 0），到期 0，矩阵 0/17；退出 0。负例：G-009 以“非同源复核：复核会话R，2026-11-14”关闭 → 退出 0；以“自家原型通过，退出 0”关闭 → 退出 1；`closed` 但关闭依据为空 → 退出 1。
  - 七个检查器均退出 0（`check_state.py` 在开发态只对“HEAD 领先 tag”告警）。
  - **复核状态**：本批次未执行非同源复核；G-001–G-017 全部保持 `open`，不以本轮同源结果关闭。待复核会话对修订后版本单次重跑，结论记入 `GAP_LEDGER.md` 后再行关闭。
- **关联 ADR**：ADR-0013（`proposed`，修订中）
- **状态**：生效（修订中；缺口未关闭）

---

### 批次 0035 — 2026-11-14 — 四层修订（第一、二层）：入口 null 归一化与引用字段由 schema 生成

- **涉及文件**：`validation/checker-prototype/checker.py`、`spec/CHECKER_INPUT_SCHEMA.md`、`spec/methods/deterministic-checker.md`（A.1.9/A.1.11–A.1.17 输入块）、`scripts/check_three_table.py`、`adr/0013-unified-adjudication-of-check-semantics.md`（§8.4）、`GAP_LEDGER.md`（核查记录）、`knowledge/glossary-usage.json`、`GLOSSARY.md`（生成块）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **第一层：入口统一 null 归一化**。新增 `find_null()`，在 `evaluate()`（`run_case` 的唯一入口）中一次覆盖**顶层键、嵌套对象键、数组元素**三种 `null`；命中即返回 `cannot_evaluate` / `missing_input`，17 个 `check` 函数不再各自兜底。D1 的 `commitments: null` 不再落入 `fail/invalid_change_target`。样例中 4 处语义性 `null`（A.1.9-1 `assumption/verification_condition`、A.1.13-1 `contract`、A.1.15-1 `record`、A.1.17-1 `reassessment_condition`）改为“缺键”或 `{}`，期望输出未变。
  2. **第一层负例**：`--null-sweep` 重写为路径级扫描。顶层必需键 43/43、数组元素 89/89（覆盖 54 条 `(check_id, 路径)` / 27 条唯一路径）、嵌套对象键 6/6，合计 138/138 返回 `cannot_evaluate`，崩溃 0。单点负例：D1 `commitments: null`、D1 `deliverables: [null]`、C1 `assertions: [{...}, null]`、D1 `target: null` 均返回 `cannot_evaluate/missing_input`。
  3. **第二层：引用字段清单由 schema 生成**。schema 新增 §2bis：2bis.1 用 34 行标注引用字段（源路径 / 字段 / 目标集合 / 形态，含 `type` 判别与 `any`），2bis.2 显式登记 40 个非引用字段。原型启动时解析 §2bis.1 生成 `REFERENCE_RULES`，删除手写 `checks` 列表；解析 §3 生成 `REQUIRED_KEYS`。补齐 `contracts[].accountable_signature` 与 `changes[].assumption.approved_by`（并新增 `assertions[].assumption.approved_by`）。
  4. **第二层负例**：F3 的 `accountable_signature: "A-404"` → `fail/dangling_reference`，改回 `A-1` → `pass`；D2 的 `assumption.approved_by: "A-404"` → `fail/dangling_reference`。临时在 §2 `contracts[]` 行加入 `counterparty_id` 且不在 §2bis 标注时，`check_three_table.py` 输出“字段 `counterparty_id` 在第 2 节声明，但 §2bis 既未标注为引用也未登记为非引用”并退出 1；移除后退出 0。
  5. **§3 输入域同步**：`ASSERTION_MUTUAL_EXCLUSION` +`deliverables`，`ALL_IMPROVEMENT_ASSUMPTION` +`actors`，`PROJECT_CHARTER_EXISTENCE` +`outcomes/constraints/actors/assertions`，`CLOSURE_ACCEPTANCE_LINK` +`actors`，`PROCUREMENT_CONTRACT_ANCHOR` +`constraints/actors`，`TAILORING_RECORD_EXISTENCE` +`actors`。新增 `--input-domain`：样例中实际出现的引用目标集合必须已在 §3 声明，实测 0 处缺口；样例顶层键无 §3 之外的额外集合。
  6. **检查器**：`check_three_table.py` 新增第 6 项（§2 字段必须被 §2bis.1 或 §2bis.2 覆盖）与第 7 项（输入域闭包）。
- **钩子绕过**：无。
- **验证**：
  - `python3 validation/checker-prototype/checker.py`：34/34 样例通过，17/17 `check_id` 通过。
  - `python3 validation/checker-prototype/checker.py --null-sweep`：138/138，崩溃 0（顶层 43、数组元素 89、嵌套对象 6）。
  - `python3 validation/checker-prototype/checker.py --input-domain`：0 处缺口。
  - `python3 scripts/check_three_table.py`：正文 17 条规则、判定列 17 个 `check_id` / 40 个子句、schema 17 个输入域、引用字段 27 个 / 非引用字段 40 个；退出 0。负例（`counterparty_id` 未标注）退出 1。
  - 七个检查器均退出 0（`check_state.py` 在开发态只对“HEAD 领先 tag”告警）。
  - **复核状态**：G-001–G-017 仍为 `open`（17/17），本轮同源结果不构成关闭依据；第三、四层待执行，全部完成后只重跑一次非同源复核。
- **关联 ADR**：ADR-0013（`proposed`，§8.4）
- **状态**：生效（修订中；缺口未关闭）

---

### 批次 0036 — 2026-11-14 — 四层修订（第三层）：A 表由 A.2 派生与固定变异集

- **涉及文件**：`spec/methods/deterministic-checker.md`（A 表 7 列、A.2 第 8 列、A.1 样例基线）、`scripts/check_three_table.py`（派生与逐格比较、`--write`、`--method`）、`scripts/test_check_table_mutations.py`（新增）、`adr/0013-unified-adjudication-of-check-semantics.md`（§8.4）、`GAP_LEDGER.md`（核查记录）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **A 表唯一生成路径**：A 表不再手工维护，`scripts/check_three_table.py --write` 由 A.2 重建；A 表列固定为 `check_id | 规则 | 判定（子句 id） | 子句指纹 | 输入 | 原因码 | 规则状态`。默认模式逐格比较“文件 A 表”与“A.2 生成结果”，不再做两表字段互比。
  2. **子句指纹**：`sha256(clause id | 规则 | 子句文本 | 原因码 | 承接 check_id | severity | 规则状态)[:12]`，再按 `check_id` 聚合。任一项语义改动都会改变指纹并使检查失败；`canonical()` 只忽略空白差异。
  3. **A.2 第 8 列**：40 条子句补 `规则状态`（F/G 组为 `assumption`，其余 `active`），与方法 §4.5、A 表规则状态列同源。
  4. **样例基线**：A.1 区新增“样例基线（跨轮横比锚点）”，锚定提交 `1a42b8b`（批次 0034）、34 个样例，并逐条登记 A.1.9-1、A.1.9-2、A.1.11-1、A.1.12-1、A.1.13-1、A.1.15-1、A.1.17-1 的输入块改动与原因；**期望输出零改动**。此后“34/34”一律相对该基线比较。
  5. **固定变异集**：新增 `scripts/test_check_table_mutations.py`，变异副本写入临时目录，不改工作区；基线必须退出 0，逐条变异必须退出 1 且命中预期证据，否则脚本退出 1。变异集固定为 11 条，可重复执行。
- **变异测试全表**：

| 编号 | 类别 | 变异内容 | 抓到 | 退出码 | 证据 |
|---|---|---|---|---|---|
| M01 | 子句语义 | G-C1#1 改成“必须有 Actor 负责人” | 是 | 1 | `DELIVERABLE_ASSERTION_LINK` 子句指纹不一致（`32a91e4431f9` → `6f4b58fcac7a`） |
| M02 | 量词 | G-A1#1 的“至少一个”改为“恰好一个” | 是 | 1 | `PROJECT_MINIMAL_EXISTENCE` 子句指纹不一致（`6a4f8c0ad633` → `ad8e6f971ba0`） |
| M03 | 原因码删除 | G-E1#1 删除 `multiple_accountable` | 是 | 1 | `ROLE_MINIMAL_COMPLETENESS` 子句指纹不一致（`a707061b238f` → `9a2223634395`） |
| M04 | 枚举归属 | 把枚举条件写进 G-B1#2 | 是 | 1 | 子句 `G-B1#2` 写了枚举条件；枚举归属 G-B2 |
| M05 | 枚举归属 | 从 G-B2#1 删除枚举条件 | 是 | 1 | `G-B2#1` 未写枚举条件；值闭合必须由 B2 承接 |
| M06 | 承接规则 | G-C1#1 的承接 `check_id` 改指向 `CHANGE_CONSTRAINT_LINK` | 是 | 1 | `CHANGE_CONSTRAINT_LINK` 规则列不一致（文件 `G-D1`，生成 `G-C1、G-D1`） |
| M07 | 子句 id | G-C1#1 改为 G-D1#4（指向别的规则） | 是 | 1 | `DELIVERABLE_ASSERTION_LINK` 子句 id 列不一致（`G-C1#1` → `G-D1#4`） |
| M08 | severity | G-E1#3 的 severity 由 `warn` 改为 `block` | 是 | 1 | `ROLE_MINIMAL_COMPLETENESS` 子句指纹不一致（`a707061b238f` → `652398553027`） |
| M09 | 规则状态 | G-B1#2 的规则状态由 `active` 改为 `assumption` | 是 | 1 | `DUAL_DIMENSION_ANNOTATION` 子句指纹不一致（`2cde52fd3961` → `6650cf0c3301`） |
| M10 | 子句删除 | 删除 G-E1#3 整行 | 是 | 1 | `ROLE_MINIMAL_COMPLETENESS` 子句 id 列不一致（文件含 `G-E1#3`，生成不含） |
| M11 | 原因码篡改 | G-D1#3 改为未定义的 `invalid_relation` | 是 | 1 | `CHANGE_CONSTRAINT_LINK` 子句指纹不一致（`3e473f8ea1e8` → `9dfa4c069d15`） |

- **边界说明**：变异集只改 A.2、不改 A 表，检测机制是“A.2 派生结果 ≠ 提交的 A 表”。若改动 A.2 后执行 `--write` 重建 A 表，检查器无法区分“合法规格修订”与“绕过”，这只能由提交差异与评审承担；该结构性边界已在脚本与本节写明，不属于检查器可检测范围。
- **钩子绕过**：无。
- **验证**：
  - `python3 scripts/check_three_table.py`：17 条规则 / 17 个 `check_id` / 40 个子句 / 17 个输入域；退出 0。
  - `python3 scripts/test_check_table_mutations.py`：11 条变异，抓到 11 条，未抓到 0 条；退出 0。
  - `python3 validation/checker-prototype/checker.py`：34/34，17/17 `check_id`；退出 0。
  - `--null-sweep`：138/138，崩溃 0；`--input-domain`：0 缺口。
  - **复核状态**：G-001–G-017 仍为 `open`（17/17），本轮同源结果不构成关闭依据；第四层完成后只重跑一次非同源复核。
- **关联 ADR**：ADR-0013（`proposed`，§8.4）
- **状态**：生效（修订中；缺口未关闭）

---

### 批次 0037 — 2026-11-14 — 四层修订（第四层）：扩展关系、悬空原因、violations 撤除、G-A2#2 可达

- **涉及文件**：`spec/CHECKER_INPUT_SCHEMA.md`（§1.5、§1.14、§2、§2bis.2、§3、§4）、`spec/methods/deterministic-checker.md`（A.2 的 `G-B2#2`、`G-C1#1`、`G-E2#3`、原因码映射、悬空引用原因归属表、G-A2#2 可达性）、`validation/checker-prototype/checker.py`（`EXTENSION_RELATIONS`、`check_dimension_value`）、`adr/0013-unified-adjudication-of-check-semantics.md`（§8.4）、`GAP_LEDGER.md`（核查记录）、`CHANGELOG.md`（本批次）
- **变更摘要**：
  1. **`subject_group_extension` 扩展关系**：schema §2 定义 `value` / `relation` / `base` 三字段，§4 新增 `subject_group_extension_relation = {specializes, cross_cuts}`；`base` 必须是 17 项基础 `subject_group` 之一，`value` 不得与基础枚举重名。A.2 新增 `G-B2#2`（`invalid_subject_group_extension`），`G-B2#1` 只承接“标签值在基础枚举或**合法**扩展内”。原型按行序判定：先值闭合、后扩展声明。只写 `{value}` 不再通过。
  2. **悬空引用原因统一为“规则子句原因优先”**：A.2 的“悬空引用原因归属”表固定每个 `check_id` 在悬空时返回的原因码；只有子句原因码列显式列出 `dangling_reference` 才返回该码（`G-C1#1`、`G-E2#1`、`G-E2#3`）。其余子句返回自己的原因码；无子句承接的引用由 `validate_references()` 在全部子句 `pass` 后兜底。schema §1.5 同步该定性。
  3. **`violations[]` 选择撤除**：schema §1.14 明确“原型不输出 `violations[]`；`reason` 为按 A.2 行序首条命中原因码”；实现不新增该字段，`run_case` 输出键实测为 `check_id / source_rule / severity / rule_status / verdict / reason`。
  4. **`G-A2#2` 在声明输入域内可达**：schema §2 的 `commitments[]` / `deliverables[]` 增加可选 `node_type`，§3 的 `CONSTRAINT_ANCHOR_REQUIRED` 判定所需字段注明“提供时须 ∈ `management_node_type`”。未提供视为未断言类型，不触发本子句；提供非法值 → `cannot_evaluate` / `undefined_object_type`。
- **负例实测**：
  - `subject_group_extension: [{value: "custom"}]` 且标签引用 `custom` → `fail` / `dimension_value_out_of_enum`；只写 `{value: "custom"}` 但未被引用 → `fail` / `invalid_subject_group_extension`；`value` 与基础枚举重名 → `fail` / `invalid_subject_group_extension`；合法 `{value: "custom", relation: "specializes", base: "planning"}` → `pass`。
  - 悬空引用：`A2` → `unanchored_management_item`；`C1` → `dangling_reference`；`D1` → `invalid_change_target`；`E1` → `unknown_accountable`；`E2#1` / `E2#3` → `dangling_reference`。与 A.2 归属表逐行一致。
  - `run_case` 输出不含 `violations[]`。
  - `G-A2#2`：`node_type: "Unknown"` → `cannot_evaluate` / `undefined_object_type`；`node_type: "ManagementActivity"` + 完整 A.1.2-2 输入 → `pass`。
- **验证**：
  - `python3 validation/checker-prototype/checker.py`：34/34，17/17 `check_id`；退出 0。
  - `--null-sweep`：138/138，崩溃 0；`--input-domain`：0 缺口。
  - `python3 scripts/check_three_table.py`：17 条规则 / 17 个 `check_id` / 41 个子句 / 17 个输入域；退出 0。
  - `python3 scripts/test_check_table_mutations.py`：11/11 抓到；退出 0。
  - 七个检查器全部退出 0（`check_no_raw_material` 曾因 A.1 基线引用块 803 字符超 800 阈值失败，已把基线移出引用块后复跑通过；`check_glossary_usage --write` 已重建基线）。
  - **复核状态**：G-001–G-017 仍为 `open`（17/17）。四层修订完成，只重跑一次非同源复核；在同源结果下不关闭任何缺口。
- **关联 ADR**：ADR-0013（`proposed`，§8.4）
- **状态**：生效（修订中；缺口未关闭）

---

### 批次 0038 — 2026-11-14 — 补漏：A.2 改动的非同源签收纪律

- **性质**：这是对批次 0036“A 表由 A.2 派生”的**补漏**，不是新决定。派生检查只能保证“A 表与 A.2 一致”；改 A.2 再跑 `--write` 会使两者自洽，无法区分合法规格修订与绕过。签收纪律补上这一缺口。
- **涉及文件**：`AGENTS.md`（新增 3.6.7）、`adr/0013-unified-adjudication-of-check-semantics.md`（决策表新增 `A2-SIGNOFF`，P1 子句数 40→41，P8 检查深度补签收同步）、`spec/methods/deterministic-checker.md`（A.2 区头新增复核签收行）、`scripts/check_three_table.py`（规则 8）、`scripts/test_check_table_mutations.py`（S01/S02）、`CHANGELOG.md`（本批次）
- **签收格式**：`复核签收：<复核者/会话> / <YYYY-MM-DD> / A.2 指纹 `<12位>``。指纹 = 全部子句指纹按 clause id 排序后的 sha256 前 12 位。
- **机械阻断**：`scripts/check_three_table.py` 规则 8 比对签收行指纹与当前 A.2 指纹；不一致即退出 1。`--write` 只重建 A 表，**不更新签收行**，因此“改 A.2 + --write”仍会被拦。
- **正负例（`scripts/test_check_table_mutations.py`）**：

| 编号 | 场景 | 预期 | 实际 | 退出码 | 证据 |
|---|---|---|---|---|---|
| S01 | 只改 A.2 + `--write`，不更新签收 | 阻断 | 阻断 | 1 | `A.2 已改动但复核签收未同步：签收行 … a7e02bdfd23f，当前 A.2 指纹 08979d4851b5` |
| S02 | 改 A.2 并更新签收与指纹 | 通过 | 通过 | 0 | `[通过] 正文、判定列、schema 三表一致…A.2 签收与指纹同步…` |

- **基线例外**：本次提交的签收行标注“纪律基线（同源修订；非同源复核待提交后执行）”，仅此一次；此后 A.2 改动必须由非同源复核更新签收行。
- **边界**：检查器只验证签收记录与 A.2 同步，不能验证签收人是否真的非同源；后者由提交评审与 AGENTS 3.6.6 共同约束。
- **验证**：变异集 11/11 抓到；签收正负例 2/2 符合预期；34/34、null-sweep 138/138、input-domain 0 缺口；七个检查器退出 0。
- **复核状态**：G-001–G-017 仍为 `open`（17/17），等非同源复核结论。
- **关联 ADR**：ADR-0013（`proposed`，§2.2、§8.4）
- **状态**：生效（纪律补漏；缺口未关闭）
