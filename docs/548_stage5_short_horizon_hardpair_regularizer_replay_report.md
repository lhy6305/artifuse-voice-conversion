# 548 Stage5 Short Horizon Hardpair Regularizer Replay Report

## Summary
- This round follows the corrected `547` guidance:
  - re-anchor from the stable pre-drift `templatepush_b` frontier
  - compare blocker-specific regularizer behavior against matched plain continuation
  - inspect the shortest possible horizon before the known later drift basin dominates the reading
- No new training was opened.
- Instead, existing `step1`, `step2`, and `step3` checkpoints from:
  - plain continuation control
  - `hardpairspeca`
  were replayed on the full active `5`-record slice under the same real `rectangular_overlap_count_norm` no-gate export contract.
- Result:
  - both families preserve `0/5 auto_reject` through `step3`
  - `step1` is effectively identical between focused regularizer and plain continuation
  - `step2` shows a small transient focused de-sharing advantage on decoded peak overlap
  - that advantage disappears again by `step3`
- Therefore:
  - the current hard-pair regularizer family still does not show a robust mechanism-specific advantage
  - at most, it shows a narrow transient early-step side signal that is too small and too unstable to promote as a new main route

## Replayed Artifacts
- Plain continuation control:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_full5_templatepushb_contcontrol_step1_rectgateoff_round1_1`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_full5_templatepushb_contcontrol_step2_rectgateoff_round1_1`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_full5_templatepushb_contcontrol_step3_rectgateoff_round1_1`
- Hard-pair focused regularizer:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_full5_hardpairspeca_step1_rectgateoff_round1_1`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_full5_hardpairspeca_step2_rectgateoff_round1_1`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_full5_hardpairspeca_step3_rectgateoff_round1_1`
- Source-filter reviews:
  - `reports/runtime/stage5_source_filter_review_reviewslice_full5_templatepushb_contcontrol_step1_rect_r1_1`
  - `reports/runtime/stage5_source_filter_review_reviewslice_full5_templatepushb_contcontrol_step2_rect_r1_1`
  - `reports/runtime/stage5_source_filter_review_reviewslice_full5_templatepushb_contcontrol_step3_rect_r1_1`
  - `reports/runtime/stage5_source_filter_review_reviewslice_full5_hardpairspeca_step1_rect_r1_1`
  - `reports/runtime/stage5_source_filter_review_reviewslice_full5_hardpairspeca_step2_rect_r1_1`
  - `reports/runtime/stage5_source_filter_review_reviewslice_full5_hardpairspeca_step3_rect_r1_1`

## Real Export Reading
- Through `step3`, both families still keep:
  - `0/5 auto_reject`
  - `5/5 review_required`
- The near-open control `target::chapter3_30_firefly_132` is still preserved through `step3` in both families.
- Aggregate machine-side metrics improve steadily relative to the original `templatepush_b` frontier in both families:
  - baseline `templatepush_b`:
    - `decoded_template_cosine_mean = 0.968295`
    - `decoded_vuv_high_band_ratio_mean = 0.111866`
    - `decoded_vuv_centroid_gap_hz_mean = 1206.279004`
  - plain continuation `step3`:
    - `0.934805`
    - `0.197204`
    - `2157.768750`
  - focused regularizer `step3`:
    - `0.934831`
    - `0.197103`
    - `2156.067285`
- So the short-horizon story is not "regularizer vs no regularizer".
- The dominant effect is:
  - both short continuations leave the original `templatepush_b` machine frontier
  - both stay in the still-safe `0/5 auto_reject` region up to `step3`

## Stepwise Comparison

### Step1
- Plain continuation and `hardpairspeca` are effectively identical.
- Representative values:
  - `decoded_template_cosine_mean`:
    - control `0.959899`
    - focused `0.959932`
  - `decoded_vuv_high_band_ratio_mean`:
    - control `0.135782`
    - focused `0.135712`
  - `132 decoded_frame_template_cosine_mean`:
    - control `0.929079`
    - focused `0.929140`
  - hard-pair decoded peak-set Jaccard `114/105`:
    - both `0.6`
- Reading:
  - no meaningful regularizer-specific separation is visible at `step1`

### Step2
- This is the only point where a small focused advantage appears.
- Export-side statuses remain identical:
  - both `0/5 auto_reject`
  - both keep `132` as `review_required`
- Aggregate decoded template and per-record template values are still nearly identical:
  - control `decoded_template_cosine_mean = 0.948775`
  - focused `0.948805`
  - control `132 decoded_frame_template_cosine_mean = 0.908469`
  - focused `0.908523`
- The only visible focused gain is on cross-record decoded peak sharing:
  - control mean decoded peak-set Jaccard `0.628687`
  - focused `0.565253`
- But even here:
  - hard-pair `114/105` Jaccard stays identical at `0.6`
  - no export status changes
  - no clear record-level opening appears
- Reading:
  - there is a real but narrow transient focused de-sharing signal at `step2`
  - it is not yet a blocker-opening signal

### Step3
- The transient `step2` advantage disappears again.
- Representative values:
  - control mean decoded peak-set Jaccard `0.583030`
  - focused `0.583030`
  - control `132 decoded_frame_template_cosine_mean = 0.882676`
  - focused `0.882719`
  - control `114 decoded_frame_template_cosine_mean = 0.960311`
  - focused `0.960352`
  - control `105 decoded_frame_template_cosine_mean = 0.936148`
  - focused `0.936183`
- Reading:
  - by `step3`, the focused family is again functionally indistinguishable from plain continuation

## Corrected Interpretation
- `547` showed that long-horizon post-`templatepush_b` basin change was mostly continuation drift.
- `548` refines that again:
  - even before the known later drift basin takes over, the current hard-pair regularizer does not produce a stable differentiated trajectory
  - its only visible effect is a small `step2` drop in mean decoded peak overlap
  - that effect is not durable by `step3`
- Therefore the current family should not be described as:
  - a confirmed blocker-specific breakthrough
  - a validated replacement for plain continuation
  - or a distinct route-opening mechanism

## Decision
- Keep:
  - the conclusion that any future same-anchor comparison must be step-matched and control-matched
  - the observation that `step2` contains a small transient focused de-sharing signal worth remembering
- Do not keep:
  - the current `hardpairspeca` objective family as a new default continuation line
  - the assumption that the existing focused logspec penalty is enough to separate `114/105` in a durable way

## Recommended Next Action
- Do not continue the current focused logspec regularizer family by inertia.
- If this family is revisited at all:
  - treat `step2` as the only checkpoint worth bounded listening review
  - and compare it only against the matched `step2` plain continuation control
- If the project wants a new blocker-specific route:
  - use a materially different mechanism than the current logspec pairwise excess penalty
  - still require explicit `132` preservation
  - still require matched no-op continuation control in the same round
