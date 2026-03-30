# Stage3 RMVPE voicing-threshold and VUV-postprocess calibration report

## Summary
- Extended the Stage3 provider audit CLI to support:
  - RMVPE voicing-threshold sweeps
  - simple current-contract VUV postprocess presets
- Ran a calibration sweep on `8` validation records with:
  - thresholds: `0.01, 0.02, 0.03, 0.05, 0.08`
  - presets: `raw, fill1, fill2, min2_fill1, min2_fill2`
- Main conclusion:
  - no swept variant clears provider-only readiness-like screening
  - threshold changes only shift a mild tradeoff
  - simple VUV postprocessing is effectively a no-op on this slice

## Implementation
- The Stage3 provider-only audit CLI now accepts:
  - `--rmvpe-voicing-thresholds`
  - `--rmvpe-vuv-postprocess-presets`
- The audit now emits:
  - `rmvpe_current_contract_variant_summaries`
  - `rmvpe_current_contract_best_variant`

## Sweep result
- Best swept variant by the current ranking rule:
  - `thr0.010_raw`
- Best-variant aggregate:
  - `ready_like_count = 0/8`
  - `avg_voiced_log2_mae = 1.547794`
  - `avg_voiced_corr = -0.422858`
  - `avg_vuv_f1 = 0.844576`
  - `avg_joint_voiced_corr = 0.528394`
- Baseline current-contract aggregate at config threshold `0.03`:
  - `ready_like_count = 0/8`
  - `avg_voiced_log2_mae = 1.608832`
  - `avg_voiced_corr = -0.430655`
  - `avg_vuv_f1 = 0.852326`
  - `avg_joint_voiced_corr = 0.547401`

## Threshold trend
- Lower threshold `0.01` slightly improves full reference-voiced F0 metrics:
  - better `avg_voiced_corr`
  - better `avg_voiced_log2_mae`
- Higher thresholds do not rescue readiness:
  - by `0.08`, `avg_voiced_corr` worsens to about `-0.480083`
  - `avg_voiced_log2_mae` worsens to about `1.773927`
- Jointly voiced F0 quality stays broadly acceptable across thresholds:
  - `avg_joint_voiced_corr` remains about `0.53` to `0.58`
  - this reinforces the earlier conclusion that the main issue is voiced-support mismatch, not raw F0 failure on jointly voiced frames

## VUV postprocess result
- The tested presets produced almost identical aggregates:
  - `raw`
  - `fill1`
  - `fill2`
  - `min2_fill1`
  - `min2_fill2`
- On this audit slice, those simple gap-fill and short-run rules do not materially change:
  - `avg_voiced_corr`
  - `avg_voiced_log2_mae`
  - `avg_vuv_f1`
  - `avg_joint_voiced_corr`
- Therefore the current mismatch is not fixed by lightweight binary-mask cleanup after thresholded RMVPE decoding.

## Interpretation
- RMVPE provider-side threshold tuning alone is not enough.
- Simple binary VUV cleanup is also not enough.
- The current RMVPE route still does not produce a usable Stage3 current-contract provider.
- If RMVPE remains worth pursuing, the next valid probe is no longer threshold or gap-fill micro-tuning.
- The next meaningful escalation would need richer provider information than the current thresholded `f0_hz > 0` binary contract, for example:
  - confidence-aware voicing
  - salience-aware masking
  - a different provider-side contract altogether

## Decision
- Do not open a new Stage3 packet-smoke cycle for the current thresholded RMVPE route.
- Do not spend more time on the present family of threshold and simple binary VUV postprocess tweaks.
- Keep `deterministic_extractor_v1` as the only validated structural reference provider.

## Next actions
1. If RMVPE work continues, move to a confidence-aware provider design instead of more threshold sweeps.
2. Otherwise stop RMVPE tuning on the current contract and keep it below the deterministic reference route.

## Artifact reference
- Calibration audit summary:
  - `reports/runtime/streaming_student_pitch_provider_audit_rmvpe_validation8_vuvcalib/streaming_student_pitch_provider_audit.json`
