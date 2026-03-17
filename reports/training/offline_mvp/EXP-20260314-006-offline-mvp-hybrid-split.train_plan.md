# offline MVP 训练计划

- experiment_id: EXP-20260314-006-offline-mvp-hybrid-split
- dry_run: False
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_template.json

## 时间
- started_at: 2026-03-14T16:15:21
- ended_at: 2026-03-14T16:15:22
- duration_sec: 0.714648

## 数据
- manifest_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/splits/hybrid_stratified_blocked
- split_strategy: materialized_split
- target_manifest_count: 624
- source_manifest_count: 537
- target_train_count: 554
- target_validation_count: 62
- target_special_eval_count: 8
- source_train_count: 483
- source_validation_count: 54
- dry_run_target_count: 4
- dry_run_source_count: 4
- target_batch_audio_shape: [4, 88200]
- target_batch_token_shape: [4, 67]
- source_batch_audio_shape: [4, 73440]
- vocab_size: 1348

## 模型门槛
- run_stage: small_scale_validation
- requires_small_scale_prerequisite: False
- prerequisite_experiment_id: None
- split_option_name: hybrid_stratified_blocked
- requires_r_res_disabled: True
- requires_text_for_training: True
- requires_text_for_runtime: False

## dry-run 前向形状
- source_z_art: [4, 457, 8]
- source_event_logits: [4, 457, 8]
- source_acoustic: [4, 457, 4]
- source_frame_mask: [4, 457]
- target_z_art: [4, 549, 8]
- target_event_logits: [4, 549, 8]
- target_acoustic: [4, 549, 4]
- target_frame_mask: [4, 549]

## 训练摘要
- num_steps: 3
- completed_steps: 3
- validation_interval: 1
- checkpoint_interval: 1

## 最新 step 指标
- step: 3
- loss_total: 55.63977813720703
- target.loss_total: 22.105615615844727
- source.loss_total: 33.53416442871094
- grad_norm: 34.372535705566406
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-006-offline-mvp-hybrid-split.step3.pt
- validation_enabled: True
- validation_runs: 3

## 状态
- status: training_run_completed
