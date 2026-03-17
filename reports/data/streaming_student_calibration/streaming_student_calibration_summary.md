# Stage3 Streaming Student Calibration Asset Summary

- generated_at: 2026-03-17T11:29:02
- config_path: F:/proj_dev/tmp/workdir4/configs/streaming_student_stage_template.json
- split_dir: F:/proj_dev/tmp/workdir4/data_prep/round1_1/splits/hybrid_stratified_blocked
- asset_version: stage3_calibration_asset_v1

## Selection
- selected_record_count: 11
- selected_total_duration_sec: 135.964922
- target_duration_sec: 120.0
- max_records: 12

## Conditioning Contract
- speaker_embed_dim: 16
- geom_embed_dim: 8
- alpha_parameterization: global_scalar
- alpha_default_value: 1.0

## Coverage
- utterance_structure_type_counts: {"multi_clause_single_terminal": 5, "multi_terminal": 3, "other": 2, "single_clause_terminal": 1}
- final_terminal_type_counts: {"none": 4, "terminal_exclamation": 1, "terminal_period": 5, "terminal_question": 1}
- pool_membership_counts: {"challenge_proxy_core": 2, "challenge_proxy_relaxed": 3, "micro_pause_none_singleton_relaxed": 2, "micro_pause_none_singleton_strict": 1, "micro_singleton_anypunct_expansion": 2, "micro_singleton_anypunct_relaxed": 3, "short_pause_no_terminal": 2, "short_terminal_burst": 1, "structural_clause_ge4": 8, "structural_clause_ge4_no_final_terminal": 2, "structural_multi_terminal": 3, "structural_no_final_terminal": 4, "structural_question_exclaim": 2}
- covered_tags: ["clause:ge4", "content:lexical", "duration_bucket:long", "duration_bucket:mid", "duration_bucket:short", "final_terminal:none", "final_terminal:terminal_exclamation", "final_terminal:terminal_period", "final_terminal:terminal_question", "pause:multi", "pool:challenge_proxy_core", "pool:challenge_proxy_relaxed", "pool:micro_pause_none_singleton_strict", "pool:micro_singleton_anypunct_expansion", "pool:structural_clause_ge4", "pool:structural_clause_ge4_no_final_terminal", "pool:structural_multi_terminal", "pool:structural_question_exclaim", "special_duration_ceiling:False", "special_duration_ceiling:True", "special_proximity:high", "special_proximity:low", "special_proximity:mid", "structure:multi_clause_single_terminal", "structure:multi_terminal", "structure:other", "structure:single_clause_terminal", "terminal:present", "text_bucket:long", "text_bucket:mid", "text_bucket:short"]

## Artifacts
- selected_records_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/target_calibration_records.jsonl
- asset_template_path: F:/proj_dev/tmp/workdir4/data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_template.json

## Notes
- This stage only selects calibration records and writes a placeholder conditioning asset template.
- Current selection uses structural diversity already available in weak_event_hints and target_special_supervision sidecars.
- The output is a bootstrap asset scaffold, not a learned s_spk_target / s_geom_target / alpha estimate.
