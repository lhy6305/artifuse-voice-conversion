# Stage3 Streaming Student Checkpoint Selection

- generated_at: 2026-03-17T15:36:42
- checkpoint_paths: ['F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step4.pt', 'F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step8.pt', 'F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step12.pt']
- selection_rule: lexicographic(min_target_validation_loss_total, min_target_special_eval_loss_total)
- best_checkpoint: {"checkpoint_path": "F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step12.pt", "step": 12, "target_validation_loss_total": 6.919654, "target_special_eval_loss_total": 6.845759}

## Ranking
- step=12 target_validation_loss_total=6.919654 target_special_eval_loss_total=6.845759 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step12.pt
- step=8 target_validation_loss_total=7.667545 target_special_eval_loss_total=7.188635 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step8.pt
- step=4 target_validation_loss_total=8.651326 target_special_eval_loss_total=7.825405 checkpoint_path=F:/proj_dev/tmp/workdir4/reports/training/streaming_student_loop/checkpoints/streaming_student_stage_loop_eventprior025_v1.step4.pt

## Notes
- This report compares already-produced Stage3 checkpoints using fuller teacher-supervised checkpoint evaluation.
- The current ranking rule is validation-first; special_eval is a tiebreaker when requested.
- These are still proxy losses and should be interpreted as checkpoint-selection aids, not final user-facing quality conclusions.
