# Stage3 packet calibration bias-recompute bugfix and deterministic energy family reevaluation report

## Summary
- This report remains useful for the clipped-scale stale-bias bugfix, but its later continuation tradeoff interpretation is numerically superseded by `docs/506_stage3_f0_zero_mae_gate_bugfix_and_affine_energy_cont8_followup_report.md`.
- Found a real bug in the downstream packet affine calibration path that invalidated the absolute `ENERGY` MAE story in reports `499` to `504`.
- Root cause:
  - affine `scale` was clipped to `[-8, 8]`
  - but `bias` was not recomputed after the clip
- The bug especially distorted `ENERGY` packet audit values because several probes learned high raw slopes.
- After fixing the bug and re-running the packet selectors, the deterministic isolated-energy line is much better than previously believed:
  - the active family is no longer around `0.55`
  - the true current family frontier is around `0.243` to `0.247`
- The best current deterministic family is still the affine-calibrated objective family.
- A short continuation from the previous family-best checkpoint improves the true energy-best value further to `0.232511`, but starts giving back `F0` after step `1`.

## Root cause
- File:
  - `src/v5vc/streaming_student/downstream_control_packet.py`
- Affected functions:
  - `calibrate_f0_log_proxy_to_reference`
  - `calibrate_scalar_proxy_to_reference`
- Old behavior:
  - fit affine `y ~= x * scale + bias`
  - clamp `scale` to `[-8, 8]`
  - keep the old `bias`
- This is mathematically inconsistent whenever raw fitted `scale` exceeds the clamp range.
- Once `scale` changes, `bias` must be recomputed from the same centered fit relation:
  - `bias = mean(y) - mean(x) * scale`

## Fix
- Applied the same low-risk fix in both calibration helpers:
  - clamp `scale`
  - immediately recompute `bias`
- New behavior now matches the intended clipped affine fit instead of a mixed unclipped-bias artifact.

## Concrete proof case
- Reproduced on:
  - `reports/runtime/ss_pktsel_detpitch_energycalib_warm4/pkt_exp/s0002_ss_detpitch_energycalib_warm4/records/target__chapter3_3_firefly_162.pt`
- Observed values:
  - `scale_raw = 15.729062`
  - `scale_clamped = 8.0`
  - `bias_raw = -11.764772`
  - `bias_recomputed = -5.581621`
- Impact on calibrated packet `ENERGY` MAE:
  - old implementation path: `0.818279`
  - corrected bias-recomputed path: `0.182918`
- This confirms the issue was not cosmetic rounding noise. It materially changed packet-facing `ENERGY` conclusions.

## Post-fix family reevaluation
- Re-ran packet-aware selectors for the active deterministic isolated-energy families:
  - `adapter`
  - `dynrange`
  - `calib`
  - `calib_lrhalf`
- Corrected family comparison:

| family | selector step | selector energy mae | energy-best step | energy-best mae | energy ready |
| --- | --- | ---: | --- | ---: | ---: |
| adapter | 2 | 0.274015 | 4 | 0.246715 | 0 |
| dynrange | 2 | 0.273451 | 4 | 0.246440 | 0 |
| calib | 3 | 0.250076 | 4 | 0.243179 | 0 |
| calib_lrhalf | 4 | 0.263163 | 1 | 0.258234 | 0 |

## Reinterpreted conclusions
- The old `0.550` to `0.707` narrative is no longer valid for the active deterministic isolated-energy families.
- The corrected deterministic isolated-energy frontier is already in the `0.24x` range.
- The affine-calibrated family remains the strongest family:
  - best selector-facing checkpoint: step `3`, `0.250076`
  - best raw energy checkpoint: step `4`, `0.243179`
- The low-learning-rate follow-up is still a no-go relative to the normal affine-calibrated family:
  - best raw energy only `0.258234`

## Important selector pitfall
- Packet-selector top-1 is still not the same thing as the family `ENERGY` best checkpoint.
- This is expected under the current lexicographic selector because it prioritizes:
  - readiness counts
  - `VUV`
  - `F0`
  - `APER`
  - only then `ENERGY`
- In the corrected affine-calibrated family:
  - selector top-1 is step `3`
  - raw energy-best is step `4`
- So family review must always cite both:
  - selector top-1
  - raw energy-best checkpoint

## Affine-calibrated continuation
- Started from:
  - `reports/training/ss_detpitch_energycalib_warm4/checkpoints/ss_detpitch_energycalib_warm4.step4.pt`
- Ran:
  - `reports/training/ss_detpitch_energycalib_cont4`
  - `reports/runtime/ss_pktsel_detpitch_energycalib_cont4/streaming_student_packet_checkpoint_selection.json`
- Corrected continuation outcome:

| step | f0 ready | vuv ready | aper ready | energy ready | avg energy calibrated mae |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1 | 3 | 3 | 2 | 0 | 0.239505 |
| 2 | 2 | 3 | 2 | 0 | 0.236783 |
| 3 | 2 | 3 | 2 | 0 | 0.234545 |
| 4 | 2 | 3 | 2 | 0 | 0.232511 |

- This is the best deterministic isolated-energy result so far:
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.232511`
- But it is not a route-opening win because:
  - `energy_ready_count` still stays `0/3`
  - `F0` drops from `3/3` at step `1` to `2/3` at steps `2` to `4`

## Main conclusion
- The packet calibration bug fix materially changes the deterministic `ENERGY` story.
- The active deterministic isolated-energy line is no longer a weak `0.55` family; it is a substantially stronger `0.24x` family.
- The current best family is still the affine-calibrated objective family.
- Continuing that family can still improve `ENERGY`, but the next barrier is now a joint-control tradeoff:
  - more `ENERGY` gain starts to damage `F0`
- Therefore the next valid continuation is not more blind reweighting or lr-half retries.
- The next valid continuation must become joint-control-aware:
  - preserve the already-open deterministic `F0 / VUV / APER`
  - while improving `ENERGY` below the packet threshold

## Decision
- Keep the affine-calibrated deterministic energy family as the active isolated `ENERGY` line.
- Treat reports `499` to `504` as historically useful but numerically superseded by this bugfix reevaluation.
- Use this report as the current reference when discussing deterministic packet-facing `ENERGY`.

## Next actions
1. Keep the deterministic nof0corr scaffold as the active explicit-provider reference.
2. Keep the affine-calibrated family as the active deterministic isolated `ENERGY` family.
3. Do not interpret packet-selector top-1 as the energy-best checkpoint without checking the raw family metrics.
4. If this line continues, switch to joint-control-aware optimization instead of more blind scalar tuning or lr-half retries.
