# 案例素材台账（MANIFEST）

依据 `adr/0020-case-material-handling.md`：案例素材不放 `SOURCE_LEDGER.md`；本目录存放改造后的场景事实与来源台账。只有由案例抽象出的评分判据才进来源登记表，并落在 `rule:` 或 `check:` 上。

## 1. 入库边界

1. **只存改造后的场景事实**：本目录下的 JSON 是为工件 schema 重写的活动、预算、风险、状态、EVM、审计记录，不是原文摘录。
2. **不存原文、原表、原图**：不复制报告正文、表格、图表或大段译文；需要复核时按下方 URL 回到公开来源。
3. **不伪装官方数据**：由公开总额/完成度推导的 EVM 标 `derived_not_official_evm`；缺公开三值的题不设 EVM 题。
4. **许可**：NAO 报告按 Open Government Licence v3.0；Parliament 页面按 Parliamentary copyright；仅改造事实，不复制表达。
5. **可复现**：每题的 `source_ref` 指向本台账条目；台账记录访问日期与核验状态。

## 2. 公开案例

| case_id | 机构 / 报告 | 报告号与日期 | 许可 | 访问日期 | 核验状态 | 已入库改造素材 | 对应题目 |
|---|---|---|---|---|---|---|---|
| `NAO-CROSSRAIL` | UK National Audit Office, *Completing Crossrail* | HC 2106，2019-05-03 | OGL v3.0 | 2026-11-16 | 摘要级已核实 | `validation/cases/NAO-CROSSRAIL/inputs/`（6 件，已运行：`phase2-public-crossrail`） | D6-PUB-01～06 |
| `NAO-UNIVERSAL-CREDIT` | UK National Audit Office, *Universal Credit: early progress*；*Rolling out Universal Credit* | HC 1123，2018-06-15；早期报告 2013 | OGL v3.0 | 2026-11-16 | 摘要级已核实 | `validation/cases/NAO-UNIVERSAL-CREDIT/inputs/`（6 件，已运行：`phase3-public-uc`、`phase6-contract-gaps`） | D6-PUB-07～11、D6-PUB-23 |
| `NAO-HS2` | UK National Audit Office, *High Speed Two reset* | 2026 年报告 | OGL v3.0 | 2026-11-16 | 摘要级已核实 | `validation/cases/NAO-HS2/inputs/`（7 件，已运行：`phase4-public-hs2`、`phase6-contract-gaps`） | D6-PUB-12～17、D6-PUB-24 |
| `NAO-NPFIT` | UK National Audit Office, *The National Programme for IT in the NHS: an update on the delivery of detailed care records systems* | HC 888，2011 | OGL v3.0 / Parliamentary copyright | 2026-11-16 | 摘要级已核实 | `validation/cases/NAO-NPFIT/inputs/`（5 件，已运行：`phase5-public-npfit`） | D6-PUB-18～22 |

**URL**：

- Crossrail: <https://www.nao.org.uk/wp-content/uploads/2019/05/Completing-Crossrail.pdf>
- Universal Credit: <https://www.nao.org.uk/wp-content/uploads/2018/06/Rolling-out-Universal-Credit.pdf>
- HS2: <https://www.nao.org.uk/reports/high-speed-two-reset/>
- NPfIT: <https://publications.parliament.uk/pa/cm201012/cmselect/cmpubacc/c1070-i/c107001.htm>

**改造说明**：

