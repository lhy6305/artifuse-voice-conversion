# 518 Stage5 Consumer Handoff Localization For Energypeak Stage3 Winner Report

## Summary
- This round kept the current deterministic Stage3 winner fixed:
  - `reports/training/ss_detpitch_energypeak_s2_step1/checkpoints/ss_detpitch_energypeak_s2_step1.step1.pt`
- No Stage3 training was continued.
- Instead, this round localized the current Stage5 no-res consumer failure using:
  - waveform handoff probes
  - waveform decoder structure probe
- The result is now more specific than the earlier decoded fail-fast result:
  - the current failure is already present before predicted activity gating
  - the current failure is not mainly created by the residual-shape branch
  - the strongest Stage5-local amplification still sits at `decoder_hidden -> waveform_decoder_base_logits`

## Probes Run

### tv8 waveform handoff probe
- Output:
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_tv8_round1_1/stage5_waveform_handoff_probe.json`
- Input dataset:
  - `reports/runtime/streaming_student_stage5_dataset_energypeak_s2_step1_tv8/streaming_student_stage5_dataset_index.json`

### tv8 waveform decoder structure probe
- Output:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_streaming_student_energypeak_tv8_round1_1/stage5_waveform_decoder_structure_probe.json`
- Input dataset:
  - `reports/runtime/streaming_student_stage5_dataset_energypeak_s2_step1_tv8/streaming_student_stage5_dataset_index.json`

### se8 waveform handoff probe
- Output:
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_se8_round1_1/stage5_waveform_handoff_probe.json`
- Input dataset:
  - `reports/runtime/streaming_student_stage5_dataset_energypeak_s2_step1_se8/streaming_student_stage5_dataset_index.json`

## Handoff Findings

### tv8
- All three reconstruction routes remain fully rejected:
  - `decoded_no_gate`: `8/8 auto_reject`
  - `decoded_pre_ola_gate`: `8/8 auto_reject`
  - `decoded_post_ola_gate`: `8/8 auto_reject`
- Probe diagnosis:
  - `buzz_before_predicted_activity_gate = true`
  - `predicted_activity_gate_changes_auto_reject_status = false`
  - `primary_localization = buzz_present_by_waveform_frames_before_gate`
- Representative aggregate metrics:
  - `decoded_no_gate decoded_frame_template_cosine_mean = 0.979705`
  - `decoded_no_gate spectral_centroid_gap_hz = 9471.169922`
  - `decoded_no_gate spectral_high_band_energy_ratio_gap = 0.717442`
  - `decoded_post_ola_gate decoded_frame_template_cosine_mean = 0.979666`
  - `decoded_post_ola_gate spectral_centroid_gap_hz = 9375.224609`
  - `decoded_post_ola_gate spectral_high_band_energy_ratio_gap = 0.709875`

### se8
- The same route-level conclusion repeats on special_eval:
  - `decoded_no_gate`: `8/8 auto_reject`
  - `decoded_pre_ola_gate`: `8/8 auto_reject`
  - `decoded_post_ola_gate`: `8/8 auto_reject`
- Probe diagnosis is unchanged:
  - `buzz_before_predicted_activity_gate = true`
  - `predicted_activity_gate_changes_auto_reject_status = false`
  - `primary_localization = buzz_present_by_waveform_frames_before_gate`

## Structure Findings

### Baseline Collapse Localization
- `tv8` structure probe baseline summary:
  - `fused_hidden_template_cosine_mean = 0.984966`
  - `waveform_frames_template_cosine_mean = 0.985838`
  - `decoded_frames_template_cosine_mean = 0.979666`
  - `fused_hidden_adjacent_cosine_mean = 0.999636`
  - `waveform_frames_adjacent_cosine_mean = 0.999706`
- Baseline decoder-collapse diagnosis:
  - `collapse_not_localized_to_waveform_decoder`
- Interpretation:
  - temporal collapse is already largely present by `fused_hidden`
  - the waveform decoder is not introducing a fresh late-stage tanh-only collapse

### Upstream Coupling Localization
- The strongest Stage5-local control distortion still occurs at:
  - `decoder_hidden -> waveform_decoder_base_logits`
- Key metrics:
  - `decoder_to_base_logits_voicing_corr_jump = -0.833975`
  - `decoder_to_base_logits_abs_aper_corr_jump = 0.502128`
  - `decoder_to_base_logits_abs_aper_energy_product_corr_jump = 0.353305`
  - `strongest_transition = decoder_to_base_logits`
  - `diagnosis = decoder_hidden_to_base_logits_is_main_coupling_amplifier`
- Interpretation:
  - even when upstream hidden states still carry some energy and APER structure, the base-logits projection amplifies the wrong coupling direction and pushes the final waveform path deeper into the buzz family

### Projection Geometry Localization
- Baseline geometry summary:
  - `fused_hidden_effective_rank_fraction = 0.020055`
  - `waveform_decoder_base_logits_effective_rank_fraction = 0.003353`
  - `decoder_to_base_logits_effective_rank_drop = 0.016702`
  - `decoder_to_base_logits_top1_variance_jump = 0.029384`
  - `decoder_to_base_logits_template_distance_drop = -0.575413`
  - `strongest_transition = decoder_to_base_logits`
  - `diagnosis = decoder_hidden_to_base_logits_is_main_geometry_collapse`
- Interpretation:
  - the current Stage5 consumer is not only over-templated before waveform reconstruction
  - it also becomes even lower-rank at the base-logits projection

### Residual-Shape Reading
- `waveform_decoder_base_logits_only` remains effectively the baseline route:
  - `mean_waveform_mean_abs_delta_vs_baseline = 0.0`
- `waveform_residual_shape_only` does not expose an alternative speech-like route:
  - `mean_decoded_frame_template_cosine_mean = 0.0`
- Therefore the active failure is not primarily caused by the residual-shape injection branch.

## Decision
- The current Stage3 winner remains valid as the packet-facing reference.
- The current Stage5 no-res consumer remains blocked.
- The next probe should not return to Stage3 continuation.
- The immediate Stage5 next step should target the `decoder_hidden -> waveform_decoder_base_logits` path, not predicted activity gating and not residual-shape-only hypotheses.

## Recommended Next Action
- Use the current fixed Stage3 winner as input and run a Stage5 consumer-side probe that directly targets base-logits projection behavior.
- Good next candidates are:
  - an existing Stage5 checkpoint family with branch-condition adaptation if one is already available
  - or a minimal Stage5 decoder-side intervention specifically around base-logits coupling and low-rank collapse

## Key Artifacts
- Stage3 winner:
  - `reports/training/ss_detpitch_energypeak_s2_step1/checkpoints/ss_detpitch_energypeak_s2_step1.step1.pt`
- Stage5 package bridges:
  - `reports/runtime/streaming_student_stage5_dataset_energypeak_s2_step1_tv8/streaming_student_stage5_dataset_index.json`
  - `reports/runtime/streaming_student_stage5_dataset_energypeak_s2_step1_se8/streaming_student_stage5_dataset_index.json`
- Handoff probes:
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_tv8_round1_1/stage5_waveform_handoff_probe.json`
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_se8_round1_1/stage5_waveform_handoff_probe.json`
- Structure probe:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_streaming_student_energypeak_tv8_round1_1/stage5_waveform_decoder_structure_probe.json`
