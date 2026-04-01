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
- The current upper-bound result is therefore:
  - Stage5 can use the right fine-structure signal class
  - the current deployable upstream contract does not yet provide that signal class
- This is a strong default hypothesis, not a formal proof that no downstream redesign could ever help.

## Active Main Line

### Line A: Upstream waveform-geometry contract redesign
- Active objective:
  - replace analysis-only target-derived fine-structure fields with a producer-side learnable and deployable waveform-geometry code
- Current judgment:
  - this is the highest-value route
  - it should be validated by oracle before any new large consumer sweep
- Required acceptance pattern:
  - the new code must materially preserve record-specific fine geometry under the same oracle probe family used in `567` and `568`
  - if it cannot beat the old low-signal regime, do not open a new Stage5 integration cycle

### Line B: Keep the current Stage5 upper-bound route only as a reference consumer
- `streaming_student_waveform_pca_code_v1` is currently an analysis-only upper bound, not a deployable solution.
- Its value is:
  - proving signal sufficiency
  - giving a bounded consumer target
  - providing a comparison anchor for future producer-side codes
- Do not spend the next round on another broad Stage5-local regularizer search.

## Current Maintenance Rules
- Keep `docs/01` and `docs/02` compressed.
- Put long historical context into `docs/archive/` snapshots and numbered reports.
- When the active docs start accumulating report-by-report journaling again, archive first and then rewrite them back into takeover form.

## Current Recommended Next Steps
- No new experiment is scheduled in this documentation-maintenance round.
- The next implementation plan is:
  1. formalize the producer-side fine-structure contract target
  2. define the packet field shape, metadata, and export plumbing for a deployable waveform-geometry code
  3. add the corresponding supervision path in Stage3 training code
  4. preserve the existing oracle probe as the first gate for the new code family
  5. only after the contract and plumbing are in place, run bounded smoke and oracle validation
- Decision rule for the next experimental phase:
  - if the learned producer-side code clears the oracle gate, reconnect it to the current stable Stage5 baseline and compare against the analysis-only upper bound
  - if it does not clear the oracle gate, revisit the representation design before touching Stage5 again
  - if it clears oracle but still collapses into the same buzz basin after integration, reopen downstream architecture and objective redesign as a first-class branch

## Active Reference Reports
- `docs/555_stage5_producer_fine_structure_probe_report.md`
- `docs/566_stage5_richercontract_listening_result_self_audit_and_next_direction_report.md`
- `docs/567_stage3_fine_structure_reference_oracle_gate_report.md`
- `docs/568_stage5_fine_structure_code_oracle_and_wavepca16_bootstrap_report.md`
- `docs/569_stage5_wavepca16_upper_bound_bounded_training_and_regularizer_report.md`
- `docs/570_active_docs_archive_and_next_plan_refresh_report.md`
