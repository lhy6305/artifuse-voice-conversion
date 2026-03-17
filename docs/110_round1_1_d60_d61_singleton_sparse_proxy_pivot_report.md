# `round1.1 / D60-D61 / singleton sparse proxy pivot` 报告

## 目的
- `post-D59` 诊断已经说明:
  - 当前矛盾是 `proxy principle mismatch`
  - 不是继续把 `clause>=2 short-pause` cohort 喂得更稳定
- 这轮正式做两件事:
  - 把 `formal_special_clause_shape_aux` 改成 `clause-free singleton sparse-frame supervision`
  - 用 `micro_pause_none_singleton_strict` 作为 late quick-screen 的首个 train-side proxy cohort
- 同时补一个最小 teacher-gate 对照，避免把收益误判成 gate 微调结果

先说人话:
- 这轮不是继续修 `D59`。
- 是承认 `D59` 那套代理原则不对，然后换一条真正贴近 special slice 的监督原则。

## 配置与实验
### D60
- 配置:
  - `configs/offline_mvp_train_d60_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_late_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-016-offline-mvp-d60-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-late-20step-calibration`
- 设计:
  - 保留 `D59` 的 `20 step` quick-screen 骨架
  - late targeted sampling 切到 `micro_pause_none_singleton_strict`
  - late teacher gate 也切到 `micro_pause_none_singleton_strict`
  - 新增 `singleton_sparse_proxy_aux`
    - 不依赖 `clause_role / clause_transition`
    - 直接约束:
      - low presence
      - low energy
      - low peak ratio
      - moderate fall

### D61
- 配置:
  - `configs/offline_mvp_train_d61_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_relaxed_late_20step_smallscale_seeded_shuffle.json`
- 实验:
  - `EXP-20260316-017-offline-mvp-d61-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-relaxed-late-20step-calibration`
- 设计:
  - 完全继承 `D60`
  - 只把 late teacher gate 从 `micro_pause_none_singleton_strict`
    放宽回:
    - `short_pause_no_terminal`
    - `required_within_special_duration_ceiling = true`
    - `required_utterance_structure_types = ['other']`
    - `required_final_terminal_types = ['none']`

## 关键事实
### 1. `D60` 证明原则切换本身有效，不再复刻 `D59` 的 validation-first 滑坡
- `D59 final = 2.480048 / 0.171791 / 2.994481 / 0.374835`
- `D60 final = 2.52274 / 0.112137 / 3.260251 / 0.435391`

相对 `D59`:
- validation `+0.042692`
- special delta `-0.059654`
- `zero_e_evt +0.26577`
- `zero_z_art +0.060556`

解释:
- validation 有代价，但 route 方向明显变了:
  - 不再是把 `D59` 那条 validation-first compromise 再演一遍
  - 而是重新拉回 special / control-aware 区间

### 2. `D60` 已经非常接近 `D33`，说明 singleton proxy principle 是真的可用，不是偶然噪声
- `D33 final = 2.52818 / 0.111677 / 3.312339 / 0.465828`
- `D60 final = 2.52274 / 0.112137 / 3.260251 / 0.435391`

相对 `D33`:
- validation 更好 `-0.00544`
- special 略差 `+0.00046`
- `zero_e_evt` 略弱 `-0.052088`
- `zero_z_art` 略弱 `-0.030437`

解释:
- 这轮新的 singleton sparse proxy，
  已经不是“只比 D59 好一点”的负结果修补。
- 它基本到达了 `D33` 级别的 special-route 区间，
  只是 control floor 还略弱一点。

### 3. late singleton supervision 在 `step11-20` 全程真实命中
- `D60 step11-20`
  - `loss_singleton_sparse_proxy_aux = 0.340000 -> 0.362918`
  - 全部非零
- late targeted sampling:
  - `phase_priority_record_count = 8`
  - 就是 `micro_pause_none_singleton_strict` 全集
- late teacher phase 也确实切到了目标 cohort

