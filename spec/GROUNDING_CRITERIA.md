## 接地完成判据

**权威关系**：本文件是执行层规范。它定义“本技能在某个部署中已接地”的判据。判据的**状态声明**受 `CONSTITUTION.md` 第 12 条约束。
**动机**：`README.md` 说“设计上完备，运行上待接地”，但从未定义“接地”的完成判据。没有判据，无法判断 v0.3 何时可用、新的部署是否已接地。

### 1. 判据清单

本技能在某部署中“已接地”，当且仅当以下六条判据全部满足：

**G1（规则锚定完成）**

`GRAMMAR.md` 的全部规则，其规则状态不得为 `pending_reanchor`；`assumption` 状态须已在部署中显式接受（见第 3 节）。

**可查方式**：`GRAMMAR.md` 规则组状态汇总表；部署配置中的 `accepted_assumptions` 清单。

**G2（编译方法已启用且产物齐备）**

至少一个编译方法处于 `enabled` 状态（`spec/COMPILATION_METHODS.md`），且其产物（`validation/` 下的检查清单与检查项规格）已生成并在 `STATE.md` 中登记为 `active`。

**可查方式**：`COMPILATION_METHODS.md` 的启用状态；`STATE.md` 中 `validation/CHECKLIST.md` 的状态；部署配置中的产物清单。

**G3（检查器可执行且通过反例检验）**

启用的编译方法所对应的检查器在部署中可执行；`validation/test-cases/` 中的全部反例检验用例执行通过（每条用例的结论与预期一致）。

**可查方式**：`STATE.md` 中相关检查器与用例的状态；部署配置中的检查器执行入口；反例检验执行报告（登记为证据工件）。

**G4（术语表与 JSONL 同步）**

`GLOSSARY.md` 的 A 类条目与 `knowledge/anchored-entries.jsonl` 的对应条目定义一致；`scripts/check_glossary_sync.md` 描述的检查项全部通过。

**可查方式**：同步检查的执行记录。

**G5（上下文装配规范可执行）**

`spec/CONTEXT_ASSEMBLY.md` 的四类场景在部署中可执行；至少 S2 与 S3 场景的装配清单已生成过一次（作为装配能力的验证）。

**可查方式**：装配清单实例；装配执行日志。

**G6（部署可行性勘察结论已登记）**

以下三项的勘察结论已在部署中登记，每项状态为 `confirmed_present` / `confirmed_absent` / `undetermined`（见第 2 节）：

- **批准角色存在性**：高影响决策的批准角色是否已指派；
- **P0 响应能力**：部署是否具备在 P0 信号出现时的即时响应能力（值班/on-call）；
- **CI 能力**：部署是否具备自动化检查执行能力（若启用的编译方法依赖 CI）。

**可查方式**：部署配置中的 `deployment_feasibility` 字段；每项附 `declared_by`、`declared_at`、`evidence`、`source`。

### 2. G6 的三种状态语义

G6 的三项状态**不要求全部为 `confirmed_present`** 才视为接地。状态本身是声明，后果按既有规则消费：

| 状态 | 含义 | 后果 |
|---|---|---|
| `confirmed_present` | 已确认具备 | 按具备处理 |
| `confirmed_absent` | 已确认不具备 | 按既有规则的“不具备”后果处理：批准角色缺失 → 高影响决策阻塞；P0 响应缺失 → 部署可行性缺陷，按 `COMPILATION_META.md` F-C4 处置；CI 缺失 → 启用的编译方法须声明退化路径 |
| `undetermined` | 尚未确定 | 按保守方向处理：批准角色缺失时高影响决策阻塞（与未声明同后果）；P0 响应缺失时按“无值班能力”设计但不判定为缺陷；CI 缺失时走退化路径。**`undetermined` 必须附 `conversion_event`（最后负责时刻）与 `deadline`** |

**转换事件**：
- 批准角色：首次高影响决策进入批准路径前；
- P0 响应：首次依赖 P0 响应的检查执行前；
- CI：首次依赖自动化的检查执行前。

**到期未转**：强制转 `confirmed_absent`，适用其后果，禁止继续以 `undetermined` 免检。

### 3. `assumption` 状态的接受

G1 要求 `pending_reanchor` 解除，但 `assumption` 状态**不要求解除**——`assumption` 是规则的合法状态（`GRAMMAR.md` 规则组 F、G 在核验完成前以 `assumption` 身份存在）。接地要求的是：

