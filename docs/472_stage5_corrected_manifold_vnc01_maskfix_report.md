# 2026-03-28 Stage5 corrected-manifold `vnc01` mask-fix report

## Conclusion
- Resolved the real reason the first `vnc01` line failed to engage:
  - the training loss was multiplying both sequences by `frame_activity_target`
  - that weighting flipped the signed correlation and hid the negative-corr failure mode
- After changing the loss to use `frame_activity_target` only as an active-frame mask, the voicing regularizer immediately became active:
  - smoke validation:
    `waveform_decoder_base_logits_to_voicing_active_zero_corr = -0.878450`
  - the old dormant version had reported positive values around `+0.79`
- Then I ran a full corrected-manifold 8-step finetune from the same anchor.
- Mechanism-side result:
  - it materially reduced the internal coupling error
  - especially at `decoder_hidden -> waveform_decoder_base_logits`
- Heard-route result:
  - still no breakthrough
  - `step4` only ties the current anchor
  - `step8` regresses slightly

## Training Run
- output:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_vnc01_maskfix_round1_1/`
- init checkpoint:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- dataset:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_corr24_trainval_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- setup:
  - same `fbmcrs + residualshape` 8-step recipe
  - extra loss:
    `waveform_decoder_base_logits_voicing_negative_corr = 0.1`
  - corrected semantics:
    active-frame mask only, no multiplicative weighting by `frame_activity_target`

## Validation

| run | best step | best validation loss |
| --- | ---: | ---: |
| `anchor_step8` | `8` | `1.311899` |
| `vnc01_dormant_step8` | `8` | `1.222884` |
| `vnc01_maskfix_step8` | `8` | `1.242400` |

- Reading:
  - mask-fix is worse than the dormant version on the training objective
  - but still better than the original anchor
  - this is consistent with the loss now applying real pressure instead of silently doing nothing

## Handoff Comparison

### `decoded_post_ola_gate`

| run | auto_reject | template | rms_corr | centroid_gap_hz | high_band_gap | diagnosis |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `anchor_step8` | `14` | `0.973165` | `0.907448` | `4679.957520` | `0.354575` | `needs_more_localization` |
| `vnc01_maskfix_step4` | `14` | `0.973488` | `0.907238` | `4560.591797` | `0.345170` | `needs_more_localization` |
| `vnc01_maskfix_step8` | `15` | `0.974073` | `0.906457` | `4451.310547` | `0.334622` | `needs_more_localization` |

### `decoded_no_gate`

| run | auto_reject | template | rms_corr | centroid_gap_hz | high_band_gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| `anchor_step8` | `16` | `0.974278` | `0.755193` | `4677.519043` | `0.351795` |
| `vnc01_maskfix_step4` | `18` | `0.974625` | `0.745823` | `4596.396484` | `0.344502` |
| `vnc01_maskfix_step8` | `19` | `0.975258` | `0.759468` | `4504.020020` | `0.334638` |

### Handoff Stage Aggregates

| run | logits_template | frames_template | logits_abs_ge_1 | frames_abs_ge_095 |
| --- | ---: | ---: | ---: | ---: |
| `anchor_step8` | `0.987227` | `0.985322` | `0.067440` | `0.007914` |
| `vnc01_maskfix_step4` | `0.987752` | `0.985890` | `0.068838` | `0.007768` |
| `vnc01_maskfix_step8` | `0.988032` | `0.986222` | `0.070867` | `0.007819` |

## Why This Matters
- The signed loss now clearly hits the intended basin.
- But removing the internal voicing inversion is not sufficient by itself to improve the heard route.
- What changed is mostly internal coupling quality, not the final template-heavy operating point.

## Structure Probe Reading
- probe:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_finetune_corr24_fbmcrs_rs_vnc01_maskfix_step8_validation24_gateoff_round1_1/`

### Baseline summary
- `fused_hidden_template = 0.957332`
- `waveform_frames_template = 0.986222`
- `fused_to_waveform_template_gap = 0.028890`

### Coupling comparison

| run | decoder_to_base_logits_voicing_jump | decoder_to_base_logits_aper_jump | decoder_to_base_logits_product_jump | waveform_frames_rms_to_voicing_corr |
| --- | ---: | ---: | ---: | ---: |
| `anchor_step8` | `-1.751059` | `+0.134542` | `+0.112305` | `-0.813209` |
| `vnc01_dormant_step8` | `-1.649919` | `+0.259563` | `+0.213730` | `-0.813209` |
| `vnc01_maskfix_step8` | `-1.428482` | `-0.015697` | `-0.074409` | `-0.268987` |
- reading:
  - mask-fix meaningfully reduces the decoder-to-base-logits voicing sign flip
  - it also neutralizes the aper/product re-projection that had become stronger on the dormant run
  - by the time we reach `waveform_frames`, voicing correlation is far less inverted than before
- but:
  - the route still lands in a template-heavy heard basin
  - the main diagnosis remains `needs_more_localization`

## Smoke Confirmation
- smoke output:
  - `reports/runtime/tmp_offline_mvp_nores_vocoder_dataset_finetune_corr24_fbmcrs_rs_vnc01_maskfix_smoke_round1_1/`
- key smoke confirmation:
  - `loss_waveform_decoder_base_logits_voicing_negative_corr_relu = 0.878450`
  - `waveform_decoder_base_logits_to_voicing_active_zero_corr = -0.878450`

## Decision
- Keep the mask-fix in the codebase.
- Retire the old interpretation that `vnc01` simply “does not activate”.
- Also retire the idea that fixing `decoder_to_base_logits` voicing inversion alone is enough.
- The next step should move one level closer to the heard route:
  - preserve the internal coupling gains from mask-fixed `vnc`
  - add a direct localization / template operating-point objective on `waveform_frames` or decoded frames
  - do not continue scanning the same standalone `vnc` weight

## Artifacts
- training summary:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_vnc01_maskfix_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.md`
- step4 handoff:
  - `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_vnc01_maskfix_step4_round1_1/stage5_waveform_handoff_probe.json`
- step8 handoff:
  - `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_vnc01_maskfix_step8_round1_1/stage5_waveform_handoff_probe.json`
- step8 structure probe:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_finetune_corr24_fbmcrs_rs_vnc01_maskfix_step8_validation24_gateoff_round1_1/stage5_waveform_decoder_structure_probe.json`
