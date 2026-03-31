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

### 27. Do not overread deterministic pitch-provider smoke metrics as proof that Stage3 F0 is solved
- The new `deterministic_extractor_v1` route is a contract bootstrap and plumbing validation step.
- It intentionally feeds explicit F0 and VUV information derived from the in-repo acoustic-state extraction family.
- Therefore very strong smoke-level F0 agreement is expected and does not by itself prove external-sidecar readiness or final online deployment suitability.
- Use Step A to validate the shared provider contract, then compare RMVPE against the same contract in Step B.

### 28. Do not assume an external specialist model automatically fits the current Stage3 target contract
- Step B confirmed that RMVPE can be wired into the Stage3 provider interface.
- Step B also confirmed that naive direct RMVPE injection can still fail badly on the current packet screen.
- "external expert exists" and "current contract is compatible with that expert output" are different questions.
- Diagnose provider-to-contract mismatch before promoting RMVPE as the new default route.

### 29. Do not keep treating RMVPE mismatch as a simple lag problem after provider-only audit says otherwise
- Provider-only audit now has a deterministic positive control and an RMVPE negative result on the same Stage3 contract.
- Deterministic provider reaches exact teacher agreement, so the audit path and teacher target contract are not the root cause.
- RMVPE remains `ready_like = 0/8` on the validation audit slice even after anchor `{start, center, end}` and lag `[-8, +8]` sweeps.
- Aggregate RMVPE current-contract metrics are still poor:
  - `avg_voiced_log2_mae = 1.608832`
  - `avg_voiced_corr = -0.430655`
  - `avg_vuv_f1 = 0.852326`
- Best-correlation sweeping improves aggregate correlation only to about `-0.13859`, which is still not usable.
- Therefore the next valid diagnostic is contract decomposition:
  - `rmvpe_f0 + deterministic_vuv`
  - voiced-intersection F0 analysis
  - octave and affine probes on voiced intersections
- Do not spend more time on lag-only sweeps or longer training runs with unchanged raw RMVPE injection.

### 30. Do not read negative reference-voiced RMVPE F0 metrics as proof that the jointly voiced F0 is bad
- The enriched RMVPE audit shows a strong gap between full reference-voiced metrics and jointly voiced metrics.
- Aggregate example:
  - full reference-voiced `avg_voiced_corr = -0.430655`
  - jointly voiced `avg_joint_voiced_corr = 0.547401`
  - jointly voiced `avg_joint_voiced_log2_mae = 0.1088`
- Hybrid `rmvpe_f0 + deterministic_vuv` also proves that fixing VUV alone does not automatically clear readiness, but it removes VUV as the only explanation.
- The current evidence says:
  - RMVPE often has usable F0 on frames where it agrees with the teacher that voicing exists
  - the dominant remaining mismatch is voiced-support drift
  - octave shift is not the main failure mode on the audited slice because joint octave probing keeps selecting shift `0`
- Therefore the next valid RMVPE probe is provider-side VUV calibration, not more octave debugging or more F0-loss training.

### 31. Do not keep spending time on threshold and simple binary VUV cleanup once the RMVPE calibration sweep is flat
- The provider-side RMVPE calibration sweep tested:
  - thresholds `0.01, 0.02, 0.03, 0.05, 0.08`
  - postprocess presets `raw, fill1, fill2, min2_fill1, min2_fill2`
- No variant achieved `ready_like > 0`.
- The best swept variant was only a mild tradeoff improvement:
  - `thr0.010_raw`
  - `avg_voiced_corr = -0.422858`
  - `avg_voiced_log2_mae = 1.547794`
- Simple postprocess presets were effectively no-ops on the audited slice.
- This means the current thresholded RMVPE route is not going to be rescued by more small threshold or gap-fill tuning.
- If RMVPE work continues, the next valid escalation requires richer provider information such as confidence-aware or salience-aware voicing, not more binary postprocess tweaks.
- Do not open a new packet-smoke cycle for the current thresholded RMVPE route.

### 32. Do not overread the confidence-aware RMVPE bootstrap as if it already solved the packet gate
- `rmvpe_confidence_v1` is a meaningful structural improvement over the old thresholded RMVPE route:
  - it keeps unthresholded sampled F0
  - it exposes sampled confidence instead of collapsing everything into `f0_hz > 0`
- But the first one-step packet smoke still lands at:
  - `f0_ready_count = 0/3`
  - `auto_reject_count = 3/3`
- Therefore:
  - the confidence-aware branch is worth keeping as a live experiment
  - but it is still not valid to promote it as the new Stage3 F0 solution
- If this branch continues, the next valid test is a short controlled training loop, not more threshold tweaking and not a premature route-opening claim.

### 33. Do not read short-loop loss improvement on `rmvpe_confidence_v1` as packet-gate progress
- The short controlled loop did improve sampled validation loss:
  - step `2`: `4.434691`
  - step `4`: `2.72968`
  - step `6`: `2.861254`
- But packet-aware screening across all six checkpoints still found:
  - `f0_ready_count = 0/3`
  - `auto_reject_count = 3/3`
- The packet-aware selector picked step `3`, while sampled validation preferred step `4`.
- This does not mean the branch is close to opening.
- It means:
  - teacher-loss improvement and packet-facing readiness remain separate objectives
  - the current confidence-aware consumer is still below the `F0` handoff bar
- Do not keep extending the same short-loop pattern by inertia.
- If RMVPE work continues from here, require a richer provider-consumer contract change rather than more copies of the same training loop.

### 34. Do not assume that simply separating RMVPE confidence from hard `VUV` is enough to rescue the current consumer
- The `rmvpe_split_confidence_v1` probe explicitly stopped overloading sampled confidence as `VUV`.
- It kept:
  - unthresholded RMVPE `F0`
  - hard thresholded `VUV`
  - separate sampled confidence as an extra Stage3 input
- This did improve some affine-calibrated `F0` MAE values on sample3.
- But it still produced:
  - `f0_ready_count = 0/3`
  - `auto_reject_count = 3/3`
- Aggregate sample3 tradeoff was:
  - slightly better `avg_f0_calibrated_log2_mae`
  - slightly worse `avg_vuv_reference_mae`
  - no meaningful `F0` correlation rescue
- So the current blocker is not just that confidence and `VUV` were conflated.
- The remaining problem is deeper consumer-side inability to exploit the richer RMVPE contract.
- Do not keep running more consumer-preserving RMVPE probes unless the next step changes:
  - explicit voiced-support modeling
  - confidence-aware or salience-aware correction logic
  - or the `F0` supervision and calibration objective itself

### 35. Do not mistake smaller RMVPE correction magnitude for actual packet-gate rescue
- The gated consumer probe introduced:
  - `provider_confidence_gate_mode = hard_vuv_times_confidence_v1`
- It did what it was supposed to do locally:
  - `loss_log_f0_correction_l1` dropped from `0.099057` to `0.047207`
  - sample packet `log_f0_correction` magnitude also dropped substantially
- But the packet result still stayed at:
  - `f0_ready_count = 0/3`
  - `auto_reject_count = 3/3`
- This means:
  - "correction head too active" was a real sub-issue
  - but it was not the main route-opening blocker
- Do not continue the current RMVPE Stage3 family with more same-style gates, small correction tweaks, or more one-step packet smokes.
- If RMVPE is revisited later, require a larger redesign than the current correction contract.

### 36. Do not keep scalar energy reweighting on the deterministic nof0corr scaffold as if it were already a joint-control solution
- The deterministic explicit-provider nof0corr reference is now strong enough to localize the remaining blocker:
  - best packet checkpoint reaches `f0_ready_count = 3/3`
  - best packet checkpoint reaches `vuv_ready_count = 3/3`
  - best packet checkpoint reaches `aper_ready_count = 2/3`
  - but `energy_ready_count` stays `0/3`
- Energy-focused scalar reweighting does move `ENERGY`, but only with a tradeoff:
  - scratch energy-focus later reaches `energy_ready_count = 2/3`
  - but the same checkpoints drop to `f0_ready_count = 1/3` and `aper_ready_count = 0/3`
- Warm-starting from the packet-best deterministic checkpoint does not rescue this:
  - packet-best warm-start checkpoint already falls to `f0_ready_count = 0/3`
  - later warm-start checkpoints still follow the same pattern of better `ENERGY` with worse `F0 / APER`
- Sampled validation also improves during warm-start, so this is not a case where bad teacher loss simply hid the answer.
- The real lesson is:
  - the current scalar objective family can trade controls against each other
  - but it cannot protect the already-open `F0 / VUV / APER` state while improving `ENERGY`
- Do not continue more same-family scalar scans or short warm-start retries by inertia.
- The next valid move requires a structural optimization change such as:
  - energy-isolated optimization
  - stagewise freeze
  - or another objective split that preserves already-open controls

### 37. Do not overread strict stagewise freeze as if preserving `F0 / VUV / APER` automatically means `ENERGY` will now improve
- The new energy-freeze probe explicitly trained only:
  - `frontend.energy_head`
  - `student.energy_branch_delta_head`
