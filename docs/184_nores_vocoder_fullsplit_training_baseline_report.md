# 184. no-residual vocoder full-split training baseline 报告

## 背景
- `docs/183_nores_vocoder_fullsplit_export_measurement_report.md`
  已确认:
  - Stage5 full-split package export
    已成立
  - `--skip-existing`
    复用已足够快
- 所以下一环节
  不该再停在导出侧，
  而是直接验证:
  - full-split package 池
    上的 dataset-level training

## 本轮目标
1. 基于 full-split package 池
   跑一版正式 baseline loop
2. 确认:
   - 多 package 采样训练
   - 全 validation package
     评估
   - checkpoint 落盘
     都已成立
3. 给 Stage5
   一个真正可继续迭代的
   full-split baseline 停点

## baseline loop

### 命令

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_baseline_round1_1 --num-steps 6 --packages-per-step 8 --validation-interval 3 --checkpoint-interval 3 --sampler-mode shuffle --seed 20260317
```

### 训练配置
- dataset:
  - `592 train`
  - `66 validation`
- loop:
  - `num_steps = 6`
  - `packages_per_step = 8`
  - `validation_interval = 3`
  - `checkpoint_interval = 3`
- sampler:
  - `shuffle`
  - `seed = 20260317`

## 结果
- 总耗时:
  - `duration_sec = 2.697842`
- train `loss_total`:
  - `step1 = 0.936593`
  - `step2 = 0.819006`
  - `step3 = 0.710484`
  - `step4 = 0.661867`
  - `step5 = 0.608702`
  - `step6 = 0.625163`
- validation `loss_total`:
  - `step3 = 0.638567`
  - `step6 = 0.593835`
- best checkpoint:
  - `step6`
  - `loss_total = 0.593835`

## 当前判断

### 1. Stage5 full-split dataset-level baseline 已成立
- 现在已经不只是:
  - full-split package export
- 还已经具备:
  - full-split dataset loop
  - 全 validation package
    评估
  - checkpoint selection

### 2. 当前优先级判断被训练侧验证通过
- 这次 baseline
  说明:
  - 不需要先停下来
    重写 cache / loader
  - 当前 package 池
    已经足够支持
    一版正式 baseline 训练

### 3. 当前训练结论仍然只是 proxy baseline
- 这里验证的是:
  - spectral/gate proxy target
    的 dataset-level loop
- 还不是:
  - waveform decoder baseline
  - 最终 vocoder objective

## 当前边界
- 当前 loop
  仍是:
  - Python 级逐包加载
- 当前 validation
  仍是:
  - proxy spectral/gate validation
- 当前训练步数
  只有:
  - `6 step`
- 所以现在只能写成:
  - full-split Stage5 proxy baseline established
- 不能写成:
  - Stage5 training converged
  - final vocoder baseline ready

## 当前产物
- summary:
  - `reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_baseline_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`
  - `reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_baseline_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.md`
- checkpoints:
  - `step3`
  - `step6`

## 下一步
1. 在当前 full-split baseline
   之上，
   决定下一版更偏向:
   - 拉长 step
   - 增加 packages_per_step
   - 还是补更细的 validation 监控
2. 继续观察:
   - 逐包加载是否开始成为训练瓶颈
3. 只有在 proxy baseline
   稳定后，
   再决定何时切向:
   - decoder / waveform-STFT
     目标

## 一句话结论
- Stage5 现在已经不只是
  “full-split package 能导出”，
  而是已经能基于
  `658` 个 package
  跑通 full-split dataset-level baseline loop；
  当前主线应继续推进
  proxy baseline 训练，
  而不是退回 export/cache 争论。
