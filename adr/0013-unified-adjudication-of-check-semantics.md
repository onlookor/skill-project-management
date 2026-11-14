# ADR-0013: 判定层表示规范——以一次裁定收口语义、表达能力与三表对照

- **状态**：`proposed`（2026-11-14 修订中；上一轮 `accepted` 裁定已被非同源复核重跑推翻，见第 8 节）
- **日期**：2026-11-14（草案 2026-11-14；同日首次裁定后因复核推翻回到修订）
- **决策者**：架构负责人（按用户批准执行）；人类责任方已批准
- **serves_charter**：C3（来源封闭、可追溯）、C6（可机械检查、可审计）的维护条件
- **grounding_refs**：无（决策针对判定层表示，不依赖来源条目）
- **affected_files**：`GRAMMAR.md`（未改）、`spec/methods/deterministic-checker.md`（A 表、A.2 子句表、§4.2/4.4、样例）、`spec/CHECKER_INPUT_SCHEMA.md`（表示规范与枚举）、`validation/checker-prototype/checker.py`、`GAP_LEDGER.md`、`TODO.md`、`ROADMAP.md`、`AGENTS.md`、`scripts/check_three_table.py`（新增）、`scripts/check_glossary_usage.py`（新增）、`validation/CHECKLIST.md`（`source_commit`）

## 1. 背景与范围扩张

首轮草案把范围限定为“补判定列语义”，收口 G-001、G-002、G-003、G-005、G-006、G-007 六条缺口。独立复核随后报出 **8 条上层设计问题**，它们不是某条规则与判定列的落差，而是判定层的表示方式本身有缺陷；继续按“逐条补判定列”处理，会在同一结构缺陷上反复产生新缺口。

因此本 ADR 把范围扩张为 **“判定层表示规范”**：同时裁定原有的 D0–D9 与 8 条设计问题（P1–P8），并且**只动一次冻结文件、只重跑一次复核**。M2 的定位随之改为“表示层收口”，17 项复核结论是输入，不是出口。

### 1.1 裁定范围

| 类别 | 条目 | 原文出处 |
|---|---|---|
| 已登记缺口 | G-001、G-002、G-003、G-004、G-005、G-006、G-007 | `GAP_LEDGER.md` |
| 待决点 | D0–D9（草案阶段列出） | 本 ADR 第 2 节 |
| 上层设计问题 | P1 子条件被压缩、P2 未封闭枚举与自然语言值、P3 跨对象全称/相关性无载体、P4 引用完整性不统一、P5 assumption 时效与批准资格无载体、P6 链/路径/可达性无规范化、P7 适用性缺状态机且枚举缺 `not_applicable`、P8 三表无机械对照 | 独立复核报告 |

**不再排除 G-004**：草案曾以其成因为 `severity-mismatch` 为由排除；扩范围后 P1（子条件压缩）正是 G-004 的根因，排除会使“子句表”留下一个已知空洞，故纳入并由 A.2 的子句 severity 承接。

## 2. 决定

以下每条均为最终决定。“实现位置”指本次已落地的文件与检查项。

### 2.1 表示层（P2、P3、P4、P5、P6、P7）

