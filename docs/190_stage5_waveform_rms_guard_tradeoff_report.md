# 190. Stage5 waveform RMS guard 权衡与 baseline24 报告

## 背景
- `docs/189_stage5_waveform_stft_bootstrap_decoder_report.md`
  已确认:
  - minimal decoder +
    waveform/STFT objective
    已能训练
  - 但无 guard 的
    `12-step`
    baseline
    出现明显
    loudness collapse:
    - validation
      `decoded_waveform_rms`
      `0.077280`
    - target RMS
      `0.123402`

## 本轮目标
1. 在现有 waveform/STFT
   objective 上
   新增最小
   `RMS guard`
2. 对比:
   - `rms_guard = 0.5`
   - `rms_guard = 0.2`
3. 判断:
   - 哪个权重更适合
     作为当前下一阶段
     baseline 配方

## 本轮代码落地

### 1. `src/v5vc/offline_vocoder_training.py`
- 新增:
  - `compute_rms_guard_loss`
- `compute_nores_vocoder_losses`
  现在额外支持:
  - `loss_rms_guard`
  - `decoded_to_target_rms_ratio`
- `loss_total`
  现在可选加上:
  - `rms_guard_weight * loss_rms_guard`

### 2. `src/v5vc/cli.py`
- Stage5 三个训练入口新增:
  - `--rms-guard-weight`
- 默认值:
  - `0.0`

## 单包 smoke

### 命令

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-train-step --train-targets reports/runtime/offline_mvp_nores_vocoder_train_targets_smoke_chapter3_3_firefly_162/offline_mvp_nores_vocoder_train_targets.pt --output-dir reports/runtime/offline_mvp_nores_vocoder_waveform_rmsguard_train_step_smoke_chapter3_3_firefly_162 --device cpu --seed 20260317 --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.5
```

结果:
- `loss_total = 2.299453`
- `loss_rms_guard = 0.930856`
- `decoded_to_target_rms_ratio = 2.536679`

说明:
- 新 guard
  已进入训练图，
  不只是参数占位

## full-split 对照实验

### A. 过强 guard: `rms_guard = 0.5`

命令:

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard_baseline12_round1_1 --device cuda:0 --num-steps 12 --packages-per-step 4 --validation-interval 6 --checkpoint-interval 6 --sampler-mode shuffle --seed 20260317 --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.5
```

step12 validation:
- `loss_total = 1.087844`
- `loss_waveform = 0.149384`
- `loss_stft = 0.730605`
- `loss_rms_guard = 0.193111`
- `decoded_waveform_rms = 0.147275`
- `target_waveform_rms = 0.123402`
- `decoded_to_target_rms_ratio = 1.220926`

判断:
- 它确实把振幅
  从塌缩侧
  拉回来了
- 但代价是:
  - waveform / STFT
    重建明显恶化
  - validation
    `step6 -> step12`
    改善很弱

### B. 较轻 guard: `rms_guard = 0.2`

命令:

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline12_round1_1 --device cuda:0 --num-steps 12 --packages-per-step 4 --validation-interval 6 --checkpoint-interval 6 --sampler-mode shuffle --seed 20260317 --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2
```

step12 validation:
- `loss_total = 0.907862`
- `loss_waveform = 0.124450`
- `loss_stft = 0.547905`
- `loss_rms_guard = 0.150582`
- `decoded_waveform_rms = 0.108953`
- `target_waveform_rms = 0.123402`
- `decoded_to_target_rms_ratio = 0.903179`

判断:
- 相比无 guard:
  - reconstruction 代价增加
  - 但振幅显著更接近目标
- 相比 `0.5`:
  - reconstruction 好得多
  - RMS 也没有被推到
    明显过强的一侧

### C. `rms_guard = 0.2` 继续拉到 `24-step`

命令:

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline24_round1_1 --device cuda:0 --num-steps 24 --packages-per-step 4 --validation-interval 12 --checkpoint-interval 12 --sampler-mode shuffle --seed 20260317 --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2
```

