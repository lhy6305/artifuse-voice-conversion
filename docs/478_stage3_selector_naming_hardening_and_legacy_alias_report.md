# 478 Stage3 selector naming hardening and legacy alias report

## Scope
- Reduce Stage3 checkpoint-selector ambiguity after `477`.
- Keep backward compatibility for older docs and command history.
- Make the validation-first selector explicitly identify itself as a post-hoc teacher-loss selector.

## Code Changes
- Hardened Stage3 post-hoc selector metadata and report wording:
  - `src/v5vc/streaming_student/checkpoint_selection_entry.py`
- Added an explicit CLI alias:
  - `select-streaming-student-posthoc-teacher-loss-checkpoint`
- Kept the older CLI name for compatibility:
  - `select-streaming-student-best-checkpoint`
  - now documented as a legacy name
- Updated parser help text in:
  - `src/v5vc/cli.py`

## Compatibility Policy
- Existing command:
  - `select-streaming-student-best-checkpoint`
  - still works
- New explicit command:
  - `select-streaming-student-posthoc-teacher-loss-checkpoint`
  - is now the preferred name for new work
- Output filenames remain unchanged for compatibility:
  - `streaming_student_checkpoint_selection.json`
  - `streaming_student_checkpoint_selection.md`
- The output payload now carries explicit selector identity fields:
  - `selector_version = stage3_posthoc_teacher_loss_checkpoint_selector_v1`
  - `selection_objective = posthoc_teacher_supervised_loss`
  - `best_checkpoint_by_posthoc_teacher_loss`
- `best_checkpoint` is retained only as a legacy alias field.

## Verification

### 1. Compile check
- Command:
  - `python -m compileall src/v5vc/streaming_student/checkpoint_selection_entry.py src/v5vc/cli.py`
- Result:
  - pass

### 2. Explicit alias command run
- Command family:
  - `.\python.exe -m v5vc.cli select-streaming-student-posthoc-teacher-loss-checkpoint ...`
  - with `PYTHONPATH=src`
  - same dense `warm6_18` checkpoint set:
    - `step12`
    - `step15`
    - `step18`
  - output:
    - `reports/eval/ss_posthoc_t6wb18dense_r1_1/`
- Result:
  - command completed successfully
  - report header now explicitly reads:
    - `Stage3 Streaming Student Post-Hoc Teacher-Loss Checkpoint Selection`
  - selection metadata is present in JSON and markdown

## Main Findings

### 1. Tooling now states its own objective instead of relying on tribal memory
- This was the missing hardening after `477`.
- A report consumer can now tell directly whether the ranking came from:
  - packet-aware downstream screening
  - or post-hoc teacher-loss evaluation

### 2. Backward compatibility was preserved where it matters
- Old docs, notes, and scripts that still call `select-streaming-student-best-checkpoint` will not break.
- At the same time, new work no longer needs to keep spreading the ambiguous old name.

### 3. The command naming now matches the actual evidence role
- The selector does not pick a universal "best checkpoint".
- It picks a checkpoint that is best under:
  - post-hoc full-slice teacher-supervised proxy loss
- That wording is now visible in:
  - CLI help
  - markdown title
  - JSON fields
  - report notes

## Judgment
- This hardening is low-risk and worthwhile.
- It does not change Stage3 scientific conclusions.
- It changes the chance of future decision drift caused by ambiguous naming.
- The repo can now keep both truths in parallel without hiding the distinction:
  - packet-aware next-best candidate:
    - `warm6_18.step15`
  - current post-hoc teacher-loss best on the same three-checkpoint recheck:
    - `warm6_18.step12`

## Mainline Impact
- Prefer the explicit command name for new work:
  - `select-streaming-student-posthoc-teacher-loss-checkpoint`
- Keep the packet-aware selector as the handoff-facing selector.
- Keep the post-hoc teacher-loss selector as the teacher-loss comparison selector.
- Do not use either selector output without naming its objective in the corresponding report.

## Key Artifacts
- Explicit alias output:
  - `reports/eval/ss_posthoc_t6wb18dense_r1_1/streaming_student_checkpoint_selection.json`
- Related report:
  - `docs/477_stage3_packet_aware_checkpoint_selector_integration_and_selection_drift_report.md`
