# 112. round1.1 `D64-D67 / D60 tail-strength decomposition` 报告

## 背景
- 在 `D60` 已成为当前 `post-D59` 主线上最有效的 singleton sparse route 之后，
  当前剩余问题是:
  - 能否在不丢掉 `D60` 的 singleton principle 收益前提下，
  - 继续削掉它相对 `D22` 的 validation tax。
- 本轮先做两种直接 tail 缩减:
  - `D64 = shorter tail`
  - `D65 = weaker tail`
- 结果不理想后，再进一步把 `D65` 的“变弱”拆成两个单变量:
  - `D66 = aux weight lighter`
  - `D67 = sampler ratio lighter`

## 实验设计
### `D64`
- 配置:
  - `configs/offline_mvp_train_d64_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_shorttail_15step_smallscale_seeded_shuffle.json`
- 唯一原则变化:
  - 总步数从 `20 -> 15`
  - late singleton phase 从 `step11-20` 缩到 `step11-15`

### `D65`
- 配置:
  - `configs/offline_mvp_train_d65_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_weaktail_20step_smallscale_seeded_shuffle.json`
- 唯一原则变化:
  - late `priority_ratio: 0.75 -> 0.5`
  - `singleton_sparse_proxy_aux.weight: 0.10 -> 0.08`

### `D66`
- 配置:
  - `configs/offline_mvp_train_d66_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_auxlighter_20step_smallscale_seeded_shuffle.json`
- 唯一原则变化:
  - 只改 `singleton_sparse_proxy_aux.weight: 0.10 -> 0.08`
  - late sampler 仍保持 `0.75`

### `D67`
- 配置:
  - `configs/offline_mvp_train_d67_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_samplerlighter_20step_smallscale_seeded_shuffle.json`
- 唯一原则变化:
  - 只改 late `priority_ratio: 0.75 -> 0.5`
  - aux weight 仍保持 `0.10`

## final 结果
- `D60 = 2.52274 / 0.112137 / 3.260251 / 0.435391`
- `D64 = 2.539564 / 0.154003 / 3.012511 / 0.400641`
- `D65 = 2.482579 / 0.172447 / 2.980073 / 0.375719`
- `D66 = 2.522723 / 0.11214 / 3.260339 / 0.435397`
- `D67 = 2.482594 / 0.172458 / 2.979895 / 0.375695`

指标顺序固定为:
- `target_validation / special_delta / zero_e_evt / zero_z_art`

## 关键对比
### `D64` 对 `D60`
- validation 更差 `+0.016824`
- special 更差 `+0.041866`
- `zero_e_evt` 更差 `-0.24774`
- `zero_z_art` 更差 `-0.03475`

结论:
- `short tail` 不是降低 validation tax 的办法
- 它连 validation 自身都没有保住，同时还明显伤 special/control floor

### `D65` 对 `D60`
- validation 更好 `-0.040161`
- 但 special 更差 `+0.06031`
- `zero_e_evt` 更差 `-0.280178`
- `zero_z_art` 更差 `-0.059672`

结论:
- `weaker tail` 确实能换来 validation
- 但代价是 singleton principle 的核心收益大幅回吐
- 它整体更像退回到接近 `D59` 的 validation-first compromise

### `D66` 对 `D60`
- 四项结果近乎逐点一致:
  - `D60 = 2.52274 / 0.112137 / 3.260251 / 0.435391`
  - `D66 = 2.522723 / 0.11214 / 3.260339 / 0.435397`

结论:
- `singleton_sparse_proxy_aux.weight: 0.10 -> 0.08`
  在当前 `D60` family 上基本是 no-op

### `D67` 对 `D65`
- 四项结果也近乎逐点一致:
  - `D65 = 2.482579 / 0.172447 / 2.980073 / 0.375719`
  - `D67 = 2.482594 / 0.172458 / 2.979895 / 0.375695`

结论:
- `D65` 的回退几乎全部来自:
  - late `priority_ratio: 0.75 -> 0.5`
- 而不是 aux weight 下降

## 解释
- 这轮可以把 `D60` family 的 tail-strength 问题拆清楚:
  1. `shorter tail` 不行
  2. `lighter aux weight` 基本没效果
  3. 真正有杠杆、但也是高风险的变量是 late sampler ratio
- 更具体地说:
  - `D60` 的 singleton principle 收益，
    当前主要依赖 late batch 里足够强的 singleton cohort 占比
  - 把 late sampler ratio 从 `0.75` 降到 `0.5`
    会明显把 special / `e_evt` / `z_art` 收益打掉
  - 单纯把 aux 权重从 `0.10` 降到 `0.08`
    基本不足以改变 final route

先说人话:
- `D60` 这条线不是“尾巴太长了”，也不是“aux 稍微太重了”。
- 真正关键的是 late singleton batch 占比。
- 一旦把这个占比往下拉，validation 会变好一点，但 special-aware 原则基本就掉光了。

## route 结论
- 新 selector:
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_d22_d29_d33_d60_d64_d65_d66_d67_default_minimax/`
- 结果继续保持:
  - `selected_policy = default_minimax`
  - `selected_anchor = D22`
- 新 final comparison:
  - `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d59_d60_d61_d64_d65_d66_d67_default_minimax/`

## 当前阶段正式结论
1. `D60` 仍是当前 `post-D59` singleton sparse 主线上最好的 quick-screen 点。
2. `D60` family 的简单 tail-length / tail-strength sweep 已基本收口。
3. `aux weight` 不是当前主变量；late singleton `sampler ratio` 才是主杠杆。
4. 但这个主杠杆一旦往下调，就会明显把 route 拖回 validation-first compromise。

## 下一步
- 暂停继续做:
  - `D60` family 的 short-tail
  - `D60` family 的 aux-weight 微调
  - `D60` family 的 sampler-ratio 下调 sweep
- 若还要继续削 singleton principle 的 validation tax，
  下一手应离开这条简单 tail-strength 轴，
  转向:
  - 更上游的 backbone / handoff 形状
  - 或新的 matched-horizon / checkpoint-selected 设计
