# Stage3 deterministic affine-calibrated energy cont12 to cont20 partial route-opening report

## Summary
- The corrected deterministic affine-calibrated continuation line did not plateau at `cont8`.
- Continuing the same family through `cont12`, `cont16`, and `cont20` produced the first real partial named-control opening on the active sample3 packet slice.
- Current best states are now split by role:
  - packet-facing selector top-1: `ss_detpitch_energycalib_cont20.step2`
  - raw deterministic `ENERGY` frontier: `ss_detpitch_energycalib_cont20.step3`
- `cont20` is the first continuation block that reaches:
  - `energy_ready_count = 2/3`
  - `all_core_controls_ready_count = 2/3`
  - while preserving `F0 / VUV / APER = 3/3, 3/3, 2/3`
- The remaining blocker is now localized to one record:
  - `target::chapter3_4_firefly_106`

## Gate context
- Packet gate thresholds in `src/v5vc/streaming_student/downstream_control_packet.py` are:
  - `MAX_APER_REFERENCE_MAE = 0.3`
  - `MAX_ENERGY_STAGE5_NORM_REFERENCE_MAE = 0.15`
- On the current deterministic affine-calibrated line, the full route is now blocked by one record that still misses both thresholds.

## Continuation trajectory

| block | selector top-1 | raw energy-best | best auto reject | best all-core ready | best energy ready | raw energy-best mae |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| warm4 | step3 | step4 | 3 | 0 | 0 | 0.243179 |
| cont4 | step1 | step4 | 3 | 0 | 0 | 0.232511 |
| cont8 | step1 | step4 | 3 | 0 | 0 | 0.224320 |
| cont12 | step3 | step4 | 2 | 1 | 1 | 0.216033 |
| cont16 | step1 | step4 | 2 | 1 | 1 | 0.201423 |
| cont20 | step2 | step3 | 1 | 2 | 2 | 0.120149 |

- The key transition is:
  - `cont12`: first `1/3` opening
  - `cont16`: same opening count, but lower raw energy frontier
  - `cont20`: first `2/3` opening and first `all_core_controls_ready_count = 2/3`

## cont12
- Selector artifact:
  - `reports/runtime/ss_pktsel_detpitch_energycalib_cont12/streaming_student_packet_checkpoint_selection.json`
- Best packet-facing step:
  - step `3`
- Best raw energy step:
  - step `4`

| step | auto reject | all-core ready | energy ready | avg energy calibrated mae |
| --- | ---: | ---: | ---: | ---: |
| 1 | 3 | 0 | 0 | 0.222237 |
| 2 | 3 | 0 | 0 | 0.220165 |
| 3 | 2 | 1 | 1 | 0.218085 |
| 4 | 2 | 1 | 1 | 0.216033 |

## cont16
- Selector artifact:
  - `reports/runtime/ss_pktsel_detpitch_energycalib_cont16/streaming_student_packet_checkpoint_selection.json`
- Best packet-facing step:
  - step `1`
- Best raw energy step:
  - step `4`

| step | auto reject | all-core ready | energy ready | avg energy calibrated mae |
| --- | ---: | ---: | ---: | ---: |
| 1 | 2 | 1 | 1 | 0.213951 |
| 2 | 2 | 1 | 1 | 0.211601 |
| 3 | 2 | 1 | 1 | 0.208299 |
| 4 | 2 | 1 | 1 | 0.201423 |

## cont20
- Selector artifact:
  - `reports/runtime/ss_pktsel_detpitch_energycalib_cont20/streaming_student_packet_checkpoint_selection.json`
- Best packet-facing step:
  - step `2`
- Best raw energy step:
  - step `3`

| step | auto reject | all-core ready | energy ready | avg energy calibrated mae |
| --- | ---: | ---: | ---: | ---: |
| 1 | 2 | 1 | 1 | 0.175635 |
| 2 | 1 | 2 | 2 | 0.143957 |
| 3 | 1 | 2 | 2 | 0.120149 |
| 4 | 1 | 2 | 2 | 0.143918 |

## Record-level localization
- `target::chapter3_3_firefly_162`
  - becomes energy-ready by `cont12.step3`
  - at `cont20.step3`: `energy_stage5_norm_calibrated_reference_mae = 0.087414`
- `target::chapter3_3_firefly_138`
  - becomes energy-ready by `cont20.step2`
  - at `cont20.step3`: `energy_stage5_norm_calibrated_reference_mae = 0.107154`
- `target::chapter3_4_firefly_106`
  - remains the only blocking record
  - at `cont20.step3`:
    - `aper_calibrated_reference_mae = 0.401752`
    - `energy_stage5_norm_calibrated_reference_mae = 0.165880`
  - compared with gate thresholds:
    - `APER` misses `0.3` by a wide margin
    - `ENERGY` misses `0.15` by a smaller but still decisive margin

## Selector interpretation
- The selector and the raw energy frontier are now both useful, but they answer different questions.
- `cont20.step2` is the least-risk packet-facing checkpoint because:
  - it ties the best readiness counts
  - then wins on higher-priority secondary packet metrics such as `avg_vuv_reference_mae`
- `cont20.step3` is the raw deterministic `ENERGY` frontier because:
  - it has the lowest `avg_energy_stage5_norm_calibrated_reference_mae`
  - `0.120149` is materially better than `step2` at `0.143957`

## Main conclusion
- The active deterministic affine-calibrated line is no longer a fully closed route.
- It now has a real partial opening:
  - `F0 / VUV / APER / ENERGY = 3/3, 3/3, 2/3, 2/3`
  - `all_core_controls_ready_count = 2/3`
- The route is still not fully open, but the bottleneck is now localized and concrete:
  - a single long record still fails both `APER` and `ENERGY`
- This changes the next move:
  - continue the same affine-calibrated deterministic family
  - but frame the next continuation around the remaining blocker record instead of broad family-level uncertainty

## Decision
- Keep `ss_detpitch_energycalib_cont20.step2` as the current packet-facing checkpoint on this deterministic line.
- Keep `ss_detpitch_energycalib_cont20.step3` as the current raw deterministic `ENERGY` frontier.
- Treat `target::chapter3_4_firefly_106` as the concrete remaining blocker for full route opening on the active sample3 slice.

## Next actions
1. Continue the affine-calibrated deterministic family from `ss_detpitch_energycalib_cont20.step3`, not from a weaker earlier continuation.
2. Keep packet-aware screening on the same sample3 slice for continuity with `warm4`, `cont4`, `cont8`, `cont12`, `cont16`, and `cont20`.
3. Add blocker-localized reading for `target::chapter3_4_firefly_106` before opening any redesign branch, because the remaining gap is now record-specific rather than family-wide.
