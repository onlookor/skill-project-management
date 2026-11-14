## 后续工作

**登记规则**：见 `AGENTS.md` 第 3.2 条。本文件是**单点工作项台账**；顺序、里程碑与出口条件见 `ROADMAP.md`。编号续用，不重排；不静默删除，关闭时保留行并标 `done` 或 `dropped` 并附证据。

**状态取值**：`open` / `in-progress` / `blocked-external` / `done` / `dropped`。

**里程碑**：M0–M7 的定义与出口条件见 `ROADMAP.md`。

### M0 基线与发布卫生

**状态**：已关闭（2026-11-13，批次 0024；出口证据见 `ROADMAP.md` 的 M0）。

| 编号 | 里程碑 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|---|
| T-070 | M0 | 引用修复 | 全仓库检索已删除编译规范的残留引用，更新为 `spec/COMPILATION_META.md` + `spec/methods/deterministic-checker.md` 的对应位置 | 执行层补丁（不需 ADR） | 无 | `done`（2026-11-12，`scripts/check_anchors.py` 复核为 0 错误） |
| T-110 | M0 | 发布一致性检查 | 建立 `manifest.json` 的包版本与最新 annotated tag 的一致性检查，避免两处记录漂移（已并入 `scripts/check_state.py`） | 执行层补丁 | 无 | `done`（2026-11-13，批次 0021；`0.4.0` ↔ `v0.4.0` 通过） |
| T-111 | M0 | 产物基线字段 | 为 `validation/CHECKLIST.md` 补充 `source_commit` 字段并在生成流程中写入；在此之前现有清单视为“基线未记录”，装配时按过期处理（ADR-0004） | 执行层补丁 | 无 | `done`（2026-11-13：`source_commit` = `b16e3b8`，方法声明最后变更提交；批次 0022） |
| T-114 | M0 | 一致性检查 | 建立“文档中所有 `grounding_ref` 都指向 `SOURCE_LEDGER.md` 的 active 条目”的闭环检查，并与 `check_ledger_landings.py` 合并为一次运行 | 执行层补丁 | 无 | `done`（2026-11-12，已由 `scripts/check_anchors.py` 实现，与落点检查同批运行） |
| T-116 | M0 | 流程接入 | 把 `scripts/check_anchors.py` 纳入提交前检查清单，与 `check_ledger_landings.py` 同批运行 | 执行层补丁 | 无 | `done`（2026-11-13：`.githooks/pre-commit` 依次运行四个检查器；负例提交被阻断、正例提交放行；批次 0023、0024） |
| T-127 | M0 | 规范层补丁 | 把规则组 B 的 `pending_reanchor` 签注同步为 `active`：`validation/CHECKLIST.md`、`spec/methods/deterministic-checker.md` 与方法条目摘要三处，与 ADR-0008 一致；规则组 F、G 的 `assumption` 标注按实际状态保留 | 执行层补丁 | 无 | `done`（2026-11-13：三处均为 `active`，`severity` 保持 `advisory`；批次 0022） |
| T-128 | M0 | 发布 | 打 annotated tag `v0.5.0`，同步 `manifest.json` 的 `package_version` 与 `release_tag`；发布说明记录批次与检查器结果 | CHANGELOG + tag | M0 其余条目完成，四个检查器为 0 | `done`（2026-11-13：`manifest.json` 为 `0.5.0` / `v0.5.0`；annotated tag `v0.5.0` 指向批次 0022 提交，已 push 到 origin，远端解引用为 `7f386df`；批次 0022） |

### M1 可执行校验器 v0

