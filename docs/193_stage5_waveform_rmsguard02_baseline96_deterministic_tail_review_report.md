# 193. Stage5 waveform `rms_guard=0.2` baseline96 deterministic 尾段复核报告

## 背景
- `docs/192_stage5_waveform_rmsguard02_baseline48_and_deterministic_reproducibility_fix_report.md`
  已把 Stage5
  waveform 主线推进到:
  - `rms_guard = 0.2`
  - `48-step`
  - deterministic-ready
- 当时的核心问题是:
  - 继续拉到
    `96-step`
    是否仍值得
  - 以及尾段 gain
    是否还保持
    broad-based

## 本轮目标
1. 用
   `--deterministic`
   跑通
   `96-step`
   waveform baseline
2. 对照:
   - `24`
   - `48`
   - `72`
   - `96`
   的 validation 轨迹
3. 用 checkpoint review
   判断尾段:
   - `48 -> 72`
   - `72 -> 96`
   的覆盖面变化

## 实验命令

### A. baseline96 deterministic

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline96_deterministic_round1_1 --device cuda:0 --num-steps 96 --packages-per-step 4 --validation-interval 24 --checkpoint-interval 24 --sampler-mode shuffle --seed 20260317 --deterministic --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2
```

### B. checkpoint review

```powershell
.\python.exe manage.py review-offline-mvp-nores-vocoder-checkpoints --summary reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline96_deterministic_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json --output-dir reports/runtime/offline_mvp_nores_vocoder_checkpoint_review_waveform_rmsguard02_baseline96_deterministic_round1_1 --top-k 10
```

## 结果

### runtime
- dataset:
  - `592 train`
  - `66 validation`
- 总耗时:
  - `164.346084 sec`
- best checkpoint:
  - `step96`
  - `loss_total = 0.616506`

### validation 轨迹
- step24:
  - `loss_total = 0.749261`
  - `loss_waveform = 0.126458`
  - `loss_stft = 0.352675`
  - `loss_rms_guard = 0.132272`
  - `decoded_to_target_rms_ratio = 0.938716`
- step48:
  - `loss_total = 0.656366`
  - `loss_waveform = 0.130834`
  - `loss_stft = 0.239656`
  - `loss_rms_guard = 0.119011`
  - `decoded_to_target_rms_ratio = 0.981499`
- step72:
  - `loss_total = 0.625926`
  - `loss_waveform = 0.130924`
  - `loss_stft = 0.193803`
  - `loss_rms_guard = 0.119126`
  - `decoded_to_target_rms_ratio = 0.979730`
- step96:
  - `loss_total = 0.616506`
  - `loss_waveform = 0.135704`
  - `loss_stft = 0.179105`
  - `loss_rms_guard = 0.116592`
  - `decoded_to_target_rms_ratio = 1.051881`

## checkpoint review

### 1. `24 -> 48`
- average delta:
  - `-0.092896`
- improved:
  - `66 / 66`
- worsened:
  - `0 / 66`

### 2. `48 -> 72`
- average delta:
  - `-0.030440`
- improved:
  - `66 / 66`
- worsened:
  - `0 / 66`

### 3. `72 -> 96`
- average delta:
  - `-0.009420`
- improved:
  - `42 / 66`
- worsened:
  - `24 / 66`
- top worsened delta
  最大约:
  - `+0.009355`

### 4. `24 -> 96`
- average delta:
  - `-0.132755`
- improved:
  - `66 / 66`
- worsened:
  - `0 / 66`

## 当前判断

### 1. `48 -> 72` 仍然属于 broad-based gain
- 这一段
  不是只靠少数样本
  拖均值
- 仍然是:
  - `66 / 66`
    全量改善

### 2. `72 -> 96` 已进入明显尾段
- 虽然均值仍然继续下降:
  - `0.625926 -> 0.616506`
- 但 package 级
  已经变成:
  - `42 / 66` improved
  - `24 / 66` worsened
- 所以当前不能再写成:
  - `96-step`
    仍然像
    `48 -> 72`
    那样稳定广覆盖改善

### 3. 当前 best-by-loss checkpoint 是 `96`，但 `72` 更像“更稳妥的晚停点”
- `step96`
  的优势是:
  - `loss_total`
    最低
  - `loss_stft`
    继续下降
- 但 `step72`
  的优点是:
  - 仍保持
    `66 / 66`
    broad-based gain
  - `decoded_to_target_rms_ratio`
    为
    `0.979730`
    更接近 1.0
- 相比之下，
  `step96`
  已经出现:
  - 局部回退增多
  - RMS ratio
    上翻到
    `1.051881`

### 4. 当前不建议继续把更长 horizon 自动升格为主线
- 从:
  - `24 -> 48`
    `-0.092896`
- 到:
  - `48 -> 72`
    `-0.030440`
- 再到:
  - `72 -> 96`
    `-0.009420`
- 这说明:
  - 尾段收益
    还没归零
  - 但已经明显进入
    diminishing-return tail
  - 且开始伴随
    局部回退
    与 RMS 过冲

先说人话:
- 这轮说明
  `96-step`
  不是没用，
  它确实把平均 loss
  再往下压了一点。
- 但到了这一步，
  模型已经不再是
  “大家一起都在变好”，
  而是
  “大多数还在好，
   但已经有一批样本
   开始轻微回退”。
- 所以现在更像样的工程口径是:
  - `96`
    是最优均值点
  - `72`
    是更稳妥的
    晚停候选

## 当前产物
- baseline96 deterministic:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline96_deterministic_round1_1`
- review96 deterministic:
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_review_waveform_rmsguard02_baseline96_deterministic_round1_1`

## 下一步建议
1. 若当前目标是
   工程稳妥默认值，
   优先把:
   - `step72`
   视为 waveform route
   的默认晚停候选
2. 若当前目标是
   继续追逐
   最低平均 loss，
   也不建议直接再拉到:
   - `144`
   - `192`
   - 或更长
   而应先补:
   - late-stop selection
   - 或更强 objective
3. 更合理的下一步主线
   已经开始转向:
   - waveform route
     checkpoint selection
   - multi-resolution STFT
   - adversarial / feature-matching
     设计准备

## 一句话结论
- Stage5 waveform
  `rms_guard = 0.2`
  在 deterministic
  `96-step`
  下把 validation
  继续压到
  `0.616506`，
  但 `72 -> 96`
  已出现
  `24 / 66`
  package 级轻微回退，
  且 RMS ratio
  从
  `0.979730`
  上翻到
  `1.051881`；
  因此当前更合理的口径是:
  - `96`
    是 best-by-loss
  - `72`
    是更稳妥的
    late-stop 候选
  - 主线不再应是
    brute-force 继续拉长 horizon
