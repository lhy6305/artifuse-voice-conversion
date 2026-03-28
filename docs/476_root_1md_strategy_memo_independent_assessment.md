# 2026-03-28 Independent assessment of temporary root `1.md` strategy memo

## Scope
- Input memo:
  - repository-root temporary file `1.md`
- This assessment treats `1.md` as a read-only temporary memo, not as an active source of truth.
- The goal is:
  - check which recommendations are still well supported by current evidence
  - identify which parts are overstated, stale, or too broad
  - translate the useful parts into adjusted next-stage execution guidance

## Evidence Base
- Active takeover docs:
  - `docs/01_project_overview_and_plan.md`
  - `docs/02_pitfalls_log.md`
- Strategic and historical context:
  - `docs/281_teacher_first_v2_cprime_reconstruction_assessment_and_handoff.md`
  - `docs/282_teacher_first_v2_core_acoustic_state_and_c3_boundary_design.md`
  - `docs/355_post_buzz_fail_main_scheme_reevaluation_and_v2core_gap_report.md`
- Current Stage3 and handoff evidence:
  - `docs/370_stage3_to_stage5_downstream_handoff_candidates_report.md`
  - `docs/374_stage3_student_control_packet_readiness_gate_report.md`
  - `docs/376_stage3_teacher_eevt_directional_targetstate_bridge_ab_and_readiness_report.md`
  - `docs/389_stage3_student_packet_minimal_stage5_adapter_and_decoded_smoke_fail_report.md`
- Current teacher-first user-line evidence:
  - `docs/354_teacher_first_riskv2_quick_listening_fail_and_inference_tweak_stop_report.md`
- Current Stage5 corrected-manifold evidence:
  - `docs/472_stage5_corrected_manifold_vnc01_maskfix_report.md`
  - `docs/473_stage5_corrected_manifold_vnc01_maskfix_wfta005_report.md`
  - `docs/474_stage5_corrected_manifold_wfta005_novnc_counterfactual_report.md`
  - `docs/475_stage5_corrected_manifold_vnc01_maskfix_wfta003_followup_report.md`
- Repository-health context:
  - `docs/447_repo_health_and_compliance_audit_20260328.md`
  - `docs/448_repo_health_remediation_followup_20260328.md`

## Summary Verdict
- `1.md` is directionally useful.
- Its strongest value is not a new strategy proposal. Its strongest value is:
  - anti-thrash discipline
  - route and governance discipline
  - a correct warning that "pipeline runs" and "decoded exists" are not quality success
- However, `1.md` is too broad in two places:
  - it over-generalizes "stop same-layer tuning" in a way that would wrongly retire the current active `wfta003` corrected-manifold line
  - it re-centers `C-prime / v2-core` in a way that understates the latest concrete blocker, which is still `F0 / vuv / aper / E` handoff readiness rather than an abstract restatement of `e_evt`
- Therefore the memo should be treated as:
  - mostly valid strategic discipline
  - partially stale execution prioritization
  - not a drop-in replacement for the current active docs

## Recommendations From `1.md` That Are Well Supported

### 1. Do not confuse runnable pipeline success with quality success
- This is strongly supported.
- Current evidence already shows:
  - `teacher-first` can export real `decoded.wav`
  - `student_control_packet -> minimal Stage5 adapter` can export real `decoded.wav`
  - both facts still coexist with hard negative quality conclusions
- So `decoded exists` must stay separate from:
  - speech emergence
  - acceptable audio
  - route promotion

### 2. Do not extrapolate current local results into proof of the full design
- This is strongly supported.
- The current repo still operates on:
  - offline MVP constraints
  - no-res baseline constraints
  - partial proxy and bridge contracts
  - incomplete design-state handoff
- Current positive or negative findings remain route-specific, not universal proof of the whole V5.1 design.

### 3. Retire the old default Stage5 downstream recycle loop
- This is strongly supported.
- Current active docs already state that the old `Stage5 no-res downstream` route is no longer worth re-running by inertia.
- The evidence base in `370`, `374`, `376`, and `389` remains consistent with that conclusion.

### 4. Keep machine gate as a negative gate only
- This is strongly supported.
- Current gate usage across packet readiness, buzz rejection, and teacher-first risk review is still asymmetric:
  - good at auto-reject
  - not good enough to auto-promote

### 5. Stop teacher-first inference-only tweak loops as a main repair path
- This is strongly supported.
- `354` already gives the needed hard stop:
  - the improved risk heuristics were useful
  - but the audible result was still pure buzz
- So normalization, gate toggles, affine matching, and override tricks can remain diagnostic tools, not the primary fix path.

### 6. Keep paired Stage3 blocked until a real frame bridge exists
- This is strongly supported.
- Current docs still agree that paired source waveform and target teacher frames are not naturally frame-aligned.

### 7. Keep route and governance discipline explicit
- This is strongly supported.
- The repo already has route selection, checkpoint selection, negative gates, handoff reports, and listening governance.
- `1.md` is correct that new work should keep declaring:
  - route target
  - replacement target
  - stop rule
  - promotion boundary

