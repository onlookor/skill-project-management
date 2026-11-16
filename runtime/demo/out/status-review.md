# 状态评审（机械渲染）

- 工序：status_review
- 配置摘要：sha256:5c04f1f7e229b2b76aca9bf6ed876a14a796b9f325c59ee77faef64730669db8

每个测量期的偏差点按 CFG-03 映射为分档标签；不在覆盖区间时工序以退出码 3 中止，而不是归档。

```json
{
  "bands": [
    {
      "band": "yellow",
      "band_order": 3,
      "period": "2026-01",
      "value": 1.0
    }
  ],
  "metric": "SPI",
  "status": "pass"
}
```
