## 契约解析规则

**权威关系**：本文件是执行层文件，落实 `spec/INTERFACE_CONTRACT_SPEC.md` 第 5、6、8 节。解析由宿主运行时机械执行，生成模型不参与（`CONSTITUTION.md` 第 1 条）。

### 1. v1 单层解析（启用）

**权威位置**：领域技能目录下的独立契约文件（`*.pm-contract.yaml` 或 `*.pm-contract.json`），与领域技能的 `SKILL.md` 并列。

**解析步骤**：

1. **扫描**：宿主启动时扫描已挂载领域技能目录，查找 `*.pm-contract.{yaml,json}` 文件。
2. **schema 校验**：按 `contracts/schema/pm-slot-contract.schema.json` 校验。失败 → 该技能标 `contract_invalid`，不参与协作，记录缺陷（含校验错误详情）。
3. **必填槽位校验**：`subject_type`、`deliverable_forms`、`constraint_domains`、`assertion_vocabulary` 必须非空。缺失 → 该技能标 `contract_incomplete`，不参与协作，报告缺失项。
4. **语义校验**（schema 无法表达的约束）：
   - `constraint_domains` 中每项的 `relation_to_generic` 为 `specializes` 时必须有 `generic_class`；
   - `subject_group_extension` 中每项的 `relation_to_base` 非 `orthogonal_to` 时必须有 `base_subject_group`；
   - `actor_roles` 中 `can_be_accountable: true` 的角色名不得暗示 AI（本技能不检查角色名的语义，但若领域技能显式声明了 `AIActor` 类型，`can_be_accountable` 必须为 `false`——这是 G-E1 的契约层投影）。
5. **assumption_refs 校验**：按 `ASSUMPTION_PROTOCOL.md` 第 4 节校验每条 `alignment_check` 的字段完备性。不完整 → 该技能标 `contract_incomplete`。
6. **产出扁平快照**：

```json
{
  "skill_id": "...",
  "contract_source": "<契约文件路径>",
  "contract_hash": "<文件内容哈希>",
  "resolved_slots": {
    "subject_type": { "value": "...", "source": "<契约文件路径>" },
    "deliverable_forms": { "value": ["..."], "source": "..." },
    "constraint_domains": { "value": [...], "source": "..." },
    "assertion_vocabulary": { "value": [...], "source": "..." },
    "actor_roles": { "value": [...], "source": "..." },
    "subject_group_extension": { "value": [...], "source": "..." }
  },
  "assumption_refs": [...],
  "status": "valid | contract_invalid | contract_incomplete",
  "defects": [...]
}
```

快照是**幂等**的：同一契约文件 + 同一 resolver 版本 → 同一快照。快照携带来源标识，便于后续检查项溯源。

### 2. 多层合并语义（定义但不启用）

**v1 不实现多层合并。** 本节定义语义，供未来启用时参考。启用条件：需要 ADR 论证真实需求出现（`spec/INTERFACE_CONTRACT_SPEC.md` 第 6 节）。

#### 2.1 层级与优先级

从低到高：

1. `SKILL.md` 内嵌区块（作者默认）
2. 独立契约文件（正式声明）
3. 注册表条目（部署覆盖）

#### 2.2 字段级合并

合并是字段级的，不是整文件替换。

| 字段状态 | 表示 | 合并行为 |
|---|---|---|
| 未声明 | 字段缺失 | 继承低层级值；全部层级缺失 → 槽位“未填充”，按 `ASSUMPTION_PROTOCOL.md` 第 5 节阻断或标 `assumption` |
| 声明值 | 字段有值 | 覆盖低层级同名字段 |
| 显式移除 | 字段值为 `null` | 覆盖为“无”，**不允许**低层级回填 |

#### 2.3 列表字段

默认**替换**，不追加。追加需显式声明 `merge: append`。追加语义在契约合并中易产生歧义（顺序、去重、来源归属），故默认不用。

#### 2.4 同级冲突

同级来源对同一字段给出不同值 → `contract_conflict`，阻断，不静默取值。

#### 2.5 null 与必填槽位

`null` 作用于 `required: true` 的槽位 → `contract_violation`，契约不可满足，阻断。这与“未声明”不同：未声明是继承低层级，`null` 是主动移除，移除必填项是违约。

#### 2.6 immutable 标记

字段可标 `immutable: true`（如法规强制的 `assertion_vocabulary`）。高层级试图覆盖 immutable 字段 → `contract_violation`。这使“覆盖权”本身成为可声明的治理对象。

### 3. PACT 适配节

PACT 是可选插件（`CONSTITUTION.md` 第 8 条）。若宿主安装 PACT，本节规定契约槽位与 PACT 构件的映射边界。

#### 3.1 可映射

| 契约槽位 | PACT 构件 | 映射规则 |
|---|---|---|
| `deliverable_forms` | `Token` 类型 | 每个形态映射为一个 Token 类型；形态名 = Token 类型名 |
| `constraint_domains` | `Token` 类型 + 关系 | 每个约束域映射为一个 Token 类型；`relation_to_generic` 映射为 Token 间关系类型 |
| `assertion_vocabulary` | `AssertionToken` 元数据 | 每个断言词汇映射为 `AssertionToken` 的 `assertion_kind` 字段值；`maps_to` 映射为该字段的枚举值 |

#### 3.2 不可映射（必须在适配层显式声明）

| 契约要素 | 不可映射原因 |
|---|---|
| `actor_roles.can_be_accountable` | PACT 的 Gate 是“参与者 × 工件类型”的能力，不是角色属性的字段级约束；问责约束须在技能自身校验器执行（G-E1 的契约层投影） |
| `subject_group_extension.relation_to_base` | PACT 无“与基础分类的关系”概念 |
| 连接实例的映射规则（`spec/INTERFACE_CONTRACT_SPEC.md` 第 3 节） | PACT 管理单技能内的工件流，不管理跨技能的槽位映射 |
| `assumption_refs` | PACT 无 assumption 概念 |
| `contract_hash` 的幂等性保证 | PACT 不保证契约解析的幂等；幂等性由宿主解析器提供 |

#### 3.3 纪律

- 可映射项按上表映射；映射规则本身是 `contracts/` 的一部分，不进入 `GRAMMAR.md`。
- 不可映射项由技能自身的确定性校验器执行；PACT 不承担。
- **PACT 缺失时**：全部契约解析由宿主解析器执行，技能完备性不受影响（`CHARTER.md` 承诺 C4）。
- **禁止**：为了“用上 PACT”而把不可映射项硬塞为 AND 条件，或把 OR 分支拆成多条 AND 条件后假装等价。

### 4. 解析失败的处置

| 失败类型 | 状态 | 处置 |
|---|---|---|
| schema 校验失败 | `contract_invalid` | 记录缺陷（含错误详情）；该技能不参与协作；不影响其他技能 |
| 必填槽位缺失 | `contract_incomplete` | 报告缺失项；该技能不参与协作；不推断缺失值 |
| 语义校验失败 | `contract_incomplete` | 同上 |
| assumption_refs 不完整 | `contract_incomplete` | 同上 |
| 同级冲突（多层时） | `contract_conflict` | 阻断；报告冲突字段与来源 |
| null 作用于必填槽位 | `contract_violation` | 阻断；报告槽位与来源 |
| immutable 字段被覆盖 | `contract_violation` | 阻断；报告字段与覆盖来源 |

**解析失败不构成成文法违规**，构成部署配置缺陷。缺陷记录在宿主台账，不写入任何项目文件（`AGENTS.md` 第 1 条纪律的延伸）。
