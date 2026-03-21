# 2026-03-21 Stage5 training apply-mode 最小 A/B probe 报告

## 结论
- 当前在最小可控范围内，
  训练侧
  `pre_overlap_add`
  与
  `post_ola_envelope`
  没有表现出足够大的短程差异，
  不值得直接升格成长程训练主实验。
- 更准确地说：
  - 同包单步 train-step
    差异约
    `1e-6 ~ 1e-5`
  - 同包 `3 step`
    loop
    差异约
    `1e-5`
  - 小型 dataset loop
    差异也只到
    `1e-5 ~ 1e-4`
    量级
- 因此当前更合理的工程口径是：
  - 训练侧 apply mode
    已有正式实验入口
  - 但现有短程证据
    还不足以支持
    “马上切到
    postenv
    做更大训练”

## 本轮目标
1. 验证训练侧新参数
   `--reconstruction-frame-gain-apply-mode`
   是否真的可用
2. 用同一训练资产、
   同一 seed、
   只改 apply mode
   的方式做最小 A/B
3. 判断它是否值得继续升级成更长训练实验

## 本轮执行

### 1. 同包单步 train-step A/B
- 训练包：
  - `reports/runtime/offline_mvp_nores_vocoder_train_targets_smoke_chapter3_3_firefly_162/offline_mvp_nores_vocoder_train_targets.pt`
- 共同参数：
  - `seed = 20260317`
  - `waveform_weight = 0.5`
  - `stft_weight = 0.5`
  - `rms_guard_weight = 0.2`
  - `use_predicted_activity_gate = true`

#### preOLA
```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-train-step `
  --train-targets reports/runtime/offline_mvp_nores_vocoder_train_targets_smoke_chapter3_3_firefly_162/offline_mvp_nores_vocoder_train_targets.pt `
  --output-dir reports/runtime/stage5_training_reconstruction_applymode_probe_round1_1/train_step_preola `
  --device cpu `
  --seed 20260317 `
  --waveform-weight 0.5 `
  --stft-weight 0.5 `
  --rms-guard-weight 0.2 `
  --use-predicted-activity-gate `
  --reconstruction-frame-gain-apply-mode pre_overlap_add
```

#### postenv
```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-train-step `
  --train-targets reports/runtime/offline_mvp_nores_vocoder_train_targets_smoke_chapter3_3_firefly_162/offline_mvp_nores_vocoder_train_targets.pt `
  --output-dir reports/runtime/stage5_training_reconstruction_applymode_probe_round1_1/train_step_postenv `
  --device cpu `
  --seed 20260317 `
  --waveform-weight 0.5 `
  --stft-weight 0.5 `
  --rms-guard-weight 0.2 `
  --use-predicted-activity-gate `
  --reconstruction-frame-gain-apply-mode post_ola_envelope
```

### 2. 同包 `3 step` loop A/B
- 输出：
  - `.../training_loop_preola/`
  - `.../training_loop_postenv/`

### 3. 小型 dataset loop A/B
- 数据集索引：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_path_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- 规模：
  - `2 train packages`
  - `1 validation package`
  - `3 steps`
  - `packages_per_step = 2`

## 本轮中途发现并修复的工程问题
- 在 dataset loop
  第一次执行时，
  `average_loss_metrics(...)`
  默认把所有
  `loss_metrics`
  字段都按浮点求平均
- 本轮新增了：
  - `reconstruction_frame_gain_apply_mode`
  这个字符串字段后，
  dataset loop
  聚合阶段直接报错
- 当前已修复：
  - 数值字段继续求平均
  - 非数值字段若所有 package
    一致则原样保留
  - 若不一致则显式报错

## 结果

### 1. 单步 train-step 基本打平
- `preOLA loss_total = 1.745659`
- `postenv loss_total = 1.745658`
- `delta_loss_total = -0.000001`
- `delta_stft = -0.000002`
- `delta_waveform = 0`
- `delta_rms_ratio = 0`

解释：
- 当前单步上看，
  `postenv`
  几乎没有带来可区分的训练信号变化

### 2. 同包 `3 step` loop 仍几乎打平
- 第 3 个 train step：
  - `preOLA loss_total = 1.342578`
  - `postenv loss_total = 1.342589`
  - `delta = +0.000011`
- 第 3 个 validation：
  - `preOLA loss_total = 1.208208`
  - `postenv loss_total = 1.208195`
  - `delta = -0.000013`
- `postenv`
  只在：
  - validation `loss_total`
  - validation `loss_stft`
  上
  给出极小幅改善，
  量级仍只有
  `1e-5`

解释：
- 这说明：
  即便拉到
  `3 step`
  短程优化，
  训练侧 apply mode
  也没有出现能明显放大的分叉

### 3. 小型 dataset loop 也没有出现实质性分叉
- 第 3 个 train step：
  - `preOLA loss_total = 1.398098`
  - `postenv loss_total = 1.398099`
  - `delta = +0.000001`
- 第 3 个 validation：
  - `preOLA loss_total = 1.286636`
  - `postenv loss_total = 1.286661`
  - `delta = +0.000025`
- 第 3 个 validation：
  - `delta_waveform = +0.000008`
  - `delta_stft = +0.000009`
  - `delta_rms_ratio = +0.000081`

解释：
- 到小型 dataset loop
  层面，
  也没有出现
  `postenv`
  明显更优的信号
- 反而是：
  validation
  仍几乎等价，
  还带一点极小幅逆风

## 当前判断

### 1. 当前训练侧 `postenv` 还不值得直接升格
- 现在能说的是：
  - 参数通了
  - 单步 / 短程 / 小型 dataset
    都能跑
- 不能说的是：
  - 训练侧切到
    `postenv`
    已经明显更好

### 2. 当前更合理的默认仍是保持训练侧 `pre_overlap_add`
- 因为：
  - 现有证据不支持切默认
  - export-side
    的默认提升，
    也不应自动外推到训练侧

### 3. 若未来还要继续追这条题，应先升级证据层级
- 真想继续问：
  - 训练侧 apply mode
    是否值得换
- 下一轮至少应升级到：
  - 更长 dataset loop
  - 正式 validation split
  - checkpoint 对照
- 不再值得继续停留在：
  - 单包短程 smoke

## 一句话结论
- 当前训练侧
  `pre_overlap_add`
  vs
  `post_ola_envelope`
  在最小可控 A/B
  里几乎完全打平；
  这条线现在更像
  “已具备正式实验能力，
  但暂时没有足够收益信号”，
  而不是下一轮必须立刻放大的主实验。
