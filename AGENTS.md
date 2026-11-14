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

### 3. Schedule 纪律：ROADMAP.md、CHANGELOG.md 与 TODO.md

技能项目自身有三个**调度文档**，其存在不构成立法，但其纪律对本仓库的执行者具有约束力。三者分工固定：`ROADMAP.md` 回答“先做什么、做到什么算完”，`CHANGELOG.md` 回答“已经发生了什么”，`TODO.md` 回答“每个单点工作项现在什么状态”。

#### 3.1 CHANGELOG.md —— 变更历史的唯一登记处

- **登记范围**：规范层（`CHARTER.md`、`CONSTITUTION.md`、`GRAMMAR.md`、`SOURCE_LEDGER.md`）的任何实质变更；执行层（`spec/`、`contracts/`、`validation/`）中改变已有规则编译结果的结构性变更；知识层（`knowledge/`）条目的新增、删除或语义变更；`adr/` 中 ADR 的新增与状态迁移。
- **不登记**：错别字修正、排版调整、`README.md` 与 `AGENTS.md` 自身的措辞微调（除非改变其约束范围）。
- **格式**：按批次追加。每批包含：`{批次号, 日期, 涉及文件, 变更摘要, 关联 ADR 编号（若有）}`。
- **纪律**：**禁止改写已登记批次**。发现登记错误时，追加一条更正条目并引用原批次，不改原批次。批次号一经发布永不复用。批次号由发布里程碑统一分配；已占用但未形成条目的编号不复用（批次 0017 为既有先例）。
- **版本载体**：文件不写版本号、不携带版本头；包版本只有一个，以 annotated tag 声明发布点（ADR-0003）。外部引用读根目录 `manifest.json`。
- **与 ADR 的分工**：ADR 记录的是“为什么这样治理”；CHANGELOG 记录的是“什么时候、哪些文件、以什么批次被修改了”。一条实质性变更通常同时产生一条 ADR 和一个 CHANGELOG 批次；CHANGELOG 批次引用 ADR 编号，ADR 不引用 CHANGELOG 批次号（避免双向维护）。

#### 3.2 TODO.md —— 单点工作项台账

- **登记范围**：尚未完成的单点工作项，包括方法注册表种子条目填充、`pending_reanchor` 条目的重新锚定、`spec/` 尚未定稿的章节、样例契约的补充、验证套件的第一轮执行、已识别的缺口与待办。
- **不登记**：顺序、里程碑与出口条件（归 `ROADMAP.md`）；文件当前状态（归 `STATE.md`）；纯想法（想法先进入 `adr/` 的 `proposed` 状态，被接受后才进入 TODO 作为执行项）。已完成的工作不移出，保留行并标 `done`。
- **格式**：每条包含 `{编号, 里程碑, 性质, 治理路径, 前置依赖, 完成状态}`。编号一经分配续用，**不得删除条目、不得重排**；不再需要时标 `dropped` 并附理由。
- **状态取值**：`open` / `in-progress` / `blocked-external` / `done` / `dropped`。`blocked-external` 表示依赖仓库外条件（外部全文、第三方系统、人工发送等），必须在条目中写明解锁条件。该状态仅用于调度，不进入 `CONSTITUTION.md` 第 9 条的状态标记清单。
- **性质分类**：`规范层补丁` / `执行层补丁` / `知识层填充` / `样例与示例` / `验证` / `治理` / `发布`。每类对应的治理路径不同（规范层走 ADR，执行层走结构性变更判定，知识层走来源治理，样例走随样例更新，验证走结果登记，发布走 tag 与 CHANGELOG）。
- **纪律**：每项工作开始时登记状态为 `in-progress`，完成或放弃时更新状态并说明原因。**不得静默删除工作项**。顺序与出口条件以 `ROADMAP.md` 为准；两者冲突时先修 `ROADMAP.md` 的汇总，不改变单点状态。

#### 3.3 调度文档的写入权限

