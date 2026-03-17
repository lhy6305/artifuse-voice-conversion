# 178. no-residual vocoder 最小训练合同与单步 smoke 报告

## 背景
- `docs/177_nores_vocoder_scaffold_bootstrap_report.md`
  已把:
  - teacher-first contract
  - consumer-side branch scaffold
  - no-residual vocoder scaffold
  固定成了正式代码锚点
- 但如果后续还停在:
  - 只有 scaffold
  - 没有训练目标
  - 没有反向传播 smoke
  那 Stage5
  仍然会卡在
  “能前向，不能训练”

## 本轮目标
1. 为 no-residual vocoder scaffold
   新增最小训练目标构建能力
2. 用真实音频与真实 teacher runtime 语义
   生成对齐后的 spectral/gate targets
3. 再跑一个正式单步训练 smoke，
   确认:
   - loss
   - backward
   - grad clipping
   - optimizer step
   - checkpoint 落盘
   都已成立

## 本轮代码落地

### 1. 新增训练目标构建模块
- 新增:
  - `src/v5vc/offline_vocoder_training.py`
- CLI:
  - `build-offline-mvp-nores-vocoder-train-targets`

当前能力:
- 从
  `teacher_vocoder_input_scaffold.pt`
  读取:
  - periodic branch features
  - noise branch features
  - source runtime metadata
- 从真实目标音频构建:
  - `harmonic_envelope_target`
  - `noise_envelope_target`
  - `periodic_gate_target`
  - `noise_gate_target`
- 训练包同时保留:
  - 对齐后的 waveform
  - runtime 元数据
  - 当前 target 的解释边界

### 2. 新增单步训练 smoke 入口
- CLI:
  - `run-offline-mvp-nores-vocoder-train-step`

当前能力:
- 读取
  `offline_mvp_nores_vocoder_train_targets.pt`
- 实例化
  `NoResidualSourceFilterVocoderScaffold`
- 计算:
  - harmonic envelope L1
  - noise envelope L1
  - periodic gate BCE
  - noise gate BCE
- 执行:
  - backward
  - grad clipping
  - Adam step
  - checkpoint / summary 落盘

### 3. 为训练目标对齐补齐上游元数据
- 更新:
  - `src/v5vc/offline_teacher_downstream_contract.py`
  - `src/v5vc/offline_teacher_vocoder_input_scaffold.py`

新增保留:
- `input_audio_path`
- `source_audio_path`
- `source_runtime.sample_rate`
- `source_runtime.frame_length`
- `source_runtime.hop_length`

原因:
- 没有这些字段，
  train-target builder
  无法确认:
  - teacher frame 语义
  - STFT 对齐长度
  - 旧 scaffold 是否需要显式 override

## smoke test

### 步骤 1. 重导带 runtime 元数据的 contract

```powershell
.\python.exe manage.py export-offline-mvp-teacher-downstream-contract --input-audio data_prep/round1_1/firefly_mainstream/audio/chapter3_3_firefly_162.wav --output-dir reports/runtime/offline_mvp_teacher_downstream_contract_smoke_v2_chapter3_3_firefly_162 --chunk-samples 2048 --device cpu
```

### 步骤 2. 重建 consumer-side scaffold

```powershell
.\python.exe manage.py build-offline-mvp-teacher-vocoder-input-scaffold --contract reports/runtime/offline_mvp_teacher_downstream_contract_smoke_v2_chapter3_3_firefly_162/teacher_downstream_control_contract.pt --output-dir reports/runtime/offline_mvp_teacher_vocoder_input_scaffold_smoke_v2_chapter3_3_firefly_162
```

### 步骤 3. 构建最小 train-target package

```powershell
.\python.exe manage.py build-offline-mvp-nores-vocoder-train-targets --input-scaffold reports/runtime/offline_mvp_teacher_vocoder_input_scaffold_smoke_v2_chapter3_3_firefly_162/teacher_vocoder_input_scaffold.pt --target-audio data_prep/round1_1/firefly_mainstream/audio/chapter3_3_firefly_162.wav --output-dir reports/runtime/offline_mvp_nores_vocoder_train_targets_smoke_chapter3_3_firefly_162
```

结果:
- `frame_count = 167`
- `periodic_input_dim = 35`
- `noise_input_dim = 29`
- `harmonic_target_dim = 32`
- `noise_target_dim = 32`
- STFT:
  - `stft_freq_bins = 201`
  - `harmonic_source_bins = 100`
  - `noise_source_bins = 101`

### 步骤 4. 跑单步训练 smoke

```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-train-step --train-targets reports/runtime/offline_mvp_nores_vocoder_train_targets_smoke_chapter3_3_firefly_162/offline_mvp_nores_vocoder_train_targets.pt --output-dir reports/runtime/offline_mvp_nores_vocoder_train_step_smoke_chapter3_3_firefly_162
```

结果:
- `duration_sec = 1.367454`
- `frame_count = 167`
- `grad_norm = 1.715228`
- `loss_total = 1.009354`
- `loss_harmonic_envelope = 0.449511`
- `loss_noise_envelope = 0.294842`
- `loss_periodic_gate = 0.659462`
- `loss_noise_gate = 0.665541`

## 当前判断

### 1. Stage5 最小训练 plumbing 已成立
- 现在已经不只是
  “前向 shape 没问题”
- 还已经验证:
  - target package 可构建
  - loss 可计算
  - backward 可执行
  - optimizer step 可执行
  - checkpoint 可落盘

### 2. 这仍不是 final vocoder training recipe
- 当前 target
  仍是:
  - proxy spectral envelopes
  - proxy gate targets
- 还不是:
  - waveform decoder
  - STFT multi-resolution reconstruction
  - adversarial / feature matching
  - 最终音频导出链

### 3. 当前真实停点已从“只有 scaffold”推进到“最小训练合同已成立”
- 所以下一次恢复上下文时，
  不应再把 Stage5
  误判回:
  - 只完成 `177`
  - 只有前向 dry-run

## 当前边界
- 当前还没有:
  - 多 step 训练 loop
  - validation loop
  - decoder / upsampling
  - waveform reconstruction target
  - GAN losses
- 所以现在只能写成:
  - no-residual vocoder minimal training contract established
- 不能写成:
  - Stage5 vocoder training completed

## 下一步
1. 在当前 train-target package
   之上补:
   - 多 step 训练 loop
   - checkpoint series
   - 基础 validation
2. 明确下一阶段主要训练目标:
   - 继续沿 spectral/gate proxy
     做稳定性验证
   - 还是转向更接近 waveform 的 decoder 目标
3. 在显式 `f0_hz / r_res`
   仍缺失前，
   继续把这条线
   保持为:
   - no-residual baseline route

## 一句话结论
- 本轮已经把 Stage5
  从“只有 no-residual scaffold”
  推进到“最小训练合同 + 单步训练 smoke 已成立”；
  当前下一步应进入
  多步训练与 decoder 目标收口，
  而不是再回头重复确认
  scaffold 是否存在。