| 编号 | 里程碑 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|---|
| T-011 | M1 | 检查器实现规格 | 为 `spec/methods/deterministic-checker.md` 附录 A 注册表中的每个 check 补充参考实现的输入/输出样例 | 结构性变更需 ADR | 无 | `done`（2026-11-14：17/17 个 check_id 各补触发/不触发两组，共 34 个样例；批次 0027） |
| T-100 | M1 | 检查器判定修正 | 修正 `ROLE_MINIMAL_COMPLETENESS` 的 warn/block 混合判定：区分“问责结构根本性缺失（block）”与“角色合并声明缺失（warn）”两种情形（见 `ERRATA.md` E-004；与 T-107 同批）；缺口台账编号 G-004 | 结构性变更需 ADR（改变已有规则的编译结果） | 无 | `in-progress`（2026-11-14 首轮关闭被非同源复核推翻；G-004 已重开，待判定列格式与原因码修正后由非同源复核关闭） |
| T-103 | M1 | 检查回放机制 | 定义检查执行记录的回放机制：检查失败后如何以同一输入快照重放、如何比对两次结论、回放记录保存在哪里 | 执行层补丁 | 无 | `open` |
| T-107 | M1 | 可执行原型 | 提供一个最小可执行的确定性校验器原型（哪怕只覆盖 3–5 个 `check_id`），以验证 `spec/methods/deterministic-checker.md` 的判定逻辑可被程序实现；`QUICKSTART.md` 的走查为手工推演，不构成可执行证据。**当前进度**：`validation/checker-prototype/checker.py` 已覆盖 17/17 个 `check_id`、34/34 个样例，输入 schema 见 `spec/CHECKER_INPUT_SCHEMA.md` | 执行层补丁 | T-011 | `done`（2026-11-14：34/34 样例、17/17 `check_id` 通过；批次 0029） |
| T-041 | M1 | 验证套件 | 为 `GRAMMAR.md` 的 `active` 规则设计检查器测试用例（含 `pass` / `fail` / `cannot_evaluate` 三值覆盖；与 T-101 的用例补齐同批） | 结果登记 | T-011 | `open` |
| T-042 | M1 | 验证套件 | 验证 `ASSUMPTION_PROTOCOL.md` 第 5 节的四条 `unknown` 处置纪律在检查器实现中一致 | 结果登记 | T-011 | `open` |
| T-081 | M1 | 验证套件 | 验证 `CM-DET-CHECKER` 的退化路径（`runtime: deterministic-checker/human-fallback`）下 P1–P6 仍被满足 | 结果登记 | 无 | `open` |
| T-130 | M1 | 判定口径裁定 | 裁定 G-A1 的“`Constraint` 作用于该 `Outcome` 或 `Commitment`”子句是否纳入 `PROJECT_MINIMAL_EXISTENCE`：当前 A 表判定列只检查四类节点存在与 `Commitment` 端点，未检查约束作用边；若纳入，属于改变已有 `check_id` 判定，需 ADR；缺口台账编号 G-002 | 结构性变更需 ADR | T-011 样例编写时暴露 | `done`（2026-11-14：G-002 经非同源复核关闭，批次 0043） |
| T-131 | M1 | 判定口径裁定 | 裁定 G-E2 的“该 `Assertion` 以 `assumption` 形式存在并附带验证条件”是否纳入 `AI_AUTONOMY_DELEGATION_AUDITABLE`：当前 A 表判定列只要求链上有 `Assertion` 声明范围/边界/撤销条件；若纳入，属于改变已有 `check_id` 判定，需 ADR；缺口台账编号 G-003 | 结构性变更需 ADR | T-011 样例编写时暴露 | `done`（2026-11-14：G-003 经非同源复核基线 `9519b82` 关闭，批次 0046） |
| T-137 | M1 | 判定口径裁定 | 修正 `actors[].type` 的封闭枚举归一化：`CHECKER_INPUT_SCHEMA.md` §1.11 未列 `actor_type`，原型 `enum_results()` 未校验，`Bogus` 仍 `pass`；合法值限 §2 枚举，非法值判 `cannot_evaluate/undefined_enum_value`；缺口台账编号 G-018 | 执行层补丁 | T-133 复核结论 | `open` |

### M2 表示层收口

