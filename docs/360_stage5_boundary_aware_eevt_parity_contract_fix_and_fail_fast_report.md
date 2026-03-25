# 360. Stage5 boundary-aware `e_evt` parity contract 修复与 fail-fast 报告

## 结论
- 我把
  `source_semantic_parity_sidecar`
  直接接进了
  Stage5 downstream `e_evt`
  contract，
  不再只是 metadata
  或外挂 consumer。
- 随后我又发现并修掉了一个更关键的 contract bug：
  - `event_presence_proxy`
    之前错误地用
    `amax(e_evt)`
  - 在 boundary-aware `e_evt`
    下，
    这会把
    `final_clause`
    之类的结构维度
    误当成
    “整句都有事件”
- 修完以后，
  这条线仍然应正式判停：
  - validation export
    依旧
    `all_records_auto_reject = true`
  - 所以当前 Stage5
    `boundary-aware e_evt`
    parity route
    仍不值得继续推
    fullsplit
    或人工试听

## 一、本轮先做了什么

### 1. 把 source-aware boundary 语义直接接入 Stage5 downstream contract
- 代码：
  - `src/v5vc/event_semantics.py`
  - `src/v5vc/offline_teacher_downstream_contract.py`
  - `src/v5vc/offline_teacher_vocoder_input_scaffold.py`
  - `src/v5vc/offline_vocoder_training.py`
- 当前行为：
  - `build_teacher_e_evt_v1_targets(...)`
    现在优先从：
    - `source_semantic_parity_sidecar`
    构造：
    - `p_pause_boundary`
    - `p_terminal_boundary`
    - `p_final_clause`
  - 不再只能依赖：
    - `target_event_timing_semantic_sidecar`
  - paired Stage5 package build
    现在会把：
    - `source_semantic_parity_sidecar`
    直接下传给
    `export_offline_mvp_teacher_downstream_contract(...)`

### 2. smoke 验证
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_eevtv3parity_smoke_round1_1/`
- 关键确认：
  - contract：
    `e_evt_summary.boundary_source = source_semantic_parity_sidecar`
  - scaffold：
    `event_semantics.e_evt_boundary_source = source_semantic_parity_sidecar`
  - notes
    也已从：
    - zero-filled diagnostics
    改成：
    - source-axis parity rasterization

## 二、随后定位到的更关键 contract bug

### 1. 问题是什么
- 旧逻辑把：
  - `event_presence_proxy = amax(e_evt)`
- 但现在
  `e_evt`
  的维度里已经包含：
  - `p_pause_boundary`
  - `p_terminal_boundary`
  - `p_final_clause`
- 这意味着：
  - 只要一句话是
    `single` / `final clause`
  - `event_presence_proxy`
    就可能整段被拉高
  - 进而错误抬高：
    - `noise_gate_target`
    - `activity_gate` 相关目标

### 2. 证据
- 修复前，
  `132`
  的 contract 摘要里：
  - `timing_final_clause_frame_ratio = 1.0`
  - `event_presence_proxy.mean = 1.0`
- 这显然不合理：
  - `final_clause`
    是结构位
  - 不是逐帧事件存在位

### 3. 修复内容
- 现在：
  - `event_presence_proxy`
    只从
    `e_evt[:, 0:4]`
    计算
  - 也就是只看：
    - `p_frication`
    - `p_stop_closure`
    - `p_burst`
    - `p_voicing`
- 不再把：
  - `a_aper`
  - boundary / clause
    维度
  混进去

### 4. 修复后 smoke
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_eevtv3paritypresencefix_smoke_round1_1/`
- 关键确认：
  - `132`
    的
    `event_presence_proxy.mean`
    从
    `1.0`
    回到：
    - `0.617205`

## 三、修复前后 overfit24 结果

### 1. 旧 baseline
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_sourceparityplumb_baseline_round1_1/`
- validation step24：
  - `loss_total = 0.572382`
  - `loss_harmonic_envelope = 0.285243`
  - `loss_noise_envelope = 0.052113`
  - `loss_periodic_gate = 0.543894`
  - `loss_noise_gate = 0.631239`

### 2. parity boundary-aware `e_evt`，但还没修 proxy
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_eevtv3parity_round1_1/`
- validation step24：
  - `loss_total = 0.565315`
  - `loss_harmonic_envelope = 0.287515`
  - `loss_noise_envelope = 0.055844`
  - `loss_periodic_gate = 0.553126`
  - `loss_noise_gate = 0.556654`
- 解释：
  - 表面上
    `loss_total`
    好于 baseline
  - 但这个结果已经被
    `event_presence_proxy`
    错算污染，
    不能直接当真

### 3. parity boundary-aware `e_evt`，并修好 proxy
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_eevtv3paritypresencefix_round1_1/`
- validation step24：
  - `loss_total = 0.583198`
  - `loss_harmonic_envelope = 0.287515`
  - `loss_noise_envelope = 0.055122`
  - `loss_periodic_gate = 0.553126`
  - `loss_noise_gate = 0.649682`

### 4. 当前解释
- 这说明：
  - 先前那点
    `loss_total`
    改善
    不能再当有效正向证据
- 修完 contract bug
  以后，
  这条路线
  在共享指标上
  并没有站住

## 四、自动门禁结果
- 修复后 export：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit24_eevtv3paritypresencefix_validation_trainingsync_round1_1/nores_vocoder_audio_export.json`
- 关键结果：
  - `auto_reject_count = 2`
  - `review_required_count = 0`
  - `all_records_auto_reject = true`
- 也就是说：
  - 即使 boundary-aware
    parity contract
    已接通
  - 即使错误的
    `event_presence_proxy`
    也已经修掉
  - 最终输出仍然属于：
    - obvious buzz

## 五、当前阶段判断
1. 这轮不是白做：
   - 它收掉了
     一个真实的
     Stage5 contract bug
   - 以后所有
     boundary-aware
     `e_evt`
     路线
     都不能再用
     `amax(e_evt)`
     当
     `event_presence_proxy`
2. 但作为训练路线，
   当前 Stage5
   `boundary-aware e_evt`
   parity route
   仍应正式判停
3. 所以下一步不该继续做：
   - fullsplit
   - 听审 bundle
   - decode 小修
4. 更合理的下一步应是：
   - 把这条结论写死后，
   - 转去更明确的
     Stage5 target contract /
     supervision route

## 六、结论收口
1. 现在可以更硬地说：
   - 不是因为
     `source-only e_evt`
     还少一个小 bug
     才失败
2. 即使把：
   - boundary-aware parity
     接进去
   - `event_presence_proxy`
     合同错误
     修掉
   以后，
   结果仍然是：
   - `all_records_auto_reject = true`
3. 所以 Stage5
   当前这条
   `e_evt` consumer-side
   路线
   到这里应正式收口
