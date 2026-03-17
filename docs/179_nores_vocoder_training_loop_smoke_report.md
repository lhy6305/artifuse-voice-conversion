# 179. no-residual vocoder 最小多步 loop smoke 报告

## 背景
- `docs/178_nores_vocoder_training_contract_and_single_step_smoke_report.md`
  已确认:
  - Stage5 最小 train-target package
    已成立
  - 单步:
    - loss
    - backward
    - optimizer step
    - checkpoint
    已成立
- 但如果继续停在
  single-step smoke，
  那么 Stage5
  仍缺:
  - 连续 step 轨迹
  - 周期 validation
  - checkpoint series
  - best checkpoint 口径

## 本轮目标
1. 在当前单步训练之上，
   补最小多步训练 loop
2. 让 Stage5
   也能像前面阶段一样
   持续落盘:
   - step history
   - validation history
   - checkpoint series
3. 用最小 `3-step` smoke
   验证 loop 逻辑已成立

## 本轮代码落地

### 1. `offline_vocoder_training.py` 已新增最小 loop
- 新增函数:
  - `run_offline_mvp_nores_vocoder_training_loop`

当前能力:
- 读取 train-target package
- 可选读取独立 validation package
- 按 step 循环:
  - 前向
  - loss
  - backward
  - grad clipping
  - optimizer step
- 周期写出:
  - `step_history`
  - `validation_history`
  - `checkpoints`
  - `best_checkpoint`

### 2. 已新增正式 CLI
- 新增命令:

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-training-loop --train-targets <package.pt>
```

说明:
- 当前若不传
  `--validation-targets`，
  会复用 train package
  做 plumbing 级 validation
- 这只是最小工程验证，
  不是正式泛化评估

## smoke test

### 命令

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-training-loop --train-targets reports/runtime/offline_mvp_nores_vocoder_train_targets_smoke_chapter3_3_firefly_162/offline_mvp_nores_vocoder_train_targets.pt --output-dir reports/runtime/offline_mvp_nores_vocoder_training_loop_smoke_chapter3_3_firefly_162 --num-steps 3 --validation-interval 1 --checkpoint-interval 1
```

### 结果
- 总耗时:
  - `duration_sec = 1.414744`
- train / validation frame_count:
  - `167 / 167`
- step 级 `loss_total`:
  - `step1 = 1.001534`
  - `step2 = 0.864256`
  - `step3 = 0.767466`
- validation `loss_total`:
  - `step1 = 0.864256`
  - `step2 = 0.767466`
  - `step3 = 0.704201`
- best checkpoint:
  - `step3`
  - `loss_total = 0.704201`

### 当前产物
- loop summary:
  - `reports/runtime/offline_mvp_nores_vocoder_training_loop_smoke_chapter3_3_firefly_162/logs/offline_mvp_nores_vocoder_loop.summary.json`
  - `reports/runtime/offline_mvp_nores_vocoder_training_loop_smoke_chapter3_3_firefly_162/offline_mvp_nores_vocoder_loop.summary.md`
- checkpoints:
  - `step1`
  - `step2`
  - `step3`
    都已写出

## 当前判断

### 1. Stage5 最小可迭代训练骨架已成立
- 现在已经不只是
  “跑一个 optimizer step”
- 而是已经能持续记录:
  - 多 step 下降轨迹
  - 周期 validation
  - checkpoint series
  - best checkpoint

### 2. 当前 loop 仍只是 plumbing 级验证
- 当前 smoke
  只在单个 aligned package
  上重复训练
- 而且 validation
  默认复用了同一 package
- 所以它只能说明:
  - 训练 loop 工程已成立
- 不能说明:
  - Stage5 已有泛化能力
  - 当前目标定义已经足够好

### 3. 当前真实停点已推进到“Stage5 可持续迭代”
- 所以下次恢复上下文时，
  不应再把 Stage5
  误判回:
  - 只有 single-step smoke
  - 或只有 scaffold

## 当前边界
- 当前仍没有:
  - dataset-level package sampling
  - 独立 validation set
  - decoder / upsampling
  - waveform reconstruction
  - audio export
- 所以现在只能写成:
  - minimal iterative training loop established
- 不能写成:
  - vocoder training pipeline completed

## 下一步
1. 把当前 loop
   从:
   - 单 package 反复训练
   推到:
   - 多 package / dataset-level
     采样训练
2. 准备独立 validation package，
   避免继续用
   `train_targets_reused`
   充当泛化评估
3. 基于 loop 稳定后再决定:
   - 继续沿 spectral/gate proxy
   - 还是切向更接近 waveform 的 decoder 目标

## 一句话结论
- 本轮已经把 Stage5
  从“最小训练合同 + 单步 smoke”
  推进到“最小多步 loop 也已跑通”；
  当前下一步应转向
  dataset-level package 构建与独立 validation，
  而不是继续停留在单样本单步验证。