| 编号 | 里程碑 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|---|
| T-080 | M2 | 验证套件 | 为 `CM-DET-CHECKER` 的 P1c（不扭曲）设计反例检验用例：每条规则至少一个“应通过”与一个“应失败”用例，含量词边界（空集/单元素/多元素）与例外触发用例 | 结果登记 | 无 | `in-progress`（`validation/test-cases/` 已落 3 个用例，其余见 T-101） |
| T-101 | M2 | 反例用例补齐 | 补齐未落盘的 10 个反例检验用例正文：`TC-A1-01`、`TC-A1-03`、`TC-C1-01`、`TC-C1-02`、`TC-D1-01`、`TC-D1-02`、`TC-D1-03`、`TC-E1-01`、`TC-E1-02`、`TC-E1-03`；并补齐未覆盖规则（G-A2、G-C2、G-D2、G-E2、G-B1、G-B2、G-F1–F4、G-G1–G3）的用例 | 结果登记 | T-080 | `open` |
| T-133 | M2 | 独立复核 | 对 T-107 原型做非同源复核：34/34 是样例与实现同源的自证，不构成独立证据。复核方按 `validation/independent-review-package.md` 做独立实现比对或人工逐条比对规则正文，并记录差异。**输入**：独立复核已完成 3/17 个 `check_id` 的比对（G-A1、G-C1、G-D1 的 6 个样例，6/6 判定一致），并报出 G-005、G-006、G-007 与八条表示层问题（P1–P8）；这些结论已作为 ADR-0013 的裁定输入并全部关闭。**剩余动作**：对 ADR-0013 改动后的判定列/schema 做**一次**非同源重跑，记录差异；若出现新差异，按缺口入口判据登记，不以“已经复核过”挡回。**不构成 M2 出口**：M2 的出口由 `check_three_table.py`、原型重跑与“同源缺口零新增”机械判定，不以复核进度为门 | 结果登记 | T-107 | `done`（2026-11-14：非同源复核基线 `9519b82` 完成，关闭 G-014/G-001/G-003/G-007/G-008，新登记 G-018，维持 G-017 `open`；批次 0046） |
| T-134 | M2 | 判定口径裁定 | 裁定 G-C1 的“`Assertion` 内容须是关于该交付物是什么、处于什么状态、满足什么条件的明确陈述”是否纳入 `DELIVERABLE_ASSERTION_LINK`：当前判定列只检查 `asserted_by` 边存在，未检查断言内容，也未检查 `about` 是否指向该交付物；样例 A.1.3-2 的空断言仍期望 `pass`。若纳入，属于改变已有 `check_id` 判定，需 ADR；缺口台账编号 G-005 | 结构性变更需 ADR | T-133 复核结论 | `done`（2026-11-14：G-005 经非同源复核关闭，批次 0043） |
| T-135 | M2 | 判定口径裁定 | 裁定 G-D1 的“变更提议的对象限于 `Commitment` 或 `Deliverable`”是否纳入 `CHANGE_CONSTRAINT_LINK`：当前判定列对任何变更提议生效，缺少 `target` 对象类型谓词；若纳入，属于改变已有 `check_id` 判定，需 ADR；缺口台账编号 G-006 | 结构性变更需 ADR | T-133 复核结论 | `done`（2026-11-14：G-006 经非同源复核关闭；`constraint=null` 走 `cannot_evaluate/missing_input`，措辞更正见批次 0046） |
| T-136 | M2 | 判定口径裁定 | 裁定判定列的五处语义口径并写回附录 A：端点量词（`Commitment` 的 `by`/`to` 是“每个”还是“存在一个”）、空对象语义（`{}` 与缺键/空列表的区分）、悬空引用的原因码（`fail` 还是 `cannot_evaluate`）、多违规时 `reason` 的优先级、`about` 反向引用是否构成 G-C1 的“出边”；裁定结果属判定列语义补全，改变已有 `check_id` 判定时需 ADR；缺口台账编号 G-007 | 结构性变更需 ADR | T-133 复核结论 | `done`（2026-11-14：G-007 经非同源复核基线 `9519b82` 关闭，批次 0046；G-001 同时关闭，`actors[].type` 另立 G-018） |

### M3 本体定义