| 编号 | 决定 | 实现位置 |
|---|---|---|
| P2 | 判定列只允许引用 schema 第 4 节的**具名枚举**；不得出现自然语言值。枚举集合由三表检查器校验闭合。 | `spec/CHECKER_INPUT_SCHEMA.md` 第 1.8、4 节；`scripts/check_three_table.py` 规则 5 |
| P3 | 跨对象条件必须落为**关系路径**，量词显式：顶层域默认全称、引用必须全部解析、“存在一个”用集合非空表达。 | schema 第 1.6、1.7、3bis 节 |
| P4 | 引用完整性采用**全局统一策略**：目标 `id` 不存在 → `fail` / `dangling_reference`；目标类型未在 schema 定义 → `cannot_evaluate` / `undefined_object_type`。所有 `check_id` 同一口径，由原型在进入各 `check` 前统一执行，不再只在 G-C1/G-E2 局部实现。引用字段清单由 schema §2bis.1 的标注表生成，代码不维护第二份清单。 | schema 第 1.5、2bis 节；原型 `validate_references()` / `REFERENCE_RULES` |
| P5 | `assumption` 表示为对象 `{verification_condition, status, verified_at, expires_at, approved_by, approval_basis}`；`expired`、或 `pending` 且缺 `approved_by` → `cannot_evaluate` / `assumption_unclosed`；未满足验证条件的变更不得出现在 `approval_basis` 中。 | schema 第 1.9、2 节；`ALL_IMPROVEMENT_ASSUMPTION`、`AI_AUTONOMY_DELEGATION_AUDITABLE` |
| P6 | 链式条件用路径表示 `{start, steps: [{relation, direction, target_type, target_id}], reach}`，`steps[]` 必须带目标 `id` 才能定位下一节点；判定列写路径表达式，不再使用“终至”“链上有”等自然语言，也不再保留 `delegated_from` 扁平字符串写法。 | schema 第 1.10、3bis 节；G-E2 |
| P7 | 结论枚举扩为 `{pass, fail, cannot_evaluate, not_applicable}`；适用性状态机 `applicable / inapplicable / pending` 固定映射，`pending` 不得静默转 `applicable`。 | 方法 §4.2、§4.4；原型 `run_case` |

### 2.2 结构与对照（P1、P8、D0）

| 编号 | 决定 | 实现位置 |
|---|---|---|
| P1 | 规则正文的规范性条件拆为 **clause id**（`G-XX#n`），A 表“判定（子句 id）”列声明每个 `check_id` 覆盖的子句；verdict 由子句聚合（任一 `fail` → `fail`；否则任一 `cannot_evaluate` → `cannot_evaluate`），`severity` 取失败子句最高级，`reason` 取首条失败子句。 | 方法 A.2（41 个子句）；A 表“判定（子句 id）”列 |
| D0 | 采纳“子句级覆盖声明”。未覆盖子句必须标 `not-checked` 并写理由，不得留空。 | `scripts/check_three_table.py` 规则 4 |
| P8 | 三表机械对照作为**交付物**，由 `scripts/check_three_table.py` 承接，见第 3 节。检查深度限定为：结构一致（规则 ↔ `check_id` ↔ schema 输入域）、子句闭合、枚举封闭、判定列不含叙述性短语、G-B1/G-B2 条件归属、原因码定义与映射、A.2 签收同步；**不保证规则正文与子句表的全文语义等价**。 | 新增脚本 + pre-commit + `check_state.py` |
| A2-SIGNOFF | **A.2 的任何改动必须由非同源复核签收**：A.2 区头的“复核签收”行必须携带当前 A.2 区段指纹（全部子句指纹按 clause id 排序后的 sha256 前 12 位）。只改 A.2 再跑 `--write` 会重建自洽的 A 表，派生一致性检查无法识别，因此由规则 8 阻断签收指纹不一致的提交；签收人资格复用 3.6.6 的非同源语义。 | 方法 A.2 区头；`scripts/check_three_table.py` 规则 8；`AGENTS.md` 第 3.6.7 条；`scripts/test_check_table_mutations.py` S01/S02 |
| G-004 | `G-E1#3`（角色重合声明缺失）子句 severity 为 `warn`，不再与问责结构缺失同按 `block` 判死。 | 方法 A.2；原型 `check_role_minimal` 返回 severity 覆盖 |

### 2.3 逐点待决项结论（D1–D9）

