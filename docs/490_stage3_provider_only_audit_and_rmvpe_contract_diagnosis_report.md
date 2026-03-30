# Stage3 provider-only audit and RMVPE contract diagnosis report

## Summary
- Added a dedicated Stage3 provider-only audit CLI:
  - `audit-streaming-student-pitch-provider`
- The audit compares raw provider outputs directly against teacher `target_f0_hz` and `target_vuv`.
- No Stage3 student correction, proxy acoustic branch, or downstream packet calibration is involved.

## Scope
- Configs audited:
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_v1.json`
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_rmvpe_v1.json`
- Split:
  - `target_validation`
- Sample count:
  - `8`
- Output roots:
  - `reports/runtime/streaming_student_pitch_provider_audit_detpitch_validation8`
  - `reports/runtime/streaming_student_pitch_provider_audit_rmvpe_validation8`

## What changed
- The existing provider-only audit entry was promoted to a first-class CLI command and exported from the Stage3 package.
- Files touched for the CLI bootstrap:
  - `src/v5vc/cli.py`
  - `src/v5vc/streaming_student/__init__.py`
  - `src/v5vc/streaming_student/pitch_provider_audit_entry.py`

## Deterministic provider audit result
- `deterministic_extractor_v1` behaved as the expected positive control.
- Aggregate current-contract metrics on 8 validation records:
  - `ready_like_count = 8/8`
  - `avg_voiced_log2_mae = 0.0`
  - `avg_voiced_corr = 1.0`
  - `avg_vuv_mae = 0.0`
  - `avg_vuv_f1 = 1.0`
- This confirms:
  - the provider-only audit itself is wired correctly
  - the teacher target contract is internally coherent
  - the shared Stage3 provider interface is not the root cause of the RMVPE failure

## RMVPE provider audit result
- `rmvpe_v1` failed the provider-only readiness-like screen on all 8 audited validation records.
- Current-contract aggregate metrics:
  - `ready_like_count = 0/8`
  - `avg_voiced_log2_mae = 1.608832`
  - `avg_voiced_corr = -0.430655`
  - `avg_affine_voiced_log2_mae = 0.174768`
  - `avg_vuv_mae = 0.21888`
  - `avg_vuv_f1 = 0.852326`
- Best-correlation sweep result over anchor `{start, center, end}` and lag `[-8, +8]`:
  - `ready_like_count = 0/8`
  - `avg_voiced_corr = -0.13859`
  - `avg_voiced_log2_mae = 2.64388`
  - `avg_vuv_f1 = 0.715763`
- Best-MAE sweep result:
  - `ready_like_count = 0/8`
  - `avg_voiced_log2_mae = 1.567083`
  - `avg_voiced_corr = -0.390457`
  - `avg_vuv_f1 = 0.857427`

## Per-record pattern
- One record is genuinely good under the current contract:
  - `target::chapter3_29_firefly_130`
  - `voiced_log2_mae = 0.086231`
  - `voiced_corr = 0.540977`
  - `vuv_f1 = 0.961194`
- Several records are structurally bad and remain bad after lag/anchor sweep:
  - `target::chapter4_7_firefly_105`
    - current `voiced_log2_mae = 3.944556`
    - current `voiced_corr = -0.947121`
    - current `vuv_f1 = 0.698678`
  - `target::chapter3_4_firefly_106`
    - current `voiced_log2_mae = 3.772204`
    - current `voiced_corr = -0.890394`
    - current `vuv_f1 = 0.705432`
  - `target::chapter3_26_firefly_114`
    - current `voiced_log2_mae = 3.0811`
    - current `voiced_corr = -0.850049`
    - current `vuv_f1 = 0.747126`
- Positive-correlation counts:
  - current contract: `1/8`
  - best-correlation sweep: `4/8`
  - correlation `>= 0.3`: still only `1/8`

## Interpretation
- The deterministic positive control proves the Stage3 provider audit and target contract are valid.
- The RMVPE mismatch is not explained by a simple global lag:
  - lag and anchor sweeping improved some records slightly
  - the sweep did not produce any readiness-like success
  - aggregate correlation remained negative
- The failure is also not "pure VUV collapse":
  - aggregate `vuv_f1` is still about `0.85`
  - some records retain strong VUV behavior while F0 correlation remains negative
- The low affine-fit MAE relative to raw MAE suggests partial monotonic information is present in some regions, but the direct Stage3 contract is still wrong enough that RMVPE cannot be promoted.
- The mismatch appears heterogeneous across records:
  - some are near-usable
  - some show severe under-voicing
  - some likely contain octave and/or calibration mismatch on voiced frames

## Decision
- Do not promote `rmvpe_v1` to the default Stage3 pitch provider.
- Do not spend more time on simple lag-only sweeps.
- Do not resume longer Stage3 training runs with current raw RMVPE injection.

## Next actions
1. Run a hybrid provider diagnosis:
   - `rmvpe_f0 + deterministic_vuv`
   - This isolates whether the dominant mismatch comes from F0 magnitude/trajectory or from voiced-mask contract drift.
2. Add voiced-intersection diagnostics:
   - evaluate F0 only on frames where both RMVPE and teacher are voiced
   - add octave-shift and affine-log2 probes there
3. If the hybrid and voiced-intersection probes still fail, treat RMVPE as non-viable for the current Stage3 contract and keep the deterministic provider only as a structural reference route.

## Artifact references
- Deterministic audit summary:
  - `reports/runtime/streaming_student_pitch_provider_audit_detpitch_validation8/streaming_student_pitch_provider_audit.json`
- RMVPE audit summary:
  - `reports/runtime/streaming_student_pitch_provider_audit_rmvpe_validation8/streaming_student_pitch_provider_audit.json`
