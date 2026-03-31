# 528 Stage5 Review-Slice Noise-Hidden Residual Structure Probe Report

## Summary
- This round completed the next structural question after `527`:
  - can the current residual-shape branch-condition adapter already exploit `noise_hidden` if its feature inputs are rerouted more explicitly
- The answer is:
  - only weakly
  - and not enough to reproduce the earlier `noise_hidden` scaling counterfactual
- The best structural reroute on the active `5`-record `fusionbranchmeancontrast_residualshape_scale050` review slice is:
  - `residual_branch_noise_hidden_only`
- But it only moves aggregate waveform-frames `vuv` high-band gap from:
  - baseline `-0.003187`
  - to `-0.002912`
- This remains far behind both comparators:
  - oracle target-side positive control `0.003254`
  - deployable `noise_hidden_rms_soft_residual_gain500` counterfactual `0.003365`
- So the practical result is:
  - `noise_hidden` is still the right upstream carrier
  - but the current residual adapter projection does not unlock it through simple feature rerouting
  - the next valid move now requires an explicit new `noise_hidden -> residual` projection or path, not more gate-side work and not more adapter-input shuffling

## Code Change
- Added reusable structural probe module:
  - `src/v5vc/stage5_vuv_noise_hidden_residual_structure_probe.py`
- Added CLI entrypoint:
  - `analyze-stage5-nores-vuv-noise-hidden-residual-structure-probe`
- CLI wiring lives in:
  - `src/v5vc/cli.py`

## Probe Run
- Command:
  - `.\python.exe manage.py analyze-stage5-nores-vuv-noise-hidden-residual-structure-probe --output-dir reports/runtime/stage5_vuv_noise_hidden_residual_structure_probe_streaming_student_energypeak_fusionresshape050_round1_1 --review-bundle reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json --audio-export-manifests reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionresshape050_round1_1/nores_vocoder_audio_export.json reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_se8_fusionresshape050_round1_1/nores_vocoder_audio_export.json`
- Output:
  - `reports/runtime/stage5_vuv_noise_hidden_residual_structure_probe_streaming_student_energypeak_fusionresshape050_round1_1/stage5_vuv_noise_hidden_residual_structure_probe.json`
  - `reports/runtime/stage5_vuv_noise_hidden_residual_structure_probe_streaming_student_energypeak_fusionresshape050_round1_1/stage5_vuv_noise_hidden_residual_structure_probe.md`

## Variants
- `baseline`
- `target_unvoiced_residual_gain300`
  - positive control
- `noise_hidden_rms_soft_residual_gain500`
  - best earlier deployable scaling comparator
- `residual_branch_fused_from_noise_hidden`
  - recompute residual adapter features with `noise_hidden` in the fused slot
- `residual_branch_branchmean_from_noise_hidden`
  - recompute residual adapter features with `noise_hidden` in the branch-mean slot
- `residual_branch_noise_hidden_vs_periodic`
  - recompute residual adapter features as explicit `noise_hidden` versus `periodic_hidden`
- `residual_branch_noise_hidden_only`
  - collapse both residual adapter feature slots to `noise_hidden`

## Aggregate Findings
- Aggregate diagnosis:
  - `primary_diagnosis = explicit_noise_hidden_to_residual_feature_reroute_has_partial_leverage_but_needs_new_projection`
- Baseline aggregate waveform-frames `vuv` high-band gap:
  - `-0.003187`
- Best structural reroute:
  - `residual_branch_noise_hidden_only = -0.002912`
- Structural gain vs baseline:
  - `+0.000275`
- Best earlier deployable scaling comparator:
  - `noise_hidden_rms_soft_residual_gain500 = 0.003365`
- Oracle target-side positive control:
  - `target_unvoiced_residual_gain300 = 0.003254`
- Best-structure gap to scaling comparator:
  - `0.006277`
- Best-structure gap to oracle:
  - `0.006166`

## Reading
- This result is materially different from `527`.
- `527` only showed:
  - the right carrier already exists upstream in `noise_hidden`
- `528` now shows:
  - the current residual adapter weights are not enough to expose that carrier through simple feature-slot substitutions
- The practical evidence is consistent across all tested reroutes:
  - every structural variant stays negative at waveform-frames `vuv` gap
  - every structural variant remains `review_required 5/5`
  - the best structural variant is only a tiny improvement over baseline
- Therefore the main blocker is no longer:
  - where to source the unvoiced carrier
- The main blocker is now:
  - how to project or inject that carrier into the residual path in a way the current checkpoint can actually use

## Decision
- Keep `noise_hidden` as the main next-step carrier for this line.
- Retire the idea that the current residual-shape adapter can likely be rescued by simple feature rerouting alone.
- Do not go back to:
  - gate-head tuning
  - generic base-logit gain shaping
  - or more variants that only reshuffle the same residual adapter input tuple

## Recommended Next Action
- Open a real structural Stage5 probe that adds an explicit new `noise_hidden -> residual` projection or injection path on `waveform_decoder_base_logits -> waveform_frames`.
- Keep the current checkpoint frozen for the first bounded probe if possible, so the next result continues to localize consumer-side capacity instead of mixing in new training effects.
