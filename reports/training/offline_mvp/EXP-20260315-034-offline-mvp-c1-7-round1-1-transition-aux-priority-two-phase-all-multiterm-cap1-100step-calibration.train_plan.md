# offline MVP 训练计划

- experiment_id: EXP-20260315-034-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-all-multiterm-cap1-100step-calibration
- dry_run: False
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_c1_7_round1_1_clause_transition_aux_priority_two_phase_all_multiterm_cap1_smallscale_100_seeded_shuffle.json

## 时间
- started_at: 2026-03-15T01:28:34
- ended_at: 2026-03-15T01:28:40
- duration_sec: 6.127002

## 数据
- manifest_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/manifests
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- split_strategy: materialized_split
- target_manifest_count: 666
- source_manifest_count: 537
- target_train_count: 592
- target_validation_count: 66
- target_special_eval_count: 8
- source_train_count: 483
- source_validation_count: 54
- dry_run_target_count: 4
- dry_run_source_count: 4
- target_batch_audio_shape: [4, 88200]
- target_batch_token_shape: [4, 69]
- target_batch_text_feature_shape: [4, 13]
- target_text_feature_version: b1_1_stats_v2
- source_batch_audio_shape: [4, 96000]
- vocab_size: 1369

## 模型门槛
- run_stage: small_scale_validation
- requires_small_scale_prerequisite: False
- prerequisite_experiment_id: None
- split_option_name: hybrid_stratified_blocked
- requires_r_res_disabled: True
- requires_text_for_training: True
- requires_text_for_runtime: False

## 可复现性
- seed: 20260314
- shuffle_train_records: True
- target_sampler_seed: 20260314
- source_sampler_seed: 20260315

## Targeted Sampling
- enabled: True
- priority_record_count: 185
- mode: priority_interleave
- active_until_step: 0
- priority_ratio: 0.0
- schedule_phases: [{'active_until_step': 25, 'priority_ratio': 0.75, 'priority_structure_types': [], 'exclude_structure_types': ['multi_terminal'], 'min_clause_count': 4, 'secondary_sampling': {'enabled': True, 'max_slots': 1, 'priority_structure_types': ['multi_terminal'], 'exclude_structure_types': [], 'exclude_primary_matches': False}}, {'active_until_step': 45, 'priority_ratio': 0.25, 'priority_structure_types': [], 'exclude_structure_types': [], 'min_clause_count': 4}]
- phase_priority_record_counts: [{'active_until_step': 25, 'priority_ratio': 0.75, 'priority_record_count': 234}, {'active_until_step': 45, 'priority_ratio': 0.25, 'priority_record_count': 185}]
- min_clause_count: 4
- priority_structure_types: []
- exclude_structure_types: []

## dry-run 前向形状
- source_z_art: [4, 598, 8]
- source_event_logits: [4, 598, 8]
- source_acoustic: [4, 598, 4]
- source_frame_mask: [4, 598]
- target_z_art: [4, 549, 8]
- target_event_logits: [4, 549, 8]
- target_acoustic: [4, 549, 4]
- target_frame_mask: [4, 549]

## 训练摘要
- num_steps: 100
- completed_steps: 100
- validation_interval: 10
- checkpoint_interval: 10
- sampler_mode: priority_interleave

## 最新 step 指标
- step: 100
- loss_total: 5.423484802246094
- target.loss_total: 2.722952127456665
- source.loss_total: 2.7005324363708496
- grad_norm: 7.772251605987549
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260315-034-offline-mvp-c1-7-round1-1-transition-aux-priority-two-phase-all-multiterm-cap1-100step-calibration.step100.pt
- validation_enabled: True
- validation_runs: 10

## 状态
- status: training_run_completed
