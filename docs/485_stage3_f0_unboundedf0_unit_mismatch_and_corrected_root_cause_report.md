# 485 Stage3 F0 unbounded_log_v1 unit mismatch diagnosis and parameterization root cause report

## Scope
- Tested `f0_parameterization_mode = unbounded_log_v1` as a candidate to break sigmoid-midpoint collapse.
- Diagnosed a pre-existing unit mismatch bug in the loss computation.
- Refocused the F0 bottleneck diagnosis to the correct root cause.

## unbounded_log_v1 probe result
- `unboundedf0_vuvbg12` at step12 full-validation:
  - `loss_total = 2.825132`
  - `loss_teacher_coarse_f0_state = 11.324607`
  - `loss_teacher_f0_state = 9.139885`
  - `coarse_log_f0` output range: `[4.28, 4.70]`
  - `coarse_log_f0` correlation with target log2 F0: `-0.46, -0.01, -0.45`
- This is clearly worse than `vuvbalancedgate12` (loss_total=1.524679).
- Probe is no-go.

## Root cause: unit mismatch in unbounded_log_v1
- Loss computation always uses `target_log_f0 = torch.log2(teacher_target_f0_hz.clamp_min(1.0))`
  - Target range: ~7.3 to 9.1 (log2 of Hz values 160-550)
- `unbounded_log_v1` outputs a raw linear head with no bounding
  - After random init the head outputs are near 0
  - After 12 steps the outputs converge to ~4.4-4.7 (natural log of 80-110 Hz)
  - But the loss target is log2 scale (7-9), not natural log scale (4-5)
  - MSE is therefore (4.5 - 8.0)^2 ~ 12.2, matching observed loss_coarse_f0_state=11.3
- This is a structural unit mismatch that cannot be fixed by training longer.
- `unbounded_log_v1` is permanently broken for F0 supervision in the current loss function.

## Actual root cause of the bounded_log2_hz_v1 F0 collapse
- `bounded_log2_hz_v1` is in the correct unit (log2 Hz), no mismatch.
- But after 24 steps, `coarse_log_f0` output range is still only [7.68, 8.29] (0.61 octaves)
  while target range spans [6.5, 9.1] (2.61 octaves).
- The sigmoid function `floor + sigmoid(raw) * (ceil - floor)` has output range [5.64, 9.10].
  The model converges to a narrow midpoint band, not because of unit mismatch,
  but because the F0 supervision signal is too weak to push the sigmoid away from center.
- With current weights `teacher_coarse_f0_state=0.05` and 6-step linear warmup,
  the F0 gradient is a small fraction of the total loss,
  and the model default behavior (sigmoid near 0.5) is a strong attractor.

## Corrected next probe direction
- The fix must make the F0 supervision signal stronger relative to the midpoint attractor.
- Do not try more parameterization changes. Both bounded and unbounded have been tested.
- The next probe should increase `teacher_coarse_f0_state` weight significantly
  and reduce or eliminate the warmup schedule for the F0 loss.
- Candidate: `teacher_coarse_f0_state = 0.15` with no warmup (or 2-step warmup only)
- Keep `bounded_log2_hz_v1` and `explicit_named_control_family_v1` unchanged.
- Success condition: `coarse_log_f0` output range widens beyond 1.0 octaves at step12,
  and `f0_proxy_reference_corr` improves on the 3-sample packet screen.
- Stop rule: if `loss_total` at step12 exceeds `vuvbalancedgate12` by more than 0.3,
  or if `vuv_ready_count` drops below 1, stop.

## Mainline impact
- No change to current packet-facing reference or packet-aware candidate.
- `unbounded_log_v1` is confirmed structurally broken for F0 in the current loss function.
  Do not use it again without first fixing the loss unit to match.
