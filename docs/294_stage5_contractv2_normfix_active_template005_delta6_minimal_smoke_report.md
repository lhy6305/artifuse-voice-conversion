# 2026-03-24 Stage5 `contractv2_normfix` `active_template=0.05 + frame_delta=6.0` 最小 smoke 报告

## 结论
- 本轮已按当前接班计划，
  在
  `contractv2_normfix`
  dataset index
  上完成一组
  **严格可比的双臂最小 smoke**：
  - baseline
  - `active_template = 0.05`
    `frame_delta = 6.0`
- 当前结果方向很清楚：
  1. candidate 臂
     确实把
     `active_template`
     明显压低了；
  2. 但
     `frame_delta`
     基本没动；
  3. `waveform / stft`
     只出现了轻微改善，
     还不能直接写成
     “已摆脱 buzz”。
- 因此这轮 smoke
  更准确的定位应是：
  - **objective-side 方向验证通过**
  - 但还没有到
    **可听转正**
    的结论级别。

## 一、本轮执行目标
- 上轮
  `docs/293`
  已确认：
  - `contractv2_normfix`
    虽然 validation
    数值回升，
    但现有 waveform objective
    仍允许
    `template-buzz + envelope-following`
    假解。
- 因此本轮不再回头修：
  - source
  - target reference
  - inference-only
    小 tweak
- 而是直接做：
  - objective-only
    minimal smoke

## 二、实验设置

### 共同设置
- dataset index：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- `num_steps = 4`
- `packages_per_step = 4`
- `validation_interval = 2`
- `checkpoint_interval = 2`
- `sampler_mode = shuffle`
- `seed = 20260324`
- `deterministic = true`
- `device = cuda:0`
- `activity_gate = 0.2`
- `waveform = 0.5`
- `stft = 0.5`
- `rms_guard = 0.2`
- `use_predicted_activity_gate = true`
- `reconstruction_frame_gain_apply_mode = pre_overlap_add`

### baseline 臂
- `active_template = 0.0`
- `frame_delta = 0.0`
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_baseline_smoke_round1_2/`

### candidate 臂
- `active_template = 0.05`
- `frame_delta = 6.0`
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_active_template005_delta6_smoke_round1_1/`

## 三、训练结果

### baseline 臂
- `step4 validation`
  - `loss_total = 1.229178`
  - `loss_waveform = 0.125092`
  - `loss_stft = 0.601828`
  - `loss_rms_guard = 0.155673`
  - `loss_active_frame_template_excess_relu_0p02 = 0.503176`
  - `loss_frame_delta_unit_rms_l1 = 0.936750`
  - `decoded_to_target_rms_ratio = 0.899397`
- selection：
  - `best_validation = step4`
  - `best_rms = step4`
  - `stable_late_stop = null`

### candidate 臂
- `step4 validation`
  - `loss_total = 6.866590`
  - `loss_waveform = 0.123751`
  - `loss_stft = 0.594695`
  - `loss_rms_guard = 0.164449`
  - `loss_active_frame_template_excess_relu_0p02 = 0.391574`
  - `loss_frame_delta_unit_rms_l1 = 0.936771`
  - `decoded_to_target_rms_ratio = 0.887167`
- selection：
  - `best_validation = step4`
  - `best_rms = step2`
  - `stable_late_stop = null`

### 当前直接比较
- candidate
  相比 baseline：
  - `active_template`
    明显下降
    `0.503176 -> 0.391574`
  - `frame_delta`
    基本不变
    `0.936750 -> 0.936771`
  - `waveform`
    轻微改善
    `0.125092 -> 0.123751`
  - `stft`
    轻微改善
    `0.601828 -> 0.594695`
  - `rms_guard`
    略差
    `0.155673 -> 0.164449`

## 四、固定 6 条试听记录导出

### 固定记录集
- `target::chapter3_2_firefly_212`
- `target::chapter3_2_firefly_155`
- `target::chapter3_3_firefly_162`
- `target::chapter3_17_firefly_133`
- `target::chapter3_3_firefly_245`
- `target::chapter3_2_firefly_163`

### 导出设置
- listening source：
  - `decoded_pitch_matched`
- pitch-match reference：
  - `aligned_target`
- predicted gate：
  - on
