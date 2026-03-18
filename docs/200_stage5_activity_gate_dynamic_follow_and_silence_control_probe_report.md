# 200. Stage5 activity-gate dynamic-follow 与 silence-control probe 报告

## 背景
- `docs/199_stage5_partial_human_audit_signal_and_progress_decision_report.md`
  已确认:
  - 当前 Stage5
    真正主 blocker
    不是
    `48 / 72 / 96`
    checkpoint 排名
  - 而是
    raw `decoded.wav`
    三者都没有学会
    像样的动态跟随
    与静音控制
- 因此下一棒不该继续优先做:
  - 更多 checkpoint 听审
- 而应先验证:
  - 能否把
    “该响的时候响、
     该静的时候静”
    作为显式训练 / 重建控制量
    接回 Stage5

## 本轮目标
1. 给 Stage5
   no-res waveform route
   增加:
   - frame activity target
   - predicted activity gate
2. 先做:
   - 单步 smoke
   - `24-step` probe
   - `48-step` deterministic run
3. 判断这条机制
   是否真的缓解:
   - dynamic-follow
   - silence-control

## 本轮代码落地

### 1. `src/v5vc/offline_vocoder_training.py`
- 新增:
  - `compute_frame_activity_target(...)`
- 当前做法:
  - 从
    `aligned_waveform`
    以
    `frame_length=400`
    `hop_length=160`
    估计帧级 activity
  - 用它约束:
    - `periodic_gate`
    - `noise_gate`
    - 以及
      `activity_gate = max(periodic_gate, noise_gate)`
- 同时支持:
  - 在 waveform 重建时
    用预测 activity
    对 frame 做 gate

### 2. `src/v5vc/cli.py`
- 为以下入口新增参数:
  - `--activity-gate-weight`
  - `--use-predicted-activity-gate`
- 覆盖命令:
  - `run-offline-mvp-nores-vocoder-train-step`
  - `run-offline-mvp-nores-vocoder-training-loop`
  - `run-offline-mvp-nores-vocoder-dataset-training-loop`
  - `export-offline-mvp-nores-vocoder-audio`

### 3. `src/v5vc/nores_vocoder_audio_export.py`
- 导出侧现在也能显式记录:
  - `waveform_decode.use_predicted_activity_gate`
  - `waveform_decode.activity_gate_weight_for_metrics`
- 这样后续复盘时
  不会再混淆:
  - 这份 `decoded.wav`
    到底有没有经过
    predicted activity gate

## 本轮实验

### 1. 单步 smoke

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-train-step --train-targets reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/packages/validation/target__chapter3_22_firefly_114/train_targets/offline_mvp_nores_vocoder_train_targets.pt --output-dir reports/runtime/offline_mvp_nores_vocoder_activitygate_train_step_smoke_chapter3_22_firefly_114 --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2 --activity-gate-weight 0.2 --use-predicted-activity-gate
```

- 产物:
  - `reports/runtime/offline_mvp_nores_vocoder_activitygate_train_step_smoke_chapter3_22_firefly_114/`
- 结果:
  - 单步 forward / backward / checkpoint
    全部打通

### 2. `24-step` dataset probe

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate24_probe_round1_1 --device cuda:0 --num-steps 24 --packages-per-step 4 --validation-interval 12 --checkpoint-interval 12 --sampler-mode shuffle --seed 20260318 --deterministic --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2 --activity-gate-weight 0.2 --use-predicted-activity-gate
```

- 产物:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate24_probe_round1_1/`
- 结果:
  - `step24 validation loss_total = 0.832555`

### 3. `48-step` deterministic run

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate48_deterministic_round1_1 --device cuda:0 --num-steps 48 --packages-per-step 4 --validation-interval 12 --checkpoint-interval 12 --sampler-mode shuffle --seed 20260318 --deterministic --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2 --activity-gate-weight 0.2 --use-predicted-activity-gate
```

