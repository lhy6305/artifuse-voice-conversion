# 545 Stage5 TemplatepushB Crossrecord Resonance Trap Localization Report

## Summary
- This round continues the post-`544` structural localization.
- The goal is no longer to prove that `templatepush_b` improves machine metrics.
- That point is already settled by `542` to `544`.
- The active question is narrower:
  - why does `templatepush_b` reduce template-collapse severity and improve energy following
  - while all `5` decoded outputs still remain pure buzz under human review
- The updated answer is:
  - the route is still trapped in a shared cross-record resonance template
  - the dominant bottleneck is still the `decoder_hidden -> waveform_decoder_base_logits` projection
  - `templatepush_b` lowers within-record collapse metrics without creating record-specific speech structure

## Inputs Reviewed
- Human review conclusion from `544`:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_full5_templatepushb_rectgateoff_round1_1`
- Full5 handoff probe for `templatepush_b` under aligned rectangular reconstruction:
  - `reports/runtime/stage5_waveform_handoff_probe_reviewslice_full5_templatepushb_rectcontract_r1_1`
- Full5 structure probe for `templatepush_b`:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_reviewslice_full5_templatepushb_r1_1`
- Full5 source-filter reviews used for cross-record peak overlap comparison:
  - old `539` frontier:
    - `reports/runtime/stage5_source_filter_review_reviewslice_full5_producerinterface_rect_r1_1`
  - new `templatepush_b` frontier:
    - `reports/runtime/stage5_source_filter_review_reviewslice_full5_templatepushb_rect_r1_1`

## Human Review Anchor
- `544` already settles the perceptual conclusion:
  - all `5` decoded outputs remain pure buzz
  - energy-following fluctuation is somewhat stronger
  - spectrograms still show uniform stripe bands
  - some short sand-like regions appear
  - no stable speech structure appears
  - no region sounds human-like
- Therefore this report does not ask whether the route is "better".
- It asks why the route is still non-speech despite the machine-side gain.

## Handoff Improvement Is Real But Not Sufficient
- Relative to corrected `539`, the aligned full5 handoff probe still shows real improvement:
  - `waveform_frame_logits_template_cosine_mean = 0.990774 -> 0.971137`
  - `waveform_frames_template_cosine_mean = 0.989148 -> 0.967072`
  - `decoded_no_gate auto_reject_count = 3 -> 0`
  - `decoded_no_gate decoded_frame_template_cosine_mean = 0.985812 -> 0.968295`
- So the machine-side gain is not a fake threshold-only artifact.
- But human review says the gain still does not cross into speech.

## Cross-Record Peak Collapse Still Strengthens
- Cross-record decoded resonance peaks remain highly shared across records.
- Mean pairwise decoded peak-set Jaccard rises from `0.707` on corrected `539` to `0.773` on `templatepush_b`.
- Mean aligned-target peak-set Jaccard on the same `5` records is only `0.116`.
- The strongest evidence is that several decoded record pairs now share identical peak sets:
  - `target::no_text_voice/chapter3_21_firefly_108` vs `target::chapter3_26_firefly_114`: `1.0`
  - `target::no_text_voice/chapter3_21_firefly_108` vs `target::chapter4_7_firefly_105`: `1.0`
  - `target::chapter3_26_firefly_114` vs `target::chapter4_7_firefly_105`: `1.0`
- Those same aligned-target pairs remain far apart:
  - `0.143`
  - `0.067`
  - `0.231`
- This means `templatepush_b` is not generating record-specific speech structure.
- It is generating a slightly less harsh but still strongly shared stripe or comb pattern.

## Structure Localization Still Points To The Same Bottleneck
- The full5 structure probe does not relocate the main collapse site.
- Baseline decoder-collapse summary now reads:
  - `fused_hidden_template_cosine_mean = 0.981582`
  - `waveform_frames_template_cosine_mean = 0.969611`
  - `decoded_frames_template_cosine_mean = 0.963064`
  - diagnosis: `collapse_not_localized_to_waveform_decoder`
- Upstream coupling localization still reads:
  - `strongest_transition = decoder_to_base_logits`
  - `decoder_to_base_logits_voicing_corr_jump = 1.178460`
  - diagnosis: `decoder_hidden_to_base_logits_is_main_coupling_amplifier`
- Geometry localization also still reads:
  - `strongest_transition = decoder_to_base_logits`
  - `decoder_to_base_logits_effective_rank_drop = 0.024176`
  - `decoder_to_base_logits_template_distance_drop = -1.463558`
  - diagnosis: `decoder_hidden_to_base_logits_is_main_geometry_collapse`
- Compared with corrected `539`, the main location stays the same while the template-distance drop becomes even more extreme:
  - corrected `539`: `-0.783778`
  - `templatepush_b`: `-1.463558`

## Variant Reading Still Supports A Fixed Resonance Projector Basin
- Variant ranking continues to support the same interpretation.
- `waveform_decoder_base_logits_only` is still almost identical to baseline on decoded template collapse:
  - baseline decoded template cosine `0.963064`
  - `waveform_decoder_base_logits_only` decoded template cosine `0.963293`
- `fused_hidden_from_branch_mean` is also near-baseline:
  - decoded template cosine `0.962831`
- `waveform_residual_shape_only` still collapses almost completely:
  - decoded template cosine `0.999405`
- So the residual-shape path still does not carry speech by itself, while the base-logits path still dominates what is heard.

## Updated Interpretation
- `templatepush_b` should now be read as:
  - lower within-record template-collapse severity
  - better energy-following
  - lower harshness
  - but continued attraction into a shared cross-record resonance template
- This is consistent with the human review:
  - buzz becomes a little more animated
  - but does not become speech
- The missing ingredient is not another small reduction in template-collapse magnitude.
- The missing ingredient is record-specific speech-structure formation before or at the `decoder_hidden -> waveform_decoder_base_logits` projection.

## Decision
- Keep:
  - `templatepush_b` as the strongest bounded machine-side frontier so far
  - the conclusion that focused hard-pair pressure can move the route materially
- Retire:
  - any idea that `templatepush_b` is near-speech
  - any plan to keep escalating the same template-push family without a new structure hypothesis
  - any interpretation that lower decoded template cosine alone proves speech emergence

## Recommended Next Action
- Do not broaden replay yet.
- Do not run another same-family template-push continuation first.
- The next bounded move should target breaking the shared cross-record resonance template at the active bottleneck:
  - `decoder_hidden -> waveform_decoder_base_logits`
- The next experiment family should be judged by whether it increases record-specific decoded structure, not only by whether it lowers current collapse scalars further.
