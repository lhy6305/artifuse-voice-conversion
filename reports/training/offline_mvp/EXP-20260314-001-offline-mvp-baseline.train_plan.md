# offline MVP 训练计划

- experiment_id: EXP-20260314-001-offline-mvp-baseline
- dry_run: True
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
- z_art: [4, 457, 8]
- event_logits: [4, 457, 8]
- acoustic: [4, 457, 4]
- frame_mask: [4, 457]

## 状态
- status: dry_run_ready
