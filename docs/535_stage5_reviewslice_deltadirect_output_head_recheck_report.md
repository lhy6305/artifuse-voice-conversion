# 535 Stage5 Review-Slice Delta-Direct Output-Head Recheck Report

## Summary
- This round executed the next bounded recheck after `534`.
- The remaining question was:
  - after rectangular reconstruction is no longer the main unknown
  - does the active `delta_direct_v1` review-slice route still fail mainly because of:
    - `tanh` saturation at the final frame activation
    - or the upstream `decoder_hidden -> waveform_decoder_base_logits` projection itself
- Two existing probes were re-run on the current `5`-record review slice:
  - `analyze-stage5-nores-waveform-handoff`
  - `analyze-stage5-nores-waveform-decoder-structure`
- The combined answer is now sharp:
  - `tanh` is not the main new collapse site on the current route
  - logit saturation pressure is also not the main issue
  - the strongest current collapse and control distortion still localize to `decoder_hidden -> waveform_decoder_base_logits`
  - the current output head behaves close to a fixed-template projector around the active operating region

## Probe Runs

### Review-slice waveform handoff recheck
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-waveform-handoff --output-dir reports/runtime/stage5_waveform_handoff_probe_reviewslice_noisehidden_deltadirect_r1_1 --checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_noisehidden_deltadirect_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --split-name validation --sample-count 5 --device cpu --predicted-activity-gate-floor 0.0 --predicted-activity-gate-smoothing-frames 3`
- Output:
  - `reports/runtime/stage5_waveform_handoff_probe_reviewslice_noisehidden_deltadirect_r1_1/stage5_waveform_handoff_probe.json`
  - `reports/runtime/stage5_waveform_handoff_probe_reviewslice_noisehidden_deltadirect_r1_1/stage5_waveform_handoff_probe.md`

### Review-slice waveform decoder structure recheck
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-waveform-decoder-structure --output-dir reports/runtime/stage5_waveform_decoder_structure_probe_reviewslice_noisehidden_deltadirect_r1_1 --checkpoint reports/runtime/offline_mvp_nores_vocoder_reviewslice_noisehidden_deltadirect_microfit_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt --dataset-index reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json --split-name validation --sample-count 5 --device cpu --predicted-activity-gate-floor 0.0 --predicted-activity-gate-smoothing-frames 3`
- Output:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_reviewslice_noisehidden_deltadirect_r1_1/stage5_waveform_decoder_structure_probe.json`
  - `reports/runtime/stage5_waveform_decoder_structure_probe_reviewslice_noisehidden_deltadirect_r1_1/stage5_waveform_decoder_structure_probe.md`

## Handoff Recheck Reading
- Aggregate review-slice handoff result:
  - `tanh_is_main_new_collapse_site = false`
  - `logits_show_heavy_saturation_pressure = false`
- Key stage metrics:
  - `waveform_frame_logits_template_cosine_mean = 0.993400`
  - `waveform_frames_template_cosine_mean = 0.992189`
  - `logits_to_frames_template_cosine_gap = -0.001211`
  - `waveform_frame_logits_fraction_abs_ge_1 = 0.070934`
  - `waveform_frame_logits_fraction_abs_ge_2 = 0.001039`
  - `waveform_frame_logits_fraction_abs_ge_3 = 0.0`
- Reading:
  - the final `tanh` only changes template collapse at second-order scale on this route
  - logits are not heavily saturated
  - the collapse is already present before the final activation

## Structure Recheck Reading
- Baseline decoder collapse summary:
  - `fused_hidden_template_cosine_mean = 0.982696`
  - `waveform_frames_template_cosine_mean = 0.992756`
  - `fused_to_waveform_template_cosine_gap = 0.010060`
  - diagnosis:
    - `collapse_not_localized_to_waveform_decoder`
- Baseline coupling localization:
  - `decoder_to_base_logits_voicing_corr_jump = 0.511328`
  - `decoder_to_base_logits_abs_aper_corr_jump = 0.710864`
  - `strongest_transition = decoder_to_base_logits`
  - diagnosis:
    - `decoder_hidden_to_base_logits_is_main_coupling_amplifier`
- Baseline geometry localization:
  - `decoder_to_base_logits_effective_rank_drop = 0.023670`
  - `decoder_to_base_logits_template_distance_drop = -0.666438`
  - `strongest_transition = decoder_to_base_logits`
  - diagnosis:
    - `decoder_hidden_to_base_logits_is_main_geometry_collapse`

## Variant Reading
- `waveform_decoder_base_logits_only`
  - `mean_waveform_mean_abs_delta_vs_baseline = 0.003795`
  - `mean_waveform_frames_template_cosine_mean = 0.992804`
  - `mean_decoded_frame_template_cosine_mean = 0.983060`
- Reading:
  - removing residual-shape injection barely changes the route
  - the main failure is not primarily carried by the residual-shape branch
- `waveform_residual_shape_only`
  - `mean_waveform_frames_template_cosine_mean = 0.999503`
  - `mean_decoded_frame_template_cosine_mean = 0.999433`
- Reading:
  - the residual-shape branch alone is an even harder fixed-template non-speech path
- `fused_hidden_frame_mean`
  - `mean_waveform_mean_abs_delta_vs_baseline = 0.012394`
  - `mean_waveform_frames_template_cosine_mean = 1.000000`
  - `mean_decoded_frame_template_cosine_mean = 0.998379`
- Reading:
  - collapsing fused-hidden temporal dynamics barely changes the heard route
  - this is strong evidence that the current output head already acts close to a fixed-template projector around the active operating region

## Combined Interpretation
- `534` proved that rectangular reconstruction preserves decoded `vuv` rescue while the route still fails from waveform-frame template collapse.
- `535` now sharpens the generator-side conclusion:
  - the remaining blocker is not another reconstruction mystery
  - it is also not mainly the final `tanh`
  - it is not mainly the residual-shape injection branch either
- The dominant current blocker is:
  - the `decoder_hidden -> waveform_decoder_base_logits` output-head projection
  - more specifically, a low-rank, template-heavy projector that discards useful temporal diversity before reconstruction ever starts

## Decision
- Keep rectangular reconstruction as the decoded positive control for the repaired `vuv` path.
- Retire renewed `tanh` saturation speculation on the active review slice.
- Retire renewed residual-shape-only speculation on the active review slice.
- Replace the next-action wording with the sharper target:
  - localize and modify the `decoder_hidden -> waveform_decoder_base_logits` projection head itself

## Recommended Next Action
- Open the next bounded probe or microfit directly on the output-head projection path.
- Good next targets are:
  - output-head trainable-prefix microfit on the review slice
  - stronger base-logits structural losses rather than more reconstruction sweeps
  - direct checks on whether the projection can preserve temporal diversity when supervised against the same repaired local `vuv` route
- Do not spend the next round on:
  - Hann vs rectangular comparison
  - gate-side tuning
  - or generic `tanh` saturation debate
