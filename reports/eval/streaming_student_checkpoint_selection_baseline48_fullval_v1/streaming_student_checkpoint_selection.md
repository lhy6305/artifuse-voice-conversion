# Stage3 Streaming Student Checkpoint Selection

- generated_at: 2026-03-17T16:41:42
- checkpoint_paths: ['F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step12.pt', 'F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step24.pt', 'F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step36.pt', 'F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step48.pt']
- selection_rule: lexicographic(min_target_validation_loss_total, min_target_special_eval_loss_total)
- best_checkpoint: {"checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step48.pt", "step": 48, "target_validation_loss_total": 7.141462, "target_special_eval_loss_total": 7.572382}

## Ranking
- step=48 target_validation_loss_total=7.141462 target_special_eval_loss_total=7.572382 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step48.pt
- step=24 target_validation_loss_total=7.292622 target_special_eval_loss_total=7.804316 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step24.pt
- step=36 target_validation_loss_total=7.323279 target_special_eval_loss_total=7.76588 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step36.pt
- step=12 target_validation_loss_total=8.134648 target_special_eval_loss_total=8.11794 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_baseline48_fullval_v1.step12.pt

## Notes
- This report compares already-produced Stage3 checkpoints using fuller teacher-supervised checkpoint evaluation.
- The current ranking rule is validation-first; special_eval is a tiebreaker when requested.
- These are still proxy losses and should be interpreted as checkpoint-selection aids, not final user-facing quality conclusions.
