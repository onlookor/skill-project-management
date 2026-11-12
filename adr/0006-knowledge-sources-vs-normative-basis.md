# ADR-0006: 区分知识来源与规范依据，并强制编译落点

- **状态**：accepted
- **日期**：2026-11-12
- **决策者**：用户（人类责任方）要求追到根上，执行方取证并落地
- **serves_charter**：服务于 C3（来源封闭、可追溯，且每条来源必须真正支撑编译目标）
- **grounding_refs**：无（治理决策）
- **affected_files**：`CONSTITUTION.md` 第 2 条（新增两类文献区分、字段表、第 2.1、2.6 条）、`SOURCE_LEDGER.md`（新增 `compilation_landing` 字段与 7 个 active 条目的落点）、`scripts/check_ledger_landings.py`（新建）、`scripts/README.md`、`AGENTS.md` 第 4 条目录树、`README.md` 文件地图、`CHANGELOG.md` 批次 0010、`TODO.md`

## 背景

来源登记表中曾收录 `Nygard-ADR-2011` 与 `RFC2119-1997`，二者都不支撑任何通用项目管理规则，却通过了当时的入表条件。取证如下（行号指本决策之前的版本）：

- `SOURCE_LEDGER.md:5`：“本表只登记**已核验**的来源。”——只要求“已核验”，没有要求“与通用项目管理相关”，也没有要求“该来源的论断会进入编译产物”。
- `SOURCE_LEDGER.md:19`：`claim_mapping` 定义为“本条目支持 `GRAMMAR.md` 或 `knowledge/` 中的哪些具体规则/条目”。字段措辞已经把范围限定在 `GRAMMAR.md` 与 `knowledge/`。
- `SOURCE_LEDGER.md:143`（Nygard 条目）：`claim_mapping` 实际写的是“`CONSTITUTION.md` 第 4 条（ADR 格式）；`adr/ADR-TEMPLATE.md` 的结构依据”——落点落在治理文件，不在编译产物，已经越过字段自身的范围，却未被拦截。
- `SOURCE_LEDGER.md:156-157`（RFC 2119 条目）：`allowed_uses` 为“`GRAMMAR.md` 与 `CONSTITUTION.md` 中规范性措辞的语义依据”，`claim_mapping` 为“`CONSTITUTION.md` 第 3 条；`GRAMMAR.md` 使用说明”。同样没有进入任何可检查的规则或知识条目。
- `CONSTITUTION.md:29`：只规定“`GRAMMAR.md` 中任何一条规则的来源锚定，必须指向登记表中已注册的 ID”，没有规定“登记表只能收会被 GRAMMAR 或 knowledge 使用的东西”。
- `CONSTITUTION.md:45-49`（原第 2.1 条）：新增条件只有“公开标准 / 同行评议工作 / 已接受的上游本体”三类，ADR 文章（业界实践文献）与 RFC 2119（IETF 标准）都能满足其中一类。
- `CONSTITUTION.md:53`（原第 2.3 条）：只有排除清单（厂商博客、非官方镜像、无关披露文件），没有正向的领域相关性测试。

**判定**：主因是**条文缺口**——缺少“领域无关 + 编译落点”的正向准入测试；并伴随**术语含混**——“来源”同时被用来指知识来源与规范依据；**执行偏差**是次要因素，Nygard 与 RFC 条目违反了 `claim_mapping` 字段自身的范围而未被发现，因为没有任何机械检查核对落点。

## 决定

1. **术语分层**：明确区分“知识来源”（进入 `SOURCE_LEDGER.md`）与“规范依据”（进入 `adr/README.md` 与 `CONSTITUTION.md` 第 3.6 条，不入表）。
2. **准入测试**：新增 `CONSTITUTION.md` 第 2.6 条，先做领域测试（是否通用项目管理），再做落点测试（是否进入 `GRAMMAR.md` 规则 / `knowledge/` 条目 / 方法条目 / 检查项），并在字段表中把 `compilation_landing` 列为必填字段。
3. **机械检查**：新增 `scripts/check_ledger_landings.py`，核对每个 active 条目是否有落点、落点记号是否合法、落点在对应文件中是否真实存在；`pending:` 记为警告。
4. **补齐现有条目**：为 7 个 active 条目写入 `compilation_landing`；`SPRINGER-PMBOK-2024` 因正文未获取，只能写 `pending:T-112`，由脚本报为待落点。

## 考虑过的替代方案

1. **只删除 ADR/RFC 两个条目，不改条文**。拒绝：删除只能消除这一次的混入，下一次同类文献仍可通过同样的条文缺口进入；用户明确要求追到根上。
2. **把 ADR 记法与 RFC 2119 登记在 `SOURCE_LEDGER.md` 的独立分区**。拒绝：这会让“封闭枚举”同时承载两种语义，`grounding_ref` 的合法取值再次失去一致含义；规范依据应当在其使用处就近声明。
3. **用人工评审代替脚本**。拒绝：这次混入正是人工评审漏掉的；落点存在性是确定性问题，适合机械检查。

## 结果

### 正面

- 来源表有了可执行的正向准入测试，不再依赖“看起来权威”或“不违反排除清单”。
- 每个 active 来源都能指向具体编译落点，`source → rule/knowledge/method/check` 的链条可机械核对。
- “来源”一词的两个含义被拆开，ADR 记法与 BCP 14 找到了正确的去处。

### 负面

- `compilation_landing` 与 `claim_mapping` 存在信息重叠，未来可能漂移。
- 脚本只能验证“落点存在”，不能验证“来源确实蕴含该规则”；后者仍需 `provenance_note` 与人工评审。
- `pending:` 只产生警告，不阻断；正文长期取不到时，条目会长期停留在“已登记但无落点”。

### 需要跟进的事项

- **T-114**：建立“文档中所有 `grounding_ref` 都指向登记表 active 条目”的闭环检查，与落点检查合并为一次运行。
- **T-115**：定期复核 `SPRINGER-PMBOK-2024` 的 `pending:T-112` 状态，避免长期无落点。
