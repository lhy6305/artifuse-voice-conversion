# 218. Stage5 low-activity probe 四候选扩展与治理边界复核报告

## 背景
- `docs/217_stage5_low_activity_soft_rerank_sensitivity_report.md`
  已完成
  `step60 vs step72`
  的敏感性分析
- 但上一轮仍有一个明显边界:
  - 当前 low-activity probe
    只覆盖
    `step60`
    与
    `step72`
  - ratio sweep
    本质上仍停留在
    二选一

## 本轮目标
1. 为
   `activitygate72`
   family
   补齐:
   - `step36`
   - `step48`
   的 validation bundle
2. 把 low-activity probe
   扩到:
   - `step36`
   - `step48`
   - `step60`
   - `step72`
3. 重跑:
   - selection sidecar
   - soft rerank
   - sensitivity
4. 判断当前二选一稳健性
   是真实策略稳健，
   还是样本切片本身已经塌缩

## 本轮代码补充

### 1. 修正 low-activity governance tie 表达
- 修改:
  - `src/v5vc/nores_vocoder_checkpoint_selection.py`
- 当前当多个 branch
  在同一指标上完全并列时，
  不再假装只有一个
  winner
- 会显式写成:
  - 并列 branch 组

### 2. 修正 sensitivity locality note
- 修改:
  - `src/v5vc/nores_vocoder_low_activity_sensitivity.py`
- 当前 sensitivity
  的备注会根据
  实际覆盖到的
  late candidates
  动态生成
- 不再把
  “只覆盖 `60/72`”
  这种旧口径
  留在新结果里

## 本轮执行命令

### 1. 补导出 `step36` / `step48`

```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  --checkpoint reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step36.pt `
  --split-name validation `
  --target-record-ids target::chapter3_3_firefly_162 target::chapter3_22_firefly_114 target::chapter3_3_firefly_213 target::chapter3_3_firefly_122 target::chapter3_4_firefly_109 target::chapter3_4_firefly_106 `
  --sample-count 6 `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate36_decodedpitchmatch_validation_round1_1 `
  --listening-audio-source decoded_pitch_matched `
  --pitch-match-reference aligned_target `
  --activity-gate-weight 0.2 `
  --use-predicted-activity-gate

.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  --checkpoint reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step48.pt `
  --split-name validation `
  --target-record-ids target::chapter3_3_firefly_162 target::chapter3_22_firefly_114 target::chapter3_3_firefly_213 target::chapter3_3_firefly_122 target::chapter3_4_firefly_109 target::chapter3_4_firefly_106 `
  --sample-count 6 `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate48_decodedpitchmatch_validation_round1_1 `
  --listening-audio-source decoded_pitch_matched `
  --pitch-match-reference aligned_target `
  --activity-gate-weight 0.2 `
  --use-predicted-activity-gate
```

### 2. 四候选 low-activity probe

```powershell
.\python.exe manage.py analyze-stage5-low-activity-fragments `
  --bundle `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate36_decodedpitchmatch_validation_round1_1 `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate48_decodedpitchmatch_validation_round1_1 `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate60_decodedpitchmatch_validation_round1_1 `
    reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decodedpitchmatch_validation_round1_1 `
  --analysis-audio-sources decoded `
  --output-dir reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_round1_1 `
  --top-k-windows 8
```

### 3. 用四候选 probe 重跑 selection 与 sensitivity

```powershell
.\python.exe manage.py select-offline-mvp-nores-vocoder-checkpoint `
  --summary reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_round1_1 `
  --late-step-ratio 0.5 `
  --validation-guard-ratio 1.03 `
  --max-pairwise-worsened-ratio 0.2 `
  --max-rms-ratio-deviation 0.03 `
  --low-activity-probe reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_round1_1/stage5_low_activity_fragmentation_probe.json `
  --low-activity-audio-source decoded `
  --low-activity-soft-validation-ratio 1.05

.\python.exe manage.py analyze-offline-mvp-nores-vocoder-low-activity-sensitivity `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_round1_1/nores_vocoder_checkpoint_selection.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_low_activity_sensitivity_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_round1_1 `
  --weight-step 0.05
```

