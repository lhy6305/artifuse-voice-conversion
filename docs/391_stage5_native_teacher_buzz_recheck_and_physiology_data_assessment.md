# 391. Stage5 native teacher buzz 复核与生理传感器数据评估

## 修正说明（2026-03-26）
- 本报告依赖的 native teacher validation3 export 写于旧版 `export-offline-mvp-nores-vocoder-audio` 语义下。
- 该命令现已修正：
  - export decode 默认值
  - training metric 继承逻辑
  - `loss_metrics` 与实际 `decoded.wav` 的语义标注
- 因此本报告当前应视为：
  - `高优先级、但待回补确认`
- 在按修正后 export 语义重跑前，以下结论不能再当作最终口径：
  - `3/3 auto_reject_obvious_buzz`
  - 相关 `centroid / high-band / frame-template` 数值
- 当前正式修正依据见：
  - `docs/393_stage5_export_semantics_correction_scope_and_rerun_requirements.md`
  - `docs/394_stage5_export_semantics_rerun_confirmation_report.md`
- 当前状态更新：
  - `391` 已按修正后的 export 语义完成最小回补重跑
  - 主结论成立，恢复为当前可直接引用结论

## 结论
- `teacher-student` 蒸馏路线现阶段应暂停。
- 当前 `Stage5 native teacher -> decoded.wav` 路线本身已经可被更硬地判为失败，不是只有 student packet 才会出 buzz。
- 我用当前 best native Stage5 checkpoint 做了新的 `3-sample validation` 真实导出，结果 `3/3` 都被机器门禁判为 `auto_reject_obvious_buzz`。
- 因此，当前最值得修的是：
  - 现有 `Stage5` 承接层 / waveform decode / template-collapse 假解问题
  - 不是继续做蒸馏
  - 也不是现在就引入真实发音的生理传感器数据
- 对“是否需要真实发音的生理传感器数据”的当前正式判断是：
  - `不需要`
  - 原因不是它永远没价值，而是当前主故障还停留在更低层、更明确的合同与解码病灶上；在 native teacher 路线自己都还明显 buzz 时，引入新模态只会扩大变量数，不会优先解决主问题

## 一、本轮复核动作

### 1. 使用当前 native teacher 正式 checkpoint 做最小真实导出
- 解释器：
  - `F:/proj_dev/tmp/workdir4/python.exe`
- 命令：
  - `python -m v5vc.cli export-offline-mvp-nores-vocoder-audio --output-dir reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_validation3_recheck_round1_1 --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_contractv2_normfix_round1_1/nores_vocoder_checkpoint_selection.json --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json --selection-target best_validation --split-name validation --sample-count 3`
- 产物：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_validation3_recheck_round1_1/nores_vocoder_audio_export.json`

### 2. 真实 decoded 路径
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_validation3_recheck_round1_1/target__chapter3_3_firefly_162__decoded.wav`
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_validation3_recheck_round1_1/target__chapter3_3_firefly_138__decoded.wav`
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_validation3_recheck_round1_1/target__chapter3_4_firefly_106__decoded.wav`

## 二、复核结果

### 1. 当前 native teacher route 不是局部失败，而是 `3/3` 全部 obvious buzz
- `buzz_reject_summary`：
  - `record_count = 3`
  - `auto_reject_count = 3`
  - `review_required_count = 0`
  - `all_records_auto_reject = true`
- 被拒记录：
  - `target::chapter3_3_firefly_162`
  - `target::chapter3_3_firefly_138`
  - `target::chapter3_4_firefly_106`

### 2. 失败形态高度一致
- 三条样本都呈现：
  - `decoded short-time frames remain highly template-collapsed relative to aligned target diversity`
  - `decoded frame RMS mainly follows aligned target envelope while short-time structure stays collapsed`
- 典型指标范围：
  - `decoded_frame_template_cosine_mean ~= 0.991 ~ 0.997`
  - `decoded_frame_adjacent_cosine_mean ~= 0.992 ~ 1.000`
  - `spectral_centroid_gap_hz ~= 4956 ~ 5113`
  - `spectral_high_band_energy_ratio_gap ~= 0.286 ~ 0.338`

## 三、这对路线判断意味着什么

### 1. 现在不能再把 buzz 主要归咎给 student packet
- 之前已经确认：
  - student route 会进一步拉差
- 但本轮证明：
  - native teacher route 自己就已经 `3/3 obvious buzz`
- 所以当前最高优先级故障是：
  - `Stage5 native teacher` 承接层本身
  - 不是 `student -> Stage5 adapter` 这层的次级偏差

### 2. 现有旧证据与本轮复核是一致的
- `stage5_waveform_decoder_structure_probe_contractv2_normfix_round1_1`
  已说明：
  - collapse 不只是局部小头的问题
  - waveform decoder 在当前工作区间接近 fixed-template projector
- `stage5_waveform_objective_collapse_probe_contractv2_normfix_round1_1`
  已说明：
  - 当前 waveform objective 对 template-collapse 假解约束不足
- 本轮 `3-sample native decoded` 只是把这个结论从 probe/support 层进一步拉到了真实听审入口层

## 四、是否需要真实发音的生理传感器数据

### 当前判断：不需要
- 原因 1：
  - native teacher 现有控制链自己就还没有脱离 obvious buzz
- 原因 2：
  - 当前已确认的主病灶是：
    - `Stage5` 现有承接层 / waveform decode / template-collapse 假解
  - 这不是“缺 articulatory ground truth”才能优先解释的问题
- 原因 3：
  - 引入生理传感器数据会新增：
    - 新采集成本
    - 新对齐问题
    - 新合同设计
    - 新建模变量
  - 但并不会优先修复当前已经明示的 native buzz 故障

### 以后什么情况下才值得重新讨论
- 至少应先满足：
  - 现有 acoustic / event / control 链已经能稳定产出非 buzz、具有人声结构的 decoded
  - 主要瓶颈明确转成“现有可观察控制不够表达发音器官状态”
- 在此之前：
  - 生理传感器数据不是当前主线

## 五、下一步
- 暂停：
  - `teacher-student` 蒸馏推进
- 不做：
  - 生理传感器数据引入
- 主线切换为：
  - `Stage5 native teacher buzz` 修复
- 更具体地说：
  - 先围绕当前 native teacher route 的
    - waveform decoder structure
    - template-collapse 假解
    - 现有 objective / decode semantics
    做最小修复候选
  - 不再把“先补更多上游模态”当作默认下一步
