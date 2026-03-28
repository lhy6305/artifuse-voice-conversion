# 483 Stage3 selector output path budget remediation report

## Scope
- Remediate repeated Windows long-path incidents in recent Stage3 selector artifacts.
- Fix the corresponding writers instead of only deleting the affected directories.
- Record the replacement artifact roots and the new path-budget rule now in force.

## Incident
- The following managed output roots were long enough to trigger sandbox and Windows-style path handling warnings:
  - `reports/eval/streaming_student_checkpoint_selector_comparison_timingfocus6warm_baseline18_denseckpt_round1_1`
  - `reports/eval/streaming_student_checkpoint_selector_comparison_vuvbalancedgate24_vs_warm6step15_round1_1`
- The same naming pattern also made the related selector outputs fragile:
  - `reports/eval/streaming_student_posthoc_teacher_loss_checkpoint_selection_timingfocus6warm_baseline18_denseckpt_round1_1`
  - `reports/eval/streaming_student_packet_checkpoint_selection_timingfocus6warm_baseline18_denseckpt_round1_1`
- The failure mode was operational, not cosmetic:
  - artifact write could succeed
  - later move, follow-up write, or filesystem traversal could become unreliable

## Root Cause
- Output root leaves encoded the full experiment sentence.
- Nested selector subdirectories also stayed verbose.
- Packet export directories repeated full experiment ids at another nesting level.
- The result was deep file paths around `290+` characters on this machine.

## Code Remediation
- Added managed-path shortening helpers in:
  - `src/v5vc/managed_paths.py`
- New helper behavior:
  - sanitize path components
  - compact long components with a short hash suffix
  - resolve managed output roots against a Windows-safe soft budget
- The current repo-side soft ceiling is:
  - `220`

## Writer Changes
- Updated:
  - `src/v5vc/streaming_student/checkpoint_selection_entry.py`
  - `src/v5vc/streaming_student/packet_checkpoint_selection_entry.py`
  - `src/v5vc/streaming_student/checkpoint_selector_comparison_entry.py`
  - `src/v5vc/cli.py`
- Effective changes:
  - selector output dirs now pass through `resolve_managed_output_dir(...)`
  - selector artifacts now record both `requested_output_dir` and actual `output_dir`
  - packet export subtree names were shortened from `packet_exports` to `pkt_exp`
  - comparison subtree names were shortened from verbose labels to `posthoc` and `pkt`
  - long packet export leaf names now use compact step-plus-hash forms instead of repeating the full raw experiment id
  - Stage3 selector CLI defaults now prefer compact roots:
    - `reports/eval/ss_posthoc_<scope>`
    - `reports/eval/ss_pktsel_<scope>`
    - `reports/eval/ss_cmp_<scope>`

## Replacement Artifacts
- The long-path outputs were regenerated into compact roots:
  - `reports/eval/ss_posthoc_t6wb18dense_r1_1`
  - `reports/eval/ss_pktsel_t6wb18dense_r1_1`
  - `reports/eval/ss_cmp_t6wb18dense_r1_1`
  - `reports/eval/ss_cmp_vbg24_vs_w6s15_r1_1`
- The old long-path roots were then removed so active docs no longer point at fragile paths.

## Verification
- Measured deepest paths after remediation:
  - `ss_posthoc_t6wb18dense_r1_1`: `109`
  - `ss_pktsel_t6wb18dense_r1_1`: `159`
  - `ss_cmp_t6wb18dense_r1_1`: `160`
  - `ss_cmp_vbg24_vs_w6s15_r1_1`: `163`
- These are now below the current managed Windows soft budget.
- Active docs and live selector code no longer reference the deleted long-path roots.
- The short-path replacement artifacts preserve the same Stage3 conclusions as the earlier runs:
  - dense family comparison still separates `step12` post-hoc teacher-loss leadership from `step15` packet-aware leadership
  - role-aware comparison still keeps `vuvbalancedgate24.step24` as packet-facing reference and `warm6_18.step15` as the next-best non-reference packet candidate

## Policy Outcome
- This incident is now governed by:
  - `docs/482_windows_path_budget_and_artifact_naming_policy.md`
- Required behavior going forward:
  1. shorten the writer immediately after any long-path warning
  2. regenerate or relocate the artifact into a compact root
  3. update the citing docs to the actual short path
  4. keep managed outputs under the current path budget instead of treating path warnings as harmless noise
