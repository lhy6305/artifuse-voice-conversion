# Stage3 deterministic dedicated APER branch route opening report

## Summary
- A dedicated APER-branch structural probe was run from the stable packet-facing anchor:
  - `cont20.step2`
- New scaffold change:
  - `aper_control_branch_mode = dedicated_aper_branch_v1`
- New config:
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_nof0corr_aperbranchfreeze_v1.json`
- New loss weights:
  - `configs/streaming_student_loss_weights_detpitch_aperbranch_v1.json`
- Main result:
  - this is the first deterministic probe that opens `APER` to `3/3` on the active sample3 packet screen
  - the global state becomes `F0 / VUV / APER / ENERGY = 3/3, 3/3, 3/3, 2/3`
  - the remaining blocker is no longer `APER`
  - the remaining blocker is now `ENERGY` on `target::chapter3_4_firefly_106`

## Structural change
- The old blocker-oriented APER probe only unfroze:
  - `frontend.aper_head`
  - `student.aper_branch_delta_head`
- That route preserved the existing partial opening but left blocker-record APER near `0.403`.
- This new probe instead gives APER its own isolated capacity:
  - `student.aper_branch_input_proj`
  - `student.aper_branch_norm`
  - `student.aper_branch_encoder`
  - `student.aper_branch_delta_head`
- This is the first explicit evidence that APER needed a structural branch upgrade, not just unfreezing.

## Training and packet outputs
- Training output:
  - `reports/training/ss_detpitch_aperbranch_cont20s2_warm4`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_aperbranch_cont20s2_warm4/streaming_student_packet_checkpoint_selection.json`

| step | auto reject | all-core ready | aper ready | energy ready | avg aper calibrated mae | avg energy calibrated mae |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 1 | 2 | 2 | 2 | 0.207019 | 0.143974 |
| 2 | 1 | 2 | 3 | 2 | 0.169555 | 0.143991 |
| 3 | 1 | 2 | 3 | 2 | 0.144945 | 0.144009 |
| 4 | 1 | 2 | 3 | 2 | 0.124169 | 0.144026 |

- Packet-facing selector top-1:
  - step `4`
- New reading:
  - `APER` is now stably open from step `2` onward
  - `ENERGY` stays at `2/3`
  - the route does not become fully open yet, but the blocker hierarchy changes completely

## Comparison against the previous APER scaffold
- Previous APER-oriented freeze probe:
  - `docs/510_stage3_detpitch_aperenergy_blocker_probe_report.md`
- Under the old APER scaffold, blocker-record APER stayed near:
  - `0.403249`
- Under the dedicated APER branch, blocker-record APER at step `4` becomes:
  - `aper_calibrated_reference_mae = 0.232967`
- This is below the packet gate:
  - `MAX_APER_REFERENCE_MAE = 0.3`

## Blocker record: `target::chapter3_4_firefly_106`
- The blocker record is no longer blocked by APER under this scaffold.
- Step `4` packet reading:
  - `aper_reference_mae = 0.367744`
  - `aper_calibrated_reference_mae = 0.232967`
  - `energy_stage5_norm_reference_mae = 0.362878`
  - `energy_stage5_norm_calibrated_reference_mae = 0.198465`
- This shows a new blocker order:
  - `APER` is now packet-open on the blocker record
  - `ENERGY` is the only remaining non-ready control on that record

## Main conclusion
- The dedicated APER branch is a real positive structural fix.
- It changes the deterministic line from:
  - `F0 / VUV / APER / ENERGY = 3/3, 3/3, 2/3, 2/3`
- To:
  - `F0 / VUV / APER / ENERGY = 3/3, 3/3, 3/3, 2/3`
- Therefore:
  - the old statement "the remaining blocker is APER plus ENERGY" is no longer correct on the active deterministic line
  - the remaining blocker is now localized to `ENERGY` on `target::chapter3_4_firefly_106`

## Decision
- Keep the dedicated APER branch as a validated structural direction.
- Keep step `4` as the packet-facing best checkpoint for the APER-only branch.
- Do not go back to APER-flatness language in active docs.

## Next actions
1. Keep the dedicated APER branch active in the deterministic line.
2. Use this APER-open checkpoint as the base for the next combined APER plus ENERGY probe.
3. Treat the remaining blocker as energy-localized, not APER-localized.
