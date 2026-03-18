# 202. Stage5 activity-gate checkpoint governance 与 audio audit kickoff 报告

## 背景
- `docs/201_stage5_activitygate72_continuation_report.md`
  已确认:
  - activity-gate family
    现在是
    Stage5 默认主线
- 但要把它真正交到
  人工听审阶段，
  还缺两件事:
  1. 新 family
     自己的 checkpoint
     治理口径
  2. 一条明确的
     GUI 启动命令
     和脚本入口

## 本轮目标
1. 在 activity-gate72
   family 上
   复用现有 selector，
   先看旧政策
   会给出什么结果
2. 基于实际结果，
   固定本轮听审的
   主对比对象
3. 产出正式命令、
   bundle 路径、
   输出目录和脚本入口

## 本轮执行

### 1. 新 family checkpoint selection

```powershell
.\python.exe manage.py select-offline-mvp-nores-vocoder-checkpoint --summary reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json --output-dir reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_round1_1 --late-step-ratio 0.5 --validation-guard-ratio 1.03 --max-pairwise-worsened-ratio 0.2 --max-rms-ratio-deviation 0.03
```

### 2. 两路 validation bundle

```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio --checkpoint reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step60.pt --split-name validation --target-record-ids target::chapter3_3_firefly_162 target::chapter3_22_firefly_114 target::chapter3_3_firefly_213 target::chapter3_3_firefly_122 target::chapter3_4_firefly_109 target::chapter3_4_firefly_106 --sample-count 6 --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate60_validation_round1_1 --activity-gate-weight 0.2 --use-predicted-activity-gate
```

```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio --checkpoint reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step72.pt --split-name validation --target-record-ids target::chapter3_3_firefly_162 target::chapter3_22_firefly_114 target::chapter3_3_firefly_213 target::chapter3_3_firefly_122 target::chapter3_4_firefly_109 target::chapter3_4_firefly_106 --sample-count 6 --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_validation_round1_1 --activity-gate-weight 0.2 --use-predicted-activity-gate
```

### 3. GUI smoke

```powershell
.\python.exe manage.py launch-audio-audit-gui --bundle reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate60_validation_round1_1 reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_validation_round1_1 --output-dir reports/audio/audio_audit_gui_stage5_activitygate60_vs_72_session --auto-close-ms 1000
```

## 新 family 治理结果

### 1. 旧 selector 政策在新 family 上的直接输出
- best validation checkpoint:
  - `step72`
  - `loss_total = 0.564671`
  - `decoded_to_target_rms_ratio = 0.917435`
- best RMS checkpoint:
  - `step24`
  - `loss_total = 0.832555`
  - `decoded_to_target_rms_ratio = 1.006118`
- selected stable late-stop:
  - `null`

### 2. 为什么 stable late-stop 为空
- 不是因为
  late candidates
  在 pairwise 上塌了
- 实际上:
  - `36 -> 48`
    worsened_ratio
    为 `0.0`
  - `48 -> 60`
    worsened_ratio
    为 `0.0`
  - `60 -> 72`
    worsened_ratio
    也只有
    `0.015152`
- 真正卡住的是:
  - 旧
    `validation_guard_ratio = 1.03`
    对应阈值:
    - `0.581611`
  - `step60 = 0.584654`
    只比它高
    `0.003043`
  - `step72`
    虽在 guard 内，
    但
    `rms_ratio_deviation = 0.082565`
    明显超出
    `0.03`

这说明:
- 旧 selector
  没有“坏掉”
- 而是新 family
  已经进入
  一个更明确的 tradeoff:
  - `72`
    validation 更强
  - `60`
    loudness 更稳

### 3. 为什么本轮不把 `step24` 当成人工听审主对比对象
- 虽然它是
  best RMS
- 但它的 validation
  `loss_total = 0.832555`
  相比
  `step60 / step72`
  明显落后
- 所以它更像:
  - 早期平衡参照
- 不像:
  - 当前值得优先听的
    主线候选

## 本轮 6 条样本 aggregate 复核

