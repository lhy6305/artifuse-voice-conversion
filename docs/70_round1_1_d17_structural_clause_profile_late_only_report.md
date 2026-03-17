# `round1.1 / D17 / structural_clause_profile late-only` 报告

## 目的
- 在 `D15 / D16` 已经把 challenge-profile family 基本收口后，
- 继续验证“更强的结构监督定义变化”是否值得走下去，
- 但这次不再让 challenge 邻域 profile 主导 late phase，
- 而是只在 `structural_clause_ge4` 上新增一条 late-only 的 sample-level structural profile aux。

## 代码与配置
### 新增代码
- `src/v5vc/offline_mvp/losses.py`
  - 新增 `structural_clause_profile_aux`
  - 支持独立 `weight_schedule`
- 同步更新:
  - `src/v5vc/train_entry.py`
  - `src/v5vc/special_eval.py`
  - `src/v5vc/ablation_eval.py`
  - `src/v5vc/special_eval_series.py`

### D17
- 实验:
  - `EXP-20260315-043-offline-mvp-d17-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-structural-clause-profile-late-only-100step-calibration`
- 配置:
  - `configs/offline_mvp_train_d17_round1_1_special_proxy_core_clause_ge4_early_handoff_zart_influence_structural_clause_profile_late_only_smallscale_100_seeded_shuffle.json`
- 基线:
  - `D7`

### 配置变化
`D17` 相对 `D7` 的唯一主改动是:
- 保留 `D7` sampler
- 保留 `D7` 的 `z_art_influence_aux`
- 新增:
  - `structural_clause_profile_aux.pool_memberships = ["structural_clause_ge4"]`
  - `structural_clause_profile_aux.weight = 0.08`
  - `weight_schedule = step61-80 linear ramp to 0.08`

也就是说:
- challenge proxy 仍只负责前段进入轨迹与 explicit-control 保留
- 新 aux 只负责 handoff 之后的 structural late shaping

## 关键结果
### 1. `D17` 不是空实现，late-only structural aux 确实在后段生效
- dry-run step0:
  - `loss_structural_clause_profile_aux = 0.057874`
  - effective `weight = 0.0`
- training step70:
  - `loss_structural_clause_profile_aux = 0.04029`
  - effective `weight = 0.0378947`
- training step80:
  - `loss_structural_clause_profile_aux = 0.009333`
  - effective `weight = 0.08`
- training step90:
  - `loss_structural_clause_profile_aux = 0.013067`
  - effective `weight = 0.08`
- training step100:
  - `loss_structural_clause_profile_aux = 0.073294`
  - effective `weight = 0.08`

解释:
- 这轮不是“配置挂空”。
- 新 aux 在 late window 的确持续参与了优化。

### 2. 但 `D17 final` 几乎数值级复刻 `D7 final`
- `D17 final`
  - `target_validation.loss_total = 2.730107`
  - `target_special_eval.delta_loss_total = -0.003152`
  - `zero_e_evt.delta_target_loss_total = 3.491084`
  - `zero_z_art.delta_target_loss_total = 0.599597`

对比 `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`:
- validation 只差 `0.000013`
- final special 只差 `0.000021`
- `e_evt` 只差 `0.001359`
- `z_art` 只差 `0.000013`

这不是“接近”。
这是当前精度下的近似重合。

### 3. `D17` 的 late-window 也与 `D7` 几乎重合
- `D17 step80 = 3.688579 / -0.306971 / 2.659684 / 1.084378`
- `D17 step90 = 3.427158 / -0.342993 / 2.807291 / 0.509014`
- `D17 step100 = 2.730107 / -0.003152 / 3.491084 / 0.599597`

对比 `D7`:
- `D7 step80 = 3.688559 / -0.306983 / 2.65962 / 1.084382`
- `D7 step90 = 3.427092 / -0.342982 / 2.806937 / 0.50902`
- `D7 step100 = 2.73012 / -0.003131 / 3.489725 / 0.59961`

解释:
- `D17` 没有把 `D7` 推到新的终点，
- 也没有改变 `step80 -> step90 -> step100` 的 late-window 形状，
- 基本就是在同一条轨迹上做了数值级扰动。

### 4. 这条负证据比 `D15` 更强
`D15` 的问题是:
- challenge-profile 在 late phase 基本没继续吃到样本，
- 所以只能说“没有形成新 regime”

而 `D17` 的事实是:
- 新 aux 明确在 late phase 持续生效，
- 但轨迹仍近似复刻 `D7`

所以正式结论应是:
- 当前这种“基于 sidecar 的 sample-level event mean / peak ratio structural profile”
- 即使只挂在 `structural_clause_ge4`
- 即使只在 late phase 启动
- 也没有形成新的行为杠杆

## 当前结论
- `structural_clause_profile_aux` 工程上是成立的，late-only schedule 也确实命中了目标阶段。
- 但 `D17` 没有形成新的解，反而给出更硬的负证据:
  - 不是因为 late exposure 不足
  - 而是因为当前这种 sample-level structural profile 目标本身不足以改写 `D7` 轨迹

## 当前建议
1. 保留 `structural_clause_profile_aux` 代码，但不继续优先扩展这个 family。
2. 不把 `D17` 升为默认方案。
3. 当前若继续推进结构监督方向，不应再做:
   - `structural_clause_profile_aux` 纯权重 sweep
   - `structural_clause_profile_aux` 纯启动步位 sweep
4. 下一步更值得试的是:
   - boundary-local / frame-local 的结构监督
   - 而不是继续做 sample-level event mean profile

## 备注
- 本轮 `init-experiment` 自动生成的记录是 `EXP-...033-d17`，但实际训练执行使用的是 `EXP-...043-d17`。
- 已补齐 `EXP-...043-d17` 的 experiment record 与 metrics skeleton，并以 `043` 作为本轮 canonical run id。
