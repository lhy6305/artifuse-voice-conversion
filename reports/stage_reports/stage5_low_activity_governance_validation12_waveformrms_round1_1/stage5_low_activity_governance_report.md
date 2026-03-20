# stage5 low-activity governance report - validation12 waveformrms

## Metadata
- generated_at: 2026-03-20T19:35:57
- audio_source: decoded
- governance_mode: tradeoff

## Executive Status
- executive_status: Current low-activity governance mode is tradeoff; fragmentation axis favors [offline_mvp_nores_vocoder_dataset_loop.step36, offline_mvp_nores_vocoder_dataset_loop.step48, offline_mvp_nores_vocoder_dataset_loop.step60]; leakage-strength axis favors offline_mvp_nores_vocoder_dataset_loop.step72; soft rerank currently selects step 72.

## Fragmentation Axis
- fragmentation_axis: best_fragmentation=[offline_mvp_nores_vocoder_dataset_loop.step36, offline_mvp_nores_vocoder_dataset_loop.step48, offline_mvp_nores_vocoder_dataset_loop.step60] best_alignment=offline_mvp_nores_vocoder_dataset_loop.step72 best_quietness=offline_mvp_nores_vocoder_dataset_loop.step72
- fragmentation_note: Use this axis when burst/toggle risk and local structural safety are the primary question.

## Leakage-Strength Axis
- leakage_strength_axis: best_leakage_strength=offline_mvp_nores_vocoder_dataset_loop.step72 worst_floor_leakage=[offline_mvp_nores_vocoder_dataset_loop.step36, offline_mvp_nores_vocoder_dataset_loop.step48, offline_mvp_nores_vocoder_dataset_loop.step60]
- leakage_note: Use this axis when comparing residual leakage strength inside a leakage cluster or choosing a fallback after fragmentation has already tied.

### Leakage Strength Tie-Break
- offline_mvp_nores_vocoder_dataset_loop.step60 (mean_waveform_rms=0.022724)
- offline_mvp_nores_vocoder_dataset_loop.step48 (mean_waveform_rms=0.038473)
- offline_mvp_nores_vocoder_dataset_loop.step36 (mean_waveform_rms=0.059632)

### Leakage Smoothness Tie-Break
- offline_mvp_nores_vocoder_dataset_loop.step60 (mean_sample_delta_peak=0.196337)
- offline_mvp_nores_vocoder_dataset_loop.step48 (mean_sample_delta_peak=0.221658)
- offline_mvp_nores_vocoder_dataset_loop.step36 (mean_sample_delta_peak=0.34293)

## Cross-Axis Note
- Cross-axis note: fragmentation axis and leakage-strength axis point to different branch/groups; treat this as a dual-axis tradeoff instead of forcing a single winner.

## Soft Rerank Snapshot
- enabled=True soft_validation_ratio=1.05 eligible_candidate_count=2 selected_step=72 selected_score=0.1 loss_total=0.564671 rms_ratio_deviation=0.082565

## Top Windows
- record_id=target::chapter3_6_firefly_106 segment_index=1 delta_fragmentation_score=6.013935 worst_branch=offline_mvp_nores_vocoder_dataset_loop.step72 best_branch=offline_mvp_nores_vocoder_dataset_loop.step48
- record_id=target::chapter3_26_firefly_107 segment_index=1 delta_fragmentation_score=5.01555 worst_branch=offline_mvp_nores_vocoder_dataset_loop.step72 best_branch=offline_mvp_nores_vocoder_dataset_loop.step60
- record_id=target::chapter3_29_firefly_113 segment_index=1 delta_fragmentation_score=3.015623 worst_branch=offline_mvp_nores_vocoder_dataset_loop.step72 best_branch=offline_mvp_nores_vocoder_dataset_loop.step60

## Source Artifacts
- checkpoint_selection_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_lowactivity4way_validation12_waveformrms_round1_1/nores_vocoder_checkpoint_selection.json
- probe_path: F:/proj_dev/tmp/workdir4/reports/audio/stage5_low_activity_fragmentation_probe_activitygate36_48_60_72_decoded_validation12_waveformrms_round1_1/stage5_low_activity_fragmentation_probe.json
- summary_path: F:/proj_dev/tmp/workdir4/reports/runtime/offline_mvp_nores_vocoder_waveform_stft_rmsguard02_activitygate02_gate72_deterministic_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json

## Notes
- This fixed-format report is derived from nores_vocoder_checkpoint_selection.json and reuses the embedded dual-axis governance template.
- Fragmentation axis and leakage-strength axis are intentionally rendered separately so tradeoff cases do not get compressed into a single winner.
- Use top_windows for decoded listening follow-up; use the dual-axis template for governance wording.
