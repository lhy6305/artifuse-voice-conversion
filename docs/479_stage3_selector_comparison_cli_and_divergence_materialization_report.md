# 479 Stage3 selector comparison CLI and divergence materialization report

## Scope
- Add one Stage3 command that runs both active checkpoint selectors on the same checkpoint set.
- Materialize selector disagreement into one combined artifact instead of forcing manual cross-reading.
- Verify the command on the known `warm6_18` dense checkpoint slice.

## Code Changes
- Added a combined selector-comparison entry:
  - `src/v5vc/streaming_student/checkpoint_selector_comparison_entry.py`
- Wired the comparison entry into package exports:
  - `src/v5vc/streaming_student/__init__.py`
- Added a new CLI command:
  - `compare-streaming-student-checkpoint-selectors`
  - implemented in `src/v5vc/cli.py`
- Hardened the packet-aware selector with explicit identity fields:
  - `selector_version = stage3_packet_aware_checkpoint_selector_v1`
  - `selection_objective = packet_aware_downstream_screen`
  - `best_checkpoint_by_packet_screen`
  - file:
    - `src/v5vc/streaming_student/packet_checkpoint_selection_entry.py`

## Verification

### 1. Compile check
- Command:
  - `python -m compileall src/v5vc/streaming_student/checkpoint_selector_comparison_entry.py src/v5vc/streaming_student/packet_checkpoint_selection_entry.py src/v5vc/streaming_student/__init__.py src/v5vc/cli.py`
- Result:
  - pass

### 2. Combined selector run
- Command family:
  - `.\python.exe -m v5vc.cli compare-streaming-student-checkpoint-selectors ...`
  - with `PYTHONPATH=src`
  - checkpoint set:
    - `step12`
    - `step15`
    - `step18`
  - output:
    - `reports/eval/ss_cmp_t6wb18dense_r1_1/`
- Result:
  - command completed successfully
  - combined comparison artifact was generated

## Main Findings

### 1. Selector divergence is now directly materialized instead of inferred
- Combined output states:
  - `top1_agree = false`
- The two top picks are:
  - post-hoc teacher-loss best:
    - `step12`
  - packet-aware best:
    - `step15`

### 2. The largest ranking split is no longer hidden in two separate directories
- The combined report marks:
  - `largest_rank_gap = step12`
  - post-hoc teacher-loss rank:
    - `1`
  - packet-aware rank:
    - `3`
  - `rank_delta = 2`
- This is the strongest concise statement of the current mismatch:
  - the same checkpoint can look best under teacher-loss recheck and worst under packet-aware screening

### 3. The comparison command reduces interpretation risk without changing scientific conclusions
- No selector result changed because of this command.
- What changed is the evidence surface:
  - future reports no longer need to manually stitch together
    - one post-hoc selector output
    - one packet-aware selector output
    - one handwritten conclusion paragraph
- The combined artifact now carries:
  - selector objectives
  - selector versions
  - top-1 agreement status
  - per-checkpoint rank deltas

## Judgment
- This command is worth keeping as the default checkpoint-disagreement materializer for Stage3.
- It directly supports the current mainline governance rule:
  - do not say "best checkpoint" without naming the selection objective
- It also shortens future evidence loops:
  - one command
  - one output directory
  - one explicit disagreement record

## Mainline Impact
- Keep current Stage3 checkpoint conclusions unchanged:
  - post-hoc teacher-loss recheck best:
    - `warm6_18.step12`
  - packet-aware next-best candidate:
    - `warm6_18.step15`
- For future Stage3 checkpoint-family reviews, prefer this order:
  1. run `compare-streaming-student-checkpoint-selectors`
  2. cite the combined report
  3. only then decide which selector matters for the downstream decision
- This does not open a new Stage5 route:
  - all three dense checkpoints remain packet auto-reject
  - `F0 / vuv / aper / E` are still not handoff-ready

## Key Artifacts
- Combined comparison output:
  - `reports/eval/ss_cmp_t6wb18dense_r1_1/streaming_student_checkpoint_selector_comparison.json`
- Supporting selector reports inside the same output root:
  - `posthoc/streaming_student_checkpoint_selection.json`
  - `pkt/streaming_student_packet_checkpoint_selection.json`
- Related reports:
  - `docs/477_stage3_packet_aware_checkpoint_selector_integration_and_selection_drift_report.md`
  - `docs/478_stage3_selector_naming_hardening_and_legacy_alias_report.md`
