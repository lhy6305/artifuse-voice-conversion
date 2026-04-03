# Project Overview and Execution Plan

## Document Role
- This file keeps only the current goal, active route judgment, takeover state, and next steps.
- Detailed per-round history belongs in numbered reports and archive snapshots.
- Current archive snapshots:
  - `docs/archive/01_project_overview_and_plan_snapshot_20260326.md`
  - `docs/archive/01_project_overview_and_plan_snapshot_20260328.md`
  - `docs/archive/01_project_overview_and_plan_snapshot_20260401.md`

## Project Goal Summary
- The project goal remains an industrial voice-conversion system that balances offline quality and online latency.
- The intended interpretable control chain is still:
  - `z_art`
  - `e_evt`
  - `F0 / vuv / aper / E`
  - tightly constrained `r_res`
- The current near-term success condition is narrower:
  - prove that the handoff can preserve record-specific fine speech structure, not only coarse activity or timbre-like texture

## Current Repository Layout
- `initial_design.md`: primary design document
- `initial_design_judg.md`: risk review
- `manage.py`: unified command entry
- `python.exe`: fixed project interpreter
- `src/v5vc/`: main source tree
- `configs/`: configuration files and templates
- `reports/`: training, evaluation, and export artifacts
- `docs/`: active docs and numbered reports
- `docs/archive/`: archived snapshots from older stages

## Current Stage Assessment
- The old default idea of repeatedly polishing the existing Stage5 local route is no longer justified.
- Multiple Stage5-local fixes changed buzz texture, harshness, or intermittency, but listening review still did not reveal speech structure.
- Oracle evidence now supports a stronger upstream diagnosis:
  - dense magnitude-style sidecars remain low-signal
  - direct local waveform geometry is sufficient by oracle
  - compact waveform-geometry codes such as `waveform_pca_code_dim_8/16/32` also open the oracle gate
- The first deployable producer-side waveform-code branch now exists end to end, but the first source-mode sweep is still negative:
  - `student_hidden_v1`, `shared_hidden_v1`, and `control_hidden_v1` all train and export correctly
  - none materially beat the old `selected_dynamic_controls` baseline on the full5 cross-record oracle
  - `control_hidden_v1` is only a slight relative improvement, not a gate-opening result
- Same-slice normalization closed a recent ambiguity:
  - hidden-source `wavepca16` supervision variants looked different across runs partly because the implicit full5 export slice drifted
  - once normalized onto the same five records, whitened per-frame target, detached-source head, and chunk-level target all stayed near the same weak `~0.005` deployable-code regime
- A more structural upstream redesign then changed the result materially:
  - the old fine-structure source modes all depended on frontend paths whose direct frame input was only coarse `energy + abs_mean` statistics
  - adding a dedicated `waveform_frame_encoder_v1` branch let the producer-side compact code read unit-RMS waveform frames directly
  - that new deployable code jumped to `predicted_fine_structure_code_family = 0.545295 / 0.547317` on the same fixed-slice oracle
- The current upper-bound result is therefore:
  - Stage5 can use the right fine-structure signal class
  - a deployable upstream code can now materially preserve that signal class when it is allowed to read raw local waveform geometry
- The main uncertainty has moved:
  - no longer "can a deployable upstream code carry useful fine geometry at all"
  - now "how much of the new geometry code survives bounded Stage5 integration relative to the analysis-only upper bound"
- The first bounded `train8 + validation5` Stage5 comparison from `574` sharpened that uncertainty further:
  - the deployable `waveform_geometry_code` route does not yet beat the no-code baseline on held-out Stage5 loss
  - a raw `wavepca16` upper bound was partially confounded by code-distribution mismatch
  - a whitened `wavepca16` upper bound closes part of that gap, which proves Stage5 is sensitive to code distribution semantics
  - but packet-level fidelity to the whitened target is still weak, so the main blocker remains producer-side code quality rather than a pure Stage5 scale mismatch
- The next producer-side push from `575` refined that diagnosis:
  - explicit fidelity losses improved code variance, frame dynamics, template collapse, and own-vs-other record margin
  - the fixed-slice deployable oracle improved materially from `~0.545` to `~0.619`
  - but the corrected bounded `train8 + validation5` Stage5 result still did not improve on held-out loss
  - this means upstream producer changes are not a dead end, but the next move should be structural contract work rather than another small loss rebalance