- `assumption` 级规则在部署中被**显式接受**：部署配置中 `accepted_assumptions` 列出被接受的 `assumption` 级规则 ID，每条附接受理由；
- 被接受的 `assumption` 级规则，其检查项在部署中按 `advisory` 执行（不阻断），并携带 `assumption_basis`；
- 未被接受的 `assumption` 级规则，其检查项**不执行**（既不阻断也不告警），登记为部署的“未启用检查项”。

**为什么允许 `assumption` 未被接受**：某些部署可能暂时不需要某类检查（如不需要阶段闭合检查的小型项目）。允许按需接受，不强制全量启用。

### 4. 判据未过时的处置

| 判据 | 未过时的含义 | 处置 |
|---|---|---|
| G1 | 存在 `pending_reanchor` 规则，或 `assumption` 规则未被接受 | `pending_reanchor` 规则按 `advisory` 执行；未接受的 `assumption` 规则不执行 |
| G2 | 无启用方法，或产物未生成/未在 `STATE.md` 登记为 `active` | **阻断**：无启用方法时技能无执行路径；产物未登记或未生成时拒绝运行 |
| G3 | 检查器不可执行，或反例检验未通过 | **阻断**：检查器不可执行时技能无法执行任何检查；反例未通过时检查结果不可信 |
| G4 | 同步检查未通过 | 记录缺陷；相关术语按 JSONL 为准（`CONSTITUTION.md` 第 11.5 条）；不阻断 |
| G5 | 装配规范未验证 | 记录缺陷；不影响技能执行；登记为待验证项 |
| G6 | 三项状态声明缺失 | 缺失项按 `undetermined` 处理（保守方向）；不阻断接地判定，但记录为部署缺陷 |

**接地判定的输出**：六条判据的逐条结果 + 总判定（`grounded` / `partially_grounded` / `ungrounded`）。

- `grounded`：六条全部满足（G6 的 `undetermined` 状态视为“已声明”，不视为未满足）；
- `partially_grounded`：G2/G3 满足，其余有未满足项；
- `ungrounded`：G2 或 G3 未满足。

**未接地时的行为**：产出决策标 `provisional`（`CONSTITUTION.md` 第 12.3 条）。

### 5. 接地判定的记录

接地判定本身是**证据工件**：

```json
{
  "grounding_check_id": "<唯一标识>",
  "deployment_id": "<部署标识>",
  "checked_at": "<时间戳>",
  "criteria": {
    "G1": { "verdict": "pass|fail", "detail": "..." },
    "G2": { "verdict": "pass|fail", "detail": "..." },
    "G3": { "verdict": "pass|fail", "detail": "..." },
    "G4": { "verdict": "pass|fail", "detail": "..." },
    "G5": { "verdict": "pass|fail", "detail": "..." },
    "G6": {
      "verdict": "pass|fail",
      "items": [
        { "dimension": "approval_role", "state": "confirmed_present|confirmed_absent|undetermined",
          "declared_by": "...", "declared_at": "...", "evidence": "...", "source": "...",
          "conversion_event": "...", "deadline": "..." }
      ]
    }
  },
  "overall": "grounded|partially_grounded|ungrounded",
  "provisional_mode": false
}
```

接地判定记录保存期限 = 部署存续期 + 1 年（注册表默认值）。

### 6. 与 `COMPILATION_META.md` 的关系

- G2、G3 是 `COMPILATION_META.md` 第 2 条（P1–P6）与第 3 条（准入条件）的**运行时验证**：P1–P6 是编译方的义务，G2/G3 是部署方对“编译方是否履行了义务”的检查。
- G3 的反例检验是 P1c（不扭曲）的运行时证据。
- G6 的 CI 能力与 `spec/methods/deterministic-checker.md` 第 10.2 节的退化路径关联：CI 缺失时，启用的方法必须声明退化路径（确定性校验器的退化路径为 `human-fallback`）。

### 7. 版本纪律

- 本文件新增判据需 ADR（因为它改变“接地”的定义）。
- 本文件调整判据的可查方式或状态语义，走 CHANGELOG。
- 本文件的判据与 `CONSTITUTION.md` 第 12 条、`STATE.md` 的文件状态保持语义一致；不一致时以本文件为准。
