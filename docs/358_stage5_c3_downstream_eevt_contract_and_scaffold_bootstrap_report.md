# 358. Stage5 `C3` downstream `e_evt` contract / scaffold bootstrap 报告

## 结论
- 本轮已把
  Stage5 `C3`
  下游真正推进到：
  - teacher downstream contract
    显式导出
    `e_evt`
  - teacher vocoder scaffold
    真正消费
    `e_evt`
- 当前做法不是：
  - 再做 target-side semantic sidecar
    微调
- 而是把已经在 Stage3
  站稳的
  `teacher_e_evt_v1`
  概念，
  真正接到
  Stage5 consumer-side
  contract 上。
- 当前边界也已明确写死：
  - 这是
    source-only runtime
    downstream bootstrap
  - 没有 target timing sidecar
  - 所以后 3 个 boundary 维度
    当前只能是
    zero-filled diagnostics
  - 不能误写成
    完整 boundary-aware
    `e_evt`
    已落地

## 一、本轮代码改动
- 更新：
  - `src/v5vc/offline_teacher_downstream_contract.py`
  - `src/v5vc/offline_teacher_vocoder_input_scaffold.py`
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/offline_vocoder_scaffold.py`
  - `src/v5vc/teacher_first_vc_demo.py`

### 1. downstream contract 升级到 `v3`
- 新导出版本：
  - `offline_teacher_downstream_control_v3`
- 当前 payload
  在保留：
  - `event_probs`
  的同时，
  新增：
  - `e_evt`
  - `e_evt_meta`
  - `e_evt_summary`
- `event_presence_proxy`
  也不再假设
  `event_probs[..., 0]`
  是旧活动门，
  而是改为：
  - `amax(e_evt)`

### 2. teacher vocoder scaffold 升级到 `v3`
- 新 scaffold 版本：
  - `offline_teacher_vocoder_input_scaffold_v3`
- 当前行为：
  - `available_controls`
    同时保留：
    - `event_probs`
    - `e_evt`
  - noise branch
    由原先消费：
    - `event_probs`
    改为优先消费：
    - `e_evt`
  - legacy
    `event_probs`
    退到：
    - diagnostic compatibility
- 当前 smoke 上：
  - `periodic_input_dim = 36`
  - `noise_input_dim = 36`
- 也就是说：
  - 这次没有改动 Stage5 模型输入维度
  - 只改了 semantic family

### 3. 兼容链同步补齐
- `offline_vocoder_training.py`
  与
  `offline_vocoder_scaffold.py`
  已把
  `offline_teacher_vocoder_input_scaffold_v3`
  加入支持列表
- `teacher_first_vc_demo.py`
  已把旧
  `event_probs`
  family override
  映射到统一：
  - `event_family`
  并允许同时命中：
    - `noise.e_evt`
    - `noise.event_probs`
  以避免旧诊断 override
  因 semantic 改名而悄悄失效

## 二、为什么这一步有价值
1. 这次推进的是：
   - Stage3 已站稳的
     `teacher_e_evt_v1`
   - 向 Stage5 `C3`
     downstream consumer
     的真实落地
2. 它解决的不是：
   - 听感立刻变好
3. 它解决的是：
   - 以前 Stage5 下游明明在谈
     `e_evt`
   - 但 consumer 实际仍吃
     legacy `event_probs`
   - 现在这层错位终于被收掉了

## 三、最小 smoke 验证

### 1. downstream contract smoke
- 目录：
  - `reports/runtime/offline_mvp_teacher_downstream_contract_eevt_smoke_round1_1/`
- 核心结果：
  - `contract_version = offline_teacher_downstream_control_v3`
  - `e_evt.shape = [457, 8]`
  - `event_probs.shape = [457, 8]`
  - `e_evt_summary.timing_sidecar_used = false`
  - `timing_pause_frame_ratio = 0.0`

### 2. teacher vocoder scaffold smoke
- 目录：
  - `reports/runtime/offline_mvp_teacher_vocoder_input_scaffold_eevt_smoke_round1_1/`
- 核心结果：
  - `scaffold_version = offline_teacher_vocoder_input_scaffold_v3`
  - `noise_feature_semantics = ["e_evt", "aper", "vuv", "E_log_rms_norm", "alpha", "s_spk_target", "s_geom_target"]`
  - `noise_event_feature_family = e_evt`
  - `available_controls`
    已同时存在：
    - `event_probs`
    - `e_evt`

### 3. Stage5 no-res scaffold smoke
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_scaffold_eevt_smoke_round1_2/`
- 结果：
  - 正常完成 shape build
  - `periodic_input_dim = 36`
  - `noise_input_dim = 36`
  - 新 summary
    已明确写出：
    - noise branch
      现在消费
      bootstrap `e_evt`

### 4. Stage5 train-target package smoke
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_train_targets_eevt_smoke_round1_1/`
- 核心结果：
  - `training_package_version = offline_mvp_nores_vocoder_train_targets_v2`
  - `source_scaffold_version = offline_teacher_vocoder_input_scaffold_v3`
  - package build
    正常完成

### 5. Stage5 dataset package smoke
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_eevtplumb_smoke_round1_1/`
- 核心结果：
  - `train_package_count = 1`
  - `validation_package_count = 1`
  - `summary.train.source_scaffold_versions = ["offline_teacher_vocoder_input_scaffold_v3"]`
  - `summary.validation.source_scaffold_versions = ["offline_teacher_vocoder_input_scaffold_v3"]`
  - 单包 payload
    也已确认：
    - `source_scaffold_version = offline_teacher_vocoder_input_scaffold_v3`
    - `periodic_input_dim = 36`
    - `noise_input_dim = 36`

## 四、当前阶段判断
1. 现在可以正式说：
   - Stage5 `C3`
     downstream consumer
     已不再只停留在
     legacy `event_probs`
2. 更准确的当前状态是：
   - source acoustic state
     已在链上
   - bootstrap
     `e_evt`
     也已在链上
   - 但 source-only runtime
     还没有 target timing sidecar
   - 所以后 3 个 boundary 维度
     只是零填诊断位
3. 所以下一步不该写成：
   - `e_evt`
     已全部完成
4. 更合理的写法应是：
   - Stage5 `C3`
     已具备显式
     `e_evt`
     consumer entry
   - 下一步要评估：
     - 如何给 downstream route
       提供更强的 boundary-aware
       `e_evt`
       资产
     - 或如何把当前已通过 smoke 的
       `v3 scaffold`
       拉回
       fullsplit
       正式基线验证

## 五、下一步
1. 保持当前：
   - `event_probs`
     仅作 legacy compatibility
   - `e_evt`
     作为 Stage5 downstream
     新默认 event family
2. 不再回到：
   - target-only semantic/timing
     小 consumer
     微调
3. 下一条更值钱的推进应改为：
   - 用当前
     `offline_teacher_vocoder_input_scaffold_v3`
     做
     Stage5 package/fullsplit
     级验证
   - 明确记录
     `source_scaffold_version = v3`
     的量化对照