- It did remove the earlier forgetting failure:
  - all screened checkpoints stayed at `f0_ready_count = 3/3`
  - all screened checkpoints stayed at `vuv_ready_count = 3/3`
  - all screened checkpoints stayed at `aper_ready_count = 2/3`
- But `ENERGY` still did not move:
  - all screened checkpoints stayed at `energy_ready_count = 0/3`
- The old absolute packet MAE from that probe is numerically superseded by the later packet-calibration bugfix.
- So the remaining blocker is not only shared-update interference.
- It is also that the current isolated energy-only heads are too weak to change packet-facing `ENERGY` on their own.
- Do not keep repeating the same two-head freeze loop by inertia.
- The next valid escalation requires new isolated energy-specific capacity, not just stronger patience with the current isolated heads.

### 38. Do not overread isolated `ENERGY` metric improvement as if the named-control route is now open
- The dedicated energy-adapter line is still structurally better than the old two-head freeze because it improves packet-facing `ENERGY` while preserving:
  - `f0_ready_count = 3/3`
  - `vuv_ready_count = 3/3`
  - `aper_ready_count = 2/3`
- But the packet-calibration bugfix changed the absolute scale of the story:
  - the active corrected deterministic isolated-energy frontier is around `0.243` to `0.247`, not the older `0.550` narrative
- Later corrected continuations changed the route-opening outcome materially:
  - `cont12` reaches `energy_ready_count = 1/3`
  - `cont20` reaches `energy_ready_count = 2/3`
  - `cont20` also reaches `all_core_controls_ready_count = 2/3`
- So the correct reading is:
  - the isolated branch direction is real
  - the absolute progress is much better than previously believed
  - the route is now partially open, but not fully open
- Do not turn "partial opening" into a full route-opening claim.
- If this line continues, the next valid move is stronger isolated `ENERGY` capacity or energy-specific objective routing, not celebratory route-opening language.

### 39. Do not assume that supervising `ENERGY` on the packet-gate normalization scale is enough by itself
- The new `teacher_energy_stage5_state` loss directly aligns Stage3 `ENERGY` supervision with the packet gate's `stage5_norm` scale.
- This wiring is valid and low-risk.
- But this family is now numerically superseded by the corrected later calibration-aware branch.
- Readiness stayed unchanged:
  - `energy_ready_count = 0/3`
  - `all_core_controls_ready_count = 0/3`
- So the current bottleneck is not just a mismatch between training scale and gate scale.
- Do not spend more cycles on same-family `ENERGY` weight nudging framed as "better scale alignment".
- If this line continues, the next valid move is stronger isolated capacity or a more direct packet-facing energy objective than the current per-frame MSE family.

### 40. Do not treat naive widening of the isolated energy branch as the default next escalation
- The widened dedicated energy-branch probe kept the deterministic nof0corr scaffold and doubled:
  - `energy_control_branch_hidden_dim` from `96` to `192`
- It preserved:
  - `f0_ready_count = 3/3`
  - `vuv_ready_count = 3/3`
  - `aper_ready_count = 2/3`
- But it did not improve packet-facing `ENERGY`:
  - this family remains worse than the corrected later dynamic-range and affine-calibrated families
- The widened family also shows an unstable short-loop pattern:
  - early step retains partial improvement
  - later steps regress materially
- So "more width" is not a good default continuation on this line.
- If this line continues, prefer more structured isolated capacity or more direct packet-facing objectives instead of naive width scaling.

### 41. Do not assume generic Stage5 temporal and correlation shaping will fix packet-facing energy collapse
- The new Stage5-shape probe added:
  - `teacher_energy_stage5_temporal`
  - `teacher_energy_stage5_correlation`
- These losses were active and the short warm-start loop was healthy:
  - training loss fell across steps `1` to `4`
  - sampled validation still chose a real checkpoint
- But packet-facing `ENERGY` still did not become the active winning branch even after the later packet-calibration bugfix reevaluation.
- It remains clearly weaker than the corrected later dynamic-range and affine-calibrated families.
- So the current blocker is not solved by generic trajectory pressure on normalized energy.
- If this line continues, the next valid move should target the observed failure mode more directly:
  - centered energy shape
  - dynamic-range or variance matching
  - or a more calibration-aware packet-facing objective

### 42. Do not mistake the first small dynamic-range win for actual energy readiness
- The direct dynamic-range probe added:
  - `teacher_energy_stage5_centered_state`
  - `teacher_energy_stage5_std`
- After the packet-calibration bugfix reevaluation, this branch still remains a real positive direction:
  - corrected energy-best `avg_energy_stage5_norm_calibrated_reference_mae = 0.246440`
- But the route is still not open:
  - `energy_ready_count = 0/3`
  - `all_core_controls_ready_count = 0/3`
- So this result should be read as:
  - the direct dynamic-range family is more promising than generic shape losses
  - but it is still below the packet gate and not a readiness milestone
- If this line continues, keep pushing more explicit dynamic-range or calibration-aware objectives rather than declaring victory or falling back to the old generic losses.

### 43. Do not let packet-selector top-1 rank hide the real winner inside the deterministic energy family
- The packet-calibration and zero-mae gate bugfixes make this pitfall more important, not less.
- In the current corrected affine-calibrated continuation family:
  - packet selector top-1 at `cont20` is step `2` with `avg_energy_stage5_norm_calibrated_reference_mae = 0.143957`
  - raw energy-best at `cont20` is step `3` with `avg_energy_stage5_norm_calibrated_reference_mae = 0.120149`
- But the packet-aware selector still ranks a worse checkpoint first because the lexicographic rule prioritizes:
  - readiness counts
  - then `VUV`
  - then `F0`
  - then `APER`
  - only then `ENERGY`
- Therefore, when the active question is specifically deterministic isolated `ENERGY`, do not quote selector top-1 alone.
- Always read:
  - the ranking
  - the best raw `avg_energy_stage5_norm_calibrated_reference_mae`
  - and whether the energy-best checkpoint is different from the lexicographic top-1

### 44. Do not assume a lower learning rate will automatically stabilize the new affine-calibrated energy family
- After the affine-calibrated probe showed the strongest `ENERGY` result so far, a direct follow-up halved learning rate from `5.0e-4` to `2.5e-4`.
- This did not help:
  - corrected energy-best is only `0.258234`
  - this is still worse than the normal affine-calibrated family corrected energy-best `0.243179`
- So the current next move is not "blindly lower the learning rate and retry".
- The active positive signal is still the calibration-aware objective family itself, not the lr-half variant.

### 45. Do not trust packet affine calibration metrics if clipped `scale` and `bias` are not internally consistent
- The downstream packet calibration path used to:
  - fit affine `scale` and `bias`
  - clamp `scale`
  - keep the old unclipped `bias`
- This is wrong whenever raw `scale` exceeds the clamp range.
- The correct behavior is:
  - clamp `scale`
  - recompute `bias` from the clipped `scale`
- A concrete deterministic `ENERGY` proof case changed from:
  - `0.818279`
  - to `0.182918`
- Therefore:
  - old absolute packet-facing deterministic `ENERGY` MAE values in reports `499` to `504` are numerically superseded
  - any future packet affine audit change must verify this calibration invariant first

### 46. Do not read continued affine-calibrated `ENERGY` improvement as a free win once `F0` starts dropping again
- This pitfall is now retired in its previous form.
- The earlier apparent `F0` drop inside affine-calibrated continuation was caused by the zero-mae gate bug:
  - exact `f0_calibrated_log2_mae = 0.0` was treated as falsy and replaced by the fallback failure value
- After the gate fix and selector re-run:
  - `cont4` keeps `F0 = 3/3` on all four checkpoints
  - `cont8` also keeps `F0 = 3/3` on all four checkpoints
  - while `ENERGY` improves monotonically down to `0.224320`
- So do not escalate into joint-control redesign based on the earlier invalid tradeoff reading.
- The current valid reading is:
  - affine-calibrated continuation is still the active deterministic mainline
  - the remaining blocker is the still-closed `ENERGY` gate, not renewed `F0` instability

### 47. Do not use falsy fallback logic on packet-gate metrics where `0.0` is a valid success value
- The Stage3 packet gate used to treat:
  - `f0_calibrated_log2_mae = 0.0`
  - as if the metric were missing
- Root cause:
  - `float(value or fallback)` was used on a metric where exact zero is a meaningful best-case result
- This created a false `F0` regression story inside the affine-calibrated continuation family.
- The safe rule is:
  - only use fallback on `None`
  - never use boolean-falsy fallback on numeric metrics where `0.0` is valid

### 48. Do not let packet-selector top-1 hide a stable continuing energy frontier just because early checkpoints have slightly better secondary metrics
- After both packet-side bugfixes, the affine-calibrated deterministic continuation line is now clearly monotonic on the active sample3 packet slice:
  - warm4 energy-best: `0.243179`
  - cont4 energy-best: `0.232511`
  - cont8 energy-best: `0.224320`
- Later continuation keeps extending the same pattern:
  - cont12 energy-best: `0.216033`
  - cont16 energy-best: `0.201423`
  - cont20 energy-best: `0.120149`
