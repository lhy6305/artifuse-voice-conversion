# Stage3 deterministic no-f0-correction energy tradeoff and warm-start no-go report

## Summary
- Continued the deterministic provider line after the RMVPE family was retired as the active route-opening branch.
- The key objective was no longer raw `F0` recovery.
- The key objective became:
  - preserve the already-open deterministic `F0 / VUV / APER` pattern
  - improve `ENERGY`
  - test whether a better packet tradeoff can be reached by warm-starting from the packet-best deterministic checkpoint
- The result is negative but decisive:
  - deterministic `nof0corr` is now the strongest Stage3 packet reference on the current sample3 slice
  - scalar energy reweighting can improve `ENERGY`
  - but it does so by damaging the already-open `F0 / APER` state
  - warm-starting from the packet-best deterministic checkpoint does not preserve the earlier `F0` opening

## Evaluated runs

### 1. Deterministic no-f0-correction short loop
- Training summary:
  - `reports/training/ss_detpitch_nof0corr_loop6/logs/ss_detpitch_nof0corr_loop6.summary.json`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_nof0corr6/streaming_student_packet_checkpoint_selection.json`
- Best packet checkpoint:
  - step `1`
- Best packet readiness:
  - `f0_ready_count = 3/3`
  - `vuv_ready_count = 3/3`
  - `aper_ready_count = 2/3`
  - `energy_ready_count = 0/3`
  - `auto_reject_count = 3/3`
- Best packet averages:
  - `avg_f0_proxy_reference_corr = 1.0`
  - `avg_f0_calibrated_log2_mae = 0.02182`
  - `avg_vuv_reference_mae = 0.006132`
  - `avg_aper_calibrated_reference_mae = 0.282262`
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.707125`

### 2. Deterministic no-f0-correction plus energy-focus from scratch
- Training summary:
  - `reports/training/ss_detpitch_nof0corr_energyfocus_loop6/logs/ss_detpitch_nof0corr_energyfocus_loop6.summary.json`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_nof0corr_energyfocus6/streaming_student_packet_checkpoint_selection.json`
- Best packet checkpoint:
  - step `1`
- Best packet readiness stayed effectively unchanged:
  - `f0_ready_count = 3/3`
  - `vuv_ready_count = 3/3`
  - `aper_ready_count = 2/3`
  - `energy_ready_count = 0/3`
- Best packet averages stayed effectively unchanged:
  - `avg_f0_calibrated_log2_mae = 0.038542`
  - `avg_aper_calibrated_reference_mae = 0.282589`
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.707125`
- But later checkpoints showed a real energy tradeoff:
  - step `5`: `f0_ready_count = 1/3`, `aper_ready_count = 0/3`, `energy_ready_count = 2/3`, `avg_energy_stage5_norm_calibrated_reference_mae = 0.132437`
  - step `6`: `f0_ready_count = 1/3`, `aper_ready_count = 0/3`, `energy_ready_count = 2/3`, `avg_energy_stage5_norm_calibrated_reference_mae = 0.122613`
- Interpretation:
  - scalar energy emphasis can move `ENERGY`
  - but the current consumer and objective mix cannot keep the earlier `F0 / APER` packet state while doing it

### 3. Warm-start energy-focus from the packet-best deterministic checkpoint
- Init checkpoint:
  - `reports/training/ss_detpitch_nof0corr_loop6/checkpoints/ss_detpitch_nof0corr_loop6.step1.pt`
- Training summary:
  - `reports/training/ss_detpitch_nof0corr_energyfocus_warm4/logs/ss_detpitch_nof0corr_energyfocus_warm4.summary.json`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_nof0corr_energyfocus_warm4/streaming_student_packet_checkpoint_selection.json`
- Sampled validation improved further than both earlier runs:
  - warm-start best sampled validation: step `4`, `loss_total = 2.202795`
  - scratch energy-focus best sampled validation: step `4`, `loss_total = 2.344869`
  - deterministic nof0corr best sampled validation: step `4`, `loss_total = 2.557129`
- But packet behavior regressed immediately:
  - packet-best warm-start checkpoint is step `1`
  - `f0_ready_count = 0/3`
  - `vuv_ready_count = 3/3`
  - `aper_ready_count = 2/3`
  - `energy_ready_count = 0/3`
  - `avg_f0_calibrated_log2_mae = 0.337563`
  - `avg_aper_calibrated_reference_mae = 0.28057`
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.707125`
- The late warm-start tradeoff still followed the same pattern:
  - step `4`: `f0_ready_count = 0/3`, `aper_ready_count = 0/3`, `energy_ready_count = 2/3`, `avg_energy_stage5_norm_calibrated_reference_mae = 0.151419`
- Interpretation:
  - warm-starting from the packet-best deterministic checkpoint does not preserve its already-open `F0` state under the current energy-focused objective
  - the first resumed checkpoint already loses packet-facing `F0` readiness
  - this is stronger evidence than the scratch run because it rules out "bad random init" as the main explanation

## Main conclusion
- The deterministic provider line is no longer blocked by `F0` on the current sample3 screen.
- The strongest current packet reference is:
  - deterministic provider
  - `f0_correction_enabled = false`
  - packet-best checkpoint at step `1`
- On that reference:
  - `F0` is open on `3/3`
  - `VUV` is open on `3/3`
  - `APER` is close on `2/3`
  - `ENERGY` remains the dominant blocker at `0/3`
- The remaining failure is not that `ENERGY` is immovable.
- The remaining failure is that the current scalar-loss route improves `ENERGY` only by giving back `F0` and `APER`.

## Decision
- Stop further same-family scalar weight nudging on top of the current deterministic nof0corr scaffold.
- Do not continue:
  - more energy proxy vs energy state scalar scans
  - more short warm-start loops with the same objective family
  - more packet selector retries hoping for a lucky checkpoint
- The next valid escalation must change the optimization structure, not just the scalar weights.

## Next actions
1. Keep `deterministic_extractor_v1` plus `f0_correction_enabled = false` as the current Stage3 packet-facing reference for explicit pitch-provider work.
2. Treat `ENERGY` as the main remaining named-control blocker on this line.
3. If this line continues, require a larger design change such as:
   - energy-isolated optimization
   - stagewise freeze of already-open controls
   - or another objective split that protects `F0 / VUV / APER` while training `ENERGY`
