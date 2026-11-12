# ADR-0007: 锚点稳定化——禁用行号、稳定 ID 与指纹基线

- **状态**：accepted
- **日期**：2026-11-12
- **决策者**：用户（人类责任方）提出锚定方法问题并要求取证后落地；执行方盘点、设计并实现检查器
- **serves_charter**：服务于 C3（来源封闭、可追溯）与 C6（可机械检查、可审计）
- **grounding_refs**：无（治理决策）
- **affected_files**：`spec/ANCHOR_SPEC.md`（新建）、`scripts/check_anchors.py`（新建）、`scripts/anchor_baseline.json`（新建）、`CONSTITUTION.md` 第 3.1、4、7.3 条（失效引用修复）、`GRAMMAR.md`（失效引用修复）、`validation/CHECKLIST.md`（失效引用修复）、`spec/ASSUMPTION_PROTOCOL.md`（失效引用修复）、`spec/INTERFACE_CONTRACT_SPEC.md`（失效引用修复）、`spec/COMPILATION_METHODS.md`（失效引用修复）、`spec/methods/deterministic-checker.md`（失效引用修复）、`TODO.md`（T-070 完成）、`scripts/README.md`、`AGENTS.md`、`README.md`、`CHANGELOG.md` 批次 0014

## 背景

用户报告：软工技能早期按绝对行号锚定，文件插入一行后，插入点之后的锚点全部错位。要求判断本项目是否需要同样的锚定改造。

盘点结果（2026-11-12，只读扫描 38 个 Markdown 文件）：

| 锚点类别 | 形态 | 位置 | 插一行后是否失效 |
|---|---|---|---|
| 规则 | `G-A1` … `G-G3` | `GRAMMAR.md` 17 条规则标题 | 否 |
| 检查项 | `check_id`（`PROJECT_MINIMAL_EXISTENCE` 等） | `validation/CHECKLIST.md`、`spec/methods/deterministic-checker.md` 附录 A | 否 |
| 知识条目 | `term` | `knowledge/anchored-entries.jsonl` | 否 |
| 方法 | `M-*` | `knowledge/methods/registry-skeleton.md` | 否 |
| 来源 | 来源 `id` | `SOURCE_LEDGER.md` 7 个 active 条目 | 否 |
| 术语 | `T-A-001` 等 | `GLOSSARY.md` 术语标题 | 否 |
| 待办 | `T-NNN` | `TODO.md` | 否 |
| ADR | `ADR-000N` | `adr/` 文件名 | 否 |
| 章节引用 | `` `文件.md` 第 N 条/节 `` | 全仓 236 处 | 否（重编号才失效） |
| 标题路径 | 目前无实际使用 | — | 否 |
| **行号** | `文件.md:123`、`#L123`、`@m:123`、`第 123 行` | 仅 `adr/0006` 的 7 处历史证据 | **是** |

**关键事实**

1. **活跃文件没有任何行号锚点**。规则、检查项、来源、术语、方法、待办全部使用稳定 ID；编译元框架与确定性校验器只按 `第 N 条/节` 引用。插入一行不会使这些锚点错位。
2. **行号锚点是历史证据，且已经失效**。`adr/0006` 的 `SOURCE_LEDGER.md:19`、`SOURCE_LEDGER.md:143` 等写于来源表重写之前；今天按行号读到的已不是原条文。它们没有造成错误执行，因为 ADR 明写“行号指本决策之前的版本”，但这正说明行号不能承担定位。
3. **真正的问题不是行号，而是失效引用无人发现**。全仓有 11 处活跃文件引用已删除的 `spec/COMPILATION_SPEC.md`（`CONSTITUTION.md` 3 处、`GRAMMAR.md` 2 处、`validation/CHECKLIST.md` 2 处、`spec/ASSUMPTION_PROTOCOL.md` 2 处、`spec/INTERFACE_CONTRACT_SPEC.md` 1 处、`spec/COMPILATION_METHODS.md` 1 处、`spec/methods/deterministic-checker.md` 1 处历史注），另有计划中的方法文件被当作已存在引用。没有机械检查，所以拆文件后残留了整整一轮发布。
4. **既有口径已存在**：`/home/wgz/projects/skills/software-engineering/锚点与引用规范.md` 与 `ADR-ANCHOR-01` 已经确立“结构地址、行号禁用、指纹只作漂移检测、失效显式报错、冻结 as-of”五条原则。本项目应当复用原则，不另造语法。