- But the selector top-1 does not simply track the raw energy frontier:
  - cont12 selector top-1 is step `3`
  - cont16 selector top-1 is step `1`
  - cont20 selector top-1 is step `2`
- This happens because the lexicographic rule prioritizes readiness counts and secondary packet metrics before raw `ENERGY`.
- Therefore:
  - selector top-1 is the least-risk packet candidate
  - raw energy-best is the correct frontier indicator for this active deterministic energy line
- Do not misread selector churn or selector conservatism as evidence that the later continuation stopped helping.

### 49. Do not keep describing the pre-dedicated-APER deterministic affine-calibrated line as "fully closed"
- That statement was accurate before `cont12`, but it is no longer accurate after the corrected later continuations.
- At that stage, the correct state on the active sample3 packet slice was:
  - `F0 / VUV / APER / ENERGY = 3/3, 3/3, 2/3, 2/3`
  - `all_core_controls_ready_count = 2/3`
  - `auto_reject_count = 1`
- The route was still not fully open, but the remaining blocker was already localized to one record:
  - `target::chapter3_4_firefly_106`
- At `cont20.step3`, that record still misses both thresholds:
  - `aper_calibrated_reference_mae = 0.401752` vs gate `0.3`
  - `energy_stage5_norm_calibrated_reference_mae = 0.165880` vs gate `0.15`
- Future docs and decisions must describe this as a partial opening with one localized blocker, not as a family that is still uniformly shut.

