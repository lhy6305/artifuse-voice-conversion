# 520 Stage5 Fixed-Input Fusion Residualshape Breakthrough And Scale Screen Report

## Summary
- This round kept the current deterministic Stage3 winner fixed:
  - `reports/training/ss_detpitch_energypeak_s2_step1/checkpoints/ss_detpitch_energypeak_s2_step1.step1.pt`
- No Stage3 training was continued.
- After retiring hidden-side branch-conditioned decoder families as the immediate next move, this round evaluated the more direct output-side residual-shape family on the same fixed-input Stage5 packages:
  - `fusionbranchmeancontrast_residualshape_fullsplit24`
  - plus residual-shape scale variants on `tv8`
- This is the first current fixed-input Stage5 family that materially escapes the old `8/8 auto_reject` basin:
  - full residual-shape:
    - `tv8 = 6/8 auto_reject`
    - `se8 = 6/8 auto_reject`
  - `scale050` residual-shape:
    - `tv8 = 5/8 auto_reject`
    - `se8 = 6/8 auto_reject`
- The route is still not decoded-ready, but the failure family has changed:
  - no longer the old uniform `buzz_before_predicted_activity_gate = true`
  - handoff diagnosis now reports `needs_more_localization`
- The best current fixed-input Stage5 consumer-side candidate is now:
  - `fusionbranchmeancontrast_residualshape_scale050`

## Probes Run

### Fixed-input full residual-shape family
- tv8 audio export:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionresshape_round1_1/nores_vocoder_audio_export.json`
- tv8 waveform handoff probe:
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_tv8_fusionresshape_round1_1/stage5_waveform_handoff_probe.json`
- tv8 waveform decoder structure probe:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_streaming_student_energypeak_tv8_fusionresshape_round1_1/stage5_waveform_decoder_structure_probe.json`
- se8 audio export:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_se8_fusionresshape_round1_1/nores_vocoder_audio_export.json`
- se8 waveform handoff probe:
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_se8_fusionresshape_round1_1/stage5_waveform_handoff_probe.json`

### Fixed-input residual-shape scale screen
- tv8 handoff probe, `scale025`:
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_tv8_fusionresshape025_round1_1/stage5_waveform_handoff_probe.json`
- tv8 handoff probe, `scale050`:
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_tv8_fusionresshape050_round1_1/stage5_waveform_handoff_probe.json`
- tv8 audio export, `scale050`:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionresshape050_round1_1/nores_vocoder_audio_export.json`
- se8 handoff probe, `scale050`:
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_se8_fusionresshape050_round1_1/stage5_waveform_handoff_probe.json`
- se8 audio export, `scale050`:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_se8_fusionresshape050_round1_1/nores_vocoder_audio_export.json`

## Fixed-Input Full Residual-Shape Findings

### tv8
- Audio export:
  - `auto_reject_count = 6/8`
  - `all_records_auto_reject = false`
  - `mean_loss_total = 0.948918`
  - `mean_decoded_frame_template_cosine_mean = 0.981316`
  - `mean_decoded_frame_rms_to_aligned_frame_rms_corr = 0.885453`
  - `mean_spectral_centroid_gap_hz = 4509.864129`
  - `mean_spectral_high_band_energy_ratio_gap = 0.341384`
- Handoff probe:
  - `decoded_no_gate = 4/8 auto_reject`
  - `decoded_pre_ola_gate = 6/8 auto_reject`
  - `decoded_post_ola_gate = 6/8 auto_reject`
  - `primary_localization = needs_more_localization`
  - `buzz_before_predicted_activity_gate = false`
  - `predicted_activity_gate_changes_auto_reject_status = false`

### se8
- Audio export:
  - `auto_reject_count = 6/8`
  - `all_records_auto_reject = false`
  - `mean_loss_total = 1.026228`
  - `mean_decoded_frame_template_cosine_mean = 0.98786`
  - `mean_decoded_frame_rms_to_aligned_frame_rms_corr = 0.703558`
  - `mean_spectral_centroid_gap_hz = 3641.096417`
  - `mean_spectral_high_band_energy_ratio_gap = 0.260861`
- Handoff probe:
  - `decoded_no_gate = 6/8 auto_reject`
  - `decoded_pre_ola_gate = 6/8 auto_reject`
  - `decoded_post_ola_gate = 6/8 auto_reject`
  - `primary_localization = needs_more_localization`
  - `buzz_before_predicted_activity_gate = false`
  - `predicted_activity_gate_changes_auto_reject_status = false`

### Reading
- Unlike the earlier fixed-input baseline and branch-conditioned decoder families, the full residual-shape family no longer stays in uniform pre-gate buzz failure.
- This is still not a success route, but it is a real change in operating region.

## Fixed-Input Scale Screen

