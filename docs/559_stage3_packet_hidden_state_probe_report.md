# 559 Stage3 Packet Hidden-State Probe Report

## Summary
- Date: `2026-04-01`
- Goal: continue the post-`558` upstream localization step and test whether the non-exported student hidden states behind the current packet exporter still contain materially stronger cross-record fine waveform geometry than the exported packet contract
- Result: a direct hidden-state oracle probe was run by replaying the active Stage3 checkpoint on the exact full5 review-slice records behind the current Stage5 packages
- Main conclusion:
  - the current student hidden states also remain near zero for cross-record fine waveform geometry
  - no hidden stage materially outperforms the already weak exported packet contract
  - therefore the main missing fine structure is not simply trapped inside an unexported hidden-state reservoir right behind the packet boundary

## Runtime
- Stage3 checkpoint:
  - `reports/training/ss_detpitch_energypeak_s2_step1/checkpoints/ss_detpitch_energypeak_s2_step1.step1.pt`
- Review-slice package index:
  - `reports/runtime/stage5_review_slice_dataset_index_streaming_student_energypeak_fusionresshape050_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- Output:
  - `reports/runtime/stage3_packet_hidden_state_probe_reviewslice_full5_templatepushb_hireslogspec_waveform_r1_1/`

## Key Results
- Best cross-record hidden-stage waveform scores remain near zero:
  - `shared_hidden = 0.009423 / 0.00692`
  - `control_hidden = 0.007309 / 0.008088`
  - `student_hidden = 0.006876 / 0.00962`
  - `teacher_hidden_projection = 0.007502 / 0.005465`
  - `teacher_fused_hidden_projection = 0.005777 / 0.006242`
  - `f0_branch_hidden = 0.007107 / 0.00889`
  - format above is `linear / mlp`
- Coarse structure still remains strong:
  - log-spectrum cosine stays around `0.930` to `0.935`
  - RMS correlation stays around `0.9996` to `0.9999`
- Hidden-state reading:
  - best linear hidden stage is only `shared_hidden = 0.009423`
  - best hidden MLP stage is only `student_hidden = 0.00962`
  - both are still below even the already weak `558` packet-control frontier

## Interpretation
- This probe closes the “maybe the packet exporter dropped a strong hidden reservoir” story.
- On the active Stage3 checkpoint:
  - `shared_hidden` is weak
  - `control_hidden` is weak
  - `student_hidden` is weak
  - teacher-facing projection heads are weak
- So the current missing fine structure has moved earlier than the packet-export boundary and earlier than the currently observed student hidden-state family itself.

## Recommended Next Action
- Move one step earlier again into the current frontend inputs and source acoustic-state formation path.
- The next valid question is:
  - whether raw packet reference controls, pitch-provider inputs, or frontend raw control families still contain materially stronger fine waveform geometry than the hidden states and exported packet contract
