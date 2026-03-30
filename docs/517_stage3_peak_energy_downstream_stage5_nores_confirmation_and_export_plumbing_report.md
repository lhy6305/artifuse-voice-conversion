# 517 Stage3 Peak-Energy Downstream Stage5 No-Res Confirmation And Export Plumbing Report

## Summary
- The current deterministic Stage3 winner remains:
  - `F:/proj_dev/tmp/workdir4/reports/training/ss_detpitch_energypeak_s2_step1/checkpoints/ss_detpitch_energypeak_s2_step1.step1.pt`
- This round did not continue Stage3 training.
- Instead it performed downstream-facing confirmation with the existing Stage5 no-res decoded route.
- The result is structurally clear:
  - Stage3 packet readiness remains open on the widened validation screens.
  - The existing Stage5 no-res consumer still fails hard on decoded output.

## Export Plumbing Fix
- `src/v5vc/nores_vocoder_audio_export.py` had drifted behind the current
  `compute_nores_vocoder_losses(...)` signature.
- The export path was still calling the old loss signature and crashed on the new
  Stage5 package family.
- This was fixed by forwarding the now-required optional control targets:
  - `energy_proxy_target`
  - `energy_log_rms_norm_target`
  - `aper_target`
  - `vuv_target`
  - `voiced_proxy_target`
  - `aperiodicity_proxy_target`
- This is a low-risk plumbing fix for decoded confirmation only.
- It does not change Stage3 training conclusions.

## Downstream Confirmation Setup
- Reused the packet exports already produced by the packet-aware selector:
  - `reports/runtime/ss_pktsel_detpitch_energypeak_s2_step1_tv8/pkt_exp/s0001_ss_detpitch_energypeak_s2_step1/streaming_student_downstream_control_packet.json`
  - `reports/runtime/ss_pktsel_detpitch_energypeak_s2_step1_se8/pkt_exp/s0001_ss_detpitch_energypeak_s2_step1/streaming_student_downstream_control_packet.json`
- Built synthetic Stage5 dataset packages from those packet exports:
  - `reports/runtime/streaming_student_stage5_dataset_energypeak_s2_step1_tv8/streaming_student_stage5_dataset_index.json`
  - `reports/runtime/streaming_student_stage5_dataset_energypeak_s2_step1_se8/streaming_student_stage5_dataset_index.json`
- Used the existing Stage5 no-res selection:
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_contractv2_normfix_acttmpl005_zerojitter4_fullsplit24_round1_1/nores_vocoder_checkpoint_selection.json`
- Resolved checkpoint:
  - `reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_contractv2_normfix_acttmpl005_zerojitter4_fullsplit24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step24.pt`

## Results

### target_validation tv8
- Export summary:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_round1_1/nores_vocoder_audio_export.json`
- Outcome:
  - `sample_count = 8`
  - `auto_reject_count = 8`
  - `all_records_auto_reject = true`
- The current Stage5 no-res decoded route therefore fails on all 8 validation-confirmed
  deterministic handoff candidates.
- Representative failure signals:
  - decoded spectral centroid remains about `7.5 kHz` to `9.2 kHz` above target
  - decoded high-band ratio gap remains about `0.64` to `0.78`
  - decoded frame-template and adjacent-frame cosine stay in the historical
    envelope-following buzz regime
- The original former Stage3 blocker record
  `target::chapter3_4_firefly_106` is still auto-rejected downstream even though
  its Stage3 packet controls are now clean.

### target_special_eval se8
- Export summary:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_se8_round1_1/nores_vocoder_audio_export.json`
- Outcome:
  - `sample_count = 8`
  - `auto_reject_count = 8`
  - `all_records_auto_reject = true`
- This reproduces the same negative result on the wider special-eval slice.
- The downstream failure is therefore not limited to the original validation subset.

## Interpretation
- The current deterministic Stage3 line is now strong enough to be treated as a
  packet-facing reference.
- But the existing Stage5 no-res consumer remains in the historical decoded buzz
  family even when fed the new Stage3 winner.
- Therefore the active bottleneck has moved again:
  - no longer Stage3 packet control readiness
  - now Stage5 decoded consumer behavior

## Decision
- Keep `ss_detpitch_energypeak_s2_step1.step1` as the active deterministic
  packet-facing Stage3 reference.
- Do not resume same-family Stage3 continuation from this result.
- Treat the current Stage5 no-res decoded route as still blocked.
- Future work for this line should target Stage5 consumer or handoff diagnosis,
  not more Stage3 control tuning.

## Key Artifacts
- Stage3 winner:
  - `reports/training/ss_detpitch_energypeak_s2_step1/checkpoints/ss_detpitch_energypeak_s2_step1.step1.pt`
- Packet confirmation:
  - `reports/runtime/ss_pktsel_detpitch_energypeak_s2_step1_tv8/streaming_student_packet_checkpoint_selection.json`
  - `reports/runtime/ss_pktsel_detpitch_energypeak_s2_step1_se8/streaming_student_packet_checkpoint_selection.json`
- Stage5 synthetic dataset packages:
  - `reports/runtime/streaming_student_stage5_dataset_energypeak_s2_step1_tv8/streaming_student_stage5_dataset_index.json`
  - `reports/runtime/streaming_student_stage5_dataset_energypeak_s2_step1_se8/streaming_student_stage5_dataset_index.json`
- Stage5 decoded confirmation:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_round1_1/nores_vocoder_audio_export.json`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_se8_round1_1/nores_vocoder_audio_export.json`