| 编号 | 里程碑 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|---|
| T-122 | M3 | 本体构建 | 按 `spec/ONTOLOGY_FEASIBILITY.md` 第 3 节构建全量本体：`pmbok8-vocab.ttl`（92 类 / 35 对象属性 / 7 数据类型属性）、`pmbok8-processes.ttl`（7 域 + 5 焦点区 + 40 过程 + I/O）、`pmbok8-artifacts.ttl`（124 工件）、`pmbok8-tools.ttl`（185 工具与技术）、`pmbok8-shapes.ttl`（24 条形状）、24 个违规 fixture + 1 个通过 fixture、`scripts/validate_ontology.py` | CHANGELOG（内容与格式）；不新增编译方法 | 无（校验需 `rdflib`、`pyshacl`） | `done`（2026-11-13：24 条形状全部由对应 fixture 判出违规，本体全图 `conforms: true`） |
| T-126 | M3 | 本体补全 | 为 124 个工件与 185 个工具与技术补齐自写定义（当前为 `taxonomy-only`，只保留术语名、类别与页码）；写不出自述定义者保持 `pending`，不得用原文改写凑数 | 执行层补丁（CHANGELOG） | 无 | `open` |
| T-132 | M3 | 流程撤除 | 评估并撤除缺口台账临时机制（`GAP_LEDGER.md` 与 `scripts/check_gap_ledger.py`）：按 `AGENTS.md` 3.6.5 的三项撤除条件核对连续两个发布点的 `open=0`、核查矩阵 17/17 `consistent` 与全量“规则正文 ↔ 判定列”对照；满足则删除台账与检查器、移除钩子与 `check_state.py` 调用，未满足则按台账规则冻结 | 执行层补丁 + 钩子 | 硬约束：不晚于 M3 关闭 | `open` |
| T-138 | M3 | 试点执行 | 按 `spec/M3_M4_PLAN.md` 第 3 节执行 15 条草稿试点：6 工件 + 6 工具 + 1 过程 + 1 焦点区 + 1 绩效域；产出草稿条目、`pilot-id-map`、1 份契约、1 份产物样例与 3 组冲突样例，并逐项判定 7 条判据与 6 条止损 | CHANGELOG + 试点报告 | D1/D2/D3/D8 已定；D4 降级 | `done`（2026-11-14：15 条落盘，14 条有候选 IRI、1 条 `null` 且有稳定自然键，止损未命中；外部抽样 blocked-external；批次 0047） |
| T-139 | M3 | 字段语义统一 | 统一 `grounding_ref` 语义：D3 选定指向 `knowledge:<term>`，但现有 10 条 `knowledge/anchored-entries.jsonl` 指向来源 ID；放量前需在“修订 D3 表述”与“新增独立 `source_ref` 并迁移现有条目”之间二选一。试点按 D3 写入、来源移入 `evidence`，两套语义暂时并存 | 结构性变更需 ADR | T-138 试点发现；D4 同批 | `done`（2026-11-14：按“两种意图拆开”落实；10 条来源迁入 `evidence[]`，`grounding_ref` 只用于规则/本体到条目的绑定；语义写入 `ANCHOR_SPEC`、`CHECKER_INPUT_SCHEMA` §1.16 与 `GRAMMAR`；批次 0048） |
| T-140 | M1 | 检查器修正 | 修正 `check_no_raw_material.py` 的 `RM-PROSEBLOCK`：连续 ≥15 行、每行 ≥100 字符且非 Markdown 表格行的结构化 JSON/JSONL 记录被误判为文本层转储；当前 `knowledge/anchored-entries.jsonl` 为 10 条，扩到 15 条即阻断 M3 铺开。按格式或记录结构豁免结构化数据，保留对 PDF/OCR 转储的检测；补“15 条长 JSONL 不报”与“15 行长文本转储仍报”两组负例；缺口台账编号 G-019 | 执行层补丁 | T-138 试点发现 | `done`（2026-11-14，批次 0049：新增 `is_structured_jsonl()`，仅豁免每行一个 JSON 对象的 `.jsonl`；`--self-test` T-NRM-01–04 4/4 通过；15 条/20 条 JSONL 实测 0 报。G-019 仍 `open`，待非同源复核或人工签收） |

### M4 来源收口