## 四候选 probe 结果

### 1. `step36 / 48 / 60` 在当前 6-record 低活动切片上几乎完全塌成同一类
- decoded aggregate:
  - 三者都为:
    - `mean_fragmentation_score = 0.0`
    - `mean_active_fraction = 1.0`
    - `mean_activity_alignment_mae = 0.975229`
    - `mean_activity_excess_mean = 0.975229`
- 只有
  `mean_sample_delta_peak`
  还略有区别:
  - `step36 = 0.335038`
  - `step48 = 0.231301`
  - `step60 = 0.223779`

### 2. `step72` 仍然是唯一明显不同的一类
- `mean_fragmentation_score = 1.222465`
- `mean_active_fraction = 0.521389`
- `mean_activity_alignment_mae = 0.546807`
- `mean_activity_excess_mean = 0.546807`

### 3. 当前最重要的新事实
- 这轮扩展后，
  不是
  `48`
  挑战了
  `72`
- 而是发现:
  - 当前 low-activity
    这组样本窗
    对
    `36/48/60`
    的区分能力几乎为零

## 对 selection / sensitivity 的影响

### 1. 当前 soft rerank 结果不变
- 仍然是:
  - `step72`
    胜
    `step60`
- 当前默认:
  - `soft_validation_ratio = 1.05`
  - 权重
    `0.35 / 0.35 / 0.2 / 0.1`
  都未变化

### 2. ratio sweep 现在终于不只剩二选一
- 当前 metric-ready late candidates
  已变为:
  - `72`
  - `60`
  - `48`
  - `36`
- 进入 soft rerank
  的门槛分别是:
  - `step72 = 1.0`
  - `step60 = 1.035389`
  - `step48 = 1.110966`
  - `step36 = 1.259344`

### 3. 但推荐仍完全不变
- 即使把 ratio
  放宽到:
  - `1.110966`
    纳入
    `step48`
  - `1.259344`
    纳入
    `step36`
- 选中的仍然都是:
  - `step72`

### 4. 当前翻盘边界也不变
- `fragmentation_weight`
  仍然要到:
  - `0.55`
  以上，
  推荐才会翻到
  `step60`
- `step48`
  和
  `step36`
  没有形成新的翻盘路线

## 当前解释

### 1. 这轮不是“证明当前策略跨更多 checkpoint 仍然很强”
- 更准确的说法是:
  - 当前 probe
    把
    `36/48/60`
    都看成了同一类
- 所以:
  - 新增 checkpoint
    没有改变推荐，
    主要不是因为
    rerank
    真的学会了更细腻取舍，
  - 而是因为
    当前低活动切片
    没给出新的区分信息

### 2. 这轮真正把下一步需求说清了
- 后续若还想继续提升
  low-activity governance
  的区分能力，
  优先不是:
  - 再调一轮权重
- 而是:
  - 扩大 record 范围
  - 扩大低活动窗口类型
  - 或补更能区分
    `36/48/60`
    的指标

## 当前产物
- 四候选 probe:
  - `reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_round1_1/`
- 四候选 selection:
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_round1_1/`
- 四候选 sensitivity:
  - `reports/runtime/offline_mvp_nores_vocoder_low_activity_sensitivity_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_round1_1/`

## 一句话结论
- 这轮把 low-activity
  从
  `60/72`
  扩到
  `36/48/60/72`
  后，
  当前 soft rerank
  推荐仍然是
  `step72`，
  但更重要的新发现是:
  - 当前这组低活动切片
    几乎无法区分
    `36/48/60`
  - 下一步应优先扩样本与指标，
    而不是继续在现有切片上
    微调权重。
