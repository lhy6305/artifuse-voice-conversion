# 547 Stage5 Templatepushb Continuation Control Vs Crossrecord Regularizer Report

## Summary
- This round closes the missing causal-control gap left by `546`.
- `546` compared new cross-record regularizer runs only against the original `templatepush_b` checkpoint, but not against a matched plain continuation from the same `templatepush_b.step8` anchor.
- That missing control is now executed and replayed on the same full active `5`-record slice.
- Result:
  - plain continuation alone reproduces the same full5 regression that was previously attributed to the regularizer family
  - the regularizer runs stay only second-order different from that plain continuation basin
  - therefore the main `546` causal claim must be narrowed: the observed basin shift is primarily continuation drift from the unstable `templatepush_b` frontier, not a clean regularizer-specific effect

## Executed Continuation Control
- Control training run:
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepushb_contcontrol_round1_1`
- Init checkpoint:
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepushb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- Dataset:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_hardpaircontrol4_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- This control exactly matches the same `hardpaircontrol4` continuation setup used by the `crossrecordspec*` and `hardpairspec*` families except that:
  - `waveform_decoder_base_logits_cross_record_logspec_template_weight = 0.0`
  - `waveform_frames_cross_record_logspec_template_weight = 0.0`
  - `cross_record_logspec_focus_record_ids = []`
- Best checkpoint:
  - step `8`

## Full5 Replay Artifacts
- Real export:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_full5_templatepushb_contcontrol_rectgateoff_round1_1`
- Source-filter review:
  - `reports/runtime/stage5_source_filter_review_reviewslice_full5_templatepushb_contcontrol_rect_r1_1`
- Handoff probe:
  - `reports/runtime/stage5_waveform_handoff_probe_reviewslice_full5_templatepushb_contcontrol_rectcontract_r1_1`
- Structure probe:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_reviewslice_full5_templatepushb_contcontrol_r1_1`

## Real Export Comparison
- `templatepush_b` full5 real export:
  - `0/5 auto_reject + 5/5 review_required`
- Plain continuation control:
  - `1/5 auto_reject + 4/5 review_required`
- `crossrecordspeca`:
  - `1/5 auto_reject + 4/5 review_required`
- `hardpairspeca`:
  - `1/5 auto_reject + 4/5 review_required`
- The regressed record is the same in all three post-step8 continuations:
  - `target::chapter3_30_firefly_132`

## Aggregate Comparison
- Relative to `templatepush_b`, plain continuation alone already reproduces the same basin shift:
  - `decoded_template_cosine_mean = 0.968295 -> 0.802061`
  - `decoded_vuv_high_band_ratio_mean = 0.111866 -> 0.262307`
  - `decoded_vuv_centroid_gap_hz_mean = 1206.279004 -> 2620.503418`
  - mean decoded peak-set Jaccard `0.773333 -> 0.504242`
- The regularizer families stay extremely close to that plain continuation basin:
  - `crossrecordspeca decoded_template_cosine_mean = 0.802901`
  - `hardpairspeca decoded_template_cosine_mean = 0.802036`
  - `crossrecordspeca decoded_vuv_high_band_ratio_mean = 0.265358`
  - `hardpairspeca decoded_vuv_high_band_ratio_mean = 0.262423`
  - `crossrecordspeca decoded_vuv_centroid_gap_hz_mean = 2668.964160`
  - `hardpairspeca decoded_vuv_centroid_gap_hz_mean = 2622.227051`
  - all three post-step8 continuations keep hard-pair decoded peak-set Jaccard at `1.0` for `114/105`

## Record-Level Reading
- The per-record differences between plain continuation and the regularizer runs are small.
- For the regressed near-open control `target::chapter3_30_firefly_132`:
  - plain continuation:
    - `decoded_frame_template_cosine_mean = 0.651960`
    - `decoded_frame_rms_to_aligned_frame_rms_corr = 0.631803`
  - `crossrecordspeca`:
    - `0.652881`
    - `0.645352`
  - `hardpairspeca`:
    - `0.651892`
    - `0.633132`
- Other records also stay near-identical in status and metric scale across the three post-step8 continuations.

## Handoff And Structure Comparison
- Plain continuation reproduces the same internal basin that `546` previously attributed to the regularizer family:
  - handoff `waveform_frame_logits_template_cosine_mean = 0.804718`
  - handoff `waveform_frames_template_cosine_mean = 0.789449`
  - handoff `decoded_no_gate auto_reject_count = 1`
  - handoff `decoded_no_gate decoded_frame_template_cosine_mean = 0.802061`
  - handoff `decoded_no_gate decoded_frame_rms_to_aligned_frame_rms_corr = 0.486976`
- Those numbers are nearly identical to `crossrecordspeca`:
  - `0.805198`
  - `0.790112`
  - `1`
  - `0.802902`
  - `0.493782`
- The structure probe also lands in the same localization:
  - coupling diagnosis remains `decoder_hidden_to_base_logits_is_main_coupling_amplifier`
  - geometry diagnosis remains `decoder_hidden_to_base_logits_is_main_geometry_collapse`
  - plain continuation `decoder_to_base_logits_template_distance_drop = -3.679934`
  - `crossrecordspeca decoder_to_base_logits_template_distance_drop = -3.675515`
- Variant ranking also stays dominated by the same projection family:
  - plain continuation baseline decoded template cosine `0.789769`
  - plain continuation `waveform_decoder_base_logits_only = 0.790023`
  - plain continuation `fused_hidden_from_branch_mean = 0.806338`

## Corrected Interpretation
- `546` still established something useful at the code level:
  - the new batch regularizer path is implemented and valid
- But the original causal reading is now too strong:
  - we cannot say the new regularizer family is what moved the route from the `templatepush_b` basin to the later `1/5 auto_reject` basin
  - a matched no-regularizer continuation from the same anchor already makes that same move
- The corrected reading is:
  - `templatepush_b.step8` is an unstable frontier under further same-scope continuation
  - plain continuation naturally drifts into a lower-template, higher-high-band, `132`-regressing basin
  - the current regularizer variants mostly ride on top of that drift and change only second-order details

## Decision
- Supersede the strong causal wording from `546`.
- Keep:
  - the cross-record regularizer code path
  - the observation that the post-step8 basin is different from the original `templatepush_b` basin
- Do not keep:
  - the claim that the regularizer itself is the main cause of that basin shift
  - the claim that the regularizer family has yet shown a distinct route-opening advantage over matched plain continuation

## Recommended Next Action
- Do not continue judging new same-anchor families without a matched no-op continuation control.
- Do not continue the current cross-record regularizer family by inertia.
- If pair-specific anti-collapse work continues, re-anchor from the stable pre-drift `templatepush_b` frontier and require explicit control preservation for `target::chapter3_30_firefly_132`.
- More broadly:
  - treat the active issue as post-frontier continuation instability at the same `decoder_hidden -> waveform_decoder_base_logits` bottleneck
  - not as a validated regularizer-led de-sharing breakthrough