## 决定

1. **定位只用稳定地址**：稳定 ID（规则/检查项/来源/术语/方法/待办/ADR）、章节号（`第 N 条/节`）、标题路径（`doc:<path>#sec-<标题>`）。行号、页码、字符偏移不得作为 locator。
2. **行号只作展示值**：解析器在运行时从文件现算行号，只出现在报错与人工定位信息里，不写入任何权威文件。`adr/`、`CHANGELOG.md`、`ERRATA.md` 中的历史行号按 as-of 冻结，检测器只提示，不计错误。
3. **被锚定文本加指纹**：`GRAMMAR.md` 每条规则块与 `SOURCE_LEDGER.md` 每个来源条目块，按“逐行去空白、丢空行、行内空白折叠”后取 `sha256`，写入 `scripts/anchor_baseline.json`。指纹只回答“这块文本变了吗”，不用于定位。
4. **失效必须显式报错**：`scripts/check_anchors.py` 输出封闭枚举（`E-FILE-MISSING`、`E-NO-TARGET`、`E-AMBIGUOUS`、`E-LINE-LOCATOR`、`W-FINGERPRINT-DRIFT`、`I-AS-OF`），退出码 0/1/2。禁止“取第一个匹配”式兜底。
5. **复用软工口径、不引入 `@` 语法**：本项目现有 236 处章节引用与全部稳定 ID 已经可读可解析；改写为 `@m:` 语法没有定位收益，只会制造迁移风险。未来若需要行内精确锚点（列表项、表行），直接采用软工的 `@` 语法与 `sec-`/`row-`/`li-` 子锚。
6. **补规范与检查器**：新增 `spec/ANCHOR_SPEC.md`（normative）与 `scripts/check_anchors.py`；后者同时完成 T-114 的 `grounding_ref` 闭环检查与 T-070 的残留引用修复复核。

## 考虑过的替代方案

1. **全量迁移到 `@m:` / `@d:` 语法**。拒绝：涉及 236 处章节引用与全部稳定 ID，收益仅是“形式统一”，成本是整仓改写与新的解析器；现有引用在插行场景下本来就稳定。
2. **保持现状，只靠人工评审**。拒绝：11 处失效引用已经证明人工评审漏检；失效引用存在性是确定性问题，适合机械检查。
3. **只用文本指纹，不用稳定 ID**。拒绝：软工实测同条款内前 12 字碰撞 295 处；文本只用于识别内容，不能标识身份。
4. **用 Markdown AST 生成指纹**。拒绝：引入解析器依赖后，解析器版本差异本身会成为新的失效源；空白规范化 + `sha256` 已足够检测漂移。
5. **把行号锚点全部改成“行号 + 指纹”**。拒绝：这仍然以行号为 locator，插行后必须整体重算；指纹只能事后报警，不能自动修复。

## 结果

### 正面

- 插行不再影响任何定位：稳定 ID 与章节号在插入场景下不变；指纹只对“被锚定块内容变化”报警。
- 失效引用从“发布后无人发现”变为“提交前显式失败”。首轮实跑即清出 11 处 `COMPILATION_SPEC.md` 残留与 1 处测试用例命名示例误报。
- 与软工技能共享同一套原则，后续若需要行内锚点可直接对齐语法，不再造第二套。

### 负面

- 规则与来源内容被有意修改时，必须重冻基线；忘记重冻会持续产生 `W-FINGERPRINT-DRIFT`。
- 指纹对“改一个字”和“整段重写”同样报警，不能替代人工判断改得对不对。
- 章节号在重编号时仍会失效；本方案只能保证“失效被报出来”，不能保证“编号永不失效”。

### 需要跟进的事项

- **T-116**：把 `scripts/check_anchors.py` 纳入提交前检查清单（与 `check_ledger_landings.py` 同批运行）。
- **T-117**：为 `SKILL.md`、`validation/test-cases/TC-*.md` 等尚未创建的引用建立计划项登记，避免长期以“示例/计划”身份存在。
