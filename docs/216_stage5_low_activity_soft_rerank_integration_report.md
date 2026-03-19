# 216. Stage5 low-activity soft rerank 接入 checkpoint selection 报告

## 背景
- `docs/215_stage5_low_activity_governance_sidecar_integration_report.md`
  已将
  low-activity
  指标接入 selection payload
  作为:
  - governance sidecar
- 但 sidecar
  仍只负责“展示 tradeoff”，
  还没有给出
  一个明确的
  near-best late candidate
  推荐结果

## 本轮目标
1. 保持:
   - `best_validation_checkpoint`
   - `selected_stable_late_stop`
   不变
2. 在此基础上，
   新增一层:
   - late candidate 内部的
     low-activity soft rerank
3. 把当前推荐结果
   明确写入
   selection payload

## 本轮代码变更

### 1. 修改文件
- `src/v5vc/nores_vocoder_checkpoint_selection.py`
- `src/v5vc/cli.py`

### 2. 新增 CLI 参数
- `--low-activity-soft-validation-ratio`
  - 默认:
    `1.05`

### 3. selection payload 新增内容
- 顶层新增:
  - `low_activity_soft_rerank`
- 每个 late candidate
  当前会附带:
  - `qualifies_for_low_activity_soft_rerank`
  - `low_activity_governance_score`
  - `low_activity_governance_breakdown`
  - `low_activity_soft_rerank_rank`

## 当前 soft rerank 规则

### 1. 只在 late candidates 内部生效
- 不看早期 checkpoint
- 不重写主 selector

### 2. 只允许 near-best validation 候选进入
- 当前门槛:
  - `loss_total <= best_validation * 1.05`
- 同时要求:
  - pairwise worsened ratio
    不超过
    现有 cap

### 3. 当前分数构成
- `mean_activity_alignment_mae`
  - 权重 `0.35`
- `mean_activity_excess_mean`
  - 权重 `0.35`
- `mean_active_fraction`
  - 权重 `0.2`
- `mean_fragmentation_score`
  - 权重 `0.1`

### 4. 当前解释
- 这是一个
  low-activity
  side objective
- 目的不是找
  “整体最优 checkpoint”
- 而是找
  “在主指标已经接近时，
  low-activity 行为更平衡的候选”

## 本轮真实重跑命令

```powershell
.\python.exe manage.py select-offline-mvp-nores-vocoder-checkpoint `
  --summary reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_round1_1 `
  --late-step-ratio 0.5 `
  --validation-guard-ratio 1.03 `
  --max-pairwise-worsened-ratio 0.2 `
  --max-rms-ratio-deviation 0.03 `
  --low-activity-probe reports/audio/stage5_low_activity_fragmentation_probe_activitygate60_vs_72_multisource/stage5_low_activity_fragmentation_probe.json `
  --low-activity-audio-source decoded `
  --low-activity-soft-validation-ratio 1.05
```

## 本轮验证

### 1. 语法校验

```powershell
.\python.exe -m py_compile src\v5vc\nores_vocoder_checkpoint_selection.py src\v5vc\cli.py
```

### 2. selection 重跑
- 已通过

### 3. 下游兼容性 smoke

```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_round1_1/nores_vocoder_checkpoint_selection.json `
  --selection-target best_validation `
  --split-name validation `
  --sample-count 1 `
  --output-dir tmp/stage5_selection_low_activity_soft_rerank_smoke `
  --activity-gate-weight 0.2 `
  --use-predicted-activity-gate
```

- 已通过

## 当前结果

### 1. 当前 soft rerank 只纳入了 `step60` 和 `step72`
- `soft_validation_threshold = 0.592905`
- 所以:
  - `step60 = 0.584654`
    进入
  - `step72 = 0.564671`
    进入
  - `step36 / step48`
    被排除

### 2. 当前推荐结果
- `selected_candidate = step72`
- 当前分数:
  - `step72 = 0.1`
  - `step60 = 0.9`

### 3. 为什么 `step72` 会胜出
- 它虽然
  `fragmentation`
  更高，
  但这项只占
  `10%`
- 它在以下三项都显著更优:
  - `alignment_mae`
  - `activity_excess_mean`
  - `active_fraction`
- 所以在
  low-activity
  side objective
  下，
  当前更平衡的 near-best late candidate
  仍然是
  `step72`

## 当前策略边界
1. `soft rerank`
   不会覆盖:
   - `best_validation_checkpoint`
   - `selected_stable_late_stop`
2. 它只是新增:
   - 一个有明确门槛、
     有明确权重、
     有可解释 breakdown
     的 governance recommendation
3. 因此当前策略层级是:
   - 一级:
     原 selector
   - 二级:
     low-activity soft rerank

## 一句话结论
- 本轮已经把
  low-activity
  从
  “只展示 tradeoff”
  推进到了
  “在 near-best late candidates 内部给出可解释推荐”。
- 当前在
  `activitygate60 vs 72`
  上，
  这层 soft rerank
  推荐的仍然是
  `step72`。
