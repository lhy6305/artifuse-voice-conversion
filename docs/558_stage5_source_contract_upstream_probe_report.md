# 558 Stage5 Source-Contract Upstream Probe Report

## Summary
- Date: `2026-04-01`
- Goal: continue the post-`557` upstream localization step and test whether the upstream source contract behind `source_scaffold` still contains materially stronger record-generalizable fine waveform geometry than the forwarded Stage5 control package
- Result: the upstream source-contract probe was run on the current full5 review slice; on this route the source contract resolves to `streaming_student_downstream_control_v1` packets rather than the older teacher contract family
- Main conclusion:
  - the current student packet controls remain low-signal for cross-record fine waveform geometry
  - packet-only diagnostics that are not forwarded into `source_scaffold` are also low-signal
  - adding those diagnostics back into the full packet control package still does not open a stronger fine-structure reservoir
  - therefore the missing fine waveform structure is already weak in the available upstream source contract itself, not only after `source_scaffold` repackaging

## Runtime
- Stage5 anchor:
  - `reports/runtime/offline_mvp_nores_vocoder_reviewslice_hardpaircontrol4_templatepushb_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- Dataset index:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- Output:
  - `reports/runtime/stage5_teacher_contract_hidden_probe_reviewslice_full5_templatepushb_hireslogspec_waveform_r1_1/`
- Note:
  - despite the legacy output directory name, the actual probed upstream contract for this review slice is the student packet path pointed to by `source_scaffold.source_contract_path`

## Key Results
- Forwarded control baselines remain low-signal:
  - `selected_dynamic_controls = 0.009515 / 0.012218`
  - `all_available_controls = 0.005871 / 0.003945`
  - `unselected_available_controls = 0.011726 / 0.008911`
  - format above is `linear / mlp`
- Upstream student packet controls are not materially stronger:
  - `source_contract_core_controls = 0.011209 / 0.011934`
  - `source_contract_full_dynamic = 0.008409 / 0.014052`
- Packet-only diagnostics are also weak:
  - `source_contract_diagnostics_family = 0.00583 / -0.000269`
  - `source_contract_controls_plus_diagnostics = 0.006909 / 0.006309`
- Coarse structure still stays strong across these views:
  - `source_contract_core_controls` keeps `logspec = 0.933509`, `rms_corr = 0.998569`, `vuv_accuracy = 0.99937`
  - `source_contract_full_dynamic` keeps `logspec = 0.929844`, `rms_corr = 0.998977`, `vuv_accuracy = 0.99937`
  - `source_contract_diagnostics_family` keeps `logspec = 0.933864`, `rms_corr = 0.999782`, `vuv_accuracy = 0.99786`
- Formal diagnosis:
  - `fine_waveform_geometry_is_already_weak_in_the_available_upstream_source_contract`

## Interpretation
- `557` already showed that `source_scaffold` itself is low-signal.
- `558` closes the next loophole:
  - the student packet content behind that scaffold does not hide a much stronger temporal reservoir in the currently exported control or diagnostic fields
  - packet diagnostics are useful for coarse supervision and auditing, but they do not rescue the missing cross-record fine waveform geometry
- So the next structural question must move earlier again:
  - either into hidden states that are not currently exported by the packet
  - or into the raw source acoustic-state and pitch-provider formation path before the packet is built

## Recommended Next Action
- Probe the non-exported student hidden states directly:
  - `shared_hidden`
  - `control_hidden`
  - `student_hidden`
  - `teacher_hidden_projection`
  - `teacher_fused_hidden_projection`
- If those are also low-signal, then the bottleneck has moved earlier than the current packet-export boundary.
