# offline MVP 训练计划

- experiment_id: DRYRUN-20260316-d62-d22-singleton-latepulse
- dry_run: True
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d62_round1_1_d7_init_d10_teacher_consolidation_teacher_consistency_singleton_sparse_latepulse_30step_smallscale_seeded_shuffle.json

## 时间
- started_at: 2026-03-16T13:36:02
- ended_at: 2026-03-16T13:36:04
- duration_sec: 1.563958

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
- target_batch_token_shape: [4, 51]
- target_batch_text_feature_shape: [4, 13]
- target_text_feature_version: b1_1_stats_v2
- target_weak_event_hints_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/c1_weak_event_hints/target_weak_event_hints.jsonl
- target_special_supervision_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/target_special_supervision/target_special_supervision_sidecar.jsonl
- source_batch_audio_shape: [4, 57600]
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
- seed: 20260316
- shuffle_train_records: True
- target_sampler_seed: 20260316
- source_sampler_seed: 20260317

## Targeted Sampling
- enabled: True
- priority_record_count: 16
- mode: priority_interleave
- active_until_step: 30
- priority_ratio: 0.25
- schedule_phases: [{'active_until_step': 20, 'priority_ratio': 0.25, 'priority_structure_types': [], 'exclude_structure_types': [], 'priority_pool_memberships': ['challenge_proxy_core'], 'priority_record_ids': [], 'exclude_pool_memberships': []}, {'active_until_step': 30, 'priority_ratio': 0.5, 'priority_structure_types': [], 'exclude_structure_types': [], 'priority_pool_memberships': ['micro_pause_none_singleton_strict'], 'priority_record_ids': [], 'exclude_pool_memberships': [], 'required_within_special_duration_ceiling': True, 'required_utterance_structure_types': ['other']}]
- phase_priority_record_counts: [{'active_until_step': 20, 'priority_ratio': 0.25, 'priority_record_count': 16}, {'active_until_step': 30, 'priority_ratio': 0.5, 'priority_record_count': 8}]
- min_clause_count: 0
- required_within_special_duration_ceiling: None
- priority_structure_types: []
- min_special_proximity_score: 0.0
- max_special_proximity_score: 1.0
- required_final_terminal_types: []
- required_utterance_structure_types: []
- exclude_structure_types: []
- priority_pool_memberships: ['challenge_proxy_core']
- priority_record_ids: []
- exclude_pool_memberships: []

## dry-run 前向形状
- source_z_art: [4, 358, 8]
- source_event_logits: [4, 358, 8]
- source_acoustic: [4, 358, 4]
- source_frame_mask: [4, 358]
- target_z_art: [4, 549, 8]
- target_event_logits: [4, 549, 8]
- target_acoustic: [4, 549, 4]
- target_frame_mask: [4, 549]

## 训练摘要
- num_steps: 30
- completed_steps: 0
- validation_interval: 10
- checkpoint_interval: 10
- initial_learning_rate: 0.00015
- learning_rate_schedule: {'enabled': False}
- teacher_consistency: {'enabled': True, 'teacher_checkpoint_path': 'reports/training/offline_mvp_d10_special_proxy_core_clause_ge4_late_handoff_zart_influence/checkpoints/EXP-20260315-026-offline-mvp-d10-round1-1-special-proxy-core-clause-ge4-late-handoff-zart-influence-100step-calibration.step100.pt', 'weight': 0.15, 'event_weight': 1.0, 'z_art_weight': 1.0, 'pool_memberships': ['challenge_proxy_core'], 'teacher_checkpoint_paths': ['F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d10_special_proxy_core_clause_ge4_late_handoff_zart_influence/checkpoints/EXP-20260315-026-offline-mvp-d10-round1-1-special-proxy-core-clause-ge4-late-handoff-zart-influence-100step-calibration.step100.pt'], 'schedule_phases': []}
- sampler_mode: priority_interleave

## 最新 step 指标
- step: 0
- effective_learning_rate: 0.00015
- loss_total: 5.653940677642822
- target.loss_total: 2.8388071060180664
- source.loss_total: 2.811028003692627
- grad_norm: 0.0
- checkpoint_path: None
- validation_enabled: True
- validation_runs: 0

## 状态
- status: dry_run_ready
