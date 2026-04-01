# 560 Stage3 Frontend-Input Probe Report

## Summary
- Date: `2026-04-01`
- Goal: continue the post-`559` upstream localization step and test whether the current raw frontend-input families still contain materially stronger fine waveform geometry than the weak packet hidden states and exported contract
- Result: a frontend-input oracle probe was run over the same full5 review slice, covering packet reference controls, pitch-provider inputs, and the raw frontend control family
- Main conclusion:
  - the raw frontend and source-acoustic families are slightly stronger than the packet hidden states
  - but they are still far below any convincing fine waveform regime
  - therefore the whole currently available source-acoustic and Stage3 packet formation path remains intrinsically low-signal for the missing cross-record fine waveform detail

## Runtime
- Review-slice package index:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- Output:
  - `reports/runtime/stage3_frontend_input_probe_reviewslice_full5_templatepushb_hireslogspec_waveform_r1_1/`

## Key Results
- Best available upstream input family is still sub-threshold:
  - `packet_reference_controls = 0.02178 / 0.014518`
  - `pitch_provider_family = 0.020932 / 0.016573`
  - `frontend_raw_control_family = 0.006395 / 0.004273`
  - format above is `linear / mlp`
- Coarse structure remains strong enough for broad control reconstruction:
  - `packet_reference_controls` keeps `logspec = 0.931473`, `rms_corr = 0.885081`, `vuv_accuracy = 0.997344`
  - `pitch_provider_family` keeps `logspec = 0.925801`, `rms_corr = 0.574591`, `vuv_accuracy = 0.997942`
  - `frontend_raw_control_family` keeps `logspec = 0.931446`, `rms_corr = 0.999853`, `vuv_accuracy = 0.997909`
- Relative reading:
  - source-acoustic reference and pitch-provider families are somewhat stronger than the packet hidden states from `559`
  - but they still stay in the `~0.02` regime, well below any route-opening fine-structure level
  - the frontend raw control family is not a hidden stronger reservoir either

## Interpretation
- `558` showed that the exported student packet contract is low-signal.
- `559` showed that the immediately upstream student hidden states are also low-signal.
- `560` now bounds the next earlier family:
  - even the available raw source-acoustic reference controls and pitch-provider inputs remain only weakly informative for cross-record fine waveform geometry
  - the current Stage3/Stage5 interface is therefore not merely failing to preserve a strong upstream temporal reservoir
  - the currently available upstream reservoir itself is weak

## Decision
- Keep:
  - the conclusion that the bottleneck is now earlier than Stage5-local consumer structure
  - the conclusion that the current student packet exporter is not hiding a strong omitted temporal reservoir
- Stop treating as the default next move:
  - more Stage5-local control-subset reshuffling
  - more packet-export field juggling
  - another story that only one omitted hidden tensor is blocking the route

## Recommended Next Action
- The next work is no longer another same-style localization replay.
- The next valid structural move is to redesign upstream representation formation or supervision, for example:
  - expose a richer source-acoustic contract than the current scalar control family
  - or add a dedicated fine-structure-bearing upstream representation instead of expecting the current Stage3 packet family to carry that detail implicitly
