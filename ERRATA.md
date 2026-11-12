## 幻觉更正台账

**权威关系**：本文件是执行层的自我审查台账。它不修改任何规范，只记录“本技能编制过程中发现并修正的错误”“外部评审指出的问题及处置”“待核验的存疑表述”。与 `SOURCE_LEDGER.md` 的关系：来源的核验状态变更走 ADR；本文件记录的是**技能自身表述**的更正，不改变来源登记。

### 1. 登记规则

- **登记范围**：(i) 本技能编制过程中发现并修正的错误（编造引用、版本臆断、字段虚构、语义张冠李戴）；(ii) 外部评审指出的问题及处置；(iii) 待核验的存疑表述。
- **不登记**：错别字、排版、措辞微调（走 CHANGELOG）。
- **格式**：按编号追加，禁止改写已登记条目；更正时追加新条目并引用原条目编号。
- **与 CHANGELOG 的分工**：CHANGELOG 记录“什么文件在什么时候被改成了什么”；ERRATA 记录“我们曾经犯过什么错、如何发现、如何修正”。一条更正通常同时产生一个 ERRATA 条目和一个 CHANGELOG 批次。

### 2. 已登记条目

#### E-002 — Szwed 的 PMBOK OWL 本体“reasoner 验证”表述张冠李戴

- **原表述**：早期讨论中将“reasoner 自动验证一致性”的表述归于 Szwed 的 PMBOK OWL 本体（340 类）。
- **问题**：该表述实际出自 Silega 等 2024 年论文（Springer, CIIP 2023），与 Szwed 的工作是两回事；“340 类”无可核验出处。
- **发现方式**：外部评审指出。
- **修正**：`SOURCE_LEDGER.md` 的候选来源清单中排除 Szwed 条；Silega 等 2024 的工作后续按 ADR-0005 以 `SPRINGER-PMBOK-2024` 登记（正文未获取）。
- **波及文件**：`SOURCE_LEDGER.md`。
- **状态**：`closed`（2026-11-11）

#### E-003 — PMBOK 版本漂移未在登记表中显式声明

- **原表述**：`SOURCE_LEDGER.md` 的 PMBOK 条目在初版中未记录“PMBOK 已出至第 8 版（2025-11）”这一事实。
- **问题**：版本漂移未显式声明，可能使读者误以为第 7 版是当前版本。
- **发现方式**：外部评审指出。
- **修正**：初版条目备注中补记版本漂移；后续按 ADR-0005 删除第 7 版条目，第 8 版以 `PMBOK8-2025` 入表（本地 PDF 与 EPUB 均已获取）。
- **波及文件**：`SOURCE_LEDGER.md`、`GLOSSARY.md`。
- **状态**：`closed`（2026-11-11）

#### E-004 — `ROLE_MINIMAL_COMPLETENESS` 的 warn/block 混合逻辑未明确

- **原表述**：`spec/methods/deterministic-checker.md` 附录 A 中，`ROLE_MINIMAL_COMPLETENESS` 的判定为“每个决策类 Commitment 有唯一 accountable_by 指向 HumanActor/LegalEntity，且至少一个 responsible_by；重合时有 role_merge_declaration”，severity 为 `block`。
- **问题**：当 Accountable 与 Responsible 重合但缺少 `role_merge_declaration` 时，应整体判 `fail`（block）还是判 `warn`？原判定未区分两种情形：问责结构根本性缺失（如 Accountable 为 AIActor）应 block；角色合并声明缺失应 warn。原判定将二者混为一谈。
- **发现方式**：QUICKSTART 最小走查样例（第 2.3 节 C-002 的检查）暴露。
- **修正**：登记为待修正项（见 `TODO.md` T-100）；在修正前，QUICKSTART 中的输出按“role_merge_declaration 缺失触发 warn”处理，并在 `spec/methods/deterministic-checker.md` 附录 A 的判定摘要中加注。
- **波及文件**：`spec/methods/deterministic-checker.md`、`QUICKSTART.md`。
- **状态**：`open`（待修正）

#### E-005 — `GLOSSARY.md` 与 `anchored-entries.jsonl` 的同步无机制保障

