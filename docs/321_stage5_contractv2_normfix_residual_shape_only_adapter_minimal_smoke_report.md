# 321. Stage5 `contractv2_normfix` residual-shape-only branch-conditioned adapter 最小 smoke 报告

## 一、目的
1. 承接
   `docs/319_stage5_contractv2_normfix_branch_conditioned_decoder_adapter_minimal_smoke_report.md`
   与
   `docs/320_stage5_contractv2_normfix_residual_shape_only_plumbing_and_checkpoint_shape_inference_report.md`
   的下一步，
   在当前最强骨架上做第一发：
   - `residual-shape-only branch-conditioned adapter`
2. 本轮要回答的问题是：
   - 把 adapter
     从“改整个 branch hidden”
     收窄到：
     - 只改 residual-shape / residual-envelope
     之后，
     能不能保住：
     - `active_template`
     - `adjacent cosine`
     - `rms_ratio`
     这些结构收益，
     同时继续拿到一点
     `waveform / stft`
     改善

## 二、实验配置

### 输出目录
- training:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_residualshapecond_smoke_round1_1/`
- fixed-6 export:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_periodicgate_rmsfloor065_residualshapecond_fixed6_round1_1/`

### 固定主线
- `periodic_plus_noise_residual_shape_recurrent`
- `periodic_waveform_frame_delta = 0.25`
- `periodic_waveform_frame_adjacent_cosine = 0.01`
- `periodic_waveform_frame_rms_floor = 0.65`
- `waveform = 0.5`
- `stft = 0.5`
- `rms_guard = 0.2`
- `use_predicted_activity_gate = true`
- `reconstruction_frame_gain_apply_mode = pre_overlap_add`

### 本轮唯一变量
- `use_residual_shape_branch_condition_adapter = true`

### 运行命令
```powershell
.\python.exe manage.py run-offline-mvp-nores-vocoder-dataset-training-loop --dataset-index reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_residualshapecond_smoke_round1_1 --device cuda:0 --num-steps 4 --packages-per-step 4 --validation-interval 2 --checkpoint-interval 2 --sampler-mode shuffle --seed 20260324 --deterministic --waveform-weight 0.5 --stft-weight 0.5 --rms-guard-weight 0.2 --activity-gate-weight 0.2 --use-predicted-activity-gate --reconstruction-frame-gain-apply-mode pre_overlap_add --waveform-decoder-mode periodic_plus_noise_residual_shape_recurrent --periodic-waveform-frame-delta-weight 0.25 --periodic-waveform-frame-adjacent-cosine-weight 0.01 --periodic-waveform-frame-rms-floor-weight 0.65 --use-residual-shape-branch-condition-adapter
```

## 三、step4 validation 对比

### baseline: `rms_floor=0.65`
- `loss_waveform = 0.120592`
- `loss_stft = 0.591259`
- `loss_rms_guard = 0.188080`
- `loss_active_template = 0.169904`
- `loss_frame_adjacent_cosine = 328.754300`
- `decoded_to_target_rms_ratio = 0.863991`

### `branchcondadapter_conservative`
- `loss_waveform = 0.119979`
- `loss_stft = 0.550005`
- `loss_rms_guard = 0.193689`
- `loss_active_template = 0.264050`
- `loss_frame_adjacent_cosine = 329.594893`
- `decoded_to_target_rms_ratio = 0.851279`

### `residual-shape-only`
- `loss_waveform = 0.119611`
- `loss_stft = 0.554591`
- `loss_rms_guard = 0.203732`
- `loss_active_template = 0.275200`
- `loss_frame_adjacent_cosine = 329.910991`
- `decoded_to_target_rms_ratio = 0.841527`

### validation 解读
1. `residual-shape-only`
   依然在买：
   - `waveform`
   - `stft`
   改善
2. 但它没有保住结构收益，
   反而继续拉坏：
   - `rms_guard`
   - `active_template`
   - `adjacent cosine`
   - `decoded_to_target_rms_ratio`
3. 更关键的是：
   - 它连上一轮更好的
     `branchcondadapter_conservative`
     都没有超过
4. 也就是说：
   - **把介入位置收窄到 residual-shape path，本身并没有自动消掉“重建更好、结构更差”的老问题**

## 四、fixed 6 条 aggregate

