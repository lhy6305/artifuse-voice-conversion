# `round1.1 / checkpoint selection` 联合分析报告

## 目的
- 当前 `C1.8 / C1.10 / C1.13` 都出现了同一类现象：
  - final checkpoint 看起来不理想
  - 但中后段 checkpoint 一度出现更好的 special 行为
- 本轮不再继续堆新的小 auxiliary loss。
- 当前先验证：
  - 现有训练轨迹里到底有没有“可选但被 final 覆盖掉”的更优 checkpoint
  - 如果有，它的代价具体是什么

## 分析输入
- 分析命令：
  - `.\python.exe manage.py analyze-offline-mvp-checkpoint-selection --experiment-metrics ... --output-dir reports/eval/offline_mvp_checkpoint_selection_round1_1`
- 输入实验：
  - `EXP-032`
  - `EXP-035`
  - `EXP-039`
  - `EXP-042`
- 分析口径：
  - 合并每个实验已有的 `special_eval_series` 与 `checkpoint_series_eval`
  - late window 定义为：
    - `late_step_ratio = 0.8`
    - 对当前 `100 step` 实验即 `step >= 80`
  - validation guard 定义为：
    - `target_validation.loss_total <= best_validation * 1.25`
  - positive-control floor 定义为：
    - `zero_z_art.delta_target_loss_total >= 0.1`
    - `zero_e_evt.delta_target_loss_total >= 0.1`

## 关键结果
- `EXP-032 final` 仍是当前这四条轨迹里最强的 final checkpoint：
  - `target_validation.loss_total = 2.672052`
  - `target_special_eval.delta_loss_total = 0.103108`
  - `zero_e_evt.delta_target_loss_total = 1.735497`
  - `zero_z_art.delta_target_loss_total = 1.275259`
- `EXP-035 / 039 / 042` 在 late window 里出现了几乎同构的三段分叉：
  - `step80`
    - special 最好
    - `z_art / e_evt` 都仍为正且不弱
    - 但 validation 明显更差
  - `step90`
    - validation 和 `e_evt` 明显更强
    - special 仍为负
    - 但 `z_art` 已接近 `0`
  - `step100`
    - validation 达到本实验最好
    - 但 special 翻回正值
    - `e_evt` 也从 `step90` 回落

## 最关键的对照
### `EXP-042`
- `step80`
  - `target_validation.loss_total = 4.282626`
  - `target_special_eval.delta_loss_total = -0.553492`
  - `zero_e_evt.delta_target_loss_total = 0.66439`
  - `zero_z_art.delta_target_loss_total = 0.550914`
- `step90`
  - `target_validation.loss_total = 3.522161`
  - `target_special_eval.delta_loss_total = -0.295714`
  - `zero_e_evt.delta_target_loss_total = 1.520532`
  - `zero_z_art.delta_target_loss_total = 0.005477`
- `step100`
  - `target_validation.loss_total = 2.910157`
  - `target_special_eval.delta_loss_total = 0.356926`
  - `zero_e_evt.delta_target_loss_total = 0.948263`
  - `zero_z_art.delta_target_loss_total = 0.178659`

### `EXP-039`
- `step80`
  - `target_validation.loss_total = 4.283327`
  - `target_special_eval.delta_loss_total = -0.551359`
  - `zero_e_evt.delta_target_loss_total = 0.659585`
  - `zero_z_art.delta_target_loss_total = 0.552126`
- `step90`
  - `target_validation.loss_total = 3.521361`
  - `target_special_eval.delta_loss_total = -0.293919`
  - `zero_e_evt.delta_target_loss_total = 1.517961`
  - `zero_z_art.delta_target_loss_total = 0.007022`
- `step100`
  - `target_validation.loss_total = 2.911644`
  - `target_special_eval.delta_loss_total = 0.354963`
  - `zero_e_evt.delta_target_loss_total = 0.949482`
  - `zero_z_art.delta_target_loss_total = 0.175258`

### `EXP-035`
- `step80`
  - `target_validation.loss_total = 4.260131`
  - `target_special_eval.delta_loss_total = -0.528372`
  - `zero_e_evt.delta_target_loss_total = 0.681383`
  - `zero_z_art.delta_target_loss_total = 0.555121`
- `step90`
  - `target_validation.loss_total = 3.522096`
  - `target_special_eval.delta_loss_total = -0.2803`
  - `zero_e_evt.delta_target_loss_total = 1.513861`
  - `zero_z_art.delta_target_loss_total = -0.001579`
- `step100`
  - `target_validation.loss_total = 2.889709`
  - `target_special_eval.delta_loss_total = 0.39305`
  - `zero_e_evt.delta_target_loss_total = 0.931855`
  - `zero_z_art.delta_target_loss_total = 0.215737`

## 结论
- 这轮支持“先做 checkpoint 选择 / 训练流程层”，因为：
  - `035 / 039 / 042` 确实都学到过比 final 更好的 special 行为
  - 问题不是“完全没学到”
  - 而是“late window 内部的 tradeoff 没有被当前 checkpoint 选择规则接住”
- 但这轮也明确说明：
  - 不能简单把 `step80` 或 `step90` 直接升为默认 checkpoint
  - 因为它们分别代表两种不同牺牲：
    - `step80`：
      - 保住了 special 和双控制
      - 但 validation 明显更差
    - `step90`：
      - 保住了 validation 和 `e_evt`
      - 但 `z_art` 基本塌到接近 `0`
- 所以真正该做的不是“拍脑袋挑 `80` 还是 `90`”，而是：
  - 正式设计一个联合 gate
  - 至少同时看：
    - `target_validation.loss_total`
    - `target_special_eval.delta_loss_total`
    - `zero_e_evt.delta_target_loss_total`
    - `zero_z_art.delta_target_loss_total`

先说人话：
- 现在已经能确认，问题不只是“模型没学会”。
- 更像是它在后段走过了几个不同方向的岔路口，而我们现在还没有一套靠谱的选点规则。

## 建议的下一步
1. 不把 `EXP-035 / 039 / 042` 的任一 early checkpoint 直接升为默认模型。
2. 下一轮优先补一个正式的 checkpoint gate：
   - 先做离线分析规则
   - 再决定是否要把它写进训练流程
3. gate 至少要能区分：
   - `step80` 这种“special + 双控制较好，但 validation 较差”
   - `step90` 这种“validation + e_evt 更强，但 z_art 接近塌缩”
4. 如果做完 gate 后，`035 / 039 / 042` 仍无法在可接受 validation 代价下稳定超过 `EXP-032 final`，再转更强的数据视角改造。

## 产物入口
- `reports/eval/offline_mvp_checkpoint_selection_round1_1/checkpoint_selection_analysis.json`
- `reports/eval/offline_mvp_checkpoint_selection_round1_1/checkpoint_selection_analysis.md`
