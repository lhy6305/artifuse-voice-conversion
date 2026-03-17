# offline MVP 训练计划

- experiment_id: EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration
- dry_run: False
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d29_round1_1_d26_init_d22_teacher_cross_anchor_consolidation_20step_smallscale_seeded_shuffle.json

## 时间
- started_at: 2026-03-15T18:34:29
- ended_at: 2026-03-15T18:34:33
- duration_sec: 3.382464

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
- target_batch_token_shape: [4, 36]
- target_batch_text_feature_shape: [4, 13]
- target_text_feature_version: b1_1_stats_v2
- target_weak_event_hints_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/c1_weak_event_hints/target_weak_event_hints.jsonl
- target_special_supervision_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/target_special_supervision/target_special_supervision_sidecar.jsonl
- source_batch_audio_shape: [4, 96000]
- vocab_size: 1369

## 模型门槛
- run_stage: small_scale_validation
- requires_small_scale_prerequisite: False
- prerequisite_experiment_id: None
- init_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d26_d7_init_d10_teacher_consolidation_teacher_consistency_shortpausegate_priority_exp043/checkpoints/EXP-20260315-043-offline-mvp-d26-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-shortpausegate-priority-20step-calibration.step20.pt
- split_option_name: hybrid_stratified_blocked
- requires_r_res_disabled: True
- requires_text_for_training: True
- requires_text_for_runtime: False

## 可复现性
- seed: 20260315
- shuffle_train_records: True
- target_sampler_seed: 20260315
- source_sampler_seed: 20260316

## Targeted Sampling
- enabled: True
- priority_record_count: 19
- mode: priority_interleave
- active_until_step: 20
- priority_ratio: 0.25
- schedule_phases: []
- phase_priority_record_counts: []
- min_clause_count: 0
- priority_structure_types: []
- exclude_structure_types: []
- priority_pool_memberships: ['challenge_proxy_core', 'short_pause_no_terminal']
- priority_record_ids: []
- exclude_pool_memberships: []

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
- num_steps: 20
- completed_steps: 20
- validation_interval: 10
- checkpoint_interval: 10
- initial_learning_rate: 0.00015
- learning_rate_schedule: {'enabled': False}
- teacher_consistency: {'enabled': True, 'teacher_checkpoint_path': 'F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d22_d7_init_d10_teacher_consolidation_teacher_consistency_exp039/checkpoints/EXP-20260315-039-offline-mvp-d22-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-30step-calibration.step30.pt', 'weight': 0.15, 'event_weight': 1.0, 'z_art_weight': 1.0, 'pool_memberships': ['challenge_proxy_core', 'short_pause_no_terminal']}
- sampler_mode: priority_interleave

## 最新 step 指标
- step: 20
- effective_learning_rate: 0.00015
- loss_total: 5.043759346008301
- target.loss_total: 2.659381628036499
- source.loss_total: 2.3768444061279297
- grad_norm: 12.538534164428711
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d29_d26_init_d22_teacher_cross_anchor_consolidation_exp045/checkpoints/EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration.step20.pt
- validation_enabled: True
- validation_runs: 2

## 状态
- status: training_run_completed