| 编号 | 里程碑 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|---|
| T-001 | M4 | `pending_reanchor` 解除 | 核验 ISO 21502:2020 是否保留“五过程组 × 十主题组”矩阵结构；核验方式：获取全文（本地优先），核对分类维度 | ADR | 本地资源或权威访问 | `open` |
| T-002 | M4 | `assumption` 升级（G-F 组） | 逐条核验 G-F1–G-F4 的锚定来源（ISO 21502:2020 的过程覆盖、PRINCE2 的阶段管理原则）；核验后决定升级为 `block` 或修订陈述 | ADR | T-001 同源核验 | `open` |
| T-003 | M4 | `assumption` 升级（G-G 组） | 核验 G-G1–G-G3 的锚定来源（PRINCE2 裁剪原则）；核验后决定升级或修订 | ADR | 无 | `open` |
| T-004 | M4 | 来源精度提升 | 为 `M-EST-01`、`M-DEC-01`、`M-RISK-01`、`M-EV-01` 补充更精确的来源锚定（当前仅指向 PMBOK 原则层交叉验证；与 T-094 合并执行） | ADR + `SOURCE_LEDGER.md` 更新 | 本地资源 | `open` |
| T-005 | M4 | 来源精度提升 | 核验 PRINCE2-2023 的具体条款措辞（当前仅版本核验）；核验后更新 `SOURCE_LEDGER.md` 的 `verification_method` 与相关规则的 `provenance_note` | ADR | 本地资源 | `open` |
| T-006 | M4 | 来源精度提升 | 核验 ProjectCO-2024 的论文内部细节（当前仅存在性核验）；核验后决定是否扩展 `claim_mapping` | ADR | 本地资源 | `open` |
| T-007 | M4 | 一致性检查 | 建立 `GRAMMAR.md` 的 `grounding_ref` 与 `SOURCE_LEDGER.md` 的 `claim_mapping` 的双向一致性检查项 | 执行层补丁（不需 ADR） | 无 | `open` |
| T-008 | M4 | 版本漂移 | 评估是否引入 PMBOK 8th edition (2025-11)；引入需 ADR 论证规则依赖 | ADR | T-004 同源 | `open` |
| T-052 | M4 | 治理实践 | 审查 `SOURCE_LEDGER.md` 候选来源清单，决定是否引入 Silega 等 2024 年 PMBOK 形式化论文（需先核验原文） | ADR | 原文核验 | `blocked-external`（解锁条件：取得全文，或按 T-106 确认长期不可得后收口） |
| T-094 | M4 | 术语补充 | 为 `GLOSSARY.md` E 类条目补充更精确的 `grounding_ref`（当前 `WBS`、`PERT`、`EVM` 的 `grounding_ref` 仅为 PMBOK 原则层交叉验证；与 T-004 合并执行） | ADR + `SOURCE_LEDGER.md` 更新 | T-004 | `open` |
| T-106 | M4 | 外部依赖失效处置 | 规定“外部来源长期不可得”时的处置规则（T-001–T-003 均依赖获取 ISO 21502:2020 全文；当前未定义永远取不到时如何收口） | ADR | 无 | `open` |
| T-112 | M4 | 来源核验 | 取得 Springer 章节 `10.1007/978-3-031-50495-2_13` 全文后，核对其 OWL 本体与“reasoner 一致性检查”的论断，决定是否将其作为知识层条目的来源；在此之前 `SPRINGER-PMBOK-2024` 仅元数据可用。2026-11-12 致信尝试因 SMTP 535 认证失败未发出（ERRATA E-015）；网页端手动发送见 T-121（与 T-115 合并处置） | 来源治理（ADR） | 通讯作者提供全文 | `blocked-external`（解锁条件：取得全文） |
| T-113 | M4 | 来源核验 | 核对本地 ISO 21502:2020 副本的“过程组/主题组”结构，决定 G-B1、G-B2 是否解除 `pending_reanchor` | 来源治理（ADR） | 无（本地副本已具备） | `done`（2026-11-12：逐页核对确认无该矩阵；G-B1/G-B2 按第 6/7 章改写并解除 `pending_reanchor`，ADR-0008，CHANGELOG 批次 0015） |
| T-115 | M4 | 来源核验 | 复核 `SPRINGER-PMBOK-2024` 的 `pending:T-112` 状态；正文长期不可得时，决定是保留为待落点条目还是移出登记表 | 来源治理（ADR） | T-112 | `blocked-external`（解锁条件：T-112 取得全文或确认不可得） |
| T-119 | M4 | 来源核验 | 取得 ProjectCO 论文外部附录（`bit.ly/ProjectCO_Appendices`）与本体文件，核对 `Actor`、`Commitment`、`Constraint` 是否有原文依据；若确无，则改写 `knowledge/anchored-entries.jsonl` 中三个条目的来源表述并复核 G-A1、G-D1、G-E1 的锚定 | 来源治理（ADR） | 附录与本体文件可获取 | `blocked-external`（解锁条件：附录与本体文件可获得） |
| T-121 | M4 | 治理 | 由用户经网页端手动发送请求全文的邮件：收件人 `silega@sfedu.ru`，发信人 `wgzhi@hotmail.com`，署名 Gengzhi Wei。正文见下方附录。SMTP 客户端通道因服务器停用基础认证（`535 5.7.139`）不可用，本项**未发送**；不得记为已发送 | 无（人工操作） | 用户手动发送 | `blocked-external`（解锁条件：用户完成手动发送并回填发送结果） |
| T-123 | M4 | 来源治理 | 评估是否修订 `SOURCE_LEDGER.md` 中 `PMBOK8-2025` 的 `allowed_uses` 与 `claim_mapping`，使其可作为概念层（而非仅原则层交叉验证）依据；修订需 ADR，并说明对 P1a 与 `check_ledger_landings.py` 的影响。**试点证据（T-138）**：15 条草稿的来源证据全部指向该来源，`allowed_uses` 未放开前，放量条目会集体处于“有 grounding_ref 但无概念层使用授权”的状态 | 来源治理（ADR） | T-122 | `done`（2026-11-14：用户授权，ADR-0016 `accepted`；`allowed_uses` 放宽至概念层，仍禁成段摘录、原文替代定义、未核页批量引用与规则直接锚定；批次 0048） |
| T-125 | M4 | 接入建议 | 若将来把本体接成 `grounding_ref`：优先评估 G-A1（项目最小存在）、G-A2（断言主体）、G-C1（可交付物与断言）、G-D1（承诺链）、G-E1（约束锚定）与对应知识条目 `Project`、`Assertion`、`Deliverable`、`Commitment`、`Constraint`；先做“形状 ↔ 规则文本”逐条对照（P1c），再决定是否改来源用途 | 规范层（ADR） | T-123、P1c 对照 | `open` |

