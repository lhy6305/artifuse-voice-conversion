# 338. Stage5 `target_event_semantic_sidecar` 接线、overfit24 对照与最小听审包报告

## 结论
- 我先检查了刚才这轮代码改动里是否残留错误路径；
  结果是：
  - `src/v5vc/cli.py`
  - `src/v5vc/offline_vocoder_training.py`
  中都没有
  `workdir3`
  或临时路径残留
- 随后继续把
  `target_event_semantic_sidecar`
  这条线推进到：
  - Stage5 package/index 接线完成
  - Stage5 dataset loop 的保守 semantic weighting smoke 跑通
  - strict comparable
    overfit24
    baseline vs semantic-weight
    A/B 跑完
  - 最小听审包已导出
- 当前量化判断是：
  - semantic weighting
    确实已经生效
  - 但收益仍偏弱，
    还不能只凭数值宣布这条线成立
- 因而当前最值钱的下一问已收敛为：
  - 听
    `reports/audio/stage5_paired_parallel_overfit24_semanticweight_compare_quick_audit_20260325/`
  - 只判断
    semantic variant
    是否真的比 baseline
    更接近 target，
    且不再只是 pure buzz

## 一、路径自检
- 直接扫描我刚才改动的代码文件后，
  未发现以下残留：
  - `workdir3`
  - `stage5_semantic_smoke_specs`
  - `semantic_plumb_smoke`
  - 旧绝对路径
- 因此本轮继续推进前，
  代码侧不存在你刚才指出的那类错误路径问题。

## 二、代码接线范围

### 1. CLI
- `build-offline-mvp-nores-vocoder-dataset-packages`
  新增：
  - `--target-event-semantic-sidecar`
- `run-offline-mvp-nores-vocoder-dataset-training-loop`
  新增：
  - `--semantic-supervision-enabled`

### 2. Stage5 package / dataset index
- package payload
  现在会写入：
  - `target_event_semantic_sidecar`
  - `target_semantic_overview`
- dataset index
  现在会记录：
  - `target_event_semantic_sidecar_path`
  - split 级
    `semantic_sidecar_summary`
- paired package
  若 sidecar 可用、
  但旧 package
  尚未带上该字段，
  builder
  会强制重建，
  避免旧缓存把新 contract
  静默吃掉。

### 3. Stage5 training consumer
- dataset loop
  新增了保守的 package-level semantic weighting：
  - 先依据
    `target_event_semantic_sidecar`
    生成
    `semantic_base_multiplier`
  - 再用
    `package_alpha = 0.2`
    缩成
    `semantic_package_multiplier`
- 训练与验证现在都会记录：
  - `loss_total_semantic_weighted`
  - `semantic_sidecar_present`
  - `semantic_weight_applied`
  - `semantic_base_multiplier`
  - `semantic_package_multiplier`
- best checkpoint
  选择逻辑也已经切到：
  - 优先按
    `loss_total_semantic_weighted`
    选

## 三、接线验证

### 1. semantic-plumbed dataset package smoke
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_paired_parallel_overfit_semantic_plumb_smoke_round1_1/`
- 结果：
  - `train_packages = 2`
  - `validation_packages = 2`
  - split 级
    `semantic_sidecar_summary.present_count = 2`
- package payload
  已确认带有：
  - `target_event_semantic_sidecar`
  - `target_semantic_overview.semantic_contract_version = target_event_semantic_sidecar_v1`

### 2. semantic weighting 1-step smoke
- 输出目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit_semantic_weighting_smoke_round1_1/`
- 关键结果：
  - `training.semantic_supervision.enabled = true`
  - `semantic_weight_applied_ratio = 1.0`
  - `semantic_base_multiplier_mean = 1.17`
  - `semantic_package_multiplier_mean = 1.034`
- 说明：
  - semantic metadata
    已经不是只停留在 package/index；
    它确实进入了 optimization
    路径

## 四、overfit24 严格可比 A/B

### baseline
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_semanticplumb_baseline_round1_1/`
- validation step24：
  - `loss_total = 0.856916`
  - `loss_total_semantic_weighted = 0.856916`
  - `loss_waveform = 0.159986`
  - `loss_stft = 0.364732`
  - `loss_rms_guard = 0.021712`
  - `decoded_to_target_rms_ratio = 0.978607`

### semantic weighting
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_paired_parallel_overfit24_semanticweight_round1_1/`
- validation step24：
  - `loss_total = 0.854944`
  - `loss_total_semantic_weighted = 0.883594`
  - `loss_waveform = 0.162385`
  - `loss_stft = 0.364957`
  - `loss_rms_guard = 0.014582`
  - `decoded_to_target_rms_ratio = 0.996579`
  - `semantic_weight_applied_ratio = 1.0`
  - `semantic_base_multiplier_mean = 1.17`
  - `semantic_package_multiplier_mean = 1.034`

### 当前解释
- 这说明：
  - semantic weighting
    真的接通了
  - 而且对
    RMS guard /
    loudness match
    有正向影响
- 但同时：
  - `loss_waveform`
    略差
  - `loss_stft`
    基本持平略差
  - `loss_total_semantic_weighted`
    作为当前选择指标，
    也没有显示出“明确胜出”
- 因此它现在更像：
  - 一个已接通的 semantic bootstrap
  - 而不是已经证明能带来可听收益的
    成熟改动

## 五、validation training-sync export 与最小听审包

### export 目录
- baseline：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit24_semanticplumb_baseline_validation_trainingsync_round1_1/`
- semantic：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit24_semanticweight_validation_trainingsync_round1_1/`

### case 级 export 观察
- case107：
  - baseline
    `loss_total = 0.807132`
    / `decoded_to_target_rms_ratio = 0.965721`
  - semantic
    `loss_total = 0.802600`
    / `decoded_to_target_rms_ratio = 0.982048`
- case132：
  - baseline
    `loss_total = 0.906701`
    / `decoded_to_target_rms_ratio = 0.991493`
  - semantic
    `loss_total = 0.907289`
    / `decoded_to_target_rms_ratio = 1.011109`

### 最小听审包
- 目录：
  - `reports/audio/stage5_paired_parallel_overfit24_semanticweight_compare_quick_audit_20260325/`
- 文件顺序：
  - case107：
    - `source`
    - `target_aligned`
    - `baseline_decoded`
    - `semantic_decoded`
  - case132：
    - `source`
    - `target_aligned`
    - `baseline_decoded`
    - `semantic_decoded`

## 六、当前阶段判断
- 相比继续猜：
  - semantic weighting
    是不是略微更合理
- 当前更有价值的是直接听。
- 因为这条线现在已经具备：
  - 正确接线
  - 严格可比 baseline
  - 最小 training-sync 对照包
- 所以下一问不应再是：
  - 要不要再改一点 semantic bonus
- 而应是：
  - semantic variant
    是否第一次开始比 baseline
    更像 target

## 七、下一步
1. 优先听：
   - `reports/audio/stage5_paired_parallel_overfit24_semanticweight_compare_quick_audit_20260325/`
2. 只回答：
   - case107 / 132
     上，
     `semantic_decoded`
     是否比
     `baseline_decoded`
     更接近
     `target_aligned`
3. 若仍只是 pure buzz，
   则说明：
   - 仅靠当前这种
     package-level semantic weighting
     还不够，
   - 下一步就应继续推进
     更明确的
     design-state
     `e_evt`
     consumer，
     而不是在权重上微调。
