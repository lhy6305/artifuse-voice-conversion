# 361. Stage5 `teacher_e_evt_gate_targets_v1` supervision route fail-fast 报告

## 结论
- 我把 Stage5 package 里的 gate supervision 正式升级成了显式 `target_contract_mode`，不再只靠旧的 proxy target 混合逻辑。
- 新模式 `teacher_e_evt_gate_targets_v1` 已真实沿链路生效：
  - package / dataset index 都明确记录了：
    - `target_contract_mode = teacher_e_evt_gate_targets_v1`
  - 其 gate target 公式也被写进了 package summary
- 但这条 supervision-side route 仍应 fail-fast 判停：
  - paired overfit24 validation step24：
    - `loss_total = 0.583764`
  - 旧 baseline：
    - `loss_total = 0.572382`
  - validation export：
    - `auto_reject_count = 2`
    - `all_records_auto_reject = true`
- 所以当前结论很硬：
  - 不是只有 Stage5 input-side consumer 不行
  - 连 supervision-side `e_evt gate target` 显式替换，也还不足以把系统拉出 obvious buzz

## 一、本轮做了什么

### 1. 新增显式 `target_contract_mode`
- 代码：
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/cli.py`
- 新增模式：
  - `legacy_proxy`
  - `teacher_e_evt_gate_targets_v1`
- 当前行为：
  - `legacy_proxy`
    保持现有 Stage5 gate supervision 逻辑不变
  - `teacher_e_evt_gate_targets_v1`
    改为从显式 `e_evt` 维度构造 gate target

### 2. 新 `teacher_e_evt_gate_targets_v1` 的 supervision 公式
- `periodic_gate_target`
  使用：
  - `max(vuv, p_voicing)`
- `noise_gate_target`
  使用：
  - `max(aper * E_log_rms_norm, max(max(p_frication, p_stop_closure, p_burst, a_aper), max(p_pause_boundary, p_terminal_boundary) * max(aper, E_log_rms_norm)))`
- 明确排除：
  - `p_final_clause`
- 这样做的目的：
  - 不再依赖旧的泛化 proxy
    `event_presence_proxy`
  - 同时避免把句法结构位继续误当成逐帧事件存在

### 3. package/index/复用逻辑也一起接通
- package payload / summary
  已新增：
  - `target_contract`
- dataset index
  已新增：
  - 顶层 `target_contract_mode`
  - 单包 `target_contract`
- `skip_existing`
  现在也会检查：
  - 旧包的 `target_contract_mode`
    是否与当前请求一致

## 二、smoke 结果
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_eevttargetcontract_smoke_round1_2/`
- 关键确认：
  - dataset index 顶层：
    - `target_contract_mode = teacher_e_evt_gate_targets_v1`
  - 单包 `target_contract`：
    - `contract_family = teacher_e_evt_gate_targets_v1`
    - `uses_explicit_e_evt = true`
    - `e_evt_boundary_source = source_semantic_parity_sidecar`
    - `excluded_e_evt_dimensions = ["p_final_clause"]`
- 这说明：
  - 本轮不是又做了一个 metadata-only 标记
  - gate supervision 公式已经真实换掉

## 三、paired overfit24 结果

### 1. 新 route
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_eevttargetcontract_round1_1/`
- validation step24：
  - `loss_total = 0.583764`
  - `loss_harmonic_envelope = 0.285446`
  - `loss_noise_envelope = 0.054458`
  - `loss_periodic_gate = 0.558537`
  - `loss_noise_gate = 0.660759`

### 2. 对照 baseline
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_sourceparityplumb_baseline_round1_1/`
- validation step24：
  - `loss_total = 0.572382`
  - `loss_harmonic_envelope = 0.285243`
  - `loss_noise_envelope = 0.052113`
  - `loss_periodic_gate = 0.543894`
  - `loss_noise_gate = 0.631239`

### 3. 当前解释
- 新 supervision route
  并没有在共享指标上站住：
  - `loss_total`
    更差
  - `loss_noise_envelope`
    更差
  - `loss_periodic_gate`
    更差
  - `loss_noise_gate`
    更差
- 也就是说：
  - 这轮不是“量化更好但听感没起来”
  - 而是量化和自动门禁都没有给出继续投资的理由

## 四、validation export 门禁
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit24_eevttargetcontract_validation_trainingsync_round1_1/`
- 关键结果：
  - `auto_reject_count = 2`
  - `review_required_count = 0`
  - `all_records_auto_reject = true`
- 两条 validation
  仍都是：
  - `auto_reject_obvious_buzz`

## 五、当前阶段判断
1. 这轮不是白做：
   - 它第一次把 Stage5 gate supervision 本身做成了显式可切换合同
   - 后续所有 Stage5 supervision A/B 都不必再靠改散落公式硬比
2. 但作为训练路线：
   - 当前 `teacher_e_evt_gate_targets_v1`
     已被 fail-fast 否定
3. 因而后续不应再做：
   - 这个公式上的小扫参
   - `pause / terminal`
     权重小修
   - 同层 overfit/fullsplit 扩展
   - 人工试听 bundle

## 六、下一步
1. 正式停止：
   - Stage5 current
     `target_contract_mode = teacher_e_evt_gate_targets_v1`
     route
2. 如果还保留 Stage5 主线，
   下一步必须更上收：
   - target contract 更强的 supervision 形态
   - 或 Stage3/teacher 侧更根本的 target shaping
3. 不再把：
   - “显式 `e_evt` 已接到 consumer-side”
   - “显式 `e_evt` 已接到 target-side gate supervision”
   误解成：
   - Stage5 现在只差一个公式细节