### M5 接口、契约与跨技能

| 编号 | 里程碑 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|---|
| T-010 | M5 | 解析器实现规格 | 为 `contracts/resolver.md` 补充解析器的参考实现伪代码（供宿主实现时参照） | 结构性变更需 ADR | 无 | `open` |
| T-012 | M5 | 多层合并启用评估 | 评估是否启用多层契约合并（`spec/INTERFACE_CONTRACT_SPEC.md` 第 6 节）；启用需 ADR 论证真实需求 | ADR | 三个以上技能接入 | `blocked-external`（解锁条件：三个以上技能实际接入） |
| T-013 | M5 | PACT 适配验证 | 在宿主安装 PACT 时验证 `spec/INTERFACE_CONTRACT_SPEC.md` 第 8 节与 `contracts/resolver.md` 第 3 节的可映射/不可映射声明是否与实际 PACT 行为一致 | 执行层补丁 | PACT 可用 | `blocked-external`（解锁条件：宿主安装可用的 PACT） |
| T-030 | M5 | 契约样例 | 补充第三个领域样例（如“运维/服务管理”），验证槽位定义的领域无关性 | 随样例更新 | 无 | `open` |
| T-031 | M5 | 连接实例样例 | 在 `contracts/examples/` 中补充连接实例声明样例（不进入成文法） | 随样例更新 | 无 | `open` |
| T-104 | M5 | 跨技能端到端走查 | 设计一条“领域技能产物 → 项目管理槽位/baseline”的端到端走查样例（如需求工程产物进入本项目），验证 `spec/INTERFACE_CONTRACT_SPEC.md` 的槽位定义在真实流动中可用 | 随样例更新 | T-031 | `open` |
| T-105 | M5 | 方法注册表可用性 | 补充方法的规模/领域筛选机制与方法组合说明（如挣值与风险的配合、WBS 与估算的配合）；当前注册表只有检索键，没有组合与筛选规则 | 来源治理 | T-004、T-020–T-027 | `open` |
| T-118 | M5 | 规范层补丁 | 评估 G-B1、G-B2 是否由 `advisory` 升为 `block`：需先取得双标签在样例契约中的使用证据（值集是否够用、映射歧义是否可控）。M0 的签注同步见 T-127；本项只做升级评估 | 规范层补丁（ADR） | 样例契约覆盖 A–G 组 | `open` |

### M6 知识层与术语

