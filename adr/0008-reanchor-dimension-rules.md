# ADR-0008: 规则组 B 重新锚定——从“五过程组 × 十主题组”改为 ISO 21502:2020 的两套实践

- **状态**：accepted
- **日期**：2026-11-12
- **决策者**：执行方核对本地副本后提出；用户要求“把待核对项落实或如实降级”
- **serves_charter**：服务于 C2（来源封闭、可追溯）与 C3（不得把无来源支持的表述写成已接地）
- **grounding_refs**：`ISO21502-2020`
- **affected_files**：`GRAMMAR.md`（第 1 条说明、规则组 B 引言、G-B1、G-B2、G-F1–G-F4、G-G1–G-G3 的核验注、规则组状态汇总表 B 行）、`SOURCE_LEDGER.md`（`ISO21502-2020` 条目）、`ERRATA.md`（E-013）、`TODO.md`（T-113 关闭，T-118 新增）、`spec/ANCHOR_SPEC.md`（外部资料页码定位的澄清）、`CHANGELOG.md` 批次 0015

## 背景

G-B1、G-B2 自 ADR-0005 起处于 `pending_reanchor`：原锚点 ISO 21500:2012 已于 2021 年撤回，改挂 ISO 21502:2020，但“五过程组 × 十主题组”矩阵是否在 2020 版中保留未核对。规则组 B 因此长期只能以 `advisory` 运行，且其前提本身没有证据支撑。

2026-11-12 使用 `pdftotext` 逐页提取本地 62 页副本并定位关键章节，结论如下：

1. ISO 21502:2020 **不含**任何“过程组 × 主题组”矩阵。正文由两套实践构成：第 6 章“Integrated project management practices”（6.2–6.9，印刷页 18–26，八个生命周期位置）与第 7 章“Management practices for a project”（7.2–7.18，印刷页 26–45，十七项管理实践）。
2. 附录 A 是**资料性**的：表 A.1 把 ISO 21500:2012 的 39 个过程映射到本文档实践；表 A.2 以 ISO 21500:2012 的五个过程组（Initiating / Planning / Implementing / Controlling / Closing）为列首，把本文档实践放回旧框架中对照（印刷页 47–51）。这是对已撤回标准的兼容对照，不是本文档自身的结构。
3. 因此“把矩阵当作 ISO 21502:2020 的内容”是把已撤回标准的结构伪装成现行标准，属于 `CONSTITUTION.md` 第 3.2 条要拦截的“来源存在但来源不蕴含该规则”。

## 决定

1. **G-B1 改写**：管理项须同时携带 `process_group` 与 `subject_group` 两个标签；前者取自第 6 章的八个生命周期位置，后者取自第 7 章的十七项管理实践。
2. **G-B2 改写**：值集封闭于上述两套枚举；领域特化仍走 `subject_group_extension` 槽位（`specializes` / `cross_cuts` / `orthogonal_to`）。删除“正交”语义——原文只给出实践对照，不宣称两维独立。
3. **状态**：规则组 B 由 `pending_reanchor` 转为 `active`；`severity` 保持 `advisory`。理由是双标签要求、维度收敛与扩展机制均为技能自身的形式化贡献，按 `CONSTITUTION.md` 第 3.2 条须在 `provenance_note` 中划清边界；升级为 `block` 需先有样例契约的使用证据（T-118）。
4. **G-F3、G-F4 的措辞同步修正**：把“采购主题组”“时间主题组”改为 ISO 21502:2020 的实际实践名（7.17 Procurement、7.6 Schedule management），并补充页码。
5. **PRINCE2 侧**：G-F1、G-F2、G-G1–G3 的 `assumption_verification` 记录 2026-11-12 的核对结论与页码；不改变规则文本与 `advisory` 判定（原则措辞可核，具体字段集仍是自身贡献）。

## 结果

- 规则组 B 不再有“悬空的待核对前提”，锚点与标准正文一致；`check_anchors.py` 与 `check_ledger_landings.py` 通过。
- 代价：维度值从两个短枚举变为 8 + 17 个值，生成端需要更多约束；`advisory` 期间不阻断，因此暂不影响既有契约。
- 未解决的相邻问题：ProjectCO 的 `Actor` / `Commitment` / `Constraint` 术语归属（T-119）与 Springer 正文获取（T-112），不在本决策范围。
