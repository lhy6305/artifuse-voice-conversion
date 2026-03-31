# 531 Stage5 Frame Reconstruction Geometry Probe Report

## Summary
- This round pushed the downstream blocker one step narrower after `530`.
- The new question was:
  - after `delta_direct_v1` rescues frame-space `vuv` separation
  - which part of frame-to-waveform reconstruction actually destroys it
- A new review-slice reconstruction probe now keeps `waveform_frames` fixed and swaps only the reconstruction geometry.
- Main result:
  - current `hann_ola_baseline` remains the worst route
  - `rectangular_ola` is dramatically better on both the baseline review slice and the `delta_direct_v1` replay
- On the corrected `delta_direct_v1` review slice:
  - waveform-frames aggregate `vuv` high-band gap: `0.002642`
  - `hann_ola_baseline`: `-0.066444`
  - `rectangular_ola`: `0.017643`
  - `hop_stitch`: `-0.001695`
  - `flatten_frames`: `0.000006`
- So the current decode-side blocker is now more specific than generic overlap-add:
  - the active `hann`-windowed reconstruction contract is the main geometry sink
  - simple overlap averaging with a rectangular window already removes most of the failure

## Code Change
- Added reusable frame-reconstruction probe:
  - `src/v5vc/stage5_vuv_frame_reconstruction_probe.py`
- Added CLI entrypoint:
  - `analyze-stage5-nores-vuv-frame-reconstruction-review`
- CLI wiring lives in:
  - `src/v5vc/cli.py`

## Variants
- `hann_ola_baseline`
  - current no-gate decode route
  - Hann-window overlap-add with window-weight normalization
- `rectangular_ola`
  - overlap-add with rectangular window and overlap averaging
- `hop_stitch`
  - stitch the first hop segment from each frame and append the last tail
- `flatten_frames`
  - flatten frames end to end with no overlap-add

## Probe Runs
- Baseline review slice:
  - `.\python.exe manage.py analyze-stage5-nores-vuv-frame-reconstruction-review --output-dir reports/runtime/stage5_vuv_frame_reconstruction_review_streaming_student_energypeak_fusionresshape050_round1_1 --review-bundle reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json --audio-export-manifests reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionresshape050_round1_1/nores_vocoder_audio_export.json reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_se8_fusionresshape050_round1_1/nores_vocoder_audio_export.json`
- `delta_direct_v1` replay slice:
  - `.\python.exe manage.py analyze-stage5-nores-vuv-frame-reconstruction-review --output-dir reports/runtime/stage5_vuv_frame_reconstruction_review_reviewslice_noisehidden_deltadirect_round1_1 --review-bundle reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json --audio-export-manifests reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_noisehidden_deltadirect_round1_1/nores_vocoder_audio_export.json`

## Artifacts
- Baseline:
  - `reports/runtime/stage5_vuv_frame_reconstruction_review_streaming_student_energypeak_fusionresshape050_round1_1/stage5_vuv_frame_reconstruction_review.json`
  - `reports/runtime/stage5_vuv_frame_reconstruction_review_streaming_student_energypeak_fusionresshape050_round1_1/stage5_vuv_frame_reconstruction_review.md`
- `delta_direct_v1`:
  - `reports/runtime/stage5_vuv_frame_reconstruction_review_reviewslice_noisehidden_deltadirect_round1_1/stage5_vuv_frame_reconstruction_review.json`
  - `reports/runtime/stage5_vuv_frame_reconstruction_review_reviewslice_noisehidden_deltadirect_round1_1/stage5_vuv_frame_reconstruction_review.md`

## Baseline Reading
- Baseline remains upstream-blocked:
  - waveform-frames aggregate `vuv` gap: `-0.003187`
- Even so, the reconstruction variants still show a strong geometry effect:
  - `hann_ola_baseline = -0.001495`
  - `rectangular_ola = 0.017801`
  - `hop_stitch = -0.007005`
  - `flatten_frames = -0.000970`
- This means the current reconstruction contract is not neutral even on an already-bad frame-space input.

## Delta-Direct Reading
- `delta_direct_v1` is the mainline case because frame-space was already rescued there:
  - waveform-frames aggregate `vuv` gap: `0.002642`
- Reconstruction comparison:
  - `hann_ola_baseline = -0.066444`
  - `rectangular_ola = 0.017643`
  - `hop_stitch = -0.001695`
  - `flatten_frames = 0.000006`
- Non-positive record counts:
  - waveform-frames: `2/5`
  - `hann_ola_baseline`: `5/5`
  - `rectangular_ola`: `0/5`
  - `hop_stitch`: `3/5`
  - `flatten_frames`: `3/5`

## Record-Level Reading
- The three records that become clearly positive in frame space under `delta_direct_v1` all collapse under `hann_ola_baseline` and all recover under `rectangular_ola`:
  - `target::chapter3_30_firefly_132`
    - waveform-frames `0.007480`
    - `hann_ola_baseline -0.084459`
    - `rectangular_ola 0.023590`
  - `target::chapter3_26_firefly_114`
    - waveform-frames `0.005468`
    - `hann_ola_baseline -0.062534`
    - `rectangular_ola 0.025381`
  - `target::chapter4_7_firefly_105`
    - waveform-frames `0.003489`
    - `hann_ola_baseline -0.076168`
    - `rectangular_ola 0.017050`

## Interpretation
- `530` already showed that the route is broken before predicted activity gating.
- `531` now narrows that further:
  - the main sink is not "all decode"
  - it is specifically the current `hann`-windowed no-gate reconstruction geometry
- `rectangular_ola` being positive on `5/5` in the `delta_direct_v1` replay is strong leverage evidence that the failure is not inherent to the rescued `waveform_frames` themselves.
- At the same time, this is still not a route-opening claim:
  - these are counterfactual reconstruction variants
  - no training or listening confirmation was used here
  - the result is leverage evidence about reconstruction contract, not final deployment proof

## Decision
- Keep `delta_direct_v1` as the validated upstream local rescue branch.
- Retire the generic wording that the next step is just "decode-side".
- Replace it with the sharper statement:
  - the current `hann_ola_baseline` reconstruction contract is the main decode-side sink

## Recommended Next Action
- Open a bounded Stage5 reconstruction-contract AB around the current no-gate decode path.
- The first variants should stay tightly scoped:
  - rectangular overlap averaging
  - Hann normalization alternatives
  - possibly square-root Hann style overlap rules if needed
- Do not spend the next round on:
  - predicted-activity gate tuning
  - carrier sourcing
  - residual-adapter feature routing
  - generic decode-side speculation without window-contract isolation
