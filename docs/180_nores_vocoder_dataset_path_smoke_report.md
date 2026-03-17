# 180. no-residual vocoder dataset path smoke 报告

## 背景
- `docs/179_nores_vocoder_training_loop_smoke_report.md`
  已确认:
  - Stage5 最小多步 loop
    已成立
  - 但它仍停在:
    - 单 package 反复训练
- 所以上次停点后的下一步，
  就是把 Stage5
  从:
  - 单 package plumbing
  推到:
  - split-backed dataset path

## 本轮目标
1. 把 `offline_vocoder_training.py`
   中已写出的 dataset 级能力
   正式接到 CLI
2. 用 `round1_1`
   正式 split
   物化最小 dataset index
3. 跑通最小 dataset-level loop smoke，
   确认:
   - train package 采样
   - 独立 validation package
   - checkpoint series
   都已成立

## 本轮代码落地

### 1. 已新增 Stage5 dataset package builder CLI
- 新增命令:
  - `build-offline-mvp-nores-vocoder-dataset-packages`

当前能力:
- 从 `target_train.jsonl / target_validation.jsonl`
  读取记录
- 对每条记录顺序构建:
  - teacher downstream contract
  - teacher vocoder input scaffold
  - no-residual train-target package
- 最终写出:
  - `offline_mvp_nores_vocoder_dataset_index.json`
  - `offline_mvp_nores_vocoder_dataset_index.md`

### 2. 已新增 Stage5 dataset training loop CLI
- 新增命令:
  - `run-offline-mvp-nores-vocoder-dataset-training-loop`

当前能力:
- 读取 dataset index
- 每 step
  从 train packages
  采样多个 package
- 对 validation packages
  做独立 validation
- 持续落盘:
  - step history
  - validation history
  - checkpoint series
  - best checkpoint

## smoke test

### 步骤 1. 物化最小 dataset packages

```powershell
.\python.exe manage.py build-offline-mvp-nores-vocoder-dataset-packages --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_path_smoke_round1_1 --max-train-records 2 --max-validation-records 1 --selection-mode shortest_duration --device cpu
```

结果:
- train packages:
  - `target::chapter3_22_firefly_105`
  - `target::chapter3_17_firefly_138`
- validation packages:
  - `target::chapter3_3_firefly_162`
- dataset index:
  - `train_package_count = 2`
  - `validation_package_count = 1`

### 步骤 2. 跑 dataset-level 3-step loop smoke

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_path_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_smoke_round1_1 --num-steps 3 --packages-per-step 2 --validation-interval 1 --checkpoint-interval 1 --sampler-mode sequential
```

结果:
- 总耗时:
  - `duration_sec = 1.327001`
- train step `loss_total`:
  - `step1 = 1.088626`
  - `step2 = 0.940188`
  - `step3 = 0.822948`
- validation `loss_total`:
  - `step1 = 0.946483`
  - `step2 = 0.825`
  - `step3 = 0.738584`
- best checkpoint:
  - `step3`
  - `loss_total = 0.738584`

## 当前判断

### 1. Stage5 dataset path 已正式接通
- 现在已经不只是:
  - 单 package train-target
  - 单 package loop
- 还已经具备:
  - split-backed package builder
  - dataset index
  - 多 package 采样训练
  - 独立 validation package

### 2. 这次 smoke 回答的是“dataset plumbing 已成立”
- 它已经证明:
  - Stage5 可以从正式 split
    走到 dataset-level loop
- 但它还没有证明:
  - 全量 split 吞吐可接受
  - 当前 proxy objective
    已经足够好
  - 最终 waveform decoder
    已经有方向定论

### 3. 当前真实停点已推进到“Stage5 dataset-level baseline”
- 所以下次恢复上下文时，
  不应再把 Stage5
  误判回:
  - 只有 single-package loop
  - 或只有 next step 草案

## 当前边界
- 当前 smoke
  只物化了:
  - `2` 个 train package
  - `1` 个 validation package
- 当前 package export
  仍会:
  - 按记录重复走 teacher runtime
  - 按记录重载 package
- 当前 loop
  仍是:
  - Python 级 package 列表采样
  - 不是 packed dataloader
- 所以现在只能写成:
  - Stage5 dataset path established
- 不能写成:
  - Stage5 dataset training throughput ready
  - final vocoder training pipeline completed

## 当前产物
- dataset index:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_path_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_path_smoke_round1_1/offline_mvp_nores_vocoder_dataset_index.md`
- dataset loop:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_smoke_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json`
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_smoke_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.md`
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_smoke_round1_1/checkpoints/`

## 下一步
1. 把当前 smoke
   从超小 subset
   推到更大的 split-backed package 池，
   先摸清:
   - teacher runtime 导出耗时
   - package 落盘体积
2. 决定 Stage5 dataset path
   下一步更偏向:
   - 先做 package cache / packed loader
   - 还是先切到 decoder / waveform-STFT 目标
3. 在 throughput 边界清楚前，
   不要把当前 dataset path
   误写成:
   - 可直接全量正式训练

## 一句话结论
- 本轮已经把 Stage5
  从“单 package loop 已成立”
  推进到“split-backed dataset path 也已跑通”；
  当前下一步应转向
  更大 package 池与 throughput 边界，
  再决定是否继续优化 proxy objective
  还是切向 decoder 目标。
