## 快速开始

**性质**：入口文档。用一个最小样例走完“输入 → 装配 → 检查 → 输出”的完整流程，并给出与真实 LLM 的接合示例。

### 1. 这个技能包是什么（30 秒版）

把通用项目管理知识编译为**可判定、可溯源、可由小型本地 LLM 执行**的规则与条目。它不替领域技能做领域判断；它提供任何项目都必然包含的元概念、元规则、元知识。

**不读任何其他文件时，你只需要知道三件事**：
1. 规则在 `GRAMMAR.md`，规则组 A–G，共 17 条；
2. 检查执行由确定性校验器按 `validation/CHECKLIST.md` 执行，不由模型“读清单自行判断”；
3. 输出必须物理分为 `grounded`（有出处）与 `assumption`（无出处但附验证条件）两个区块。

### 2. 最小走查样例

#### 2.1 输入：一个 fake 项目上下文

```yaml
# 输入：某组织内部文档迁移项目
project:
  id: "P-2026-001"
  name: "内部文档迁移项目"
  outcome: "将 2000 份纸质档案迁移至电子档案系统，并通过合规审计"
  actors:
    - id: "A-001"
      type: "HumanActor"
      name: "张工（项目经理）"
    - id: "A-002"
      type: "AIActor"
      name: "文档扫描 Agent"
  commitments:
    - id: "C-001"
      by: "A-001"
      to: "P-2026-001.outcome"
      description: "完成档案迁移并通过审计"
    - id: "C-002"
      by: "A-001"
      to: "P-2026-001.outcome"
      description: "档案扫描质量达标"
  deliverables:
    - id: "D-001"
      form: "AsBuiltArchive"      # 来自契约槽位 deliverable_forms
      produced_by: "C-001"
    - id: "D-002"
      form: "InspectionReport"
      produced_by: "C-002"
  constraints:
    - id: "K-001"
      domain: "building_code_compliance"   # 来自契约槽位 constraint_domains
      description: "符合《档案法》与《电子文件管理规范》"
    - id: "K-002"
      domain: "site_access"
      description: "纸质档案存放地仅工作日可进入"
  assumptions:
    - id: "AS-001"
      statement: "纸质档案总数为 2000 份（来自移交清单初稿，未逐份核对）"
      purpose: "A"
      verification:
        type: "refutable_indicator"
        indicator: "逐份核对后的实际份数"
        threshold: "与 2000 的偏差 > 10%"
        observation: "迁移完成后逐份盘点"
        on_trigger: "触发范围基线修订"
```

#### 2.2 装配（S2 检查执行场景）

宿主运行时执行 `spec/CONTEXT_ASSEMBLY.md` 第 3 节的 S2 场景装配：

```json
{
  "manifest_id": "M-2026-001-01",
  "scene": "S2",
  "task_summary": "检查项目 P-2026-001 的规则组 A、C、E",
  "loads": [
    { "file": "validation/CHECKLIST.md", "level": "slice",
      "slice": { "rule_groups": ["A", "C", "E"] }, "reason": "S2 必读" },
    { "file": "spec/methods/deterministic-checker.md", "level": "slice",
      "slice": { "check_ids": ["PROJECT_MINIMAL_EXISTENCE", "CONSTRAINT_ANCHOR_REQUIRED",
                               "DELIVERABLE_ASSERTION_LINK", "ASSERTION_MUTUAL_EXCLUSION",
                               "ROLE_MINIMAL_COMPLETENESS", "AI_AUTONOMY_DELEGATION_AUDITABLE"] },
      "reason": "S2 必读" },
    { "file": "contracts/examples/construction.pm-contract.yaml", "level": "full",
      "reason": "当前领域技能契约" }
  ],
  "token_budget": { "total": 8000, "allocated": 6500, "remaining": 1500 },
  "degradations": [
    { "file": "GLOSSARY.md", "from": "full", "to": "on_demand", "reason": "预算充足但非必读" }
  ],
  "blocked": false
}
```

#### 2.3 检查执行（确定性校验器，非模型）

校验器按 `spec/methods/deterministic-checker.md` 附录 A 的判定逻辑执行，逐条产出：

```
## 检查执行记录 — M-2026-001-01

### PROJECT_MINIMAL_EXISTENCE (G-A1)
verdict: pass
输入快照: 谓词快照 v1.0.3（Project/Actor×2/Outcome/Commitment×2/Constraint×2 均在位）
rule_status: active

### CONSTRAINT_ANCHOR_REQUIRED (G-A2)
verdict: pass
输入快照: C-001 constrained_by K-001, K-002; C-002 constrained_by K-001
rule_status: active

### DELIVERABLE_ASSERTION_LINK (G-C1)
verdict: fail
原因: D-001 与 D-002 均无 asserted_by 边指向 Assertion 节点
rule_status: active
severity: block

### ASSERTION_MUTUAL_EXCLUSION (G-C2)
verdict: cannot_evaluate
原因: 无 Assertion 节点，无法判定互斥
rule_status: active
severity: warn

### ROLE_MINIMAL_COMPLETENESS (G-E1)
verdict: pass
输入快照: C-001 accountable_by A-001 (HumanActor), responsible_by A-002 (AIActor);
          C-002 accountable_by A-001, responsible_by A-001 (须 role_merge_declaration)
          注: C-002 的 Accountable 与 Responsible 重合，但 A-001 是 HumanActor，
              且 role_merge_declaration 未在输入中声明 —— 触发 advisory 提示
rule_status: active
severity: block → 因 role_merge_declaration 缺失，实际输出 warn

### AI_AUTONOMY_DELEGATION_AUDITABLE (G-E2)
verdict: cannot_evaluate
原因: A-002 的自治权范围未声明（无 delegated_from 链）
rule_status: active
severity: warn
```

