# 320. Stage5 `contractv2_normfix` residual-shape-only 开关 plumbing 与 checkpoint 结构自动识别修复报告

## 一、目的
1. 承接
   `docs/319_stage5_contractv2_normfix_branch_conditioned_decoder_adapter_minimal_smoke_report.md`
   的下一步，
   先把
   `residual-shape-only`
   新结构的工程链路补齐
2. 这一步回答的不是：
   - 新结构是否有效
3. 而是：
   - 新开关是否已经从 CLI 一路接到训练入口
   - `audio export`
     与
     `teacher_first`
     这类 checkpoint 消费侧，
     能否仅凭 checkpoint
     自动识别新结构，
     避免后续导包时把模型误判成旧形态

## 二、恢复到的中断状态
1. 已存在的半成品改动包括：
   - `cli.py`
     已新增
     `--use-residual-shape-branch-condition-adapter`
   - `offline_vocoder_training.py`
     已把该开关接入：
     - train step
     - training loop
     - dataset loop
   - `offline_vocoder_scaffold.py`
     已实现
     residual-shape-only
     adapter 本体
   - `nores_vocoder_audio_export.py`
     已开始支持从 checkpoint
     反推新结构
2. 但当时仍停在一个危险的中间态：
   - `teacher_first_vc_demo.py`
     仍按旧逻辑构建与校验 vocoder checkpoint
   - 它还把 checkpoint shape
     硬编码成
     `fused_single`
     的
     `waveform_decoder.3.*`
   - 同时
     `infer_branch_label(...)`
     的调用方
     还没跟上新签名

## 三、本次代码修复

### 1. 共享 checkpoint 结构推断
- 文件：
  - `src/v5vc/offline_vocoder_scaffold.py`
- 新增共享辅助函数：
  - `infer_waveform_decoder_mode_from_state_dict(...)`
  - `infer_decoder_branch_condition_adapter_from_state_dict(...)`
  - `infer_residual_shape_branch_condition_adapter_from_state_dict(...)`
  - `build_nores_vocoder_scaffold_from_state_dict(...)`
- 作用：
  - 统一从
    `model_state_dict`
    反推：
    - waveform decoder mode
    - decoder branch-condition adapter
    - residual-shape-only adapter

### 2. export 侧改为复用共享推断
- 文件：
  - `src/v5vc/nores_vocoder_audio_export.py`
- 调整：
  - `build_model_from_checkpoint(...)`
    现在直接复用
    `build_nores_vocoder_scaffold_from_state_dict(...)`
  - `infer_branch_label(...)`
    与
    `describe_waveform_decode_variant(...)`
    增加默认参数，
    避免旧调用点在签名扩展后直接崩掉
  - export summary
    与 branch label
    会继续落盘：
    - `use_decoder_branch_condition_adapter`
    - `use_residual_shape_branch_condition_adapter`

### 3. teacher-first 下游消费者补齐
- 文件：
  - `src/v5vc/teacher_first_vc_demo.py`
- 调整：
  - vocoder checkpoint
    重建逻辑改为复用：
    `build_nores_vocoder_scaffold_from_state_dict(...)`
  - vocoder checkpoint
    校验逻辑不再假定：
    `fused_single`
    固定 shape
  - 新校验方式改为：
    - 先根据 checkpoint
      反推结构
    - 再实例化对应 scaffold
    - 对整份 expected `state_dict`
      做 missing / unexpected / shape mismatch
      核对
  - `infer_branch_label(...)`
    的 teacher-first 调用方
    已补齐：
    - `decoder_branch_mean_mix_alpha=0.0`
    - `use_decoder_branch_condition_adapter`
    - `use_residual_shape_branch_condition_adapter`

## 四、验证

### 1. 语法级 smoke
- 命令：
```powershell
.\python.exe -m py_compile src\v5vc\offline_vocoder_scaffold.py src\v5vc\nores_vocoder_audio_export.py src\v5vc\teacher_first_vc_demo.py src\v5vc\offline_vocoder_training.py src\v5vc\cli.py
```
- 结果：
  - 通过

### 2. 合成 residual-shape-only checkpoint smoke
- 方法：
  - 直接实例化：
    `periodic_plus_noise_residual_shape_recurrent`
    + `use_residual_shape_branch_condition_adapter=True`
    的 scaffold
  - 仅用其 `state_dict`
    走：
    - `build_model_from_checkpoint(...)`
    - `validate_vocoder_checkpoint_against_runtime_dims(...)`
- 结果：
  - 能正确识别：
    - decoder mode =
      `periodic_plus_noise_residual_shape_recurrent`
    - `use_residual_shape_branch_condition_adapter = true`
    - `use_decoder_branch_condition_adapter = false`

### 3. 真实 adapter checkpoint smoke
- 使用 checkpoint：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_contractv2_normfix_periodicshape_recurrent_periodictemporal_periodicgate_rmsfloor065_branchcondadapter_smoke_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step4.pt`
- 验证路径：
  - `nores_vocoder_audio_export.build_model_from_checkpoint(...)`
  - `teacher_first_vc_demo.validate_vocoder_checkpoint_against_runtime_dims(...)`
  - `teacher_first_vc_demo.build_vocoder_model_from_runtime_dims(...)`
- 结果：
  - 全部通过
  - 能正确识别：
    - decoder mode =
      `periodic_plus_noise_residual_shape_recurrent`
    - `use_decoder_branch_condition_adapter = true`
    - `use_residual_shape_branch_condition_adapter = false`

## 五、当前状态结论
1. `residual-shape-only`
   开关的工程 plumbing
   现已补齐到训练入口
2. `audio export`
   不再需要额外手写结构参数，
   已可从 checkpoint
   自动识别新结构
3. 更关键的是：
   `teacher_first`
   这条后续真实消费链
   也已不再依赖旧的
   `fused_single`
   shape 假设
4. 因而下一次真正跑
   `residual-shape-only`
   smoke 时，
   不会再因为 checkpoint 误判而卡在导包前

## 六、下一步
1. 直接启动第一发：
   - `residual-shape-only branch-conditioned adapter`
     最小 smoke
2. 跑完后优先验证：
   - fixed-set aggregate
   - `audio export`
   - `teacher_first`
     是否都能无人工干预地吃下新 checkpoint
