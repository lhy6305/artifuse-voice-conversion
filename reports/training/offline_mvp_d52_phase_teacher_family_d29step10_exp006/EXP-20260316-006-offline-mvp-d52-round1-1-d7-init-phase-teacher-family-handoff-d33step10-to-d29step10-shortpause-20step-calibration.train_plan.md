# offline MVP 训练计划

- experiment_id: EXP-20260316-006-offline-mvp-d52-round1-1-d7-init-phase-teacher-family-handoff-d33step10-to-d29step10-shortpause-20step-calibration
- dry_run: False
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d52_round1_1_d7_init_phase_teacher_family_handoff_d33step10_to_d29step10_shortpause_20step_smallscale_seeded_shuffle.json

## 时间
- started_at: 2026-03-16T01:35:38
- ended_at: 2026-03-16T01:35:41
- duration_sec: 3.107514

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
- active_until_step: 20
- priority_ratio: 0.25
- schedule_phases: []
- phase_priority_record_counts: []
- min_clause_count: 0
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
- num_steps: 20
- completed_steps: 20
- validation_interval: 10
- checkpoint_interval: 10
- initial_learning_rate: 0.00015
- learning_rate_schedule: {'enabled': False}
- teacher_consistency: {'enabled': True, 'teacher_checkpoint_path': 'reports/training/offline_mvp_d29_d26_init_d22_teacher_cross_anchor_consolidation_exp045/checkpoints/EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration.step10.pt', 'weight': 0.15, 'event_weight': 1.0, 'z_art_weight': 1.0, 'acoustic_weight': 0.0, 'fused_hidden_weight': 0.0, 'pool_memberships': ['challenge_proxy_core', 'short_pause_no_terminal'], 'schedule_phases': [{'active_until_step': 10, 'weight': 0.15, 'event_weight': 1.0, 'z_art_weight': 1.0, 'acoustic_weight': 0.0, 'fused_hidden_weight': 0.05, 'pool_memberships': ['challenge_proxy_core', 'short_pause_no_terminal'], 'teacher_checkpoint_path': 'reports/training/offline_mvp_d33_d7_init_d10_teacher_consistency_shortpause_fused_hidden_exp050/checkpoints/EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration.step10.pt', 'min_special_proximity_score': 0.0, 'max_special_proximity_score': 1.0, 'required_final_terminal_types': [], 'required_utterance_structure_types': [], 'base_sample_weight': 1.0, 'proximity_weight_scale': 0.0, 'final_terminal_type_weight_overrides': {}, 'utterance_structure_type_weight_overrides': {}}, {'active_until_step': 20, 'weight': 0.15, 'event_weight': 1.0, 'z_art_weight': 1.0, 'acoustic_weight': 0.0, 'fused_hidden_weight': 0.0, 'pool_memberships': ['challenge_proxy_core', 'short_pause_no_terminal'], 'teacher_checkpoint_path': 'reports/training/offline_mvp_d29_d26_init_d22_teacher_cross_anchor_consolidation_exp045/checkpoints/EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration.step10.pt', 'min_special_proximity_score': 0.0, 'max_special_proximity_score': 1.0, 'required_final_terminal_types': [], 'required_utterance_structure_types': [], 'base_sample_weight': 1.0, 'proximity_weight_scale': 0.0, 'final_terminal_type_weight_overrides': {}, 'utterance_structure_type_weight_overrides': {}}], 'teacher_checkpoint_paths': ['F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d29_d26_init_d22_teacher_cross_anchor_consolidation_exp045/checkpoints/EXP-20260315-045-offline-mvp-d29-round1-1-d26-init-d22-teacher-cross-anchor-consolidation-20step-calibration.step10.pt', 'F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d33_d7_init_d10_teacher_consistency_shortpause_fused_hidden_exp050/checkpoints/EXP-20260315-050-offline-mvp-d33-round1-1-d7-init-d10-teacher-consistency-shortpausegate-fused-hidden-20step-calibration.step10.pt']}
- sampler_mode: priority_interleave

## 最新 step 指标
- step: 20
- effective_learning_rate: 0.00015
- loss_total: 4.942955493927002
- target.loss_total: 2.5130391120910645
- source.loss_total: 2.4276695251464844
- grad_norm: 8.461602210998535
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d52_phase_teacher_family_d29step10_exp006/checkpoints/EXP-20260316-006-offline-mvp-d52-round1-1-d7-init-phase-teacher-family-handoff-d33step10-to-d29step10-shortpause-20step-calibration.step20.pt
- validation_enabled: True
- validation_runs: 2

## 状态
- status: training_run_completed
