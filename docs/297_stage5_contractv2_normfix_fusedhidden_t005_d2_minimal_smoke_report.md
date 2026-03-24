# 2026-03-24 Stage5 `contractv2_normfix` `fused_hidden_template=0.05 + fused_hidden_delta=2.0` 最小 smoke 报告

## 结论
- 已在当前 `contractv2_normfix`
  recipe 上完成一轮
  `fused_hidden`
  级别 objective
  最小 smoke：
  - 有效训练目录：
    `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_fusedhidden_t005_d2_smoke_round1_3/`
- 当前结果是：
  - `fused_hidden_template`
    指标有轻微下降
  - 但
    `waveform / stft / rms / active_template / frame_delta`
    与 baseline
    几乎完全重合
- 因而当前判断是：
  - 这组
    `0.05 / 2.0`
    的 `fused_hidden`
    objective
    **只带来了极弱改动**
  - 没有证据表明系统已离开
    buzz-only
    失败区

## 一、背景
- `docs/296`
  已确认：
  - 主要坍缩更早发生在
    `fusion -> fused_hidden`
  - 不支持把问题单独归到
    `waveform_decoder`
- 因此本轮最小实验的目标是：
  - 不改 decoder
  - 不改 data
  - 只在当前 recipe 上
    增加两项
    `fused_hidden`
    级反坍缩 loss

## 二、实现改动
- 已在训练损失里加入：
  - `loss_fused_hidden_template_excess_vs_branch`
    - 惩罚
      `fused_hidden`
      相比 branch hidden
      更模板化
  - `loss_fused_hidden_delta_floor_halfmax`
    - 惩罚
      `fused_hidden`
      相邻帧变化幅度
      低于 branch hidden
      地板
- dataset loop
  新增参数：
  - `--fused-hidden-template-weight`
  - `--fused-hidden-delta-weight`

## 三、运行配置
- dataset index：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- smoke 配置：
  - `num_steps = 4`
  - `packages_per_step = 4`
  - `validation_interval = 2`
  - `checkpoint_interval = 2`
  - `device = cuda`
  - `seed = 20260324`
  - `deterministic = true`
  - `activity_gate_weight = 0.2`
  - `waveform_weight = 0.5`
  - `stft_weight = 0.5`
  - `rms_guard_weight = 0.2`
  - `active_template_weight = 0.0`
  - `frame_delta_weight = 0.0`
  - `fused_hidden_template_weight = 0.05`
  - `fused_hidden_delta_weight = 2.0`
  - `use_predicted_activity_gate = true`
  - `reconstruction_frame_gain_apply_mode = pre_overlap_add`

## 四、重要执行说明
- 早期目录：
  - `..._smoke_round1_1/`
  - `..._smoke_round1_2/`
  **不应作为正式结果引用**
- 原因是：
  - 首次接线时，
    dataset loop
    CLI
    没把新增
    `fused_hidden`
    权重正确透传到训练函数
- 这个问题已修复，
  并通过
  `summary['training']['loss_weights']`
  确认：
  - `fused_hidden_template = 0.05`
  - `fused_hidden_delta = 2.0`
- 因此本报告只以：
  - `..._smoke_round1_3/`
  为有效结果

## 五、validation 结果

### baseline 参考
- 使用：
  - `docs/294`
    中的
    `contractv2_normfix_baseline_smoke_round1_2`

### candidate step4 validation
- `loss_total = 1.229590`
- `loss_waveform = 0.125093`
- `loss_stft = 0.601784`
- `loss_rms_guard = 0.155716`
- `loss_active_template = 0.502417`
- `loss_frame_delta = 0.936755`
- `loss_fused_hidden_template_excess_vs_branch = 0.007477`
- `loss_fused_hidden_delta_floor_halfmax = 0.000003`
- `decoded_to_target_rms_ratio = 0.899355`

### 与 baseline step4 对比
- baseline：
  - `loss_waveform = 0.125092`
  - `loss_stft = 0.601828`
  - `loss_rms_guard = 0.155673`
  - `loss_active_template = 0.503176`
  - `loss_frame_delta = 0.936750`
  - `loss_fused_hidden_template_excess_vs_branch = 0.008236`
  - `loss_fused_hidden_delta_floor_halfmax = 0.000004`
  - `decoded_to_target_rms_ratio = 0.899397`
- 当前解释：
  - `fused_hidden_template`
    从
    `0.008236`
    降到
    `0.007477`
    约
    `-9.2%`
  - 但其余共享指标
    改变量都非常小
  - `frame_delta`
    依然几乎完全不动

## 六、fixed 6 条试听记录 aggregate

### baseline
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_baseline_smoke_fusedhidden_metric_probe_round1_1/`
- aggregate：
  - `loss_waveform = 0.125503`
  - `loss_stft = 0.602313`
  - `loss_rms_guard = 0.107393`
  - `loss_active_template = 0.497106`
  - `loss_frame_delta = 0.898517`
  - `loss_fused_hidden_template_excess_vs_branch = 0.010317`
  - `loss_fused_hidden_delta_floor_halfmax = 0.000002`
  - `decoded_to_target_rms_ratio = 0.908930`

### candidate
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_fusedhidden_t005_d2_smoke_round1_3/`
- aggregate：
  - `loss_waveform = 0.125502`
  - `loss_stft = 0.602252`
  - `loss_rms_guard = 0.107445`
  - `loss_active_template = 0.496285`
  - `loss_frame_delta = 0.898523`
  - `loss_fused_hidden_template_excess_vs_branch = 0.009490`
  - `loss_fused_hidden_delta_floor_halfmax = 0.000002`
  - `decoded_to_target_rms_ratio = 0.908874`

### aggregate 解释
- `fused_hidden_template`
  从
  `0.010317`
  降到
  `0.009490`
  约
  `-8.0%`
- `loss_stft`
  有极轻微改善
- 但：
  - `loss_waveform`
    基本不变
  - `loss_rms_guard`
    轻微变差
  - `loss_frame_delta`
    仍基本不变
  - `decoded_to_target_rms_ratio`
    也几乎不变

## 七、当前阶段判断
1. `docs/296`
   给出的方向判断仍成立：
   - 主问题更早发生在
     `fusion / fused_hidden`
2. 但当前这组
   `fused_hidden_template=0.05`
   `fused_hidden_delta=2.0`
   的最小 smoke
   只产生了：
   - 很弱的
     `fused_hidden_template`
     改善
3. 它没有带来：
   - 可见的
     waveform-side
     改善
   - 也没有让
     `frame_delta`
     真正启动
4. 所以当前不能写成：
   - 已找到有效
     `fusion`
     objective
5. 更准确的写法是：
   - 当前权重和当前 loss
     形式
     对实际 route
     扰动太弱

## 八、建议下一步
1. 不建议直接把这组
   `0.05 / 2.0`
   权重放大成长训
2. 下一步更合理的是：
   - 重新设计
     `fused_hidden`
     objective
     形态，
     而不是只调这两个数
3. 更值得优先考虑的方向：
   - 更强的
     branch-to-fusion
     diversity preservation
   - 或把约束直接落到
     `fusion`
     前后的表征映射关系
   - 而不是只用当前这种
     轻量 penalty
     硬推

## 一句话结论
- `fused_hidden`
  级 objective
  是正确问题层级，
  但当前这组
  `template=0.05 + delta=2.0`
  的轻量实现
  几乎没有真正推动系统脱离
  baseline buzz 解；
  下一步应优先加强
  objective 形态，
  而不是继续沿这组小权重做长训。
