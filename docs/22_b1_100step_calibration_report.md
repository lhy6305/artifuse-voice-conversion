# `B1-offline-minimal` 100 step 校准报告

## 目的
- 在不直接跳到 `500 step` 的前提下，验证 `B1-offline-minimal` 在更长训练时长下是否继续保持优势。
- 重点回答两个问题：
  - `B1` 在 `20 step` 看到的控制链增益，到了 `100 step` 还在不在。
  - `B1` 是否已经表现出足够明确的整体收益，值得直接放大到 `500 step`。

先说人话：
- 上一轮只是“小测”。
- 这轮是把课时拉长，看这位新老师是不是只会短期提分，还是长期也站得住。

## 本轮配置与执行
- 配置：
  - `configs/offline_mvp_train_b1_smallscale_100_seeded_shuffle.json`
- 实验：
  - `EXP-20260314-015-offline-mvp-b1-100step-calibration`
- 运行阶段：
  - `small_scale_validation`
- 真实训练：
  - `100 step`
- 总耗时：
  - `2.828663s`

配套评估已完成：
- `reports/eval/offline_mvp_ablations_exp015/ablation_eval.json`
- `reports/eval/offline_mvp_checkpoint_series_exp015/checkpoint_series_eval.json`
- `reports/eval/offline_mvp_special_eval_exp015/special_eval_model.json`
- `reports/eval/offline_mvp_special_eval_series_exp015/special_eval_series.json`

## 训练与验证结果
### 固定 validation 历史
- step 10:
  - total `45.170193`
- step 20:
  - total `35.865547`
- step 30:
  - total `25.184158`
- step 40:
  - total `17.784084`
- step 50:
  - total `16.505917`
- step 60:
  - total `14.817028`
- step 70:
  - total `11.628149`
- step 80:
  - total `7.425701`
- step 90:
  - total `6.363696`
- step 100:
  - total `5.422634`

说明：
- 这里的 `validation.history.loss_total` 仍是训练入口里的固定小批验证口径。
- 模型级全量验证口径见后文 `special_eval / ablation` 部分。

先说人话：
- 训练确实在稳定收敛，不是 20 step 后就原地踏步。
- 但“能收敛”和“比旧方案更值得放大”是两回事，后者要看对照。

## 与无 `B1` 的 step100 对照
对照对象：
- 无 `B1`：
  - `EXP-20260314-011-offline-mvp-large-scale-500` 的 `step100`
- 有 `B1`：
  - `EXP-20260314-015-offline-mvp-b1-100step-calibration` 的 `step100`

### 1. 全量 validation 基线
- `target_loss_total`
  - 无 `B1`: `2.667123`
  - `B1`: `2.676195`
- `source_loss_total`
  - 无 `B1`: `2.686110`
  - `B1`: `2.689358`

解释：
- 这基本可以视为打平。
- `B1` 没有把整体训练拖坏，但也还没有在 `step100` 给出可观的总 loss 优势。

### 2. 控制消融
- `zero_z_art.delta_target_loss_total`
  - 无 `B1`: `1.306952`
  - `B1`: `1.332663`
- `zero_e_evt.delta_target_loss_total`
  - 无 `B1`: `1.404717`
  - `B1`: `1.407506`
- `zero_z_art.delta_source_loss_total`
  - 无 `B1`: `1.962503`
  - `B1`: `1.997582`
- `zero_e_evt.delta_source_loss_total`
  - 无 `B1`: `1.010173`
  - `B1`: `1.005402`

解释：
- 到 `step100`，`B1` 与无 `B1` 的控制敏感度几乎重合。
- 这和 `20 step` 时 `B1` 看起来更强的现象不同。

先说人话：
- `B1` 在小测阶段看起来更会“扶住控制链”。
- 但练到 `100 step` 后，老方案自己也追上来了，所以优势没有继续拉大。

## `B1` 自身的 checkpoint 变化
来自：
- `reports/eval/offline_mvp_checkpoint_series_exp015/checkpoint_series_eval.json`

### `zero_z_art.delta_target_loss_total`
- step 10: `0.097014`
- step 20: `0.207014`
- step 30: `0.248665`
- step 40: `0.025216`
- step 50: `-0.173910`
- step 60: `0.218725`
- step 70: `0.708298`
- step 80: `0.917957`
- step 90: `-0.169832`
- step 100: `1.332663`

### `zero_e_evt.delta_target_loss_total`
- step 10: `1.293825`
- step 20: `1.733871`
- step 30: `1.568373`
- step 40: `0.373772`
- step 50: `-0.521803`
- step 60: `0.269633`
- step 70: `0.352005`
- step 80: `1.466497`
- step 90: `1.734398`
- step 100: `1.407506`

解释：
- `B1` 这组曲线不是单调增长，存在明显波动。
- 但到 `step100` 时，`z_art / e_evt` 都重新回到了较强状态。

先说人话：
- `B1` 这位新老师不是一路平稳加分。
- 中间有几次像“讲课节奏不稳”，但最后还是把关键控制量拉回来了。

## `target_special_eval` 变化
### `B1` 的 step 系列
- step 10:
  - regular `19.729883`
  - special `15.867836`
  - delta `-3.862047`
- step 20:
  - regular `15.784263`
  - special `11.882978`
  - delta `-3.901285`
- step 50:
  - regular `9.470963`
  - special `5.650607`
  - delta `-3.820356`
- step 100:
  - regular `2.670612`
  - special `2.886814`
  - delta `0.216202`

### 与无 `B1` 的 step100 对比
- `target_validation_loss_total`
  - 无 `B1`: `2.661784`
  - `B1`: `2.670612`
- `target_special_eval_loss_total`
  - 无 `B1`: `2.924799`
  - `B1`: `2.886814`
- `delta_loss_total`
  - 无 `B1`: `0.263015`
  - `B1`: `0.216202`
- `delta_loss_text_aux`
  - 无 `B1`: `0.537801`
  - `B1`: `0.310898`

解释：
- 到 `step100`，`target_special_eval` 仍然是更难的 nonverbal challenge slice。
- `B1` 在这组 slice 上比无 `B1` 略稳一点，但幅度不大。

先说人话：
- 对喘气这类非完整发声，`B1` 看起来稍微更不容易失衡。
- 但这个提升不够大，还不到“凭这点就直接升大方案”的程度。

## 当前结论
### 已确认
- `B1` 在 `100 step` 下依然稳定可训练，没有破坏收敛。
- `B1` 的最终 `step100` 表现与无 `B1` 基线整体基本打平。
- `B1` 在 `target_special_eval` 上略稳一点，但优势较小。

### 尚未确认
- 还不能说 `B1` 已经在总体效果上形成明确领先。
- 还不能说只靠当前这 7 维文本/标点特征，就足以支撑直接进入 `500 step` 并期待明显收益。

## 我的建议
- 当前更像是：
  - `B1` 方向成立；
  - 但 `B1-offline-minimal` 这版特征还不够强。
- 因此下一步更合理的决策应是二选一：
  1. 直接把当前 `B1-offline-minimal` 放大到 `500 step`
  2. 先做 `B1.1` 文本监督细化，再决定是否放大

我的倾向：
- 更建议先做 `B1.1` 文本监督细化。

先说人话：
- 现在能确认“这条路不是错路”，
- 但还不能确认“这版教案已经够好，值得直接全校推广”。
