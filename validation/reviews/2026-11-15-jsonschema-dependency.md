# 复核索引：以成熟 JSON Schema 实现替换自写子集（批次 0064–0066）

**性质：非权威、不构成关闭依据、不构成 basis。** 本文件只是索引；权威依据是下面路径指向的仓库外复核产物与用户裁定。

- 非同源复核：G-019 第四轮复核（报告自身基线 `11c5d92`；本批实现基线 `f049f28`）第 1–4 节指出自写子集的语义失真、配额外溢与反向误杀
- 复核产物：`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r4/REPORT.md`
- sha256：`47b0be71a05d726a690278f2075efb13ed54ee79582176a373e8fb6dd7f74fbb`
- 复核基线：`11c5d92`
- 结论：认可（改用成熟实现与依赖指纹由用户 2026-11-15 裁定，复核报告提供失效证据；第二、三段按报告第 1、3、5 节逐项落地）

## 区段

- 区段：`spec/ACCESS_ZONES.md`
- 区段：`contracts/schema/knowledge-entry.schema.json`
- 区段：`contracts/schema/pilot-conflict.schema.json`
- 区段：`contracts/schema/pm-slot-contract.schema.json`
- 区段：`contracts/schema/package-manifest.schema.json`
- 区段：`contracts/schema/ontology-fixtures-manifest.schema.json`
- 区段：`contracts/schema/pilot-artifact.schema.json`
- 区段：`contracts/schema/pilot-id-map.schema.json`

## 批次 0064 改动范围

- 新增 `adr/0019-mature-json-schema-validator.md`：放弃自写子集、两个被否方案、例外范围与撤销条件。
- 新增 `scripts/dependency-pins.json`、`scripts/check_dependency_pins.py`、`scripts/test_dependency_pins.py`：锁定 `jsonschema` 4.26.0、分发产物 sha256（`d489f15263b8d200f8387e64b4c3a75f06629559fb73deb8fdfb525f2dab50ce`）与安装树摘要；负例 9/9。
- `spec/ACCESS_ZONES.md` §2 登记 `scripts/dependency-pins.json`；根 `README.md` 与 `scripts/README.md` 写依赖安装步骤。
- `.githooks/pre-commit` 增加依赖指纹与负例两道检查。

## 批次 0065 改动范围（第二段：接入与契约不变）

- `scripts/check_no_raw_material.py`：用 `jsonschema` 的 `validator_for` + `check_schema` 替换自写 `validate()`；返回仍是 `(keyword, pointer, message)`，`RM-SCHEMA` / `RM-FIELD` 分派、必填键指针、`oneOf` 排他语义与退出码不变；依赖缺失即 `SchemaDependencyError` 并以退出码 2 报“无法评估”。
- schema 自身过官方元 schema：仓库级 lint、`schema-doc` 与数据校验三处调用 `_validator_for`，不合规即失败。
- `x-prose-fields` 路径改为 `_resolve_prose_path` 按 schema 结构解析；解析不到或终点非字符串/字符串数组即报 `RM-SCHEMA-LINT`，不再静默失效。
- `contracts/schema/` 自动发现改为递归（`rglob`），子目录 schema 同样 lint；`scripts/check_spec_pins.py` 的 `discover_schema_files` 同步递归，新增 SP08。
- 配额按出现值计量，`x-prose-budget` 上调至 schema 合法上限（pm-slot 28,000、pilot-conflict 16,800、pilot-id-map 22,200），单文件上限 20 KiB → 32 KiB；真实 schema 中带 `enum` 的字符串补 `maxLength`。
- `--self-test` 65 → 76 项。

## 批次 0066 改动范围（第三段：r4 攻击面验收与 G-021 口径）

- 自测新增 `T-NRM-12` 11 项，逐条复现 r4 四类缺陷并确认已由结构消除：`items: true`、元组 `items`、`enum`/`const` 跳过 `maxLength`、`x-prose-fields` 路径拼错、`contracts/schema/sub/` 未 lint 与未钉扎；另含官方元 schema、依赖缺失 fail-closed、20 条假设与 8 条 `positions` 不再被误杀。
- `GAP_LEDGER.md`：G-021 按 r4 实测改写（删除“均计入总量口径”，列出容量差额与 8 条未登记通道，给出反向误杀处置），维持 `open`；G-019 补记 0064–0066，维持 `open`；G-020 未改动。

