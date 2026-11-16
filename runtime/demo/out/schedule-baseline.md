# 进度基线（机械渲染）

- 工序：schedule_baseline
- 配置摘要：sha256:5c04f1f7e229b2b76aca9bf6ed876a14a796b9f325c59ee77faef64730669db8

本页由 `render` 算子按槽位内容生成，不含自由文本。所有数值均来自输入工件与纯函数计算。

## 计算结果

```json
{
  "activities": {
    "A": {
      "critical": true,
      "ef": 5.0,
      "es": 0.0,
      "lf": 5.0,
      "ls": 0.0,
      "total_float": 0.0
    },
    "B": {
      "critical": true,
      "ef": 9.0,
      "es": 5.0,
      "lf": 9.0,
      "ls": 5.0,
      "total_float": 0.0
    },
    "C": {
      "critical": false,
      "ef": 4.0,
      "es": 1.0,
      "lf": 9.0,
      "ls": 6.0,
      "total_float": 5.0
    },
    "D": {
      "critical": true,
      "ef": 9.0,
      "es": 9.0,
      "lf": 9.0,
      "ls": 9.0,
      "total_float": 0.0
    }
  },
  "critical_path": [
    "A",
    "B",
    "D"
  ],
  "project_duration": 9.0,
  "status": "pass",
  "topological_order": [
    "A",
    "B",
    "C",
    "D"
  ]
}
```
