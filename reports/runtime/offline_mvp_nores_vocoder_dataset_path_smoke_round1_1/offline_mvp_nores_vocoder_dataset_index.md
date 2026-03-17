# Offline MVP No-Residual Vocoder Dataset Index

- generated_at: 2026-03-17T22:46:02
- selection_mode: shortest_duration
- train_split_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked/target_train.jsonl
- validation_split_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked/target_validation.jsonl
- summary: {"train_package_count": 2, "validation_package_count": 1}

## Train Packages
- record_id=target::chapter3_22_firefly_105 frame_count=61 duration_sec=0.229002 training_package_path=F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_path_smoke_round1_1/packages/train/target__chapter3_22_firefly_105/train_targets/offline_mvp_nores_vocoder_train_targets.pt
- record_id=target::chapter3_17_firefly_138 frame_count=107 duration_sec=0.396009 training_package_path=F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_path_smoke_round1_1/packages/train/target__chapter3_17_firefly_138/train_targets/offline_mvp_nores_vocoder_train_targets.pt

## Validation Packages
- record_id=target::chapter3_3_firefly_162 frame_count=167 duration_sec=0.612993 training_package_path=F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_dataset_path_smoke_round1_1/packages/validation/target__chapter3_3_firefly_162/train_targets/offline_mvp_nores_vocoder_train_targets.pt

## Notes
- This dataset index is a Stage5 package-level bridge built on top of the teacher-first contract path.
- Each package still contains proxy spectral/gate targets rather than a final waveform decoder objective.
- Current package generation may reload the teacher checkpoint per record, so this builder is a functional baseline rather than a throughput-optimized exporter.
