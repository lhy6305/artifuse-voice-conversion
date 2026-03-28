# Stage3 Streaming Student Packet-Aware Checkpoint Selection

- generated_at: 2026-03-29T00:30:17
- selector_version: stage3_packet_aware_checkpoint_selector_v1
- selection_objective: packet_aware_downstream_screen
- checkpoint_paths: ['F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop_timingfocus6warm_baseline18_denseckpt_round1_1/checkpoints/streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1.step12.pt', 'F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop_timingfocus6warm_baseline18_denseckpt_round1_1/checkpoints/streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1.step15.pt', 'F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop_timingfocus6warm_baseline18_denseckpt_round1_1/checkpoints/streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1.step18.pt']
- split_name: target_validation
- sample_count: 3
- target_record_ids: None
- max_audio_sec: None
- selection_rule: packet_facing_lexicographic(min_auto_reject_count, max_all_core_controls_ready_count, max_vuv_ready_count, max_f0_ready_count, max_aper_ready_count, max_energy_ready_count, min_avg_vuv_reference_mae, min_avg_aper_calibrated_reference_mae, min_avg_energy_stage5_norm_calibrated_reference_mae, max_avg_f0_proxy_reference_corr, min_avg_f0_calibrated_log2_mae, min_step)
- best_checkpoint_by_packet_screen: {"checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop_timingfocus6warm_baseline18_denseckpt_round1_1/checkpoints/streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1.step15.pt", "step": 15, "experiment_id": "streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1", "packet_export_dir": "F:/proj_dev/tmp/workdir4/reports/eval/streaming_student_checkpoint_selector_comparison_timingfocus6warm_baseline18_denseckpt_round1_1/packet_aware/packet_exports/step0015_streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1", "auto_reject_count": 3, "all_core_controls_ready_count": 0, "vuv_ready_count": 1, "f0_ready_count": 0, "aper_ready_count": 3, "energy_ready_count": 2, "avg_vuv_reference_mae": 0.18271, "avg_aper_calibrated_reference_mae": 0.118447, "avg_energy_stage5_norm_calibrated_reference_mae": 0.143582, "avg_f0_proxy_reference_corr": 0.416655, "avg_f0_calibrated_log2_mae": 0.329577}

## Ranking
- step=15 auto_reject_count=3 vuv_ready_count=1 f0_ready_count=0 aper_ready_count=3 energy_ready_count=2 avg_vuv_reference_mae=0.18271 avg_aper_calibrated_reference_mae=0.118447 avg_energy_stage5_norm_calibrated_reference_mae=0.143582 avg_f0_proxy_reference_corr=0.416655 avg_f0_calibrated_log2_mae=0.329577 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop_timingfocus6warm_baseline18_denseckpt_round1_1/checkpoints/streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1.step15.pt
- step=18 auto_reject_count=3 vuv_ready_count=1 f0_ready_count=0 aper_ready_count=3 energy_ready_count=2 avg_vuv_reference_mae=0.19273 avg_aper_calibrated_reference_mae=0.118431 avg_energy_stage5_norm_calibrated_reference_mae=0.138791 avg_f0_proxy_reference_corr=0.445955 avg_f0_calibrated_log2_mae=0.320489 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop_timingfocus6warm_baseline18_denseckpt_round1_1/checkpoints/streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1.step18.pt
- step=12 auto_reject_count=3 vuv_ready_count=1 f0_ready_count=0 aper_ready_count=3 energy_ready_count=1 avg_vuv_reference_mae=0.200297 avg_aper_calibrated_reference_mae=0.118257 avg_energy_stage5_norm_calibrated_reference_mae=0.154887 avg_f0_proxy_reference_corr=0.377539 avg_f0_calibrated_log2_mae=0.342035 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop_timingfocus6warm_baseline18_denseckpt_round1_1/checkpoints/streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1.step12.pt

## Notes
- This report ranks Stage3 checkpoints using downstream packet cheap-screen behavior rather than teacher-supervised validation only.
- The rule is packet-facing and negative-gate oriented: it can help choose the least-bad handoff candidate, but it does not prove Stage5 readiness.
- Use this selection together with validation summaries, not as a replacement for them.
- best_checkpoint is kept as a legacy alias for best_checkpoint_by_packet_screen.
