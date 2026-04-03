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

### 13. Do not keep sweeping code source-mode when all variants remain below the old selected-dynamic baseline
- `student_hidden_v1`, `shared_hidden_v1`, and `control_hidden_v1` can differ slightly without changing the actual decision.
- If every source-mode variant still stays below `selected_dynamic_controls` on the same full5 oracle, the next variable must be supervision or objective design, not another hidden-tap swap.

### 14. Do not mistake auxiliary improvement in selected_dynamic_controls for success of the exported compact code
- A new supervision target can improve `selected_dynamic_controls` while leaving `predicted_fine_structure_code_family` weak.
- The producer-side contract is only improved when the exported predicted code itself gets stronger on the oracle, not when neighboring controls improve incidentally.

### 15. Raw PCA coordinates are a poor direct MSE target for the compact code branch
- The unnormalized `wavepca16` target drove `loss_teacher_fine_structure_code_target` into a much larger scale than the rest of the route.
- Whitened coordinates fixed optimization scale, but that alone still did not open the deployable contract.

### 16. Do not compare producer-side oracle numbers across different implicit full5 export slices
- `sample_count=3/2` packet exports can drift onto different target records across runs.
- When a fine-structure branch is being ranked, pin explicit `target_record_ids` and compare on the same fixed slice.

### 17. Do not keep iterating on fine-structure supervision over a producer path that never sees raw local waveform geometry
- The old Stage3 fine-structure source modes all depended on frontend paths whose direct frame input was only coarse `energy + abs_mean` statistics.
- Under that architecture, target normalization, detach-source, and chunk-footprint tweaks all hit the same low-signal ceiling.
- Once a dedicated waveform-frame encoder was added, the deployable code jumped from `~0.005` to `~0.545` on the same fixed-slice oracle.

### 18. Do not compare a whitened deployable code against a raw PCA upper bound and call the gap purely "signal quality"
- `574` showed that Stage5 is sensitive to code distribution semantics.
- Whitening the analysis-only `wavepca16` upper bound changed both held-out loss and speech-emergence metrics materially.
- Future deployable-vs-upper-bound comparisons should cite whether the upper bound is raw or whitened.

### 19. Do not mistake a partially improved bounded Stage5 route for proof that producer fidelity is already good enough
- In `574`, the deployable geometry-code route and the whitened upper bound both differed from the raw upper bound, but packet-level fidelity to the whitened target still stayed weak.
- The producer-side code remained too flat in variance and frame dynamics, and its record-specific margin was still negative.
- If bounded Stage5 is being ranked before these producer-side fidelity checks are read, the diagnosis can drift back toward the wrong abstraction layer.

### 20. Do not let `build-streaming-student-stage5-dataset-packages` choose the train slice implicitly when a matched train/validation comparison is required
- A recent run accidentally built only `3` train packages because `target_record_ids` were omitted and the builder fell back to its default sampling behavior.
- That produced a misleading `3 train + 5 validation` dataset while the intended comparison slice was `8 train + 5 validation`.
- For any matched Stage5 comparison, pin explicit train record ids before package build and treat the merged offline index as a checked artifact, not an assumed one.

### 21. Do not read improved producer fidelity traits as proof that the current Stage5 objective will automatically reward them
- In `575`, better code variance, frame dynamics, template behavior, and record margin improved the fixed-slice deployable oracle.
- But the corrected bounded Stage5 run still did not improve held-out loss and became louder and brighter.
- Upstream structural progress and downstream optimization compatibility must still be checked separately.

### 22. Do not read lower bounded Stage5 loss alone as proof that the useful fine-structure signal survived
- In `576`, the temporal-conv producer route beat all earlier deployable geometry-code runs on held-out Stage5 loss and even beat the old no-code baseline.
- But speech-emergence also showed a large slide back toward a smoother no-code-like regime on frame-template and adjacent-frame structure gaps.
- When a new upstream contract lowers Stage5 loss, always check whether the route kept the intended geometry-heavy behavior or merely found an easier smoother basin.

### 23. Do not assume a chunk-level target will help if the exported contract is still a framewise code head
- `577` showed that swapping the supervision target from framewise PCA to chunk-level PCA behind the same framewise `16D` export head made the deployable oracle worse, not better.
- If the design question is really about chunk-aware geometry, the exported contract likely has to become chunk-aware too.
- Do not keep iterating on chunk-target distillation while the deployable code shape itself still forces a framewise bottleneck.

