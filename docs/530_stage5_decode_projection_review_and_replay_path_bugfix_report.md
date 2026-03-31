# 530 Stage5 Decode Projection Review And Replay Path Bugfix Report

## Summary
- This round tightened the new downstream Stage5 blocker after `529`.
- Two things were completed:
  - fixed a replay-path bug in `stage5_vuv_path_probe`
  - added a new decode-side review probe that isolates `decoded_no_gate`, `decoded_pre_ola_gate`, and `decoded_post_ola_gate`
- The bugfix matters because the first `529` replay mixed:
  - new internal activations from the replayed checkpoint
  - old `decoded.wav` from the original baseline review bundle
- After the bugfix, the corrected `delta_direct_v1` replay is much sharper:
  - aggregate waveform-frames `vuv` high-band gap stays positive at `0.002642`
  - corrected aggregate decoded `vuv` high-band gap is `-0.066452`, not `-0.001537`
- The new decode-side route decomposition then shows:
  - `decoded_no_gate = -0.066444`
  - `decoded_pre_ola_gate = -0.066328`
  - `decoded_post_ola_gate = -0.066453`
- So the current blocker is now more specific than "some downstream decode issue":
  - Hann overlap-add or equivalent frame-reconstruction geometry already destroys the rescued `vuv` separation before predicted activity gating
  - gate application mode is only a tiny second-order difference on top of that collapse

## Code Change
- Fixed `stage5_vuv_path_probe` so replayed decoded and aligned audio now resolve from the active export manifest first instead of blindly reusing the review-bundle paths:
  - `src/v5vc/stage5_vuv_path_probe.py`
- Added a new reusable decode-side review probe:
  - `src/v5vc/stage5_vuv_decode_projection_probe.py`
- Added CLI entrypoint:
  - `analyze-stage5-nores-vuv-decode-projection-review`
  - wiring in `src/v5vc/cli.py`

## Corrected Replay Artifacts
- Corrected gate-bias replay:
  - `reports/runtime/stage5_vuv_path_review_bundle_reviewslice_noisehidden_gatebias_round1_2/stage5_vuv_path_review.md`
- Corrected delta-direct replay:
  - `reports/runtime/stage5_vuv_path_review_bundle_reviewslice_noisehidden_deltadirect_round1_2/stage5_vuv_path_review.md`
- Corrected hybrid replay:
  - `reports/runtime/stage5_vuv_path_review_bundle_reviewslice_noisehidden_hybrid_round1_2/stage5_vuv_path_review.md`

## New Decode-Projection Review Artifacts
- Baseline review slice:
  - `reports/runtime/stage5_vuv_decode_projection_review_streaming_student_energypeak_fusionresshape050_round1_1/stage5_vuv_decode_projection_review.md`
- `delta_direct_v1` review slice:
  - `reports/runtime/stage5_vuv_decode_projection_review_reviewslice_noisehidden_deltadirect_round1_1/stage5_vuv_decode_projection_review.md`

## Corrected Vuv-Path Replay Reading
- `gate_bias_only_v1`
  - waveform-frames aggregate `vuv` gap: `-0.003188`
  - corrected decoded aggregate `vuv` gap: `-0.001538`
  - reading:
    - still flat and not competitive
- `gate_plus_delta_v1`
  - waveform-frames aggregate `vuv` gap: `-0.003213`
  - corrected decoded aggregate `vuv` gap: `-0.001618`
  - reading:
    - still flat and not competitive
- `delta_direct_v1`
  - waveform-frames aggregate `vuv` gap: `0.002642`
  - corrected decoded aggregate `vuv` gap: `-0.066452`
  - corrected primary localization:
    - `decoded_waveform_vuv_separation_lost_after_frame_projection`
- Practical implication:
  - the positive `waveform_frames` rescue from `529` was real
  - but the original decoded-side numeric reading in `529` was too optimistic because it was still reading stale baseline audio

## Baseline Decode-Projection Reference
- Current baseline remains upstream-blocked:
  - aggregate waveform-frames `vuv` gap: `-0.003187`
  - `decoded_no_gate = -0.001495`
  - `decoded_pre_ola_gate = -0.001470`
  - `decoded_post_ola_gate = -0.001538`
- Since baseline waveform-frames are already non-positive on `5/5`, this run is only a reference for route behavior, not the new mainline blocker proof.

## Delta-Direct Decode-Projection Result
- Aggregate:
  - aligned target `vuv` gap: `0.099338`
  - waveform-frames `vuv` gap: `0.002642`
  - `decoded_no_gate`: `-0.066444`
  - `decoded_pre_ola_gate`: `-0.066328`
  - `decoded_post_ola_gate`: `-0.066453`
- Record counts:
  - waveform-frames non-positive count: `2/5`
  - `decoded_no_gate` non-positive count: `5/5`
  - `decoded_pre_ola_gate` non-positive count: `5/5`
  - `decoded_post_ola_gate` non-positive count: `5/5`
- Record-level localization:
  - `target::chapter3_30_firefly_132`
    - waveform-frames `0.007480`
    - `decoded_no_gate -0.084459`
  - `target::chapter3_26_firefly_114`
    - waveform-frames `0.005468`
    - `decoded_no_gate -0.062534`
  - `target::chapter4_7_firefly_105`
    - waveform-frames `0.003489`
    - `decoded_no_gate -0.076168`

## Reading
- The new explicit direct-delta branch really does rescue the local frame-space sink.
- But the rescue does not merely fade a little during decode.
- It flips hard in the wrong direction during no-gate overlap-add:
  - aggregate `0.002642 -> -0.066444`
- The gate route then changes almost nothing:
  - `decoded_no_gate` vs `decoded_pre_ola_gate` difference is only `0.000116`
  - `decoded_no_gate` vs `decoded_post_ola_gate` difference is only `0.000009`
- Therefore the current main blocker is not:
  - gate-floor tuning
  - pre-vs-post gate mode debate
  - or another pass over residual carrier sourcing
- The current main blocker is:
  - frame reconstruction itself
  - more concretely, the frame-overlap-add or equivalent waveform projection path that turns a slightly positive frame-space `vuv` contrast into a strongly negative decoded one

## Decision
- Keep `delta_direct_v1` as the validated local rescue branch.
- Treat the old `529` decoded-side replay number as superseded.
- Retire decode-side gate speculation for this line:
  - the route is already broken at `decoded_no_gate`
  - pre-OLA and post-OLA gate semantics are nearly identical on the corrected delta-direct replay

## Recommended Next Action
- Open the next bounded Stage5 probe directly on frame reconstruction geometry after `waveform_frames`.
- The next high-value targets are:
  - Hann window and overlap-add interaction
  - frame-to-waveform reconstruction contract
  - explicit cross-frame continuity or anti-cancellation structure
- Do not spend the next round on:
  - predicted-activity gate tuning
  - more `noise_hidden` carrier sourcing
  - more residual-adapter feature shuffling