## 批次 0067 改动范围（DP-ARTIFACT 语义收口）

- wheel 移至仓库外持久目录 `~/.local/share/pm-governance/wheels/`（不提交进 git），sha256 与登记值一致；`check_dependency_pins.py` 实际执行产物核对。
- `DP-ARTIFACT` 缺失从警告改为“无法评估”并退出 2；版本、安装树、产物三重全部强制；负例 9 → 10 项。
- 根 `README.md`、`scripts/README.md`、`adr/0019-mature-json-schema-validator.md` 写明路径、获取方式与退档口径。

## 批次 0068 改动范围（r5 复判：可机械修复与威胁模型收口）

- 依据：`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r5/REPORT.md`，sha256 `5373a537d05870dcf4f52756bf7e0012bc0128879e22df92cb85d86007258108`，基线 `3d7211c`。
- `scripts/check_dependency_pins.py`：安装树改为按 wheel 内 `RECORD` 逐文件重算内容哈希与大小，新增 `DP-TREE`（缺文件、多文件、内容不符）与 `DP-IMPORT`（导入路径必须落在分发目录内）；不再只对 `RECORD` 文本排序取摘要（旧摘要降为次级核对）。
- `scripts/test_dependency_pins.py`：临时安装树 + 临时 wheel 夹具，10 → 13 项；覆盖影子包 / `PYTHONPATH`、改安装树保留 `RECORD`、同名假 wheel、注入文件、缺逐文件数据。
- `scripts/check_no_raw_material.py`：`additionalProperties` 指针按未知键恢复为 `$.x` / `$.a.x`，`propertyNames` 恢复为 `$.m.<键>`；缺失本地 `$ref` 转 `RM-SCHEMA`；`pattern` 嵌套量词与 512 字符上限、schema 嵌套 64 层上限、`RecursionError` 归一；新增运行时行为探测。`--self-test` 76 → 82 项。
- `adr/0019-mature-json-schema-validator.md`：输出契约段（指针来源本仓库、消息取自库）、威胁模型段（不防护有权写本机 Python 环境者）、G-022 跟进；`README.md`、`scripts/README.md` 同步。
- `GAP_LEDGER.md`：G-021 以 `accepted` 关闭（修正 2,400 为单值路径上限）；新增 G-022 并以 `accepted` 关闭；G-019 补 0067–0068 与残留、维持 `open`；G-020 未改。

## 批次 0069 改动范围（r6 复判：三处口径对齐）

- 依据：`/home/wgz/projects/skills/2026-11-14/pm-governance-review/verify-g019-r6/REPORT.md`，sha256 `1db2586e…6bd1db`，基线 `bafcb04`。
- `scripts/check_no_raw_material.py`：撤掉 `pattern` 嵌套量词启发式，只保留 512 字符上限；删除依赖该启发式的负例，改为“官方 semver / dotted-id / dotted-version / list-of-pairs / `^(a|aa)+$` 全部放行”与“只按长度拒绝超长 `pattern`”，`--self-test` 82 → 83 项。
- `adr/0019-mature-json-schema-validator.md`：威胁模型一节明确 `pattern` 回溯风险不属于威胁模型成员（schema 为自写可信资产、非外部输入）；“不改变失败方向”改为分档表述（导入失败/产物缺失退 2，逐文件核对不符与运行时探测失败退 1）。
- `scripts/README.md`：`RM-SCHEMA` 退出码与 `RM-SCHEMA-LINT` 的 `pattern` 口径对齐实现；自测数量与 r6 用例更新。
- `GAP_LEDGER.md`：G-019 改“非针对性替换均阻断”，补记 `sitecustomize` 只替换 `validator_for` 时不阻断（G-022 信任边界），说明剩余项只有口径对齐；G-021、G-022 未动。

**不构成**：G-019 的关闭依据（该条仍 `open`，残留须非同源复核）；也不证明任何提交者身份。G-021 与 G-022 的关闭依据是本索引所指的 r5 报告，不是本索引。
