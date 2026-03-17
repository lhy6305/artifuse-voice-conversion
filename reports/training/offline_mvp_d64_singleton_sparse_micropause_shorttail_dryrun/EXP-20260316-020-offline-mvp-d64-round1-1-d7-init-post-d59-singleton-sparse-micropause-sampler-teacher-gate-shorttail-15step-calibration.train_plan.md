# offline MVP 训练计划

- experiment_id: EXP-20260316-020-offline-mvp-d64-round1-1-d7-init-post-d59-singleton-sparse-micropause-sampler-teacher-gate-shorttail-15step-calibration
- dry_run: True
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d64_round1_1_d7_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_shorttail_15step_smallscale_seeded_shuffle.json

## 时间
- started_at: 2026-03-16T13:58:36
- ended_at: 2026-03-16T13:58:38
- duration_sec: 1.580934

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
- target_batch_token_shape: [4, 34]
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
- priority_record_count: 19
- mode: priority_interleave
- active_until_step: 15
- priority_ratio: 0.25
- schedule_phases: [{'active_until_step': 10, 'priority_ratio': 0.25, 'priority_structure_types': [], 'exclude_structure_types': [], 'priority_pool_memberships': ['challenge_proxy_core', 'short_pause_no_terminal'], 'priority_record_ids': [], 'exclude_pool_memberships': []}, {'active_until_step': 15, 'priority_ratio': 0.75, 'priority_structure_types': [], 'exclude_structure_types': [], 'priority_pool_memberships': ['micro_pause_none_singleton_strict'], 'priority_record_ids': [], 'exclude_pool_memberships': [], 'required_within_special_duration_ceiling': True, 'required_utterance_structure_types': ['other']}]
- phase_priority_record_counts: [{'active_until_step': 10, 'priority_ratio': 0.25, 'priority_record_count': 19}, {'active_until_step': 15, 'priority_ratio': 0.75, 'priority_record_count': 8}]
- min_clause_count: 0
- required_within_special_duration_ceiling: None
- priority_structure_types: []
- min_special_proximity_score: 0.0
- max_special_proximity_score: 1.0
- required_final_terminal_types: []
- required_utterance_structure_types: []
- exclude_structure_types: []
- priority_pool_memberships: ['challenge_proxy_core', 'short_pause_no_terminal']
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
- num_steps: 15
- completed_steps: 0
- validation_interval: 5
- checkpoint_interval: 5
- initial_learning_rate: 0.00015
- learning_rate_schedule: {'enabled': False}
- teacher_consistency: {'enabled': True, 'teacher_checkpoint_path': 'reports/training/offline_mvp_d29_d26_init_d22_teacher_cross_anchor_consolidation_exp045/checkpoints/EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration.step10.pt', 'weight': 0.15, 'event_weight': 1.0, 'z_art_weight': 1.0, 'acoustic_weight': 0.0, 'fused_hidden_weight': 0.05, 'pool_memberships': ['challenge_proxy_core', 'short_pause_no_terminal'], 'schedule_phases': [{'active_until_step': 10, 'weight': 0.15, 'event_weight': 1.0, 'z_art_weight': 1.0, 'acoustic_weight': 0.0, 'fused_hidden_weight': 0.05, 'pool_memberships': ['challenge_proxy_core', 'short_pause_no_terminal'], 'teacher_checkpoint_path': 'reports/training/offline_mvp_d33_d7_init_d10_teacher_consistency_shortpause_fused_hidden_exp050/checkpoints/EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration.step10.pt', 'min_clause_count': 0, 'min_pause_boundary_count': 0, 'min_terminal_boundary_count': 0, 'required_within_special_duration_ceiling': None, 'min_special_proximity_score': 0.0, 'max_special_proximity_score': 1.0, 'required_final_terminal_types': [], 'required_utterance_structure_types': [], 'base_sample_weight': 1.0, 'proximity_weight_scale': 0.0, 'final_terminal_type_weight_overrides': {}, 'utterance_structure_type_weight_overrides': {}}, {'active_until_step': 15, 'weight': 0.15, 'event_weight': 1.0, 'z_art_weight': 1.0, 'acoustic_weight': 0.0, 'fused_hidden_weight': 0.05, 'pool_memberships': ['micro_pause_none_singleton_strict'], 'teacher_checkpoint_path': 'reports/training/offline_mvp_d29_d26_init_d22_teacher_cross_anchor_consolidation_exp045/checkpoints/EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration.step10.pt', 'min_clause_count': 0, 'min_pause_boundary_count': 0, 'min_terminal_boundary_count': 0, 'required_within_special_duration_ceiling': True, 'min_special_proximity_score': 0.0, 'max_special_proximity_score': 1.0, 'required_final_terminal_types': ['none'], 'required_utterance_structure_types': ['other'], 'base_sample_weight': 1.0, 'proximity_weight_scale': 0.0, 'final_terminal_type_weight_overrides': {}, 'utterance_structure_type_weight_overrides': {}}], 'teacher_checkpoint_paths': ['F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d29_d26_init_d22_teacher_cross_anchor_consolidation_exp045/checkpoints/EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration.step10.pt', 'F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d33_d7_init_d10_teacher_consistency_shortpause_fused_hidden_exp050/checkpoints/EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration.step10.pt']}
- sampler_mode: priority_interleave

## 最新 step 指标
- step: 0
- effective_learning_rate: 0.00015
- loss_total: 5.553953170776367
- target.loss_total: 2.738762855529785
- source.loss_total: 2.811028003692627
- grad_norm: 0.0
- checkpoint_path: None
- validation_enabled: True
- validation_runs: 0

## 状态
- status: dry_run_ready
