# Active Pitfalls Log

## Document Role
- This file keeps only the active pitfalls that still show up often and still distort decisions.
- Long historical snapshots are archived at:
  - `docs/archive/02_pitfalls_log_snapshot_20260326.md`
  - `docs/archive/02_pitfalls_log_snapshot_20260328.md`
- If a new issue is only a local detail from one experiment round, write it into the numbered report instead of this file.

## Current High-Priority Pitfalls

### 1. PowerShell text IO can silently corrupt active UTF-8 documents
- If content encoding is omitted, PowerShell text reads can fall back to GBK and produce mojibake.
- Even when UTF-8 is requested, common PowerShell write paths may add a BOM header.
- The repository standard is UTF-8 without BOM on disk.
- For active documents, use `apply_patch` or `.\python.exe` with explicit UTF-8 handling instead of default PowerShell text IO.

### 2. Do not extrapolate Stage3 progress into "the old Stage5 route is worth rerunning"
- The most informative current Stage3 layer is still generation-side.
- The old `Stage5 no-res downstream` route is formally retired as the default fallback route.

### 3. Do not rewrite retirement of the old Stage5 route as "stop all Stage5 fail-fast work"
- What stopped is the default old route, not all Stage5 validation.
- Only genuinely different handoff families are worth new Stage5 fail-fast work.

### 4. A wired contract or a populated summary field does not prove the experiment is valid
- First verify that parameters and metadata really propagate to the final artifact.
- Before interpreting results, verify the final package, dataset index, and summary objects.

### 5. Machine gate is only a negative gate, not proof of success
- `review_required` or "not auto rejected" does not mean success.
- Machine gate can automatically reject, but it cannot prove that a route is valid.

### 6. Once listening review confirms buzz, stop same-layer micro-tuning
- Pure buzz, pure fuzz, or no-voice structure cannot be fixed by endless small parameter scans.
- If a same-layer route is already identified by listening review as the wrong basin, retire it immediately.

### 7. A falling hidden or fused-hidden imitation loss does not prove the main route improved
- Do not look only at local imitation metrics.
- Also inspect global or route-relevant metrics such as:
  - `loss_total`
  - `loss_total_semantic_disabled_reference`
  - `loss_teacher_event`
  - `loss_teacher_event_prior`

### 8. Paired source-target data is not automatically valid frame-wise supervision
- Source waveform and target teacher frames are not naturally aligned.
- Do not open paired Stage3 training before a valid frame bridge and alignment contract exists.

### 9. New semantic assets need metadata, package, and index plumbing before consumer training
- If plumbing is unclear, later failures cannot be separated into wiring failures versus model failures.
- Connect metadata first, then run a minimal consumer or supervision validation.

### 10. `student_control_packet_v1` is not yet a Stage5-ready named-control contract
- Only `e_evt / z_art` can currently be treated as ready.
- `F0 / vuv / aper / E` are still proxy or control status, not handoff-ready contract fields.

### 11. "Roughly flat" cheap-screen results do not mean "ready to open a new Stage5 route"
- Packet readiness and a small loss improvement do not mean the handoff evidence is strong enough.
- Run packet or control calibration and readiness gate first, then decide on a new Stage5 adapter.

### 12. Silent reuse through `skip_existing` can hide real artifact changes
- Formal split outputs, packets, audio, checkpoints, calibration assets, and semantic or timing sidecars can all be contaminated by stale reuse.
- Any reuse must verify identity fingerprints before old outputs are treated as current outputs.

### 13. Detailed experiment journaling must not flow back into `docs/01` or `docs/02`
- `docs/01` and `docs/02` should keep only conclusions that still affect future decisions.
- Detailed history belongs in `docs/archive/` and the numbered reports.

### 14. Do not rewrite "stop low-value micro-tuning" into retirement of the active `wfta003` corrected-manifold line
- The valid stop rule is:
  - retire already dead pure-buzz families
  - keep materially different localization probes on the current active anchor
- `472` to `475` show that targeted localization pressure still produced real Stage5 gains inside the current corrected-manifold branch.

### 15. Do not restate `C-prime / v2-core` as if `e_evt` were the only immediate blocker
- Historical `C-prime` docs remain useful strategic context, but later readiness-gate evidence is more specific.
- The current immediate blocker for opening a new handoff route is still `F0 / vuv / aper / E`, not an abstract re-statement of `e_evt` alone.

### 16. Do not collapse different Stage3 checkpoint-selection objectives into one "best checkpoint"
- In-loop training validation, post-hoc full-checkpoint teacher-loss evaluation, and packet-aware downstream screening answer different questions.
- These selectors can disagree on the same checkpoint set without any single one being the only truth.
- Always state which selection objective produced the ranking before promoting or retiring a checkpoint family.

### 17. Do not keep using the legacy Stage3 selector name as if it were objective-neutral
- `select-streaming-student-best-checkpoint` is backward-compatible, but its name is historically ambiguous.
- For new work, prefer the explicit post-hoc teacher-loss selector naming in commands and reports.
- If the legacy name is used, the report must still state that the selector objective is post-hoc teacher-supervised loss.

### 18. Do not discuss Stage3 selector disagreement from memory when a combined comparison artifact can be generated
- If a checkpoint-family decision depends on both post-hoc teacher-loss ranking and packet-aware ranking, run the combined selector-comparison command first.
- Otherwise the discussion easily drifts into hand-written summaries that omit rank gaps, objective labels, or the actual top-1 disagreement status.
- The comparison artifact should be the first citation when explaining why two selector outputs disagree.

