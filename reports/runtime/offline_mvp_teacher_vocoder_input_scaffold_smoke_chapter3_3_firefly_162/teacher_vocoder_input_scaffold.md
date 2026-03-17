# Offline MVP Teacher Vocoder Input Scaffold

- generated_at: 2026-03-17T22:07:33
- contract_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_teacher_downstream_contract_smoke_chapter3_3_firefly_162/teacher_downstream_control_contract.pt
- scaffold_version: offline_teacher_vocoder_input_scaffold_v1
- frame_count: 167
- periodic_branch_feature_dim: 35
- noise_branch_feature_dim: 29
- available_controls: {"z_art_dim": 8, "event_dim": 8, "speaker_dim": 16, "geom_dim": 8}
- missing_design_keys: {"periodic_branch": ["f0_hz"], "noise_branch": ["r_res"], "global": ["final_vocoder_waveform"]}

## Notes
- This scaffold is a consumer-side adapter for the current teacher-first contract, not a real vocoder implementation.
- periodic_branch_features uses voiced_proxy and energy_proxy instead of final f0_hz/vuv/E semantics.
- noise_branch_features uses aperiodicity_proxy and event_probs, but r_res remains unavailable in the current teacher path.