| 编号 | 里程碑 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|---|
| T-020 | M6 | 方法条目 | 填充 `estimation` 类别：类比估算、参数估算、自下而上估算 | 来源治理 | T-004 | `open` |
| T-021 | M6 | 方法条目 | 填充 `decomposition` 类别：按阶段分解、按地理分解 | 来源治理 | T-004 | `open` |
| T-022 | M6 | 方法条目 | 填充 `risk` 类别：蒙特卡洛模拟、决策树 | 来源治理 | T-004 | `open` |
| T-023 | M6 | 方法条目 | 填充 `earned_value` 类别：燃尽图、累积流量图 | 来源治理 | T-004 | `open` |
| T-024 | M6 | 方法条目 | 填充 `procurement` 类别：合同类型选择 | 来源治理 | T-002 | `open` |
| T-025 | M6 | 方法条目 | 填充 `stakeholder` 类别：权力-利益矩阵 | 来源治理 | 来源待定 | `open` |
| T-026 | M6 | 方法条目 | 填充 `communication` 类别：沟通计划编制 | 来源治理 | 来源待定 | `open` |
| T-027 | M6 | 方法条目 | 填充 `quality` 类别：质量审计、因果图 | 来源治理 | 来源待定 | `open` |
| T-028 | M6 | 本体条目 | 补充 `LegalEntity`、`HumanActor`、`AIActor` 的独立条目（当前在 `Actor` 条目中内联；与 T-092 合并执行） | 来源治理 | 无 | `open` |
| T-029 | M6 | 本体条目 | 补充 `Contract`、`ProjectCharter`、`TailoringRecord` 的条目（G-F/G-G 组引用） | 来源治理 | T-002、T-003 | `open` |
| T-040 | M6 | 验证套件 | 为首批方法条目设计检索测试集，验证 `CHARTER.md` 承诺 C1 的召回率阈值 | 结果登记 | T-020–T-027 | `open` |
| T-050 | M6 | 治理实践 | 为 `CHARTER.md` 承诺 C1 的召回率阈值确定具体数值（当前为“待首批条目入库后确定”） | ADR | T-040 | `open` |
| T-060 | M6 | 方法声明 | 编写 `spec/methods/skill-card.md`（CM-SKILL-CARD 的声明文件，按 META 第 4 条格式；文件待编写） | 方法声明变更需 CHANGELOG；启用需 ADR | 无 | `open` |
| T-061 | M6 | 方法声明 | 编写 `spec/methods/human-checklist.md`（CM-HUMAN-CHECK 的声明文件；文件待编写） | 同上 | 无 | `open` |
| T-062 | M6 | 方法声明 | 编写 `spec/methods/pact-rules.md`（CM-PACT 的声明文件；文件待编写） | 同上 | 无 | `open` |
| T-063 | M6 | 方法声明 | 编写 `spec/methods/neuro-symbolic.md`（CM-NEURO-SYMB 的声明文件；v0.1 不评估启用；文件待编写） | 同上 | 无 | `open` |
| T-071 | M6 | 一致性检查 | 建立 `spec/COMPILATION_METHODS.md` 的方法登记与 `spec/methods/{method-id}.md` 声明文件的一致性检查项（名称、适用范围、状态） | 执行层补丁 | T-060–T-063 | `open` |
| T-072 | M6 | 一致性检查 | 建立 `spec/COMPILATION_META.md` 第 2 条（P1–P6）与各方法声明文件第 3–7 节的覆盖检查项（每个方法必须逐条论证 P1–P6） | 执行层补丁 | T-060–T-063 | `open` |
| T-090 | M6 | 一致性检查 | 建立 `GLOSSARY.md` 的 A 类条目与 `knowledge/anchored-entries.jsonl` 的同步检查项（定义一致、`anchored_entry` 指针有效） | 执行层补丁 | 无 | `in-progress`（`scripts/check_glossary_sync.md` 已给出检查规格，检查执行记录待补） |
| T-091 | M6 | 术语补充 | 补充 `GLOSSARY.md` 第 6 节列出的待补充术语（编译域执行失败分类、ADR 状态、`merge: append`、`immutable`、`SLA`、`SLO`、`RPO`、`RTO`、`CI/CD`、`API`、`IDL`） | E/F 类走 CHANGELOG；B/C/D 类走 ADR | 无 | `open` |
| T-092 | M6 | 术语补充 | 为 `GLOSSARY.md` A 类的 `HumanActor`、`LegalEntity`、`AIActor`、`Contract`、`ProjectCharter`、`TailoringRecord` 补充 `anchored-entries.jsonl` 的独立条目（与 T-028、T-029 合并执行） | ADR + JSONL 同步 | T-028、T-029 | `open` |
| T-093 | M6 | 术语补充 | 为 `GLOSSARY.md` B 类的机制术语补充“首次使用处”的内联定义检查（验证 `GRAMMAR.md`、`spec/` 中各术语首次出现时是否有内联定义或指向 `GLOSSARY.md`） | 执行层补丁 | 无 | `open` |

