# T-107 原型独立复核验收包（只读）

**性质**：只读验收包。复核方在独立会话中运行，**不得修改本文件或仓库其他文件**。本包不包含原型源码，也不引用其内部结构；复核方应仅依据规则正文、输入快照与判定列独立实现或人工比对。

**复核对象**：`validation/checker-prototype/checker.py` 对下列 3 个检查项的判定结果（自证 34/34 与实现同源，不构成独立证据）。

**复核范围**：只核对附录 A 判定列；规则正文中已知未进入判定列的条件单列在每项末尾，不计入“原型是否与判定列一致”的判定。

**输入 schema**：`spec/CHECKER_INPUT_SCHEMA.md`。复核方若自行实现，必须使用该 schema 的字段名。

---

## 1. `PROJECT_MINIMAL_EXISTENCE`（G-A1，`block`）

**规则条款**：`GRAMMAR.md` 规则组 A / G-A1“项目的最小本体条件”。

> 一个 `Project` 节点存在，当且仅当以下四个槽位同时被填充：至少一个 `Actor`；至少一个 `Outcome`；该 `Actor` 对 `Outcome` 的 `Commitment`；至少一个作用于该 `Outcome` 或 `Commitment` 的 `Constraint`。

**判定列**（附录 A）：`Project` 存在；`Actor` / `Outcome` / `Commitment` / `Constraint` 四类节点均存在；每条 `Commitment` 的 `by` / `to` 指向已登记节点。

**样例位置**：`spec/methods/deterministic-checker.md` A.1.1，样例 1（触发）、样例 2（不触发）。

**样例 1 输入**：

```yaml
project: { id: "P-1" }
actors: [{ id: "A-1", type: "HumanActor" }]
outcomes: [{ id: "O-1" }]
commitments: [{ id: "C-1", by: "A-1", to: "O-1" }]
constraints: []
```

**原型实际结果**：`verdict=fail`，`reason=missing_constraint`。

**样例 2 输入**：

```yaml
project: { id: "P-2" }
actors: [{ id: "A-1", type: "HumanActor" }]
outcomes: [{ id: "O-1" }]
commitments: [{ id: "C-1", by: "A-1", to: "O-1" }]
constraints: [{ id: "K-1", constrains: "O-1" }]
```

**原型实际结果**：`verdict=pass`，`reason=null`。

**已知未覆盖**：规则正文要求 `Constraint` 作用于该 `Outcome` 或 `Commitment`；判定列未检查该边（G-002 / T-130）。复核方请注明：按判定列，原型结果是否可复现；按规则正文，是否应额外判 `fail`。

---

## 2. `DELIVERABLE_ASSERTION_LINK`（G-C1，`block`）

**规则条款**：`GRAMMAR.md` 规则组 C / G-C1“交付物必须可断言”。

> 每个 `Deliverable` 节点必须至少有一条出边指向 `Assertion` 节点。`Assertion` 的内容必须是关于该交付物“是什么、处于什么状态、满足什么条件”的明确陈述。不存在“已被识别但不可断言”的交付物。

**判定列**（附录 A）：每个 `Deliverable` 至少有一条 `asserted_by` 边指向已登记 `Assertion`。

**样例位置**：`spec/methods/deterministic-checker.md` A.1.3，样例 1（触发）、样例 2（不触发）。

**样例 1 输入**：

```yaml
deliverables: [{ id: "D-1", asserted_by: [] }]
assertions: [{ id: "S-1", about: "D-2" }]
```

**原型实际结果**：`verdict=fail`，`reason=deliverable_without_assertion`。

**样例 2 输入**：

```yaml
deliverables: [
  { id: "D-1", asserted_by: ["S-1"] },
  { id: "D-2", asserted_by: ["S-2", "S-3"] }
]
assertions: [{ id: "S-1" }, { id: "S-2" }, { id: "S-3" }]
```

**原型实际结果**：`verdict=pass`，`reason=null`。

**已知未覆盖**：无（该检查项的判定列未登记与规则正文的已知差异）。

---

## 3. `CHANGE_CONSTRAINT_LINK`（G-D1，`block`）

**规则条款**：`GRAMMAR.md` 规则组 D / G-D1“变更的约束锚定”。

> 任何对 `Commitment` 或 `Deliverable` 的变更提议，必须显式声明它作用于哪个已登记的 `Constraint` 节点，并说明该变更是 `mitigates`（缓解）、`exacerbates`（加剧）还是 `trades_off`（权衡）该约束。不允许“无约束锚定”的变更。

**判定列**（附录 A）：每个 `ChangeRequest` 的 `constraint` 指向已登记 `Constraint`，且 `relation` ∈ {`mitigates`, `exacerbates`, `trades_off`}。

**样例位置**：`spec/methods/deterministic-checker.md` A.1.4，样例 1（触发）、样例 2（不触发）。

**样例 1 输入**：

```yaml
changes: [{ id: "CH-1", constraint: "K-1", relation: "affects" }]
constraints: [{ id: "K-1" }]
```

**原型实际结果**：`verdict=fail`，`reason=invalid_change_relation`。

**样例 2 输入**：

```yaml
changes: [
  { id: "CH-1", constraint: "K-1", relation: "mitigates" },
  { id: "CH-2", constraint: "K-2", relation: "trades_off" }
]
constraints: [{ id: "K-1" }, { id: "K-2" }]
```

**原型实际结果**：`verdict=pass`，`reason=null`。

**已知未覆盖**：无（该检查项的判定列未登记与规则正文的已知差异）。

---

## 复核结论表（由复核方填写，不写回本仓库）

| 检查项 | 独立结论（pass/fail） | 与原型一致？ | 差异说明 |
|---|---|---|---|
| `PROJECT_MINIMAL_EXISTENCE` 样例 1 | | | |
| `PROJECT_MINIMAL_EXISTENCE` 样例 2 | | | |
| `DELIVERABLE_ASSERTION_LINK` 样例 1 | | | |
| `DELIVERABLE_ASSERTION_LINK` 样例 2 | | | |
| `CHANGE_CONSTRAINT_LINK` 样例 1 | | | |
| `CHANGE_CONSTRAINT_LINK` 样例 2 | | | |

**复核结论的最低要求**：由非同源实现运行上述 6 个快照，或由复核方逐条比对规则正文与判定列；结论须写明实现/比对方法、每项结论与差异。结论只用于验证“判定列可被独立复现”，不改变任何缺口状态。