| 编号 | 结论 | 影响的文件 |
|---|---|---|
| D1 | **全称 + 全解析**。顶层域每个元素都须满足；引用字段列出的每个目标都须解析；G-A1 的“至少一个 `Commitment`”由集合非空表达，不引入第二种量词写法。 | schema 1.6；G-A1 |
| D2 | **三态**：缺键/`null` → `cannot_evaluate`；`{}` → 对象存在但字段缺失 → `fail`；`[]` → 空集合按量词（全称真、存在假）。 | schema 1.3 |
| D3 | **悬空 = `fail`**（引用完整性违规）；**类型未定义 = `cannot_evaluate`**（缺表示能力，不是事实违规）。 | schema 1.5；原型 |
| D4 | `reason` 保持**单值**；聚合顺序定为 **`fail` > `cannot_evaluate` > `pass`**：任一子句 `fail` 即判 `fail`，不存在 `fail` 时才由 `cannot_evaluate` 决定；同一 verdict 内按 A.2 行序取首条。schema §1.14 与 A.2 统一为本条，删除“`cannot_evaluate` 优先于 `fail`”的旧表述。 | schema 1.14；方法 A.2 |
| D5 | `about` **构成** G-C1 的出边：见证断言可由 `asserted_by` 正向或 `about` 反向满足；但被引用断言仍须满足内容与相关性。 | schema 3bis；`DELIVERABLE_ASSERTION_LINK` |
| D6 | G-C1 **纳入**断言内容检查：`statement` 非空、`statement_kind ∈ {what, state, condition}`、`about` 指向该交付物。原样例 A.1.3-2 的“空断言仍 `pass`”期望被推翻。 | 方法 A 表、A.1.3、原型 |
| D7 | G-D1 **纳入** `target.type ∈ {Commitment, Deliverable}` 且 `target.id` 解析；缺 `target` → `missing_change_target`，越界或解析失败 → `invalid_change_target`。 | schema 3bis、A.1.4、原型 |
| D8 | G-001 三处未定义判定对象**在 schema 定义**：`management_node_type`（`ManagementActivity` / `ManagementArtifact`）、`approval_basis` 关系、`decision_class` 谓词；不再走 `doc-only`。 | schema 2、4 节 |
| D9 | G-002、G-003 **纳入**判定列：`G-A1#6`（约束须作用于该 `Outcome` 或 `Commitment`）、`G-E2#3`（自治断言须为 `assumption` 且附验证条件）。 | 方法 A 表、A.1.1、A.1.10 |

**缺口处置**：上一轮曾把 G-001–G-007 全部以 `check-change` 关闭，并把 P1–P8 合并为 G-008 关闭。该关闭已于 2026-11-14 被非同源复核重跑推翻：**关闭状态全部撤回**，G-001–G-008 回到 `open`，剩余缺陷拆为 G-009–G-017（见 `GAP_LEDGER.md`）。本轮修订不再宣称任何缺口已关闭；关闭必须由非同源复核或人工逐条签收（`AGENTS.md` 3.6.6）。

## 3. 三表机械对照（P8 交付物）

**承接检查器**：`scripts/check_three_table.py`（纯标准库，退出码 0/1/2）。

**覆盖的两两关系与闭合检查**：

| 编号 | 对照 | 判定 | 失败后果 |
|---|---|---|---|
| R1 | 正文 ↔ 判定列 | `GRAMMAR.md` 的每条规则都有承接 `check_id`；判定列的 `source_rule` 都存在 | 报错退出 1 |
| R2 | 判定列 ↔ schema | `check_id` 集合双向一致；判定列引用的字段名在 schema 中出现 | 报错退出 1 |
| R3 | 正文 ↔ schema | 规则陈述中的机制术语（如 `Actor`、`ProjectCharter`）在 schema 或术语表已定义 | 报错退出 1 |
| R4 | 子句闭合 | A.2 的每个 clause 被某个 `check_id` 覆盖，或标 `not-checked` 并写理由；A 表引用的 clause 必须存在 | 报错退出 1 |
| R5 | 枚举封闭 | 判定列中的小写枚举集合 ⊆ schema 第 4 节具名枚举 | 报错退出 1 |

**阻断路径**：`.githooks/pre-commit` 作为第 6 个检查器运行；`scripts/check_state.py` 在发布前调用，非零退出转为发布阻断（与缺口台账同一条路径，不新增平行机制）。