### M7 治理收口与 v1.0.0

| 编号 | 里程碑 | 性质 | 工作项 | 治理路径 | 前置依赖 | 状态 |
|---|---|---|---|---|---|---|
| T-051 | M7 | 治理实践 | 评估是否需要在 `CONSTITUTION.md` 第 2 条增加“来源修订”状态（当前只有 active/deprecated/superseded） | ADR | 实际需求出现 | `open` |
| T-102 | M7 | ADR 治理补强 | 补充“被拒绝方案”的 ADR 记录（考虑过、论证不可行、拒绝理由），并给出 ADR 合格性评审清单；当前 ADR-0001、ADR-0002 均只记录“决定这样做” | ADR（新增记录）；评审清单本身属执行层补丁 | 无 | `open` |
| T-108 | M7 | 版本条文的遗留冲突 | `CONSTITUTION.md` 第 9 条与第 11.7 条仍要求“版本号在文件头声明”，与现行口径（不保留文件版本头，状态登记于 `STATE.md`）冲突；待确认后按规范层程序修订，未确认前不改条文 | ADR | 用户确认 | `done`（ADR-0003、ADR-0004；CHANGELOG 批次 0007） |
| T-109 | M7 | 产物版本链重构 | `spec/COMPILATION_META.md` 第 10 条与 `spec/methods/deterministic-checker.md` 第 9 节以“文件头版本”为输入定义产物版本与对齐检查；文件层去版本后该链失效，需裁定替代口径 | ADR（改变已有规则的编译结果） | 用户裁定 | `done`（ADR-0004；CHANGELOG 批次 0007） |
| T-117 | M7 | 引用登记 | 为 `SKILL.md`、`validation/test-cases/TC-*.md` 等尚未创建的引用建立计划项登记，避免长期以“示例/计划”身份存在 | 执行层补丁 | 无 | `open` |
| T-120 | M7 | 治理 | 若确需从已发布历史中移除误提交的原始资料，制定独立 ADR：明确影响范围、协作者同步方式与是否重写历史；ADR-0009 只约束新提交 | 治理（ADR） | 实际发生历史违规 | `open` |
| T-129 | M7 | 流程撤除 | 撤除发布引导的 `--no-verify` 通道：`check_state.py` 识别 `Release-Target: <tag>` 待发布声明，`.githooks/pre-push` 严格校验 tag 存在、annotated、指向 HEAD；关闭后删除 `AGENTS.md` 3.5/7bis 的例外与 trailer 强制 | 执行层补丁 + 钩子 | 无；硬约束：不晚于 `v0.5.2` 发布，机制生效后最多 1 次豁免 | `open` |

#### 附录：T-121 邮件正文（英文）

```text
To: silega@sfedu.ru
From: wgzhi@hotmail.com
Subject: Request for full text — "A Formal Representation of Standards for Project Management: Case PMBOK" (DOI 10.1007/978-3-031-50495-2_13)

Dear Dr. Silega,

I am Gengzhi Wei, working on an open-source project-management grounding skill:
https://github.com/onlookor/skill-project-management

The project turns general project-management knowledge into mechanically checkable
rules, and every rule must be anchored to a source that can be verified.

Your chapter "A Formal Representation of Standards for Project Management: Case
PMBOK" (Silega, Lapshin, Rogozov, et al., Springer, 2024,
DOI 10.1007/978-3-031-50495-2_13) is directly relevant to this work: the OWL
representation of PMBOK and the reasoner-based consistency checking you describe
are the closest prior art we have found for grounding rules in a formal ontology.
The full text is behind a paywall, so I can currently see only the abstract and
metadata.

Would you be willing to share a copy of the full text (a preprint or accepted
manuscript is fine) for research use? It would let us check the ontology's classes
and axioms against our source ledger instead of relying on the abstract.

Thank you for your time.

Best regards,
Gengzhi Wei
wgzhi@hotmail.com
```
