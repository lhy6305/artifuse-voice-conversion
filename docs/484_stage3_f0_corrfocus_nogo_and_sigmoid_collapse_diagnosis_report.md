# 484 Stage3 F0 corrfocus probe no-go and sigmoid-midpoint collapse diagnosis report

## Scope
- Tested a minimal `teacher_coarse_f0_correlation` weight addition on top of `vuv_balanced_gate`.
- Identified the root cause of the persistent `f0_proxy_reference_corr ~ 0.4-0.6` ceiling.

## Probe Configuration
- New config: `configs/streaming_student_loss_weights_vuv_balanced_gate_corrfocus_v1.json`
- Changes vs `vuv_balanced_gate_v1`:
  - added `teacher_coarse_f0_correlation = 0.03` with 3-step warmup
  - all other weights unchanged
- Model architecture: `bounded_log2_hz_v1`, `explicit_named_control_family_v1`, same as `vuvbalancedgate12`

## Also fixed in this round
- `src/v5vc/streaming_student/train_step_entry.py`
  - added `init_checkpoint_path` parameter to match the CLI call signature
  - CLI was already passing this argument since round 457 but the function signature was missing it

## Corrfocus probe result
- `vuvbalancedgate12` baseline at step12:
  - `loss_total = 1.524679`
  - `loss_teacher_coarse_f0_correlation = 1.219091` (weight was 0.0)
  - `loss_teacher_coarse_f0_state = 0.352649`
- `corrfocus12` candidate at step12:
  - `loss_total = 3.200963`
  - `loss_teacher_coarse_f0_correlation = 1.062768` (weight was 0.03)
  - `loss_teacher_coarse_f0_state = 14.999751`
  - `loss_teacher_vuv_proxy = 0.69177`
  - `loss_log_f0_correction_l1 = 1.918658`
- All other metrics substantially worse than baseline.
- This is a clear no-go.

## Root Cause: sigmoid-midpoint collapse in bounded_log2_hz_v1
- Direct inspection of `vuvbalancedgate24.step24` packet diagnostics:
  - `coarse_log_f0` output range: `[7.68, 8.29]` (span of 0.61 octaves)
  - Target `log2(F0)` range: `[6.50, 9.11]` (span of 2.61 octaves)
  - Per-record `proxy_reference_corr` on voiced frames: `0.011, 0.064, 0.015`
- This is not a loss-weight problem. The model outputs are effectively constant.
- The `bounded_log2_hz_v1` sigmoid initialization collapses near the midpoint:
  - `log2(50) = 5.644`, `log2(550) = 9.103`, midpoint = `7.374` Hz_equiv = `165.8 Hz`
  - Observed center `~7.99` is above midpoint, suggesting some bias but still extremely compressed
- Because the output is near-constant, `coarse_f0_correlation = (1 - corr)` is permanently near `1.0`.
- Adding a gradient on correlation does not expand the output range, it only injects noise.
- The `corrfocus_v1` approach cannot fix this problem.

## Why this is a new insight
- Previous probes (strong_voiced_gate, rebalance, transition_blend) focused on supervision contract.
- This is the first direct check of actual `coarse_log_f0` output distribution at step24.
- The bottleneck is not the supervision mask or loss weight. It is the model\'s output collapsing to a narrow range.

## Next probe direction
- The correct fix is not another supervision-side mask or weight.
- The correct fix is to break the sigmoid-midpoint collapse in `coarse_log_f0`.
- Candidates:
  1. Switch `f0_parameterization_mode` from `bounded_log2_hz_v1` to `unbounded_log_v1`
     - Removes the sigmoid compression entirely
     - Model then relies on state-loss gradients to find the right scale
     - Risk: without bounds, early training can diverge
     - Mitigation: use a stronger `teacher_coarse_f0_state` weight warmup
  2. Keep `bounded_log2_hz_v1` but initialize the final sigmoid weight layer with a larger range
     - More invasive change to model init code
  3. Widen the sigmoid output range (floor/ceil) to exaggerate the gradient signal
     - Risk: creates a mismatch between what is supervised and what Stage5 expects
- Recommended immediate next probe: switch to `unbounded_log_v1` and re-run `vuvbalancedgate12`
  - This is a config-only change (no new model code)
  - It directly tests whether the parameterization was the bottleneck
  - Stop rule: if `coarse_log_f0` output range stays compressed at step12, the collapse is coming from training dynamics, not the bounded sigmoid

## Mainline impact
- `corrfocus_v1` probe: stopped at step12, no-go.
- No change to current packet-facing reference (`vuvbalancedgate24`) or packet-aware candidate (`warm6_18.step15`).
- `train_step_entry.py` signature fix: low-risk plumbing correction, does not change behavior.
