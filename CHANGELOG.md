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
