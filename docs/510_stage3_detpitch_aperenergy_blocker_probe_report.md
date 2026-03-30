# Stage3 deterministic APER plus ENERGY blocker probe report

## Summary
- A minimal blocker-oriented deterministic probe was run from the stable packet-facing anchor:
  - `cont20.step2`
- Probe design:
  - keep the existing dedicated `ENERGY` branch
  - unfreeze `frontend.aper_head`
  - unfreeze `student.aper_branch_delta_head`
  - add nonzero `teacher_aper_state` supervision
- New config:
  - `configs/streaming_student_stage_parallel_control_branch_controlfamily_detpitch_nof0corr_aperenergyfreeze_v1.json`
- New loss weights:
  - `configs/streaming_student_loss_weights_detpitch_aperenergy_stage5calib_v1.json`
- Main result:
  - the probe does not fix the remaining `APER` blocker
  - but it preserves the current `2/3` route opening
  - and it improves the raw deterministic `ENERGY` frontier further to `0.114704` at step `3`

## Training and packet results
- Training output:
  - `reports/training/ss_detpitch_aperenergy_cont20s2_warm4`
- Packet selector:
  - `reports/runtime/ss_pktsel_detpitch_aperenergy_cont20s2_warm4/streaming_student_packet_checkpoint_selection.json`

| step | auto reject | all-core ready | aper ready | energy ready | avg aper calibrated mae | avg energy calibrated mae |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 2 | 1 | 2 | 1 | 0.282772 | 0.164968 |
| 2 | 1 | 2 | 2 | 2 | 0.282621 | 0.151246 |
| 3 | 1 | 2 | 2 | 2 | 0.282341 | 0.114704 |
| 4 | 1 | 2 | 2 | 2 | 0.282042 | 0.134397 |

- Packet-facing selector top-1:
  - step `2`
- Raw deterministic `ENERGY` best:
  - step `3`

## Comparison against the previous frontier
- Previous packet-facing anchor:
  - `cont20.step2`
- Previous raw deterministic `ENERGY` frontier:
  - `cont20.step3`
- This probe keeps the same route-opening counts:
  - `aper_ready_count = 2/3`
  - `energy_ready_count = 2/3`
  - `all_core_controls_ready_count = 2/3`
- It does not open the third record.
- But it does improve the family-level raw energy frontier:
  - previous best: `0.120149` at `cont20.step3`
  - new best: `0.114704` at blocker probe step `3`

## Blocker record: `target::chapter3_4_firefly_106`
- The blocker still fails both `APER` and `ENERGY`.
- But the two controls behave very differently.

### APER
- `APER` remains structurally blocked under this minimal probe.

| checkpoint | aper raw mae | aper calibrated mae | aper raw std | aper raw corr |
| --- | ---: | ---: | ---: | ---: |
| cont20.step3 | 0.400666 | 0.401752 | 0.012522 | -0.093274 |
| blocker step3 | 0.401224 | 0.403249 | 0.013480 | -0.037728 |

- Reading:
  - raw APER is still nearly flat
  - correlation is still effectively unusable
  - affine calibration still cannot bring APER close to the `0.3` gate
  - the blocker probe therefore does not provide evidence that the current APER scaffold is sufficient

### ENERGY
- `ENERGY` still improves on the same blocker record.

| checkpoint | energy raw mae | energy calibrated mae | energy raw std | energy raw corr |
| --- | ---: | ---: | ---: | ---: |
| cont20.step3 | 0.328854 | 0.165880 | 0.096728 | 0.871793 |
| blocker step3 | 0.292883 | 0.151327 | 0.135682 | 0.890789 |

- Reading:
  - `ENERGY` is still a healthy learned control on this record
  - the blocker probe pushes it to within about `0.001327` of the packet threshold `0.15`
  - this confirms that the remaining hard gap is no longer mainly on the energy side

## Main conclusion
- The minimal APER-unfreeze probe answered the key question:
  - the current line does not fail because APER was merely forgotten by freeze
  - even after unfreezing the existing APER head and correction head, the blocker record APER still stays structurally flat and non-ready
- At the same time, the probe shows that:
  - the existing deterministic line can still improve `ENERGY`
  - and can do so without losing the current `2/3` opening
- Therefore the next deterministic escalation should not be another generic continuation.
- The next valid move should target APER more explicitly than the current scaffold allows.

## Decision
- Keep `cont20.step2` as the current packet-facing checkpoint.
- Keep blocker probe step `3` as the newest raw deterministic `ENERGY` frontier reference.
- Do not treat this probe as an APER solution.
- Reframe the deterministic blocker as:
  - primary unresolved control: `APER`
  - secondary near-threshold control: `ENERGY`

## Next actions
1. Do not open another generic continuation from the new raw energy-best by inertia.
2. If deterministic work continues, design the next probe around APER-specific capacity or APER-specific objective routing.
3. Keep explicit blocker-localized reading for `target::chapter3_4_firefly_106` in the next report, because family-average metrics now hide the real remaining failure mode.