### `step60`
- `loss_total = 0.582758`
- `decoded_to_target_rms_ratio = 0.953562`
- `loss_waveform = 0.115824`
- `loss_stft = 0.184672`
- `decoded_env_corr = 0.824315`
- `decoded_env_mae = 0.043030`
- `decoded_dynamic_std_ratio = 0.708293`
- `decoded_silent_rms = 0.015776`
- `audit_env_corr = 0.817808`
- `audit_silent_rms = 0.001772`

### `step72`
- `loss_total = 0.564981`
- `decoded_to_target_rms_ratio = 0.891505`
- `loss_waveform = 0.109393`
- `loss_stft = 0.166021`
- `decoded_env_corr = 0.833605`
- `decoded_env_mae = 0.038425`
- `decoded_dynamic_std_ratio = 0.715086`
- `decoded_silent_rms = 0.007286`
- `audit_env_corr = 0.829826`
- `audit_silent_rms = 0.001612`

## 当前判断

### 1. 本轮最该听的不是 `24 vs 60 vs 72`，而是 `60 vs 72`
- 原因:
  - `24`
    只是 RMS 很贴
  - 但 validation
    太早、太弱
- 当前真正有信息量的矛盾是:
  - `72`
    更强的 validation /
    dynamic / silence
  - 对
    `60`
    的
    loudness 偏移

### 2. 当前更合理的口径
- `step72`
  记为:
  - best validation
- `step60`
  记为:
  - provisional loudness-balanced late candidate
- 暂不把
  `step60`
  直接写死成
  正式 stable late-stop，
  因为那会变成
  私自改 selector 政策

### 3. 当前已经满足人工听审交付契约
- 有固定命令
- 有固定 bundle
- 有固定输出目录
- 有固定主对比问题
- GUI 启动 smoke
  已通过

先说人话:
- 现在真正该听的，
  不是“最早哪个最不走样”，
  而是
  `60`
  和
  `72`
  这两个新主线候选:
  - `72`
    更像成绩最好的
  - `60`
    更像更稳妥的

## 用户应运行的正式命令

```powershell
.\python.exe manage.py launch-audio-audit-gui `
  --bundle reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate60_validation_round1_1 `
           reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_validation_round1_1 `
  --output-dir reports/audio/audio_audit_gui_stage5_activitygate60_vs_72_session
```

## 对应脚本入口

```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_audio_audit_activitygate60_vs_72.ps1
```

- 若只做脚本级 smoke，
  可额外传:
  - `-AutoCloseMs 1000`

## 当前听审输出目录
- `reports/audio/audio_audit_gui_stage5_activitygate60_vs_72_session/`

## 本轮主对比目标

### 1. 主对比
- `activitygate60`
  对
  `activitygate72`
- 要回答的问题:
  - `72`
    虽然 objective 更强，
    但是否开始显得:
    - 整体偏小声
    - 边界偏薄
    - 有过度静音 / 收得过头
  - `60`
    是否在保持更稳 loudness 的同时，
    听感上已经足够接近
    `72`

### 2. 当前试听重点
- 整体响度是否自然
- 该静的时候是否静，
  但有没有静过头
- 句尾和停顿是否收得稳
- 整体起伏是否跟着目标走

## 当前产物
- selector:
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_round1_1/`
- step60 bundle:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate60_validation_round1_1/`
- step72 bundle:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_validation_round1_1/`
- GUI session:
  - `reports/audio/audio_audit_gui_stage5_activitygate60_vs_72_session/`

## 一句话结论
- activity-gate family
  现在已经具备
  正式听审入口，
  而且当前最有信息量的比较对象
  已经收束为:
  - `step72 = best validation`
  - `step60 = provisional loudness-balanced late candidate`
- 旧 selector
  在 `1.03`
  guard 下
  暂时选不出
  formal stable late-stop，
  但这不是坏事，
  反而说明
  新 family
  当前真正值得听的，
  就是这条
  `60 vs 72`
  的 tradeoff。
