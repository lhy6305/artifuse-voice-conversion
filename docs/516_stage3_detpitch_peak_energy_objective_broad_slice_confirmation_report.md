# Stage3 deterministic peak-focused ENERGY objective broad-slice confirmation report

## Summary
- The new deterministic winner checkpoint from the peak-focused `ENERGY` objective family was re-screened beyond the original sample3 slice.
- Checkpoint under confirmation:
  - `reports/training/ss_detpitch_energypeak_s2_step1/checkpoints/ss_detpitch_energypeak_s2_step1.step1.pt`
- Two broader packet screens were run:
  - `target_validation`, `sample_count = 8`
  - `target_special_eval`, `sample_count = 8`
- Main result:
  - both broader screens pass cleanly
  - the route opening is no longer only a sample3-local result

## Inputs
- Confirmed checkpoint:
  - `ss_detpitch_energypeak_s2_step1.step1`
- Validation packet screen:
  - `reports/runtime/ss_pktsel_detpitch_energypeak_s2_step1_tv8/streaming_student_packet_checkpoint_selection.json`
- Special-eval packet screen:
  - `reports/runtime/ss_pktsel_detpitch_energypeak_s2_step1_se8/streaming_student_packet_checkpoint_selection.json`

## Target validation confirmation

| metric | value |
| --- | ---: |
| split | `target_validation` |
| sample_count | `8` |
| auto_reject_count | `0` |
| all_core_controls_ready_count | `8/8` |
| f0_ready_count | `8/8` |
| vuv_ready_count | `8/8` |
| aper_ready_count | `8/8` |
| energy_ready_count | `8/8` |
| avg_energy_stage5_norm_calibrated_reference_mae | `0.115441` |

- The former blocker record remains clean in this broader validation slice:
  - `target::chapter3_4_firefly_106`
  - `energy_stage5_norm_calibrated_reference_mae = 0.131030`

## Target special-eval confirmation

| metric | value |
| --- | ---: |
| split | `target_special_eval` |
| sample_count | `8` |
| auto_reject_count | `0` |
| all_core_controls_ready_count | `8/8` |
| f0_ready_count | `8/8` |
| vuv_ready_count | `8/8` |
| aper_ready_count | `8/8` |
| energy_ready_count | `8/8` |
| avg_energy_stage5_norm_calibrated_reference_mae | `0.085116` |

- This matters because the win is not limited to the original mainstream validation slice.
- The checkpoint also stays open on the current sampled `no_text_voice` special-eval slice.

## Main conclusion
- The earlier route-opening report is now broadly confirmed.
- The current strongest deterministic checkpoint:
  - opens all four core controls on the original sample3 screen
  - opens all four core controls on the broader `target_validation` 8-sample screen
  - opens all four core controls on the broader `target_special_eval` 8-sample screen
- Therefore this result should now be treated as the active deterministic reference checkpoint, not only as a local probe win.

## Decision
- Promote `ss_detpitch_energypeak_s2_step1.step1` as the current active deterministic packet-facing checkpoint.
- Treat the previous pre-redesign checkpoints as historical anchors only.

## Next actions
1. Keep this checkpoint as the active Stage3 deterministic reference.
2. Use it for downstream-facing confirmation work rather than reopening old `ENERGY` continuation probes.
3. Keep the old continuation-stop conclusion in place for the superseded objective family.
