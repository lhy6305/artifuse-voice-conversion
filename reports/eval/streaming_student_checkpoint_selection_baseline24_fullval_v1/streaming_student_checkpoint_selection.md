# Stage3 Streaming Student Checkpoint Selection

- generated_at: 2026-03-17T16:34:13
- checkpoint_paths: ['F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline24_fullval_v1.step8.pt', 'F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline24_fullval_v1.step16.pt', 'F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline24_fullval_v1.step24.pt']
- selection_rule: lexicographic(min_target_validation_loss_total, min_target_special_eval_loss_total)
- best_checkpoint: {"checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline24_fullval_v1.step24.pt", "step": 24, "target_validation_loss_total": 7.292622, "target_special_eval_loss_total": 7.804316}

## Ranking
- step=24 target_validation_loss_total=7.292622 target_special_eval_loss_total=7.804316 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline24_fullval_v1.step24.pt
- step=16 target_validation_loss_total=7.635716 target_special_eval_loss_total=7.926552 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline24_fullval_v1.step16.pt
- step=8 target_validation_loss_total=8.879169 target_special_eval_loss_total=8.446648 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline24_fullval_v1.step8.pt

## Notes
- This report compares already-produced Stage3 checkpoints using fuller teacher-supervised checkpoint evaluation.
- The current ranking rule is validation-first; special_eval is a tiebreaker when requested.
- These are still proxy losses and should be interpreted as checkpoint-selection aids, not final user-facing quality conclusions.
