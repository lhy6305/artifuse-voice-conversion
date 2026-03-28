# Stage3 Streaming Student Checkpoint Selection

- generated_at: 2026-03-28T23:31:35
- checkpoint_paths: ['F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop_timingfocus6warm_baseline18_denseckpt_round1_1/checkpoints/streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1.step12.pt', 'F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop_timingfocus6warm_baseline18_denseckpt_round1_1/checkpoints/streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1.step15.pt', 'F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop_timingfocus6warm_baseline18_denseckpt_round1_1/checkpoints/streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1.step18.pt']
- selection_rule: lexicographic(min_target_validation_loss_total, min_target_special_eval_loss_total)
- best_checkpoint: {"checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop_timingfocus6warm_baseline18_denseckpt_round1_1/checkpoints/streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1.step12.pt", "step": 12, "target_validation_loss_total": 1.435668, "target_special_eval_loss_total": 1.271588}

## Ranking
- step=12 target_validation_loss_total=1.435668 target_special_eval_loss_total=1.271588 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop_timingfocus6warm_baseline18_denseckpt_round1_1/checkpoints/streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1.step12.pt
- step=15 target_validation_loss_total=1.476498 target_special_eval_loss_total=1.162192 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop_timingfocus6warm_baseline18_denseckpt_round1_1/checkpoints/streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1.step15.pt
- step=18 target_validation_loss_total=1.536822 target_special_eval_loss_total=1.196767 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop_timingfocus6warm_baseline18_denseckpt_round1_1/checkpoints/streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1.step18.pt

## Notes
- This report compares already-produced Stage3 checkpoints using fuller teacher-supervised checkpoint evaluation.
- The current ranking rule is validation-first; special_eval is a tiebreaker when requested.
- These are still proxy losses and should be interpreted as checkpoint-selection aids, not final user-facing quality conclusions.