| case_id | 使用的公开事实 | 改造方式 | 局限 |
|---|---|---|---|
| `NAO-CROSSRAIL` | £14.8bn（2010）、£17.6bn（2018-12）、+£2.8bn、£12.5bn 已支出、93% 完成（2018-07）、9 座新站、每小时 24 列车 | 阶段→活动与 FS 依赖；资金包→成本工作包；完成度/支出→状态与推导 EVM；2018-12 开通→里程碑 due_day | 无承包商 EVM 三值；EVM 为推导值 |
| `NAO-UNIVERSAL-CREDIT` | 2013-02～05 重置、系统开发 >£300m 且无法评估价值、2020 预测 £2,850m、+£912m、完成推迟至 2028 | 重置→里程碑网络；成本→实施包+变更包；不可评估价值→`value=null` + `unavailable_reason` | 无分 WBS 公开明细；`due_day` 上限 3650 天，2028 目标（约 5475 天）无法表达，故不设里程碑期限；风险类别受 schema 闭集限制 |
| `NAO-HS2` | £87.7bn–£102.7bn、较 2020 翻倍、2023 取消 Phase 2、Euston 暂停两年、£1.5bn 已支出（2022-12） | 上界/下界→预算口径；取消→悬挂依赖负例；暂停→不可用进度指标 | 成本是区间，题内显式取上界并标注；风险类别按 schema 五类就近归类（G-025） |
| `NAO-NPFIT` | £11.4bn、项目提前关闭未实现目标 | 类别→成本包；关闭→审计记录；目标未达成→不可用指标 | 无分年度 EVM 三值；不设 EVM 题 |

## 3. 合成案例（用于边界与负例，不计入“公开案例改造”）

| case_id | 用途 | 输入 | 对应题目 |
|---|---|---|---|
| `SYN-DEP-POS` | 依赖图正例（显式零滞后、WBS 完整） | `validation/cases/synthetic/SYN-DEP-POS/inputs/dependency-graph.json` | D6-SYN-01 |
| `SYN-DEP-CYCLE` | 依赖图成环负例 | `validation/cases/synthetic/SYN-DEP-CYCLE/inputs/dependency-graph.json` | D6-SYN-02 |
| `SYN-DEP-NOWBS` | 缺 WBS 清单的不能判定例 | `validation/cases/synthetic/SYN-DEP-NOWBS/inputs/dependency-graph.json` | D6-SYN-03 |
| `SYN-BUD-POS` | 预算正例 | `validation/cases/synthetic/SYN-BUD-POS/inputs/cost-budget.json` | D6-SYN-04 |
| `SYN-BUD-TIMESUM` | 分时段求和不一致负例 | `validation/cases/synthetic/SYN-BUD-TIMESUM/inputs/cost-budget.json` | D6-SYN-05 |
| `SYN-RISK-POS` | 风险正例 | `validation/cases/synthetic/SYN-RISK-POS/inputs/risk-register.json` | D6-SYN-06 |
| `SYN-RISK-RESIDUAL` | 残余高于初始负例 | `validation/cases/synthetic/SYN-RISK-RESIDUAL/inputs/risk-register.json` | D6-SYN-07 |
| `SYN-STATUS-POS` | 状态正例 | `validation/cases/synthetic/SYN-STATUS-POS/inputs/status-snapshot.json` | D6-SYN-08 |
| `SYN-EVM-BUDGET` | BAC 与工作包合计不一致负例 | `validation/cases/synthetic/SYN-EVM-BUDGET/inputs/evm-record.json` | D6-SYN-09 |
| `SYN-AUDIT-SEQ` | 审计序号断档负例 | `validation/cases/synthetic/SYN-AUDIT-SEQ/inputs/audit-trail.json` | D6-SYN-10 |

## 4. 待办与未入库

- 公开案例的输入 JSON：Crossrail 6 件（批次 2）、Universal Credit 6 件（批次 3 与批次 6）、HS2 7 件（批次 4 与批次 6）、NPfIT 5 件（批次 5）全部建立并运行，24/24 就绪；本台账不再有待建输入，后续只做复核与（若有）重跑登记。合成题仍为 10 道，任务集共 34 题。
- Crossrail 成本/挣值件按 GBP 建立，运行需 `V-CFG09-GBP` 变体快照（主配置 CFG-09=CNY），变体题单列、不计入主运行；状态件不参与货币核对，其金额仍为公开报告的 GBP 数值，属未覆盖项（已在运行记录中标注）。
- 未核验到公开 EVM 三值的案例（NPfIT）不设 EVM 题；Crossrail 的 EVM 题标注为推导值，不冒充官方 EVM。
- 未纳入本批的候选源（F-35 GAO 报告等）因报告号/明细未在本次访问中核实，暂不入库，避免以未核验编号充作出处。