**已知局限（明确写入，不隐瞒）**：R1–R5 是**结构级**对照（存在性、集合一致、词级定义），不做语义等价判断。语义层仍由独立复核承担；“三表通过”不等于“判定列忠实于正文”。这一局限是 ADR 的正式结论，不是待办。

## 4. 设计层风险（判断，不是可能性罗列）

**4.1 两表结构天然漂移——判断：是，结构性缺陷。** 规则正文是自然语言合取、析取、量词与例外，判定列是人工维护的谓词清单，二者没有生成关系也没有覆盖声明；34 个样例同时当规格和测试，把漂移固化成“实现与样例互相证明”。本 ADR 的 D0/A.2 只把“漏掉子句”变成可机械发现的错误，不改变“两套表示各自维护”的事实。真正的根治是“正文子句与判定列同源生成”，成本超出 M2，列为 M3 的候选，不在此承诺。

**4.2 schema 表达力——判断：已从“不能承载”提升到“能承载但受词级约束”。** 量词、空值三态、关系路径、封闭枚举、assumption 时效、路径可达性已写入 schema；但 schema 仍是扁平谓词快照，不能表达递归、否定与时间序。G-007 的五点属于旧表达缺陷的显影，现已消解；若出现需要递归或时间逻辑的条件，应新增表示而不是继续塞进扁平字段。

**4.3 检查项粒度——判断：以子句为单位的聚合是当前最优折中。** 不重划 17 个 `check_id`（会推翻 34 个样例），但子句级 severity 与 reason 让“一规则一句”的压缩问题可被定位。新增条件一律先加 clause，再决定是否提升为新 `check_id`；禁止无 clause id 的条件进入判定列。

**4.4 是否可收敛——判断：可以，判据改为“同源缺口零新增”。** 本 ADR 后 7 条缺口全部关闭；但若下一轮仍出现“正文有条件、判定列无 clause”的缺口，说明 A.2 的覆盖纪律未被遵守，而不是缺口总量问题。以此作为 M2 的可判定判据。

## 5. 裁定后的单次复核

**执行顺序**：本 ADR 一次改动 → 原型重跑 34/34 → 三表检查器通过 → 由复核会话对新判定列与 schema **只重跑一次**复核。

**本次已执行的重验（同源，不冒充独立复核）**：

- 原型：34/34（100.0%），17/17 `check_id` 全通过；`COVERAGE_GAPS` 为空。
- 三表：17 规则 / 17 `check_id` / 39 子句 / 17 输入域一致，退出 0。
- 原复核的 6 个样例：G-A1、G-C1、G-D1 的判定路径全部改变（新增约束作用边、断言内容与 `about`、`target` 类型），A.1.3-2 与 A.1.4-2 的输入/期望已按新判定更新。

**复核结论是否仍然成立**：**不成立。** 上一轮把“原型 34/34”与“三表检查器退出 0”当作裁定成立的证据，但两者都是同源结果：样例与判定列同批修改，实现与样例互相证明；三表检查器只做结构级对照，不检查语义短语（G-B1 的“值在枚举内”与 A.2 划给 B2 的冲突仍报通过）。非同源复核重跑据此推翻了 `accepted` 状态。本 ADR 不再把任何同源重验当作证据；修订完成后只重跑一次非同源复核，其结论记入 `GAP_LEDGER.md`。

## 6. 替代方案

1. **分两次裁定、两次改冻结文件**：拒绝。D0–D9 与 P1–P8 互相改写彼此的写法（例如 P1 的子句表决定 D6/D7 的落点，P3 的关系路径决定 D5/D6 的写法），分批必然返工，且会让复核跑两次。
2. **保持“逐条补判定列”**：拒绝。G-007 已证明同一表达缺陷会以多个编号反复显影。
3. **用 `doc-only` 降级换取快速清零**：拒绝。G-001/G-005/G-006 的条件是可判定的，降级等于把已知缺陷永久留在正文里；ADR-0012 的撤除条件将永远无法满足。
4. **把三表对照留给人工**：拒绝。P8 要求机械承接；人工对照无法在每次提交上执行。
5. **重划 17 个 `check_id` 的粒度**：拒绝。收益低于推翻 34 个样例与复核基线的成本；改用 clause 聚合。