- **CHANGELOG.md**：任何执行者可在完成一次实质性变更后追加批次。追加即生效，不需批准；但如果对应变更本身需要 ADR（`CONSTITUTION.md` 第 4 条），则在 ADR 被 `accepted` 之前，CHANGELOG 批次标记为 `pending-adr`，不得声称变更已生效。
- **TODO.md**：任何执行者可登记工作项与更新状态。**关闭**（标记 `done`）需要附完成证据（对应的 CHANGELOG 批次号、ADR 编号或验证结果指针）。
- **ROADMAP.md**：交付方维护。里程碑的增删与顺序变更追加 CHANGELOG 后生效；里程碑内部的进度更新不记 CHANGELOG；关闭里程碑需附出口证据。

#### 3.4 ROADMAP.md —— 计划与验收的唯一登记处

- **登记范围**：目标与完成判据；里程碑的目标、工作项映射与可验证出口条件；关键路径与并行关系；发布点与定版。
- **不登记**：单点工作项状态（归 `TODO.md`）；文件当前状态（归 `STATE.md`）；已发生的变更（归 `CHANGELOG.md`）；现状诊断与决策理由（归 `adr/`）。
- **格式**：里程碑用 `M0`–`M7` 连续编号；每个里程碑必须写明出口条件，出口条件必须能由命令、文件或计数核对。
- **计划级动作**：里程碑内允许不分配 T 编号的计划级动作（整理、一次性命令、核对）；需要跨里程碑追踪的动作，必须在越过当前里程碑前登记为 `TODO.md` 条目，再在本文件引用。
- **纪律**：里程碑增删与顺序变更记 `CHANGELOG.md`；进度更新不记；关闭里程碑必须附出口证据（命令与结论、文件路径、计数）；不得静默删除里程碑，取消的里程碑标 `dropped` 并写明理由。本文件不承载版本号，发布点以 annotated tag 为准。

#### 3.5 发布态声明与开发态豁免

`manifest.json` 的 `release_state` 是发布闸门的**显式开关**，只允许两个值：

- `released`：最新 annotated tag 必须指向 `HEAD`；领先、落后或分叉均为错误。
- `development`：仍严格校验 tag 是否为 annotated、`release_tag` 与 `package_version` 是否和 tag 一致、tag 是否为 `HEAD` 的祖先；仅当 tag 是 `HEAD` 的祖先时，把“`HEAD` 领先于 tag”降为警告。分叉仍为错误。

纪律：

- **不得自动推断**。缺省（字段缺失）按 `released` 严格处理；非法值按结构错误（退出码 2）处理。不得根据分支名、提交数量或人工口头说明推断状态。
- 状态切换必须写入 `manifest.json` 并随提交生效，不得只改工作区。
- 发布提交的引导顺序固定：tag 只能指向已存在的提交，因此“把 `release_state` 改为 `released` 并递增版本”的提交需以 `git commit --no-verify` 提交，随后立即打 annotated tag 并运行五个检查器。其他提交不得使用 `--no-verify`。
- 发布点仍只有一个：以 annotated tag 声明（ADR-0003）；`development` 只说明 `HEAD` 领先于最近发布点，不产生第二个发布点。

##### 3.5.1 绕过留痕（硬要求）

`--no-verify` 的唯一合法用途是发布引导提交。git 不记录该标志（实测：提交对象只有 `tree` / `parent` / `author` / `committer` / `message`，没有任何钩子旁路标记），因此留痕改为固定 trailer，由 `check_state.py` 机械核查：

```
Hook-Bypass: release-bootstrap
Hook-Bypass-Reason: <为什么 pre-commit 无法通过>
Hook-Bypass-Verified: <tag 名；五个检查器的复跑结果>
```

- `v0.5.2` 及以后的发布提交必须齐备三项，且 `Hook-Bypass` 的值固定为 `release-bootstrap`；缺失任一项即错误。
- 非发布提交（`release_state != released` 或 tag 未指向 `HEAD`）不得携带该 trailer，携带即错误。
- `v0.5.1` 及以前为机制引入前的历史发布，不追溯、不回填。
- trailer 是权威留痕；`CHANGELOG.md` 对应批次以 `**钩子绕过**` 字段引用同一 tag，供人阅读，检查器不解析 CHANGELOG。

##### 3.5.2 撤除条件（可判定）

