# 364. Stage5 shaped `teacher_e_evt` downstream fail-fast 报告

## 结论
- 我已把 Stage3 里刚出现正向信号的
  `center_weighted_boundary_progressive_final_clause_v1`
  继续推到了现有 Stage5 downstream `paired overfit24` 快速链路。
- 参数链这次已真实接通：
  - dataset index 顶层
    记录：
    - `teacher_e_evt_target_shaping_mode = center_weighted_boundary_progressive_final_clause_v1`
  - 单包 `target_contract`
    也记录了同一 shaping mode
- 但这条 shaped route
  在 Stage5 仍应 fail-fast 判停：
  - 对照 baseline：
    - `loss_total: 0.572382 -> 0.582266`
    - `loss_harmonic_envelope: 0.285243 -> 0.287515`
    - `loss_noise_envelope: 0.052113 -> 0.054858`
    - `loss_periodic_gate: 0.543894 -> 0.553126`
    - `loss_noise_gate: 0.631239 -> 0.646340`
  - validation export：
    - `auto_reject_count = 2`
    - `all_records_auto_reject = true`
- 所以当前结论很明确：
  - generation-side shaping
    在 Stage3 是有价值的
  - 但这版温和 shaping
    还不足以把 Stage5
    从 obvious buzz
    拉出来

## 一、本轮做了什么

### 1. 把 shaping mode 接到 Stage5 downstream/package builder
- 代码：
  - `src/v5vc/offline_teacher_downstream_contract.py`
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/cli.py`
- 新增：
  - `build-offline-mvp-nores-vocoder-dataset-packages`
    现在支持：
    - `--teacher-eevt-target-shaping-mode`
  - `skip_existing`
    也会检查：
    - `target_contract.teacher_e_evt_target_shaping_mode`

### 2. 当前快测路线
- 仍保持：
  - `paired overfit24`
  - `semantic_consumer_mode = none`
  - `target_contract_mode = legacy_proxy`
  - source parity sidecar 已接入
- 这样做的目的：
  - 只隔离
    teacher-side e_evt shaping
    这一处变量
  - 不再引入新的同层 Stage5 公式变化

## 二、smoke package
- 输出：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_eevtshapedv3parity_smoke_round1_1/`
- 关键确认：
  - dataset index 顶层：
    - `teacher_e_evt_target_shaping_mode = center_weighted_boundary_progressive_final_clause_v1`
  - 单包：
    - `source_scaffold_version = offline_teacher_vocoder_input_scaffold_v3`
    - `target_contract_mode = legacy_proxy`
    - `target_contract.teacher_e_evt_target_shaping_mode = center_weighted_boundary_progressive_final_clause_v1`
    - `e_evt_boundary_source = source_semantic_parity_sidecar`

## 三、paired overfit24

### 1. shaped route
- 输出：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_eevtshapedv3parity_round1_1/`
- validation step24：
  - `loss_total = 0.582266`
  - `loss_harmonic_envelope = 0.287515`
  - `loss_noise_envelope = 0.054858`
  - `loss_periodic_gate = 0.553126`
  - `loss_noise_gate = 0.646340`

### 2. 对照 baseline
- 对照：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_sourceparityplumb_baseline_round1_1/`
- validation step24：
  - `loss_total = 0.572382`
  - `loss_harmonic_envelope = 0.285243`
  - `loss_noise_envelope = 0.052113`
  - `loss_periodic_gate = 0.543894`
  - `loss_noise_gate = 0.631239`

### 3. 当前解释
1. 这次不是：
   - shaping mode
     没有进链
2. 相反：
   - Stage5 package contract
     已明确记录 shaping mode
   - 但共享指标
     仍整体更差
3. 所以当前不能把：
   - “Stage3 shaped labels
     变好了”
   直接推断成：
   - “Stage5 downstream
     就会自然脱离 buzz”

## 四、validation export 门禁
- 输出：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit24_eevtshapedv3parity_validation_trainingsync_round1_1/`
- 关键结果：
  - `auto_reject_count = 2`
  - `review_required_count = 0`
  - `all_records_auto_reject = true`
- 两条 validation
  仍都是：
  - `auto_reject_obvious_buzz`

## 五、当前阶段判断
1. 这轮不是白做：
   - 它第一次验证了：
     - teacher-label generation-side
       的轻量 shaping
       可以改善 Stage3
     - 但并不会自动转化成
       Stage5 downstream emergence
2. 因此当前正确结论不是：
   - generation-side shaping
     没价值
3. 而是：
   - 当前这版
     `boundary softening + final_clause ramp`
     仍然太弱，
     不足以解决 Stage5 的结构性 buzz
4. 所以后续不应继续做：
   - 这版 shaping
     的小参数再扫
   - 再扩一次同层 overfit/fullsplit
   - 再拉试听 bundle

## 六、下一步
1. 正式停止：
   - Stage5 current
     shaped `teacher_e_evt`
     downstream route
2. 若继续保留 teacher-label generation-side 主线，
   下一步必须更强：
   - 不能只做 boundary window
     软化
   - 应转向更根本的：
     - `teacher_e_evt`
       前 5 个 acoustic dims
       的 bridge/label 质量升级
     - 或更强的
       target contract / semantic state
       生成侧重构
