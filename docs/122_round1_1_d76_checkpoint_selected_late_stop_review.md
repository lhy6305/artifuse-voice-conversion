# 122. round1.1 `D76 checkpoint-selected late stop` 复核报告

## 背景
- `D76` 已经证明:
  - `D75 family` 拉到 matched long horizon(`200+`) 后没有塌掉
  - 纯 `200-step` 同 horizon 下，`D76 step200` 成为新的 validation / minimax anchor
- 但 `D76` 也表现出典型 long-horizon late dynamics:
  - validation 持续变好
  - special 持续变差
  - `e_evt` / `z_art` floor 持续回落

因此当前最值得补的不是再扩 family，
而是先看:
- `D76` 的 late window 里，
  是否已经存在一个更合适的 checkpoint-selected late stop

## 方法
### 1. 单实验 checkpoint-selection / gate replay
- 输入:
  - `EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration`
- 输出:
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_d76_late075/`
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_d76_late075/`

### 2. 联合 long-horizon checkpoint-selection / gate replay
- 输入:
  - `D22 step200 final`
  - `D33 step200 final`
  - `D59 step200 final`
  - `D76 step200 final`
- 输出:
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_longwindow_d22_d33_d59_d76_late075/`
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_longwindow_d22_d33_d59_d76_late075/`

### 3. `D76 step150` synthetic anchor 回放
- 物化:
  - `reports/experiments/EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration.checkpoint-step150-anchor.metrics.json`
- 再并入 long-horizon route:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d76step150/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d76step150_default_minimax/`
  - `reports/eval/offline_mvp_final_comparison_round1_1_longwindow_d22_d33_d59_d76_d76step150_default_minimax/`
  - `reports/eval/offline_mvp_route_recap_round1_1_longwindow_d22_d33_d59_d76_d76step150_default_minimax/`

## 先验校正
- 这轮没有沿用 `late_step_ratio = 0.8`
- 因为 `D76` 只有:
  - `step50 / 100 / 150 / 200`
- 如果仍用:
  - `ceil(200 * 0.8) = 160`
- 那 late window 只会剩:
  - `step200`

所以本轮统一改成:
- `late_step_ratio = 0.75`
- 让:
  - `step150`
  - `step200`
  都进入 late window

## 单实验 `D76` 结果
- final:
  - `step200 = 2.107936 / 0.246555 / 1.937766 / 0.424651`
- best late special:
  - `step150 = 2.145159 / 0.235288 / 2.062923 / 0.44088`

相对 final(`step150 - step200`):
- validation `+0.037223`
- special `-0.011267`
- `e_evt` `+0.125157`
- `z_art` `+0.016229`

解释:
- `step150` 是真实的 late-stop 候选，
  不是 no-op。
- 而且它不是“special 换控制”式的坏交易；
  在 `D76` 上它同时改善:
  - special
  - `e_evt`
  - `z_art`
- 付出的代价只有:
  - validation `+0.037223`

### gate replay 判断
- 除 `final_validation` 外，
  所有 late special gate 都会选:
  - `step150`
- 但它们的 aggregate 也一致说明:
  - improved_special_vs_final = `1`
  - improved_validation_vs_final = `0`
  - joint_anchor_beating_count = `0`

解释:
- `step150` 可以被解释成:
  - `D76` 的 special-oriented late stop
- 但不能被解释成:
  - 联合打败 `D76 final` 的新默认点

## 联合 long-horizon 结果
### 1. 不只是 `D76`，`D22 / D33 / D59` 也都有同构的 late-stop 形状
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

解释:
- 这说明 long-horizon late-stop 不是 `D76` 独有现象。
- `150 -> 200` 这一段整体就是:
  - validation 继续往下压
  - special / control 有一定幅度回吐

### 2. 联合 gate replay 里，所有 late special gate 都会退到各自的 `step150`
- aggregate:
  - `mean_delta_vs_final_validation = +0.035993`
  - `mean_delta_vs_final_special = -0.0091`
  - `mean_delta_vs_final_e_evt = +0.081802`
  - `mean_delta_vs_final_z_art = -0.001661`

解释:
- 把 late-stop 当成一条制度，
  会稳定换来:
  - 略好的 special
  - 更好的 `e_evt`
  - 几乎持平的 `z_art`
  - 但始终更差的 validation
- 所以它更像:
  - route option
  - 而不是 free lunch

## `D76 step150` synthetic anchor 的决定性结果
当把 `D76 step150` 真正物化成 anchor 再并入 pure long-horizon route 后：

- validation = `D76 step200`
- special = `D76 step150`
- `zero_e_evt = D76 step150`
- `zero_z_art = D33 step200`
- minimax = `D33 step200`

新阈值:
- `budget_to_minimax_anchor = 0.014763`
- `budget_to_special_anchor = 0.037223`

这意味着:
1. `D76 step150` 自己不是 minimax
2. 一旦允许它作为正式候选进入同 horizon route，
   反而会把 minimax 从:
   - `D76 step200`
   切回:
   - `D33 step200`

解释:
- `D76 step150` 虽然 special / `e_evt` 更强，
  但 `z_art` floor 仍明显不够高，
  不足以扛住 minimax
- 于是它一出现，
  route 的 least-worst 平衡点就回到:
  - control 更完整的 `D33 step200`

## 当前阶段正式判断
1. `D76 step150` 是真实的 checkpoint-selected late-stop 候选。
2. 但它当前只能被表述为:
   - special-oriented late-stop option
   - 不是 long-horizon 默认 anchor
3. `D76 step200` 仍然是:
   - 不引入 synthetic checkpoint anchor 时的 pure long-horizon validation / minimax anchor
4. 一旦把 checkpoint anchor 也纳入正式候选集合，
   minimax 会切回:
   - `D33 step200`

## 当前建议
1. 不要把 `D76 step150` 直接升格成新的 long-horizon default。
2. 当前更准确的写法应是:
   - `D76 step200 = long-horizon validation-first default`
   - `D76 step150 = long-horizon special-oriented late stop`
3. 若后续真的要把 late-stop 制度化，
   不能只看 `D76` 单实验；
   需要直接承认:
   - 一旦允许 checkpoint anchor 进入正式 route，
     当前 minimax 语义会被改写成 `D33`

## 产物
- 单实验:
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_d76_late075/`
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_d76_late075/`
- 联合 long-horizon:
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_longwindow_d22_d33_d59_d76_late075/`
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_longwindow_d22_d33_d59_d76_late075/`
- synthetic anchor:
  - `reports/experiments/EXP-20260316-032-offline-mvp-d76-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-late-fusedhidden-boost-200step-calibration.checkpoint-step150-anchor.metrics.json`
- synthetic-anchor route:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d76step150/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d76step150_default_minimax/`
  - `reports/eval/offline_mvp_final_comparison_round1_1_longwindow_d22_d33_d59_d76_d76step150_default_minimax/`
  - `reports/eval/offline_mvp_route_recap_round1_1_longwindow_d22_d33_d59_d76_d76step150_default_minimax/`
