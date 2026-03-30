# Stage3 deterministic peak-focused ENERGY objective route opening report

## Summary
- A new deterministic `ENERGY` objective family was tested after the previous same-family continuation line was stopped.
- Structural scaffold:
  - keep the dedicated APER branch frozen after the `APER = 3/3` opening
  - keep the dedicated ENERGY branch active
- New loss family:
  - `teacher_energy_stage5_peak_affine_calibrated`
  - implemented as a peak-focused affine-calibrated Stage5 energy loss that upweights high reference energy frames
- New loss override:
  - `configs/streaming_student_loss_weights_detpitch_aperbranch_energypeak_stage5calib_v1.json`
- Main result:
  - starting from the stable packet-facing anchor `ss_detpitch_aperbranch_energy_warm4.step2`, a single peak-focused step opens the full active sample3 packet screen
  - the resulting checkpoint reaches:
    - `energy_ready_count = 3/3`
    - `all_core_controls_ready_count = 3/3`
    - `auto_reject_count = 0`
- This is the first deterministic Stage3 checkpoint family in the current line that clears all four core controls on the active sample3 packet screen

## Implementation
- Code change:
  - `src/v5vc/streaming_student/losses.py`
- New loss key:
  - `teacher_energy_stage5_peak_affine_calibrated`
- Loss behavior:
  - keep the existing affine-calibrated Stage5 energy term
  - add a second affine-calibrated term with higher frame weight on high reference Stage5 energy frames
  - motivation: the remaining blocker had the shape of high-energy peak compression rather than APER or VUV failure

## Probes run

### Probe A: peak-focused loss from the blocker-facing micro-anchor
- Init checkpoint:
  - `ss_detpitch_aperbranch_energyonly_s2_warm4.step1`
- Training:
  - `reports/training/ss_detpitch_energypeak_micro1`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_energypeak_micro1/streaming_student_packet_checkpoint_selection.json`
- Result:
  - this still regresses
  - blocker-record `ENERGY` stays bad at `0.247702`
  - this confirms the old micro-anchor is not the right base even under the new loss family

### Probe B: peak-focused loss from the stable packet-facing anchor
- Init checkpoint:
  - `ss_detpitch_aperbranch_energy_warm4.step2`
- Training:
  - `reports/training/ss_detpitch_energypeak_s2_step1`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_energypeak_s2_step1/streaming_student_packet_checkpoint_selection.json`
- Result:
  - this probe succeeds immediately in one step

## Packet result of the winning checkpoint
- Winning checkpoint:
  - `reports/training/ss_detpitch_energypeak_s2_step1/checkpoints/ss_detpitch_energypeak_s2_step1.step1.pt`

| metric | value |
| --- | ---: |
| auto_reject_count | `0` |
| all_core_controls_ready_count | `3/3` |
| f0_ready_count | `3/3` |
| vuv_ready_count | `3/3` |
| aper_ready_count | `3/3` |
| energy_ready_count | `3/3` |
| avg_energy_stage5_norm_calibrated_reference_mae | `0.097862` |

## Record-level result

| record | aper calibrated mae | energy calibrated mae | all-core ready |
| --- | ---: | ---: | --- |
| `target::chapter3_3_firefly_162` | `0.084215` | `0.073133` | `true` |
| `target::chapter3_3_firefly_138` | `0.096371` | `0.089424` | `true` |
| `target::chapter3_4_firefly_106` | `0.162226` | `0.131030` | `true` |

- The old blocker record `target::chapter3_4_firefly_106` is now clearly past the energy gate:
  - previous best blocker-facing result: `0.150089`
  - new peak-focused result: `0.131030`

## Interpretation
- The earlier failure mode was not just "needs one more continuation step."
- The real issue was:
  - the continuation family had already saturated
  - the remaining gap needed a different objective shape
- The successful change is:
  - not a new provider
  - not a new branch
  - not a longer continuation
  - but a better `ENERGY` objective that explicitly emphasizes the peak region the old family was compressing

## Decision
- Promote the new checkpoint as the current strongest deterministic packet-facing checkpoint:
  - `ss_detpitch_energypeak_s2_step1.step1`
- Keep the old references only for role clarity:
  - stable packet-facing anchor before redesign: `ss_detpitch_aperbranch_energy_warm4.step2`
  - raw deterministic `ENERGY` frontier before redesign: `ss_detpitch_aperbranch_energy_warm4.step3`
  - blocker-facing micro-frontier before redesign: `ss_detpitch_aperbranch_energyonly_s2_warm4.step1`

## Scope note
- This result clears the active sample3 packet screen.
- It does not by itself prove broader validation robustness or Stage5 handoff success.
- But it is the first clean deterministic answer to the local four-control packet gate problem.

## Next actions
1. Keep `ss_detpitch_energypeak_s2_step1.step1` as the active deterministic checkpoint.
2. Stop the old same-family continuation line permanently.
3. Make the next work item a confirmation pass:
   - repeat packet screen on a broader slice
   - or do downstream-facing confirmation using the new winning checkpoint