**三表检查器的深度边界**：`check_three_table.py` 只保证“结构 + 已列举的语义短语规则”一致。它能发现规则未映射、`check_id` 无判定行、子句未闭合、枚举值越界、判定列写叙述、G-B1 越权写枚举、原因码未定义或与子句不一致；它**不能**判断一条子句的自然语言条件是否忠实于规则正文的完整含义。因此绿字不等于语义闭合：语义闭合只能由非同源复核或人工逐条签收确认（`AGENTS.md` 3.6.6）。此前把该脚本退出 0 当作“语义闭合”的证据，正是首轮裁定失效的原因之一。

## 7. 后果

### 正面

- 判定层有了可机械校验的表示规范：枚举封闭、量词显式、路径表示、统一引用完整性、assumption 时效、`not_applicable`。
- 三表漂移从“只能人工发现”变为“每次提交可发现”（结构级）。
- M2 的出口从“补齐 17 项”改为“表示层可判定条件”，不再依赖复核进度。

### 负面

- 样例 A.1.3-2、A.1.4-2 的输入与期望被修改；原型 34/34 的含义从“独立验证”降为“与新判定列一致”，必须靠一次独立复跑补回证据。
- A.2 的 39 个子句增加维护成本；新增规则条件必须先登记 clause，否则三表检查器报错。
- R1–R5 是词级/结构级对照，不能保证语义等价；语义复核仍是必需环节。
- `severity` 现在可能来自子句覆盖（如 `G-E1#3` 的 `warn`），`validation/CHECKLIST.md` 的 severity 列表需与 A.2 同步。

### 跟进

- T-133：修订完成后由复核会话对新判定列与 schema 只重跑一次非同源复核；结论写入 `GAP_LEDGER.md` 核查记录，并作为 G-001–G-017 的关闭依据。
- T-100：随 G-004 重开，待判定列格式与原因码修正后由非同源复核关闭。
- ADR-0012：台账机制保留；撤除条件不满足（`open` 不为 0），观察期暂停。

## 8. 修订记录（2026-11-14，非同源复核推翻首轮裁定）

### 8.1 上一轮裁定为什么失效

首轮 `accepted` 建立在两项同源证据上：原型对同批修改的样例通过 34/34；`check_three_table.py` 退出 0。二者都不能证明判定列忠实于规则正文：

1. **样例与实现同源**：样例和判定列在同一提交内修改，原型再按修改后的样例求值，一致性只说明实现跟上了新判定列。
2. **检查器只做结构对照**：`check_three_table.py` 检查存在性、集合一致与词级定义，不做语义短语检查；G-B1 判定列仍写“值在枚举内”、A.2 又划给 B2，检查器仍报通过。
3. **P4/P6 未真正落地**：引用完整性只在 C1/E2 局部实现；路径结构缺目标 `id`，且保留 `delegated_from` 扁平字符串，形成双轨。
4. **P1/P2/P3/P5 只部分解决**：A 表判定列仍有叙述性短语；`subject_group` 只物化 2/17；`assumption.pending` 分支未检查 `approved_by`；17 处 `null` 输入会抛 `TypeError`。

### 8.2 本次修订范围

按用户批准的固定顺序执行，**顺序不得颠倒**：

1. **原型**：必需键取 `null` → `cannot_evaluate`；引用完整性全局生效；`assumption.pending` 检查 `approved_by`。
2. **schema**：§1.10 路径补 `target_id` 并删除扁平字符串写法；`subject_group` 17 项完整物化；§1.14 与 A.2 的聚合优先级定为 `fail > cannot_evaluate > pass`。
3. **判定列格式**：A 表“判定”列只留子句 id，叙述下沉 A.2；A.2 增加“原因码”列并定义原因码与子句的映射。

### 8.3 状态与关闭

