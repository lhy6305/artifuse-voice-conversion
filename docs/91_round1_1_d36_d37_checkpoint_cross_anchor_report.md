# `round1.1 / D36+D37 / checkpoint-level cross-anchor follow-up` 报告

## 目的
- `D34 / D35` 已经说明:
  - 直接拿 `D22` 和 `D33 final` 做 final-to-final 互蒸，
  - 仍然只会落回 validation compressor 或 `D29` 式中间锚点
- 当前最合理的剩余假设是:
  - 问题可能不在 `D33` 这个 family 本身
  - 而在于该 family 真正有价值的入口更像 `D33 step10` 这种 special-only checkpoint

所以本轮只做最小 checkpoint-level follow-up:
- `D36 = D33 step10 init + D22 teacher`
- `D37 = D22 init + D33 step10 teacher`

## 配置与实验
### D36
- 配置:
  - `configs/offline_mvp_train_d36_round1_1_d33_step10_init_d22_teacher_checkpoint_cross_anchor_fused_hidden_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-053-offline-mvp-d36-round1-1-d33-step10-init-d22-teacher-checkpoint-cross-anchor-fused-hidden-20step-calibration`
- 设计:
  - `student init = D33 step10`
  - `teacher = D22 final`
  - 保持 `D33` 的 short-pause gate / sampler
  - `teacher_consistency.fused_hidden_weight = 0.05`

### D37
- 配置:
  - `configs/offline_mvp_train_d37_round1_1_d22_init_d33_step10_teacher_checkpoint_cross_anchor_fused_hidden_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260315-054-offline-mvp-d37-round1-1-d22-init-d33-step10-teacher-checkpoint-cross-anchor-fused-hidden-20step-calibration`
- 设计:
  - `student init = D22 final`
  - `teacher = D33 step10`
  - 保持 `D22` 的 core-only gate / sampler
  - `teacher_consistency.fused_hidden_weight = 0.05`

## 关键事实
### 1. 两条 checkpoint-level 线都不是挂空配置
- `D36 step20`
  - `loss_teacher_consistency = 0.319884`
  - `loss_teacher_event_consistency = 0.202148`
  - `loss_teacher_z_art_consistency = 0.072029`
  - `loss_teacher_fused_hidden_consistency = 0.913830`
- `D37 step20`
  - `loss_teacher_consistency = 0.184431`
  - `loss_teacher_event_consistency = 0.111081`
  - `loss_teacher_z_art_consistency = 0.037252`
  - `loss_teacher_fused_hidden_consistency = 0.721951`

解释:
- 这轮不是“改成 checkpoint-level 后 teacher 不起作用”。
- 两条线都真实吃到了 teacher pull。

### 2. `D36` 只是一个比 `D22` 更差的近邻复制品
- `D36 final`
  - `target_validation.loss_total = 2.450632`
  - `target_special_eval.delta_loss_total = 0.144661`
  - `zero_e_evt.delta_target_loss_total = 3.221708`
  - `zero_z_art.delta_target_loss_total = 0.407633`

对比 `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`:
- validation 更差 `+0.006438`
- special 更差 `+0.00466`
- `e_evt` 更弱 `-0.077327`
- `z_art` 更弱 `-0.031303`

解释:
- `D33 step10 init + D22 teacher`
  没有形成“保 special 再拉 validation”的新中间点。
- 它只把 `D33 step10` 拉回了一个比 `D22` 更差的近邻区。

### 3. `D37` 再次证明“special-only checkpoint 当 teacher”也只会压成 validation compressor
- `D37 final`
  - `target_validation.loss_total = 2.35571`
  - `target_special_eval.delta_loss_total = 0.199699`
  - `zero_e_evt.delta_target_loss_total = 2.652109`
  - `zero_z_art.delta_target_loss_total = 0.321586`

对比 `D34 final = 2.3506 / 0.201536 / 2.633041 / 0.310002`:
- 只是小幅数值扰动
- 形状完全同型

解释:
- 把 teacher 从 `D33 final` 换成更极端的 `D33 step10`，
  并没有把 `D22` 拉向更好的 special/control 中间点。
- 它仍然回到 validation compressor 方向。

### 4. checkpoint-level follow-up 没有隐藏更好的 checkpoint
- `D36`
  - `step20` 已优于其前段
  - 但整体仍不如 `D22`
- `D37`
  - `step20` 也只是比 `step10` 略缓和
  - 但整条轨迹都保持 compressor 形状

解释:
- 这轮也不是“checkpoint 选坏了”。
- checkpoint-level cross-anchor 最小变体本身没有打开新形状。

## 当前结论
1. `D33 step10` 作为 special-only checkpoint，本身值得记录，但它不是一个可直接互蒸成新 joint winner 的入口。
2. `D36` 证明:
   - `step10 init + D22 teacher`
   - 只能收敛到一个比 `D22` 更差的近邻复制品。
3. `D37` 证明:
   - `D22 init + step10 teacher`
   - 仍只会回到 validation compressor。
4. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

## 当前建议
1. 暂停继续做 `D33 step10` 的最小 checkpoint-level cross-anchor 同构变体。
2. 若继续推进，优先级应转向:
   - 更结构化的 checkpoint selection / routing
   - 或更强的 target / gate 级重构
   - 而不是继续做 `step10` 与 final 之间的简单互蒸
