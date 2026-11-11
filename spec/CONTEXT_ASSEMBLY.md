## 上下文装配规范

**权威关系**：本文件是执行层规范，方法无关。它定义“一次运行时该加载什么”，不定义“加载后如何执行”（后者由启用的编译方法与 `AGENTS.md` 第 6 条工作流规定）。
**动机**：本技能的首要服务对象是参数量 ≤ 7B、上下文窗口受限的本地 LLM。全量加载技能包在多数部署中不可行。本规范把“加载什么”从隐式依赖变为显式规范，使小模型能在有限上下文中获得“本次运行所需的最小充分集”。

### 1. 装配的定位与执行者

**装配是什么**：给定一次运行的任务描述（场景 + 输入），产出本次运行所需加载的文件集合、文件内切片、以及 token 预算分配方案。装配产物称为**装配清单**（manifest）。

**装配的执行者**：宿主运行时。**生成模型不参与装配决策**——与 `CONSTITUTION.md` 第 1 条的执行机械化纪律一致。生成模型只消费装配清单所指向的内容。

**装配与契约解析的关系**：装配发生在契约解析之前。装配清单决定加载哪些契约文件；契约解析（`contracts/resolver.md`）在装配之后执行。二者由宿主运行时顺序调用。

### 2. 四类场景

| 场景 | 触发条件 | 典型任务 |
|---|---|---|
| **S1 首次接触** | 用户首次了解本技能；无具体项目输入 | “这是什么”“怎么用” |
| **S2 检查执行** | 有具体项目上下文，需要执行规则检查 | “检查这个项目的承诺是否有约束锚定” |
| **S3 日常使用** | 有项目上下文，需要完整走一次项目管理活动 | 输入解包 → 槽位填充 → 检查 → 产出 |
| **S4 治理修改** | 需要修改成文法、来源、术语或编译方法 | “新增一条规则”“登记一个来源” |

### 3. 各场景的最小加载集

**加载集的定义**：`必读`（不加载则无法完成任务）、`按需`（任务涉及某主题时才加载）、`不加载`（本场景不需要）。

#### S1 首次接触

| 文件 | 加载级别 | 切片规则 |
|---|---|---|
| `README.md` | 必读 | 全文 |
| `CHARTER.md` | 必读 | 全文（承诺 C1–C6 是定位的核心） |
| `GLOSSARY.md` | 按需 | 仅加载用户问题中出现的术语对应条目 |
| `GRAMMAR.md` | 按需 | 仅加载用户问题涉及的规则组 |
| 其余 | 不加载 | — |

**token 预算参考**：`README.md` + `CHARTER.md` ≈ 6–8k tokens；按需切片再 +2–4k。总计 8–12k。

#### S2 检查执行

| 文件 | 加载级别 | 切片规则 |
|---|---|---|
| `validation/CHECKLIST.md` | 必读 | **仅加载与本次检查涉及的规则组对应的行**（按规则组切片） |
| `spec/methods/deterministic-checker.md` | 必读 | 附录 A（check_id 注册表）中涉及的 check_id 行 + 附录 B（翻译规范）全文 |
| `GLOSSARY.md` | 按需 | 涉及的术语条目（从 check_id 的 `predicates_used` 反查） |
| `knowledge/anchored-entries.jsonl` | 按需 | 涉及的谓词条目（从 check_id 的 `predicates_used` 反查） |
| `spec/INTERFACE_CONTRACT_SPEC.md` | 按需 | 仅当输入涉及槽位填充时加载第 2 节 |
| 契约文件 | 必读 | 当前挂载领域技能的契约文件（若有） |
| `SOURCE_LEDGER.md` | 不加载 | 来源是合法性锚点，不是执行前提（`CONSTITUTION.md` 第 7.2 级） |
| `GRAMMAR.md` | 不加载 | 检查清单已携带规则编号与判定摘要；规则原文不进入执行路径 |

**token 预算参考**：单规则组检查 ≈ 3–5k；跨规则组检查 ≈ 6–10k。

#### S3 日常使用

在 S2 的基础上追加：

| 文件 | 加载级别 | 切片规则 |
|---|---|---|
| `AGENTS.md` | 必读 | 仅加载第 1、2、5、5bis、6 条（工作流与纪律），第 3、4 条不加载（调度与目录结构不参与运行） |
| `spec/ASSUMPTION_PROTOCOL.md` | 必读 | 全文（`grounded`/`assumption` 分离是核心纪律） |
| `spec/INTERFACE_CONTRACT_SPEC.md` | 必读 | 第 2、4 节（槽位与契约格式） |
| `knowledge/methods/registry-skeleton.md` | 按需 | 仅加载与任务类别对应的方法条目（按 `category` 键检索） |
| `spec/COMPILATION_META.md` | 不加载 | P1–P6 是编译方的义务，不是使用方的义务 |
| `CONSTITUTION.md` | 不加载 | 治理规则不参与日常运行 |

**token 预算参考**：单类别任务 ≈ 8–12k；跨类别任务 ≈ 12–18k。

#### S4 治理修改

