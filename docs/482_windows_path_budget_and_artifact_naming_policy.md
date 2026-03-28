# 482 Windows path budget and artifact naming policy

## Scope
- Prevent repeated Windows long-path incidents in managed experiment outputs.
- Define a path-budget policy for new reports, scripts, and CLI defaults.
- Record the repo-side mitigations now in place.

## Why This Exists
- Recent Stage3 selector artifacts repeatedly produced very long nested paths.
- The concrete failure mode was:
  - sandbox safe-write succeeded
  - later move or follow-up filesystem operations became unreliable
- This is not a one-off naming annoyance.
- It is a recurring operational defect.

## Effective Policy

### 1. Treat `220` characters as the soft managed-path ceiling
- New managed output paths should stay comfortably below classic Windows path trouble zones.
- The repo now uses:
  - `LEGACY_WINDOWS_PATH_SOFT_LIMIT = 220`
  - file:
    - `src/v5vc/managed_paths.py`

### 2. Keep output-directory leaf names short
- New managed output roots should use compact leaf names.
- Do not create new roots like:
  - `reports/eval/streaming_student_checkpoint_selector_comparison_<very_long_suffix>`
- Prefer compact leaves such as:
  - `ss_cmp_<short_scope>`
  - `ss_posthoc_<short_scope>`
  - `ss_pktsel_<short_scope>`

### 3. Keep nested internal directory names short too
- Short root names alone are not enough.
- Internal nested directories must also stay compact.
- Current Stage3 selector tooling now uses:
  - `posthoc`
  - `pkt`
  - `pkt_exp`
- Packet export subdirectories now compact long experiment ids with a hash suffix instead of writing full raw experiment ids into every nested directory.

### 4. Preserve meaning, but compress aggressively after the scope is identifiable
- A path should stay human-recognizable.
- It does not need to spell out the entire experiment sentence.
- Good pattern:
  - stable short prefix
  - compressed scope token
  - round tag
- Example:
  - `ss_cmp_vbg24_vs_w6s15_r1_1`

### 5. Managed output may be auto-shortened
- The repo now resolves managed output directories through:
  - `resolve_managed_output_dir(...)`
  - file:
    - `src/v5vc/managed_paths.py`
- If a requested output dir is too long, the actual managed output dir may be compacted automatically.
- Artifacts should therefore record both:
  - `requested_output_dir`
  - `output_dir`

## Current Repo Mitigations
- Added generic helpers in:
  - `src/v5vc/managed_paths.py`
    - `sanitize_path_component(...)`
    - `compact_path_component(...)`
    - `resolve_managed_output_dir(...)`
- Updated Stage3 selectors to use managed short-path resolution:
  - `src/v5vc/streaming_student/checkpoint_selection_entry.py`
  - `src/v5vc/streaming_student/packet_checkpoint_selection_entry.py`
  - `src/v5vc/streaming_student/checkpoint_selector_comparison_entry.py`
- Shortened current CLI default output roots in:
  - `src/v5vc/cli.py`

## Naming Conventions For New Stage3 Selector Artifacts
- Post-hoc teacher-loss selector:
  - `reports/eval/ss_posthoc_<scope>`
- Packet-aware selector:
  - `reports/eval/ss_pktsel_<scope>`
- Combined selector comparison:
  - `reports/eval/ss_cmp_<scope>`
- Scope tokens should be compressed:
  - `t6wb18dense`
  - `vbg24_vs_w6s15`
  - `r1_1`

## Required Reporting Behavior
- When a tool auto-shortens output paths, the report must cite the actual short output path.
- Do not keep documenting only the original long requested path once a shorter replacement exists.
- When a long-path incident occurs:
  1. shorten the writer
  2. regenerate or relocate the artifact
  3. update the referencing docs
  4. record the rule if it is likely to recur

## Current Outcome
- The recent Stage3 selector artifacts that previously exceeded `290` characters at the deepest file path have been reduced to roughly `160` characters at maximum depth.
- This is now inside the repo's managed Windows path budget.