- 本 ADR 回到 `proposed`；G-001–G-008 重开；新增 G-009–G-017 登记为 `open`。
- 修订完成后只重跑一次非同源复核；复核结论未到之前，任何缺口不得关闭，也不得以“原型通过”“检查器退出 0”作为关闭依据（`AGENTS.md` 3.6.6）。

### 8.4 第二轮修订：四层顺序（已完成，待非同源复核）

用户要求按层次修，不按单项打补丁。每层完成即报实测数字与负例。

1. **第一层（已完成）**：`run_case` 入口 `find_null()` 一次覆盖顶层键、嵌套对象键、数组元素三种 `null`；命中即 `cannot_evaluate` / `missing_input`，17 个 `check` 函数不再各自兜底。`--null-sweep` 改为路径级扫描，覆盖样例中全部非空数组（89 个数组元素用例 / 54 条 `(check_id, 路径)` / 27 条唯一路径）。
2. **第二层（已完成）**：§2bis.1 是 `REFERENCE_RULES` 的唯一生成源；§2bis.2 显式登记非引用字段；§2 每个字段必须被二者之一覆盖，新增字段未标注即三表检查器退出 1。补齐 `contracts[].accountable_signature` 与 `changes[].assumption.approved_by`。§3 必需顶层键同步为解析引用所需的集合（43 个 `(check_id, 键)`），原型 `REQUIRED_KEYS` 亦从 §3 生成；`--input-domain` 校验样例中的引用目标集合全部已声明。
3. **第三层（已完成）**：A 表改为 7 列（`check_id | 规则 | 判定（子句 id） | 子句指纹 | 输入 | 原因码 | 规则状态`），只由 A.2 派生；A.2 增加第 8 列 `规则状态`。`scripts/check_three_table.py` 的 `--write` 是唯一生成路径，默认模式逐格比较“文件 A 表”与“A.2 生成结果”，不再做两表字段互比。子句指纹覆盖 clause id / 规则 / 子句文本 / 原因码 / 承接 `check_id` / severity / 规则状态，任一语义改动都会破坏一致性。新增 `scripts/test_check_table_mutations.py`：固定 11 条变异（子句语义、量词、原因码删除/篡改、枚举归属 ×2、承接规则、子句 id、severity、规则状态、子句删除），逐条调用检查器并要求退出 1；实测 11/11 抓到。A.1 区新增“样例基线”表，锚定提交 `1a42b8b`、34 个样例、输入块改动清单，期望输出零改动。
4. **第四层（已完成）**：`subject_group_extension` 定义为 `{value, relation ∈ {specializes, cross_cuts}, base}`，`base` 必须是 17 项基础枚举，`value` 不得重名；A.2 新增 `G-B2#2`（`invalid_subject_group_extension`），只写 `{value}` 不再通过。悬空引用选择“规则子句原因优先”：A.2 新增归属表，只有 `G-C1#1`、`G-E2#1`、`G-E2#3` 可返回 `dangling_reference`，其余子句返回自己的原因码，无子句承接的引用由 `validate_references()` 兜底。`violations[]` 选择撤除：schema §1.14 明确原型不输出该字段，`reason` 为 A.2 行序首条命中。`G-A2#2` 通过给 `commitments[]` / `deliverables[]` 增加可选 `node_type` 变为可达；非法值 → `cannot_evaluate` / `undefined_object_type`，未提供不触发。实测 34/34、null-sweep 138/138、input-domain 0 缺口、三表退出 0、变异 11/11、七个检查器退出 0。G-001–G-017 仍为 `open`，只重跑一次非同源复核。
5. **提交前补漏（A.2 签收纪律）**：派生检查无法识别“改 A.2 再 `--write`”的绕过，故新增 `AGENTS.md` 3.6.7、决策表 `A2-SIGNOFF`、A.2 区头“复核签收”行与 `check_three_table.py` 规则 8；只改 A.2 不更新签收 → 退出 1，改 A.2 并更新签收 → 通过。S01/S02 正负例固定于 `scripts/test_check_table_mutations.py`。这是补漏，不改变第四层的任何裁定。