## Recommendations From `1.md` That Need Narrowing Or Updating

### 1. "Stop same-layer Stage5 micro-tuning" is too broad as written
- This needs narrowing.
- Historical evidence strongly supports retiring many old pure-buzz families.
- But the latest corrected-manifold work in `472` to `475` shows a real difference between:
  - blind tiny sweeps in dead families
  - targeted localization pressure on the current active anchor
- `475` is not speech success, but it is still the strongest current corrected-manifold result:
  - validation loss improved to `1.199898`
  - post-gate auto-reject improved from `14/24` to `12/24`
  - no-gate auto-reject improved from `16/24` to `14/24`
- Therefore the correct rule is:
  - stop blind micro-sweeps in retired pure-buzz families
  - keep materially different localization probes on the current active `wfta003` anchor

### 2. "Make `C-prime / v2-core` the true main line now" is directionally right but operationally stale
- This needs updating, not rejection.
- `281`, `282`, and `355` correctly established `C-prime / v2-core` as the design-aligned contract backlog.
- But later docs changed the live execution picture:
  - `370`, `374`, and `376` moved the active takeover focus to Stage3 generation-side completion plus handoff gating
  - `472` to `475` created a still-live corrected-manifold Stage5 branch
- So `C-prime / v2-core` should remain:
  - a strategic contract-completion direction
- It should not overwrite the current immediate execution entry points:
  - named-control completion
  - handoff readiness gating
  - active `wfta003` localization follow-up

### 3. "`e_evt` is the key missing piece" is no longer the most accurate immediate blocker statement
- This is partially stale.
- Earlier `355` correctly identified the historical event-contract gap.
- But the latest readiness evidence in `374` and `376` is more specific:
  - `e_evt / z_art` can already be treated as relatively ready
  - `F0 / vuv / aper / E` remain the concrete blocker for a new Stage5 handoff
- So the updated priority is:
  - do not abandon `e_evt` contract work
  - but do not describe it as the only or even primary immediate blocker for the current handoff gate

### 4. "If native teacher Stage5 continues, jump back to fusion / objective / output-head" is too coarse
- This is only directionally plausible.
- The latest active Stage5 evidence localizes the next useful move more narrowly:
  - stay in the current `wfta003` basin
  - add a small localization-oriented constraint
  - avoid resuming generic same-family parameter churn
- That is more precise than a broad return to generic fusion or output-head surgery.

## Risks If `1.md` Is Adopted Literally

### 1. Premature retirement of the only still-improving corrected-manifold branch
- If the repo follows the memo literally, the active `wfta003` line could be stopped even though it is the current best Stage5 branch.

### 2. Mis-prioritizing `e_evt` over the actual current handoff blockers
- The repo could spend effort re-stating event semantics while the readiness gate is still failing on `F0 / vuv / aper / E`.

### 3. Overwriting current active docs with a historical strategic slogan
- `C-prime / v2-core` remains useful, but it should not replace the current active takeover picture in `docs/01`.

### 4. Treating route/governance as missing rather than already partially operational
- The better move is enforcement and cleanup, not re-invention.

## Next-Stage Task: Original Vs Adjusted

### Original next-stage task before this assessment
1. Continue Stage3 generation-side completion around `acoustic_directional_targetstate_bridge_v1`.
2. Keep `student_control_packet_v1` behind cheap screen and named-control readiness gate before opening a new Stage5 route.
3. Keep paired Stage3 blocked until a valid frame bridge exists.
4. Keep the corrected-manifold `wfta003` branch as the active Stage5 anchor and test a different localization axis rather than more same-weight shrink.

### Adjusted next-stage task after assessing `1.md`
1. Keep the original Stage3 generation-side and handoff-gate tasks unchanged. `1.md` does not overturn them.
2. Explicitly keep the old default Stage5 downstream recycle loop and teacher-first inference-only repair loop retired.
3. Reframe `C-prime / v2-core` as a strategic contract backlog, not as a reason to cancel the current `wfta003` localization line.
4. When prioritizing named-control work, focus the immediate blocker statement on `F0 / vuv / aper / E`, while keeping `e_evt` work in the contract roadmap.
5. Tighten route discipline:
  - every new probe must declare route, replacement target, success condition, and stop rule
6. Narrow the Stage5 stop rule:
  - no more blind sweeps in retired pure-buzz families
  - yes to small, clearly justified localization probes on the active `wfta003` anchor

## Final Assessment
- `1.md` should be preserved as a useful anti-thrash memo until the user deletes it.
- Its best content is discipline, not literal task ordering.
- The repo should adopt its cautionary logic, but not its broadest execution wording.
- The practical outcome is:
  - keep the current active lines
  - tighten stop rules
  - avoid stale historical route recycling
  - do not prematurely kill the only current Stage5 branch that is still generating non-trivial improvement
