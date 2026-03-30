# Stage3 RMVPE voiced-intersection and hybrid-VUV diagnosis report

## Summary
- Extended the Stage3 provider-only audit with:
  - `hybrid_reference_vuv_current`
  - `joint_*` voiced-intersection metrics
  - joint voiced-frame affine and octave probes
- Re-ran the RMVPE validation audit on `8` `target_validation` records.
- Main conclusion:
  - the dominant RMVPE mismatch is not raw F0 value quality on jointly voiced frames
  - the dominant mismatch is the voiced-support contract
  - octave shift is not the main failure mode on the audited slice

## Added diagnostics
- `hybrid_reference_vuv_current`
  - keeps RMVPE F0
  - replaces provider VUV with deterministic teacher-reference VUV
- `joint_*`
  - evaluates only frames where both RMVPE and teacher are voiced
- joint octave probe
  - tested integer octave shifts `{-2, -1, 0, 1, 2}` on jointly voiced frames

## Aggregate result
- RMVPE current-contract summary remains poor:
  - `ready_like_count = 0/8`
  - `avg_voiced_log2_mae = 1.608832`
  - `avg_voiced_corr = -0.430655`
  - `avg_vuv_f1 = 0.852326`
- But jointly voiced frames tell a different story:
  - `avg_joint_voiced_log2_mae = 0.1088`
  - `avg_joint_voiced_corr = 0.547401`
  - `avg_joint_affine_voiced_log2_mae = 0.112226`
  - `avg_joint_octave_shift_best_mae = 0.1088`
- Hybrid-VUV result:
  - `avg_vuv_mae = 0.0`
  - `avg_vuv_f1 = 1.0`
  - but `ready_like_count` still stays `0/8`
  - raw reference-voiced F0 metrics stay unchanged

## Interpretation
- `hybrid_reference_vuv_current` proves VUV is not the only blocker.
- But the large gap between:
  - `avg_voiced_corr = -0.430655`
  - and `avg_joint_voiced_corr = 0.547401`
  shows that the main collapse happens when RMVPE misses teacher-voiced frames or adds voiced support on different frames.
- In other words:
  - RMVPE F0 is often reasonable where it and the teacher agree on voicing
  - the current Stage3 contract fails because it expects a voiced-support pattern closer to the deterministic teacher target
- The joint octave probe consistently selected shift `0.0` on the audited slice.
- Therefore the current evidence does not support octave-offset as the primary failure mode.

## Per-record examples
- `target::chapter3_3_firefly_210`
  - current `voiced_corr = -0.662539`
  - joint `voiced_corr = 0.874952`
  - joint `voiced_log2_mae = 0.062671`
- `target::chapter3_4_firefly_106`
  - current `voiced_corr = -0.890394`
  - joint `voiced_corr = 0.681062`
  - joint `voiced_log2_mae = 0.092453`
- `target::chapter4_7_firefly_105`
  - current `voiced_corr = -0.947121`
  - joint `voiced_corr = 0.566015`
  - joint `voiced_log2_mae = 0.087917`
- These examples show that several apparently "bad F0" records become fairly normal once the voiced-support mismatch is factored out.

## Decision
- Do not treat RMVPE as rejected on F0 value quality alone.
- Do not spend the next cycle on octave-shift debugging.
- Do not spend the next cycle on more lag-only sweeps.
- The next valid probe is provider-side voiced-mask calibration.

## Next actions
1. Add a provider-side RMVPE voicing calibration sweep:
   - vary `pitch_provider_voicing_threshold`
   - measure `current_contract` and `joint_*` metrics together
2. If needed, add simple VUV post-processing probes:
   - min-duration voiced smoothing
   - short-gap voiced filling
   - hybrid route `rmvpe_f0 + deterministic_vuv` as a structural fallback
3. Only after VUV calibration is understood, rerun Stage3 packet smoke with the best RMVPE voicing variant.

## Artifact references
- Enriched RMVPE audit summary:
  - `reports/runtime/streaming_student_pitch_provider_audit_rmvpe_validation8_v2/streaming_student_pitch_provider_audit.json`
