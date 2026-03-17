# `round1.1 / D20 / clause_ge4_no_final_terminal` 报告

## 目的
- 在 `D18 / D19` 证明“整包 `structural_clause_ge4` 的 boundary-local late shaping 不能打破 `D7` tradeoff”后，
- 继续验证一个更高层的 supervision-definition 拆分是否值得推进：
  - 不是再改 loss 形状；
  - 而是先把 `structural_clause_ge4` 拆成更干净的子池。
- 本轮选择的是：
  - `structural_clause_ge4_no_final_terminal`
  - 也就是 `structural_clause_ge4 ∩ structural_no_final_terminal`

先说人话：
- 这轮想验证的不是“再换一个更聪明的小 aux”。
- 而是“整包 clause_ge4 之所以推坏 final，是否主要是因为它混进了太多强终止形状样本”。

## sidecar 更新
- 已在 `target_special_supervision` sidecar 中新增正式 pool:
  - `structural_clause_ge4_no_final_terminal`
- 重跑后画像：
  - 记录数: `46`
  - split: `target_train = 38`, `target_validation = 8`
  - 时长中位数: `9.83449` 秒
  - lexical 中位数: `34.5`
  - clause 中位数: `5`
  - `final_terminal_type = none` 全成立

解释：
- 它比整包 `structural_clause_ge4 = 206` 更窄，
- 但比 `challenge_proxy_core` 更像真正的长结构语句，
- 因此是一个合理的“结构复杂但不强推句末终止”的 secondary candidate。

## 实验信息
- 实验:
  - `EXP-20260315-037-offline-mvp-d20-round1-1-special-proxy-core-clause-ge4-no-final-terminal-early-handoff-zart-influence-100step-calibration`
- 配置:
  - `configs/offline_mvp_train_d20_round1_1_special_proxy_core_clause_ge4_no_final_terminal_early_handoff_zart_influence_smallscale_100_seeded_shuffle.json`
- 训练输出:
  - `reports/training/offline_mvp_d20_special_proxy_core_clause_ge4_no_final_terminal_early_handoff_zart_influence_exp037/`
- 评估输出:
  - `reports/eval/offline_mvp_special_eval_exp037d20/`
  - `reports/eval/offline_mvp_ablations_exp037d20/`
  - `reports/eval/offline_mvp_checkpoint_series_exp037d20/`
  - `reports/eval/offline_mvp_special_eval_series_exp037d20/`

## 配置差异
`D20` 相对 `D7` 的唯一主改动是：
- 保留 `challenge_proxy_core` 作为 primary
- 保留 `z_art_influence_aux`
- phase1 secondary 从:
  - `structural_clause_ge4`
  变成:
  - `structural_clause_ge4_no_final_terminal`

dry-run 已确认：
- 新 secondary pool 被训练计划识别
- `phase1 priority_record_count = 54`

## 关键结果
### 1. `D20 final` 没有打赢 `D7`
- `D20 final`
  - `target_validation.loss_total = 2.792781`
  - `target_special_eval.delta_loss_total = 0.277193`
  - `zero_e_evt.delta_target_loss_total = 2.448193`
  - `zero_z_art.delta_target_loss_total = 0.430398`

对比 `D7 final = 2.73012 / -0.003131 / 3.489725 / 0.59961`:
- validation 更差
- final special 明显翻正
- `e_evt / z_art` 都回落

### 2. `D20` 比 `D19` 温和，但没有形成新解
对比 `D19 final = 2.84661 / 0.219234 / 2.363735 / 0.441742`:
- `D20` validation 略好
- `D20` `e_evt` 略强
- `D20` `z_art` 近似
- 但 final special 仍然是正值

解释：
- 把 `clause_ge4` 缩到 no-final-terminal 子池，确实比“强行 late 喂整包 clause_ge4”更温和，
- 但还不足以回到 `D7` 级别，更没有形成新的 joint winner。

### 3. `D20` 的 late-window 也没有优于 `D7`
- `D20 step80 = 3.932341 / -0.241696 / 2.122064 / 1.022158`
- `D20 step90 = 3.508358 / -0.298419 / 2.730087 / 0.551189`
- `D20 step100 = 2.792781 / 0.277193 / 2.448193 / 0.430398`

对比 `D7`:
- `D7 step80 = 3.688559 / -0.306983 / 2.65962 / 1.084382`
- `D7 step90 = 3.427092 / -0.342982 / 2.806937 / 0.50902`
- `D7 step100 = 2.73012 / -0.003131 / 3.489725 / 0.59961`

解释：
- `D20` 不是某个 late checkpoint 被 final 冲掉了。
- 它在 `step80 / 90 / 100` 三个点都没有形成对 `D7` 的明确优势：
  - `step80` validation 更差，special 也更浅
  - `step90` special 更浅、`e_evt` 更弱，只剩 `z_art` 略高
  - `step100` 则整体退化

### 4. 这条结果说明“去掉 final terminal 冲突”本身还不够
- `D20` 已经把 secondary structural axis 从“整包 clause-rich”改成了“clause-rich 且 no-final-terminal”
- 但 final 仍然翻坏
- 这说明:
  - 当前问题不只是 `clause_ge4` 里混进了过多 terminal-rich 样本
  - 而是这条 clause-rich secondary axis 本身，在 `D7` scaffold 上仍会把轨迹推向较差终盘

## 当前结论
- `structural_clause_ge4_no_final_terminal` 是一个合理、可解释、且样本量足够的小池。
- 但 `D20` 已经说明：
  - 把 `structural_clause_ge4` 拆得更干净，
  - 还不足以在当前 `D7` scaffold 上打出新行为。
- 因此当前更不值得继续在 `clause_ge4` 家族里做更多子池切分 sweep。

## 当前建议
1. 保留 `structural_clause_ge4_no_final_terminal` sidecar pool，作为正式分析产物。
2. 不把 `D20` 升为默认方案。
3. 暂不继续优先扩展:
   - `clause_ge4` 子池切分 sweep
   - `no_final_terminal` 子池上的 handoff / ratio 微调
4. 下一步若继续推进，应转向:
   - 更不同的 supervision-definition 维度
   - 或不同的 phase / training decomposition
   - 而不是继续在 clause-rich family 内做更细拆分