通道不能永久存在。目标：发布引导提交本身能通过钩子，取消 `--no-verify`。

- **方向**：发布点校验拆成两段。`check_state.py` 在 pre-commit 识别显式待发布声明——提交信息含 `Release-Target: <tag>`，且 manifest 为 `release_state=released` / `release_tag=<tag>`；目标 tag 尚不存在时只告警，不报错。`.githooks/pre-push` 运行严格检查：tag 必须存在、annotated、指向 `HEAD`，否则阻断推送。
- **关闭时点**：不晚于 `v0.5.2` 的发布提交；若 `v0.5.2` 仍使用 `--no-verify`，通道在该发布后立即冻结，下一次发布前必须先完成撤除。
- **关闭动作**：删除本条 `--no-verify` 例外（3.5 与 7bis 第 5 条）；新增 pre-push 钩子与待发布识别；移除 `Hook-Bypass` trailer 强制（历史提交保留）；`TODO.md` T-129 标 `done` 并记 CHANGELOG。
- **次数上限**：机制生效后最多允许 1 次豁免（即 `v0.5.2`）；第 2 次豁免即违规，必须先完成撤除再发布。

#### 3.6 缺口台账与裁定（临时机制）

**依据**：`adr/0012-gap-ledger-and-adjudication.md`。台账为 `GAP_LEDGER.md`，本条的规则只约束台账的登记、分级、到期与核查，不改变任何规则语义；它本身是临时机制，撤除条件见 3.6.5。

##### 3.6.1 入口：什么必须登记

以下三类情形**任一成立即必须登记**，不得只留在讨论、提交信息或临时台账里。判定标准必须能机械套用：

| 成因 | 机械判据 |
|---|---|
| `undefined-object` | 规则正文或判定列出现的节点类型、关系或字段名，在 `spec/INTERFACE_CONTRACT_SPEC.md` 与附录 A 的“输入”列中均无定义（取两处词表的并集，差集非空即登记） |
| `rule-stricter` | 规则正文按“且 / 或 / 除非 / 附带 / 不得 / 必须”切分后，存在规范性子句在判定列中没有对应谓词或参数 |
| `severity-mismatch` | 附录 A 的 `severity` 与 `validation/CHECKLIST.md` 同行不一致，或同一判定列同时容纳“声明缺失”与“结构缺失”两种应分级不同的失败情形 |

登记字段固定为：`编号 / 状态 / 成因 / 等级 / 影响面 / 是否阻断 / 待裁定方 / 登记里程碑 / 处置出口 / 关联 T / 说明`。编号 `G-NNN` 连续分配，不复用；关联的独立工作项保留原 `T-NNN` 编号，不合并。

**机械保证**：台账的核查矩阵必须逐行覆盖附录 A 全部 `check_id`，结论只能是 `consistent` 或缺口编号；任何对 `GRAMMAR.md` 或附录 A 判定列的改动，若未在同一提交更新 `GAP_LEDGER.md`，`scripts/check_gap_ledger.py --staged` 退出 1。人工判断仍负责“子句是否对应”，但“未复核”不再可能静默通过。

##### 3.6.2 分级与停留上限

| 等级 | 含义 | 最长停留 | 默认处置 |
|---|---|---|---|
| L1 | 阻断错判：合法产物被判失败或非法产物被判通过，且阻断工作 | 1 个里程碑 | `check-change` |
| L2 | 漏判：规则正文的条件未进入判定列 | 2 个里程碑 | `check-change` |
| L3 | 语义不可判定：规则引用未定义的判定对象，无法机械判定 | 2 个里程碑 | `doc-only` |

到期里程碑 = 登记里程碑 + 最长停留。**不允许无限挂账**：缺口必须在当前里程碑跨过到期里程碑之前被裁定，或显式降级一次。显式降级＝改写等级并在说明中写“降级理由：”，同时记 `CHANGELOG.md`；每条缺口最多降级一次。

##### 3.6.3 例行裁定点与到期后果