| 文件 | 加载级别 | 切片规则 |
|---|---|---|
| `CONSTITUTION.md` | 必读 | 全文 |
| `adr/ADR-TEMPLATE.md` | 必读 | 全文 |
| `adr/0001-*.md`、`adr/0002-*.md` | 必读 | 全文（决策上下文） |
| `CHANGELOG.md` | 必读 | 最近 3 个批次（避免重复已登记的变更） |
| `TODO.md` | 必读 | 全文（避免重复已登记的工作项） |
| 目标文件 | 必读 | 本次修改涉及的文件 |
| `GLOSSARY.md` | 按需 | 涉及术语的条目 + 第 4、5 节（同步规则） |
| `SOURCE_LEDGER.md` | 按需 | 仅当修改涉及来源时 |
| `spec/COMPILATION_META.md` | 按需 | 仅当修改涉及编译时 |

**token 预算参考**：通常 15–25k。治理修改是低频高价值场景，预算较宽。

### 4. 加载优先级与降级

当 token 预算不足以加载全部“必读”时，按以下优先级降级：

1. **不可降级**：`spec/ASSUMPTION_PROTOCOL.md`（S3 必读）、涉及的 `check_id` 行（S2/S3）、涉及的契约文件（S2/S3）。这些缺失则任务无法正确执行，应阻断并报告预算不足。
2. **可降级为摘要**：`AGENTS.md` 第 6 条可降级为“工作流七步”清单；`README.md` 可降级为“定位一句话 + 文件地图”。
3. **可降级为按需检索**：`GLOSSARY.md` 条目、`knowledge/` 方法条目、`anchored-entries.jsonl` 条目。降级后由宿主在运行时按需检索（检索接口见 `AGENTS.md` 第 6 条）。
4. **可完全省略**：`SOURCE_LEDGER.md`、`GRAMMAR.md` 原文、`CONSTITUTION.md`（S2/S3 场景）。

**降级必须显式登记**：装配清单必须记录“哪些文件被降级、降级到何种形态、省略了什么”。降级不得静默。

### 5. 装配清单格式

```json
{
  "manifest_id": "<唯一标识>",
  "scene": "S1 | S2 | S3 | S4",
  "task_summary": "<一句话描述本次任务>",
  "assembled_at": "<时间戳>",
  "assembler": "<宿主运行时标识>",
  "loads": [
    {
      "file": "spec/ASSUMPTION_PROTOCOL.md",
      "level": "full",
      "reason": "S3 必读"
    },
    {
      "file": "validation/CHECKLIST.md",
      "level": "slice",
      "slice": { "rule_groups": ["A", "C"] },
      "reason": "本次检查涉及规则组 A 与 C"
    },
    {
      "file": "GLOSSARY.md",
      "level": "on_demand",
      "reason": "token 预算不足，降级为按需检索"
    }
  ],
  "token_budget": {
    "total": 12000,
    "allocated": 10500,
    "remaining": 1500
  },
  "degradations": [
    { "file": "GLOSSARY.md", "from": "full", "to": "on_demand", "reason": "预算不足" }
  ],
  "blocked": false
}
```

**装配清单的用途**：
- 宿主据此加载内容；
- 装配清单本身是**证据工件**的一部分（`spec/methods/deterministic-checker.md` 第 5 节的 `input_snapshot` 可引用 `manifest_id`）；
- 审计时可见“本次运行加载了什么、降级了什么”。

### 6. 装配与编译产物的关系

- 装配清单**不替代**编译产物。`validation/CHECKLIST.md` 是编译产物；装配清单规定“本次加载它的哪些行”。
- 装配清单**不修改**编译产物。切片是加载行为，不是对清单的修改。
- 编译产物更新时，装配清单的切片规则不变（切片按规则组，不按具体行号）。

### 7. 与 PACT / 三空间的关系

- **PACT 若存在**：装配清单的 `loads` 可包含 PACT 规则文件；PACT 运行时消费装配清单的对应条目。
- **三空间若存在**：装配清单的 `loads` 可包含三空间映射的 `assumption` 条目；未启用三空间时不加载。
- **两者均缺失时**：装配清单不含相关条目，技能完备性不受影响（`CONSTITUTION.md` 第 8 条）。

### 8. 装配的失败处理

| 失败类型 | 含义 | 处置 |
|---|---|---|
| `scene_undetermined` | 无法判定场景 | 阻断，请用户澄清 |
| `budget_insufficient` | 预算不足以加载全部不可降级项 | 阻断，报告缺失项；建议拆分任务或增大预算 |
| `file_missing` | 必读文件缺失 | 阻断，报告缺失文件（这属于部署缺陷，不是装配缺陷） |
| `slice_empty` | 切片规则产出空集（如某规则组无对应行） | 记录告警；继续执行（空集本身是合法结果） |

### 9. 修订纪律

- 本文件的变更若改变已有场景的加载集，升级为结构性变更，需 ADR。
- 本文件的变更若仅调整切片规则或预算参考值，走 CHANGELOG。
- 本文件的内容与 `README.md` 的“阅读路径”保持语义一致；不一致时以本文件为准，`README.md` 相应修订。
