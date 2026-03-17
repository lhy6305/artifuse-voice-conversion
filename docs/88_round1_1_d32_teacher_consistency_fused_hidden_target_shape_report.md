# `round1.1 / D32 / teacher-consistency fused-hidden target-shape probe` 报告

## 目的
- 在 `D31 acoustic` 已证明“只在同一条 core gate 上加一个轻量输出头”信息增益有限之后，
- 继续测试一个结构差异更大的 distillation target shape:
  - 不只蒸馏 `event + z_art`
  - 而是追加 teacher 的 `fused_hidden`
- 本轮目标是看:
  - 更靠近 control-fusion 内部态的 teacher pull，
  - 能不能把 `D22` 的 `e_evt / z_art` 保得更稳，
  - 同时不把 `default_minimax` 的 special 继续推坏

## 代码与配置
### 新增训练能力
- `src/v5vc/train_entry.py`
  - `teacher_consistency` 新增:
    - `fused_hidden_weight`
    - `loss_teacher_fused_hidden_consistency`

### D32
- 配置:
  - `configs/offline_mvp_train_d32_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_fused_hidden_smallscale_30_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-049-offline-mvp-d32-round1-1-d7-init-d10-teacher-consistency-fused-hidden-30step-calibration`
- route:
  - `default_minimax`
- 设计:
  - `student init = D7 final`
  - `teacher = D10 final`
  - `teacher_consistency.pool_memberships = ["challenge_proxy_core"]`
  - `teacher_consistency.fused_hidden_weight = 0.05`
  - `teacher_consistency.acoustic_weight = 0.0`

## 关键事实
### 1. fused-hidden consistency 不是挂空配置
- `step1`
  - `loss_teacher_consistency = 0.034267`
  - `loss_teacher_event_consistency = 0.009645`
  - `loss_teacher_z_art_consistency = 0.019376`
  - `loss_teacher_fused_hidden_consistency = 0.104925`
- `step30`
  - `loss_teacher_consistency = 0.475910`
  - `loss_teacher_event_consistency = 0.214713`
  - `loss_teacher_z_art_consistency = 0.170620`
  - `loss_teacher_fused_hidden_consistency = 1.811542`

解释:
- 这轮不是“新 target shape 没接上”。
- fused-hidden consistency 在训练全过程里持续 active，
  而且量级明显高于 `acoustic` 追加项。

### 2. `D32 final` 是一个比 `D31` 更有价值、但仍没改写 minimax 的点
- `D32 final`
  - `target_validation.loss_total = 2.442393`
  - `target_special_eval.delta_loss_total = 0.143828`
  - `zero_e_evt.delta_target_loss_total = 3.299576`
  - `zero_z_art.delta_target_loss_total = 0.434057`

对比 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
- validation 略好 `-0.001801`
- final special 略差 `+0.003827`
- `e_evt` 略强 `+0.000541`
- `z_art` 略弱 `-0.004879`

解释:
- `D32` 不是简单复刻 `D22`。
- 它第一次把 `zero_e_evt` 推成了当前 comparison 里的 leader，
  同时 validation 仍略优于 `D22`。
- 但它没有把 special gap 补回来，
  所以还不足以取代 `D22` 成为新的 `default_minimax` anchor。

### 3. checkpoint / special series 同样没有隐藏更好的终点
- special eval series:
  - `step10 = 2.592867 / 0.137444`
  - `step20 = 2.473411 / 0.171443`
  - `step30 = 2.442393 / 0.143828`
- checkpoint ablation series:
  - `step10 zero_e_evt / zero_z_art = 3.042418 / 0.416722`
  - `step20 zero_e_evt / zero_z_art = 3.063655 / 0.405321`
  - `step30 zero_e_evt / zero_z_art = 3.299576 / 0.434057`

解释:
- `step10` 虽然 special 略好于 `D22`，
  但 validation 远差，且 `e_evt / z_art` 也没站住。
- `step20` 没有形成 joint improvement。
- `step30` 已经是这轮最接近“保住 `D22` validation，同时把 `e_evt` 再顶一点”的点。
- 因此 `D32` 的问题不是“final 选坏了”，
  而是:
  - fused-hidden target shape 的收益主要落在 `e_evt`
  - 但在当前 core gate 下还不足以把 formal special 一起拉回来

### 4. route-context comparison 已确认 `D32` 是新的 control-side reference，但不是新的 minimax anchor
- 在 `D22 / D26 / D29 / D31 / D32` 的 `default_minimax` comparison 中:
  - `D32` 相对 route anchor `D22`
    - validation `-0.001801`
    - special `+0.003827`
    - `e_evt +0.000541`
    - `z_art -0.004879`
- 同时 `D32` 已成为该 comparison 的:
  - `zero_e_evt` leader

这说明:
- `D32` 比 `D31` 更接近“有独立保留价值的新 target-shape 点”
- 但它仍然没有跨过当前 minimax 通过线
- 当前 route 结论保持不变:
  - `D22 = default_minimax`
  - `D29 = validation`
  - `D26 = special / z_art`

## 当前结论
1. `D32` 证明 fused-hidden 这类更内部态的 distillation target shape 确实比 `acoustic` 加项更有信息增益。
2. `D32` 已经形成了一个可以保留的 control-side reference:
   - validation 仍稳
   - `e_evt` 还略有提升
3. 但在当前同一条 `challenge_proxy_core` gate 上，
   fused-hidden consistency 仍不足以把 special gap 一起补回来。
4. `D32` 不升为新的 minimax anchor。

## 当前建议
1. `D22` 继续保持当前 `default_minimax` anchor。
2. `D32` 可保留为 fused-hidden target-shape reference，但不直接升 anchor。
3. 若继续推进 fused-hidden 路线，更值得优先试:
   - 把 `D32` 的 target shape 和 `D26` 已验证有效的 short-pause gate / sampler 组合
   - 而不是继续在同一条 core gate 上做同构 weight 小 sweep
