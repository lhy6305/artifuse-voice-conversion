# Stage3 deterministic ENERGY-only blocker-aware anchor probe report

## Summary
- A blocker-aware deterministic `ENERGY` continuation probe was run on top of the dedicated APER plus dedicated ENERGY scaffold.
- The APER branch stayed frozen after the earlier `APER = 3/3` structural opening.
- New config:
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_nof0corr_aperbranch_energyonlyfreeze_v1.json`
- New loss weights:
  - `configs/streaming_student_loss_weights_detpitch_aperbranch_energyonly_stage5calib_v1.json`
- Two anchors were compared:
  - `ss_detpitch_aperbranch_energy_warm4.step3`
  - `ss_detpitch_aperbranch_energy_warm4.step2`
- Main conclusion:
  - the `step3` raw-energy frontier is not the best blocker-aware continuation anchor
  - the better blocker-facing anchor is `step2`
  - after one short `ENERGY`-only continuation step from `step2`, the blocker record reaches:
    - `energy_stage5_norm_calibrated_reference_mae = 0.150089`
  - this misses the packet gate `0.15` by only `0.000089`
  - but the route still remains at `F0 / VUV / APER / ENERGY = 3/3, 3/3, 3/3, 2/3`

## Inputs
- Base combined deterministic frontier:
  - `reports/runtime/ss_pktsel_detpitch_aperbranch_energy_warm4/streaming_student_packet_checkpoint_selection.json`
- New `step3`-anchor ENERGY-only continuation:
  - training: `reports/training/ss_detpitch_aperbranch_energyonly_warm4`
  - packet selector: `reports/runtime/ss_pktsel_detpitch_aperbranch_energyonly_warm4/streaming_student_packet_checkpoint_selection.json`
- New `step2`-anchor ENERGY-only continuation:
  - training: `reports/training/ss_detpitch_aperbranch_energyonly_s2_warm4`
  - packet selector: `reports/runtime/ss_pktsel_detpitch_aperenergy_s2w4/streaming_student_packet_checkpoint_selection.json`

## Why this probe was run
- Earlier combined warm4 showed:
  - packet-facing top-1 at step `2`
  - raw deterministic `ENERGY` frontier at step `3`
  - blocker-record `ENERGY` at step `3` already near threshold:
    - `0.150639`
- But blind continuation from the near-threshold state was unstable.
- The next question was:
  - should the continuation anchor still be `step3`
  - or is `step2` actually the safer blocker-aware starting point once APER is frozen

## Result 1: `step3`-anchor ENERGY-only continuation is stable but not better on the blocker

| step | auto reject | all-core ready | energy ready | avg energy calibrated mae | blocker energy calibrated mae |
| --- | ---: | ---: | ---: | ---: | ---: |
| warm4.step3 baseline | 1 | 2 | 2 | 0.114200 | 0.150639 |
| step1 | 2 | 1 | 1 | 0.182341 | 0.244509 |
| step2 | 2 | 1 | 1 | 0.187875 | 0.251005 |
| step3 | 2 | 1 | 1 | 0.172885 | 0.225797 |
| step4 | 1 | 2 | 2 | 0.135224 | 0.173005 |

- Reading:
  - this line eventually recovers the old `2/3` opening by step `4`
  - but it never beats the original blocker frontier from combined warm4 step `3`
  - so the raw `step3` anchor is not the right blocker-aware continuation anchor for this family

## Result 2: `step2`-anchor ENERGY-only continuation produces a better blocker-facing micro-step

| step | auto reject | all-core ready | energy ready | avg energy calibrated mae | blocker energy calibrated mae |
| --- | ---: | ---: | ---: | ---: | ---: |
| warm4.step2 baseline | 1 | 2 | 2 | 0.150755 | 0.201414 |
| step1 | 1 | 2 | 2 | 0.114544 | 0.150089 |
| step2 | 2 | 1 | 1 | 0.163475 | 0.213296 |
| step3 | 2 | 1 | 1 | 0.172336 | 0.223783 |
| step4 | 2 | 1 | 1 | 0.156774 | 0.200685 |

- Reading:
  - step `1` is the only useful checkpoint in this continuation
  - it preserves:
    - `F0 = 3/3`
    - `VUV = 3/3`
    - `APER = 3/3`
    - `ENERGY = 2/3`
  - it also improves the blocker metric from:
    - `0.201414` at the anchor
    - to `0.150089`
  - but the following steps regress sharply

## Comparison against the previous best blocker metric
- Previous blocker-best on the active combined line:
  - `ss_detpitch_aperbranch_energy_warm4.step3`
  - `energy_stage5_norm_calibrated_reference_mae = 0.150639`
- New blocker-best from this probe:
  - `ss_detpitch_aperbranch_energyonly_s2_warm4.step1`
  - `energy_stage5_norm_calibrated_reference_mae = 0.150089`

- Improvement:
  - absolute delta: `-0.000550`
- But this is still not enough to open the route:
  - the gap to threshold remains `0.000089`

## Main conclusion
- The current deterministic line is now clearly in a blocker-aware early-stop regime.
- The valid continuation lesson is:
  - do not continue from the raw `step3` frontier by inertia
  - do not keep longer same-family warm4 blocks after the first useful micro-step
  - if continuation continues at all, use:
    - `step2` as the anchor
    - packet-screened micro-steps
    - and immediate early-stop once blocker energy stops improving
- The route still has not opened fully.
- But the remaining gap is now extremely localized:
  - single record: `target::chapter3_4_firefly_106`
  - single control: `ENERGY`
  - residual gap: `0.000089`

## Decision
- Keep the strongest packet-facing checkpoint on the active deterministic line:
  - `ss_detpitch_aperbranch_energy_warm4.step2`
- Keep the strongest raw deterministic `ENERGY` frontier on the active combined line:
  - `ss_detpitch_aperbranch_energy_warm4.step3`
- Add a new blocker-facing micro-frontier reference:
  - `ss_detpitch_aperbranch_energyonly_s2_warm4.step1`
- Do not treat the later steps of either `ENERGY`-only continuation as new mainline checkpoints.

## Next actions
1. If deterministic continuation resumes, use `ss_detpitch_aperbranch_energyonly_s2_warm4.step1` as the blocker-facing micro-anchor rather than `warm4.step3`.
2. Do not launch another blind multi-step continuation from the raw frontier.
3. The next valid escalation should be one of:
   - packet-screened one-step micro-continuation from the blocker-facing micro-anchor
   - or a more explicit blocker-localized `ENERGY` objective redesign
