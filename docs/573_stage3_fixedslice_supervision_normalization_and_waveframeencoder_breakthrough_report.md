# Stage3 Fixed-Slice Supervision Normalization and Waveform-Frame Encoder Breakthrough Report

## Goal
- Normalize the recent producer-side fine-structure supervision variants onto the same fixed full5 review slice.
- Check whether the recent `chunk-target` and `detach-source` conclusions were real improvements or just slice drift.
- Test a higher-level upstream redesign: a dedicated deployable waveform-frame encoder branch for the predicted fine-structure code.

## Fixed-Slice Normalization

### Why this was needed
- Recent `sample_count=3/2` packet exports did not stay on one implicit full5 slice across runs.
- That made the earlier oracle numbers for:
  - whitened per-frame `wavepca16` target
  - temporal-conv predictor
  - chunk-level PCA target
  - detached-source head
  not directly comparable.
- The normalized fixed slice used here is:
  - tv3:
    - `target::chapter3_3_firefly_162`
    - `target::chapter3_3_firefly_138`
    - `target::chapter3_4_firefly_106`
  - se2:
    - `target::no_text_voice/chapter3_17_firefly_106`
    - `target::no_text_voice/chapter3_3_firefly_110`

### Same-slice oracle comparison
- Same-slice whitened per-frame `wavepca16` target:
  - training: `reports/training/ss_detpitch_finestructcode_controlhidden_wavepcatarget_whitened_loop8_r1_1/`
  - fixed-slice oracle: `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_finestructcode_controlhidden_wavepcatarget_whitened_step8_fixedslice_r1_1/`
  - `selected_dynamic_controls = 0.000326 / -0.001203`
  - `predicted_fine_structure_code_family = 0.005505 / 0.005349`
  - `selected_dynamic_plus_predicted_fine_structure_code = 0.000012 / 0.001332`
- Same-slice chunk-level PCA target:
  - training: `reports/training/ss_detpitch_finestructcode_controlhidden_wavepcachunktarget_whitened_loop8_r1_1/`
  - oracle: `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_finestructcode_controlhidden_wavepcachunktarget_whitened_step8_r1_1/`
  - `selected_dynamic_controls = 0.000288 / -0.001241`
  - `predicted_fine_structure_code_family = 0.005448 / 0.004564`
  - `selected_dynamic_plus_predicted_fine_structure_code = 0.000186 / 0.001945`
- Same-slice detached-source whitened per-frame target:
  - training: `reports/training/ss_detpitch_finestructcode_controlhidden_wavepcatarget_whitened_detachedsource_loop8_r1_1/`
  - oracle: `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_finestructcode_controlhidden_wavepcatarget_whitened_detachedsource_step8_r1_1/`
  - `selected_dynamic_controls = 0.000760 / -0.000798`
  - `predicted_fine_structure_code_family = 0.005611 / 0.004713`
  - `selected_dynamic_plus_predicted_fine_structure_code = 0.000323 / 0.002741`

### Same-slice conclusion
- Once evaluated on the same five records, all recent hidden-source supervision variants remain in the same weak regime.
- The apparent larger differences from earlier reports were substantially confounded by slice drift.
- `detach-source` is only slightly less bad than the same-slice whitened baseline.
- `chunk-target` remains negative.
- Therefore the correct reading is:
  - hidden-source supervision tweaks were not opening the deployable upstream contract
  - they were all hitting a shared ceiling

## Structural Reassessment
- The ceiling above is consistent with the Stage3 code structure itself.
- `StreamingStudentScaffold.frontend` does not read raw local waveform geometry into the hidden path used by the old fine-structure source modes.
- The current frontend input is the `frame_waveform()` feature pair:
  - `energy`
  - `abs_mean`
- That means the old `shared_hidden_v1`, `control_hidden_v1`, and `student_hidden_v1` source modes were all trying to regress fine waveform geometry from a frontend whose direct frame input was only `2D` coarse statistics.
- Under that architecture, repeated supervision refinements were likely bound by missing producer-side input information, not only by loss weighting.

## New Route: Waveform-Frame Encoder

### Implementation
- Added a new producer-side fine-structure source mode:
  - `fine_structure_code_source_mode = waveform_frame_encoder_v1`
- New code path:
  - build unit-RMS normalized aligned waveform frames directly from the input waveform
  - encode them with a dedicated MLP branch
  - predict the deployable `16D` compact code from that branch