**关键点**：检查结论由校验器产出，模型不参与。`cannot_evaluate` 不等于 `pass`；缺失输入被报告，不被静默当作通过。

#### 2.4 输出：grounded / assumption 分离

```markdown
## grounded

- 项目 P-2026-001 满足最小本体条件（G-A1: pass；依据：Project、Actor、Outcome、Commitment、Constraint 均在位）
- 承诺 C-001、C-002 均已关联约束（G-A2: pass；依据：C-001→K-001/K-002，C-002→K-001）
- 承诺 C-001 的问责结构完整（G-E1: pass；A-001 为 HumanActor 且承担 Accountable）

## 违规项（阻断）

- 交付物 D-001、D-002 均无验收断言（G-C1: fail，severity=block）
  修复建议：为 D-001、D-002 各补充至少一条 Assertion，声明其状态与验收条件

## 告警项

- 承诺 C-002 的 Accountable 与 Responsible 重合（A-001），未声明 role_merge_declaration（G-E1: warn）
  修复建议：在输入中补充 role_merge_declaration，说明合并理由
- AI 文档扫描 Agent（A-002）的自治权范围未声明（G-E2: cannot_evaluate，severity=warn）
  修复建议：补充 delegated_from 链，终至 A-001，并声明范围/边界/撤销条件

## assumption

- AS-001（来自输入）: 纸质档案总数为 2000 份（来自移交清单初稿，未逐份核对）
  purpose: A（保守假设）
  verification: 逐份核对后的实际份数，偏差 > 10% 时触发范围基线修订
  expires_at: 迁移完成后逐份盘点时
```

#### 2.5 走查后的结论

- 本次走查完成了 S2 场景的完整流程：输入 → 装配 → 检查 → 输出。
- 检查器能正确判出 `pass`（G-A1、G-A2、G-E1）、`fail`（G-C1）、`cannot_evaluate`（G-C2、G-E2）。
- `grounded` / `assumption` / 违规 / 告警的分离清晰。
- 走查暴露了一个规格缺口：`ROLE_MINIMAL_COMPLETENESS` 的 `warn` 与 `block` 混合逻辑（Accountable/Responsible 重合触发 warn，但缺失 `role_merge_declaration` 时应整体降为 warn 还是整体 block？）——该缺口登记于 `ERRATA.md` 与 `TODO.md`。

### 3. 与真实 LLM 的接合示例

以下是一个 prompt 片段示例，展示如何把技能包的内容与模型调用接合。**这不是唯一接合方式，只是可复制的最小范式**。

**场景**：让一个 3B 模型执行“为 D-001 补充验收断言”的子任务。

**Prompt 片段**：

```
你是一个项目管理助手。你的任务是：为交付物 D-001 起草一条验收断言。

【规则约束】
以下规则来自 GRAMMAR.md（规则组 C）：
- G-C1：每个 Deliverable 必须至少有一条出边指向 Assertion 节点。
  Assertion 的内容必须是关于该交付物"是什么、处于什么状态、满足什么条件"的明确陈述。

【槽位】
当前领域技能的 assertion_vocabulary 为：
- compliant（maps_to: what_condition）
- non_compliant（maps_to: what_condition）
- conditional（maps_to: what_condition）
- inspected（maps_to: what_state）
- handed_over（maps_to: what_state）
- as_built（maps_to: what_is）

【术语】
Assertion（见 GLOSSARY.md#T-A-007）：关于实体与类型的人类陈述，是本体中可验证性的最小单元。

【输出格式】
输出必须分为两个区块：

## grounded
- <有出处的命题>

## assumption
- <无出处但附验证条件的命题>

【输入】
D-001 的形态为 AsBuiltArchive，由 C-001 产出。C-001 的约束为 K-001（档案法合规）与 K-002（工作日进入）。
```

**模型应输出**（示例）：

```markdown
## grounded

- D-001 的验收断言：`inspected`（状态：已检验）且 `compliant`（条件：满足 K-001 档案法合规）
  依据：G-C1 要求 Deliverable 有 Assertion；assertion_vocabulary 中 inspected 映射 what_state，
        compliant 映射 what_condition，二者组合覆盖 G-C1 要求的"状态 + 条件"

## assumption

- 无
```

**关键点**：
- 规则原文（G-C1）与槽位词汇表被显式放入 prompt，模型不需要“记得”它们；
- 术语（Assertion）引用 `GLOSSARY.md#T-A-007`，模型不需要“理解”抽象定义，只需要按引用使用；
- 输出格式被强制分为两个区块，`grounded` 中的命题必须能追溯到规则或槽位；
- 模型**不**执行检查（检查由校验器执行）；模型只做“局部判断 + 自然语言表述”。

### 4. 下一步读什么

- 想知道**为什么这样设计**：读 `CHARTER.md`。
- 想**接进一个项目**：读 `spec/INTERFACE_CONTRACT_SPEC.md` 第 2、4 节，然后在自己的领域技能目录放一份契约文件。
- 想**修改规则**：读 `CONSTITUTION.md` 第 4 条与 `adr/ADR-TEMPLATE.md`。
- 想知道**当前还缺什么**：读 `TODO.md` 与 `ERRATA.md`。
