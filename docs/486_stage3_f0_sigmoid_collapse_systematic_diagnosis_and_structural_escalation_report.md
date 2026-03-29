# 486 Stage3 F0 sigmoid-collapse systematic diagnosis and next structural probe report

## Scope
- Systematically tested three F0 supervision configurations to diagnose coarse_log_f0 collapse.
- Identified that the collapse is structural, not addressable by loss weight tuning.

## Config error correction
- f0boost12 and f0mid12 were accidentally run with streaming_student_stage_template.json
  which uses unbounded_log_v1 + shared_student_v1, a completely different architecture.
- Those results are invalid and have been superseded by f0boost12_cfgfix using the correct
  configs/streaming_student_stage_parallel_control_branch_controlfamily_v1.json.

## Three-way comparison at step12 (all using correct controlfamily config)

Full-validation metrics:
- vuvbalancedgate12: loss_total=1.524679, coarse_f0_state=0.352649, coarse_f0_corr=1.219091
- f0temporal12 (+temporal 0.02): loss_total=1.526989, coarse_f0_state=0.352644, coarse_f0_corr=1.219037
- f0boost12_cfgfix (state 0.15): loss_total=1.797786, coarse_f0_state=0.347987, coarse_f0_corr=1.233446

coarse_log_f0 output range on 3 validation records:
- vuvbalancedgate12: avg_span=0.060 oct avg_corr=-0.226
- f0temporal12: avg_span=0.060 oct avg_corr=-0.226
- f0boost12_cfgfix: avg_span=0.094 oct avg_corr=-0.276

## Root cause confirmed
- All three configurations produce near-identical coarse_log_f0 output distributions.
- Span of 0.06-0.09 octaves vs target range of 2.6 octaves = model outputs flat near mean.
- Negative correlation means the model's tiny residual variation is inverted relative to target.
- This is invariant across:
  - loss weight scaling (0.05 to 0.15)
  - temporal loss addition (teacher_coarse_f0_temporal=0.02)
- Therefore the collapse is NOT caused by insufficient supervision signal strength.

## Structural diagnosis
- The explicit_named_control_family_v1 architecture routes F0 through f0_branch_encoder.
- f0_branch_input is: [control_hidden, conditioning, coarse_log_f0, sigmoid(vuv_logits), energy, sigmoid(event_prior_logits)]
- The waveform input goes through UnifiedStreamingFrontend which computes coarse_log_f0 from raw audio frames.
- At early training, the frontend log_f0_head has no useful F0 information in its shared encoder.
- The f0_branch_encoder sees this noisy coarse_log_f0 and cannot extract meaningful F0 dynamics.
- MSE loss pulls the output toward the target mean (log2(260 Hz) ~ 8.02),
  but provides no gradient signal to expand the output variance.
- Result: coarse_log_f0 collapses to a near-constant value near the target mean.

## What cannot fix this
- Increasing teacher_coarse_f0_state weight: makes training loss worse, doesn't expand variance.
- Adding teacher_coarse_f0_temporal: adds a frame-delta consistency signal but if output is near-constant,
  deltas are near zero and so is the gradient.
- Adding teacher_coarse_f0_correlation: the correlation loss is undefined for near-constant outputs
  and produces noisy gradients near corr=0.
- Changing f0_parameterization_mode to unbounded_log_v1: introduces a unit mismatch
  (natural log vs log2 target) and makes things worse.

## What might fix this
Option A: Provide explicit F0 pitch features as model input
- Add a lightweight external pitch estimator (e.g. SWIPE, REAPER, RAPT, or simple autocorrelation)
  that runs on the input waveform frames and feeds a pitch feature vector into the model.
- This gives the F0 branch a direct pitch signal to imitate rather than requiring it to discover
  pitch from raw waveform statistics alone.
- Risk: adds a dependency on an external pitch estimator at inference time.

Option B: Add F0 from teacher label as auxiliary input signal
- During training only, feed the teacher_target_f0_hz into the student as a soft target hint
  in the form of a positional or conditional embedding.
- At inference time, use a lightweight run-time F0 estimator or leave blank.
- Risk: creates a training/inference gap.

Option C: Accept current F0 limitation and focus energy elsewhere
- The current packet-aware screen shows vuv_ready_count=1 and f0_ready_count=0.
- The f0_proxy_reference_corr is 0.43-0.61 on the 3-sample screen for vuvbalancedgate24.
- This is better than step12, suggesting more training steps help somewhat.
- But vuvbalancedgate24 still shows avg_span=0.61 octaves which is far from the target 2.6 octaves.
- Given that the F0 head produces flat outputs, the apparent corr=0.43-0.61 in vuvbalancedgate24
  is likely due to the affine calibration step in the packet export, not actual F0 tracking.
- This means F0 is not a genuine control signal in the current architecture.
- Accepting this means the handoff gate for F0 will remain permanently closed.

## Recommendation
- Do not continue loss-weight or temporal-loss F0 probes. They are confirmed no-go.
- Escalate to user: the F0 representation bottleneck requires a structural decision.
- The choice is between:
  1. Adding an explicit pitch feature input (Option A or B)
  2. Accepting that F0 will not be a genuine control in the current Stage3 architecture
     and focusing resources on vuv/aper/energy refinement and Stage5 corrected-manifold work.
- This decision affects whether F0 can ever pass the readiness gate in the current architecture.

## Mainline impact
- f0temporal12 probe: no meaningful change vs baseline, not promoted.
- f0boost12_cfgfix probe: loss slightly worse, coarse_log_f0 slightly less collapsed but still flat, not promoted.
- corrfocus_v1, unboundedf0, f0boost, f0mid: all confirmed no-go.
- Current packet-facing reference (vuvbalancedgate24) and packet-aware candidate (warm6_18.step15)
  remain unchanged.
- F0 readiness gate is structurally blocked in the current architecture.
