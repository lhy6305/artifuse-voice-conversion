# Context Bootstrap and Collaboration Rules

## Read Order
Whenever a new work session starts, or whenever prior chat context is missing, read these files in order:

1. `docs/00_context_bootstrap.md`
2. `docs/01_project_overview_and_plan.md`
3. `docs/02_pitfalls_log.md`
4. `initial_design.md`
5. `initial_design_judg.md`

## Current Two-Lane Entry Points
- Since `2026-03-21`, default work is split into two lanes:
  - Experiment lane:
    continue Stage5 decode-side branch verification and listening-governance work.
  - End-user lane:
    design and implement the `teacher-first / single-target` minimal runnable loop.
- After reading `00/01/02`, restore lane-specific context from:
  - experiment lane:
    `docs/236_stage5_step72_decode_gate_smooth3_postenv_validation_report.md`
  - end-user lane:
    `docs/237_teacher_first_single_target_terminal_user_line_design.md`
- The current experiment breakpoint is not "run another random probe". It is:
  - `step72__decode_gate_smooth3_postenv` already completed focused human audit.
  - the default decode apply mode was promoted to `post_ola_envelope`.
- The current end-user breakpoint is not "prove that Stage5 validation export can write wav". It is:
  - connect the existing teacher runtime, downstream contract, vocoder scaffold, and trained checkpoint into a real `source audio -> target audio` minimal loop.

## Multi-AI Parallel Collaboration
- If multiple AI sessions need to work in the same workspace (the user will tell you if so, defaults to single-ai), read:
  - `docs/242_multi_ai_parallel_collaboration_assessment_and_registry_report.md`
- Formal session registry path:
  - `reports/collab/ai_work_sessions/`
- Before starting a new parallel session, run:
  - `.\python.exe manage.py register-ai-work-session ...`
- Minimum session declaration:
  - declare the current lane
  - declare write roots
  - declare dependent handoff docs

## Mandatory Rules

### 1. Encoding and Active Documentation Policy
- All code, scripts, and documents must use UTF-8 without BOM on disk.
- All active documents must be written in English ASCII only.
- Archived legacy documents may remain unchanged until they are explicitly migrated.
- Always read text with explicit UTF-8 handling.
- Hidden pitfall:
  - PowerShell text IO reads as GBK when content encoding is omitted.
  - even when UTF-8 is specified, common PowerShell write paths may add a BOM header.
  - for active documents, do not rely on default PowerShell text IO.
  - use `apply_patch` or the repository `.\python.exe` with explicit UTF-8 without BOM behavior.
- If a historical file has mixed encodings, record the issue in `docs/02_pitfalls_log.md` before converting it.

### 2. Python Environment
- Only use the repository root `python.exe`.
- Do not use system Python.
- Default Python command form:
  - `.\python.exe ...`

### 3. Escalated Execution Constraints
- Audio processing, Torch training, native-library execution, long-running inference, and batch feature extraction should use escalated execution when the environment requires it.
- Read-only checks, lightweight text work, and documentation maintenance can run without escalation when allowed.
- If a required command fails because of sandbox restrictions, retry with the correct execution mode instead of trying to bypass the restriction.

### 4. Documentation Maintenance Discipline
- Any meaningful task update must also update on-disk documentation, not only chat output.
- Active documentation must keep covering:
  - project structure
  - overall task outline
  - current progress
  - current-stage acceptance criteria
  - next-stage tasks
  - active pitfalls
- If a document is obsolete, revise it or move it into `docs/archive/`. Do not silently delete it.

### 5. Recovery and Handoff Requirements
- Assume chat history can be lost at any time.
- All important judgments, stage conclusions, and blockers must be written to disk.
- Before moving to a new phase, verify that the current documents are sufficient for another person to take over.

### 6. Directory Structure and Temporary File Management
- Keep the repository structure clean at all times.
- Temporary files must live in clearly marked locations such as `tmp/`, `scratch/`, or `*_tmp.*`.
- After temporary files are used:
  - if they have long-term value, promote them into formal files and update documentation.
  - if they do not, delete them promptly.
- Do not leave one-off outputs, draft scripts, or disposable experiment artifacts mixed into the repository root.
- If a local Git repository is created for side work, its directory and commit boundaries must still stay clear.

### 7. Decision Process
- Final strategy choices belong to the user.
- Before presenting options, complete the necessary data gathering and fact checks.
- When presenting options, state directly:
  - the observed facts
  - the available options
  - the strengths of each option
  - the weaknesses or risks of each option
  - the recommended choice and why
