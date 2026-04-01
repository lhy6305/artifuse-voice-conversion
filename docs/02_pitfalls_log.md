# Active Pitfalls Log

## Document Role
- This file keeps only active pitfalls that still distort current decisions.
- Long historical snapshots are archived at:
  - `docs/archive/02_pitfalls_log_snapshot_20260326.md`
  - `docs/archive/02_pitfalls_log_snapshot_20260328.md`
  - `docs/archive/02_pitfalls_log_snapshot_20260401.md`
- If an issue is only a local detail from one round, write it into the numbered report instead of this file.

## Current High-Priority Pitfalls

### 1. PowerShell text IO can silently corrupt active UTF-8 documents
- If content encoding is omitted, PowerShell can read as GBK and produce mojibake.
- Common PowerShell write paths can also add a BOM header.
- For active documents, use `apply_patch` or `.\python.exe` with explicit UTF-8 handling.

### 2. Detailed experiment journaling must not flow back into `docs/01` or `docs/02`
- Active docs should keep only decisions that still affect future work.
- Detailed history belongs in numbered reports and `docs/archive/`.

### 3. Machine gate is only a negative gate, not proof of success
- `review_required` or "not auto rejected" does not prove quality.
- Human review or stronger structure-facing evidence is still required before calling a route open.

### 4. Once repeated listening review still says "same stripe-pattern buzz", stop same-layer Stage5 polish
- Lower harshness, lower brightness, or more intermittency does not equal speech emergence.
- If human review still hears the same non-speech basin, escalate the abstraction level.

### 5. Do not confuse oracle sufficiency with a deployable solution
- An analysis-only oracle can prove that a signal class is sufficient.
- It does not prove that the current training code can predict that signal class.

### 6. Do not confuse a compact magnitude-style dense sidecar with the waveform-geometry signal class that the oracle actually requires
- The recent oracle result is not "any denser sidecar works".
- The key discriminator is local waveform geometry, not merely more scalar or spectral summary channels.

### 7. Do not treat the current upstream diagnosis as a strict proof that downstream cannot still matter
- The strongest current conclusion is:
  - upstream representation and contract are the default main suspect
- It is not:
  - a formal proof that no stronger downstream consumer or objective could use the old contract better

### 8. Do not reopen another broad Stage5-local regularizer sweep before a new upstream code exists
- Recent work already showed that regularizers can change brightness and RMS while preserving the same non-speech basin.
- The next discriminative experiment should be representation-side, not another local loss shuffle.

### 9. On the upper-bound waveform-code route, lower brightness and better RMS do not by themselves mean the useful structure survived
- The useful readout is whether structure-facing alignment and record-specific geometry stay alive.
- A checkpoint that looks calmer spectrally can still destroy the signal that mattered.

### 10. Do not rank waveform-regularized checkpoints by validation loss alone
- Once waveform regularizers are active, `loss_total` can disagree with the machine traits that matter for listening.
- Use role-aware checkpoint selection and cite the actual structure-facing metrics.

### 11. Do not hand off listening review with scattered runtime artifacts
- When human listening is the next critical-path step, keep audio, spectrograms, manifests, and machine summaries in one bundle directory.

### 12. Silent reuse through `skip_existing` can hide real artifact changes
- Reused packets, packages, exports, and summaries must be identity-checked before they are treated as current outputs.

## Current Maintenance Rules
- If this file grows too much again, archive a new snapshot instead of turning it back into a long historical log.
- Prefer keeping only the pitfalls that still affect the next concrete decision.

## Active Reference Reports
- `docs/566_stage5_richercontract_listening_result_self_audit_and_next_direction_report.md`
- `docs/567_stage3_fine_structure_reference_oracle_gate_report.md`
- `docs/568_stage5_fine_structure_code_oracle_and_wavepca16_bootstrap_report.md`
- `docs/569_stage5_wavepca16_upper_bound_bounded_training_and_regularizer_report.md`
- `docs/570_active_docs_archive_and_next_plan_refresh_report.md`
