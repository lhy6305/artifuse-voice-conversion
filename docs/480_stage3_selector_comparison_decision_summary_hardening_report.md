# 480 Stage3 selector comparison decision-summary hardening report

## Scope
- Extend the combined Stage3 selector-comparison artifact from raw disagreement display to decision-oriented output.
- Make the comparison artifact explicitly separate:
  - teacher-loss reference choice
  - handoff-facing packet candidate choice
  - unified best checkpoint status
  - conservative Stage5 route-opening recommendation

## Code Changes
- Hardened:
  - `src/v5vc/streaming_student/checkpoint_selector_comparison_entry.py`
- Added a new `decision_summary` section to the combined comparison payload:
  - `teacher_loss_reference_checkpoint`
  - `handoff_facing_packet_candidate_checkpoint`
  - `unified_best_checkpoint`
  - `top1_agree`
  - `open_new_stage5_route_recommended`
  - `rationale`
- Updated the combined markdown report to show:
  - `Decision Summary`

## Verification

### 1. Compile check
- Command:
  - `python -m compileall src/v5vc/streaming_student/checkpoint_selector_comparison_entry.py`
- Result:
  - pass

### 2. Re-run combined selector comparison
- Command family:
  - `.\python.exe -m v5vc.cli compare-streaming-student-checkpoint-selectors ...`
  - with `PYTHONPATH=src`
  - same dense `warm6_18` checkpoint set
- Result:
  - command completed successfully
  - combined markdown now includes `Decision Summary`
  - combined JSON now includes `decision_summary`

## Main Findings

### 1. The combined artifact now gives two actionable roles instead of one overloaded ranking story
- Current `decision_summary` resolves the checkpoint family into:
  - `teacher_loss_reference_checkpoint = step12`
  - `handoff_facing_packet_candidate_checkpoint = step15`
  - `unified_best_checkpoint = null`
- This is the right representation of the current evidence.
- It is better than forcing one selector to overwrite the other.

### 2. The artifact now emits a conservative route-opening conclusion directly
- Current combined output says:
  - `open_new_stage5_route_recommended = false`
- Current rationale is:
  - the packet-aware top checkpoint still shows sampled auto-reject behavior
- This is consistent with the current mainline gate logic:
  - comparison tooling can identify the least-bad handoff-facing candidate
  - it still cannot promote a new Stage5 route while the packet screen remains auto-reject

### 3. The comparison artifact now closes the last big interpretation gap
- Before this hardening:
  - the combined artifact showed disagreement
  - but a reader still had to infer the practical next decision
- After this hardening:
  - the artifact itself states the recommended role split
  - and explicitly states that route opening is not recommended

## Judgment
- This is the correct next step after `479`.
- It does not add a new research claim.
- It converts existing evidence into a safer operational interface for future takeover and reporting.
- The main value is governance:
  - fewer hand-written explanations
  - fewer ambiguous "best checkpoint" statements
  - a more direct bridge from selector evidence to route decision discipline

## Mainline Impact
- Keep the active Stage3 checkpoint-family reading unchanged:
  - teacher-loss reference:
    - `warm6_18.step12`
  - handoff-facing packet candidate:
    - `warm6_18.step15`
  - unified best checkpoint:
    - none
  - open new Stage5 route:
    - no
- For future Stage3 selector comparisons, prefer citing the `decision_summary` block first, then the detailed per-checkpoint rank table second.

## Key Artifacts
- Hardened combined comparison output:
  - `reports/eval/ss_cmp_t6wb18dense_r1_1/streaming_student_checkpoint_selector_comparison.json`
- Related reports:
  - `docs/479_stage3_selector_comparison_cli_and_divergence_materialization_report.md`
  - `docs/478_stage3_selector_naming_hardening_and_legacy_alias_report.md`
