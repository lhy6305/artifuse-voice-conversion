# 366. Stage5 `teacher_e_evt` acoustic-bridge downstream fail-fast 报告

## 结论
- 我已把当前更强的 generation-side 候选：
  - `teacher_e_evt_bridge_mode = acoustic_guided_event_bridge_v1`
  - `teacher_e_evt_target_shaping_mode = center_weighted_boundary_progressive_final_clause_v1`
  真正推到了现有 Stage5 downstream `paired overfit24` 快速链路。
- 参数链这次已真实生效：
  - dataset index 顶层
    已记录：
    - `teacher_e_evt_bridge_mode = acoustic_guided_event_bridge_v1`
    - `teacher_e_evt_target_shaping_mode = center_weighted_boundary_progressive_final_clause_v1`
  - 单包 `target_contract`
    也记录了同一组 mode
- 但这条 route 仍应 fail-fast 判停：
  - 对照旧 baseline：
    - `loss_total: 0.572382 -> 0.599406`
    - `loss_harmonic_envelope: 0.285243 -> 0.294476`
    - `loss_noise_envelope: 0.052113 -> 0.062687`
    - `loss_periodic_gate: 0.543894 -> 0.573510`
  - 对照上一版
    shaped-only：
    - `loss_total: 0.582266 -> 0.599406`
  - validation export：
    - `auto_reject_count = 2`
    - `all_records_auto_reject = true`
- 所以当前结论很硬：
  - `acoustic_guided_event_bridge_v1`
    是 Stage3 侧更好的 teacher-label generation-side 资产
  - 但推到当前 Stage5 downstream
    反而更差，
    仍不能解除 obvious buzz

## 一、本轮做了什么

### 1. 把 `teacher_e_evt_bridge_mode` 接到 Stage5 downstream/package 链
- 代码：
  - `src/v5vc/offline_teacher_downstream_contract.py`
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/cli.py`
- 新增：
  - Stage5 contract
    现在也支持显式：
    - `teacher_e_evt_bridge_mode`
  - dataset package/index/skip_existing
    也会记录并检查：
    - `teacher_e_evt_bridge_mode`
    - `teacher_e_evt_target_shaping_mode`

### 2. 快测口径
- 仍保持：
  - `paired overfit24`
  - `semantic_consumer_mode = none`
  - `target_contract_mode = legacy_proxy`
  - `source_semantic_parity_sidecar` 已接
- 只切：
  - `bridge_mode`
  - `shaping_mode`

## 二、smoke package
- 输出：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_eevtacousticbridge_smoke_round1_1/`
- 关键确认：
  - 顶层：
    - `teacher_e_evt_bridge_mode = acoustic_guided_event_bridge_v1`
    - `teacher_e_evt_target_shaping_mode = center_weighted_boundary_progressive_final_clause_v1`
  - 单包：
    - `target_contract.teacher_e_evt_bridge_mode = acoustic_guided_event_bridge_v1`
    - `target_contract.teacher_e_evt_target_shaping_mode = center_weighted_boundary_progressive_final_clause_v1`
    - `source_scaffold_version = offline_teacher_vocoder_input_scaffold_v3`

## 三、paired overfit24

### 1. acoustic-bridge candidate
- 输出：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_eevtacousticbridge_round1_1/`
- validation step24：
  - `loss_total = 0.599406`
  - `loss_harmonic_envelope = 0.294476`
  - `loss_noise_envelope = 0.062687`
  - `loss_periodic_gate = 0.573510`
  - `loss_noise_gate = 0.637708`

### 2. 对照 baseline
- baseline：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_sourceparityplumb_baseline_round1_1/`
- shaped-only：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_eevtshapedv3parity_round1_1/`
- validation step24 对照：
  - baseline：
    - `loss_total = 0.572382`
  - shaped-only：
    - `loss_total = 0.582266`
  - acoustic-bridge：
    - `loss_total = 0.599406`

## 四、validation export 门禁
- 输出：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit24_eevtacousticbridge_validation_trainingsync_round1_1/`
- 关键结果：
  - `auto_reject_count = 2`
  - `review_required_count = 0`
  - `all_records_auto_reject = true`
- 两条 validation
  仍都是：
  - `auto_reject_obvious_buzz`

## 五、当前解释
1. 当前 teacher-label generation-side
   确实已经找到
   更强的上游正向方向：
   - `acoustic_guided_event_bridge_v1`
2. 但这轮也再次说明：
   - Stage3 正向
     不能直接外推成
     Stage5 downstream 也会更好
3. 而且这次不是打平，
   是更差：
   - 相比旧 baseline
     更差
   - 相比上一版 shaped-only
     也更差
4. 所以当前不能继续做：
   - `acoustic_guided_event_bridge_v1`
     在 Stage5 同层的 overfit/fullsplit 扩展
   - 也不应再做人耳试听包

## 六、下一步
1. 正式停止：
   - Stage5 current
     acoustic-bridge downstream route
2. 若继续保留
   teacher-label generation-side 主线，
   当前更合理的判断是：
   - 上游 `teacher_e_evt`
     资产质量
     已经在变好
   - 但 Stage5 当前 no-res downstream consumer/supervision
     仍不是承接 breakthrough 的层
3. 所以后续不该继续抠：
   - current Stage5 route
4. 应转去：
   - 更高层级的 Stage3/teacher target state 资产升级
   - 或重新评估承接这些上游改进的真正下游层
