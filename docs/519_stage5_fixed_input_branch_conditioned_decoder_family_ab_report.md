# 519 Stage5 Fixed-Input Branch-Conditioned Decoder Family AB Report

## Summary
- This round kept the current deterministic Stage3 winner fixed:
  - `reports/training/ss_detpitch_energypeak_s2_step1/checkpoints/ss_detpitch_energypeak_s2_step1.step1.pt`
- No Stage3 training was continued.
- Instead, this round compared two already-trained Stage5 decoder-side families on the same fixed `tv8` synthetic Stage5 packages:
  - plain `branchcondadapter`
  - `fusionbranchmeancontrast_branchcond`
- Both families remain blocked:
  - `8/8 auto_reject`
  - same `buzz_present_by_waveform_frames_before_gate` localization
- The better of the two is `fusionbranchmeancontrast_branchcond`, but it still does not open the decoded route.
- The new structure probes keep the main localization unchanged:
  - `decoder_hidden -> waveform_decoder_base_logits` is still the main coupling amplifier
  - `decoder_hidden -> waveform_decoder_base_logits` is still the main geometry-collapse site
- Therefore the next Stage5 move should not be another hidden-side branch-conditioned adapter family.

## Probes Run

### Fixed-input plain branchcondadapter on current Stage3 winner
- Audio export:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_branchcond_round1_1/nores_vocoder_audio_export.json`
- Waveform handoff probe:
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_tv8_branchcond_round1_1/stage5_waveform_handoff_probe.json`
- Waveform decoder structure probe:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_streaming_student_energypeak_tv8_branchcond_round1_1/stage5_waveform_decoder_structure_probe.json`

### Fixed-input fusionbranchmeancontrast_branchcond on current Stage3 winner
- Audio export:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionbranchcond_round1_1/nores_vocoder_audio_export.json`
- Waveform handoff probe:
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_tv8_fusionbranchcond_round1_1/stage5_waveform_handoff_probe.json`
- Waveform decoder structure probe:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_streaming_student_energypeak_tv8_fusionbranchcond_round1_1/stage5_waveform_decoder_structure_probe.json`

### Fixed-input baseline reference
- Audio export:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_round1_1/nores_vocoder_audio_export.json`
- Waveform handoff probe:
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_tv8_round1_1/stage5_waveform_handoff_probe.json`
- Waveform decoder structure probe:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_streaming_student_energypeak_tv8_round1_1/stage5_waveform_decoder_structure_probe.json`

## Handoff Comparison

### Route status
- All three fixed-input routes remain blocked on `tv8`:
  - baseline: `8/8 auto_reject`
  - plain `branchcondadapter`: `8/8 auto_reject`
  - `fusionbranchmeancontrast_branchcond`: `8/8 auto_reject`
- All three still diagnose:
  - `buzz_before_predicted_activity_gate = true`
  - `predicted_activity_gate_changes_auto_reject_status = false`
  - `primary_localization = buzz_present_by_waveform_frames_before_gate`

### Aggregate decoded_post_ola_gate comparison
- Baseline:
  - `decoded_frame_template_cosine_mean = 0.979666`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.776052`
  - `spectral_centroid_gap_hz = 9375.224609`
  - `spectral_high_band_energy_ratio_gap = 0.709875`
- Plain `branchcondadapter`:
  - `decoded_frame_template_cosine_mean = 0.996371`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.915846`
  - `spectral_centroid_gap_hz = 5732.299316`
  - `spectral_high_band_energy_ratio_gap = 0.56265`
- `fusionbranchmeancontrast_branchcond`:
  - `decoded_frame_template_cosine_mean = 0.988974`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.877519`
  - `spectral_centroid_gap_hz = 3139.213867`
  - `spectral_high_band_energy_ratio_gap = 0.485989`

### Reading
- Plain `branchcondadapter` improves brightness and RMS-following relative to baseline, but it also becomes even more template-collapsed.
- `fusionbranchmeancontrast_branchcond` keeps the same failure family, but it is materially less bright than both baseline and plain `branchcondadapter`.
- Even so, `fusionbranchmeancontrast_branchcond` still stays far inside the buzz basin:
  - route still `8/8 auto_reject`
  - pre-gate failure remains unchanged

## Structure Comparison

### Baseline
- Collapse summary:
  - `fused_hidden_template_cosine_mean = 0.984966`
  - `waveform_frames_template_cosine_mean = 0.985838`
  - `decoded_frames_template_cosine_mean = 0.979666`
  - `diagnosis = collapse_not_localized_to_waveform_decoder`