- The temporal-conv contract probe from `576` sharpened the picture again:
  - adding short temporal context on top of the waveform-frame encoder kept improving producer-side variance, dynamics, and record margin
  - fixed-slice deployable oracle stayed nearly flat around `~0.619`
  - but bounded `train8 + validation5` Stage5 loss improved strongly to `0.417480`, which is now better than both the old deployable geometry-code route and the old no-code baseline
  - speech-emergence then revealed the catch: the route became much calmer and less bright, but also much closer to the smoother no-code basin on frame-template and adjacent-frame structure metrics
- The first direct chunk-target follow-up from `577` now closes another branch:
  - keeping the `waveform_frame_encoder_v1 + temporal_conv_v1` producer but swapping in a chunk-level PCA target does not help
  - short-loop validation becomes slightly worse
  - fixed-slice deployable oracle drops materially from `~0.619` to `~0.508`
  - this suggests the next contract step should change the exported code shape itself, not only replace the supervision target family behind the same framewise head
- The next contract-shape probe from `578` closes the most direct widened-export branch too:
  - widening the deployable contract to a short-temporal local window really does improve the fixed-slice deployable oracle from `~0.619` to `~0.691`
  - but bounded `train8 + validation5` Stage5 gets materially worse at `0.548187`
  - the widened contract also pulls speech-emergence back toward the older bright geometry-heavy basin rather than preserving the calmer `576` regime
  - a follow-up `center + neighbor_deltas` repack keeps essentially the same oracle strength but still fails bounded Stage5 at `0.558221`
  - this means the next bottleneck is no longer just upstream signal presence; it is now the interface between a stronger short-temporal contract and the current Stage5 consumer/objective
- The first structured consumer-interface follow-up from `579` sharpens that again:
  - splitting the widened contract into `center_code` for the periodic branch and `neighbor_delta_code` for the noise branch is stable and preserves the widened oracle level
  - bounded Stage5 improves only marginally to `0.544851`
  - speech-emergence softens a little relative to flat short-temporal concat, but activity/RMS alignment collapses badly
  - so simple branchwise routing is still not enough; the next interface likely needs an explicit adaptor/gate or temporal fusion module
- The next interface branch from `580` now resolves that bottleneck more cleanly:
  - keeping the exact same `center + neighbor_delta` contract but moving the semantic sidecar behind a dedicated Stage5 branch adaptor/gate recovers bounded Stage5 strongly
  - matched `train8 + validation5` held-out loss improves from `579`'s `0.544851` to `0.417454`
  - this essentially ties the old calm `576` route at `0.417480` while avoiding the widened-contract collapse from `578/579`
  - speech-emergence also returns almost exactly to the `576` calm basin rather than the bright widened-contract basin
  - but the new gate probe shows why this is not yet a full success:
    - full-train adaptor usage stays conservative at roughly `periodic_gate≈0.134`, `noise_gate≈0.099`
    - an adaptor-only freeze control overuses the semantic path and degrades badly to `0.511409`
  - the current reading is therefore:
    - explicit adaptor/gate is necessary to make the stronger short-temporal contract survivable
    - but the present adaptor mostly stabilizes by conservative injection, not by clearly unlocking a new speech-structural regime beyond `576`

## Active Main Line

### Line A: Upstream waveform-geometry contract redesign
- Active objective:
  - turn the new `waveform_frame_encoder_v1` producer-side code into the default deployable upstream fine-structure contract
- Current judgment:
  - this is the highest-value route
  - the oracle gate is now materially open on the new waveform-frame-encoder branch
  - the next bottleneck is specifically producer-side code fidelity in the whitened code space
  - the most recent fidelity-loss round improved that bottleneck partially, but not enough to survive bounded Stage5 cleanly
  - short temporal context on the producer contract now appears to help bounded Stage5 survive, but not yet in the fully intended fine-structure-preserving way
  - chunk-level target distillation behind the same framewise export head has now been tested and rejected as a next-step direction
  - naive widened short-temporal exports have now also been tested and rejected as a direct next-step direction
  - a first structured center-vs-delta split consumer has now also been tested and is still insufficient
  - an explicit Stage5 semantic adaptor/gate is now the first interface branch that rescues the stronger contract on bounded Stage5
  - however, current adaptor behavior is still conservative enough that the route remains effectively tied to the calmer `576` basin rather than clearly exploiting extra widened geometry
