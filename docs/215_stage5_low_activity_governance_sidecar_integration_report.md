# 215. Stage5 low-activity governance sidecar 接入 checkpoint selection 报告

## 背景
- `docs/214_stage5_low_activity_subjective_claims_quant_backcheck.md`
  已把
  Stage5 low-activity
  相关主观判断
  回查成较稳定的量化口径:
  - `mean_active_fraction`
  - `mean_activity_alignment_mae`
  - `mean_activity_excess_mean`
  - `fragmentation_score`
- 但在本轮接入前，
  `select-offline-mvp-nores-vocoder-checkpoint`
  仍然只看:
  - validation loss
  - RMS ratio
  - pairwise worsened ratio
- 也就是说，
  low-activity tradeoff
  还停留在专项报告里，
  没有进入
  checkpoint governance
  的正式 payload

## 本轮目标
1. 不修改现有 selector
   的硬选点规则
2. 把
   low-activity
   量化结果
   作为 governance sidecar
   接入 selection payload
3. 让后续任何读取
   selection json / markdown
   的环节，
   都能直接看到:
   - 局部毛刺风险
   - 低活动底音泄漏
   - 与 target 能量轨迹的贴合度

## 本轮代码变更

### 1. 修改文件
- `src/v5vc/nores_vocoder_checkpoint_selection.py`
- `src/v5vc/cli.py`

### 2. 新增 CLI 参数
- `--low-activity-probe`
  - 可选
  - 指向
    `stage5_low_activity_fragmentation_probe.json`
- `--low-activity-audio-source`
  - 默认:
    `decoded`

### 3. selection payload 新增内容
- 顶层新增:
  - `low_activity_probe_analysis`
- 各类 candidate
  新增:
  - `low_activity_metrics`

### 4. 当前 sidecar 暴露的核心量化字段
- `mean_fragmentation_score`
- `mean_active_fraction`
- `mean_activity_alignment_mae`
- `mean_activity_excess_mean`
- `mean_sample_delta_peak`

### 5. 当前 sidecar 还会输出的混淆提示字段
- `target_context_toggle_mean`
- `target_boundary_jump_max`

## 接入策略

### 1. 本轮是 governance sidecar，不是 selector policy rewrite
- 当前只做:
  - 注释
  - 汇总
  - guardrail
- 当前不做:
  - 直接重排 candidate
  - 自动覆盖
    `best_validation_checkpoint`
  - 自动覆盖
    `selected_stable_late_stop`

### 2. 当前 guardrail 文本
- 核心规则是:
  - low-activity fragmentation
    只视为局部风险指标
  - 必须和
    `activity_alignment_mae`
    以及
    `activity_excess_mean`
    一起解释，
    才能讨论
    checkpoint
    是否真的更差

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
  --low-activity-audio-source decoded
```

## 本轮验证

### 1. 语法校验

```powershell
.\python.exe -m py_compile src\v5vc\nores_vocoder_checkpoint_selection.py src\v5vc\cli.py src\v5vc\nores_vocoder_audio_export.py
```

### 2. selection 重跑
- 已通过
- 输出目录:
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_round1_1/`

### 3. selection downstream 兼容性 smoke

```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_round1_1/nores_vocoder_checkpoint_selection.json `
  --selection-target best_validation `
  --split-name validation `
  --sample-count 1 `
  --output-dir tmp/stage5_selection_low_activity_sidecar_smoke `
  --activity-gate-weight 0.2 `
  --use-predicted-activity-gate
```

- 已通过
- 说明:
  - 旧的音频导出下游
    能兼容
    新增 sidecar 字段

## 当前结果

### 1. best validation 仍然是 `step72`
- 旧 selector
  的主选点规则
  没被改写
- 这次只是让 payload
  明确附带:
  - `step72`
    的
    low-activity
    指标

### 2. 当前 governance sidecar 明确写出了 tradeoff
- `best_alignment = step72`
- `best_quietness = step72`
- `best_fragmentation = step60`
- `worst_floor_leakage = step60`

### 3. 这正好对应当前听审与量化回查结论
- `step72`
  更贴
  target
  的低活动能量变化
- `step60`
  低活动底音泄漏更重
- `step72`
  同时存在局部 fragmentation
  风险窗口

## 当前对 checkpoint governance 的影响
1. 从现在起，
   读取 selection payload
   时，
   不再只有:
   - validation
   - RMS
   - pairwise
2. 还会同时看到:
   - low-activity
     quietness / leakage
   - activity alignment
   - fragmentation
3. 但当前阶段，
   这些信息仍是:
   - governance sidecar
   - 解释增强
   不是
   - 自动改判主选点

## 一句话结论
- 本轮已经把
  low-activity
  量化结果
  正式接进
  checkpoint selection payload，
  但保持了策略克制:
  - 先增强治理解释能力，
  - 暂不直接重写 selector。