### 24. Do not assume that a stronger deployable source-scaffold oracle will automatically survive the current Stage5 consumer/objective
- `578` showed that widening the deployable contract to a short-temporal export improved the fixed-slice deployable oracle from `~0.619` to `~0.691`.
- But the same widened contract made bounded `train8 + validation5` Stage5 much worse and pulled decode metrics back toward the older bright geometry-heavy basin.
- Read contract-shape oracle gain and bounded Stage5 survival as separate gates.

### 25. Do not spend the next round on another flat window repack of the same compact code
- `578` also tried a `center + neighbor_deltas` rewrite after the plain short-temporal stack.
- Oracle stayed roughly the same, but bounded Stage5 still failed.
- The next discriminative move is a structured contract/consumer interface, not a third flat concat variant.

### 26. Do not assume that simple branchwise routing is already a sufficient structured interface for the stronger contract
- `579` split the widened contract into `center_code -> periodic branch` and `neighbor_delta_code -> noise branch`.
- The split preserved the widened oracle level and slightly improved held-out loss versus flat short-temporal concat.
- But it still stayed far behind `576`, and activity/RMS alignment collapsed badly.
- The next interface branch needs an explicit adaptor/gate or temporal fusion block, not just a static reassignment of features to existing branches.

### 27. Do not read widened-contract failure under flat concat or static routing as proof that Stage5 cannot use the stronger contract at all
- `580` kept the same `center + neighbor_delta` package features as `579`, but moved them behind a dedicated branch semantic adaptor/gate.
- That alone recovered bounded Stage5 from `0.544851` to `0.417454` and brought speech-emergence back to the calm `576` basin.
- When stronger contracts fail under naive wiring, test an explicit interface layer before blaming the contract family itself.

### 28. Do not confuse recovered bounded loss with proof that the widened geometry is already being used strongly
- In `580`, the explicit adaptor/gate fixed the widened-contract collapse.
- But the learned full-train gate stayed conservative at roughly `periodic_gate≈0.134` and `noise_gate≈0.099`, with residual deltas much smaller than the base hidden scale.
- A route can recover bounded Stage5 by learning to softly absorb the stronger contract, not necessarily by unlocking a new geometry-heavy regime.

### 29. Do not assume adaptor-only additive finetuning is enough to reveal the value of the stronger contract
- `580` also tried freezing the old Stage5 scaffold and training only the new semantic adaptor modules.
- That raised adaptor gate and delta magnitude sharply, but degraded held-out validation to `0.511409`.
- The current widened-contract interface still needs coordinated co-adaptation with part of the old Stage5 path; "just bolt on a residual sidecar" is not yet sufficient.

## Current Maintenance Rules
- If this file grows too much again, archive a new snapshot instead of turning it back into a long historical log.
- Prefer keeping only the pitfalls that still affect the next concrete decision.

## Active Reference Reports
- `docs/566_stage5_richercontract_listening_result_self_audit_and_next_direction_report.md`
- `docs/567_stage3_fine_structure_reference_oracle_gate_report.md`
- `docs/568_stage5_fine_structure_code_oracle_and_wavepca16_bootstrap_report.md`
- `docs/569_stage5_wavepca16_upper_bound_bounded_training_and_regularizer_report.md`
- `docs/570_active_docs_archive_and_next_plan_refresh_report.md`
- `docs/571_stage3_fine_structure_code_source_mode_sweep_report.md`
- `docs/572_stage3_wavepca_target_supervision_probe_report.md`
- `docs/573_stage3_fixedslice_supervision_normalization_and_waveframeencoder_breakthrough_report.md`
- `docs/574_stage5_waveframeencoder_bounded_integration_and_normalized_upper_bound_report.md`
- `docs/575_stage3_waveframeencoder_fidelity_losses_and_bounded_stage5_tradeoff_report.md`
- `docs/576_waveframeencoder_temporalconv_contract_probe_and_bounded_stage5_report.md`
- `docs/577_waveframeencoder_chunk_target_temporalconv_negative_probe_report.md`
- `docs/578_stage5_short_temporal_contract_shape_probe_report.md`
- `docs/579_stage5_center_delta_split_consumer_probe_report.md`
- `docs/580_stage5_center_delta_adapter_semantic_gate_probe_report.md`