解释:
- 这轮不能再把结果解释成:
  - “可能只是没命中样本”
  - 或“aux 还没真正被激活”

### 4. `D61` 与 `D60` 数值级完全重合，说明这轮收益不是靠把 teacher gate 再收得更死
- `D61 final = 2.52274 / 0.112137 / 3.260251 / 0.435391`
- 与 `D60` 四项完全一致
- 训练 step loss 轨迹也逐点重合

解释:
- 一个合理推断是:
  - 在当前 `0.75` late singleton priority 下
  - late batch 已经基本由 strict singleton 样本主导
  - 所以把 teacher gate 从
    - `short_pause_no_terminal under ceiling`
    再收成
    - `micro_pause_none_singleton_strict`
  - 在这轮设置里没有带来新增 active subset

### 5. `D60` 仍然不足以改写当前 `default_minimax` handoff
- `D22 final = 2.444194 / 0.140001 / 3.299035 / 0.438936`
- `D60 final = 2.52274 / 0.112137 / 3.260251 / 0.435391`
- selector(`D22 / D29 / D33 / D60`, `budget=0.05`) 仍给出:
  - `selected_policy = default_minimax`
  - `selected_anchor = D22`

关键差异:
- `D60 vs D22`
  - validation `+0.078546`
  - special `-0.027864`
  - `zero_e_evt -0.038784`
  - `zero_z_art -0.003545`

解释:
- `D60` 已经证明 special principle 对了，
  但 validation tax 仍太高，
  还没跨过当前 `default_minimax` 预算门槛。

## 当前结论
1. `post-D59` 的原则切换是对的:
   - `clause-free singleton sparse proxy`
   - 确实比 `formal clause-shape` 更接近当前 special route
2. 当前最主要的有效变量是:
   - late singleton targeted sampling
   - `singleton_sparse_proxy_aux`
3. 当前最不值得继续抠的变量是:
   - strict vs relaxed late teacher gate
   - 在这轮设置下它是近似 no-op
4. 当前正式 route 不变:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`

## 当前建议
1. 不刷新当前 fixed handoff / stage-report。
2. 下一手不要继续在 `D60 / D61` 上细抠 teacher gate。
3. 更值得做的是把这条 singleton sparse proxy principle 移植到更强 validation backbone:
   - 优先考虑 `D22` family
   - 或做更短的 late singleton pulse / 更早衰减，削掉 validation tax
4. 若后续还要做 quick-screen follow-up，优先方向应是:
   - `D22 backbone + singleton sparse late pulse`
   - 而不是 `D59 family + more gate tuning`

## 产物
- `reports/training/offline_mvp_d60_singleton_sparse_micropause_exp016/`
- `reports/training/offline_mvp_d61_singleton_sparse_micropause_relaxed_teacher_exp017/`
- `reports/eval/offline_mvp_special_eval_d60_singleton_sparse_micropause_exp016/`
- `reports/eval/offline_mvp_special_eval_d61_singleton_sparse_micropause_relaxed_teacher_exp017/`
- `reports/eval/offline_mvp_ablations_d60_singleton_sparse_micropause_exp016/`
- `reports/eval/offline_mvp_ablations_d61_singleton_sparse_micropause_relaxed_teacher_exp017/`
- `reports/eval/offline_mvp_checkpoint_series_d60_singleton_sparse_micropause_exp016/`
- `reports/eval/offline_mvp_checkpoint_series_d61_singleton_sparse_micropause_relaxed_teacher_exp017/`
- `reports/eval/offline_mvp_special_eval_series_d60_singleton_sparse_micropause_exp016/`
- `reports/eval/offline_mvp_special_eval_series_d61_singleton_sparse_micropause_relaxed_teacher_exp017/`
- `reports/eval/offline_mvp_anchor_route_selection_round1_1_d22_d29_d33_d60_default_minimax/`
- `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d59_d60_d61_default_minimax/`
