# offline MVP 训练计划

- experiment_id: EXP-20260314-002-offline-mvp-step1
- dry_run: False
- config_path: F:/proj_dev/tmp/workdir4/configs/offline_mvp_train_template.json

## 数据
- manifest_dir: F:/proj_dev/tmp/workdir4/data_prep/round1/manifests
- target_manifest_count: 624
- source_manifest_count: 537
- dry_run_target_count: 4
- dry_run_source_count: 4
- target_batch_audio_shape: [4, 88200]
- target_batch_token_shape: [4, 67]
- source_batch_audio_shape: [4, 73440]
- vocab_size: 1384

## 模型门槛
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

## step 指标
- loss_total: 51.73610305786133
- target.loss_total: 15.529247283935547
- source.loss_total: 36.20685577392578
- grad_norm: 28.910484313964844
- checkpoint_path: F:/proj_dev/tmp/workdir4/reports/training/offline_mvp/checkpoints/EXP-20260314-002-offline-mvp-step1.step1.pt

## 状态
- status: single_step_completed
