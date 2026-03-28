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
