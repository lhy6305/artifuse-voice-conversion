# offline MVP 训练计划

- experiment_id: EXP-20260315-022-offline-mvp-d6-round1-1-special-proxy-core-clause-ge4-early-handoff-zsmooth-decay-100step-calibration
- dry_run: False
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_d6_round1_1_special_proxy_core_clause_ge4_early_handoff_zsmooth_decay_smallscale_100_seeded_shuffle.json

## 时间
- started_at: 2026-03-15T14:12:00
- ended_at: 2026-03-15T14:12:08
- duration_sec: 7.286114

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
- target_batch_token_shape: [4, 44]
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
- active_until_step: 0
- priority_ratio: 0.0
- schedule_phases: [{'active_until_step': 20, 'priority_ratio': 0.5, 'priority_structure_types': [], 'exclude_structure_types': [], 'priority_pool_memberships': ['challenge_proxy_core'], 'exclude_pool_memberships': [], 'secondary_sampling': {'enabled': True, 'max_slots': 1, 'priority_structure_types': [], 'exclude_structure_types': [], 'priority_pool_memberships': ['structural_clause_ge4'], 'exclude_pool_memberships': [], 'exclude_primary_matches': True}}, {'active_until_step': 60, 'priority_ratio': 0.25, 'priority_structure_types': [], 'exclude_structure_types': [], 'priority_pool_memberships': ['challenge_proxy_core'], 'exclude_pool_memberships': []}]
- phase_priority_record_counts: [{'active_until_step': 20, 'priority_ratio': 0.5, 'priority_record_count': 201}, {'active_until_step': 60, 'priority_ratio': 0.25, 'priority_record_count': 16}]
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
- num_steps: 100
- completed_steps: 100
- validation_interval: 10
- checkpoint_interval: 10
- sampler_mode: priority_interleave

## 最新 step 指标
- step: 100
- loss_total: 5.347645282745361
- target.loss_total: 2.57372784614563
- source.loss_total: 2.7739174365997314
- grad_norm: 5.518606185913086
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp_d6_special_proxy_core_clause_ge4_early_handoff_zsmooth_decay_exp022/checkpoints/EXP-20260315-022-offline-mvp-d6-round1-1-special-proxy-core-clause-ge4-early-handoff-zsmooth-decay-100step-calibration.step100.pt
- validation_enabled: True
- validation_runs: 10

## 状态
- status: training_run_completed
