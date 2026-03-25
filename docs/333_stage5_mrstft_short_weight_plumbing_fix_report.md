# 333. Stage5 short-window MRSTFT 权重调用链补齐与 dataset-loop 日志修复报告

## 结论
- `loss_mrstft_short_256_512_1024` 之前长期为 `0.0`，
  不是因为实验已经证明
  short-window MRSTFT
  无效，
  而是因为
  `run-offline-mvp-nores-vocoder-dataset-training-loop`
  的 CLI 分支没有把
  `--multires-stft-short-weight`
  继续下传到
  `run_offline_mvp_nores_vocoder_dataset_training_loop(...)`。
- 同时，
  dataset-loop summary
  顶层
  `training.loss_weights`
  也漏记了
  `multires_stft_short`，
  导致即使底层已实现，
  从日志上也无法确认权重是否真正生效。
- 这两处已于
  `2026-03-25`
  补齐，
  并通过新的 CLI smoke
  验证：
  - `training.loss_weights.multires_stft_short = 0.2`
  - `step_history[0].loss_metrics.loss_mrstft_short_256_512_1024 = 1.305642`
  - `validation_history[0].loss_metrics.loss_mrstft_short_256_512_1024 = 1.103331`

## 本次修复内容

### 1. 调用链补齐
- 文件：
  - `src/v5vc/cli.py`
- 修复点：
  - 在
    `args.command == "run-offline-mvp-nores-vocoder-dataset-training-loop"`
    分支中，
    显式传入：
    - `multires_stft_short_weight=args.multires_stft_short_weight`
- 结果：
  - dataset-level CLI
    终于和已经补过的底层训练函数口径一致，
    新权重可以沿
    CLI -> dataset loop -> per-package loss
    全链路传到底。

### 2. 日志口径补齐
- 文件：
  - `src/v5vc/offline_vocoder_training.py`
- 修复点：
  - 在
    `run_offline_mvp_nores_vocoder_dataset_training_loop(...)`
    产出的 summary
    顶层
    `training.loss_weights`
    中新增：
    - `multires_stft_short`
- 结果：
  - 后续不再需要通过读代码猜
    “到底有没有把新权重传进去”，
    直接看 summary
    就能确认。

## 验证

### 验证命令
```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop `
  --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_cli_mrstftshort020_probe_round1_2 `
  --num-steps 1 `
  --packages-per-step 1 `
  --validation-interval 1 `
  --checkpoint-interval 1 `
  --sampler-mode sequential `
  --seed 20260325 `
  --deterministic `
  --waveform-weight 0.5 `
  --stft-weight 0.5 `
  --rms-guard-weight 0.2 `
  --multires-stft-short-weight 0.2
```

### 验证结果
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_cli_mrstftshort020_probe_round1_2/`
- 核对到的关键字段：
  - `training.loss_weights.multires_stft_short = 0.2`
  - `step_history[0].loss_metrics.loss_mrstft_short_256_512_1024 = 1.305642`
  - `validation_history[0].loss_metrics.loss_mrstft_short_256_512_1024 = 1.103331`
- 解释：
  - 这说明 short-window MRSTFT
    已经不是“只在代码里定义了名字”，
    而是确实进入了 dataset-level CLI 训练路径，
    并被日志真实记录。

## 对当前实验结论的影响
- 之前
  `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_mrstftshort020_smoke_round1_1/`
  中看到的
  `loss_mrstft_short_256_512_1024 = 0.0`
  不能再被拿来当作
  short-window MRSTFT
  的实验结论。
- 更准确的表述应改为：
  - 那一轮 smoke
    只是把
    “CLI 参数已声明、底层损失已实现”
    跑到了
    “dataset-level 命令入口尚未接通”
    的半成品状态。

## 补充：已完成纠正后的 overfit24 重跑
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_mrstftshort020_smoke_round1_2/`
- 运行口径：
  - 与旧的
    `round1_1`
    保持同一 tiny paired dataset、
    `24` 步、
    `packages_per_step = 2`、
    `--use-predicted-activity-gate`、
    `--multires-stft-short-weight 0.2`
  - 但这次权重已真正接通
- 新结果中已确认：
  - `training.loss_weights.multires_stft_short = 0.2`
  - `step24 loss_mrstft_short_256_512_1024 = 0.345859`
  - `validation step24 loss_mrstft_short_256_512_1024 = 0.336557`
  - `validation step24 loss_total = 0.914235`
- 与旧的未接通日志相比：
  - 旧
    `round1_1`
    的
    `validation step24 loss_total = 0.94829`
  - 旧
    `round1_1`
    的
    `validation step24 loss_mrstft_short_256_512_1024 = 0.0`
  - 新
    `round1_2`
    的对应值变为：
    - `0.914235`
    - `0.336557`
- 这至少说明：
  - 现在已经拿到了第一份真正包含
    short-window MRSTFT
    的 dataset-level smoke
  - 后续是否“有收益”，
    应基于
    `round1_2`
    继续判断，
    不再参考旧的全零口径

## 下一步
1. 以
   `round1_2`
   为新的有效基线，
   重新判断：
   - short-window MRSTFT
     是否真的带来有意义的共享指标变化。
2. 在新日志基础上，
   再决定它是：
   - 保留为有效 loss family
   - 还是正式判定为“接通后仍无收益”。