### 50. Do not assume the raw deterministic `ENERGY` frontier is automatically the right next continuation anchor
- After `cont20`, the raw deterministic `ENERGY` frontier was:
  - `cont20.step3`
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.120149`
- A direct follow-up continuation from that checkpoint produced `cont24`, and it regressed to:
  - `energy_ready_count = 1/3`
  - `all_core_controls_ready_count = 1/3`
  - best `avg_energy_stage5_norm_calibrated_reference_mae = 0.165920`
- The regression happened on both:
  - the remaining hard blocker `target::chapter3_4_firefly_106`
  - and the previously opened second energy-ready record `target::chapter3_3_firefly_138`
- Therefore:
  - raw energy-best is a frontier indicator
  - but it is not automatically the correct next init checkpoint
- If deterministic continuation continues, the continuation rule itself must be reconsidered instead of blindly launching the next block from the raw energy-best checkpoint.

### 51. Do not summarize the pre-dedicated-APER remaining sample3 blocker as if `ENERGY` were the only unresolved control
- After `cont20`, the remaining blocker record is:
  - `target::chapter3_4_firefly_106`
- A blocker-localized packet diagnosis shows that its harder failure is actually `APER`, not `ENERGY`.
- On this record across `cont20.step2`, `cont20.step3`, and `cont24.step1`:
  - raw `aper_prob` std stays around `0.0125`
  - raw APER correlation stays slightly negative at about `-0.093`
  - calibrated APER MAE stays stuck near `0.402`
  - this remains far above the packet gate threshold `0.3`
- `ENERGY` is still unresolved on the same record, but it is qualitatively healthier:
  - raw energy correlation is positive and high
  - calibration substantially reduces MAE
  - `cont20.step3` already brought calibrated energy MAE down to `0.165880`
- Therefore the current blocker hierarchy is:
  - primary: `APER` structural flatness on `target::chapter3_4_firefly_106`
  - secondary: `ENERGY` threshold stability on the same record
- Future docs and continuation plans should not describe the remaining deterministic gap as a generic energy-only problem.

### 52. Do not assume that simply unfreezing the current APER head and APER correction head is enough to fix the blocker record
- A blocker-oriented deterministic probe was run from `cont20.step2` with:
  - `frontend.aper_head` unfrozen
  - `student.aper_branch_delta_head` unfrozen
  - nonzero `teacher_aper_state` supervision
  - the existing dedicated `ENERGY` branch kept active
- This probe preserved the current `2/3` route opening and even improved the raw deterministic `ENERGY` frontier to `0.114704`.
- But on the blocker record `target::chapter3_4_firefly_106`, APER still stayed structurally bad:
  - calibrated APER MAE worsened slightly from `0.401752` to `0.403249`
  - raw APER remained nearly flat
  - raw APER correlation remained effectively unusable
- Therefore the current APER failure is not explained only by the old energy-only freeze policy.
- If deterministic work continues, the next APER step must be more explicit than simply unfreezing the existing APER path.

### 53. Do not keep describing `target::chapter3_4_firefly_106` as an APER blocker after the dedicated APER branch landed
- That statement was accurate for:
  - `cont20`
  - `cont24`
  - and the minimal APER-unfreeze probe
- It is no longer accurate on the active dedicated-APER scaffold.
- With `aper_control_branch_mode = dedicated_aper_branch_v1`:
  - `APER` opens to `3/3` on sample3
  - the global deterministic state becomes `F0 / VUV / APER / ENERGY = 3/3, 3/3, 3/3, 2/3`
  - blocker-record `APER` falls to `0.232967`, below the `0.3` gate
- Therefore the old APER-flatness blocker story is now superseded on the active line.
- Future docs should describe the remaining blocker as:
  - `ENERGY` only
  - localized to `target::chapter3_4_firefly_106`

### 54. Do not keep blindly continuing from a near-threshold combined checkpoint just because it is the raw energy frontier
- After the dedicated APER plus dedicated ENERGY warm4 probe:
  - packet-facing top-1 is step `2`
  - raw deterministic `ENERGY` frontier is step `3`
  - blocker-record `ENERGY` reaches `0.150639`, missing the `0.15` gate by only `0.000639`
- That looks like a natural continuation anchor, but a direct continuation from this near-threshold combined state does not stably improve it.
- The follow-up `cont8` shows:
  - step `1`: `energy_ready_count = 1/3`
  - step `2`: `energy_ready_count = 1/3`
  - step `3`: `energy_ready_count = 1/3`
  - step `4`: `energy_ready_count = 2/3`
- So the continuation mostly regresses the line before partially recovering.
- Therefore:
  - raw energy-best remains a frontier indicator
  - but it is not enough to justify inertia-driven continuation
- Future continuation should use blocker-aware early-stop or threshold-aware anchor rules instead of blindly launching the next block from the current raw frontier.

### 55. Do not assume the raw `step3` frontier is the best blocker-aware continuation anchor once APER is frozen
- After APER opened to `3/3`, a dedicated-scaffold `ENERGY`-only continuation probe compared two anchors:
  - raw energy frontier anchor: `ss_detpitch_aperbranch_energy_warm4.step3`
  - packet-facing anchor: `ss_detpitch_aperbranch_energy_warm4.step2`
- The `step3`-anchor continuation recovered only to:
  - blocker-record `ENERGY = 0.173005`
  - and never beat the earlier blocker frontier `0.150639`
- The `step2`-anchor continuation did better, but only at its first micro-step:
  - `ss_detpitch_aperbranch_energyonly_s2_warm4.step1`
  - blocker-record `ENERGY = 0.150089`
  - this still missed the gate `0.15` by only `0.000089`
- Later steps from the same `step2` anchor regressed again.
- Therefore:
  - the better blocker-aware anchor is `step2`
  - but the continuation regime is now micro-step plus early-stop, not warm4 by inertia
- Future docs and experiments should keep these roles separate:
  - packet-facing top-1
  - raw energy frontier
  - blocker-facing micro-frontier

### 56. Do not keep taking extra same-family micro-steps once the blocker-facing micro-frontier is reached
- After the blocker-aware anchor probe, the best blocker-facing micro-frontier became:
  - `ss_detpitch_aperbranch_energyonly_s2_warm4.step1`
  - blocker-record `ENERGY = 0.150089`
- A direct one-step continuation from that micro-frontier was then run:
  - `ss_detpitch_aperenergy_micro1.step1`
- It did not produce a marginal fluctuation.
- It regressed sharply:
  - blocker-record `ENERGY`: `0.150089 -> 0.247955`
  - `energy_ready_count`: `2 -> 1`
  - `all_core_controls_ready_count`: `2 -> 1`
- Therefore the same-family deterministic continuation line has reached a stop condition.
- Future work should not keep sampling more micro-steps from this family.
- The next valid move must be a more explicit blocker-localized `ENERGY` objective redesign.

### 57. Do not confuse the stopped continuation family with the later successful objective-redesign family
- The stopped family is:
  - same scaffold
  - same objective family
  - more continuation from the old micro-frontier
- That line is still a valid no-go and should remain stopped.
- The later successful line is different in the important way:
  - it adds `teacher_energy_stage5_peak_affine_calibrated`
  - and it restarts from the stable packet-facing anchor `ss_detpitch_aperbranch_energy_warm4.step2`
- Under that redesigned objective family, a single step reaches:
  - `energy_ready_count = 3/3`
  - `all_core_controls_ready_count = 3/3`
  - blocker-record `ENERGY = 0.131030`
- Therefore:
  - keep the old continuation-stop lesson
  - but do not let it block the new objective-redesign family

### 58. Do not keep calling the new deterministic winner only a sample3-local success after the broader screens are clean
- After the peak-focused objective redesign landed, the first opening was shown on the original sample3 packet slice.
- That was only the first confirmation level.
- The checkpoint was then re-screened on:
  - `target_validation` with `sample_count = 8`
  - `target_special_eval` with `sample_count = 8`
- Both screens reached:
  - `auto_reject_count = 0`
  - `all_core_controls_ready_count = 8/8`
  - `energy_ready_count = 8/8`
- Therefore the current correct wording is:
  - validation-confirmed deterministic packet-facing reference
- Do not keep describing it as only a local sample3 win unless a later wider evaluation disproves it.

### 59. Do not equate packet-open Stage3 handoff with decoded-ready Stage5 output
- The deterministic winner `ss_detpitch_energypeak_s2_step1.step1` is now clean on the widened packet screens:
  - `target_validation 8/8`
  - `target_special_eval 8/8`
- That does not mean the current Stage5 no-res consumer is ready.
- After adapting those packet exports into synthetic Stage5 dataset packages and decoding them through the existing selected no-res checkpoint, both widened decoded confirmation runs still produced:
  - `auto_reject_count = 8/8`
  - `all_records_auto_reject = true`
- Therefore:
  - Stage3 packet readiness and Stage5 decoded readiness are separate gates
  - the active blocker for this line has moved to the Stage5 consumer, not back to Stage3

### 60. Keep decoded confirmation tooling aligned with the current Stage5 loss contract before reading route conclusions from it
- The first downstream confirmation attempt did not fail because of the new Stage3 checkpoint.
- It failed because `nores_vocoder_audio_export.py` was still calling an older
  `compute_nores_vocoder_losses(...)` signature.
- The export tool had to be updated to pass the now-required optional control targets:
  - `energy_proxy_target`
  - `energy_log_rms_norm_target`
  - `aper_target`
  - `vuv_target`
  - `voiced_proxy_target`
  - `aperiodicity_proxy_target`
- Therefore:
  - when Stage5 target or loss contracts grow, keep downstream export and probe tools in sync before reading experiment meaning from a crash
  - once the tool mismatch is fixed, treat the rerun result as the real route conclusion

### 61. Do not blame the current Stage5 failure on predicted activity gating when `decoded_no_gate` is already fully rejected
- After the current deterministic Stage3 winner was bridged into Stage5 packages, waveform handoff probes were run on:
  - `target_validation tv8`
  - `target_special_eval se8`
- On both slices:
  - `decoded_no_gate = 8/8 auto_reject`
  - `decoded_pre_ola_gate = 8/8 auto_reject`
  - `decoded_post_ola_gate = 8/8 auto_reject`
- The probe diagnosis is explicit:
  - `buzz_before_predicted_activity_gate = true`
  - `predicted_activity_gate_changes_auto_reject_status = false`
- Therefore:
  - the current failure is not primarily created by the export-side predicted activity gate
  - future Stage5 work should not spend its first move on more gate-floor or gate-smoothing tweaks

### 62. Do not treat the residual-shape branch as the current primary culprit when the base-logits path already explains the failure
- The current `tv8` waveform decoder structure probe shows:
  - `waveform_decoder_base_logits_only` is effectively the baseline route
  - `waveform_residual_shape_only` does not reveal a usable alternate speech-like path
- At the same time, the strongest current localization remains:
  - `decoder_hidden -> waveform_decoder_base_logits`
- The probe diagnosis is explicit in two ways:
  - coupling: `decoder_hidden_to_base_logits_is_main_coupling_amplifier`
  - geometry: `decoder_hidden_to_base_logits_is_main_geometry_collapse`
- Therefore:
  - the immediate Stage5 next step should target the base-logits projection path
  - not residual-shape-only hypotheses
  - and not another round of Stage3 control tuning

### 63. Do not mistake hidden-side branch-conditioned decoder adapters for a real Stage5 fix when they only trade brightness against collapse
- Fixed-input AB on the current deterministic Stage3 winner now covers:
  - plain `branchcondadapter`
  - `fusionbranchmeancontrast_branchcond`
- Both still remain blocked on `tv8`:
  - `8/8 auto_reject`
  - same `buzz_present_by_waveform_frames_before_gate` diagnosis
- Plain `branchcondadapter` does improve brightness relative to the baseline:
  - `spectral_centroid_gap_hz` improves from `9375.224609` to `5732.299316`
  - `spectral_high_band_energy_ratio_gap` improves from `0.709875` to `0.56265`
- But it also becomes even more template-collapsed:
  - `decoded_frame_template_cosine_mean` worsens from `0.979666` to `0.996371`
- `fusionbranchmeancontrast_branchcond` is the less-bad hidden-side adapter:
  - `spectral_centroid_gap_hz = 3139.213867`
  - `spectral_high_band_energy_ratio_gap = 0.485989`
  - `decoded_frame_template_cosine_mean = 0.988974`
- Even so, it still does not open the route and its structure probe still says:
  - `decoder_hidden_to_base_logits_is_main_coupling_amplifier`
  - `decoder_hidden_to_base_logits_is_main_geometry_collapse`
- Therefore:
  - hidden-side branch-conditioned decoder adapters are not the current winning Stage5 direction
  - the next valid Stage5 move should target the base-logits or frame-space path more directly

### 64. Do not misread "residual-shape-only is not a standalone route" as evidence that all output-side residual-shape handoff ideas are dead
- The earlier baseline structure probe only showed:
  - `waveform_residual_shape_only` by itself is not a usable speech-like route
- That is not the same claim as:
  - all residual-shape output-side handoff families are useless
- Fixed-input screening on the current deterministic Stage3 winner now shows the opposite:
  - `fusionbranchmeancontrast_residualshape_fullsplit24` reduces decoded auto-reject to:
    - `tv8 = 6/8`
    - `se8 = 6/8`
  - `fusionbranchmeancontrast_residualshape_scale050` improves the current `tv8` screen further to:
    - `tv8 = 5/8`
    - while keeping `se8 = 6/8`
- The route is still not open, but this is the first current fixed-input Stage5 family that materially leaves the old uniform `8/8 auto_reject` basin.
- The handoff diagnosis also changes qualitatively:
  - `primary_localization = needs_more_localization`
  - `buzz_before_predicted_activity_gate = false`
- Therefore:
  - do not go back to hidden-side branch-conditioned decoder adapters by inertia
  - keep the current residual-shape output-side family alive as the best current Stage5 consumer-side candidate

### 65. Once a Stage5 family produces a narrow review-required slice, stop spending listening time on fully auto-rejected outputs first
- The current `fusionbranchmeancontrast_residualshape_scale050` screen now yields:
  - `tv8`: `3` review-required records
  - `se8`: `2` review-required records
- At this point, the highest-value listening set is the review-required slice, not the full decoded export.
- The current prepared bundle lives at:
  - `reports/runtime/stage5_human_review_bundle_streaming_student_energypeak_fusionresshape050_round1_1/stage5_human_review_bundle.json`
- Therefore:
  - do not keep relistening records that are still machine-clear `auto_reject_obvious_buzz`
  - spend listening time first on the non-auto-reject slice that can change the structural decision

### 66. Do not equate Stage5 `review_required` with near-speech once human review and spectrograms say the slice is still all buzz
- The current best fixed-input Stage5 candidate `fusionbranchmeancontrast_residualshape_scale050` improved machine screening to:
  - `tv8 = 5/8 auto_reject`
  - `se8 = 6/8 auto_reject`
- That was useful, but the follow-up human review is now decisive:
  - the current `5` review-required outputs are still all buzz
- Spectrogram review also supports the human conclusion:
  - voiced/unvoiced contrast in decoded high-band ratio is nearly flat or inverted
  - aligned targets show the expected positive unvoiced-high-band lift, decoded outputs do not
- Therefore:
  - `review_required` here means only "not obviously rejected by the current heuristic"
  - it does not mean "close to speech"
  - do not keep narrating this slice as a qualitative breakthrough after the human stop conclusion

### 67. Once a Stage5 failure family is localized by a reusable review probe, stop rebuilding ad-hoc scripts for the same question
- The current `fusionbranchmeancontrast_residualshape_scale050` route now has a reusable CLI:
  - `analyze-stage5-nores-source-filter-review`
- It formalizes the same practical question that was previously answered by one-off spectrogram review:
  - does the current review-required slice still show collapsed voiced/unvoiced separation and non-speech source-filter geometry
- The current formalized result is still negative:
  - `primary_localization = vuv_separation_collapsed`
  - decoded vuv high-band contrast remains near zero while aligned targets remain clearly positive
- Therefore:
  - do not keep creating throwaway scripts for the same residual-shape review slice
  - use the reusable source-filter review CLI first
  - only open a new Stage5 family screen after that probe says the current blocker has materially changed

### 68. Once the review-slice vuv-path probe says `waveform_frames` are already flat, stop starting from post-decode or gate-side explanations
- The current `fusionbranchmeancontrast_residualshape_scale050` review slice now also has a reusable path-level CLI:
  - `analyze-stage5-nores-vuv-path-review`
- The current result is more specific than decoded-only `vuv` collapse:
  - `2/5` records already miss vuv separation at `waveform_decoder_base_logits`
  - the remaining `3/5` keep only tiny positive base-logits gaps and all `5/5` turn non-positive by `waveform_frames`
  - `waveform_residual_shape_delta` is also non-positive on `5/5`
  - `noise_gate_not_dominant_on_unvoiced_frames` appears on `5/5`
- Therefore:
  - do not start the next Stage5 move from post-decode waveform tweaks
  - do not start from predicted-activity gate tweaks
  - do not assume the residual-shape branch is almost rescuing unvoiced structure
  - start from the `waveform_decoder_base_logits -> waveform_frames` vuv-retention problem instead

### 69. Do not mistake decoded-side vuv-gap improvement from generic centered-logit boosts for a real local rescue
- The review-slice counterfactual probe now shows that simple centered-logit unvoiced gain can improve decoded-side `vuv` high-band means while still making `waveform_frames` vuv separation worse.
- Concrete example on the current `5`-record slice:
  - baseline waveform-frames mean `vuv` high-band gap: `-0.003187`
  - `unvoiced_centered_gain200` waveform-frames mean: `-0.009912`
  - yet the same variant lifts decoded mean to `0.022807`
- The cleaner local signal comes from:
  - `residual_unvoiced_gain300`
  - which flips all `5/5` waveform-frames record gaps positive
  - while keeping the aggregate decoded mean positive too
- Therefore:
  - do not promote generic base-logit gain shaping just because decoded-side sidecars look nicer
  - prefer probes that improve the actual localized sink first
  - on the current line, that means explicit unvoiced-focused residual or noise-side interventions

### 70. Do not keep treating the current gate heads as the likely deployable unvoiced carrier once the runtime-gate probe says they are empty
- The runtime-gate residual probe now shows:
  - best runtime gate variant = `baseline`
  - all runtime gate variants remain non-positive at waveform-frames `vuv` gap
  - `noise_dominance_fraction = 0.0` on all `5/5` reviewed records
- Therefore:
  - stop expecting `noise_gate`
  - `noise > periodic`
  - or simple gate-derived masks
  - to rescue the active residual-shape review slice

### 71. Once `noise_hidden` matches the oracle review-slice rescue, stop routing the next structural probe through the gate heads
- The `noise_hidden` residual probe now shows:
  - `noise_hidden_rms_soft_residual_gain500` reaches waveform-frames aggregate `vuv` high-band gap `0.003365`
  - the oracle target-side positive control is `0.003254`
  - the gap is only `-0.000111`
- This means the deployable upstream carrier is already present before the gate heads.
- Therefore:
  - the next structural probe should be explicit `noise_hidden -> residual`
  - not more gate-head tuning
  - and not more generic base-logit gain shaping

### 72. Do not mistake a valid `noise_hidden` carrier for proof that the current residual adapter can already use it
- The new residual-structure probe now tests the next narrower question:
  - can the current residual-shape branch-condition adapter recover the `noise_hidden` leverage through simple feature rerouting
- The answer is no on the current `5`-record review slice:
  - best structural reroute = `residual_branch_noise_hidden_only`
  - waveform-frames aggregate `vuv` high-band gap only improves from `-0.003187` to `-0.002912`
  - this stays far behind:
    - `noise_hidden_rms_soft_residual_gain500 = 0.003365`
    - `target_unvoiced_residual_gain300 = 0.003254`
- Therefore:
  - do not keep opening more variants that only reshuffle the same residual adapter feature tuple
  - do not say "the carrier exists, so the adapter path is basically solved"
  - the next valid move must add a new explicit `noise_hidden -> residual` projection or injection path instead of more gate tweaks or more adapter-input swapping

### 73. Do not mistake a recovered `waveform_frames` gap for a decoded route opening
- The new explicit `noise_hidden -> residual` micro-fit now proves that a real local rescue is possible:
  - `delta_direct_v1` moves waveform-frames aggregate `vuv` high-band gap from `-0.003187` to `0.002642`
- But the same run leaves decoded aggregate `vuv` high-band gap unchanged:
  - baseline decoded mean `-0.001537`
  - `delta_direct_v1` decoded mean `-0.001537`
- The primary localization also changes accordingly:
  - from `waveform_frames_vuv_separation_lost_after_base_logits`
  - to `decoded_waveform_vuv_separation_lost_after_frame_projection`
- Therefore:
  - do not stop at frame-space improvement and call the route solved
  - do not send the next round back to carrier sourcing, gate heads, or residual-adapter input reshuffling
  - the next valid move must target the downstream frame projection or decode path that erases the rescued residual contrast

### 74. Do not replay a new export manifest while still reading `decoded.wav` from the old review bundle
- The first post-`529` replay made this exact mistake:
  - internal activations came from the new `delta_direct_v1` checkpoint
  - but decoded audio still came from the original baseline review-bundle path
- That stale-path mix made the first decoded-side number look much milder than reality:
  - stale replay reading: decoded aggregate `vuv` gap `-0.001537`
  - corrected replay reading: decoded aggregate `vuv` gap `-0.066452`
- Therefore:
  - when replaying a reviewed slice through a new export manifest, always resolve decoded and aligned audio from the active manifest first
  - do not trust review-bundle audio paths as the replay source of truth once a new export has been created

### 75. Do not reopen gate-side debate once corrected replay shows `decoded_no_gate` is already collapsed
- The corrected `delta_direct_v1` decode-projection review now shows:
  - waveform-frames aggregate `vuv` gap `0.002642`
  - `decoded_no_gate = -0.066444`
  - `decoded_pre_ola_gate = -0.066328`
  - `decoded_post_ola_gate = -0.066453`
- This means the route is already broken before predicted activity gating.
- The gate-mode differences are tiny:
  - no-gate vs pre-OLA difference `0.000116`
  - no-gate vs post-OLA difference `0.000009`
- Therefore:
  - do not send the next round back to gate-floor tuning
  - do not spend time debating pre-vs-post gate mode
  - the next valid move must target frame reconstruction or overlap-add geometry itself

### 76. Do not treat the current Hann no-gate reconstruction as a neutral baseline once rectangular overlap averaging is clearly better
- The new frame-reconstruction probe now holds `waveform_frames` fixed and swaps only reconstruction geometry.
- On the corrected `delta_direct_v1` review slice, aggregate `vuv` high-band gaps are:
  - waveform-frames `0.002642`
  - `hann_ola_baseline = -0.066444`
  - `rectangular_ola = 0.017643`
  - `hop_stitch = -0.001695`
  - `flatten_frames = 0.000006`
- `rectangular_ola` is also positive on all `5/5` reviewed records in that replay.
- Therefore:
  - do not keep describing the current Hann no-gate reconstruction as if it were a neutral decode reference
  - do not say "decode-side is broken everywhere equally"
  - the next valid move must isolate windowing and overlap normalization rules, because the current Hann reconstruction contract itself is now the main localized sink

### 77. Do not overread reconstruction counterfactual wins as immediate route opening
- `rectangular_ola` is a strong positive control on the current review slice, but it is still a reconstruction counterfactual.
- It proves leverage on the localized sink.
- It does not yet prove:
  - stable training compatibility
  - wider-slice decoded readiness
  - or human-listening success
- Therefore:
  - use the result to prioritize reconstruction-contract AB work
  - but do not declare the Stage5 route open until the same conclusion survives normal export and route-level confirmation

### 78. Do not assume a small Hann-family normalization tweak will rescue the current decode contract
- The reconstruction-contract AB now tested the obvious nearby Hann-family variants on the corrected `delta_direct_v1` review slice:
  - `hann_window_sum_norm = -0.066444`
  - `hann_overlap_count_norm = -0.049303`
  - `hann_window_square_norm = -0.059694`
  - `sqrt_hann_window_square_norm = -0.027126`
  - `rectangular_overlap_count_norm = 0.017643`
- The best Hann-family neighbor is better than the current contract, but it still stays negative on all `5/5` reviewed records.
- Therefore:
  - do not keep spinning more tiny Hann normalization permutations as if one of them is likely to open the route by itself
  - the next valid move is to promote the rectangular positive control into a bounded real export contract and test it as the actual decoded route

### 79. Do not equate decoded `vuv` rescue under rectangular export with route opening
- The real export-contract AB now shows that `rectangular_overlap_count_norm` preserves the decoded `vuv` rescue when promoted from probe to actual `decoded.wav`:
  - corrected decoded aggregate `vuv` gap `0.017643`
  - source-filter localization no longer says `vuv_separation_collapsed`
- But the same real export still lands at:
  - `auto_reject_count = 5/5`
  - `review_required_count = 0/5`
  - decoded template cosine mean `0.99003`
- Therefore:
  - do not say "rectangular solved Stage5" just because the old `vuv` sink is gone
  - once rectangular export is in place, the next valid move is to localize the remaining buzz or template-collapse basin, not to reopen Hann or gate debates

### 80. Do not blame the remaining rectangular-route failure on reconstruction once waveform-frames are already template-collapsed
- The new waveform-frame template-collapse review now shows that, on the same corrected `delta_direct_v1` review slice:
  - `waveform_frames_template_cosine_mean = 0.992189`
  - `waveform_frames_adjacent_cosine_mean = 0.999529`
  - `waveform_frames_template_cosine_gap_vs_aligned = 0.959170`
- Those values already satisfy the existing obvious-buzz template-collapse pattern before any reconstruction contract is applied.
- At the same time:
  - rectangular export keeps decoded `vuv` gap positive at `0.017643`
  - rectangular decoded template cosine stays near the same frame-level collapse at `0.990030`
  - Hann decoded template cosine is also still highly collapsed at `0.984943`
- Therefore:
  - do not keep framing the remaining blocker as another Hann-vs-rectangular reconstruction mystery
  - do not assume rectangular introduced a new decoded-only collapse
  - the next valid move must target why `waveform_decoder_base_logits -> waveform_frames` already produces a near-template frame sequence even after the local `vuv` rescue

### 81. Do not reopen final-activation speculation once the review-slice handoff recheck says `tanh` is not the main new collapse site
- The active `delta_direct_v1` review-slice handoff recheck now shows:
  - `waveform_frame_logits_template_cosine_mean = 0.993400`
  - `waveform_frames_template_cosine_mean = 0.992189`
  - `logits_to_frames_template_cosine_gap = -0.001211`
  - `waveform_frame_logits_fraction_abs_ge_1 = 0.070934`
  - `waveform_frame_logits_fraction_abs_ge_2 = 0.001039`
  - `waveform_frame_logits_fraction_abs_ge_3 = 0.0`
- The probe diagnosis is therefore:
  - `tanh_is_main_new_collapse_site = false`
  - `logits_show_heavy_saturation_pressure = false`
- The paired structure recheck on the same slice also confirms:
  - `decoder_hidden -> waveform_decoder_base_logits` is still the strongest coupling amplifier
  - `decoder_hidden -> waveform_decoder_base_logits` is still the strongest geometry collapse site
- Therefore:
  - do not send the next round back to final `tanh` saturation debate
  - do not treat residual-shape-only hypotheses as the main remaining blocker
  - the next valid move must target the output-head projection itself

## Pitfall 82: Do not misread a `waveform_decoder`-only microfit as either route opening or output-head disproof
- The bounded `536` review-slice microfit moved some second-order output-head metrics:
  - `waveform_frame_logits_template_cosine_mean = 0.993400 -> 0.992962`
  - `waveform_frames_template_cosine_mean = 0.992189 -> 0.991705`
  - rectangular decoded `vuv` gap `0.017643 -> 0.032176`
- But it did not change the main route conclusion:
  - real rectangular export still stayed `5/5 auto_reject`
  - the strongest geometry collapse still stayed at `decoder_hidden -> waveform_decoder_base_logits`
  - `decoder_to_base_logits_template_distance_drop` even stayed around `-0.68`
- Therefore:
  - do not promote small head-only gains into a route-opening claim
  - do not use this result to abandon output-head localization either
  - the next valid move must widen scope from the last `waveform_decoder` stack to the broader `decoder_hidden -> waveform_decoder_base_logits` interface

## Pitfall 83: Do not misread a pre-head-adapter-only microfit as proof that widening scope already solved the interface
- The bounded `537` review-slice pre-head run did widen scope beyond the last stack:
  - a zero-init adapter was inserted between `decoder_hidden` and `waveform_decoder`
  - only `10` adapter-side parameters were trained
  - local handoff metrics moved slightly:
    - `waveform_frame_logits_template_cosine_mean = 0.993400 -> 0.992947`
    - `waveform_frames_template_cosine_mean = 0.992189 -> 0.991691`
- But it still did not change the route conclusion:
  - real rectangular export stayed `5/5 auto_reject`
  - decoded `vuv` gap reached only `0.019217`, weaker than the earlier head-only `0.032176`
  - the strongest geometry collapse still stayed at `decoder_hidden -> waveform_decoder_base_logits`
  - `decoder_to_base_logits_template_distance_drop` worsened further to `-0.701049`
- Therefore:
  - do not stop at "we already widened scope once"
  - do not treat adapter plumbing alone as the solution
  - the next valid move must be a joint interface edit, not another single-sided replay

## Pitfall 84: Do not misread the first joint-interface win as route opening
- The bounded `538` review-slice joint run is the strongest current bounded interface edit:
  - `decoded_frame_template_cosine_mean` improves to `0.988889`
  - decoded `vuv` gap stays strongly positive at `0.029999`
  - spectral brightness also drops materially relative to the baseline and pre-head-only runs
- But the main route conclusion still does not change:
  - real rectangular export remains `5/5 auto_reject`
  - the strongest geometry collapse still stays at `decoder_hidden -> waveform_decoder_base_logits`
  - `fused_hidden_frame_mean` still barely changes the heard path, so the projector basin is still active
- Therefore:
  - do not promote the first joint-interface win into "Stage5 route opened"
  - do not keep replaying the exact same joint scope by inertia
  - the next valid move must widen one step further upstream into the immediate `decoder_hidden` producer, not backslide into single-sided edits or stay frozen at the same joint boundary

## Pitfall 85: Do not misread a handoff-side near-opening on `539` as proof that the real export route is already solved
- The bounded `539` producer-plus-interface run is the first current checkpoint where the handoff probe decoded routes all escape auto-reject:
  - `decoded_no_gate = 0/5 auto_reject`
  - `decoded_pre_ola_gate = 0/5 auto_reject`
  - `decoded_post_ola_gate = 0/5 auto_reject`
- But the corresponding real rectangular export still does not match that reading:
  - `auto_reject_count = 3/5`
  - `review_required_count = 2/5`
- Therefore:
  - do not promote the handoff-side result into a route-open claim
  - do not immediately open another wider training loop by inertia
  - the next valid move must first localize the renewed handoff-vs-export gap on the improved `539` checkpoint itself

## Pitfall 86: Do not compare handoff decoded routes against real export unless reconstruction contracts are explicitly aligned
- The first `539` handoff readout made this exact mistake:
  - handoff probe reconstructed decoded routes with the old training-side Hann overlap-add helper
  - real export reconstructed decoded audio with `rectangular_overlap_count_norm`
- That mismatch created a false route split:
  - stale handoff `decoded_no_gate = 0/5 auto_reject`
  - real export `decoded.wav = 3/5 auto_reject`
- After `540` fixed the handoff probe to accept `reconstruction_contract_mode` and replayed `539` with `rectangular_overlap_count_norm`, the split disappeared:
  - corrected handoff `decoded_no_gate = 3/5 auto_reject`
  - matching real export exactly on both aggregate and record-level status
- Therefore:
  - do not compare handoff and export route metrics unless the reconstruction contract is explicitly stated on both sides
  - do not treat a handoff-vs-export discrepancy as model behavior until the route materialization semantics are aligned first

## Pitfall 87: Do not treat the corrected `539` remaining-failure split as one homogeneous class or treat `review_required 2/5` as a positive bucket
- After the corrected subset replay in `541`, the remaining `3/5 auto_reject` frontier is now clearly split:
  - hard no-gate template-collapse blockers:
    - `target::chapter3_26_firefly_114`
    - `target::chapter4_7_firefly_105`
  - one gate-sensitive border case:
    - `target::no_text_voice/chapter3_18_firefly_101`
- The gate-sensitive record is not evidence that the whole remaining failure set is gate-dominated:
  - `decoded_no_gate` template cosine is `0.985013`
  - `decoded_pre_ola_gate` template cosine slips to `0.984834`
  - this only matters because the current auto-reject threshold is exactly `0.985`
- The `2/5 review_required` records are also not both good controls:
  - `target::chapter3_30_firefly_132` is the cleaner near-open control
  - `target::no_text_voice/chapter3_21_firefly_108` is still heavily template-collapsed at `0.991612`
  - it only escapes auto-reject because `predicted_activity_to_aligned_frame_rms_corr = 0.347759` stays below the `0.75` envelope-following threshold
- Therefore:
  - do not train or compare against a naive `fail3 vs review2` grouping as if both sides were homogeneous
  - do not reopen a global `vuv` or gate-family detour just because one remaining record is gate-sensitive
  - use the hard pair as the actual blocker set, `chapter3_30_firefly_132` as the better same-frontier control, and keep `chapter3_21_firefly_108` out of the positive-control bucket

## Pitfall 88: Do not promote the first `0/5 auto_reject` full-slice replay into route opening without listening confirmation
- The focused `542` hard-pair template-push microfit is the first bounded review-slice checkpoint that replays onto the full active `5`-record slice at:
  - `0/5 auto_reject`
  - `5/5 review_required`
- This is a real machine-side gain:
  - old `539` full5 frontier was `3/5 auto_reject + 2/5 review_required`
  - full-slice decoded template cosine improves from `0.985812` to `0.968295`
  - source-filter replay also improves materially rather than only sliding under one threshold
- But the gate semantics still do not change:
  - `review_required` is not a positive acceptance state
  - there is still no machine-side label here that means "speech confirmed" or "route opened"
- Therefore:
  - do not write the first `0/5 auto_reject` replay up as solved speech emergence
  - do not immediately broaden the family or celebrate success before bounded listening review
  - treat `542` as a new strongest bounded frontier that has earned human review, not as a completed route-opening claim

## Pitfall 89: Do not confuse lower-harshness buzz plus better energy following with speech emergence
- The manual review after `544` settles the `templatepush_b` frontier:
  - all `5` decoded outputs still remain pure buzz
  - there is slightly more energy-following fluctuation
  - spectrograms still show dominant uniform stripe patterns
  - some short sand-like texture can appear locally
  - but there is still no speech structure and no human-voice-like region
- This means the current gain is real but narrower than it first appears:
  - machine negative-gate escape is real
  - template-collapse severity is lower
  - source-filter sidecars improve
  - but the route still stays inside a buzz basin
- Therefore:
  - do not keep describing the current frontier as near-speech just because it is less harsh
  - do not broaden replay or continue the same template-push family by inertia without a new structural hypothesis
  - frame the next move around missing speech structure, not only around further lowering template-collapse metrics

## Pitfall 90: Do not treat lower within-record template-collapse scalars as proof that record-specific speech structure has emerged
- The post-`544` localization in `545` shows that `templatepush_b` improves several within-record collapse metrics:
  - corrected `539` to `templatepush_b` handoff `waveform_frame_logits_template_cosine_mean = 0.990774 -> 0.971137`
  - corrected `539` to `templatepush_b` handoff `waveform_frames_template_cosine_mean = 0.989148 -> 0.967072`
  - corrected `539` to `templatepush_b` decoded no-gate template cosine `0.985812 -> 0.968295`
- But the same round also shows that decoded resonance structure is still highly shared across different records:
  - mean pairwise decoded peak-set Jaccard rises from `0.707` to `0.773`
  - aligned-target mean stays only `0.116`
  - several decoded record pairs reach identical peak sets at Jaccard `1.0`
- The structure probe also keeps the same dominant bottleneck:
  - `decoder_hidden_to_base_logits_is_main_coupling_amplifier`
  - `decoder_hidden_to_base_logits_is_main_geometry_collapse`
- Therefore:
  - do not read a lower decoded template cosine alone as evidence of speech emergence
  - do not assume that "less collapsed inside each record" means "more record-specific across records"
  - when human review still says pure buzz, check whether decoded resonance peaks are converging onto a shared cross-record template before opening broader replay

## Pitfall 91: Do not assume that globally breaking cross-record sharedness is already the same thing as building speech structure
- The new `546` batch regularizer does directly break the old shared resonance-template basin:
  - full5 decoded peak-set Jaccard mean drops from `0.773` on `templatepush_b` to about `0.50`
  - full5 decoded template cosine also drops sharply to about `0.803`
- But the route still does not improve in the way that matters:
  - real no-gate rectangular export regresses from `0/5 auto_reject` back to `1/5 auto_reject`
  - the regressed record is the current near-open control `target::chapter3_30_firefly_132`
  - the hard blocker pair `target::chapter3_26_firefly_114` and `target::chapter4_7_firefly_105` still keeps identical decoded peak sets at Jaccard `1.0`
- The structure probe also keeps the same dominant bottleneck:
  - `decoder_hidden_to_base_logits_is_main_coupling_amplifier`
  - `decoder_hidden_to_base_logits_is_main_geometry_collapse`
- Therefore:
  - do not promote a global cross-record de-sharing trick into route opening just because cross-record overlap falls
  - do not replace one scalar obsession with another one
  - when a global de-sharing objective hurts the near-open control while leaving the hard blocker pair partly unresolved, the next valid move is narrower pair-specific differentiation pressure, not more of the same global penalty

## Pitfall 92: Do not attribute a new post-frontier basin shift to a new regularizer unless a matched no-regularizer continuation control says it is really new
- `546` was missing exactly this control:
  - the regularizer runs were compared against the original `templatepush_b` frontier
  - but not against a plain same-scope continuation from the same `templatepush_b.step8` anchor
- `547` closes that gap and changes the causal reading:
  - plain continuation alone regresses full5 real export from `0/5 auto_reject` to `1/5 auto_reject`
  - the regressed record is the same near-open control `target::chapter3_30_firefly_132`
  - plain continuation also reproduces the same post-step8 basin shape:
    - `decoded_template_cosine_mean = 0.802061`
    - mean decoded peak-set Jaccard `0.504242`
    - hard-pair `114/105` Jaccard still `1.0`
    - structure still localizes to `decoder_hidden -> waveform_decoder_base_logits`
    - `decoder_to_base_logits_template_distance_drop = -3.679934`
- The regularizer families are only second-order different from that same plain continuation basin:
  - `crossrecordspeca decoded_template_cosine_mean = 0.802901`
  - `hardpairspeca decoded_template_cosine_mean = 0.802036`
  - per-record statuses remain identical across the three post-step8 continuations
- Therefore:
  - do not claim that a newly added loss is what caused a basin shift unless a matched no-op continuation control fails to make the same move
  - do not use a near-threshold unstable frontier as a causal baseline without matched continuation governance
  - for future same-anchor ABs, require the plain continuation control in the same round before writing any mechanism-level conclusion

## Pitfall 93: Do not promote a small single-step de-sharing blip into a new mechanism unless it survives the next matched step
- `548` adds the next missing governance layer after `547`:
  - once plain continuation control is present, the next temptation is to overread the first short-horizon difference
- On the stable pre-drift `templatepush_b` anchor:
  - `step1` of plain continuation and `hardpairspeca` is effectively identical
  - `step2` shows a small focused gain on mean decoded peak-set Jaccard:
    - control `0.628687`
    - focused `0.565253`
  - but export statuses remain identical:
    - both `0/5 auto_reject`
    - both preserve `132`
    - hard-pair `114/105` Jaccard still stays `0.6`
- Most importantly, the apparent focused gain is not durable:
  - by `step3`, mean decoded peak-set Jaccard is again identical at `0.583030`
  - export statuses and per-record metrics are again nearly indistinguishable
- Therefore:
  - do not write up a single-step metric dip as a real new mechanism unless the next matched step still preserves it
  - do not let a transient cross-record overlap change outrank route-level facts like `132` preservation, hard-pair separation, or export status
  - if the only visible advantage disappears one step later, stop calling that family a new main line

## Pitfall 94: Do not continue a blocker-specific family once the remaining difference has been narrowed to a human-audible question but no human review has been done yet
- After `549`, the current focused family is no longer blocked on missing machine-side preparation:
  - the matched `step2 control vs focused` paired bundle now exists
  - it already isolates the only `4` records that matter for the next decision
  - it already includes both audio and spectrogram sidecars for direct A/B review
- At that point, more same-family continuation would be the wrong move:
  - machine-side differences are already too small to settle the question alone
  - the remaining decision is now whether a human can hear or see more record-specific structure on `114/105` without any regression on `132`
- Therefore:
  - once the problem has been narrowed to a bounded human-review question, do not reopen training first
  - do not keep inflating scalar logs when the next real evidence must come from paired listening
  - complete the paired review before deciding whether to retire or continue the family

## Pitfall 95: Do not keep a blocker-specific family alive after paired human review says the matched variants are still the same buzz basin
- `550` resolves the paired `step2` review from `549`:
  - focused `step2` and control `step2` are both still pure buzz
  - both still show only slightly stronger energy-following fluctuation
  - both still show uniform thin-line stripe spectrograms
  - both still show only tiny local sand-like texture
  - neither produces speech structure or any human-voice-like region
- That means the last remaining ambiguity from `548` is gone:
  - the transient `step2` de-sharing signal is not a human-meaningful gain
  - it is not enough to justify another same-family continuation
- Therefore:
  - once matched human review says two variants are the same buzz basin, stop the family
  - do not keep a line alive on tiny transient machine-side differences after human evidence has already collapsed them back together
  - move on only to a materially different mechanism, not another replay of the same objective family

## Pitfall 96: Do not call a new local freedom a breakthrough if the export status stays the same and the old structure bottleneck does not move
- `551` adds a genuinely different local mechanism:
  - a minimal dynamic residual basis head on `waveform_decoder_base_logits`
  - new parameters only
  - clean partial-init training from the old `templatepush_b` frontier
  - slightly better machine-side source-filter aggregates on full5 real export
- That still is not enough to claim the bottleneck is solved:
  - full5 real export remains `0/5 auto_reject + 5/5 review_required`, exactly the same negative-gate status as `templatepush_b`
  - the structure probe still localizes the main bottleneck to `decoder_hidden -> waveform_decoder_base_logits`
  - `decoder_to_base_logits_template_distance_drop` remains strongly negative and even worsens slightly relative to the old frontier
- Therefore:
  - do not confuse "new mechanism trains and nudges machine metrics" with "route-opening evidence"
  - if export status is unchanged and structure localization is unchanged, treat the result as an incremental smoke only
  - require either human-audible improvement or a real structural relocation before promoting the new family to main line

## Pitfall 97: Do not scatter hearing-review evidence across multiple runtime directories once human A/B is the next critical-path decision
- By `551`, the next valid step is explicit human A/B between `templatepushb` and `dynamicheadsmokea`
- Before `552`, the needed assets were split across:
  - audio export directories
  - source-filter review directories
  - an older single-variant listening bundle
  - a separate structure-probe directory
- That makes human review slower and more error-prone:
  - it is too easy to compare mismatched files
  - it is harder to verify that both variants use the same record set and reference targets
  - it raises the cost of repeating the same review pattern on later variants
- Therefore:
  - once human review becomes the next gating decision, collocate all current audio, spectrogram, and json/md sidecars under one root directory
  - keep aligned references and per-variant decoded assets under the same `records/<record_id>/...` tree
  - keep copied manifests in the same root so the review context never depends on chasing the original runtime paths

## Pitfall 98: Do not keep escalating tiny output-head freedoms after repeated human review says every variant is still the same pure-buzz basin
- By `553`, this has happened across multiple local families:
  - template-push improved machine metrics but stayed pure buzz
  - focused de-sharing regularizers changed some machine overlap scalars but stayed pure buzz
  - minimal dynamic output-head freedom also stayed pure buzz and was not even clearly distinguishable from `templatepushb` by listening
- That means the project now has enough evidence to tighten the framing:
  - a local head can still be the visible bottleneck interface
  - but repeated tiny local freedom increases are not yet evidence that the missing ingredient is "just one more head tweak"
- Therefore:
  - stop escalating same-locality output-head ideas by inertia once multiple human reviews collapse them back into the same buzz basin
  - before any new training family, ask whether the hidden representation itself still contains recoverable target-specific speech structure
  - prefer oracle-style sufficiency probes before another round of local projector tuning

## Pitfall 99: Do not misread coarse oracle recoverability as evidence that fine speech structure is still available to a local waveform head
- By `554`, the new oracle probe shows two very different realities at once:
  - RMS, VUV, and compressed log-spectrum are still strongly recoverable from multiple stages
  - cross-record waveform-frame recovery stays near zero even after adding a small nonlinear waveform MLP oracle
- That means:
  - a coarse oracle success only proves that envelope-, activity-, and broad spectral information survived
  - it does not prove that target-specific fine waveform geometry still exists in a form the local head can exploit
- Therefore:
  - do not use strong coarse oracle numbers as a reason to continue local output-head redesign by default
  - once fine waveform oracle metrics remain near zero across both linear and small nonlinear readouts, shift the main localization effort upstream into the producer / fusion representation path


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
- `docs/488_stage3_deterministic_pitch_provider_bootstrap_and_smoke_report.md`
- `docs/489_stage3_rmvpe_provider_bootstrap_and_contract_mismatch_smoke_report.md`
- `docs/490_stage3_provider_only_audit_and_rmvpe_contract_diagnosis_report.md`
- `docs/491_stage3_rmvpe_voiced_intersection_and_hybrid_vuv_diagnosis_report.md`
- `docs/492_stage3_rmvpe_voicing_threshold_and_vuv_postprocess_calibration_report.md`
- `docs/493_stage3_rmvpe_confidence_provider_bootstrap_and_packet_smoke_report.md`
- `docs/494_stage3_rmvpe_confidence_short_loop_and_packet_selector_report.md`
- `docs/495_stage3_rmvpe_split_confidence_probe_report.md`
- `docs/496_stage3_rmvpe_splitconf_gated_correction_probe_report.md`
- `docs/497_stage3_detpitch_nof0corr_energy_tradeoff_and_warmstart_nogo_report.md`
- `docs/498_stage3_detpitch_energyfreeze_isolation_probe_report.md`
- `docs/499_stage3_detpitch_energy_adapter_freeze_probe_report.md`
- `docs/500_stage3_detpitch_energy_stage5_objective_routing_probe_report.md`
- `docs/501_stage3_detpitch_energy_adapter_widening_probe_report.md`
- `docs/502_stage3_detpitch_energy_stage5_shape_objective_probe_report.md`
- `docs/503_stage3_detpitch_energy_stage5_dynamic_range_objective_probe_report.md`
- `docs/504_stage3_detpitch_energy_stage5_affine_calibrated_objective_and_lrhalf_followup_report.md`
- `docs/505_stage3_packet_calibration_bias_recompute_bugfix_and_energy_family_reevaluation_report.md`
- `docs/506_stage3_f0_zero_mae_gate_bugfix_and_affine_energy_cont8_followup_report.md`
- `docs/507_stage3_detpitch_affine_energy_cont12_to_cont20_partial_route_opening_report.md`
- `docs/508_stage3_detpitch_affine_energy_cont24_regression_from_raw_frontier_report.md`
- `docs/509_stage3_blocker_localized_firefly106_aper_flatness_and_energy_secondary_report.md`
- `docs/510_stage3_detpitch_aperenergy_blocker_probe_report.md`
- `docs/511_stage3_detpitch_dedicated_aper_branch_route_opening_report.md`
- `docs/512_stage3_detpitch_dedicated_aper_plus_energy_warm4_and_cont8_report.md`
- `docs/513_stage3_detpitch_energyonly_blocker_aware_anchor_probe_report.md`
- `docs/514_stage3_detpitch_energy_micro1_regression_and_same_family_stop_report.md`
- `docs/515_stage3_detpitch_peak_energy_objective_route_opening_report.md`
- `docs/516_stage3_detpitch_peak_energy_objective_broad_slice_confirmation_report.md`
- `docs/517_stage3_peak_energy_downstream_stage5_nores_confirmation_and_export_plumbing_report.md`
- `docs/518_stage5_consumer_handoff_localization_for_energypeak_stage3_winner_report.md`
- `docs/519_stage5_fixed_input_branch_conditioned_decoder_family_ab_report.md`
- `docs/520_stage5_fixed_input_fusion_residualshape_breakthrough_and_scale_screen_report.md`
- `docs/521_stage5_fusion_residualshape_scale050_human_review_bundle_report.md`
- `docs/522_stage5_fusion_residualshape_scale050_spectrogram_review_and_human_stop_report.md`
- `docs/523_stage5_source_filter_review_cli_formalization_and_vuv_collapse_confirmation_report.md`
- `docs/524_stage5_review_slice_vuv_path_localization_probe_report.md`
- `docs/525_stage5_review_slice_vuv_retention_counterfactual_probe_report.md`
- `docs/526_stage5_review_slice_runtime_gate_vs_oracle_unvoiced_residual_probe_report.md`
- `docs/527_stage5_review_slice_noise_hidden_unvoiced_residual_probe_report.md`
- `docs/528_stage5_review_slice_noise_hidden_residual_structure_probe_report.md`
- `docs/529_stage5_explicit_noise_hidden_residual_microfit_and_downstream_projection_blocker_report.md`
- `docs/530_stage5_decode_projection_review_and_replay_path_bugfix_report.md`
- `docs/531_stage5_frame_reconstruction_geometry_probe_report.md`
- `docs/532_stage5_reconstruction_contract_hann_family_ab_report.md`
- `docs/533_stage5_real_export_contract_ab_report.md`
- `docs/534_stage5_waveform_frame_template_collapse_localization_report.md`
- `docs/535_stage5_reviewslice_deltadirect_output_head_recheck_report.md`
- `docs/536_stage5_reviewslice_outputhead_only_microfit_report.md`
- `docs/537_stage5_reviewslice_prehead_adapter_microfit_report.md`
- `docs/538_stage5_reviewslice_joint_interface_microfit_report.md`
- `docs/539_stage5_reviewslice_producer_interface_microfit_partial_opening_report.md`
- `docs/540_stage5_waveform_handoff_contract_alignment_bugfix_report.md`
- `docs/541_stage5_reviewslice_remaining_failure_subset_localization_report.md`
- `docs/542_stage5_reviewslice_hardpair_templatepush_microfit_report.md`
- `docs/543_stage5_templatepushb_listening_bundle_and_machine_preread_report.md`
- `docs/544_stage5_templatepushb_manual_review_and_human_stop_report.md`
- `docs/545_stage5_templatepushb_crossrecord_resonance_trap_localization_report.md`
- `docs/546_stage5_crossrecord_logspec_regularizer_ab_report.md`
- `docs/547_stage5_templatepushb_continuation_control_vs_crossrecord_regularizer_report.md`
- `docs/548_stage5_short_horizon_hardpair_regularizer_replay_report.md`
- `docs/549_stage5_step2_paired_listening_bundle_preparation_report.md`
- `docs/550_stage5_step2_paired_manual_review_and_focused_regularizer_stop_report.md`
- `docs/551_stage5_dynamic_output_head_smoke_report.md`
- `docs/552_stage5_paired_full5_listening_bundle_colocation_report.md`
- `docs/553_stage5_dynamicheadsmokea_manual_review_and_oracle_probe_plan_report.md`
- `docs/554_stage5_representation_oracle_waveform_sufficiency_report.md`
