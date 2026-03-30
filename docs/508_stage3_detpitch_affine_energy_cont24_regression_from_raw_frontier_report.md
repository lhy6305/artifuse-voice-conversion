# Stage3 deterministic affine-calibrated energy cont24 regression from raw frontier report

## Summary
- After `cont20` opened the deterministic line to:
  - `energy_ready_count = 2/3`
  - `all_core_controls_ready_count = 2/3`
  - raw energy-best `0.120149` at `cont20.step3`
- the next continuation was started from the raw deterministic `ENERGY` frontier:
  - `reports/training/ss_detpitch_energycalib_cont20/checkpoints/ss_detpitch_energycalib_cont20.step3.pt`
- This continuation did not improve the route.
- Instead, `cont24` regressed the packet result back to:
  - `energy_ready_count = 1/3`
  - `all_core_controls_ready_count = 1/3`
  - `auto_reject_count = 2`

## Commands
- Training:
  - `reports/training/ss_detpitch_energycalib_cont24`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_energycalib_cont24/streaming_student_packet_checkpoint_selection.json`

## cont24 packet result

| step | auto reject | all-core ready | energy ready | avg energy calibrated mae |
| --- | ---: | ---: | ---: | ---: |
| 1 | 2 | 1 | 1 | 0.165920 |
| 2 | 2 | 1 | 1 | 0.174924 |
| 3 | 2 | 1 | 1 | 0.177803 |
| 4 | 2 | 1 | 1 | 0.172231 |

- Packet selector top-1:
  - `cont24.step1`
- Raw energy-best inside `cont24`:
  - also `cont24.step1`
- This means the best state in `cont24` is already worse than the best states in `cont20`.

## Record-level regression
- `target::chapter3_3_firefly_162`
  - stays energy-ready
  - `cont24.step1`: `energy_stage5_norm_calibrated_reference_mae = 0.116197`
- `target::chapter3_3_firefly_138`
  - loses energy readiness again
  - `cont20.step3`: `0.107154`
  - `cont24.step1`: `0.154917`
  - this crosses back above the packet gate threshold `0.15`
- `target::chapter3_4_firefly_106`
  - remains blocked and also worsens
  - `cont20.step3`: `0.165880`
  - `cont24.step1`: `0.226645`
  - `APER` also stays far above threshold at `0.401766`

## Interpretation
- `cont20.step3` remains the strongest raw deterministic `ENERGY` frontier observed so far.
- But `cont24` shows that it is not a safe "keep training from here by inertia" anchor.
- The continuation regressed on both:
  - the still-open second record `target::chapter3_3_firefly_138`
  - the remaining hard blocker `target::chapter3_4_firefly_106`
- So the current deterministic line should now keep two distinct conclusions:
  - best packet-facing checkpoint: `cont20.step2`
  - best raw energy frontier: `cont20.step3`
- But it should not keep the old rule:
  - "continue from raw energy-best checkpoint until the route opens"

## Main conclusion
- `cont20` is still the active frontier.
- `cont24` is a regression block, not a new best block.
- The correct next move is now narrower:
  - do not keep blindly continuing from the raw energy-best checkpoint
  - keep `cont20.step2` as the packet-facing checkpoint
  - keep `cont20.step3` only as the raw deterministic `ENERGY` frontier reference
  - if continuation work resumes, either:
    - restart from the more stable packet-facing checkpoint
    - or add a stricter intra-block early-stop and blocker-localized rule

## Decision
- Freeze the current best deterministic family summary at `cont20`, not `cont24`.
- Treat `cont24` as evidence that the affine-calibrated line is no longer monotonic once pushed past the current frontier.
- Do not promote `cont24` into the active mainline checkpoint set.

## Next actions
1. Keep `ss_detpitch_energycalib_cont20.step2` as the current packet-facing checkpoint.
2. Keep `ss_detpitch_energycalib_cont20.step3` as the current raw deterministic `ENERGY` frontier.
3. Do not launch `cont28` by inertia from `cont20.step3`.
4. If further deterministic continuation is attempted, change the continuation rule first instead of repeating the same raw-frontier init pattern.
