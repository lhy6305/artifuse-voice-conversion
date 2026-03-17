# Offline MVP No-Residual Vocoder Dataset Index

- generated_at: 2026-03-17T22:54:00
- timing: {"started_at": "2026-03-17T22:53:58", "ended_at": "2026-03-17T22:54:00", "duration_sec": 1.977267}
- selection_mode: file_order
- train_split_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked/target_train.jsonl
- validation_split_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked/target_validation.jsonl
- summary: {"train_package_count": 3, "validation_package_count": 1, "train": {"package_count": 3, "total_audio_duration_sec": 44.111951, "total_frame_count": 12153, "total_package_size_bytes": 26342076, "total_package_build_sec": 1.886347, "avg_package_build_sec": 0.628782, "avg_package_size_bytes": 8780692.0, "built_now_count": 3, "reused_existing_count": 0}, "validation": {"package_count": 1, "total_audio_duration_sec": 0.612993, "total_frame_count": 167, "total_package_size_bytes": 391145, "total_package_build_sec": 0.069947, "avg_package_build_sec": 0.069947, "avg_package_size_bytes": 391145.0, "built_now_count": 1, "reused_existing_count": 0}, "total_package_count": 4, "total_package_size_bytes": 26733221, "total_package_build_sec": 1.956294, "index_build_duration_sec": 1.977267}

## Train Packages
- record_id=target::archive_firefly_1 frame_count=3054 duration_sec=11.087982 package_size_bytes=6627341 package_build_sec=0.504602 package_status=built_now training_package_path=F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_throughput_probe_fileorder_round1_1/packages/train/target__archive_firefly_1/train_targets/offline_mvp_nores_vocoder_train_targets.pt
- record_id=target::archive_firefly_10 frame_count=4735 duration_sec=17.184989 package_size_bytes=10257954 package_build_sec=0.718386 package_status=built_now training_package_path=F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_throughput_probe_fileorder_round1_1/packages/train/target__archive_firefly_10/train_targets/offline_mvp_nores_vocoder_train_targets.pt
- record_id=target::archive_firefly_11 frame_count=4364 duration_sec=15.83898 package_size_bytes=9456781 package_build_sec=0.663359 package_status=built_now training_package_path=F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_throughput_probe_fileorder_round1_1/packages/train/target__archive_firefly_11/train_targets/offline_mvp_nores_vocoder_train_targets.pt

## Validation Packages
- record_id=target::chapter3_3_firefly_162 frame_count=167 duration_sec=0.612993 package_size_bytes=391145 package_build_sec=0.069947 package_status=built_now training_package_path=F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_throughput_probe_fileorder_round1_1/packages/validation/target__chapter3_3_firefly_162/train_targets/offline_mvp_nores_vocoder_train_targets.pt

## Notes
- This dataset index is a Stage5 package-level bridge built on top of the teacher-first contract path.
- Each package still contains proxy spectral/gate targets rather than a final waveform decoder objective.
- Current package generation may reload the teacher checkpoint per record, so this builder is a functional baseline rather than a throughput-optimized exporter.
