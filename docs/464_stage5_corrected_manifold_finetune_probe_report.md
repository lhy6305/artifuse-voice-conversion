# 464 Stage5 corrected-manifold finetune probe report

## 结论
- 这轮先补了一个必要入口：Stage5 dataset loop 现在支持 `--init-checkpoint`，可以从既有 no-res vocoder checkpoint 做真正 finetune，而不是误跑成随机初始化。
  - 变更文件：
    - `src/v5vc/cli.py`
    - `src/v5vc/offline_vocoder_training.py`
- 然后做了最小 fail-fast finetune 对照：
  - `base train/val 3` from promoted step24 checkpoint
  - `corrected-manifold train/val 3` from同一个 promoted step24 checkpoint
  - 同样的 loss 配方、同样的 `6 steps / lr=1e-4`
- 结果是否定，但信息量足够大：
  - 两条 finetune 都能继续压低 `centroid/high_band/template`
  - 但都仍然是 `3/3 auto_reject_obvious_buzz`
  - corrected-manifold finetune 在训练 validation 上反而差于 base finetune
  - 更关键的是，交叉 handoff 证明“改输入”比“在 corrected 输入上再微调权重”更重要

一句话更新主线判断：
- `corrected input manifold` 是真实有效杠杆
- `corrected-manifold micro-finetune` 这轮没有学出比 `base-finetune` 更好的权重
- 所以下一步不该继续在这条 3-record 微调线上加码

## A. 入口修复

### 变更
- `run-offline-mvp-nores-vocoder-dataset-training-loop` 新增：
  - `--init-checkpoint`
- 初始化逻辑：
  - 从 checkpoint 读取 `model_state_dict`
  - 通过 checkpoint 自带 `model_config` 恢复模型结构
  - 恢复 `optimizer_state_dict`
  - 然后把 optimizer `lr` 显式重置成命令行传入值，避免继续沿用旧 checkpoint 学习率

### 验证
- `python -m py_compile src/v5vc/cli.py src/v5vc/offline_vocoder_training.py`
- `python manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --help`

## B. 最小 finetune 数据集

### dataset indices
- base:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_base_trainval3_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- corrected:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_corr_trainval3_round1_1/offline_mvp_nores_vocoder_dataset_index.json`

### notes
- 两者都只含同一组 `3` 条记录
- `train_packages` 与 `validation_packages` 共享同一最小集合
- corrected 数据集来自：
  - `acousticstateswap + eventzero`

## C. finetune runs

### shared setup
- init checkpoint:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_acttmpl005_zerojitter4_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt`
- training:
  - `num_steps = 6`
  - `packages_per_step = 3`
  - `validation_interval = 3`
  - `checkpoint_interval = 3`
  - `learning_rate = 1e-4`
  - same promoted loss family:
    - `waveform = 0.5`
    - `stft = 0.5`
    - `rms_guard = 0.2`
    - `activity_gate = 0.2`
    - `active_template = 0.05`
    - `frame_spectral_flux_zero_target_jitter = 4.0`

### outputs
- base finetune:
  - run:
    - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_base_trainval3_round1_1/`
  - best checkpoint:
    - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_base_trainval3_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step6.pt`
  - best validation loss:
    - `1.123916`
- corrected finetune:
  - run:
    - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr_trainval3_round1_1/`
  - best checkpoint:
    - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr_trainval3_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step6.pt`
  - best validation loss:
    - `1.145162`

### immediate read
- 在最小 3-record setting 下，corrected-manifold finetune 没有带来更好的 validation 轨迹。

## D. Handoff comparison

### direct before/after

| variant | auto_reject | centroid_gap | high_band_gap | template_cos | rms_corr | fused_template | waveform_template |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `base_pre` | 3 | 9278.554688 | 0.712497 | 0.943517 | 0.900798 | 0.963773 | 0.962746 |
| `base_ft` | 3 | 9143.567383 | 0.703061 | 0.938025 | 0.899558 | 0.962813 | 0.960035 |
| `corr_pre` | 3 | 9116.155273 | 0.711012 | 0.936230 | 0.909780 | 0.957994 | 0.958754 |
| `corr_ft` | 3 | 9018.030273 | 0.701364 | 0.932198 | 0.905800 | 0.957134 | 0.956447 |

### interpretation
- 两条 finetune 都在 absolute metrics 上继续向好：
  - `centroid_gap` 继续下降
  - `high_band_gap` 继续下降
  - `template_cos` 继续下降
- 但没有一条把 route 从 `auto_reject_obvious_buzz` 里拉出来

## E. 4-quadrant cross evaluation

### matrix
- `base_ft_on_base`
  - `auto_reject = 3/3`
  - `centroid_gap = 9143.567383`
  - `high_band_gap = 0.703061`
  - `template_cos = 0.938025`
  - `rms_corr = 0.899558`
- `corr_ft_on_corr`
  - `auto_reject = 3/3`
  - `centroid_gap = 9018.030273`
  - `high_band_gap = 0.701364`
  - `template_cos = 0.932198`
  - `rms_corr = 0.905800`
- `corr_ft_on_base`
  - `auto_reject = 3/3`
  - `centroid_gap = 9178.089844`
  - `high_band_gap = 0.703913`
  - `template_cos = 0.939804`
  - `rms_corr = 0.896531`
- `base_ft_on_corr`
  - `auto_reject = 3/3`
  - `centroid_gap = 8992.117188`
  - `high_band_gap = 0.701809`
  - `template_cos = 0.930842`
  - `rms_corr = 0.908202`

### key separation
- 在 **base input** 上：
  - `corr_ft ckpt` 比 `base_ft ckpt` 更差
  - delta:
    - `template +0.001779`
    - `high_band +0.000852`
    - `centroid +34.522461`
    - `rms_corr -0.003027`
- 在 **corrected input** 上：
  - `base_ft ckpt` 反而略优于 `corr_ft ckpt`
  - delta:
    - `template -0.001356`
    - `high_band +0.000445`
    - `centroid -25.913085`
    - `rms_corr +0.002402`

### meaning
- 这组交叉结果已经很清楚：
  - improvement 主要来自 `corrected input`
  - 不是来自 `corrected-manifold finetune` 学出了更好的 checkpoint
- 换句话说：
  - corrected 输入流形是真杠杆
  - 但这轮 3-record micro-finetune 没把这个杠杆固化成更好的权重

## 当前更新后的判断
- 不建议继续沿着“3-record corrected-manifold micro-finetune”扩大搜索。
- 它已经给出足够明确的负结论：
  - 能改善指标
  - 但打不开 route
  - 且没有学出优于 base-finetune 的权重

## 下一步
- 更合理的主线只剩两条：
  1. 如果还要走训练线，就直接升级到更大 corrected-manifold dataset，而不是继续在 3-record 微调上迭代
  2. 否则就转去更深层的 decoder/fusion attractor 修复，因为当前 fixed family 仍然把所有路线锁在 buzz basin 内
