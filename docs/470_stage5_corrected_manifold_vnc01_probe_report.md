# 2026-03-28 Stage5 corrected-manifold `vnc01` probe report

## Conclusion
- Promoted the corrected-manifold structure diagnosis into a real finetune:
  - anchor init:
    `corr24 fbmcrs + residualshape step8`
  - added loss:
    `waveform_decoder_base_logits_voicing_negative_corr = 0.1`
- Training objective improved again:
  - anchor best validation:
    `1.311899`
  - `bhb01` best validation:
    `1.253358`
  - `vnc01` best validation:
    `1.222884`
- But handoff did not break the current corrected-manifold barrier:
  - anchor `decoded_post_ola_gate auto_reject = 14/24`
  - `vnc01 step4 = 14/24`
  - `vnc01 step8 = 14/24`
- It also regressed `decoded_no_gate`:
  - anchor `16/24`
  - `vnc01 step8 = 18/24`
- Structure probe confirms why:
  - the dominant coupling is still
    `decoder_hidden -> waveform_decoder_base_logits`
  - strongest jump remains the voicing sign flip
  - the new loss was effectively inactive during training because
    `waveform_decoder_base_logits_to_voicing_active_zero_corr`
    stayed positive on the training/validation batches
- So this round is a negative result on mechanism efficacy:
  - `vnc01` improves optimization metrics
  - it does not improve heard-route localization
  - it does not actually hit the failure mode exposed by the dataset-side structure probe

## Training Run
- output:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_vnc01_round1_1/`
- init checkpoint:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- dataset:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_corr24_trainval_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- setup:
  - `num_steps = 8`
  - `packages_per_step = 6`
  - `validation_interval = 4`
  - `checkpoint_interval = 4`
  - `learning_rate = 1e-4`
  - `fusion_mode = branch_mean_contrast_residual_v1`
  - `use_residual_shape_branch_condition_adapter = true`
  - `residual_shape_branch_condition_mode = raw_additive_v1`
  - extra loss:
    `waveform_decoder_base_logits_voicing_negative_corr = 0.1`

## Validation

| run | best step | best validation loss |
| --- | ---: | ---: |
| `corr24_step8_fbmcrs_residualshape` | `8` | `1.311899` |
| `corr24_step8_fbmcrs_residualshape_bhb01` | `8` | `1.253358` |
| `corr24_step8_fbmcrs_residualshape_vnc01` | `8` | `1.222884` |

## Handoff Comparison

### `decoded_post_ola_gate`

| run | auto_reject | template | rms_corr | centroid_gap_hz | high_band_gap | diagnosis |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `anchor_step8` | `14` | `0.973165` | `0.907448` | `4679.957520` | `0.354575` | `needs_more_localization` |
| `vnc01_step4` | `14` | `0.973526` | `0.907143` | `4555.134277` | `0.344615` | `needs_more_localization` |
| `vnc01_step8` | `14` | `0.974312` | `0.905943` | `4454.031738` | `0.334683` | `needs_more_localization` |

### `decoded_no_gate`

| run | auto_reject | template | rms_corr | centroid_gap_hz | high_band_gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| `anchor_step8` | `16` | `0.974278` | `0.755193` | `4677.519043` | `0.351795` |
| `vnc01_step4` | `18` | `0.974653` | `0.738668` | `4591.908203` | `0.344013` |
| `vnc01_step8` | `18` | `0.975453` | `0.727690` | `4514.878906` | `0.335126` |

### Handoff Stage Aggregates

| run | logits_template | frames_template | logits_abs_ge_1 | frames_abs_ge_095 |
| --- | ---: | ---: | ---: | ---: |
| `anchor_step8` | `0.987227` | `0.985322` | `0.067440` | `0.007914` |
| `vnc01_step4` | `0.987792` | `0.985934` | `0.067997` | `0.007797` |
| `vnc01_step8` | `0.988202` | `0.986409` | `0.069025` | `0.007283` |

## What The New Loss Actually Did
- The new scalar was wired correctly and recorded in training summaries.
- But across the recorded batches:
  - `loss_waveform_decoder_base_logits_voicing_negative_corr_relu = 0.0`
  - `waveform_decoder_base_logits_to_voicing_active_zero_corr`
    stayed positive, roughly in the `0.68 - 0.91` range
- Interpretation:
  - this loss only activates when active-frame zero-lag voicing correlation goes negative
  - that negative state is visible in dataset-side structure probes
  - but it is not appearing on the per-batch training statistic used by this objective
  - so the regularizer is too sparse or too indirect to move the actual failure basin

## Structure Probe Reading
- probe:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_finetune_corr24_fbmcrs_rs_vnc01_step8_validation24_gateoff_round1_1/`
- `vnc01 step8` baseline summary:
  - `fused_hidden_template = 0.957061`
  - `waveform_frames_template = 0.986409`
  - `fused_to_waveform_template_gap = 0.029348`
- dominant coupling remains:
  - `strongest_transition = decoder_to_base_logits`
  - `strongest_transition_score = 1.649919`
- key jumps:
  - `decoder_to_base_logits_voicing_corr_jump = -1.649919`
  - `decoder_to_base_logits_abs_aper_corr_jump = +0.259563`
  - `decoder_to_base_logits_abs_aper_energy_product_corr_jump = +0.213730`
  - `decoder_to_base_logits_uv_v_rms_jump = -0.173411`

### Comparison vs previous corrected-manifold anchors

| run | fused_hidden_template | frames_template | template_gap | voicing_jump | aper_jump | product_jump |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `anchor_step8` | `0.956970` | `0.985322` | `0.028352` | `-1.751059` | `+0.134542` | `+0.112305` |
| `bhb01_step8` | `0.957257` | `0.986569` | `0.029312` | `-1.651879` | `+0.256149` | `+0.212693` |
| `vnc01_step8` | `0.957061` | `0.986409` | `0.029348` | `-1.649919` | `+0.259563` | `+0.213730` |

- Reading:
  - `vnc01` weakens the voicing jump slightly versus the original anchor
  - but it does so while moving the route into essentially the same template-heavy operating region as `bhb01`
  - in practice this means:
    better validation and slightly better brightness metrics are being bought by the wrong internal trade
  - the heard-route barrier does not move

## Decision
- Keep the code support for `waveform_decoder_base_logits_voicing_negative_corr_weight`.
- Do not continue with more weight scans on this exact loss.
- The next mechanism step should be a stronger signed-structure objective that cannot stay dormant on the current batches:
  - either directly target the dataset-level `decoder_to_base_logits_voicing_corr_jump`
  - or supervise a stronger voiced-vs-unvoiced separation / signed correlation statistic on `waveform_decoder_base_logits`
- Also keep using `corr24 fbmcrs + residualshape step8` as the corrected-manifold mechanism anchor.

## Artifacts
- training summary:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_vnc01_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.md`
- step4 handoff:
  - `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_vnc01_step4_round1_1/stage5_waveform_handoff_probe.json`
- step8 handoff:
  - `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_vnc01_step8_round1_1/stage5_waveform_handoff_probe.json`
- step8 structure probe:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_finetune_corr24_fbmcrs_rs_vnc01_step8_validation24_gateoff_round1_1/stage5_waveform_decoder_structure_probe.json`
