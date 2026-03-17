# 113. round1.1 `D68-D69 / D60 upstream D22 late handoff` 报告

## 背景
- 在 `D60` family 的 simple tail-strength 轴已经基本收口之后，
  下一步要验证的不是:
  - tail 再短一点
  - aux 再轻一点
  - sampler ratio 再低一点
- 而是更上游的问题:
  - `D60` 的 late teacher source / handoff shape
    能否用更接近 `D22` 的方式，
    把 validation tax 再削掉一点，
    同时不丢掉 singleton sparse principle 的 special-aware 收益。

## 实验设计
### `D68`
- 配置:
  - `configs/offline_mvp_train_d68_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_teacher_source_d22late_20step_smallscale_seeded_shuffle.json`
- 原则变化:
  - 保持 `D60` 的:
    - late singleton targeted sampling
    - `singleton_sparse_proxy_aux`
    - late `fused_hidden_weight = 0.05`
    - late teacher pool = `micro_pause_none_singleton_strict`
  - 只把 late teacher checkpoint source 从:
    - `D29 step10`
    - 改成 `D22 step30`

### `D69`
- 配置:
  - `configs/offline_mvp_train_d69_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_d22like_latehandoff_20step_smallscale_seeded_shuffle.json`
- 原则变化:
  - 在 `D68` 基础上进一步把 late handoff shape 调成更 `D22-like`
  - 具体为:
    - late `fused_hidden_weight: 0.05 -> 0.0`
    - late teacher pool:
      - `micro_pause_none_singleton_strict -> challenge_proxy_core`
  - 但仍保留:
    - late singleton targeted sampling
    - `singleton_sparse_proxy_aux`

## final 结果
- `D60 = 2.52274 / 0.112137 / 3.260251 / 0.435391`
- `D68 = 2.522315 / 0.112037 / 3.26795 / 0.434833`
- `D69 = 2.523948 / 0.111144 / 3.271397 / 0.434243`

指标顺序固定为:
- `target_validation / special_delta / zero_e_evt / zero_z_art`

## 关键对比
### `D68` 对 `D60`
- validation 更好 `-0.000425`
- special 更好 `-0.0001`
- `zero_e_evt` 更好 `+0.007699`
- `zero_z_art` 更差 `-0.000558`

结论:
- `D68` 确实没有退化
- 但改善量级只有 epsilon 级
- 更合理的解释是:
  - late teacher source 改成 `D22 step30`
    只带来极轻微再平衡
  - 没有形成新的 route

### `D69` 对 `D60`
- validation 更差 `+0.001208`
- special 更好 `-0.000993`
- `zero_e_evt` 更好 `+0.011146`
- `zero_z_art` 更差 `-0.001148`

结论:
- 把 late handoff shape 再调成更 `D22-like`，
  也没有把这条线推入新的 regime
- 它只是把:
  - special / `e_evt`
    再往前拽一小点
  - 同时把 validation / `z_art`
    再吐回去一小点

### `D69` 对 `D68`
- validation 更差 `+0.001633`
- special 更好 `-0.000893`
- `zero_e_evt` 更好 `+0.003447`
- `zero_z_art` 更差 `-0.00059`

结论:
- `D69` 本质上只是 `D68` 的同盆地再平衡
- 没有证据表明:
  - 更 `D22-like` 的 late pool / fused-hidden 形状
  - 会自然消掉 `D60` 的 validation tax

## 解释
- 这轮说明:
  - `D60` family 的问题不只是 late teacher source 选错了
  - 也不只是 late pool / fused-hidden 形状不够像 `D22`
- 即使把 late handoff upstream shape 往 `D22` 靠，
  当前 singleton sparse route 也只是围绕 `D60` 做极小幅再平衡，
  而不会自己长成新的 minimax anchor。

先说人话:
- 这轮不是没变化。
- 是有变化，但小到不值得解释成“新路线”。
- `D68 / D69` 更像在 `D60` 附近拧了两个很弱的旋钮，
  不是打开了一个新的门。

## route 结论
- 新 selector:
  - `reports/eval/offline_mvp_anchor_route_selection_round1_1_d22_d29_d33_d60_d68_d69_default_minimax/`
- 结果继续保持:
  - `selected_policy = default_minimax`
  - `selected_anchor = D22`
- 新 route analysis 里还出现了一个值得单独说明的变化:
  - raw `special_push` anchor 已从 `D33` 变成 `D69`
  - 但这只来自 `special_delta` 的极小领先:
    - `D69 = 0.111144`
    - `D33 = 0.111677`
  - 同时 `D33` 仍保持:
    - `best zero_e_evt = 3.312339`
    - `best zero_z_art = 0.465828`

结论:
- 这更像 special-route selector 上的 epsilon 级换人，
  不是正式三锚点口径已经被稳定改写。
- 当前 fixed handoff 仍不应贸然把
  - `D33 = special / e_evt / z_art`
  直接改写成 `D69`。
- 新 final comparison:
  - `reports/eval/offline_mvp_final_comparison_round1_1_d22_d29_d33_d59_d60_d61_d64_d65_d66_d67_d68_d69_default_minimax/`

补充说明:
- 这轮在生成 selector 时，
  顺手暴露了 route-analysis 的一个工具链坑:
  - 当某个 policy 没有 eligible anchor 时，
    旧实现会直接报错退出
- 现已修成:
  - 将该 policy 记为 `unavailable`
  - 不再阻断默认 selector / final comparison 产物生成

## 当前阶段正式结论
1. `D68 / D69` 都没有改写 `D60` 是当前 singleton sparse 主线 local optimum 的结论。
2. 把 late teacher source 改到 `D22`，或把 late handoff shape 调成更 `D22-like`，都只产生 epsilon 级再平衡。
3. 当前 `D60` family 的“更上游 D22-late-handoff”轴也可以暂时收口。
4. 当前 selector 继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33` 仍是更稳的 `special / e_evt / z_art` 官方口径
   - `D69` 只是在 raw `special_push` 上以 epsilon 级优势短暂领先

## 下一步
- 暂停继续做:
  - `D60 -> D22 late teacher source` 小变体
  - `D60 -> D22-like late handoff shape` 小变体
- 若继续推进 singleton sparse 主线，
  更值得优先尝试:
  - matched-horizon / checkpoint-selected 设计
  - 或比当前 teacher-source / handoff-shape 微调更强的 backbone 级变化