- Required acceptance pattern:
  - the new code must now survive bounded Stage5 integration better than the old no-code baseline
  - compare it against the analysis-only `waveform_pca_code` upper bound before escalating to listening review

### Line B: Keep the current Stage5 upper-bound route only as a reference consumer
- `streaming_student_waveform_pca_code_v1` is currently an analysis-only upper bound, not a deployable solution.
- Its value is:
  - proving signal sufficiency
  - giving a bounded consumer target
  - providing a comparison anchor for future producer-side codes
- There are now two useful reference forms:
  - raw `wavepca16`
  - whitened `wavepca16`
- For future bounded comparisons, the whitened upper bound should be the default first reference because it matches producer-side supervision semantics better.
- Do not spend the next round on another broad Stage5-local regularizer search.

## Current Maintenance Rules
- Keep `docs/01` and `docs/02` compressed.
- Put long historical context into `docs/archive/` snapshots and numbered reports.
- When the active docs start accumulating report-by-report journaling again, archive first and then rewrite them back into takeover form.

## Current Recommended Next Steps
- The next implementation plan is:
  1. stop expanding hidden-source fine-structure sweeps over `shared_hidden_v1`, `control_hidden_v1`, and `student_hidden_v1`
  2. treat the fixed-slice oracle protocol from `573` as the comparison standard whenever producer-side fine-structure branches are compared
  3. make `waveform_frame_encoder_v1` the active producer-side main line for the deployable waveform-geometry code
  4. treat the first bounded Stage5 result from `574` as a failure-to-match-upper-bound checkpoint, not as a reason to reopen old hidden-source sweeps
  5. treat the fidelity-loss result from `575` as proof that producer metrics can move without yet resolving bounded Stage5
  6. treat `576` as proof that producer-side temporal context can materially improve bounded Stage5 optimization even when fixed-slice oracle stays almost flat
  7. do not read that improvement as success by itself, because `576` also showed a slide back toward a smoother no-code-like structure regime
  8. shift the next work from scalar loss tuning toward structured contract-shape and consumer-interface changes on top of the waveform-frame encoder branch
  9. focus that producer work on:
     - code variance
     - frame-to-frame code dynamics
     - record-specific separation margin against wrong-record code targets
     - short local temporal structure in the compact contract itself
     - exported contract shape, not only target-side chunk supervision
     - how Stage5 receives and separates center-vs-local-delta information from a stronger short-temporal contract
  10. after producer fidelity improves, rerun bounded Stage5 comparison against:
     - the same-slice no-geometry baseline
     - the whitened `streaming_student_waveform_pca_code_v1` upper bound
  11. do not spend the next round on a third flat window-repack of the same code
  12. prefer the next branch to be a structured interface experiment:
     - two-timescale code
     - center-vs-delta split consumer
     - or a dedicated short-temporal adaptor/gate inside Stage5 rather than blind concatenation
  13. after `579`, narrow that preference further:
     - simple branchwise center-vs-delta routing is not enough
     - the next concrete branch should add an explicit Stage5 adaptor/gate or temporal fusion block on top of the stronger contract
  14. after `580`, narrow it again:
     - explicit adaptor/gate is now the default interface baseline for stronger short-temporal contracts
     - do not go back to flat concat or static branch routing as the main line
  15. the next discriminative branch should test whether widened geometry can become genuinely useful rather than merely harmless:
     - increase adaptor temporal expressivity or fusion depth
     - or allow limited co-adaptation around the adaptor interface rather than full-stage free drift
     - always compare against both:
       - full-train adaptor baseline from `580`
       - adaptor-only freeze negative control from `580`
  16. treat `580` as proof of interface necessity, not proof that the stronger contract is already fully exploited
- Decision rule for the next experimental phase:
  - if producer-side fidelity to the whitened target improves and bounded Stage5 results then move toward the whitened upper bound, continue on the upstream contract line
  - if producer fidelity improves or deployable oracle improves but bounded Stage5 still stalls, revisit the Stage5 consumer/objective with the normalization confound already removed
  - if both producer fidelity and bounded Stage5 survive but listening still hears the same non-speech basin, reopen downstream architecture and objective redesign as a first-class branch

## Active Reference Reports
- `docs/555_stage5_producer_fine_structure_probe_report.md`
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
