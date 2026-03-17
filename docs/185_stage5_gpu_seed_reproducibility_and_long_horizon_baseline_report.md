# 185. Stage5 GPU seed 可复现性补齐与长程 baseline 报告

## 背景
- `docs/184_nores_vocoder_fullsplit_training_baseline_report.md`
  的正式口径
  还停在:
  - full-split package 池
  - `6-step`
  - dataset-level proxy baseline
- 但本次接班恢复时，
  工作区里已经存在
  尚未落盘的后续 runtime 产物:
  - `reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_smoke_round1_1`
  - `reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_baseline12_round1_1`
- 同时，
  代码侧已补:
  - Stage5 三个训练入口的 `--device`
    显式控制

## 恢复出的隐藏进展

### 1. GPU path 其实已经成立
- `2-step GPU smoke`
  已跑通:
  - device = `cuda:0`
  - validation `loss_total = 0.720063`
- `12-step GPU baseline`
  也已跑通:
  - step3 = `0.676120`
  - step6 = `0.599989`
  - step9 = `0.558026`
  - step12 = `0.539549`

### 2. 当前正式口径需要纠正
- 所以真实停点
  已不只是:
  - CPU / default route 下的
    `6-step baseline`
- 而是已经进入:
  - GPU-backed
  - longer-horizon
  - full-split proxy baseline

## 本轮先补的工程缺口

### 1. 问题
- 旧版 Stage5 dataset loop
  虽然有:
  - `--seed`
- 但它只用于:
  - package sampler 顺序
- 没有用于:
  - model initialization
  - Torch / CUDA 随机状态

### 2. 本轮修正
- `src/v5vc/offline_vocoder_training.py`
  新增统一种子设置:
  - `torch.manual_seed(seed)`
  - `torch.cuda.manual_seed_all(seed)`
- `src/v5vc/cli.py`
  为以下入口补齐 / 统一
  seed 语义:
  - `run-offline-mvp-nores-vocoder-train-step`
  - `run-offline-mvp-nores-vocoder-training-loop`
  - `run-offline-mvp-nores-vocoder-dataset-training-loop`
- summary 里也开始写入:
  - `training.seed`
  - `reproducibility.seed`

## 本轮新实验

### A. seeded GPU baseline24
命令:

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_seeded_baseline24_round1_1 --device cuda:0 --num-steps 24 --packages-per-step 8 --validation-interval 6 --checkpoint-interval 6 --sampler-mode shuffle --seed 20260317
```

结果:
- 总耗时:
  - `3.084492 sec`
- validation `loss_total`:
  - step6 = `0.614341`
  - step12 = `0.533927`
  - step18 = `0.490061`
  - step24 = `0.469644`
- best checkpoint:
  - `step24`
  - `loss_total = 0.469644`

### B. seeded GPU baseline48
命令:

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_seeded_baseline48_round1_1 --device cuda:0 --num-steps 48 --packages-per-step 8 --validation-interval 12 --checkpoint-interval 12 --sampler-mode shuffle --seed 20260317
```

结果:
- 总耗时:
  - `3.754564 sec`
- validation `loss_total`:
  - step12 = `0.533927`
  - step24 = `0.469644`
  - step36 = `0.449341`
  - step48 = `0.441292`
- best checkpoint:
  - `step48`
  - `loss_total = 0.441292`

## 当前判断

### 1. Stage5 主线已经推进到 seeded GPU long-horizon baseline
- 当前正式最新停点
  应更新为:
  - full-split
  - GPU-backed
  - seeded
  - `48-step`
  - proxy baseline

### 2. 当前还看不到“先重构 loader”的必要性
- `48-step`
  覆盖:
  - `592 train`
  - `66 validation`
  - 全 validation pass
  - checkpoint 落盘
- 总耗时
  仍只有:
  - `3.754564 sec`
- 所以当前更像是:
  - 训练目标还值得继续挖
- 而不是:
  - loader 已先成为主瓶颈

### 3. 当前 proxy baseline 仍然没有收敛完成，但下降趋势明确
- 从:
  - `6-step baseline = 0.593835`
- 到:
  - undocumented GPU `12-step = 0.539549`
- 再到:
  - seeded GPU `24-step = 0.469644`
  - seeded GPU `48-step = 0.441292`
- 这说明:
  - 当前 proxy objective
    仍然能从更长 horizon
    中继续获益

## 当前边界
- 当前全部结论
  仍然只针对:
  - spectral/gate proxy target
- 还不是:
  - decoder baseline
  - waveform-STFT objective
  - final vocoder objective

## 当前产物
- undocumented restore 参考:
  - `reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_smoke_round1_1`
  - `reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_baseline12_round1_1`
- seeded baseline24:
  - `reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_seeded_baseline24_round1_1`
- seeded baseline48:
  - `reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_seeded_baseline48_round1_1`

## 下一步建议
1. 若继续沿当前 proxy objective
   深挖，
   优先做:
   - `step48` 之后的更长 horizon
     checkpoint review
   - 或再拉一档
     `96-step`
     seeded baseline
2. 在当前量级下，
   不建议把主线先切回:
   - packed loader
   - cache 重构
3. 只有当 proxy baseline
   的 horizon 收益明显放缓后，
   再优先转向:
   - decoder / waveform-STFT
     目标

## 一句话结论
- Stage5 当前真实最新停点，
  已经不是 `docs/184` 的
  `6-step baseline`，
  而是补齐 seed 可复现性后，
  在 full-split package 池上
  跑通了 `cuda:0` 的
  `48-step` long-horizon proxy baseline，
  并把 validation `loss_total`
  继续压到 `0.441292`。
