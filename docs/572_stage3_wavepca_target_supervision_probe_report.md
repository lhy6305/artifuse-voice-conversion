# Stage3 WavePCA Target Supervision Probe Report

## Goal
- Move the producer-side fine-structure branch beyond plain waveform-frame reconstruction.
- Test whether directly supervising the deployable `16D` predicted code against the previously validated `wavepca16` upper-bound family can materially improve the Stage5 source-scaffold oracle.

## Routes Tested

### 1. Raw waveform-PCA target
- config:
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_finestructurecode_controlhidden_wavepcatarget_v1.json`
- loss overrides:
  - `configs/streaming_student_loss_weights_detpitch_finestructurecode_wavepcatarget_v1.json`
- training:
  - `reports/training/ss_detpitch_finestructcode_controlhidden_wavepcatarget_loop8_r1_1/`
- full5 oracle:
  - `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_finestructcode_controlhidden_wavepcatarget_step4_r1_1/`

### 2. Whitened waveform-PCA target
- config:
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_finestructurecode_controlhidden_wavepcatarget_whitened_v1.json`
- loss overrides:
  - `configs/streaming_student_loss_weights_detpitch_finestructurecode_wavepcatarget_v1.json`
- training:
  - `reports/training/ss_detpitch_finestructcode_controlhidden_wavepcatarget_whitened_loop8_r1_1/`
- full5 oracle:
  - `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_finestructcode_controlhidden_wavepcatarget_whitened_step8_r1_1/`

### Reference baseline
- control-hidden reconstruction-only route:
  - `reports/training/ss_detpitch_finestructcode_controlhidden_loop8_r1_1/`
  - `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_finestructcode_controlhidden_loop8_r1_1/`

## Training-Side Result
- Raw PCA target:
  - single-step smoke proved the branch wiring, but `loss_teacher_fine_structure_code_target` immediately sat around `16`.
  - short-loop best validation was `step4 loss_total=8.882119`, with `loss_teacher_fine_structure_code_target=12.946568`.
  - this showed that raw PCA coordinates were numerically awkward as a direct MSE target.
- Whitened PCA target:
  - whitening the PCA coordinates fixed the scale problem.
  - single-step smoke dropped `loss_teacher_fine_structure_code_target` to about `1.0`.
  - 8-step loop remained stable and reached `step8 validation loss_total=2.611911`, with `loss_teacher_fine_structure_code_target=0.996542`.

## Full5 Oracle Comparison
Numbers below are `oracle_waveform_frame_cosine_mean / oracle_waveform_mlp_frame_cosine_mean`.

### Reference control-hidden baseline
- `selected_dynamic_controls = 0.016222 / 0.011001`
- `predicted_fine_structure_code_family = 0.007777 / 0.006761`
- `selected_dynamic_plus_predicted_fine_structure_code = 0.011860 / 0.006087`

### Raw PCA target at best validation `step4`
- `selected_dynamic_controls = 0.019590 / 0.018986`
- `predicted_fine_structure_code_family = 0.007267 / 0.004211`
- `selected_dynamic_plus_predicted_fine_structure_code = 0.016988 / 0.010136`

### Whitened PCA target at best validation `step8`
- `selected_dynamic_controls = 0.016335 / 0.010761`
- `predicted_fine_structure_code_family = 0.007973 / 0.007380`
- `selected_dynamic_plus_predicted_fine_structure_code = 0.012583 / 0.002397`

## Interpretation
- Raw PCA target did not make the deployable predicted code better.
- What raw PCA target did do was lift `selected_dynamic_controls`, which means the auxiliary supervision changed the shared model state, but not in the way needed for the exported compact code itself.
- Whitened PCA target fixed the optimization scale and slightly improved the direct predicted-code-only oracle over the plain control-hidden baseline.
- That improvement was still tiny:
  - `0.007973 / 0.007380` remains in the same low-signal regime
  - it still does not beat the current selected-dynamic baseline
  - it still does not open a materially stronger deployable upstream contract
- Therefore:
  - the problem is not only raw target scaling
  - simply distilling the analysis-side `wavepca16` family into the current compact per-frame code head is not enough

## Main Conclusion
- The project now has three negative producer-side families in a row:
  - reconstruction-only compact code
  - raw PCA-code target
  - whitened PCA-code target
- The best reading is no longer "we need another scalar weight shuffle".
- The next branch should change producer architecture or target structure, not just target normalization:
  - add stronger temporal context for the code predictor
  - or redesign the fine-structure contract away from a purely per-frame linear head target

## Next Recommended Direction
- Keep the current `control_hidden_v1` source choice as the working reference.
- Stop iterating on direct per-frame PCA-code MSE variants.
- Move to a stronger upstream branch such as:
  - a dedicated temporal fine-structure predictor head with multi-frame receptive field
  - or a chunk-level / temporally contextual waveform-geometry code rather than a strictly frame-local code

## Artifacts
- `reports/training/ss_detpitch_finestructcode_controlhidden_wavepcatarget_trainstep_smoke_r1_1/`
- `reports/training/ss_detpitch_finestructcode_controlhidden_wavepcatarget_loop8_r1_1/`
- `reports/training/ss_detpitch_finestructcode_controlhidden_wavepcatarget_whitened_trainstep_smoke_r1_1/`
- `reports/training/ss_detpitch_finestructcode_controlhidden_wavepcatarget_whitened_loop8_r1_1/`
- `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_finestructcode_controlhidden_wavepcatarget_step4_r1_1/`
- `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_finestructcode_controlhidden_wavepcatarget_whitened_step8_r1_1/`
