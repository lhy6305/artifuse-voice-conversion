# 176. teacher downstream control contract 报告

## 背景
- `docs/175_teacher_runtime_wrapper_and_streaming_smoke_test_report.md`
  已把 teacher-first
  runtime wrapper
  落成正式代码与命令
- 但仅有 runtime wrapper
  还不够作为
  “下一环节接线”的正式入口，
  因为下游模块需要一个
  明确的输入合同

## 本轮目标
1. 把当前 teacher
   真正可提供的控制量
   规范成正式 contract
2. 同时把:
   - 目标说话人校准条件
   - 当前缺失项
   明确写进 contract
3. 避免把当前产物
   误写成设计稿里的
   最终 Stage5 vocoder 合同

## 本轮代码落地
### 1. 新增 contract 导出模块
- 新增:
  - `src/v5vc/offline_teacher_downstream_contract.py`

### 2. 新增 CLI 命令
- 新增:

```powershell
.\python.exe manage.py export-offline-mvp-teacher-downstream-contract --input-audio <wav>
```

- 当前命令会导出:
  - `teacher_downstream_control_contract.pt`
  - `teacher_downstream_control_contract.json`
  - `teacher_downstream_control_contract.md`

## contract 内容
### 1. 当前明确提供的字段
- `frame_start_ms`
- `z_art`
- `event_logits`
- `event_probs`
- `hidden`
- `fused_hidden`
- `acoustic.energy_log`
- `acoustic.abs_mean`
- `acoustic.zero_cross_rate`
- `acoustic.delta_energy`
- `conditioning.s_spk_target`
- `conditioning.s_geom_target`
- `conditioning.alpha`

### 2. 当前额外导出的 proxy 字段
- `energy_proxy`
- `voiced_proxy`
- `aperiodicity_proxy`
- `event_presence_proxy`
- `energy_change_proxy`

这些 proxy
都只是当前 teacher
可用输出上的桥接映射，
不是最终设计稿里
独立训练好的
正式控制头。

### 3. 当前明确缺失的设计稿字段
- `f0_hz`
- `r_res`
- `final_vocoder_waveform`

## 为什么要这样设计
### 1. 当前 teacher 还不能诚实地声称自己具备最终 Stage5 条件集
- 设计稿里的
  Stage5 无残差声码器
  理想输入是:
  - `z_art`
  - `e_evt`
  - `F0`
  - `vuv`
  - `aper`
  - `E`
  - `s_spk`
  - `s_geom`
- 但当前 offline teacher
  真实稳定提供的是:
  - `z_art`
  - `event_probs / event_logits`
  - 一组 `acoustic` 四维 proxy
- 所以这轮 contract
  只能写成:
  - teacher-first downstream control contract
  不能写成:
  - final vocoder conditioning contract

### 2. calibration 条件必须一起落盘
- 否则下游模块
  即使拿到了控制帧，
  也缺少目标说话人条件
- 本轮 contract
  默认同时带上:
  - `s_spk_target`
  - `s_geom_target`
  - `alpha`
  来源:
  - `data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json`

## smoke test
### 样本
- `data_prep/round1_1/firefly_mainstream/audio/chapter3_3_firefly_162.wav`

### 命令

```powershell
.\python.exe manage.py export-offline-mvp-teacher-downstream-contract --input-audio data_prep/round1_1/firefly_mainstream/audio/chapter3_3_firefly_162.wav --output-dir reports/runtime/offline_mvp_teacher_downstream_contract_smoke_chapter3_3_firefly_162 --chunk-samples 2048 --device cpu
```

### 结果
- contract 已成功写出:
  - `reports/runtime/offline_mvp_teacher_downstream_contract_smoke_chapter3_3_firefly_162/teacher_downstream_control_contract.pt`
  - `reports/runtime/offline_mvp_teacher_downstream_contract_smoke_chapter3_3_firefly_162/teacher_downstream_control_contract.json`
  - `reports/runtime/offline_mvp_teacher_downstream_contract_smoke_chapter3_3_firefly_162/teacher_downstream_control_contract.md`
- 同时保留了
  与 full pass 的
  runtime 一致性验证:
  - `frame_count_equal = true`
  - `frame_alignment_equal = true`

## 当前判断
- 现在 teacher-first
  已不只是:
  - 可跑 runtime
- 还已经具备:
  - 可供下游模块接线的
    正式输入合同

- 但必须坚持一个边界:
  - 当前 contract
    是过渡性 teacher-first
    control contract
  - 不是最终
    Stage5 vocoder contract

## 下一步
1. 后续下游模块
   默认从:
   - `teacher_downstream_control_contract.pt`
   读取输入
2. 若进入真正的
   Stage5 vocoder 开发，
   再把当前 contract
   升级到:
   - 显式 `F0 / vuv / aper / E`
   - 可选 `r_res`
3. 在那之前，
   不要把当前 proxy 字段
   误当成最终设计稿里的
   全量条件定义
