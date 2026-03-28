# 477 Stage3 packet-aware checkpoint selector integration and selection-drift report

## Scope
- Formalize the previously manual Stage3 packet-aware checkpoint comparison into a reusable repo command.
- Verify the command on the known `warm6_18` dense-checkpoint slice.
- Re-check the existing validation-first checkpoint selector in the current codebase.

## Code Changes
- Added a new Stage3 packet-aware checkpoint selector:
  - `src/v5vc/streaming_student/packet_checkpoint_selection_entry.py`
- Wired the new selector into package exports:
  - `src/v5vc/streaming_student/__init__.py`
- Added a new CLI command:
  - `select-streaming-student-packet-aware-checkpoint`
  - implemented in `src/v5vc/cli.py`
- Repaired the existing validation-first selector after contract drift:
  - `src/v5vc/streaming_student/checkpoint_selection_entry.py`
  - fix: pass `semantic_supervision` through to `evaluate_split(...)`

## Verification

### 1. Compile check
- Command:
  - `python -m compileall src/v5vc/streaming_student/packet_checkpoint_selection_entry.py src/v5vc/streaming_student/__init__.py src/v5vc/streaming_student/checkpoint_selection_entry.py src/v5vc/cli.py`
- Result:
  - pass

### 2. Packet-aware selector run
- Command family:
  - `.\python.exe -m v5vc.cli select-streaming-student-packet-aware-checkpoint ...`
  - with `PYTHONPATH=src`
  - checkpoints:
    - `step12`
    - `step15`
    - `step18`
  - output:
    - `reports/eval/streaming_student_packet_checkpoint_selection_timingfocus6warm_baseline18_denseckpt_round1_1/`
- Result:
  - command completed successfully
  - best checkpoint:
    - `warm6_18.step15`

### 3. Validation-first selector re-check
- Command family:
  - `.\python.exe -m v5vc.cli select-streaming-student-best-checkpoint ...`
  - with `PYTHONPATH=src`
  - same three checkpoints
  - output:
    - `reports/eval/streaming_student_checkpoint_selection_timingfocus6warm_baseline18_denseckpt_round1_1_recheck/`
- Result:
  - before the fix, this command failed because `evaluate_split(...)` now requires `semantic_supervision`
  - after the fix, the command completed successfully

## Main Findings

### 1. The new packet-aware selector reproduces the current manual Stage3 packet judgment
- Packet-aware ranking on the three dense checkpoints is:
  - `step15`
  - `step18`
  - `step12`
- The best row is:
  - `auto_reject_count = 3`
  - `vuv_ready_count = 1`
  - `f0_ready_count = 0`
  - `aper_ready_count = 3`
  - `energy_ready_count = 2`
  - `avg_vuv_reference_mae = 0.18271`
  - `avg_aper_calibrated_reference_mae = 0.118447`
  - `avg_energy_stage5_norm_calibrated_reference_mae = 0.143582`
  - `avg_f0_proxy_reference_corr = 0.416655`
  - `avg_f0_calibrated_log2_mae = 0.329577`
- This matches the practical conclusion already carried in `453` and `459`:
  - packet-aware next-best candidate remains `warm6_18.step15`

### 2. The repo previously had no formal Stage3 packet-aware selector, only manual report logic
- This gap is now closed.
- The new selector turns packet-facing checkpoint choice into a reproducible artifact instead of a one-off report judgment.

### 3. There is real checkpoint-selection objective drift, not just a tooling gap
- The repaired validation-first selector now ranks the same three checkpoints as:
  - `step12`
  - `step15`
  - `step18`
- Current post-hoc full-checkpoint losses are:
  - `step12`: `target_validation_loss_total = 1.435668`, `target_special_eval_loss_total = 1.271588`
  - `step15`: `1.476498`, `1.162192`
  - `step18`: `1.536822`, `1.196767`
- So the repo now has at least three different notions of "best checkpoint":
  - in-loop training-trajectory validation from historical reports
  - post-hoc full-checkpoint teacher-supervised evaluation
  - packet-aware downstream cheap screen

### 4. Historical "validation best = step18" should not be silently conflated with the repaired selector output
- `453` used the training trajectory recorded during the dense warm-start run.
- The repaired selector uses current post-hoc full-slice checkpoint evaluation against current teacher-label and calibration assets.
- These are not the same metric, and they can disagree.
- Therefore the current mismatch is a scope difference first, not automatically evidence that the older report was wrong.

## Judgment
- The new packet-aware selector is valid and useful.
- It answers a real active mainline question:
  - which Stage3 checkpoint is least bad for downstream packet-facing handoff screening
- The repaired validation-first selector is also useful again, but it must now be interpreted more carefully:
  - it is a post-hoc full-checkpoint teacher-loss selector
  - it is not interchangeable with historical in-loop validation summaries
- The main risk is not the packet-aware selector itself.
- The main risk is continuing to say "best checkpoint" without specifying:
  - best by which metric
  - best for which downstream decision

## Mainline Impact
- Keep the Stage3 packet-facing reference unchanged:
  - `vuvbalancedgate24`
- Keep the packet-aware next-best candidate unchanged:
  - `warm6_18.step15`
- Use the new packet-aware selector whenever the question is downstream packet or handoff screening.
- Keep the repaired validation-first selector for post-hoc teacher-loss comparison, but do not let it overwrite packet-aware handoff judgment by naming ambiguity.
- Do not open a new Stage5 route from any of these checkpoints yet:
  - all three sampled dense checkpoints remain `auto_reject`
  - `F0 / vuv / aper / E` are still not handoff-ready

## Key Artifacts
- Packet-aware selector output:
  - `reports/eval/streaming_student_packet_checkpoint_selection_timingfocus6warm_baseline18_denseckpt_round1_1/streaming_student_packet_checkpoint_selection.json`
- Validation-first selector output after repair:
  - `reports/eval/streaming_student_checkpoint_selection_timingfocus6warm_baseline18_denseckpt_round1_1_recheck/streaming_student_checkpoint_selection.json`
- Historical comparison context:
  - `docs/453_stage3_warm6_dense_checkpoint_packetaware_selection_report.md`
  - `docs/459_stage3_targetblend_earlystop_and_checkpoint_average_probe_report.md`
