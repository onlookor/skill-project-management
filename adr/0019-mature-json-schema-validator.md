# ADR-0019: 用成熟 JSON Schema 实现替换自写校验子集

- **状态**：accepted
- **日期**：2026-11-15
- **决策者**：用户（2026-11-15 裁定“把自写的 JSON Schema 校验子集换成成熟校验器”，基线 `f049f28`）
- **serves_charter**：C6（知识可检索、规则可检查）
- **grounding_refs**：无（治理自身的决策）
- **affected_files**：`scripts/check_no_raw_material.py`（校验入口与散文配额解析）；`scripts/check_dependency_pins.py`、`scripts/test_dependency_pins.py`、`scripts/dependency-pins.json`（新增）；`contracts/schema/`（保持内容契约不变，递归发现与元 schema 校验）；`spec/ACCESS_ZONES.md`（数据登记与本体规则说明）；`scripts/README.md`、`.githooks/pre-commit`（依赖安装与检查链）；`TODO.md`（T-146）；`CHANGELOG.md`

## 背景

`CONSTITUTION.md` 13.3 要求数据区文件按 `contracts/schema/*.schema.json` 校验。该能力由 `scripts/check_no_raw_material.py` 内的自写 `validate()` 承担，只覆盖仓库当时用到的关键字。

第三、四轮外部复核（基线 `3664b64`、`f049f28`）证明自写子集存在结构性失真：

- `items: true` 与元组 `items` 让数组元素绕过值约束；
- `enum` / `const` 命中时提前返回，同级的 `maxLength` 被跳过；
- `$ref` 曾忽略同级断言，`oneOf` 曾按 `anyOf` 处理；
- `x-prose-fields` 的路径拼错后静默失效，配额看似存在、实际不生效；
- `contracts/schema/` 只做单层枚举，子目录中的 schema 既不 lint 也不钉扎。

这些问题不是漏了某个关键字，而是“我们自己实现了一个语义标准”。每补一个关键字，就新增一处可能与规范偏离的解释；复核者必须同时审查 JSON Schema 规范与我们的实现，才能判断校验是否成立。这使第 13.3 条的阻断不可复核。

## 决定

数据区与 schema 自身的校验改用成熟实现 `jsonschema`（固定 `4.26.0`），并把版本、分发产物 sha256 与安装树摘要登记进指纹机制（`scripts/dependency-pins.json`，由 `scripts/check_dependency_pins.py` 核对）。自写 `validate()` 退役；对外输出契约不变。

**本 ADR 只批准“校验语义”的外部依赖，不批准任何数据与证据的外部依赖。** `contracts/schema/` 的内容、`knowledge/` 条目、本体、复核记录与来源登记仍必须自包含在仓库内；不得以“依赖库会处理”为由把数据、证据或判据移出仓库。

## 考虑过的替代方案

1. **继续扩充自写子集**：补齐 `items` 的布尔/元组形态、`enum` 与断言的合并语义、`oneOf` 排他、`if/then/else`、`patternProperties` 等。拒绝理由：这是把“实现 JSON Schema”当成产品功能。每轮复核都会产生新的关键字缺口，且缺口只能靠“又发现一次”来暴露；本次 r4 的四类缺陷正是这种模式的产物。自写的测试通过只证明“我们按自己的理解正确”，不证明“按规范正确”。
2. **改为代码校验函数**（为每份数据文件写 Python 校验函数）：可读、可调试，但把契约从声明式降为过程式。schema 文件与数据登记表将不再是唯一事实来源，新增数据文件必须先写代码，无法由 lint 与钉扎机械核对“契约是否完整”；同时会绕开 `x-prose-fields` 这类可被指纹覆盖的声明。拒绝理由：治理成本更高、可复核性更低。

## 自包含原则的例外范围

- **只覆盖校验语义**：`jsonschema` 只决定“一条 schema 如何解释一条数据”。它不接触数据内容、不生成证据、不替代复核，也不进入任何判定链的输入端。
- **不覆盖数据与证据**：`contracts/schema/` 的 schema 文本、`knowledge/` 条目、`ontology/`、`validation/reviews/` 与 `SOURCE_LEDGER.md` 仍全部在仓库内，且仍由仓库内检查器与钉扎保护。
- **不改变失败方向**：依赖缺失、导入失败或版本/指纹不符时，`check_no_raw_material.py` 必须以“无法评估”退出 2 并给出安装命令，不得降级为跳过校验，也不得只警告后继续。
- **可替换性**：校验入口只依赖 `jsonschema` 的 `Draft202012Validator` 与 `check_schema` 两个公开接口；替换实现只改一处适配层，不触碰输出契约（reason code、文件路径、JSON 指针、退出码）。

## 撤销条件与退回档次

满足任一条即启动撤销评审：

1. 目标运行环境无法安装或导入固定版本的 `jsonschema`，且用户拒绝引入该依赖；
2. 依赖的分发产物或安装树连续两轮无法核对（指纹机制失效）；
3. 上游实现不再支持 JSON Schema 2020-12 元 schema 校验。

退回按三档，逐档显式登记，不许静默降级：

- **A 档（首选）**：换用另一个成熟实现（同版本锁定 + 同指纹机制），输出契约不变。
- **B 档**：恢复自写子集，但只允许实现 `contracts/schema/` 实际用到的关键字，并在 schema lint 中把未实现关键字判死；任何新增关键字必须同批补实现与负例。
- **C 档（最后手段）**：对该数据文件判“无法评估”，退出 2 并阻断提交，直到依赖恢复。绝不退到“跳过校验”。

## 结果

### 正面

- 校验语义由规范实现承担，`items` 布尔/元组、`enum`/`const` 与同级断言、`oneOf` 排他等问题由结构消除，不再依赖逐轮补洞。
- schema 自身用官方元 schema 校验，schema 写错即失败。
- 依赖被替换可被发现：版本、分发产物 sha256 与安装树摘要三重核对。

### 负面

- 引入一个仓库外运行时依赖，破坏“零外部依赖即可运行”的旧假设；已在 `scripts/README.md` 与根 `README.md` 写明安装步骤。
- 指纹对安装树敏感：升级 `jsonschema` 必须同批更新 `scripts/dependency-pins.json`，否则 pre-commit 阻断。
- 分发产物不在本地时只能核对安装树（会给出警告），产物级核对需要设置 `JSONSCHEMA_WHEEL`。

### 需要跟进的事项

- `TODO.md` T-146：依赖接入、元 schema 校验、递归发现与 r4 攻击面验收。
- 撤销评审的触发条件由后续复核按本 ADR 检查；撤销时须新增 ADR，不得直接改本文件结论。