- **裁定点绑定里程碑**：`GAP_LEDGER.md` 头部必须写 `**当前里程碑**：M#`；推进里程碑时同步更新该字段。
- **到期未裁定**：`python3 scripts/check_gap_ledger.py` 退出 1；`check_state.py` 调用该检查器并把非零结果转为错误，从而阻断发布；pre-commit 同样阻断提交。
- **裁定记录**：处置出口与说明写回台账，`status` 改为 `closed`；关闭证据写入 `CHANGELOG.md`。

##### 3.6.4 处置出口

每条缺口关闭时只能落到以下四种之一，不允许“沉默”：

- `rule-change`：改规则正文，使其与判定列或输入 schema 一致。
- `check-change`：改判定列，使其覆盖规则正文。
- `doc-only`：降为文档约束，并在说明中明确写“不检查”。
- `accepted`：接受现状，说明中必须写“理由：”并附批准依据。

`check_gap_ledger.py` 对上述字段做枚举校验；`accepted` 缺“理由：”、`doc-only` 缺“不检查”、`open` 却填了处置出口均报错退出 1。

##### 3.6.5 机械核查与临时性

- **检查器**：`scripts/check_gap_ledger.py` 统计总数、按级计数、按到期计数，并输出核查矩阵的 `consistent` 比例；到期未裁定或结构非法时退出 1。`--staged` 额外要求规则/判定文件与台账同批暂存。检查器与其余四个脚本并列为第五个提交前检查器。
- **撤除条件**（全部满足）：连续两个发布点 `open=0` 且核查矩阵 17/17 为 `consistent`；第二个发布周期无新增缺口；裁定方完成一次全量“规则正文 ↔ 判定列”对照，确认无 `rule-stricter` 遗留。
- **硬约束**：不晚于 M3 关闭前评估撤除（`TODO.md` T-132）。M3 关闭时仍有 `open` 缺口则机制冻结：新增缺口须经 ADR，所有 `open` 缺口必须在 M4 前裁定。
- **撤除动作**：删除 `GAP_LEDGER.md` 与 `scripts/check_gap_ledger.py`；移除本条、7bis 的钩子项与 `check_state.py` 的调用；T-132 标 `done` 并记 `CHANGELOG.md`。

### 4. 目录结构（唯一权威）

本技能目录的完整结构如下。**本节是目录结构的唯一权威**；`README.md` 中的文件地图只是导航，与本节冲突时以本节为准。