### tv8 decoded_post_ola_gate screen
- Full residual-shape:
  - `auto_reject_count = 6/8`
  - `decoded_frame_template_cosine_mean = 0.981316`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.885453`
  - `spectral_centroid_gap_hz = 4509.864258`
  - `spectral_high_band_energy_ratio_gap = 0.341384`
- `scale025`:
  - `auto_reject_count = 6/8`
  - `decoded_frame_template_cosine_mean = 0.980155`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.888005`
  - `spectral_centroid_gap_hz = 4406.603027`
  - `spectral_high_band_energy_ratio_gap = 0.332151`
- `scale050`:
  - `auto_reject_count = 5/8`
  - `decoded_frame_template_cosine_mean = 0.979413`
  - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.888663`
  - `spectral_centroid_gap_hz = 4346.541992`
  - `spectral_high_band_energy_ratio_gap = 0.327457`

### se8 check for the current scale winner
- Full residual-shape:
  - `decoded_post_ola_gate auto_reject_count = 6/8`
  - `decoded_frame_template_cosine_mean = 0.98786`
  - `spectral_centroid_gap_hz = 3641.096436`
  - `spectral_high_band_energy_ratio_gap = 0.260861`
- `scale050`:
  - `decoded_post_ola_gate auto_reject_count = 6/8`
  - `decoded_frame_template_cosine_mean = 0.98697`
  - `spectral_centroid_gap_hz = 3444.734131`
  - `spectral_high_band_energy_ratio_gap = 0.245875`

### Reading
- `scale050` is the best current residual-shape screen variant:
  - it improves `tv8` from `6/8` to `5/8 auto_reject`
  - it also improves brightness and template-collapse metrics on both `tv8` and `se8`
- `scale050` does not yet improve `se8` route counts beyond `6/8`, so this is still a partial, not universal, Stage5 decoded recovery.

## Structure Reading For Full Residual-Shape Family
- tv8 structure probe summary:
  - `fused_hidden_template_cosine_mean = 0.978221`
  - `waveform_frames_template_cosine_mean = 0.991348`
  - `decoded_frames_template_cosine_mean = 0.981316`
  - `diagnosis = collapse_not_localized_to_waveform_decoder`
- Coupling localization still remains:
  - `diagnosis = decoder_hidden_to_base_logits_is_main_coupling_amplifier`
  - `strongest_transition = decoder_to_base_logits`
- Geometry localization still remains:
  - `diagnosis = decoder_hidden_to_base_logits_is_main_geometry_collapse`
  - `decoder_to_base_logits_effective_rank_drop = 0.020465`
- But this family differs from the earlier hidden-side adapter families in one important way:
  - route-level auto-reject is no longer uniform
  - handoff diagnosis no longer collapses to the old pre-gate buzz reading

## Decision
- Keep the current deterministic Stage3 winner fixed as the packet-facing input reference.
- Retire the hidden-side branch-conditioned decoder families as the immediate Stage5 next move.
- Promote `fusionbranchmeancontrast_residualshape_scale050` as the current best Stage5 consumer-side fixed-input candidate.
- Treat this as a partial decoded breakthrough, not a route-opening success.

## Recommended Next Action
- Continue on the residual-shape output-side family rather than the hidden-side branch-conditioned family.
- Prioritize:
  - record-localized diagnosis of the remaining `tv8` and `se8` auto-reject examples under `scale050`
  - or a small fixed-input screen around nearby residual-shape scales and related output-side controls

## Key Artifacts
- Stage3 winner:
  - `reports/training/ss_detpitch_energypeak_s2_step1/checkpoints/ss_detpitch_energypeak_s2_step1.step1.pt`
- Full residual-shape:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionresshape_round1_1/nores_vocoder_audio_export.json`
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_tv8_fusionresshape_round1_1/stage5_waveform_handoff_probe.json`
  - `reports/runtime/stage5_waveform_decoder_structure_probe_streaming_student_energypeak_tv8_fusionresshape_round1_1/stage5_waveform_decoder_structure_probe.json`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_se8_fusionresshape_round1_1/nores_vocoder_audio_export.json`
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_se8_fusionresshape_round1_1/stage5_waveform_handoff_probe.json`
- Residual-shape scale screen:
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_tv8_fusionresshape025_round1_1/stage5_waveform_handoff_probe.json`
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_tv8_fusionresshape050_round1_1/stage5_waveform_handoff_probe.json`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionresshape050_round1_1/nores_vocoder_audio_export.json`
  - `reports/runtime/stage5_waveform_handoff_probe_streaming_student_energypeak_se8_fusionresshape050_round1_1/stage5_waveform_handoff_probe.json`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_se8_fusionresshape050_round1_1/nores_vocoder_audio_export.json`
