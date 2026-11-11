# ADR-0002: 编译元框架与具体编译方法的分离

- **状态**：accepted
- **日期**：2026-11-11
- **决策者**：人类责任方（项目发起）
- **serves_charter**：C4（可选插件不构成完备性前提）、C6（知识可检索、规则可检查）
- **grounding_refs**：无（本决策是治理结构决策，不锚定外部来源）
- **affected_files**：
  - `spec/COMPILATION_META.md`（新建）
  - `spec/COMPILATION_METHODS.md`（新建）
  - `spec/methods/deterministic-checker.md`（下一轮交付）
  - `spec/COMPILATION_SPEC.md`（拆分后删除）
  - `CONSTITUTION.md` 第 5 条（保护清单新增 P1–P6 与编译方法可选择）
  - `README.md` 文件地图
  - `AGENTS.md` 第 4 条目录结构
  - `validation/CHECKLIST.md` 的生成依据声明
  - `CHANGELOG.md`、`TODO.md`

## 背景

v0.1 的 `spec/COMPILATION_SPEC.md` 混杂了两类内容：

1. **方法无关的编译纪律**：编译接口（成文法向编译施加的约束）、编译产物必须满足的性质（忠实性、可判定性、三值性、证据保全、自包含、假设与事实分离）、编译失败分类、与 PACT 的分工边界。
2. **方法有关的转换规则**：`check_id` 注册表、`severity` 映射、从规则陈述到检查条件的翻译规范（5.1–5.6）、v1 单层解析的宿主适配。

这种混杂在“只有一种编译方法”时不会暴露问题。但一旦考虑编译方法有多种可选（确定性校验器、PACT 规则、技能卡片、人类检查单、神经符号编译），它就无法回答三个问题：

- 换方法时，哪些内容**必须保留**？（方法无关的纪律）
- 换方法时，哪些内容**可以整体替换**？（方法有关的转换规则）
- 一种新方法要成为合法选项，**必须满足什么**？（准入条件）

这与“项目管理元框架 vs 领域技能”的问题同构：元框架定义“什么是合法的项目管理”，领域技能定义“特定领域怎么做”。编译域缺少前者。

## 决定

将编译相关的内容分为三层：

1. **`spec/COMPILATION_META.md`**：编译元框架（方法无关）。定义编译接口、编译产物必须满足的性质（P1–P6）、编译方法准入条件、声明格式、选择/共存/替换、失败分类、编译治理。类比：项目管理元框架。
2. **`spec/COMPILATION_METHODS.md`**：编译方法注册表。登记有哪些方法、当前启用哪个、为什么、替换历史。类比：领域技能注册表。
3. **`spec/methods/{method-id}.md`**：具体方法声明文件。每种方法用独立文件声明自己的定位、适用范围、运行时目标、忠实性论证、P2–P6 的满足方式、失败处理、版本纪律、无插件完备性。类比：具体领域技能。

原 `spec/COMPILATION_SPEC.md` 的内容：
- 方法无关部分（编译目标、severity 语义、grounded/assumption 分离、失败分类、与 PACT 的分工原则）→ 上收至 `COMPILATION_META.md`。
- 方法有关部分（check_id 注册表、翻译规范 5.1–5.6、证据七要素、检查清单生成规则、PACT 可映射/不可映射清单）→ 下沉至 `spec/methods/deterministic-checker.md`。
- 原文件**删除**；全仓库对 `spec/COMPILATION_SPEC.md` 的引用在下一轮统一更新。

同时修改 `CONSTITUTION.md` 第 5 条的保护清单，新增：

- 第 2 条（P1–P6）的约束强度；
- 第 3 条（编译方法准入条件）的约束强度；
- “编译方法可选择、可共存、可替换”这一基础约束。

降低这些约束的强度，等同降低 `CONSTITUTION.md` 的基础约束，需走第 5 条的特殊程序。

## 考虑过的替代方案

**替代方案 A：保留 `COMPILATION_SPEC.md` 作为单一文件，在文件内部分章节。** 拒绝理由：文件内部分章节不能解决“换方法时哪些内容必须保留”的问题——读者仍需逐段判断。分文件后，文件边界即纪律边界。

**替代方案 B：只拆出 `COMPILATION_META.md`，不建方法注册表。** 拒绝理由：方法注册表是“有哪些方法可用、当前用哪个、为什么”的唯一登记处。没有它，方法的启用/淘汰/替换会散落在各处 ADR 中，无法一眼看清。

**替代方案 C：把编译元框架并入 `CONSTITUTION.md`。** 拒绝理由：`CONSTITUTION.md` 是治理总纲，应保持精简（三权分立、来源封闭、自包含、可选插件）。编译元框架虽然也属于治理，但它足够特殊（方法可选择、有准入条件、有 P1–P6），值得独立。并入会使 `CONSTITUTION.md` 膨胀，且把“编译方法可选择”与“三权分立”混在同一层。

## 结果

### 正面

- 编译域的“元框架 vs 具体方法”分层与“项目管理元框架 vs 领域技能”同构，读者理解一处即可理解另一处。
- 换编译方法时，`COMPILATION_META.md` 不需要修改；只需新增一份 `spec/methods/{method-id}.md`，并在 `COMPILATION_METHODS.md` 登记启用。
- 一种新方法是否合法，有明确的准入条件（META 第 3 条），不再依赖“看起来合理”。
- 不可映射项的归宿有明确纪律（META 第 5.5 条），不再有“无人承担”的静默状态。
- `CONSTITUTION.md` 第 5 条的保护清单覆盖编译域的基础约束，防止编译方法的选择被降格为纯部署细节。

### 负面

- 文件数量增加；读者需要理解“元框架 / 方法注册表 / 方法声明”三层才能定位内容。缓解：`README.md` 文件地图标注层级；`COMPILATION_METHODS.md` 提供导航。
- `spec/COMPILATION_SPEC.md` 删除后，全仓库对它的引用需要更新。这是一个瞬时不一致状态，由 CHANGELOG 记录，下一轮统一修复。
- `validation/CHECKLIST.md` 的生成依据从 `COMPILATION_SPEC.md` 变为 `COMPILATION_META.md` + `spec/methods/deterministic-checker.md`，其文件头声明需要更新。

### 需要跟进的事项

- `TODO.md`：更新 T-011（检查器实现规格）的引用路径，从 `COMPILATION_SPEC.md` 改为 `COMPILATION_META.md` + `spec/methods/deterministic-checker.md`。
- `TODO.md`：新增工作项——编写 `spec/methods/skill-card.md`、`spec/methods/human-checklist.md`、`spec/methods/pact-rules.md`（候选方法的声明文件）。
- `TODO.md`：新增工作项——全仓库 `spec/COMPILATION_SPEC.md` 引用的统一更新。
- `CHANGELOG.md`：追加批次 0002，记录本次拆分。