- apply mode：
  - `pre_overlap_add`

### baseline 导出目录
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_baseline_smoke_round1_2/`

### candidate 导出目录
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_active_template005_delta6_smoke_round1_1/`

## 五、6 条固定记录上的 aggregate 结果

### baseline
- `loss_total = 1.082355`
- `loss_waveform = 0.125503`
- `loss_stft = 0.602313`
- `loss_rms_guard = 0.107392`
- `loss_active_template_excess = 0.497106`
- `loss_frame_delta = 0.898516`
- `decoded_to_target_rms_ratio = 0.908930`

### candidate
- `loss_total = 6.490942`
- `loss_waveform = 0.124262`
- `loss_stft = 0.596525`
- `loss_rms_guard = 0.115186`
- `loss_active_template_excess = 0.379029`
- `loss_frame_delta = 0.898558`
- `decoded_to_target_rms_ratio = 0.897440`

### 当前解释
- 在固定 6 条记录上，
  candidate 延续了与 validation
  同方向的结果：
  - `active_template`
    显著下降
  - `waveform / stft`
    轻微改善
  - `frame_delta`
    仍几乎不变

## 六、逐条记录对比
- `target::chapter3_2_firefly_212`
  - `active_template`
    `0.488851 -> 0.371047`
  - `frame_delta`
    `0.740099 -> 0.740299`
  - `waveform`
    `0.122589 -> 0.121354`
- `target::chapter3_2_firefly_155`
  - `active_template`
    `0.483469 -> 0.364303`
  - `frame_delta`
    `0.929081 -> 0.929111`
  - `waveform`
    `0.130556 -> 0.129560`
- `target::chapter3_3_firefly_162`
  - `active_template`
    `0.516816 -> 0.393255`
  - `frame_delta`
    `0.977846 -> 0.977872`
  - `waveform`
    `0.140446 -> 0.139456`
- `target::chapter3_17_firefly_133`
  - `active_template`
    `0.519614 -> 0.404406`
  - `frame_delta`
    `1.055355 -> 1.055334`
  - `waveform`
    `0.128467 -> 0.127109`
- `target::chapter3_3_firefly_245`
  - `active_template`
    `0.490717 -> 0.376469`
  - `frame_delta`
    `0.726994 -> 0.726985`
  - `waveform`
    `0.112677 -> 0.111171`
- `target::chapter3_2_firefly_163`
  - `active_template`
    `0.483170 -> 0.364695`
  - `frame_delta`
    `0.961724 -> 0.961750`
  - `waveform`
    `0.118282 -> 0.116923`

## 七、当前判断
1. 这轮最小 smoke
   已经支持：
   - `docs/293`
     里
     `active_template + frame_delta`
     是合理主线
     这个判断
2. 但这轮真实落到训练后，
   当前最先被改写的，
   仍主要是：
   - `active_template`
3. `frame_delta`
   目前几乎没被带动，
   说明：
   - 当前耦合方式
     虽然方向对，
     但还没把
     transition-side
     修正真正打进去
4. 因为新 objective
   额外加了
   `0.05 * active_template + 6.0 * frame_delta`，
   当前不能拿
   candidate 的
   `loss_total`
   与 baseline
   做横向好坏判断；
   当前应主要看：
   - 共享子项
     `waveform / stft / rms_guard`
   - 以及
     `active_template / frame_delta`
     是否按预期变化

## 八、下一步
1. 先对照听：
   - baseline export
   - candidate export
   的这 6 条固定记录
2. 若听感仍主要是 buzz，
   下一步不建议直接放大步数，
   而应先决定：
   - 是否继续保持
     `active_template = 0.05`
   - 再单独改
     `frame_delta`
     的进入方式
     或权重调度
3. 当前仍不建议马上同时改：
   - contract
   - decoder head
   - GAN
   - 更大 waveform objective
   重构

## 一句话结论
- 这轮
  `contractv2_normfix`
  objective smoke
  已经正式说明：
  - `active_template(0.05) + frame_delta(6.0)`
    能稳定把模型往
    anti-template
    方向推
  - 但当前真正被改动的，
    主要还是
    `active_template`
    这一轴；
  - `frame_delta`
    还没有在训练结果里
    展现出实质性接管。
