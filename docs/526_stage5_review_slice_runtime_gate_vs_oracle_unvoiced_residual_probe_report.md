# 526 Stage5 Review-Slice Runtime Gate Vs Oracle Unvoiced Residual Probe Report

## Summary
- This round converted the earlier positive-control result into a stricter deployability check:
  - `analyze-stage5-nores-vuv-runtime-residual-probe`
- The question was no longer:
  - can an oracle target-side unvoiced mask rescue the localized sink
- The question was:
  - can the current runtime-side gate signals already do the same job without target-side help

## Probe Run
- Review bundle:
  - `reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json`
- Audio export manifests:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionresshape050_round1_1/nores_vocoder_audio_export.json`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_se8_fusionresshape050_round1_1/nores_vocoder_audio_export.json`
- Output:
  - `reports/runtime/stage5_vuv_runtime_residual_probe_streaming_student_energypeak_fusionresshape050_round1_1/stage5_vuv_runtime_residual_probe.json`
  - `reports/runtime/stage5_vuv_runtime_residual_probe_streaming_student_energypeak_fusionresshape050_round1_1/stage5_vuv_runtime_residual_probe.md`

## Variants
- `baseline`
- `target_unvoiced_residual_gain300`
  - positive control
- `noise_gate_soft_residual_gain300`
- `noise_gate_soft_residual_gain500`
- `noise_minus_periodic_soft_residual_gain500`
- `noise_dominance_hard_residual_gain300`

## Findings
- Aggregate diagnosis:
  - `primary_diagnosis = current_runtime_gates_not_enough_for_unvoiced_residual_control`
- Baseline aggregate waveform-frames `vuv` high-band gap:
  - `-0.003187`
- Oracle target-side positive control:
  - `0.003254`
- Best runtime variant is still only:
  - `baseline`
- Runtime gap to oracle:
  - `0.006441`
- All runtime-only gate variants stay non-positive at waveform-frames level:
  - `noise_gate_soft_residual_gain300 = -0.003678`
  - `noise_gate_soft_residual_gain500 = -0.004254`
  - `noise_minus_periodic_soft_residual_gain500 = -0.003187`
  - `noise_dominance_hard_residual_gain300 = -0.003187`

## Reading
- The current gate family is not merely weak.
- On this review slice it is structurally the wrong control source for unvoiced residual rescue.
- The key practical clue is even stronger at record level:
  - `noise_dominance_fraction = 0.0` on all `5/5` reviewed records
  - `noise_minus_periodic_mean` is negative on all `5/5`
- So a gate-derived unvoiced residual rule has nothing useful to latch onto in the active basin.

## Decision
- Stop treating `noise_gate` or `noise > periodic` heuristics as the next likely rescue path on this line.
- Keep the oracle target-side unvoiced residual result only as a positive-control localization aid.
- The next valid structural question must move upstream of the gate heads.
