# Stage3 deterministic dedicated APER plus ENERGY warm4 and cont8 report

## Summary
- A combined dedicated APER plus dedicated ENERGY deterministic probe was run after the APER-only structural breakthrough.
- Base checkpoint:
  - `ss_detpitch_aperbranch_cont20s2_warm4.step4`
- Combined config:
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_nof0corr_aperbranch_energyfreeze_v1.json`
- Loss weights:
  - `configs/streaming_student_loss_weights_detpitch_aperenergy_stage5calib_v1.json`
- Main result:
  - the combined branch preserves `APER = 3/3`
  - the global state becomes `F0 / VUV / APER / ENERGY = 3/3, 3/3, 3/3, 2/3`
  - the only remaining blocker is `ENERGY` on `target::chapter3_4_firefly_106`
  - a blind continuation from the near-threshold combined state is unstable and should not become the default continuation rule

## Warm4 packet results
- Training output:
  - `reports/training/ss_detpitch_aperbranch_energy_warm4`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_aperbranch_energy_warm4/streaming_student_packet_checkpoint_selection.json`

| step | auto reject | all-core ready | aper ready | energy ready | avg aper calibrated mae | avg energy calibrated mae |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2 | 1 | 3 | 1 | 0.108959 | 0.165025 |
| 2 | 1 | 2 | 3 | 2 | 0.114280 | 0.150755 |
| 3 | 1 | 2 | 3 | 2 | 0.109420 | 0.114200 |
| 4 | 1 | 2 | 3 | 2 | 0.107767 | 0.134373 |

- Packet-facing selector top-1:
  - step `2`
- Raw deterministic `ENERGY` best:
  - step `3`

## Blocker record under the combined warm4 line
- The blocker record remains:
  - `target::chapter3_4_firefly_106`
- But its blocker structure is now simpler than before:
  - `APER` is already open
  - only `ENERGY` remains above threshold

| checkpoint | aper calibrated mae | energy calibrated mae |
| --- | ---: | ---: |
| combined step2 | 0.162251 | 0.201414 |
| combined step3 | 0.166986 | 0.150639 |

- Step `3` is especially important:
  - blocker-record `ENERGY` reaches `0.150639`
  - this is only `0.000639` above the packet gate `0.15`
- So the combined branch reaches a near-open state without giving back `APER`.

## Continuation cont8
- Training output:
  - `reports/training/ss_detpitch_aperbranch_energy_cont8`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_aperbranch_energy_cont8/streaming_student_packet_checkpoint_selection.json`

| step | auto reject | all-core ready | aper ready | energy ready | avg aper calibrated mae | avg energy calibrated mae |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2 | 1 | 3 | 1 | 0.118335 | 0.182411 |
| 2 | 2 | 1 | 3 | 1 | 0.110955 | 0.188670 |
| 3 | 2 | 1 | 3 | 1 | 0.105085 | 0.176403 |
| 4 | 1 | 2 | 3 | 2 | 0.113703 | 0.140830 |

- Packet-facing selector top-1:
  - step `4`
- Reading:
  - `APER` stays open at `3/3`
  - but the line mostly regresses on `ENERGY`
  - the near-threshold `warm4.step3` state is not stably improved by blind continuation

## Main conclusion
- The combined dedicated APER plus dedicated ENERGY line is now the strongest deterministic route so far.
- Its best state is:
  - packet-facing checkpoint: `ss_detpitch_aperbranch_energy_warm4.step2`
  - raw deterministic `ENERGY` frontier: `ss_detpitch_aperbranch_energy_warm4.step3`
- The active global state on that line is:
  - `F0 / VUV / APER / ENERGY = 3/3, 3/3, 3/3, 2/3`
- The only remaining blocker is:
  - `ENERGY` on `target::chapter3_4_firefly_106`
- The continuation lesson is also clear:
  - do not continue blindly from the raw energy-best checkpoint by inertia
  - use blocker-aware or threshold-aware continuation logic instead

## Decision
- Keep `ss_detpitch_aperbranch_energy_warm4.step2` as the current packet-facing checkpoint on the strongest deterministic line.
- Keep `ss_detpitch_aperbranch_energy_warm4.step3` as the current raw deterministic `ENERGY` frontier reference on that line.
- Treat `cont8` as regression evidence, not as the new main frontier.

## Next actions
1. Keep the dedicated APER branch in the active deterministic scaffold.
2. Treat the remaining blocker as a single-record energy-threshold problem.
3. If continuation resumes, use blocker-aware early-stop or threshold-aware anchoring instead of blind same-family continuation.
