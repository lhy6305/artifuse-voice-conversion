# 201. Stage5 `activitygate72` continuation 报告

## 背景
- `docs/200_stage5_activity_gate_dynamic_follow_and_silence_control_probe_report.md`
  已确认:
  - `activitygate48`
    相比旧 route
    已经给出
    明确正信号
- 但真正关键的问题还没回答完:
  - 这条收益
    是只在 `48-step`
    附近成立
  - 还是继续拉到
    `72-step`
    仍能保住

## 本轮目标
1. 在完全相同口径下，
   继续把
   activity-gate route
   拉到 `72-step`
2. 判断:
   - validation
     是否继续改善
   - 前两条已听样本上的
     dynamic / silence
     是否继续改善
3. 给下一棒决定:
   - 是否继续沿
     activity-gate route
     扩展

## 本轮执行

### 1. `72-step` deterministic continuation

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1 --device cuda:0 --num-steps 72 --packages-per-step 4 --validation-interval 12 --checkpoint-interval 12 --sampler-mode shuffle --seed 20260318 --deterministic --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2 --activity-gate-weight 0.2 --use-predicted-activity-gate
```

- 运行时间:
  - `221.341092 sec`
- 产物:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/`

### 2. 前两条样本导出复核

```powershell
.\python.exe manage.py export-offline-mvp-nores-vocoder-audio --checkpoint reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step72.pt --split-name validation --target-record-ids target::chapter3_22_firefly_114 target::chapter3_3_firefly_122 --sample-count 2 --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_front2_round1_1 --activity-gate-weight 0.2 --use-predicted-activity-gate
```

- 产物:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_front2_round1_1/`

## 结果

### 1. validation 继续明显改善
- `activitygate48 validation loss_total = 0.627330`
- `activitygate60 validation loss_total = 0.584654`
- `activitygate72 validation loss_total = 0.564671`

相比旧 route:
- `baseline96 validation loss_total = 0.616506`

这说明:
- 当前 activity-gate route
  到 `72-step`
  仍在继续前进
- 而且 validation
  已经低于
  旧 `baseline96`

### 2. 前两条样本上的 raw `decoded.wav` 没有回退，反而继续改善
- `activitygate48` aggregate:
  - `decoded_env_corr = 0.804235`
  - `decoded_env_mae = 0.053422`
  - `decoded_dynamic_std_ratio = 0.640837`
  - `decoded_silent_rms = 0.032658`
- `activitygate72` aggregate:
  - `decoded_env_corr = 0.805906`
  - `decoded_env_mae = 0.041770`
  - `decoded_dynamic_std_ratio = 0.697361`
  - `decoded_silent_rms = 0.007221`

这说明:
- 到 `72-step`
  时，
  raw decoded
  并没有重新回到
  “全程漏声”
- 相反:
  - 静音泄漏
    进一步大幅下降
  - 包络误差
    进一步下降
  - 动态起伏比例
    继续上升

### 3. `audit_proxy.wav` 也继续保持改善
- `activitygate48 audit_env_corr = 0.792247`
- `activitygate72 audit_env_corr = 0.803721`
- `activitygate48 audit_silent_rms = 0.001145`
- `activitygate72 audit_silent_rms = 0.000896`

这说明:
- 不只是技术排查用的
  raw decoded
  在改善
- 用户实际听到的
  audit proxy
  也同步更贴 target

### 4. 需要额外注意的点
- `activitygate72`
  validation aggregate
  的
  `decoded_to_target_rms_ratio`
  为:
  - `0.917435`
- 这说明:
  - 当前 route
    虽然 dynamic /
    silence 改善很强
  - 但全量平均 loudness
    仍需要继续盯

不过对前两条已听样本:
- `chapter3_22_firefly_114`
  ratio:
  - `0.751890`
- `chapter3_3_firefly_122`
  ratio:
  - `0.994638`

所以当前更准确的理解是:
- loudness 还没有完全收口
- 但这已经不是
  “动态和静音全都失控”
  的旧问题形态

## 当前判断

### 1. activity-gate route 已经从“有希望”升级为“当前 Stage5 默认主线候选”
- 证据不是单一指标，
  而是同时出现:
  - validation 持续下降
  - raw decoded
    dynamic / silence
    持续改善
  - audit proxy
    也同步变好

### 2. 当前最值得继续追的，不再是旧 baseline family，而是 activity-gate family 自己的 checkpoint governance
- 现在更合理的问题变成:
  - `48 / 60 / 72`
    在新 family 里
    怎么治理
- 而不是:
  - 还要不要回去
    继续讨论
    旧 `step72 / step96`

### 3. 下一棒应开始回到“更大样本 + 新 family 听审”
- 因为当前 front2
  证据已经足够强，
  不再只是
  局部偶然改善
- 更合适的下一步是:
  - 导出更大 validation 样本
  - 进入新一轮人工听审
  - 并开始建立
    新 family
    的 checkpoint selection

先说人话:
- 这条 activity-gate 线
  没有在 `48-step`
  后塌掉，
  反而继续往前走了。
- 现在可以把它当成
  真主线来看，
  而不是一条
  试试看能不能救火的 side probe。

## 当前产物
- `72-step` run:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/`
- 前两条样本导出:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_front2_round1_1/`

## 下一步建议
1. 以
   `activitygate72`
   为当前默认 continuation 点，
   开始准备:
   - 更大样本导出
   - 新一轮人工听审
2. 在新 family 内
   补 checkpoint 治理:
   - best validation
   - best loudness / RMS
   - stable late-stop
3. 后续如果继续拉更长 horizon，
   必须继续同时看:
   - dynamic-follow
   - silence-control
   - loudness ratio

## 一句话结论
- `activitygate72`
  证明这条新机制
  不是短程假象:
  - validation 已降到
    `0.564671`
  - raw `decoded.wav`
    在前两条已听样本上的
    dynamic / silence
    继续明显改善
  - audit proxy
    也同步更贴 target
- 因此当前 Stage5
  默认主线
  应正式切到
  activity-gate family，
  下一棒开始准备
  新 family
  的更大样本导出、
  听审和 checkpoint 治理。
