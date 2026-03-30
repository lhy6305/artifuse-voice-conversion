# Stage3 RMVPE confidence short-loop and packet-selector report

## Summary
- Ran a short controlled Stage3 training loop on:
  - `rmvpe_confidence_v1`
- The short loop produced:
  - decreasing train loss
  - improving sampled validation loss
  - six checkpoint artifacts for packet-facing screening
- Packet-aware checkpoint selection still found:
  - `f0_ready_count = 0/3` for every checkpoint
  - `auto_reject_count = 3/3` for every checkpoint
- So short-loop optimization did not convert the confidence-aware RMVPE route into a packet-ready `F0` handoff path.

## Artifacts
- Training loop summary:
  - `reports/training/streaming_student_rmvpeconf_loop_short/logs/streaming_student_rmvpeconf_loop_short.summary.json`
- Packet-aware selector summary:
  - `reports/runtime/streaming_student_packet_checkpoin_ample3_539eea/streaming_student_packet_checkpoint_selection.json`

## Training-loop result
- Training loop configuration:
  - `6` steps
  - batch size `2`
  - sampled validation every `2` steps
- Loss trend:
  - train `loss_total` fell from `7.470232` at step `1` to `3.148796` at step `6`
  - sampled validation `loss_total` was:
    - step `2`: `4.434691`
    - step `4`: `2.72968`
    - step `6`: `2.861254`
- By sampled validation, the loop winner was:
  - step `4`

## Packet-aware selector result
- The packet-aware selector evaluated steps `1` to `6` on `target_validation` sample3.
- Best checkpoint by packet screen:
  - step `3`
- Packet-facing selector summary for all six checkpoints:
  - steps `1` to `6` all had:
    - `auto_reject_count = 3`
    - `all_core_controls_ready_count = 0`
    - `f0_ready_count = 0`
    - `vuv_ready_count = 2`
- Aggregate packet metrics changed only slightly across the loop:
  - `avg_f0_proxy_reference_corr`
    - step `1`: `-0.061261`
    - step `6`: `-0.056948`
  - `avg_f0_calibrated_log2_mae`
    - step `1`: `1.075175`
    - step `6`: `1.009708`
- These shifts are directionally better but remain far from the readiness gate.

## Shape of the later checkpoints
- Later checkpoints changed non-F0 readiness tradeoffs more than F0 readiness:
  - steps `1` to `3`: `aper_ready_count = 2`, `energy_ready_count = 0`
  - step `4`: `aper_ready_count = 1`, `energy_ready_count = 2`
  - steps `5` to `6`: `aper_ready_count = 0`, `energy_ready_count = 1`
- The selector kept step `3` because the rule prioritizes:
  - fewer auto rejects
  - more all-core-ready records
  - more `vuv` ready
  - more `f0` ready
  - more `aper` ready
  - more `energy` ready
  - then lower average calibration errors
- Since all checkpoints tied on the early fields and all failed `F0`, step `3` stayed the least-bad packet-facing choice.

## Interpretation
- The confidence-aware RMVPE provider remains a meaningful structural probe:
  - provider-only metrics improved strongly versus the old thresholded RMVPE route
- But the current Stage3 consumer and current short-loop loss mix still do not translate that better provider contract into packet-facing `F0` readiness.
- This round also confirms again that:
  - sampled validation choice and packet-aware choice are different objectives
  - disagreement between step `4` and step `3` is real but not the main story
  - the main story is that neither choice opens the route

## Decision
- Keep `rmvpe_confidence_v1` as an archived experimental branch, not an active route-opening candidate.
- Keep `deterministic_extractor_v1` as the only validated Stage3 pitch-provider reference.
- Do not continue the same short-loop pattern by inertia.

## Next actions
1. If RMVPE work continues, make the next probe a richer contract change:
   - salience-aware or confidence-aware consumer logic
   - explicit voiced-support modeling
   - or a different `F0` supervision and calibration objective
2. Do not spend more time on:
   - longer copies of the same loop
   - more threshold tuning
   - more packet screening on the unchanged confidence-aware consumer
3. Keep the mainline focus on:
   - deterministic-provider-backed structural reference work
   - generation-side completion
   - packet-gated handoff decisions outside the blocked RMVPE branch