- **原表述**：`CONSTITUTION.md` 第 11.5 条规定“冲突时以 JSONL 为准”，但未规定如何发现冲突。
- **问题**：同步靠人工，术语一多就会漂移。
- **发现方式**：本轮自我审查。
- **修正**：新增 `scripts/check_glossary_sync.md`（同步检查规格）与 `spec/GROUNDING_CRITERIA.md` G4（接地判据要求同步检查通过）。
- **波及文件**：`scripts/check_glossary_sync.md`、`spec/GROUNDING_CRITERIA.md`、`CONSTITUTION.md` 第 11.5 条（补充“同步检查的执行方式见 `scripts/check_glossary_sync.md`”）。
- **状态**：`closed`（2026-11-11）

#### E-006 — 反幻觉技能缺少自我审查台账

- **原表述**：本技能包在 v0.3 之前无 `ERRATA.md`。
- **问题**：一个反幻觉的技能，自己缺少反幻觉的自我审查机制，是结构性不对称。软件工程技能有幻觉更正表，本技能没有。
- **发现方式**：本轮自我审查。
- **修正**：新增 `ERRATA.md`（本文件）。
- **波及文件**：`ERRATA.md`、`CONSTITUTION.md`（无需新增条款，但 `README.md` 文件地图加入）。
- **状态**：`closed`（2026-11-11）

#### E-007 — “接地完成”判据缺失

- **原表述**：`README.md` 说“设计上完备，运行上待接地”，但未定义接地判据。
- **问题**：无法判断技能何时可用。
- **发现方式**：本轮自我审查。
- **修正**：新增 `spec/GROUNDING_CRITERIA.md`；`CONSTITUTION.md` 新增第 12 条（接地治理）。
- **波及文件**：`spec/GROUNDING_CRITERIA.md`、`CONSTITUTION.md`、`README.md`。
- **状态**：`closed`（2026-11-11）

#### E-008 — `GROUNDING_CRITERIA` 的 G2/G3 依赖产物版本头

- **原表述**：G2 要求“产物版本与源版本对齐”，可查方式包含“`validation/` 产物的版本头”与 `COMPILATION_META.md` 第 7.5 条版本对齐检查；G3 的可查方式未明确以 `STATE.md` 与部署配置为准。
- **问题**：现行仓库已移除文件版本头，版本对齐不再有可查对象；继续按原文执行会使 G2/G3 无法判定。
- **发现方式**：落地分享内容时与现行版本口径冲突。
- **修正**：G2 改为以 `STATE.md` 中产物状态为 `active` 且部署配置存在产物清单为准；G3 改为以 `STATE.md` 中检查器与用例状态、部署配置中的执行入口为准。删除版本头/版本对齐依赖。
- **波及文件**：`spec/GROUNDING_CRITERIA.md`。
- **状态**：`closed`（2026-11-11）

#### E-009 — `QUICKSTART` 中 `A-001` 重复用作 HumanActor 与 assumption

- **原表述**：最小样例的 `actors` 中 HumanActor 使用 `A-001`，`assumptions` 中也使用 `A-001`。
- **问题**：两个不同类型实体共享同一 ID，破坏引用唯一性，可能使校验器或读者混淆。
- **发现方式**：落地分享内容时进行样例审查。
- **修正**：assumption 改用独立前缀 `AS-001`，输入与输出中的引用同步更新。
- **波及文件**：`QUICKSTART.md`。
- **状态**：`closed`（2026-11-11）

#### E-010 — `CONTEXT_ASSEMBLY` 残留“本文件的版本”表述

- **原表述**：第 9 节标题为“版本纪律”，末条为“本文件的版本与 `README.md` 的‘阅读路径’保持语义一致”；第 6 节有“编译产物版本变化时……”。
- **问题**：现行仓库不保留文件版本头，“本文件的版本”没有可查对象；该表述与 E-008 同源，属同一口径冲突的残留。
- **发现方式**：落地分享内容后进行版本口径一致性检查。
- **修正**：第 9 节标题改为“修订纪律”，末条改为“本文件的内容与 `README.md` 的‘阅读路径’保持语义一致”；第 6 节“编译产物版本变化时”改为“编译产物更新时”。未改变任何约束语义。
- **波及文件**：`spec/CONTEXT_ASSEMBLY.md`。
- **状态**：`closed`（2026-11-11）