### 19. Do not stop at raw selector disagreement when the actual decision is role-splitting
- In the current mainline pattern, the practical decision is often:
  - one checkpoint as teacher-loss reference
  - another checkpoint as handoff-facing packet candidate
  - no unified best checkpoint
- When that happens, cite the comparison `decision_summary` directly instead of forcing a fake single-winner conclusion.

### 20. Do not let family-local packet-aware wins overwrite the incumbent global packet-facing reference by scope drift
- A checkpoint can be the packet-aware best inside one candidate family without displacing the current packet-facing reference across families.
- The current concrete example is:
  - `warm6_18.step15` as the next-best non-reference candidate
  - while `vuvbalancedgate24.step24` still holds the packet-facing reference role
- If the report scope is cross-family, use a role-aware comparison with an explicit packet reference checkpoint.

### 21. Do not treat Windows long-path warnings as harmless filesystem noise
- If a managed artifact path starts tripping sandbox or Win32-style path limits, fix the writer immediately.
- Shorten:
  - output root leaves
  - nested subdirectory names
  - repeated experiment-id path components
- Then regenerate or relocate the artifact and update the citing docs.


### 22. Do not run further F0 loss-weight or temporal-loss probes without a structural model change
- Systematic testing (484-486) confirmed: coarse_log_f0 collapses to near-constant output (span 0.06 octaves vs target 2.6 octaves) in the explicit_named_control_family_v1 architecture.
- This is invariant across: loss weight scaling (0.05 to 0.15), temporal loss addition, correlation loss addition.
- The root cause is that the waveform frontend cannot extract meaningful F0 dynamics from raw audio frames without an explicit pitch feature input.
- Probes already confirmed no-go: corrfocus_v1, unbounded_log_v1 (has unit mismatch bug), f0boost, f0mid, f0temporal.
- Do not retry any of these. The next valid probe requires a structural model change.

### 23. unbounded_log_v1 F0 parameterization has a unit mismatch bug
- The loss function computes target_log_f0 = torch.log2(teacher_target_f0_hz) which is in log2 scale (range 7-9).
- The unbounded_log_v1 head outputs in natural log / linear scale (range 4-5 after training).
- MSE between these is always large (~12) and gradients point in wrong directions.
- Do not use unbounded_log_v1 for F0 without first fixing the loss unit to match.

### 24. When comparing Stage3 probes, always verify the model config matches the baseline
- The streaming_student_stage_template.json defaults differ from the controlfamily config used for vuvbalancedgate runs.
- Using the template produces a different architecture (shared_student_v1 + unbounded_log_v1) vs the baseline (explicit_named_control_family_v1 + bounded_log2_hz_v1).
- Always specify --config configs/streaming_student_stage_parallel_control_branch_controlfamily_v1.json for Stage3 probes that intend to compare against vuvbalancedgate runs.

### 25. Do not treat waveform-only implicit F0 discovery as an architectural requirement
- The current Stage3 failure is evidence against the present waveform-only route, not evidence that explicit external pitch signals are invalid.
- External specialist pitch extraction is a legitimate engineering choice for a realtime-capable system.
- Once the current frontend route is structurally blocked, the next valid move is a provider-side structural probe, not more loss micro-tuning.

### 26. Do not keep third-party reference repositories mixed into the main project root after extraction of lessons
- Reference repos can be useful for short-lived code reading.
- They should not remain as long-term root-level project directories once the relevant ideas are captured in formal docs.
- If retention is still useful, move them into a clearly marked reference location such as `tmp/reference_repos/` instead of leaving them mixed with the main repo structure.

## Current Maintenance Rules
- Before adding a new pitfall, decide whether it will keep affecting multiple future decisions.
- If it is only a local experiment conclusion, keep it in the corresponding numbered report.
- If this file grows too much again, archive a new snapshot instead of turning it back into a giant history file.

## Key Reference Reports
- `docs/370_stage3_to_stage5_downstream_handoff_candidates_report.md`
- `docs/371_stage3_student_control_packet_v1_bootstrap_and_proxy_screen_smoke_report.md`
- `docs/372_stage3_student_control_packet_v1_cheap_screen_ab_report.md`
- `docs/374_stage3_student_control_packet_readiness_gate_report.md`
- `docs/389_stage3_student_packet_minimal_stage5_adapter_and_decoded_smoke_fail_report.md`
- `docs/447_repo_health_and_compliance_audit_20260328.md`
- `docs/475_stage5_corrected_manifold_vnc01_maskfix_wfta003_followup_report.md`
- `docs/476_root_1md_strategy_memo_independent_assessment.md`
- `docs/477_stage3_packet_aware_checkpoint_selector_integration_and_selection_drift_report.md`
- `docs/478_stage3_selector_naming_hardening_and_legacy_alias_report.md`
- `docs/479_stage3_selector_comparison_cli_and_divergence_materialization_report.md`
- `docs/480_stage3_selector_comparison_decision_summary_hardening_report.md`
- `docs/481_stage3_packet_reference_vs_warm6_candidate_role_aware_comparison_report.md`
- `docs/482_windows_path_budget_and_artifact_naming_policy.md`
- `docs/483_stage3_selector_output_path_budget_remediation_report.md`
- `docs/484_stage3_f0_corrfocus_nogo_and_sigmoid_collapse_diagnosis_report.md`
- `docs/485_stage3_f0_unboundedf0_unit_mismatch_and_corrected_root_cause_report.md`
- `docs/486_stage3_f0_sigmoid_collapse_systematic_diagnosis_and_structural_escalation_report.md`
- `docs/487_stage3_rvc_reference_review_and_rmvpe_sidecar_plan_report.md`
