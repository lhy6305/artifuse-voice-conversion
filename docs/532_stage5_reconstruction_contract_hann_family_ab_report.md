# 532 Stage5 Reconstruction Contract Hann Family AB Report

## Summary
- This round executed the next narrower reconstruction-contract AB after `531`.
- The question was:
  - is the current sink mainly the Hann window itself
  - or can a nearby Hann-family normalization rule recover the rescued frame-space `vuv` separation without leaving the Hann family
- The answer on the corrected `delta_direct_v1` review slice is now clear:
  - the whole current Hann family stays negative
  - `rectangular_overlap_count_norm` remains the only strong positive reconstruction contract
- Aggregate `vuv` high-band gaps:
  - waveform-frames: `0.002642`
  - current `hann_window_sum_norm`: `-0.066444`
  - `hann_overlap_count_norm`: `-0.049303`
  - `hann_window_square_norm`: `-0.059694`
  - `sqrt_hann_window_square_norm`: `-0.027126`
  - `rectangular_overlap_count_norm`: `0.017643`
- So the new conclusion is:
  - this is not just a normalization bug inside the current Hann contract
  - the current Hann-window reconstruction family itself is the main localized sink on this review slice

## Code Change
- Added reusable reconstruction-contract AB probe:
  - `src/v5vc/stage5_vuv_reconstruction_contract_probe.py`
- Added CLI entrypoint:
  - `analyze-stage5-nores-vuv-reconstruction-contract-review`
- CLI wiring lives in:
  - `src/v5vc/cli.py`

## Variants
- `hann_window_sum_norm`
  - current no-gate decode contract
- `hann_overlap_count_norm`
  - Hann synthesis window with plain overlap-count normalization
- `hann_window_square_norm`
  - Hann synthesis window with window-square normalization
- `sqrt_hann_window_square_norm`
  - square-root Hann with window-square normalization
- `rectangular_overlap_count_norm`
  - rectangular overlap averaging positive control

## Probe Run
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-vuv-reconstruction-contract-review --output-dir reports/runtime/stage5_vuv_reconstruction_contract_review_reviewslice_noisehidden_deltadirect_round1_1 --review-bundle reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json --audio-export-manifests reports/runtime/offline_mvp_nores_vocoder_audio_export_reviewslice_noisehidden_deltadirect_round1_1/nores_vocoder_audio_export.json`
- Output:
  - `reports/runtime/stage5_vuv_reconstruction_contract_review_reviewslice_noisehidden_deltadirect_round1_1/stage5_vuv_reconstruction_contract_review.json`
  - `reports/runtime/stage5_vuv_reconstruction_contract_review_reviewslice_noisehidden_deltadirect_round1_1/stage5_vuv_reconstruction_contract_review.md`

## Aggregate Reading
- Mainline reference:
  - waveform-frames aggregate `vuv` gap: `0.002642`
- Hann-family results:
  - `hann_window_sum_norm = -0.066444`
  - `hann_overlap_count_norm = -0.049303`
  - `hann_window_square_norm = -0.059694`
  - `sqrt_hann_window_square_norm = -0.027126`
- Positive control:
  - `rectangular_overlap_count_norm = 0.017643`

## What Improved And What Did Not
- The best Hann-family rescue is:
  - `sqrt_hann_window_square_norm`
- It is materially better than the current contract:
  - `-0.027126` vs `-0.066444`
- But it still fails decisively:
  - still negative on aggregate
  - still negative on all `5/5` reviewed records
- `rectangular_overlap_count_norm` remains qualitatively different:
  - positive on aggregate
  - positive on all `5/5` reviewed records

## Record-Level Reading
- For the three records that became clearly positive in frame space under `delta_direct_v1`, every Hann-family variant stays negative while the rectangular positive control stays positive:
  - `target::chapter3_30_firefly_132`
    - waveform-frames `0.007480`
    - best Hann neighbor `sqrt_hann_window_square_norm = -0.035995`
    - rectangular `0.023590`
  - `target::chapter3_26_firefly_114`
    - waveform-frames `0.005468`
    - best Hann neighbor `sqrt_hann_window_square_norm = -0.018062`
    - rectangular `0.025381`
  - `target::chapter4_7_firefly_105`
    - waveform-frames `0.003489`
    - best Hann neighbor `sqrt_hann_window_square_norm = -0.034082`
    - rectangular `0.017050`

## Interpretation
- `531` already proved that the current Hann no-gate reconstruction is much worse than rectangular overlap averaging.
- `532` now proves that the issue is not rescued by the most obvious nearby Hann-family normalization changes.
- Therefore:
  - the next practical AB should not keep circling inside tiny Hann normalization rewrites alone
  - the first real export-contract candidate worth carrying forward is rectangular overlap averaging

## Decision
- Keep `rectangular_overlap_count_norm` as the first strong reconstruction-contract positive control.
- Retire the assumption that a small normalization tweak inside the current Hann family is likely enough.
- Keep `sqrt_hann_window_square_norm` only as a weak neighbor reference, not as the next mainline candidate.

## Recommended Next Action
- Open a bounded export-side contract AB that promotes `rectangular_overlap_count_norm` into a real decode option on the same review slice.
- Use that AB to answer the next question:
  - does the rectangular contract still look positive once it is treated as the actual decoded route rather than only a counterfactual probe
- Do not spend the next round on:
  - more gate tuning
  - more `noise_hidden` sourcing
  - more residual-adapter routing
  - more tiny Hann normalization permutations without a new positive signal