- Coupling localization:
  - `diagnosis = decoder_hidden_to_base_logits_is_main_coupling_amplifier`
  - `decoder_to_base_logits_voicing_corr_jump = -0.833975`
  - `decoder_to_base_logits_abs_aper_corr_jump = 0.502128`
  - `decoder_to_base_logits_abs_aper_energy_product_corr_jump = 0.353305`
- Geometry localization:
  - `diagnosis = decoder_hidden_to_base_logits_is_main_geometry_collapse`
  - `decoder_to_base_logits_effective_rank_drop = 0.016702`

### Plain branchcondadapter
- Collapse summary worsens sharply:
  - `fused_hidden_template_cosine_mean = 0.99619`
  - `waveform_frames_template_cosine_mean = 0.998975`
  - `decoded_frames_template_cosine_mean = 0.996371`
- Coupling localization remains the same family:
  - `diagnosis = decoder_hidden_to_base_logits_is_main_coupling_amplifier`
  - `strongest_transition = decoder_to_base_logits`
- Geometry localization remains the same family:
  - `diagnosis = decoder_hidden_to_base_logits_is_main_geometry_collapse`
  - `decoder_to_base_logits_effective_rank_drop = 0.020164`

### fusionbranchmeancontrast_branchcond
- Collapse is less severe than plain `branchcondadapter`, but still much worse than baseline at waveform and decoded stages:
  - `fused_hidden_template_cosine_mean = 0.983032`
  - `waveform_frames_template_cosine_mean = 0.996624`
  - `decoded_frames_template_cosine_mean = 0.988974`
- Coupling localization still stays at the same transition:
  - `diagnosis = decoder_hidden_to_base_logits_is_main_coupling_amplifier`
  - `strongest_transition = decoder_to_base_logits`
- Geometry localization still stays at the same transition:
  - `diagnosis = decoder_hidden_to_base_logits_is_main_geometry_collapse`
  - `decoder_to_base_logits_effective_rank_drop = 0.021324`

### Shared structural lesson
- In all three families:
  - `waveform_decoder_base_logits_only` is effectively the baseline route
  - `waveform_residual_shape_only` does not reveal a usable speech-like alternate path
- Therefore these hidden-side branch-conditioned families do not change the active bottleneck.

## Decision
- Keep the current deterministic Stage3 winner unchanged as the packet-facing reference.
- Do not reopen Stage3 continuation.
- Do not continue plain `branchcondadapter` as the next Stage5 move.
- Do not continue `fusionbranchmeancontrast_branchcond` as the next Stage5 move either.
- If a decoder-side Stage5 probe continues from here, it should target the base-logits or frame-space handoff path more directly instead of trying another hidden-side branch-conditioned adapter family.

## Recommended Next Action
- Use the same fixed Stage3 winner and move to a more direct Stage5 consumer-side intervention around:
  - `decoder_hidden -> waveform_decoder_base_logits`
  - or a frame-space path that bypasses the same hidden-side adapter pattern

## Key Artifacts
- Stage3 winner:
  - `reports/training/ss_detpitch_energypeak_s2_step1/checkpoints/ss_detpitch_energypeak_s2_step1.step1.pt`
- Fixed-input baseline:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_round1_1/nores_vocoder_audio_export.json`
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_tv8_round1_1/stage5_waveform_handoff_probe.json`
  - `reports/runtime/stage5_waveform_decoder_structure_probe_streaming_student_energypeak_tv8_round1_1/stage5_waveform_decoder_structure_probe.json`
- Fixed-input plain branchcondadapter:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_branchcond_round1_1/nores_vocoder_audio_export.json`
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_tv8_branchcond_round1_1/stage5_waveform_handoff_probe.json`
  - `reports/runtime/stage5_waveform_decoder_structure_probe_streaming_student_energypeak_tv8_branchcond_round1_1/stage5_waveform_decoder_structure_probe.json`
- Fixed-input fusionbranchmeancontrast_branchcond:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionbranchcond_round1_1/nores_vocoder_audio_export.json`
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_tv8_fusionbranchcond_round1_1/stage5_waveform_handoff_probe.json`
  - `reports/runtime/stage5_waveform_decoder_structure_probe_streaming_student_energypeak_tv8_fusionbranchcond_round1_1/stage5_waveform_decoder_structure_probe.json`
