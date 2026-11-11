## 反例检验用例库

**性质**：本目录存放 `spec/methods/deterministic-checker.md` 第 3.3 节所要求的反例检验用例。每个用例包含：规则编号、输入、预期结论、检验目的。用例执行通过是 `spec/GROUNDING_CRITERIA.md` G3 的必要条件。

### 1. 用例格式

每个用例是一个 Markdown 文件，命名规则 `TC-{规则编号}-{序号}.md`，例如 `TC-A1-01.md`。内容包含：

```markdown
# TC-{规则编号}-{序号}: {一句话说明}

- **规则**：G-XX
- **检验目的**：验证规则的哪一条子性质（正向对照 / 反向对照 / 量词边界 / 例外触发 / unknown 处置）
- **输入**：谓词/槽位快照
- **预期结论**：pass | fail | cannot_evaluate
- **预期原因**（fail/cannot_evaluate 时必填）：...

## 输入快照

（YAML 或 JSON）

## 判定过程（预期）

（逐条说明校验器应如何求值）

## 备注

（若有用例暴露的规格缺口，在此登记，并关联 ERRATA.md 编号）
```

### 2. 用例覆盖要求

- **每条 `active` 规则至少一个正向用例与一个反向用例**。
- **涉及量词的规则**（G-A1、G-A2、G-C1、G-D1、G-E1）必须含量词边界用例（空集 / 单元素 / 多元素）。
- **涉及例外的规则**（G-E1 的 `role_merge_declaration`、G-D2 的 `trades_off`/`exacerbates`）必须含例外触发用例。
- **涉及 `unknown` 的规则**（全部三值规则）必须含 `cannot_evaluate` 用例。

### 3. 当前已落盘的用例

| 用例 | 规则 | 检验目的 | 预期结论 | 状态 |
|---|---|---|---|---|
| `TC-A1-02.md` | G-A1 | 反向对照：缺 Constraint | `fail` | `active` |
| `TC-C1-03.md` | G-C1 | 量词边界：多 Deliverable，部分有 Assertion | `fail` | `active` |
| `TC-E1-04.md` | G-E1 | 例外触发：重合但缺声明（暴露 E-004 缺口） | `warn`（预期） | `active` |

**未落盘用例**：`TC-A1-01`、`TC-A1-03`、`TC-C1-01`、`TC-C1-02`、`TC-D1-01`、`TC-D1-02`、`TC-D1-03`、`TC-E1-01`、`TC-E1-02`、`TC-E1-03` 仅出现在原始交付的表格中，未提供正文。它们登记为 `TODO.md` T-101，**不得视为已存在或已通过**。

**未覆盖的规则**：G-A2、G-C2、G-D2、G-E2、G-B1、G-B2、G-F1–F4、G-G1–G3（登记于 `TODO.md` T-101）。
