# Stage3 deterministic ENERGY micro1 regression and same-family stop report

## Summary
- A one-step blocker-facing deterministic `ENERGY` continuation was run from the current micro-frontier anchor:
  - `ss_detpitch_aperbranch_energyonly_s2_warm4.step1`
- Goal:
  - test whether a single additional micro-step could push the blocker record under the final `0.15` gate
- Result:
  - it failed clearly
  - it regressed from `ENERGY = 2/3` back to `ENERGY = 1/3`
  - blocker-record `ENERGY` worsened sharply from `0.150089` to `0.247955`
- Main conclusion:
  - the current same-family deterministic continuation line should stop here
  - a second micro-step is not justified
  - the next valid move is no longer same-family continuation
  - the next valid move is `ENERGY`-specific blocker-localized objective redesign

## Inputs
- Anchor checkpoint:
  - `reports/training/ss_detpitch_aperbranch_energyonly_s2_warm4/checkpoints/ss_detpitch_aperbranch_energyonly_s2_warm4.step1.pt`
- Continuation run:
  - training: `reports/training/ss_detpitch_aperenergy_micro1`
  - packet selector: `reports/runtime/ss_pktsel_detpitch_aperenergy_micro1/streaming_student_packet_checkpoint_selection.json`

## Comparison against the anchor

| checkpoint | auto reject | all-core ready | energy ready | avg energy calibrated mae | blocker energy calibrated mae |
| --- | ---: | ---: | ---: | ---: | ---: |
| micro-anchor `s2_warm4.step1` | 1 | 2 | 2 | 0.114544 | 0.150089 |
| micro1 step1 | 2 | 1 | 1 | 0.185413 | 0.247955 |

- Regression deltas:
  - `avg_energy_stage5_norm_calibrated_reference_mae`: `+0.070869`
  - blocker-record `ENERGY`: `+0.097866`
  - `energy_ready_count`: `2 -> 1`
  - `all_core_controls_ready_count`: `2 -> 1`

## Record-level reading
- `target::chapter3_4_firefly_106`
  - anchor: `0.150089`
  - micro1: `0.247955`
- `target::chapter3_3_firefly_138`
  - anchor family was already open at `ENERGY = ready`
  - micro1 pushes it back to `0.178393`, so it becomes non-ready too
- `target::chapter3_3_firefly_162`
  - stays energy-ready at `0.129892`

## Why this matters
- The previous report already showed:
  - same-family warm4 continuation is unstable
  - the best deterministic behavior near threshold is a single blocker-aware micro-step from the `step2` anchor
- This new micro1 run answers the next question directly:
  - even one more same-family step from that micro-anchor is not reliable
- Therefore:
  - the current family has reached its useful continuation limit
  - continuing to sample more same-family steps is no longer a disciplined search strategy

## Stop decision
- Stop the current same-family deterministic continuation line:
  - no second micro-step
  - no renewed warm4 from the same anchor family
  - no more raw-frontier or micro-frontier continuation by inertia

## Main conclusion
- The strongest current deterministic checkpoints remain:
  - packet-facing anchor: `ss_detpitch_aperbranch_energy_warm4.step2`
  - raw deterministic `ENERGY` frontier: `ss_detpitch_aperbranch_energy_warm4.step3`
  - blocker-facing micro-frontier: `ss_detpitch_aperbranch_energyonly_s2_warm4.step1`
- None of these open the final route.
- The residual gap is now small enough that repeated same-family continuation is no longer the right next action.
- The next deterministic step must be a more explicit blocker-localized `ENERGY` objective redesign.

## Next actions
1. Stop same-family deterministic continuation at the current micro-frontier.
2. Keep `ss_detpitch_aperbranch_energyonly_s2_warm4.step1` only as the last blocker-facing reference, not as a live continuation anchor.
3. Switch the next experiment family to blocker-localized `ENERGY` objective redesign.
