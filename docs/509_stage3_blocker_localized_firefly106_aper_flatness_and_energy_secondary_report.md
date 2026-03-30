# Stage3 blocker-localized firefly106 APER flatness and energy secondary report

## Summary
- A blocker-localized diagnosis was run for the remaining sample3 blocker:
  - `target::chapter3_4_firefly_106`
- Compared checkpoints:
  - `cont20.step2`
  - `cont20.step3`
  - `cont24.step1`
- Main conclusion:
  - the dominant remaining blocker is not `ENERGY` alone
  - the deeper blocker is `APER`
  - `APER` is effectively flat and weakly anti-correlated with the reference on this record
  - affine calibration does not rescue it
- `ENERGY` is still important, but it is now the secondary blocker:
  - it is reasonably correlated
  - calibration helps substantially
  - `cont20.step3` already pushed it near the gate threshold
  - the later `cont24` regression is mainly a stability problem, not evidence that `ENERGY` is the only unsolved field

## Inputs
- Packet records:
  - `reports/runtime/ss_pktsel_detpitch_energycalib_cont20/pkt_exp/s0002_ss_detpitch_energycalib_cont20/records/target__chapter3_4_firefly_106.pt`
  - `reports/runtime/ss_pktsel_detpitch_energycalib_cont20/pkt_exp/s0003_ss_detpitch_energycalib_cont20/records/target__chapter3_4_firefly_106.pt`
  - `reports/runtime/ss_pktsel_detpitch_energycalib_cont24/pkt_exp/s0001_ss_detpitch_energycalib_cont24/records/target__chapter3_4_firefly_106.pt`
- Relevant gate thresholds:
  - `MAX_APER_REFERENCE_MAE = 0.3`
  - `MAX_ENERGY_STAGE5_NORM_REFERENCE_MAE = 0.15`

## APER diagnosis
- On `firefly_106`, all three checkpoints show the same qualitative APER pattern:
  - raw `aper_prob` mean stays around `0.482`
  - raw `aper_prob` std stays around only `0.0125`
  - reference `aper` std is much larger
  - raw correlation is slightly negative at about `-0.093`
- After affine calibration:
  - calibrated `APER` std rises to about `0.04`
  - but calibrated MAE remains stuck near `0.402`
  - this is still far above the packet gate threshold `0.3`

| checkpoint | aper raw mae | aper calibrated mae | aper raw std | aper raw corr |
| --- | ---: | ---: | ---: | ---: |
| cont20.step2 | 0.400660 | 0.401717 | 0.012529 | -0.094033 |
| cont20.step3 | 0.400666 | 0.401752 | 0.012522 | -0.093274 |
| cont24.step1 | 0.400677 | 0.401766 | 0.012515 | -0.092922 |

- This is strong evidence that the remaining APER failure on this record is structural under the current scaffold:
  - the predictor is nearly flat
  - calibration can flip and stretch it
  - but calibration cannot create the missing framewise structure

## ENERGY diagnosis
- On the same record, `ENERGY` behaves differently:
  - raw correlation is clearly positive
  - calibration cuts MAE substantially
  - the best checkpoint is `cont20.step3`
- This means the current energy line is not random on the blocker record.
- It is already learning useful framewise structure, but not stably enough to stay under the final threshold.

| checkpoint | energy raw mae | energy calibrated mae | energy raw std | energy raw corr |
| --- | ---: | ---: | ---: | ---: |
| cont20.step2 | 0.362959 | 0.198391 | 0.063471 | 0.824083 |
| cont20.step3 | 0.328854 | 0.165880 | 0.096728 | 0.871793 |
| cont24.step1 | 0.372472 | 0.226645 | 0.059007 | 0.776370 |

- The key reading is:
  - `ENERGY` at `cont20.step3` is still above threshold `0.15`
  - but only by about `0.015880`
  - this is a much smaller gap than the APER gap

## Blocker hierarchy
- Current blocker order on `firefly_106` is:
  1. `APER` structural flatness
  2. `ENERGY` stability and threshold crossing
- This matters because the old continuation logic implicitly treated the line as if:
  - "keep pushing `ENERGY` and the route will open"
- The blocker-localized evidence says that is incomplete:
  - even if `ENERGY` crosses threshold, `APER` would still remain far from ready on this record

## Why cont24 regressed
- `cont24` did not reveal a new failure mode.
- It mainly confirmed that the line is unstable if continued blindly from the raw energy frontier:
  - `ENERGY` correlation dropped from `0.871793` to `0.776370`
  - `ENERGY` calibrated MAE worsened from `0.165880` to `0.226645`
  - `APER` remained unchanged in its flatness pattern
- So `cont24` regression is best read as:
  - energy-side instability on top of
  - an already-unsolved APER structural blocker

## Main conclusion
- The remaining sample3 blocker should no longer be summarized as "just keep pushing ENERGY."
- The correct localized reading is:
  - `APER` is the primary unsolved control on `target::chapter3_4_firefly_106`
  - `ENERGY` is the secondary unsolved control and was already near-threshold at `cont20.step3`
- Therefore the next deterministic continuation should not be framed as a generic energy-only continuation.
- If this line continues, the next valid action should prefer one of:
  - a continuation rule that protects the stronger `ENERGY` state without blind drift
  - or a blocker-oriented probe that explicitly targets `APER` rather than assuming `ENERGY` is the only remaining lever

## Decision
- Keep `cont20.step2` as the packet-facing checkpoint.
- Keep `cont20.step3` as the raw deterministic `ENERGY` frontier reference.
- Reframe the remaining blocker as:
  - primary: `APER` on `target::chapter3_4_firefly_106`
  - secondary: `ENERGY` stability on the same record

## Next actions
1. Do not open `cont28` by inertia from `cont20.step3`.
2. If continuation work resumes, test a more conservative anchor such as `cont20.step2`.
3. Treat any further deterministic probe as blocker-oriented and include explicit `APER` reading for `target::chapter3_4_firefly_106`.
