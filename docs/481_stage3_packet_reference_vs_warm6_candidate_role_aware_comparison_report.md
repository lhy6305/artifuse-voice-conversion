# 481 Stage3 packet-reference vs warm6 candidate role-aware comparison report

## Scope
- Use the hardened combined selector-comparison tool on the two most important current Stage3 checkpoints:
  - incumbent packet-facing reference:
    - `vuvbalancedgate24.step24`
  - current non-reference warm-start candidate:
    - `warm6_18.step15`
- Run the comparison in role-aware mode with an explicit packet reference checkpoint.

## Inputs
- Packet reference checkpoint:
  - `reports/training/streaming_student_loop_vuvbalancedgate24_round1_1/checkpoints/streaming_student_stage_loop_vuvbalancedgate24_round1_1.step24.pt`
- Warm-start candidate checkpoint:
  - `reports/training/streaming_student_loop_timingfocus6warm_baseline18_denseckpt_round1_1/checkpoints/streaming_student_stage_loop_timingfocus6warm_baseline18_denseckpt_round1_1.step15.pt`
- Comparison output:
  - `reports/eval/ss_cmp_vbg24_vs_w6s15_r1_1/`

## Verification
- Command family:
  - `.\python.exe -m v5vc.cli compare-streaming-student-checkpoint-selectors ...`
  - with:
    - `--packet-reference-checkpoint vuvbalancedgate24.step24`
    - `PYTHONPATH=src`
- Result:
  - command completed successfully
  - combined comparison report and decision summary were generated

## Main Findings

### 1. The current packet-facing reference still holds
- Packet-aware selector winner:
  - `vuvbalancedgate24.step24`
- Combined role-aware output states:
  - `packet_reference_holds = true`
- This is supported by the packet row:
  - `energy_ready_count = 3`
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.108172`
  - `avg_aper_calibrated_reference_mae = 0.11809`
  - `avg_f0_proxy_reference_corr = 0.430536`

### 2. `warm6_18.step15` remains the strongest non-reference candidate, not the new packet leader
- Current role-aware output states:
  - `packet_aware_next_best_nonreference_candidate_checkpoint = warm6_18.step15`
- Its packet row is still meaningful but not enough to displace the incumbent reference:
  - `energy_ready_count = 2`
  - `avg_vuv_reference_mae = 0.18271`
  - `avg_aper_calibrated_reference_mae = 0.118447`
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.143582`
- So the current honest wording is:
  - packet-facing reference:
    - `vuvbalancedgate24.step24`
  - packet-aware next-best non-reference candidate:
    - `warm6_18.step15`

### 3. Teacher-loss leadership and packet leadership remain split
- Post-hoc teacher-loss leader:
  - `warm6_18.step15`
  - `target_validation_loss_total = 1.476498`
  - `target_special_eval_loss_total = 1.162192`
- Packet-screen leader:
  - `vuvbalancedgate24.step24`
  - `target_validation_loss_total = 1.713152`
  - `target_special_eval_loss_total = 1.135832`
- Therefore:
  - `unified_best_checkpoint = null`
  - `top1_agree = false`

### 4. The route-opening decision remains negative
- Combined role-aware output states:
  - `open_new_stage5_route_recommended = false`
- Rationale:
  - the packet-aware top checkpoint still shows sampled auto-reject behavior
- This remains consistent with all current Stage3-to-Stage5 gate evidence:
  - no compared checkpoint is ready to open a new Stage5 route

## Judgment
- This report formalizes the current Stage3 role split cleanly:
  - `vuvbalancedgate24.step24` is still the incumbent packet reference
  - `warm6_18.step15` is still the best non-reference packet candidate and the teacher-loss leader
- That split is stable enough to write as the current mainline state.
- It should replace looser wording like:
  - "warm6.step15 is packet-aware best"
  - unless the scope is explicitly restricted to the warm6 dense subfamily only

## Mainline Impact
- Keep current active Stage3 checkpoint roles as:
  - packet-facing reference:
    - `vuvbalancedgate24.step24`
  - packet-aware next-best non-reference candidate:
    - `warm6_18.step15`
  - teacher-loss leader for this two-way comparison:
    - `warm6_18.step15`
  - unified best checkpoint:
    - none
  - open new Stage5 route:
    - no
- Future reports should distinguish:
  - family-local packet-aware best inside a candidate family
  - global incumbent packet-facing reference across families

## Key Artifact
- Role-aware comparison output:
  - `reports/eval/ss_cmp_vbg24_vs_w6s15_r1_1/streaming_student_checkpoint_selector_comparison.json`