#### E-011 — 文件版本载体与“产物版本 = 源文件版本函数”的口径变更

- **原表述**：`CONSTITUTION.md` 第 9 条、第 11.7 条要求规范层与术语表的版本号在文件头声明；`spec/COMPILATION_META.md` 第 3.6、7.5 条与第 10 条、`spec/methods/deterministic-checker.md` 第 9 节以文件版本为输入定义“产物版本 = f(`GRAMMAR.md` 版本, `SOURCE_LEDGER.md` 版本, 方法版本)”，并在装配时比对版本是否对齐。
- **问题**：文件层去版本（ADR-0003）后该链没有输入；且版本号比较无法发现“源文件已改但未递增版本号”，会给出假通过——这使“防过期产物”在版本号机制下本身就不可靠。
- **发现方式**：落地 ADR-0003 时逐条核对现存条文。
- **修正**：按 ADR-0003 改为包层 tag 声明版本、文件不承载版本；按 ADR-0004 改为产物记录生成基线的 `source_commit`，装配时比对当前源提交，源文件有未提交改动时直接判定过期。
- **波及文件**：`CONSTITUTION.md`、`spec/COMPILATION_META.md`、`spec/methods/deterministic-checker.md`、`AGENTS.md`、`README.md`、`manifest.json`。
- **状态**：`closed`（2026-11-11）

#### E-012 — Zenodo 候选条目“未核验”状态已解除，确认存在但领域不符不入表

- **原表述**：`SOURCE_LEDGER.md` 候选表记为“来源接地不能防止幻觉”的 zenodo 论文，评审未核验，标题、作者、DOI 均未确认。
- **问题**：条目长期停留在“疑似幻觉”状态，无法判断是登记错误还是检索不足。
- **发现方式**：2026-11-12 实际检索 Zenodo API 与搜索引擎。
- **修正**：确认存在两项同日预印本记录：`10.5281/zenodo.18039274`（题名 *Source-Grounding Does Not Prevent Hallucinations: A Controlled Replication Study of Google NotebookLM*）与 `10.5281/zenodo.18043672`（题名 *RAG: Source-Grounding Does Not Prevent Hallucinations in NotebookLM*），作者均为 Jennifer Evans，发布日期均为 2025-12-24，资源类型均为 Preprint。**不是幻觉**。但论文主题为 RAG 与幻觉机制，不属于通用项目管理知识，按 `CONSTITUTION.md` 第 2.6 条领域测试**仍不入表**；候选条目改记为“已核实存在、领域不符”。
- **波及文件**：`SOURCE_LEDGER.md`。
- **状态**：`closed`（2026-11-12）

### 3. 待核验的存疑表述

以下表述已进入技能包，但尚未经外部来源核验。**它们不构成阻断，但在核验完成前不得作为“已接地”的依据**（`spec/GROUNDING_CRITERIA.md` G1 的 `assumption` 接受机制已覆盖）：

| 编号 | 表述 | 位置 | 核验方式 | 状态 |
|---|---|---|---|---|
| V-001 | ISO 21502:2020 是否保留“五过程组 × 十主题组”矩阵结构 | `GRAMMAR.md` G-B1/G-B2、`SOURCE_LEDGER.md` | 获取全文核对 | `open`（T-001） |
| V-002 | PRINCE2-2023 的具体条款措辞 | `GRAMMAR.md` G-F1/G-F2/G-G1–G3、`SOURCE_LEDGER.md` | 获取全文核对 | `open`（T-005） |
| V-003 | ProjectCO-2024 的论文内部细节 | `SOURCE_LEDGER.md` | 获取全文核对 | `open`（T-006） |
| V-004 | 方法条目 `M-EST-01`、`M-DEC-01`、`M-RISK-01`、`M-EV-01` 的更精确来源 | `knowledge/methods/registry-skeleton.md` | 获取对应章节核对 | `open`（T-004） |

### 4. 不做的事

- 不把 ERRATA 当作第二套规范——它记录更正历史，不承载规则。
- 不改写已登记条目；更正时追加新条目并引用原编号。
- 不把“待核验”表述包装成“已核验”。
- 不因为某条更正是“自己发现的”就降低登记标准——自我审查与外部评审同样登记。
