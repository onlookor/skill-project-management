# 审计留痕追加（机械渲染）

- 工序：audit_review
- 配置摘要：sha256:5c04f1f7e229b2b76aca9bf6ed876a14a796b9f325c59ee77faef64730669db8

新增记录的 `prev_digest` 取上一条记录的规范化摘要；渲染只转录，不修改原记录。

```json
{
  "digest": "sha256:cf516fb4d817541e731f861731eed87b1032774da2d60dec2748e1a6a2677919",
  "record": {
    "actor": "onlookor",
    "artifact_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000",
    "artifact_type": "audit-trail",
    "checks_run": [
      "audit.chain_digest"
    ],
    "config_digest": "sha256:5c04f1f7e229b2b76aca9bf6ed876a14a796b9f325c59ee77faef64730669db8",
    "evidence_paths": [
      "runtime/demo/out/status-review.md"
    ],
    "exit_code": 0,
    "prev_digest": "sha256:10305100e47b2b4cd8f0eaf08b47109999e0a84247c8b3d9aa6adf6d0172d3b4",
    "rule_version": "batch-0095",
    "run_id": "run-demo-003",
    "seq": 3,
    "ts": "2026-11-16T20:00:00+08:00"
  },
  "status": "pass"
}
```
