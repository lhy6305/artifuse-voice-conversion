# Context Bootstrap and Collaboration Rules

## Read Order
Whenever a new work session starts, or whenever prior chat context is missing, read these files in order:

1. `docs/00_context_bootstrap.md`
2. `docs/01_project_overview_and_plan.md`
3. `docs/02_pitfalls_log.md`
4. `initial_design.md`
5. `initial_design_judg.md`

## Current Entry Point
- The default active line is now:
  - upstream fine-structure representation redesign for the streaming-student to Stage5 handoff
- The latest active reasoning chain is:
  - `docs/566_stage5_richercontract_listening_result_self_audit_and_next_direction_report.md`
  - `docs/567_stage3_fine_structure_reference_oracle_gate_report.md`
  - `docs/568_stage5_fine_structure_code_oracle_and_wavepca16_bootstrap_report.md`
  - `docs/569_stage5_wavepca16_upper_bound_bounded_training_and_regularizer_report.md`
  - `docs/570_active_docs_archive_and_next_plan_refresh_report.md`
- The current breakpoint is not "try another Stage5 local polish run".
- The current breakpoint is:
  - preserve the upper-bound conclusion from `wavepca16`
  - redesign a producer-side deployable waveform-geometry code
  - keep the same oracle gate as the first acceptance check

## Mandatory Rules

### 1. Encoding and Active Documentation Policy
- All code, scripts, and documents must use UTF-8 without BOM on disk.
- All active documents must be written in English ASCII only.
- Archived legacy documents may remain unchanged until they are explicitly migrated.
- Always read text with explicit UTF-8 handling.
- Hidden pitfall:
  - PowerShell text IO can fall back to GBK on read when encoding is omitted.
  - common PowerShell write paths can add a BOM header even when UTF-8 is requested.
  - for active documents, do not rely on default PowerShell text IO.
  - use `apply_patch` or `.\python.exe` with explicit UTF-8 without BOM behavior.

### 2. Python Environment
- Only use the repository root `python.exe`.
- Do not use system Python.
- Default Python command form:
  - `.\python.exe ...`

### 3. Documentation Maintenance Discipline
- Any meaningful task update must also update on-disk documentation, not only chat output.
- Active documentation must stay compressed enough for takeover reading.
- If `00/01/02` start growing again, snapshot them into `docs/archive/` with a date suffix before further expansion.
- Detailed history belongs in numbered reports and archive snapshots, not back in active docs.

### 4. Recovery and Handoff Requirements
- Assume chat history can be lost at any time.
- All important judgments, stage conclusions, and blockers must be written to disk.
- Before moving to a new phase, verify that the current documents are sufficient for another person to take over.

### 5. Directory Structure and Temporary File Management
- Keep the repository structure clean at all times.
- Temporary files must live in clearly marked locations such as `tmp/`, `scratch/`, or `*_tmp.*`.
- If a temporary artifact becomes decision-relevant, promote it into a formal file and update documentation.

### 6. Decision Process
- Final strategy choices belong to the user.
- Before presenting options, complete the necessary data gathering and fact checks.
- When presenting options, state directly:
  - the observed facts
  - the available options
  - the strengths of each option
  - the weaknesses or risks of each option
  - the recommended choice and why

### 7. Training and Experiment Discipline
- Before any large run, do a smaller validation run that confirms:
  - command correctness
  - data loading
  - log persistence
  - checkpoint writing
  - basic runtime speed
- Do not launch new experiments during a documentation-only maintenance task unless the user explicitly changes scope.

### 8. Network Use Discipline
- By default, the workspace is treated as offline except for built-in assistant browsing tools.
- If external network access is required, stop automatic progress first, explain the reason briefly, and give the user the exact command to run.

### 9. Communication Clarity
- Keep technical language precise, but also add plain-language explanation of what is happening.
- All assistant replies shown directly to the user must be written in Simplified Chinese.
- This rule applies to chat replies and progress updates, not to active on-disk documents.

### 10. Manual Listening Delivery Contract
- If the next step requires user listening review, the on-disk document must also state:
  - the exact command the user should run
  - the bundle directory or manifest path
  - the result output directory
  - the main comparison target for this round
  - the listening focus for this round
- Before handing listening work to the user, complete:
  - bundle preparation
  - manifest compatibility check
  - at least one runnable smoke verification

## Current Standing Assumptions
- `initial_design.md` remains the primary design baseline.
- `initial_design_judg.md` remains the risk and de-romanticization reference.
- The immediate goal is still not a full polished end-to-end system.
- The immediate goal is a deployable control chain that can preserve record-specific speech structure under bounded validation.
- The current default research focus is upstream representational sufficiency, not another Stage5-local regularizer sweep.

## Current Dataset Understanding
- `data_convert/dataset_firefly_raw/`
  - target-speaker game audio with same-name `.lab` transcripts
- `data_convert/dataset_ly65_raw.wav`
  - source-speaker office recording with many silence regions

## Documentation State Maintenance Rules
- After each meaningful subtask, update at least:
  - `docs/01_project_overview_and_plan.md`
  - `docs/02_pitfalls_log.md`
- If a new topic-specific document becomes active, register its purpose and entry point inside `docs/01_project_overview_and_plan.md`.
