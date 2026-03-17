# 138. round1.1 `D85 checkpoint-selected late-stop` 复核报告

## 背景
- `D85` 已经证明:
  - `D84 family` 拉到 `200-step` 后没有完全塌回旧形状
  - 它在 minimal family 内拿到了:
    - special
    - `e_evt`
- 但它也表现出典型 long-horizon late dynamics:
  - validation 继续改善
  - special 继续回吐
  - `e_evt` floor 继续回落

因此当前最值得补的不是再扩一个近邻 config，
而是先问:
- `D85` 的 late window 里，
  是否已经存在一个更合适的 checkpoint-selected late stop

## 方法
### 1. 单实验 checkpoint-selection / gate replay
- 输入:
  - `EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration`
- 输出:
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_d85_late075/`
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_d85_late075/`

### 2. 联合 long-horizon checkpoint-selection / gate replay
- 输入:
  - `D22 step200 final`
  - `D33 step200 final`
  - `D59 step200 final`
  - `D76 step200 final`
  - `D85 step200 final`
- 输出:
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_longwindow_d22_d33_d59_d76_d85_late075/`
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_longwindow_d22_d33_d59_d76_d85_late075/`

### 3. `D85 step150` synthetic anchor 回放
- 物化:
  - `reports/experiments/EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration.checkpoint-step150-anchor.metrics.json`
- 再并入:
  - minimal family route
  - full long-horizon route

## 先验校正
- 本轮继续沿用 `late_step_ratio = 0.75`
- 原因和 `D76` 一样:
  - `D85` 只有 `step50 / 100 / 150 / 200`
  - 若使用 `0.8`，
    late window 只会剩 `step200`

## 单实验 `D85` 结果
- final:
  - `step200 = 2.133474 / 0.231295 / 2.027351 / 0.433882`
- best late special:
  - `step150 = 2.161399 / 0.223913 / 2.066232 / 0.424634`

相对 final(`step150 - step200`):
- validation `+0.027925`
- special `-0.007382`
- `e_evt` `+0.038881`
- `z_art` `-0.009248`

解释:
- `step150` 是真实 late-stop 候选，
  不是 no-op。
- 但它不是 `D76 step150` 那种:
  - special / `e_evt` / `z_art` 三项一起改善
- `D85 step150` 的更准确形状是:
  - special 更好
  - `e_evt` 更好
  - `z_art` 略差
  - validation 更差

### gate replay 判断
- 除 `final_validation` 外，
  所有 late special gate 都会选:
  - `step150`
- aggregate 一致说明:
  - `improved_special_vs_final = 1`
  - `improved_validation_vs_final = 0`
  - `joint_anchor_beating_count = 0`

解释:
- `step150` 可以被写成:
  - `D85` 的 special-oriented late stop
- 但不能被写成:
  - 联合打败 `D85 final` 的新默认点

## 联合 long-horizon 结果
- `D22 step150 - step200`
  - validation `+0.041438`
  - special `-0.008364`
  - `e_evt` `+0.096244`
  - `z_art` `-0.010677`
- `D33 step150 - step200`
  - validation `+0.04579`
  - special `-0.010421`
  - `e_evt` `+0.062246`
  - `z_art` `-0.046173`
- `D59 step150 - step200`
  - validation `+0.019519`
  - special `-0.006347`
  - `e_evt` `+0.043562`
  - `z_art` `+0.033978`
- `D76 step150 - step200`
  - validation `+0.037223`
  - special `-0.011267`
  - `e_evt` `+0.125157`
  - `z_art` `+0.016229`
- `D85 step150 - step200`
  - validation `+0.027925`
  - special `-0.007382`
  - `e_evt` `+0.038881`
  - `z_art` `-0.009248`

联合 gate replay aggregate:
- `mean_delta_vs_final_validation = +0.034379`
- `mean_delta_vs_final_special = -0.008756`
- `mean_delta_vs_final_e_evt = +0.073218`
- `mean_delta_vs_final_z_art = -0.003178`

解释:
- `D85` 不是特例。
- 把 late-stop 当成制度，
  仍然稳定对应:
  - 略好的 special
  - 更好的 `e_evt`
  - 接近持平但略弱的 `z_art`
  - 更差的 validation
- 所以它仍是:
  - option study
  - 不是 free lunch

## `D85 step150` synthetic anchor 的结果
### 1. minimal family route
当把 `D85 step150` 并入:
- `D22 / D33 / D59 / D76 / D85`

route 变为:
- validation = `D76 step200`
- special = `D85 step150`
- `zero_e_evt = D85 step150`
- `zero_z_art = D33 step200`
- minimax = `D33 step200`

新阈值:
- `budget_to_minimax_anchor = 0.014763`
- `budget_to_special_anchor = 0.053463`

解释:
- `D85 step150` 确实比 `D85 step200` 更像 special / `e_evt` option。
- 但它的 validation tax 更高，
  反而把 special-push 所需预算从:
  - `0.025538`
  抬到了:
  - `0.053463`
- 这意味着在默认 `0.05` 预算下，
  它连 minimal family 的 special-push 都进不去。

### 2. full long-horizon route
当把 `D85 step150` 并入全量 long-horizon 集合后:
- validation = `D76`
- special = `D82`
- `zero_e_evt = D79`
- `zero_z_art + default_minimax = D33`

阈值保持:
- `budget_to_minimax_anchor = 0.014763`
- `budget_to_special_anchor = 0.040968`

解释:
- `D85 step150` 对 full route 没有产生制度级影响。
- 当前全量 route 里，
  它甚至不足以改写 special leader。

## 当前阶段正式判断
1. `D85 step150` 是真实的 checkpoint-selected late-stop 候选。
2. 但它只能被表述为:
   - 比 `D85 step200` 更激进的 special-oriented option
   - 不是新的 long-horizon default
3. 在 minimal family 内，
   它会进一步抬高 validation budget 要求。
4. 在 full long-horizon 内，
   它没有改写任何正式角色。

## 当前建议
1. 不要把 `D85 step150` 直接升格成新的 long-horizon anchor。
2. 更准确的写法应是:
   - `D85 step200 = family-level long-horizon representative`
   - `D85 step150 = family-level special-oriented late-stop option`
3. 若继续推进 outer punctuation 这条线，
   不要再优先做:
   - `step150/200` 附近的 late-stop 微调
   - checkpoint-option 堆叠
4. 信息量更高的后续动作仍是:
   - 设计新的 outer restoration 机制，
     重点补 `z_art`

## 产物
- 单实验:
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_d85_late075/`
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_d85_late075/`
- 联合 long-horizon:
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_longwindow_d22_d33_d59_d76_d85_late075/`
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_longwindow_d22_d33_d59_d76_d85_late075/`
- synthetic anchor:
  - `reports/experiments/EXP-20260316-041-offline-mvp-d85-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-200step-calibration.checkpoint-step150-anchor.metrics.json`
- minimal-family synthetic-anchor route:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d85_d85step150/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d85_d85step150_default_minimax/`
  - `reports/eval/offline_mvp_final_comparison_round1_1_longwindow_d22_d33_d59_d76_d85_d85step150_default_minimax/`
  - `reports/eval/offline_mvp_route_recap_round1_1_longwindow_d22_d33_d59_d76_d85_d85step150_default_minimax/`
- full long-horizon synthetic-anchor route:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_d85_d85step150/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_d85_d85step150_default_minimax/`
  - `reports/eval/offline_mvp_final_comparison_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_d85_d85step150_default_minimax/`
  - `reports/eval/offline_mvp_route_recap_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_d85_d85step150_default_minimax/`
