# 139. round1.1 `D86 / outer punctuation z_art-retarget 200-step` 报告

## 背景
- `D85` 已说明:
  - outer punctuation 这条 family 在 `200-step` 下不是假信号
  - 但它的 final 仍表现为:
    - special / `e_evt` 有优势
    - `z_art` 没有被真正拉回
- 因此本轮不再做同 family 小权重近邻，
  而是直接测试一个更明确的问题:
  - 如果把 late `z_art_influence_aux`
    从 strict singleton 本体
    改挂到 outer punctuation expansion pool，
    能否把 `z_art` restoration 直接补回来

## 本轮设计
### `D86`
- 配置:
  - `configs/offline_mvp_train_d86_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_zartretarget_200step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-042-offline-mvp-d86-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-200step-calibration`
- 相对 `D85` 的唯一主改动:
  - `z_art_influence_aux.pool_memberships`
    - `challenge_proxy_core`
    - -> `micro_singleton_anypunct_expansion`
  - 并且:
    - `required_within_special_duration_ceiling = true`
    - `weight_schedule = step11-25 linear ramp to 0.12`
- 保持不变:
  - `200-step`
  - late `D22` teacher
  - primary strict singleton sampler
  - `secondary_sampling -> micro_singleton_anypunct_expansion`
  - `punctuation_profile_aux -> micro_singleton_anypunct_expansion`

## 执行链
- 已完成:
  - `init-experiment`
  - `train-offline-mvp --dry-run`
  - `200-step` 正式训练
  - final `ablation_eval`
  - final `special_eval`
  - `checkpoint_series(step50/100/150/200)`
  - `special_eval_series(step50/100/150/200)`
  - 单实验 `checkpoint_selection(late075)`
  - 单实验 `checkpoint_gate_replay(late075)`
  - 联合 `D22 / D33 / D59 / D76 / D85 / D86`
    的 `checkpoint_selection(late075)` / `gate_replay(late075)`
  - `D86 step150 synthetic anchor` 物化
  - minimal / full long-horizon route 对照

## 指标口径
- shorthand final 继续记为:
  - `ablation baseline target_validation / special_delta / zero_e_evt / zero_z_art`
- route 判断继续使用:
  - `target_special_eval_model.target_validation.loss_total`

## `D86` final
- shorthand final:
  - `D86 = 2.130019 / 0.231570 / 1.816795 / 0.395586`
- route validation 列:
  - `2.135101`

- `step50 = 2.313514 / 0.186087 / 2.570719 / 0.308605`
- `step100 = 2.203182 / 0.209780 / 2.198116 / 0.461504`
- `step150 = 2.154244 / 0.225450 / 2.186293 / 0.504980`
- `step200 = 2.130019 / 0.231570 / 1.816795 / 0.395586`

解释:
- `D86 final` 没有形成新的 final anchor。
- 相对 `D85 final`，它的形状是:
  - validation 基本持平但略差
  - special 基本持平但略差
  - `e_evt` 明显更弱
  - `z_art` 也更弱
- 所以如果只看 final，
  `D86` 不能被写成对 `D85` 的正式升级。

## `D86 step150` late-stop 结果
- `D86 step150 - step200`:
  - validation `+0.021863`
  - special `-0.006120`
  - `zero_e_evt` `+0.369498`
  - `zero_z_art` `+0.109394`

解释:
- `D86 step150` 是真实的 checkpoint-selected late stop。
- 和 `D85 step150` 不同，
  它不是“special / e_evt 更好、z_art 略回吐”的老形状，
  而是:
  - special 更好
  - `e_evt` 大幅更好
  - `z_art` 也显著更好
  - validation 只付一小段 tax

### 对 `D85 step150` 的直接比较
- `D86 step150 - D85 step150`:
  - validation `-0.004435`
  - special `+0.001537`
  - `zero_e_evt` `+0.120061`
  - `zero_z_art` `+0.080346`

解释:
- `D86 step150` 没有拿下更低的 special loss。
- 但它以极小的 special 代价，
  换回了更好的 validation、`e_evt` 和 `z_art`。
- 更准确地说，
  它是当前 outer punctuation late-stop option 里
  更偏 dual-control restoration 的那个点。

## 联合 late-stop replay 结果
- `D22 / D33 / D59 / D76 / D85 / D86`
  的 late-stop aggregate 为:
  - `mean_delta_vs_final_validation = +0.032293`
  - `mean_delta_vs_final_special = -0.008317`
  - `mean_delta_vs_final_e_evt = +0.122598`
  - `mean_delta_vs_final_z_art = +0.015584`

