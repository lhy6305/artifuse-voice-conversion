# `round1.1 / C1.4 / 100-step` 首轮小规模实验报告

## 目的
- 保持原采样方案不变：
  - split 仍用 `hybrid_stratified_blocked`
  - 训练 sampler 仍用 `seeded_shuffle`
- 只把 target 数据底座从 `round1` 升到 `round1.1`，观察：
  - 主验证有没有明显提升
  - `special_eval` 压力差有没有改善
  - `z_art / e_evt` 依赖是否更稳定

先说人话：
- 这轮不是再改模型。
- 是看“多回收 42 条 lexical target 之后，同一套 `C1.4` 还能不能更像样一点”。

## 已执行内容
### 1. 正式化 `round1.1`
- 已 materialize：
  - `data_prep/round1_1/splits/hybrid_stratified_blocked/`
- 已重建：
  - `data_prep/round1_1/c1_weak_event_hints/target_weak_event_hints.jsonl`

### 2. 首轮训练已完成
- 实验：
  - `EXP-20260314-021-offline-mvp-c1-4-round1-1-100step-calibration`
- 配置：
  - `configs/offline_mvp_train_c1_4_round1_1_smallscale_100_seeded_shuffle.json`
- 训练结果：
  - `100 step` 完成
  - 最终 formal validation：
    - `target.loss_total = 2.703126`
    - `source.loss_total = 2.725783`

### 3. 配套评估已完成
- final model-level `special_eval`
- final `z_art / e_evt` ablation
- checkpoint-series ablation
- checkpoint-series `special_eval`

## 关键结果
### 1. 主验证没有出现“明显抬升”
- 对比旧线 `EXP-020`：
  - `EXP-020` final target validation 约为：
    - `2.680616`
  - `EXP-021` final target validation 约为：
    - `2.703126`
- 这说明：
  - 只把 target 数据升到 `round1.1`，并没有把主验证线明显往上推

### 2. final `special_eval` 压力差明显收窄
- `EXP-020`：
  - `delta_loss_total = 0.181996`
- `EXP-021`：
  - `delta_loss_total = 0.028766`
- 进一步看：
  - `delta_loss_acoustic` 从 `+0.045541` 变成 `-0.127952`
  - `delta_loss_text_aux` 从 `0.142410` 降到 `0.112828`
- 这说明：
  - 新 target 数据没有把 `no_text_voice` challenge 彻底变简单
  - 但 final checkpoint 上，special slice 和常规验证的差距确实缩小了

### 3. final `e_evt` 依赖更强，但 `z_art` 依赖更弱
- `EXP-020` final ablation：
  - `zero_z_art.delta_target_loss_total = 1.329629`
  - `zero_e_evt.delta_target_loss_total = 1.410986`
- `EXP-021` final ablation：
  - `zero_z_art.delta_target_loss_total = 0.886715`
  - `zero_e_evt.delta_target_loss_total = 1.781482`
- 这说明：
  - `round1.1` 这轮更依赖 `e_evt`
  - 但对 `z_art` 的依赖没有一起变强

### 4. 中段不稳问题还在，而且更重
- `step50` 对比：
  - `EXP-020`
    - `zero_z_art.delta_target_loss_total = -0.173311`
    - `zero_e_evt.delta_target_loss_total = -0.519136`
  - `EXP-021`
    - `zero_z_art.delta_target_loss_total = -0.273851`
    - `zero_e_evt.delta_target_loss_total = -0.854462`
- 这说明：
  - 旧问题没有被 `round1.1` 自动修复
  - 而且这次 `step50` 的 route-C 依赖回落更明显

## 当前结论
- `round1.1` 不是白折腾：
  - final `special_eval` 压力差更小
  - final `e_evt` 依赖更强
- 但它还不够好到可以直接说：
  - “数据一升级，route-C 就稳了”
- 当前更准确的表述是：
  - `round1.1` 带来了更好的终点 special-slice 行为
  - 但没有解决 route-C 的中期稳定性问题

先说人话：
- 这轮不像“全线大胜”。
- 更像“终点更顺了，但中途还是会打摆子”。

## 下一步建议
- 不建议立刻把这轮结果当成 `round1.1` 默认胜出证据。
- 更合理的下一步是二选一：
  - 继续在 `round1.1` 上做 route-C 稳定性修正，优先盯 `step50` 依赖回落
  - 或者先跑一轮更保守的 `round1.1` 对照线，确认收益到底主要来自数据，还是来自终点偶然性
