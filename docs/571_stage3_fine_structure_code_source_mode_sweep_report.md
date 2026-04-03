# Stage3 Fine-Structure Code Source-Mode Sweep Report

## Goal
- Test whether the first deployable producer-side fine-structure code branch can be materially improved just by changing the source tensor used to predict the code.
- Keep all other variables fixed:
  - same `code_dim=16`
  - same waveform-frame reconstruction supervision
  - same loss weights
  - same init checkpoint
  - same 8-step short loop
  - same fixed full5 oracle slice

## Variants
- `student_hidden_v1`
  - config: `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_finestructurecode_v1.json`
  - training: `reports/training/ss_detpitch_finestructcode_loop8_r1_1/`
  - oracle: `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_finestructcode_loop8_r1_1/`
- `shared_hidden_v1`
  - config: `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_finestructurecode_sharedhidden_v1.json`
  - training: `reports/training/ss_detpitch_finestructcode_sharedhidden_loop8_r1_1/`
  - oracle: `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_finestructcode_sharedhidden_loop8_r1_1/`
- `control_hidden_v1`
  - config: `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_finestructurecode_controlhidden_v1.json`
  - training: `reports/training/ss_detpitch_finestructcode_controlhidden_loop8_r1_1/`
  - oracle: `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_finestructcode_controlhidden_loop8_r1_1/`

## Common Evaluation Slice
- tv3 packet export:
  - `target::chapter3_26_firefly_114`
  - `target::chapter3_30_firefly_132`
  - `target::chapter4_7_firefly_105`
- se2 packet export:
  - `target::no_text_voice/chapter3_18_firefly_101`
  - `target::no_text_voice/chapter3_21_firefly_108`

## Short-Loop Training Comparison
- `student_hidden_v1`
  - validation `loss_total = 2.111754`
  - validation `loss_teacher_fine_structure_waveform_frame = 0.972449`
  - full5 packet `fine_structure_code_reconstruction_mae mean = 0.818314`
- `shared_hidden_v1`
  - validation `loss_total = 2.107971`
  - validation `loss_teacher_fine_structure_waveform_frame = 0.970999`
  - full5 packet `fine_structure_code_reconstruction_mae mean = 0.818119`
- `control_hidden_v1`
  - validation `loss_total = 2.108968`
  - validation `loss_teacher_fine_structure_waveform_frame = 0.970697`
  - full5 packet `fine_structure_code_reconstruction_mae mean = 0.819155`

## Full5 Oracle Comparison
- Current baseline for comparison:
  - `selected_dynamic_controls = 0.016271 / 0.011280` on `student_hidden_v1`
  - `selected_dynamic_controls = 0.016390 / 0.011599` on `shared_hidden_v1`
  - `selected_dynamic_controls = 0.016222 / 0.011001` on `control_hidden_v1`
- Predicted code only:
  - `student_hidden_v1 = 0.004932 / 0.008825`
  - `shared_hidden_v1 = 0.006839 / 0.003404`
  - `control_hidden_v1 = 0.007777 / 0.006761`
- Selected dynamic controls plus predicted code:
  - `student_hidden_v1 = 0.011543 / 0.009534`
  - `shared_hidden_v1 = 0.011380 / 0.004500`
  - `control_hidden_v1 = 0.011860 / 0.006087`
- Reference anchors remain unchanged:
  - `fine_structure_reference_family = 0.017661 / 0.019218`
  - `fine_structure_waveform_reference_family = 0.999958 / 0.845117`

Numbers above are `oracle_waveform_frame_cosine_mean / oracle_waveform_mlp_frame_cosine_mean` from the cross-record aggregates.

## Interpretation
- The branch is not broken:
  - all three source modes train stably
  - packet export succeeds
  - the predicted code appears correctly in the Stage3 packet and Stage5 source_scaffold oracle
- But changing source mode alone is not enough:
  - all three predicted-code variants stay below the old `selected_dynamic_controls` baseline on the full5 cross-record oracle
  - adding the predicted code back into `selected_dynamic_controls` still lowers the result instead of opening a new gate
- `control_hidden_v1` is the least bad of the three source choices on the direct waveform-linear metric, but the gain is still small and remains in the same low-signal regime.
- Therefore the current bottleneck is no longer "which hidden tensor should emit the code" in isolation.
- The next discriminative variable should be:
  - supervision target design
  - contract objective
  - code learning recipe
  - not another source-mode sweep

## Conclusion
- This round closes the first `source_mode` branch for the producer-side fine-structure code.
- Current ranking:
  - `control_hidden_v1` slightly best
  - `shared_hidden_v1` and `student_hidden_v1` close behind
  - none materially open the deployable upstream contract
- The project should now move to a stronger producer-side waveform-code training target rather than continue swapping hidden-source taps.

## Artifacts
- `reports/training/ss_detpitch_finestructcode_loop8_r1_1/`
- `reports/training/ss_detpitch_finestructcode_sharedhidden_loop8_r1_1/`
- `reports/training/ss_detpitch_finestructcode_controlhidden_loop8_r1_1/`
- `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_finestructcode_loop8_r1_1/`
- `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_finestructcode_sharedhidden_loop8_r1_1/`
- `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_finestructcode_controlhidden_loop8_r1_1/`
