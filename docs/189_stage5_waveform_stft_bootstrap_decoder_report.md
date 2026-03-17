# 189. Stage5 waveform-STFT bootstrap decoder 接入与 baseline12 报告

## 背景
- `docs/188_stage5_seeded_gpu_baseline192_low_frequency_probe_report.md`
  已确认:
  - proxy spectral/gate baseline
    到 `192-step`
    仍有收益
  - 但已经进入
    diminishing-return tail
- 所以下一步主线
  不该再继续
  brute-force 拉长
  proxy horizon，
  而应转向:
  - decoder / waveform-STFT
    目标接入

## 本轮目标
1. 在不重做 Stage5
   数据合同的前提下，
   给 no-res scaffold
   接入最小 waveform decoder
2. 复用现有 package
   中已保留的
   `aligned_waveform`
   与 runtime 元数据，
   接入 aligned waveform L1
   与 log-STFT loss
3. 跑通:
   - 单包 train-step smoke
   - dataset-level waveform/STFT smoke
   - 一个最小 `12-step`
     baseline

## 本轮代码落地

### 1. `src/v5vc/offline_vocoder_scaffold.py`
- `NoResidualSourceFilterVocoderScaffold`
  新增可选:
  - `frame_length`
  - `waveform_decoder`
- 当上游 scaffold
  带有
  `source_runtime.frame_length`
  时，
  模型现在会额外输出:
  - `waveform_frames`

### 2. `src/v5vc/offline_vocoder_training.py`
- `extract_training_batch`
  现在把:
  - `aligned_waveform`
    直接带入训练 batch
- 新增:
  - `extract_training_runtime`
  - `reconstruct_waveform_from_frames`
  - `compute_stft_reconstruction_loss`
- `compute_nores_vocoder_losses`
  现在支持可选:
  - `loss_waveform`
  - `loss_stft`
  - `decoded_waveform_rms`
  - `target_waveform_rms`
- 训练 step / loop / dataset loop
  都已支持:
  - waveform decoder 头
  - aligned waveform L1
  - log-STFT bootstrap loss

### 3. `src/v5vc/cli.py`
- 以下入口新增:
  - `--waveform-weight`
  - `--stft-weight`
- 默认都为:
  - `0.0`
- 这样旧 proxy baseline
  行为保持不变，
  新 objective
  通过显式参数开启

## smoke 验证

### A. 单包 waveform/STFT train-step

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-train-step --train-targets reports/runtime/offline_mvp_nores_vocoder_train_targets_smoke_chapter3_3_firefly_162/offline_mvp_nores_vocoder_train_targets.pt --output-dir reports/runtime/offline_mvp_nores_vocoder_waveform_train_step_smoke_chapter3_3_firefly_162 --device cpu --seed 20260317 --waveform-weight 0.5 --stft-weight 0.5
```

结果:
- `decoder_frame_length = 400`
- `loss_total = 1.834025`
- `loss_waveform = 0.312810`
- `loss_stft = 1.359374`
- `grad_norm = 2.577615`

### B. dataset-level waveform/STFT smoke

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_waveform_dataset_loop_smoke_round1_1 --device cuda:0 --num-steps 2 --packages-per-step 2 --validation-interval 1 --checkpoint-interval 1 --sampler-mode shuffle --seed 20260317 --waveform-weight 0.5 --stft-weight 0.5
```

结果:
- step1 train `loss_total = 1.801747`
- step2 train `loss_total = 1.600885`
- step1 validation `loss_total = 1.625060`
- step2 validation `loss_total = 1.482311`

说明:
- 新 objective
  不只是单包 smoke
  能跑，
  主 dataset loop
  也已经能真正吃
  `aligned_waveform`

## baseline12

### 命令

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_waveform_stft_baseline12_round1_1 --device cuda:0 --num-steps 12 --packages-per-step 4 --validation-interval 6 --checkpoint-interval 6 --sampler-mode shuffle --seed 20260317 --waveform-weight 0.5 --stft-weight 0.5
```

### 结果
- dataset:
  - `592 train`
  - `66 validation`
- 总耗时:
  - `20.123913 sec`
- train `loss_total`:
  - step1 = `1.791887`
  - step6 = `1.165788`
  - step12 = `0.853014`
- validation `loss_total`:
  - step6 = `1.104648`
  - step12 = `0.811442`
- best checkpoint:
  - `step12`
  - `loss_total = 0.811442`

### waveform/STFT 子项变化
- validation `loss_waveform`:
  - step6 = `0.172122`
  - step12 = `0.105141`
- validation `loss_stft`:
  - step6 = `0.797781`
  - step12 = `0.447961`

## 当前判断

### 1. decoder / waveform-STFT objective 已经不再只是口头准备
- 现在 Stage5
  已经正式具备:
  - minimal decoder head
  - aligned waveform L1
  - log-STFT bootstrap loss
  - dataset-level GPU loop

### 2. 这条新 objective 是可训练的
- 不管看:
  - 单包 train-step
  - `2-step` dataset smoke
  - `12-step` baseline
- loss 都在正常下降
- 所以当前不能再写成:
  - “decoder / waveform-STFT
     还只是准备阶段”

### 3. 但它已经暴露出 loudness collapse 风险
- validation 平均
  `decoded_waveform_rms`:
  - step6 = `0.181111`
  - step12 = `0.077280`
- validation 平均
  `target_waveform_rms`:
  - step6 = `0.123402`
  - step12 = `0.123402`
- 这说明:
  - 当前 bootstrap objective
    虽然能持续降
    waveform / STFT loss
  - 但 decoder 振幅
    正在往偏小方向塌缩

先说人话:
- 现在不是
  “新 decoder 根本训不动”，
  而是
  “它已经能训，
    但学出来的声音
    越来越小”。
- 这比“完全跑不通”
  好很多，
  但也说明
  不能立刻把这版
  loss 配方
  当成正式长期主线。

## 当前边界
- 当前接入的是:
  - minimal frame decoder
  - aligned waveform L1
  - single-resolution log-STFT
    bootstrap loss
- 还不是:
  - MRSTFT
  - adversarial loss
  - feature matching
  - final Stage5 vocoder recipe

## 当前产物
- 单包 smoke:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_train_step_smoke_chapter3_3_firefly_162`
- dataset smoke:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_dataset_loop_smoke_round1_1`
- baseline12:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_baseline12_round1_1`

## 下一步建议
1. 不建议直接把
   当前 loss 配方
   粗暴拉到
   更长 horizon
2. 更合理的下一步是:
   - 给 waveform objective
     补 loudness / RMS guard
     或等价幅度约束
3. 在 loudness collapse
   被控制住之前，
   不建议把这版
   bootstrap objective
   误写成正式 Stage5
   decoder baseline 终稿

## 一句话结论
- 本轮已经把 Stage5
  从
  “准备接 decoder / waveform-STFT”
  正式推进到
  “minimal decoder +
   waveform/STFT dataset-level
   baseline 已跑通”，
  且 `12-step` validation
  从 `1.104648`
  降到 `0.811442`；
  但同时也发现
  `decoded_waveform_rms`
  明显低于目标 RMS，
  所以下一步应先补
  loudness guard，
  而不是盲目继续拉长训练。