- Do not lock in a tradeoff-heavy option as final before the user confirms it.

### 8. Training Execution Discipline
- Any training run must log clear timing information, including start time, end time, and duration.
- Before any large run, do a smaller validation run to confirm:
  - command correctness
  - data loading
  - log persistence
  - checkpoint writing
  - basic runtime speed
- Do not estimate full-run cost from vague intuition or one partial command timing before the small run works.

### 9. Network Use Discipline
- By default, the workspace is treated as offline except for built-in assistant browsing tools.
- If external network access is required, for example:
  - fetching dependency code
  - downloading pretrained models
  - installing packages
  - downloading data or toolchains
- stop automatic progress first, explain the reason briefly, and give the user the exact command to run.
- Do not silently perform those network actions on the user's behalf.

### 10. Communication Clarity
- Keep technical language precise, but also add plain-language explanation of what is happening.
- Always make the following easy to understand:
  - the current step
  - the discovered problem
  - the point where user judgment is needed
  - why a result matters
- Regardless of which language the user uses, all assistant replies shown directly to the user must be written in Simplified Chinese.
- This rule applies to chat replies and progress updates, not to active on-disk documents.

### 11. Git Ignore and Recoverability Boundary
- The default `.gitignore` goal is not "commit as little as possible".
- The real goal is:
  - do not leak sensitive data
  - do not flood the repo with rebuildable bulk artifacts
  - keep the repository maximally recoverable after accidental loss
- Default keep priority:
  - code, config, standards docs, and stage reports
  - experiment summaries, reviews, and dataset index metadata
  - a small number of high-value checkpoints in formal training directories
- Default ignore priority:
  - raw or derived audio
  - credentials, local executables, and environment caches
  - package-level payloads that can be regenerated from existing code and metadata, such as `reports/runtime/**/packages/**`
- When expanding `.gitignore`, do not use broad extension-only rules without checking whether they would also hide:
  - checkpoints
  - dataset indexes
  - formal summaries and reviews
  - high-value training and evaluation metadata
- If an artifact class is large but high-value, prefer "keep a few critical items, ignore the rebuildable bulk" instead of ignoring the whole class.
- Any `.gitignore` boundary change must also update formal documentation with:
  - why the ignore rule exists
  - which recovery assets are still preserved
  - which ignored assets can be rebuilt from current metadata

### 12. Manual Listening Delivery Contract
- If the next step requires user listening review, do not write only "please listen" or "move to listening stage".
- The on-disk document must also state:
  - the exact command the user should run
  - the bundle directory or manifest path
  - the result output directory
  - the main comparison target for this round
  - the listening focus for this round, such as loudness stability, boundaries, or overall acceptability
- If tooling supports it, provide both:
  - one directly runnable CLI command
  - one corresponding script entry
- Before handing listening work to the user, the assistant should already complete:
  - bundle preparation
  - manifest compatibility check
  - at least one runnable smoke verification
- Do not describe a state as "ready for listening" if the user still has to guess paths, files, or comparison targets.

## Current Standing Assumptions
- `initial_design.md` remains the primary design baseline.
- `initial_design_judg.md` remains the risk and de-romanticization reference that adjusts implementation priority.
- The first priority is not a complete V5.1 end-to-end build.
- The first priority is a testable engineering skeleton and an offline MVP that can validate core assumptions.
- Validation order must stay anchored on the key risks:
  - whether the no-residual backbone can stand on its own
  - whether the streaming frontend can emit stable control primitives
  - whether pseudo-label and confidence mechanisms damage consonants
  - whether the residual branch stays strictly limited to a compensation role

## Current Dataset Understanding
- `data_convert/dataset_firefly_raw/`
  - high-quality extracted target-speaker game audio
  - `.wav` files are audio
  - `.lab` files are same-name text transcripts
  - `.lab` files are UTF-8 without BOM and include punctuation
- `data_convert/dataset_ly65_raw.wav`
  - source-speaker office recording from the user
  - recorded for clarity
  - contains many silence regions
  - may still include a small number of transient noise events

## Documentation State Maintenance Rules
- After each meaningful subtask, update at least:
  - `docs/01_project_overview_and_plan.md`
  - `docs/02_pitfalls_log.md`
- If a new topic-specific document becomes active, register its purpose and entry point inside `docs/01_project_overview_and_plan.md`.
