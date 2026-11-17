# 运行期工件契约说明（非权威）

**性质**：本文件解释 `runtime/artifacts/*.schema.json` 的边界，不替代 schema 本身的机械约束，也不构成任何认可依据。schema 是受钉扎的判据来源；本文件不改变任何检查行为。

## deviation-report（CAP-16 偏差阈值）

- 分档维度由 CFG-01 决定：要求 `cost_account` 时 `data.work_packages` 必须非空；要求 `wbs_node` 时条目必须带 `wbs_ref`。
- 偏差值由工件给出的 `pv`/`ev`/`ac` 按 CFG-03.metric 复算，本契约不接受工件自报的偏差值。
- 档位标签必须是 CFG-02.labels 的成员，且必须等于 CFG-03.boundaries 的映射结果；边界位移或标签集变化都会改变判定。
- 绑定检查：`deviation.thresholds_configured`、`deviation.dimensions`、`deviation.custom_metric`、`deviation.band_consistent`。

## risk-register 的 `band` 标签（doc-only，不参与判定）

- `risk-register.schema.json` 不定义 `band`/`band_order` 字段；分档判定只使用 CFG-14.bands 检查初始评分是否落在某个连续区间，**不比对标签**。
- 若生产者或展示层自行附加 `band` 标签，该标签**仅展示、不参与判定**；本契约不要求、不校验，也不据该标签给出任何通过结论。
- 后果（谁能据此伪造什么）：
  - 生产者可任意填写或省略 `band` 标签而仍通过 `risk.band_consistent`；因此不能用标签证明分档口径正确。
  - 展示层可把高风险标成任何名称，检查器不会发现；只读标签的审计方会得到与现实分档不一致的叙述。
  - CFG-14.bands 的标签改动不可验证：改标签不改变任何检查结论，故无法据标签审计配置变更。
  - 可机械验证的只有刻度尺寸（`risk.scale_in_range`，取值 4–5 可观测）与评分是否落入连续分档；标签正确性必须由人工签收或非同源复核承接。
