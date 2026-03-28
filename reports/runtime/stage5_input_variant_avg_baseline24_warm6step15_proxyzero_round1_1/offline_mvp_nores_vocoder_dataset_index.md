# Stage5 Input Variant Dataset

- generated_at: 2026-03-28T14:00:03
- mode: teacher_first_stage5_input_variant_dataset_v1
- source_dataset_index_path: F:/proj_dev/tmp/workdir4/reports/runtime/streaming_student_stage5_dataset_packages_avg_baseline24_warm6step15_contractv2_normfix_validation3_round1_2/streaming_student_stage5_dataset_index.json
- output_dir: F:/proj_dev/tmp/workdir4/reports/runtime/stage5_input_variant_avg_baseline24_warm6step15_proxyzero_round1_1
- train_package_count: 0
- validation_package_count: 3
- control_family_overrides: [{"family": "proxy_family", "mode": "zero", "targets": ["periodic.voiced_proxy", "periodic.energy_proxy", "noise.aperiodicity_proxy", "noise.event_presence_proxy", "noise.energy_change_proxy", "noise.energy_proxy"]}]

## Train Packages

## Validation Packages
- target::chapter3_3_firefly_162: F:/proj_dev/tmp/workdir4/reports/runtime/stage5_input_variant_avg_baseline24_warm6step15_proxyzero_round1_1/packages/validation/target_chapter3_3_firefly_162/train_targets/offline_mvp_nores_vocoder_train_targets.pt variant={"control_family_overrides": [{"family": "proxy_family", "mode": "zero", "targets": ["periodic.voiced_proxy", "periodic.energy_proxy", "noise.aperiodicity_proxy", "noise.event_presence_proxy", "noise.energy_change_proxy", "noise.energy_proxy"]}], "transform_summary": {"transformations": [], "control_family_overrides": [{"family": "proxy_family", "mode": "zero", "targets": []}]}, "source_package_path": "F:/proj_dev/tmp/workdir4/reports/runtime/streaming_student_stage5_dataset_packages_avg_baseline24_warm6step15_contractv2_normfix_validation3_round1_2/packages/validation/target__chapter3_3_firefly_162/train_targets/offline_mvp_nores_vocoder_train_targets.pt"}
- target::chapter3_3_firefly_138: F:/proj_dev/tmp/workdir4/reports/runtime/stage5_input_variant_avg_baseline24_warm6step15_proxyzero_round1_1/packages/validation/target_chapter3_3_firefly_138/train_targets/offline_mvp_nores_vocoder_train_targets.pt variant={"control_family_overrides": [{"family": "proxy_family", "mode": "zero", "targets": ["periodic.voiced_proxy", "periodic.energy_proxy", "noise.aperiodicity_proxy", "noise.event_presence_proxy", "noise.energy_change_proxy", "noise.energy_proxy"]}], "transform_summary": {"transformations": [], "control_family_overrides": [{"family": "proxy_family", "mode": "zero", "targets": []}]}, "source_package_path": "F:/proj_dev/tmp/workdir4/reports/runtime/streaming_student_stage5_dataset_packages_avg_baseline24_warm6step15_contractv2_normfix_validation3_round1_2/packages/validation/target__chapter3_3_firefly_138/train_targets/offline_mvp_nores_vocoder_train_targets.pt"}
- target::chapter3_4_firefly_106: F:/proj_dev/tmp/workdir4/reports/runtime/stage5_input_variant_avg_baseline24_warm6step15_proxyzero_round1_1/packages/validation/target_chapter3_4_firefly_106/train_targets/offline_mvp_nores_vocoder_train_targets.pt variant={"control_family_overrides": [{"family": "proxy_family", "mode": "zero", "targets": ["periodic.voiced_proxy", "periodic.energy_proxy", "noise.aperiodicity_proxy", "noise.event_presence_proxy", "noise.energy_change_proxy", "noise.energy_proxy"]}], "transform_summary": {"transformations": [], "control_family_overrides": [{"family": "proxy_family", "mode": "zero", "targets": []}]}, "source_package_path": "F:/proj_dev/tmp/workdir4/reports/runtime/streaming_student_stage5_dataset_packages_avg_baseline24_warm6step15_contractv2_normfix_validation3_round1_2/packages/validation/target__chapter3_4_firefly_106/train_targets/offline_mvp_nores_vocoder_train_targets.pt"}

## Notes
- This command rewrites Stage5 training packages by applying probe-style input-control transforms directly to package inputs.
- It is intended to bridge user-line diagnostics into a reusable training-dataset candidate without modifying the baseline training loop.
- Only zero/time_roll_half/time_shuffle are supported here because reference-backed replacements need external reference statistics and are probe-only.