```
project-management-grounding/
│
├── README.md                       # 入口导航：定位、文件地图（指针）、阅读路径
├── QUICKSTART.md                   # 快速开始：最小走查样例 + LLM 接合示例
├── ROADMAP.md                      # 计划与验收唯一登记处：目标、里程碑、出口条件、发布点（第 3.4 条）
├── AGENTS.md                       # 本文件：执行约定、目录结构权威、schedule 纪律
├── CHANGELOG.md                    # 变更历史唯一登记处（第 3.1 条）
├── TODO.md                         # 单点工作项台账（第 3.2 条）
├── ERRATA.md                       # 幻觉更正台账
├── GAP_LEDGER.md                   # 缺口台账（临时机制，第 3.6 条）
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
│   ├── ANCHOR_SPEC.md              # 锚点与引用规范：稳定 ID、标题路径、指纹、失效语义
│   ├── ONTOLOGY_FEASIBILITY.md     # 自建本体的可行性评估与方案对比（评估报告，非规范）
│   ├── CHECKER_INPUT_SCHEMA.md      # 确定性校验器的谓词快照输入 schema（T-107 起的新样例必须遵循）
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
├── ontology/
│   ├── README.md                   # 自建本体（active）：文件、格式、边界与检查规则
│   ├── pmbok8-vocab.ttl            # 92 类 / 35 对象属性 / 7 数据类型属性
│   ├── pmbok8-processes.ttl        # 7 域 / 5 焦点区 / 40 过程与 I/O
│   ├── pmbok8-artifacts.ttl        # 124 个工件个体
│   ├── pmbok8-tools.ttl            # 185 个工具与技术条目
│   ├── pmbok8-shapes.ttl           # 24 条 SHACL 形状
│   └── fixtures/                   # 1 个通过图 + 24 个违规图 + 清单
│
├── adr/
│   ├── README.md                   # ADR 格式说明（Nygard / MADR / Y-Statement）与必填治理字段
│   ├── ADR-TEMPLATE.md             # 治理决策模板（默认 Nygard 五要素 + 扩展字段）
│   ├── 0001-separate-grammar-from-governance.md
│   ├── 0002-compilation-meta-vs-methods.md
│   ├── 0003-version-and-state-governance.md
│   ├── 0004-artifact-baseline-by-commit.md
│   ├── 0005-source-ledger-scope.md
│   ├── 0006-knowledge-sources-vs-normative-basis.md
│   ├── 0007-anchor-discipline.md
│   ├── 0008-reanchor-dimension-rules.md
│   ├── 0009-no-raw-material-in-git.md
│   ├── 0010-self-authored-ontology-in-git.md
│   ├── 0011-schedule-layer-and-plan.md
│   └── 0012-gap-ledger-and-adjudication.md
│
├── .githooks/
│   └── pre-commit                  # 阻断原始资料入库（CONSTITUTION 第 13 条）
│
├── scripts/
│   ├── README.md                   # 辅助脚本目录说明
│   ├── check_glossary_sync.md      # GLOSSARY/JSONL 同步检查规格
│   ├── check_ledger_landings.py    # 来源编译落点检查（可运行）
│   ├── check_anchors.py            # 锚点解析与校验（可运行）
│   ├── anchor_baseline.json        # 规则/来源文本块的指纹基线
│   ├── check_no_raw_material.py    # 原始资料/OCR/成段原文的阻断式检查（可运行）
│   ├── check_gap_ledger.py         # 缺口台账结构、覆盖、到期与暂存同步检查（可运行）
│   ├── validate_ontology.py        # 本体与 SHACL 形状校验，含逐形状负例矩阵（可选依赖）
│   └── check_state.py              # STATE 与 git 跟踪文件的对账脚本（可运行）
│
└── validation/
    ├── CHECKLIST.md                # CM-DET-CHECKER 的产物：检查清单（生成依据见正文）
    ├── independent-review-package.md  # T-133 只读验收包（不含原型源码）
    ├── checker-prototype/
    │   └── checker.py              # T-107 最小原型：执行附录 A 的 34 个样例（纯标准库）
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
| `ROADMAP.md` | 交付方 | 里程碑、出口条件与发布点变化（第 3.4 条） | 里程碑增删与顺序变更追加 CHANGELOG；关闭需出口证据 |
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
| `spec/ANCHOR_SPEC.md` | 人类责任方 | 锚点形态、失效语义、指纹算法变化需 ADR；措辞澄清需 CHANGELOG | ADR；基线随规则/来源变更重冻 |
| `contracts/` | 交付方 | 槽位定义变化、样例更新 | 结构性变更需 ADR |
| `knowledge/` | 任何执行者 | 条目新增/变更（受 `CONSTITUTION.md` 第 2、3 条约束） | 随来源治理 |
| `ontology/` | 交付方 | 自建本体的内容与格式（受 `CONSTITUTION.md` 第 13.6 条约束） | CHANGELOG（内容/格式）；提升为来源或编译方法时需 ADR |
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
- **外部领域本体若存在**：作为**可选的语义扩展**，填充约束分类维度。**无外部领域本体时，约束分类退回通用分类（目标/环境/方案）**。领域本体与该领域技能的映射关系在对应领域的契约中（如 `contracts/examples/software-engineering.pm-contract.yaml`）以 `assumption` 形式存在，附带验证条件（与该领域技能原文一致），不冒充已确认事实。
- **任何领域技能若存在**：作为**横向对等体**，通过契约文件填充槽位。**没有任何领域技能享有特殊地位**；需求工程、软件工程、建筑施工与任何未来领域技能，都是可声明的槽位填充者。技能间的具体连接实例（如需求→软件的产物流动）登记在 `contracts/examples/` 或部署配置中，不进入成文法。

### 7bis. 原始资料与提取产物的存放与提交纪律

**依据**：`CONSTITUTION.md` 第 13 条。本条只规定执行层面的存放位置与操作顺序，不改变禁令本身。

1. **提取产物一律落在仓库外**。约定目录为 `/tmp/pm-extract-<source-id>-<date>/`，存放 `pdftotext` 文本层输出、`pdftoppm` 渲染图、Tesseract OCR 结果与任何逐页转储。**不得**落在仓库目录内，也不得放进 `resources/`。
2. **`resources/` 只在本地只读使用**。不复制、不打包、不 `git add`；`.gitignore` 已忽略 `resources/` 与文档类扩展名，但忽略规则不是许可。
3. **引用外部文献只写可复核的定位与自己的话**。默认写法是“页码定位 + 自述摘要”；确需引证术语或条款措辞时，单条不超过一行或一句，并附来源 `id` 与页码（见 `CONSTITUTION.md` 第 13.2 条）。
4. **提交前必须运行五个检查器**：`check_no_raw_material.py`、`check_anchors.py`、`check_ledger_landings.py`、`check_gap_ledger.py --staged`、`check_state.py`。本仓库已提供 `.githooks/pre-commit`，每个克隆需自行执行 `git config core.hooksPath .githooks` 启用；未启用钩子的部署必须在 `git add` 前手工逐个运行，等价命令见 `scripts/README.md`。
5. **检查器命中即停止提交**，不得用 `--no-verify` 绕过。唯一例外是第 3.5 条规定的发布引导提交（`release_state` 改为 `released` 并递增版本），该提交必须携带 3.5.1 的三项 `Hook-Bypass` trailer，并紧接 annotated tag 与五个检查器的复跑；该通道按 3.5.2 的撤除条件关闭（`TODO.md` T-129）。确需新增其他例外（例如将来要提交一张合法图片资产），走 ADR 并在检查器中登记路径豁免，而不是删除规则或放宽阈值。
6. **发现已跟踪内容违规时**：先报告文件与位置，再改为“页码定位 + 自述摘要”或移出仓库，并在 `ERRATA.md` 登记；不静默删除他人的内容。
7. **自建本体（`CONSTITUTION.md` 第 13.6 条）**：
   - 只放 `ontology/`；主格式为 Turtle（`.ttl`、`.shacl.ttl`），`.owl`/`.rdf`/`.nt`/`.n3`/`.jsonld` 仅作生成导出，仍受同一内容检查。
   - 每个文件头部必须写 `# self-authored: true`、`# source_id: <SOURCE_LEDGER id>`、`# source_pages: <定位>`；每个术语带 `dcterms:source` 与 `pm:sourcePage`。
   - 定义必须自写一句话；不得逐句对应原文，不得复制段落、列表、表格行、图注。写不出定义时省略定义并标 `definition_status: pending`，不得用原文改写凑数。
   - 本体是派生工件，不是来源；在 ADR 提升前不得作为 `grounding_ref`，不得直接充当规则依据；`STATE.md` 中状态为 `active`（形状与负例校验通过后）。
   - 提交前运行 `scripts/check_no_raw_material.py` 与 `scripts/validate_ontology.py --matrix`；本体文件命中 `RM-ONTO-*` 或 `RM-PROSEBLOCK` 同样阻断提交；缺少 `rdflib`/`pyshacl` 时校验以退出码 2 报“无法评估”。

### 8. 不做的事

- 不生成 `SOURCE_LEDGER.md` 未登记的 `grounding_ref`。
- 不在 `GRAMMAR.md` 中写入领域特有对象名。
- 不在任何项目文件中记录本次运行的临时台账（检索记录、调试输出、试验数据）——临时台账只存在于当次运行，实质性结果按第 3 条登记到 CHANGELOG 或 TODO。
- 不把“检查器沉默”当作“检查通过”。
- 不以“更合理”“最佳实践”“业界共识”作为来源。
- 不在没有 ADR 的情况下修改 `CHARTER.md`、`CONSTITUTION.md`、`GRAMMAR.md`、`SOURCE_LEDGER.md` 的实质内容。
- 不静默删除 TODO 工作项；不改写已登记的 CHANGELOG 批次。
- 不在 `ROADMAP.md` 中登记单点工作项状态或文件状态。
- 不在 `TODO.md` 中定义里程碑顺序或出口条件。
- 不给任何领域技能设置“上游/下游”的特殊地位。