解释:
- 加入 `D86` 后，
  这组 long-horizon late-stop aggregate
  不再是“`z_art` 近似持平或略弱”。
- `D86 step150` 把联合 replay 的 `z_art` 平均项
  重新推回了正值。
- 这说明:
  - outer punctuation + outer-pool `z_art` retarget
    没有改写 final
  - 但它确实改写了 late-stop option 的控制形状

## synthetic anchor route 结果
### 1. minimal family
集合:
- `D22 / D33 / D59 / D76 / D85 / D85step150 / D86 / D86step150`

结果:
- validation = `D76`
- special = `D85 step150`
- `zero_e_evt = D86 step150`
- `zero_z_art + default_minimax = D33`
- `budget_to_special_anchor = 0.053463`

解释:
- `D86 step150` 没把 minimal family 的 special leader
  从 `D85 step150` 手里抢过来。
- 但它明确改写了:
  - `zero_e_evt` leader
- 同时没有把 minimax / `z_art` 角色从 `D33` 挤掉。

### 2. full long-horizon
集合:
- `D22 / D33 / D59 / D76 / D77 / D78 / D79 / D80 / D81 / D82 / D83 / D85 / D85step150 / D86 / D86step150`

结果:
- validation = `D76`
- special = `D82`
- `zero_e_evt = D86 step150`
- `zero_z_art + default_minimax = D33`
- `budget_to_special_anchor = 0.040968`

解释:
- `D86 final` 本身没有改写 full route。
- 但 `D86 step150 synthetic anchor`
  已经把当前 checkpoint-option 层的 `zero_e_evt` 角色
  从 `D79 final` / `D85 step150` 前推到自己。
- 同时:
  - special 仍是 `D82`
  - default/minimax 仍是 `D33`
  - validation 仍是 `D76`

## 当前阶段正式判断
1. `D86 final` 不是新的正式 final anchor。
2. `D86 step150` 是真实且更强的 late-stop option:
   - 比 `D85 step150` 明显更像 dual-control restoration 点
   - 尤其补回了 `e_evt + z_art`
3. 在 minimal family 内，
   它改写的是:
   - `zero_e_evt`
   不是:
   - special / minimax
4. 在 full long-horizon 内，
   它目前最准确的制度位置是:
   - 新的 checkpoint-option 层 `zero_e_evt` leader
   - 不是新的 final-route special / minimax anchor

## 工程补记
- 本轮一度把四类 eval 并行跑到同一个 `experiment metrics` 文件上，
  触发了 last-writer-wins 覆写。
- 后续已顺序补回 `special_eval_series`，
  再完成 checkpoint-selection / route 分析。
- 这不是实验结论本身的一部分，
  但属于必须记入 pitfalls 的流程约束。

## 下一步
1. 不要把 `D86 final` 误写成对 `D85 final` 的正式刷新。
2. 更准确的写法应是:
   - `D86 step150 = current outer punctuation family 的 dual-control late-stop option`
   - 尤其负责更强的 `e_evt`
3. 若继续训练新实验，
   信息量最高的方向已经不是继续做 `D85/D86` family 小扫，
   而是问:
   - 能不能把 `D86 step150` 这种 late-window dual-control 形状
     更稳定地保到 final

## 产物
- 训练 / 评估:
  - `reports/training/offline_mvp/EXP-20260316-042.train_plan.json`
  - `reports/eval/offline_mvp_ablations_d86_exp20260316_042/`
  - `reports/eval/offline_mvp_special_eval_d86_exp20260316_042/`
  - `reports/eval/offline_mvp_checkpoint_series_d86_exp20260316_042/`
  - `reports/eval/offline_mvp_special_eval_series_d86_exp20260316_042/`
- checkpoint review:
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_d86_late075/`
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_d86_late075/`
  - `reports/eval/offline_mvp_checkpoint_selection_round1_1_longwindow_d22_d33_d59_d76_d85_d86_late075/`
  - `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_longwindow_d22_d33_d59_d76_d85_d86_late075/`
- synthetic anchor:
  - `reports/experiments/EXP-20260316-042-offline-mvp-d86-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-zartretarget-200step-calibration.checkpoint-step150-anchor.metrics.json`
- route:
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d85_d85step150_d86_d86step150/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d85_d85step150_d86_d86step150_default_minimax/`
  - `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_d85_d85step150_d86_d86step150/`
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_d85_d85step150_d86_d86step150_default_minimax/`
