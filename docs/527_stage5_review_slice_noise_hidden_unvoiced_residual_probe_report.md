# 527 Stage5 Review-Slice Noise-Hidden Unvoiced Residual Probe Report

## Summary
- After `526` showed that current runtime gate signals are unusable for unvoiced residual control, this round moved one stage upstream:
  - `analyze-stage5-nores-vuv-noise-hidden-residual-probe`
- The new question was:
  - does `noise_hidden` already carry a deployable unvoiced emphasis signal even though the gate heads do not

## Probe Run
- Review bundle:
  - `reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json`
- Audio export manifests:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_tv8_fusionresshape050_round1_1/nores_vocoder_audio_export.json`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_streaming_student_energypeak_se8_fusionresshape050_round1_1/nores_vocoder_audio_export.json`
- Output:
  - `reports/runtime/stage5_vuv_noise_hidden_residual_probe_streaming_student_energypeak_fusionresshape050_round1_1/stage5_vuv_noise_hidden_residual_probe.json`
  - `reports/runtime/stage5_vuv_noise_hidden_residual_probe_streaming_student_energypeak_fusionresshape050_round1_1/stage5_vuv_noise_hidden_residual_probe.md`

## Variants
- `baseline`
- `target_unvoiced_residual_gain300`
  - positive control
- `noise_hidden_rms_soft_residual_gain300`
- `noise_hidden_rms_soft_residual_gain500`
- `noise_hidden_delta_soft_residual_gain500`
- `noise_hidden_rmsdelta_soft_residual_gain500`

## Findings
- Aggregate diagnosis:
  - `primary_diagnosis = noise_hidden_is_close_to_oracle_for_unvoiced_residual_control`
- Baseline aggregate waveform-frames `vuv` high-band gap:
  - `-0.003187`
- Oracle target-side positive control:
  - `0.003254`
- Best deployable `noise_hidden` variant:
  - `noise_hidden_rms_soft_residual_gain500`
  - waveform-frames aggregate `vuv` high-band gap = `0.003365`
  - decoded aggregate `vuv` high-band gap = `0.013621`
- Gap to oracle:
  - `-0.000111`
  - effectively parity on this review slice
- The stronger result comes specifically from per-frame `noise_hidden` RMS, not delta:
  - `noise_hidden_rms_soft_residual_gain300 = -0.000315`
  - `noise_hidden_rms_soft_residual_gain500 = 0.003365`
  - `noise_hidden_delta_soft_residual_gain500 = -0.002705`
  - `noise_hidden_rmsdelta_soft_residual_gain500 = -0.000012`

## Reading
- This is the strongest current decomposition result on the active Stage5 sink.
- It says:
  - the current gate heads do not expose a usable unvoiced control
  - but the upstream `noise_hidden` state already does contain enough local signal to match or slightly exceed the oracle target-side positive control on the same review slice
- So the next structural move should not be:
  - more gate tweaking
  - or more generic base-logit shaping
- The next structural move should be:
  - an explicit `noise_hidden -> residual` unvoiced-focused path

## Decision
- Promote `noise_hidden` from a side observation to the main next-step carrier for this line.
- The next Stage5 structural probe should make the residual or noise-side contribution depend explicitly on `noise_hidden` rather than on the current gate heads.
