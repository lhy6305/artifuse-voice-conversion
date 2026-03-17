# Stage3 Streaming Student Checkpoint Selection

- generated_at: 2026-03-17T16:43:18
- checkpoint_paths: ['F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval48_v1.step12.pt', 'F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval48_v1.step24.pt', 'F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval48_v1.step36.pt', 'F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval48_v1.step48.pt']
- selection_rule: lexicographic(min_target_validation_loss_total, min_target_special_eval_loss_total)
- best_checkpoint: {"checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval48_v1.step48.pt", "step": 48, "target_validation_loss_total": 5.978989, "target_special_eval_loss_total": 6.328038}

## Ranking
- step=48 target_validation_loss_total=5.978989 target_special_eval_loss_total=6.328038 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval48_v1.step48.pt
- step=24 target_validation_loss_total=6.124982 target_special_eval_loss_total=6.563445 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval48_v1.step24.pt
- step=36 target_validation_loss_total=6.138614 target_special_eval_loss_total=6.53231 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval48_v1.step36.pt
- step=12 target_validation_loss_total=6.919654 target_special_eval_loss_total=6.845759 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_fullval48_v1.step12.pt

## Notes
- This report compares already-produced Stage3 checkpoints using fuller teacher-supervised checkpoint evaluation.
- The current ranking rule is validation-first; special_eval is a tiebreaker when requested.
- These are still proxy losses and should be interpreted as checkpoint-selection aids, not final user-facing quality conclusions.
