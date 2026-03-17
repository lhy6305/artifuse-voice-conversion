# offline MVP 训练计划

- experiment_id: EXP-20260315-040-offline-mvp-d23-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-relaxedgate-30step-calibration
- dry_run: False
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d23_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_relaxedgate_smallscale_30_seeded_shuffle.json

## 时间
- started_at: 2026-03-15T18:01:29
- ended_at: 2026-03-15T18:01:33
- duration_sec: 4.097901

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
- target_batch_token_shape: [4, 33]
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
- init_checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d7_special_proxy_core_clause_ge4_early_handoff_zart_influence_exp023/checkpoints/EXP-20260315-023-offline-mvp-d7-round1-1-special-proxy-core-clause-ge4-early-handoff-zart-influence-100step-calibration.step100.pt
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
- priority_record_count: 16
- mode: priority_interleave
- active_until_step: 30
- priority_ratio: 0.25
- schedule_phases: []
- phase_priority_record_counts: []
- min_clause_count: 0
- priority_structure_types: []
- exclude_structure_types: []
- priority_pool_memberships: ['challenge_proxy_core']
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
- num_steps: 30
- completed_steps: 30
- validation_interval: 10
- checkpoint_interval: 10
- initial_learning_rate: 0.00015
- learning_rate_schedule: {'enabled': False}
- teacher_consistency: {'enabled': True, 'teacher_checkpoint_path': 'F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d10_special_proxy_core_clause_ge4_late_handoff_zart_influence/checkpoints/EXP-20260315-026-offline-mvp-d10-round1-1-special-proxy-core-clause-ge4-late-handoff-zart-influence-100step-calibration.step100.pt', 'weight': 0.15, 'event_weight': 1.0, 'z_art_weight': 1.0, 'pool_memberships': ['challenge_proxy_core', 'challenge_proxy_relaxed']}
- sampler_mode: priority_interleave

## 最新 step 指标
- step: 30
- effective_learning_rate: 0.00015
- loss_total: 4.776095867156982
- target.loss_total: 2.307600259780884
- source.loss_total: 2.410416603088379
- grad_norm: 15.472813606262207
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d23_d7_init_d10_teacher_consolidation_teacher_consistency_relaxedgate_exp040/checkpoints/EXP-20260315-040-offline-mvp-d23-round1-1-d7-init-d10-teacher-consolidation-teacher-consistency-relaxedgate-30step-calibration.step30.pt
- validation_enabled: True
- validation_runs: 3

## 状态
- status: training_run_completed