validation:
- step12:
  - `loss_total = 0.907870`
  - `decoded_to_target_rms_ratio = 0.903156`
- step24:
  - `loss_total = 0.749254`
  - `loss_waveform = 0.126461`
  - `loss_stft = 0.352659`
  - `loss_rms_guard = 0.132280`
  - `decoded_waveform_rms = 0.113102`
  - `target_waveform_rms = 0.123402`
  - `decoded_to_target_rms_ratio = 0.938703`

## 核心对照

### 1. 无 guard `12-step`
- `loss_total = 0.811442`
- `loss_stft = 0.447961`
- `decoded_to_target_rms_ratio ≈ 0.626`

### 2. guard `0.5` `12-step`
- `loss_total = 1.087844`
- `loss_stft = 0.730605`
- `decoded_to_target_rms_ratio = 1.220926`

### 3. guard `0.2` `12-step`
- `loss_total = 0.907862`
- `loss_stft = 0.547905`
- `decoded_to_target_rms_ratio = 0.903179`

### 4. guard `0.2` `24-step`
- `loss_total = 0.749254`
- `loss_stft = 0.352659`
- `decoded_to_target_rms_ratio = 0.938703`

## 当前判断

### 1. `RMS guard` 确实解决了“越训越小声”的主风险
- 无 guard
  在 `12-step`
  时，
  RMS ratio
  只有约:
  - `0.626`
- `rms_guard = 0.2`
  到 `24-step`
  时，
  已回到:
  - `0.938703`

### 2. 但 guard 不能上得太重
- `0.5`
  虽然抑制 collapse，
  但会明显牺牲:
  - waveform loss
  - STFT loss
  - 整体验证改善速度
- 所以当前不能把
  “加更大 guard”
  自动理解成
  更稳妥

### 3. 当前最合理的基线配方
- 现阶段更合理的
  Stage5 waveform bootstrap
  配方是:
  - `waveform_weight = 0.5`
  - `stft_weight = 0.5`
  - `rms_guard_weight = 0.2`
- 这不是最终最优，
  但已经比:
  - 无 guard
    更可控
  - `0.5` guard
    更平衡

先说人话:
- 这一步说明
  loudness guard
  不是没用，
  它确实把
  “声音越学越小”
  这个问题
  压住了。
- 但 guard 太大
  会把模型拽过头，
  让它顾着保音量，
  反而学不好细节。
- 当前 `0.2`
  是一个更像样的平衡点，
  已经可以作为
  下一轮 waveform baseline
  的默认配方。

## 当前产物
- 单包 smoke:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_rmsguard_train_step_smoke_chapter3_3_firefly_162`
- `0.5` guard baseline12:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard_baseline12_round1_1`
- `0.2` guard baseline12:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline12_round1_1`
- `0.2` guard baseline24:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_baseline24_round1_1`

## 下一步建议
1. 现在可以把
   `rms_guard_weight = 0.2`
   作为当前默认配方
   继续做更长 waveform baseline
2. 下一步优先做:
   - `48-step`
     low-frequency baseline
   - 或 checkpoint review
3. 暂时不建议再花时间
   在:
   - `0.5`
     这类过强 guard
   上继续细抠

## 一句话结论
- Stage5 waveform bootstrap
  的 loudness collapse
  现在已经不是
  “只能看见问题，
     还没有解法”，
  而是已经拿到了
  一版可运行的
  工程修正:
  - `rms_guard_weight = 0.2`
- 这版配方在
  `24-step`
  时把 validation
  `loss_total`
  压到 `0.749254`，
  同时把
  `decoded_to_target_rms_ratio`
  稳在 `0.938703`；
  因此当前下一步
  应该沿这条配方
  继续扩展，
  而不是回到
  无 guard
  或过强 guard。
