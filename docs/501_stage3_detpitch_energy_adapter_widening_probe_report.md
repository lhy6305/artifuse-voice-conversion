# Stage3 deterministic dedicated energy-adapter widening probe report

## Summary
- Tested the next planned structural escalation on the deterministic isolated `ENERGY` line:
  - keep the dedicated energy branch
  - widen its hidden dimension from `96` to `192`
  - keep the rest of the scaffold frozen
- The widened branch is valid and trainable.
- But it does not improve packet-facing `ENERGY` beyond the existing dedicated-branch result.
- Worse, the widened branch shows unstable short-loop behavior:
  - step `1` keeps partial energy improvement
  - later steps fall back to the old `0.707125` energy plateau

## Implementation
- Files changed:
  - `src/v5vc/streaming_student/model.py`
  - `src/v5vc/streaming_student/plan_entry.py`
  - `src/v5vc/streaming_student/checkpoint_init.py`
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_nof0corr_energyadapterwidefreeze_v1.json`
- New model option:
  - `energy_control_branch_hidden_dim`
- Current probe value:
  - `192`
- Partial init helper was also hardened:
  - partial warm-start now skips checkpoint tensors whose shapes no longer match widened parameters

## Smoke
- One-step smoke:
  - `reports/training/ss_detpitch_energyadapterwide_smoke/logs/ss_detpitch_energyadapterwide_smoke.step1.json`
- The smoke confirms:
  - widened branch config is valid
  - partial init reports the expected shape-mismatch skip
  - the widened dedicated branch remains the only trainable isolated subset

## Warm-start short loop
- Config:
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_nof0corr_energyadapterwidefreeze_v1.json`
- Loss override:
  - `configs/streaming_student_loss_weights_detpitch_energy_state_focus_v1.json`
- Init checkpoint:
  - `reports/training/ss_detpitch_nof0corr_loop6/checkpoints/ss_detpitch_nof0corr_loop6.step1.pt`
- Training summary:
  - `reports/training/ss_detpitch_energyadapterwide_warm4/logs/ss_detpitch_energyadapterwide_warm4.summary.json`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_energyadapterwide_warm4/streaming_student_packet_checkpoint_selection.json`

## Packet result
- All screened checkpoints preserve the already-open controls:
  - `f0_ready_count = 3/3`
  - `vuv_ready_count = 3/3`
  - `aper_ready_count = 2/3`
  - `energy_ready_count = 0/3`
- The best energy value in the screened set appears at step `1`:
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.550949`
- But the packet selector still ranks step `2` first because the current lexicographic rule prioritizes:
  - readiness counts
  - then `VUV`
  - then `APER`
  - then `ENERGY`
- More importantly, even the best energy value in this widened family is still worse than the previous dedicated-branch result.

## Comparison vs previous dedicated energy-adapter freeze
- Previous dedicated-branch report:
  - `docs/499_stage3_detpitch_energy_adapter_freeze_probe_report.md`
- Previous packet-best energy:
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.550192`
- Current widened family best energy:
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.550949`
- So naive widening from `96` to `192` does not improve the isolated energy branch in packet-facing terms.

## Main conclusion
- The deterministic energy line is now narrowed again:
  - strict two-head freeze was too weak
  - dedicated branch at `96` gave a real but sub-threshold improvement
  - simple gate-scale loss alignment did not materially help
  - simple branch widening to `192` also does not help and appears less stable across short-loop steps
- This means the next valid move should not be more naive width escalation by inertia.

## Decision
- Keep the dedicated energy-branch family as the active isolated `ENERGY` scaffold.
- Do not continue more same-style widening probes without a more specific architectural reason.
- The next meaningful escalation should be more structured than "make the branch wider".

## Next actions
1. Stop naive energy-branch widening as a default next move.
2. If the deterministic energy line continues, prefer one of:
   - more structured isolated energy capacity
   - or a more direct packet-facing energy objective
3. Keep using packet-aware screening as the downstream-facing check, but read the ranking together with raw energy metrics when the family goal is specifically `ENERGY`.