- 产物:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate48_deterministic_round1_1/`
- 结果:
  - `step48 validation loss_total = 0.627330`

### 4. 前两条已听样本导出复核

```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio --checkpoint reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate24_probe_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt --split-name validation --target-record-ids target::chapter3_22_firefly_114 target::chapter3_3_firefly_122 --sample-count 2 --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate24_probe_front2_round1_1 --activity-gate-weight 0.2 --use-predicted-activity-gate
```

```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio --checkpoint reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate48_deterministic_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step48.pt --split-name validation --target-record-ids target::chapter3_22_firefly_114 target::chapter3_3_firefly_122 --sample-count 2 --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate48_front2_round1_1 --activity-gate-weight 0.2 --use-predicted-activity-gate
```

- 导出目录:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate24_probe_front2_round1_1/`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate48_front2_round1_1/`

## 结果复核

### 1. 训练侧 validation 信号
- 旧 baseline:
  - `baseline48 validation loss_total = 0.655545`
  - `baseline96 validation loss_total = 0.616506`
- 新 activity-gate:
  - `activitygate24 validation loss_total = 0.832555`
  - `activitygate48 validation loss_total = 0.627330`

这说明:
- `24-step`
  还只是 probe
- 但到 `48-step`
  时，
  新路线已经:
  - 明显优于旧 `baseline48`
  - 并且逼近旧 `baseline96`

### 2. 对用户已听过的前两条样本，raw `decoded.wav` 指标出现结构性改善
- 旧三路 aggregate:
  - `step48 decoded_env_corr = 0.051597`
  - `step72 decoded_env_corr = 0.083333`
  - `step96 decoded_env_corr = 0.141451`
  - `step48 decoded_dynamic_std_ratio = 0.095554`
  - `step72 decoded_dynamic_std_ratio = 0.098807`
  - `step96 decoded_dynamic_std_ratio = 0.100353`
  - `step48 decoded_silent_rms = 0.118856`
  - `step72 decoded_silent_rms = 0.118515`
  - `step96 decoded_silent_rms = 0.124973`
- 新 activity-gate aggregate:
  - `activitygate24 decoded_env_corr = 0.817243`
  - `activitygate48 decoded_env_corr = 0.804235`
  - `activitygate24 decoded_dynamic_std_ratio = 0.327715`
  - `activitygate48 decoded_dynamic_std_ratio = 0.640837`
  - `activitygate24 decoded_silent_rms = 0.080265`
  - `activitygate48 decoded_silent_rms = 0.032658`

这说明:
- 当前改善
  不是
  “略好一点”
- 而是:
  - 包络相关性
    从接近失效
    提升到
    明显可跟随
  - 动态起伏比例
    不再接近常数平线
  - 静音泄漏
    显著下降

### 3. `activitygate48` 比 `activitygate24` 更像真正可继续扩展的点
- `activitygate24`
  虽然已经把
  `decoded_env_corr`
  拉起来
  但:
  - `decoded_silent_rms`
    仍约为
    `0.080265`
  - `decoded_dynamic_std_ratio`
    仍只有
    `0.327715`
- `activitygate48`
  进一步把:
  - `decoded_silent_rms`
    压到
    `0.032658`
  - `decoded_dynamic_std_ratio`
    提升到
    `0.640837`

这说明:
- 这条机制
  不是
  “只在 very early probe
   上凑巧有效”
- 到 `48-step`
  已经显示出
  更稳定的收益

### 4. `audit_proxy.wav` 也同步改善，但当前最有价值的信息来自 raw decoded
- `activitygate48 audit_env_corr = 0.792247`
- `activitygate48 audit_env_mae = 0.041745`
- `activitygate48 audit_silent_rms = 0.001145`

对比旧 route:
- 旧三路
  `audit_env_corr`
  约为:
  - `0.721270`
    到
    `0.724423`
- 旧三路
  `audit_silent_rms`
  约为:
  - `0.001485`
    到
    `0.001571`

这说明:
- GUI 默认试听层
  也变得更贴 target
- 但更关键的是:
  - 这次连
    raw `decoded.wav`
    本身
    都被实质性拉正了

## 当前判断

### 1. Stage5 现在已经不只是“知道问题在哪”，而是出现了明确有效的修正抓手
- 之前状态是:
  - 只知道
    dynamic-follow /
    silence-control
    是 blocker
- 现在状态是:
  - `activity gate`
    已经给出
    明确正信号

### 2. 当前更合理的默认下一棒，不是回去继续做旧 checkpoint 排名，而是沿 activity-gate route 继续扩展
- 因为当前最重要的信息
  已经变成:
  - 这条控制机制
    有效
- 所以下一步更值钱的
  不是:
  - 旧 `48 / 72 / 96`
    谁听起来更顺
- 而是:
  - activity-gate route
    是否能在更长 horizon
    保持收益

### 3. 但当前还不能把它写成“最终 Stage5 已解决”
- 原因:
  - 当前 route
    仍是 bootstrap
    waveform / STFT
    目标
  - 且这轮收益
    同时依赖:
    - activity supervision
    - predicted activity gate
      参与 waveform 重建
- 所以更准确的表述应是:
  - 当前已经验证
    这条控制机制
    能显著缓解
    dynamic / silence 问题
  - 但还没有证明
    最终 vocoder 质量
    已经收口

先说人话:
- 这次不是又多跑了一组
  “看看 loss 变没变”
- 而是真的把
  Stage5
  最致命的那个问题
  撬动了:
  - 以前几乎全程都在响
  - 现在已经开始
    跟着目标
    该起就起、
    该落就落

## 当前产物
- 单步 smoke:
  - `reports/runtime/offline_mvp_nores_vocoder_activitygate_train_step_smoke_chapter3_22_firefly_114/`
- `24-step` probe:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate24_probe_round1_1/`
- `48-step` deterministic:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate48_deterministic_round1_1/`
- 前两条样本导出:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate24_probe_front2_round1_1/`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate48_front2_round1_1/`

## 下一步建议
1. 以当前
   `activitygate48`
   作为新的 Stage5
   继续扩展起点，
   优先看:
   - `72-step`
   - 或同量级 deterministic continuation
2. 若继续导出 / 听审，
   必须明确保留:
   - `waveform_decode.use_predicted_activity_gate = true`
   的口径，
   禁止和旧 decode
   设置混看
3. 后续若收益延续，
   再考虑:
   - checkpoint governance
   - 更大样本导出
   - 新一轮人工听审

## 一句话结论
- 当前 Stage5
  已从
  “定位到 dynamic / silence
   是主 blocker”
  推进到
  “activity-gate 机制
   已给出强正信号”:
  - `activitygate48`
    在 validation loss
    上优于旧 `baseline48`
  - 更关键的是，
    它把前两条已听样本上的
    raw `decoded.wav`
    从几乎不会动态跟随、
    静音严重泄漏，
    拉到了明显更可控的状态；
  因此下一棒主线
  应继续沿
  activity-gate route
  扩展，
  而不是回到旧 checkpoint
  排名问题上打转。