- Main files:
  - `src/v5vc/streaming_student/model.py`
  - `src/v5vc/streaming_student/plan_entry.py`
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_finestructurecode_waveframeencoder_wavepcatarget_whitened_v1.json`

### Training result
- smoke:
  - `reports/training/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_trainstep_smoke_r1_1/`
  - validation `loss_total = 3.215909`
  - validation `loss_teacher_fine_structure_code_target = 1.113895`
- short loop:
  - `reports/training/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_loop8_r1_1/`
  - best validation `step8 loss_total = 2.416066`
- This is materially cleaner than the older hidden-source variants on the same supervision family.

## Fixed-Slice Oracle Breakthrough
- fixed-slice packet export:
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_loop8_step8_fixedslice_tv3_pkt_r1_1/`
  - `reports/runtime/ss_detpitch_finestructcode_waveframeencoder_wavepcatarget_whitened_loop8_step8_fixedslice_se2_pkt_r1_1/`
- fixed-slice oracle:
  - `reports/runtime/stage5_source_scaffold_oracle_probe_reviewslice_full5_finestructcode_waveframeencoder_wavepcatarget_whitened_step8_fixedslice_r1_1/`

Key numbers:
- `selected_dynamic_controls = 0.001125 / -0.000522`
- `predicted_fine_structure_code_family = 0.545295 / 0.547317`
- `selected_dynamic_plus_predicted_fine_structure_code = 0.537081 / 0.543211`

Comparison against the same-slice hidden-source whitened baseline:
- waveform cosine:
  - `0.545295` vs `0.005505`
- waveform-MLP cosine:
  - `0.547317` vs `0.005349`
- selected-dynamic-plus-code waveform cosine:
  - `0.537081` vs `0.000012`
- selected-dynamic-plus-code waveform-MLP cosine:
  - `0.543211` vs `0.001332`

Interpretation:
- The deployable producer-side code is no longer stuck in the old low-signal regime.
- The bottleneck was not merely "more temporal context" or "better target normalization".
- A major missing piece was that the old producer path never actually exposed raw local waveform geometry to the compact-code branch.

## Stage5 Consumer Smoke

### Implementation
- Added a deployable Stage5 consumer mode:
  - `streaming_student_waveform_geometry_code_v1`
- Main files:
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/cli.py`
- This reads `fine_structure_code.waveform_geometry_code` from the Stage3 packet instead of the analysis-only `waveform_pca_code`.

### Package build
- Stage5 geometry-code packages:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_waveframeencoder_wavepcatarget_whitened_step8_geomcode_fixedslice_tv3_r1_1/`
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_waveframeencoder_wavepcatarget_whitened_step8_geomcode_fixedslice_se2_r1_1/`
  - merged index:
    - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_waveframeencoder_wavepcatarget_whitened_step8_geomcode_fixedslice_full5_r1_1/`
- The new Stage5 package dims are:
  - `periodic_input_dim = 52`
  - `noise_input_dim = 52`

### Train-step smoke
- output:
  - `reports/runtime/stage5_waveframeencoder_geomcode_trainstep_smoke_r1_1/`
- command target package:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_waveframeencoder_wavepcatarget_whitened_step8_geomcode_fixedslice_tv3_r1_1/packages/validation/target__chapter3_3_firefly_162/train_targets/offline_mvp_nores_vocoder_train_targets.pt`
- result:
  - `loss_total = 1.09945`

This proves the deployable geometry-code contract can already be packet-exported, packaged, consumed by Stage5, and trained through in a minimal smoke run.

## Main Conclusion
- The recent hidden-source supervision sweeps did not fail because one last loss variant was missing.
- They failed because the producer-side branch never had direct access to the signal class it was being asked to compress.
- Once a dedicated waveform-frame encoder was introduced, the deployable fine-structure code immediately jumped from the `~0.005` regime to the `~0.545` regime on the same oracle.
- This is the first producer-side result that materially clears the old oracle gate without relying on analysis-only reference leakage.

## Next Recommended Direction
- Stop broad Stage3 supervision sweeps over the old hidden-source path.
- Make `waveform_frame_encoder_v1 + waveform_geometry_code_v1` the new upstream main line.
- Move directly to bounded Stage5 dataset-loop integration on top of the new `streaming_student_waveform_geometry_code_v1` consumer.
- Compare that deployable route against:
  - the same-slice Stage5 baseline without geometry code
  - the analysis-only `streaming_student_waveform_pca_code_v1` upper bound
- Only after that comparison decide whether listening review is warranted.
