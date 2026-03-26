# 381 Stage3 control-specific head family fail and coarse F0 sign diagnosis report

## 本轮目的
- 在以下路线都已失败后，验证更强的
  `control-specific head family`
  是否能打开 `student_control_packet` 的 named-control readiness：
  - `parallel_control_encoder_v1`
  - `bounded_log2_hz_v1`
  - `explicit F0 control-state branch`
- 同时确认：
  - 当前 `F0` 反号问题
    到底主要来自 `correction branch`
    还是更上游的 `coarse_log_f0`

## 改动
- `src/v5vc/streaming_student/model.py`
  - 扩展 `f0_control_branch_mode`：
    - `explicit_named_control_family_v1`
  - 在同一条显式 control-state branch 上，同时输出：
    - `log_f0_correction`
    - `vuv_logit_correction`
    - `aper_correction`
    - `energy_correction`
- `src/v5vc/streaming_student/losses.py`
  - `teacher_vuv_proxy / teacher_vuv_state`
    改为监督 `vuv_logits + vuv_logit_correction`
  - `teacher_energy_proxy / teacher_energy_state`
    改为监督 `energy + energy_correction`
- `src/v5vc/streaming_student/proxy_acoustic.py`
  - proxy acoustic 改为使用 corrected named controls
- `src/v5vc/streaming_student/downstream_control_packet.py`
  - packet export 改为导出 corrected
    `vuv / aper / energy`
- 新 config：
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_v1.json`

## 验证范围
- 使用仓库解释器：
  - `python.exe`
- 完成：
  - `py_compile`
  - 1-step smoke
  - 严格可比 `12-step full-validation`
  - `student_control_packet` export
  - `coarse_log_f0 / log_f0_correction / f0_log_proxy`
    的逐样本相关性诊断

## 对照对象
- baseline：
  - `reports/training/streaming_student_loop_boundedf0_f0warmup12_round1_1/logs/streaming_student_stage_loop_boundedf0_f0warmup12_round1_1.summary.json`
  - `reports/runtime/streaming_student_downstream_control_packet_parallelcontrolbranch_boundedf012_round1_1/streaming_student_downstream_control_packet.json`
- candidate：
  - `reports/training/streaming_student_loop_controlfamily12_round1_1/logs/streaming_student_stage_loop_controlfamily12_round1_1.summary.json`
  - `reports/runtime/streaming_student_downstream_control_packet_controlfamily12_round1_1/streaming_student_downstream_control_packet.json`

## 结果

### 1. Stage3 主指标继续改善
- validation step12：
  - `loss_total = 1.636606 -> 1.545674`
  - `loss_total_semantic_disabled_reference = 1.516201 -> 1.425769`
  - `loss_teacher_event = 0.444191 -> 0.441407`
  - `loss_teacher_event_prior = 0.512212 -> 0.511271`
- 说明：
  - 这条更强的 control family
    在 Stage3 内部监督层面确实继续正向

### 2. 但 readiness gate 仍完全不开
- 两边 summary 一致：
  - `e_evt_ready_count = 3`
  - `f0_ready_count = 0`
  - `vuv_ready_count = 0`
  - `aper_ready_count = 0`
  - `energy_ready_count = 0`
  - `all_records_auto_reject = true`
- 说明：
  - 即使把四个 named controls 一起放进显式 family，
    也没有把任何 record 推过 handoff 最低就绪线

### 3. 局部 named-control 指标有涨有跌，但不足以打开 gate
- `target::chapter3_3_firefly_162`
  - `vuv_reference_mae = 0.263044 -> 0.200857` 改善
  - `energy_stage5_norm_reference_mae = 0.329984 -> 0.305218` 改善
  - `aper_reference_mae = 0.415236 -> 0.475935` 变差
  - `f0_proxy_reference_corr = -0.483697 -> -0.525194` 变差
- `target::chapter3_3_firefly_138`
  - `vuv_reference_mae = 0.357789 -> 0.334442` 改善
  - `energy_stage5_norm_reference_mae = 0.327984 -> 0.310599` 改善
  - `aper_reference_mae = 0.401614 -> 0.450658` 变差
  - `f0_proxy_reference_corr = -0.174299 -> -0.203372` 变差
- `target::chapter3_4_firefly_106`
  - `energy_stage5_norm_reference_mae = 0.212695 -> 0.19806` 改善
  - `aper_reference_mae = 0.381614 -> 0.393843` 略差
  - `vuv_reference_mae = 0.361476 -> 0.380736` 略差
  - `f0_proxy_reference_corr = -0.594578 -> -0.63891` 变差
- 说明：
  - `vuv / energy` 有局部改善
  - 但 `aper / F0` 没有同步跟上
  - readiness 仍不足以放行

### 4. 关键新诊断：病灶不在 correction，本体 `coarse_log_f0` 就已反号
- baseline：
  - `target::chapter3_3_firefly_162`
    - `coarse_corr = -0.473104`
    - `corr_corr = 0.452015`
    - `proxy_corr = -0.483697`
  - `target::chapter3_4_firefly_106`
    - `coarse_corr = -0.584576`
    - `corr_corr = 0.56365`
    - `proxy_corr = -0.594578`
- candidate：
  - `target::chapter3_3_firefly_162`
    - `coarse_corr = -0.512619`
    - `corr_corr = 0.431862`
    - `proxy_corr = -0.525194`
  - `target::chapter3_4_firefly_106`
    - `coarse_corr = -0.62631`
    - `corr_corr = 0.532818`
    - `proxy_corr = -0.63891`
- 结论：
  - `log_f0_correction` 本身其实是正相关补偿项
  - 但它补不回 `coarse_log_f0` 已经存在的负相关主病因
  - 所以当前问题层级不是：
    - “student-side correction head 还不够强”
  - 而是：
    - `coarse_log_f0` 的上游生成 / target contract / sign-stable parameterization`
      本身就不对

## 判断
- `control-specific head family` 这条 student-side candidate
  正式 fail-fast 停线。
- 原因不是它完全没价值，而是：
  - Stage3 数字虽继续改善
  - 但 handoff readiness 依旧完全不开
  - 且关键病灶已被定位到更上游的 `coarse_log_f0`

## 当前含义
- 后续不应继续扫：
  - `explicit_named_control_family_v1` 的层数
  - `vuv / aper / energy correction` 的小限制
  - 其它 student-side correction-family 微调
- 下一步若继续，必须上到：
  - `coarse F0 target contract`
  - 或更上游的 `frontend F0 generation / sign-stable supervision`

## 下一步
- 暂不新增 Stage5 route。
- 暂不继续 student-side correction family 微调。
- 下一条主线候选应转为：
  - `coarse_log_f0` 的 sign-stable target / supervision / parameterization 诊断与修复
  - 而不是继续在 correction family 上追加容量。