### 固定记录集
- `target::chapter3_2_firefly_212`
- `target::chapter3_2_firefly_155`
- `target::chapter3_3_firefly_162`
- `target::chapter3_17_firefly_133`
- `target::chapter3_3_firefly_245`
- `target::chapter3_2_firefly_163`

### baseline: `rms_floor=0.65`
- `loss_waveform = 0.120843`
- `loss_stft = 0.590533`
- `loss_rms_guard = 0.142804`
- `loss_active_template = 0.147958`
- `loss_frame_adjacent_cosine = 313.562889`
- `decoded_to_target_rms_ratio = 0.870710`

### `branchcondadapter_conservative`
- `loss_waveform = 0.120210`
- `loss_stft = 0.544413`
- `loss_rms_guard = 0.153712`
- `loss_active_template = 0.253424`
- `loss_frame_adjacent_cosine = 314.313416`
- `decoded_to_target_rms_ratio = 0.860224`

### `residual-shape-only`
- `loss_waveform = 0.119968`
- `loss_stft = 0.555409`
- `loss_rms_guard = 0.161527`
- `loss_active_template = 0.264562`
- `loss_frame_adjacent_cosine = 314.669098`
- `decoded_to_target_rms_ratio = 0.853588`

### fixed-6 解读
1. fixed-6
   与 validation
   完全同方向：
   - `waveform / stft`
     变好
   - 但
     `rms_guard / active_template / adjacent cosine / rms_ratio`
     一起回吐
2. 相比
   `branchcondadapter_conservative`，
   本轮
   `residual-shape-only`
   的特征更明确：
   - `waveform`
     只小幅更好
   - `stft`
     反而更差
   - 结构/能量指标则全面更差
3. 因而它不是：
   - 更稳的收窄版 adapter
4. 更像是：
   - 把 broad adapter
     的重建收益削弱了一部分，
     但没有真正解除结构回吐

## 五、消费链验证

### 1. export
- 已成功执行：
  - `export-offline-mvp-nores-vocoder-audio`
    fixed-6 导出
- export summary 中的
  `branch_label`
  为：
  - `offline_mvp_nores_vocoder_dataset_loop.step4__decode_residualshapecond_smooth3`
- 说明：
  - checkpoint
    已被自动识别成：
    `residual-shape-only`
    新结构

### 2. teacher-first / checkpoint consumer smoke
- 已对真实 candidate checkpoint
  执行：
  - `validate_vocoder_checkpoint_against_runtime_dims(...)`
  - `build_vocoder_model_from_runtime_dims(...)`
- 结果：
  - `waveform_decoder_mode = periodic_plus_noise_residual_shape_recurrent`
  - `use_decoder_branch_condition_adapter = false`
  - `use_residual_shape_branch_condition_adapter = true`

### 消费链结论
1. 本轮 checkpoint
   在：
   - export
   - teacher-first
   两条消费链上
   都已可被自动识别
2. 所以当前失败是：
   - 模型指标层面的失败
3. 不是：
   - plumbing
   - checkpoint shape
   - 导包兼容性
   的失败

## 六、当前判断
1. 这轮最重要的新信息不是：
   - residual-shape-only
     完全无效
2. 而是：
   - **仅仅把 adapter 收窄到 residual-shape path，还不够形成新的有效形态**
3. 当前可以把结论写得更硬：
   - broad hidden correction
     不成立
   - residual-shape-only
     这版最小收窄形态
     也不成立
4. 并且：
   - 它没有超过上一轮最好形态
     `branchcondadapter_conservative`

## 七、下一步建议
1. 当前不导人工听审包
2. 也不建议继续围绕：
   - 同一版 residual-shape-only adapter
   做初始化微调
3. 更合理的下一步应改成二选一：
   - 方案 A：
     继续把介入位点再收窄到
     residual gain / 标量 envelope bias
     这类更弱的调制
   - 方案 B：
     正式停止这条 decoder-conditioning 线，
     转去更上游的
     contract / semantic
     升级路线

## 一句话结论
- 第一发
  `residual-shape-only branch-conditioned adapter`
  最小 smoke
  已完成。
- 它和上一轮 broad adapter
  一样，
  仍然表现为：
  - `waveform / stft`
    更好
  - 但
    `active_template / adjacent cosine / rms_guard / rms_ratio`
    更差
- 而且它没有超过
  `branchcondadapter_conservative`。
- 因而当前不值得导听审，
  也说明“只收窄到 residual-shape path”
  还不是足够好的下一形态。
