# 2026-03-28 Stage5 corrected-manifold `wfta005` without `vnc` counterfactual report

## Conclusion
- Ran the first direct counterfactual requested by the current plan:
  - keep `waveform_frames_active_template_weight = 0.05`
  - remove `waveform_decoder_base_logits_voicing_negative_corr_weight`
- Result:
  - this does not preserve the current winner
  - heard-route falls back to the old corrected-manifold anchor level
  - training validation also regresses versus the current winner
- Main decision:
  - do not remove `vnc` from the active winner recipe
  - even though `vnc` looks dormant on late validation in the winner run, it still appears to matter for getting into the better basin during training

## Run
- output:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_step8init_wfta005_novnc_round1_1/`
- init checkpoint:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- dataset:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_corr24_trainval_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
- recipe:
  - `fusion_mode = branch_mean_contrast_residual_v1`
  - `use_residual_shape_branch_condition_adapter = true`
  - `waveform_frames_active_template_weight = 0.05`
  - no `vnc`

## Validation Loss

| run | best step | best validation loss |
| --- | ---: | ---: |
| `anchor_step8_fbmcrs_residualshape` | `8` | `1.311899` |
| `wfta005_novnc_step8` | `8` | `1.268939` |
| `wfta005_with_vnc_step8` | `8` | `1.218598` |

- reading:
  - `wfta005_novnc` is still better than the old corrected-manifold anchor
  - but it gives back a large part of the gain from the current winner
  - `step8` only improves slightly over `step4`:
    `1.308802 -> 1.268939`

## Handoff Comparison

### `decoded_post_ola_gate`

| run | auto_reject | template | centroid_gap_hz | high_band_gap | diagnosis |
| --- | ---: | ---: | ---: | ---: | --- |
| `anchor_step8` | `14` | `0.973165` | `4679.957520` | `0.354575` | `needs_more_localization` |
| `wfta005_novnc_step4` | `14` | `0.973454` | `4555.990723` | `0.344691` | `needs_more_localization` |
| `wfta005_novnc_step8` | `14` | `0.974226` | `4458.160645` | `0.335053` | `needs_more_localization` |
| `wfta005_with_vnc_step8` | `12` | `0.972969` | `4491.603027` | `0.337051` | `needs_more_localization` |

### `decoded_no_gate`

| run | auto_reject | template | centroid_gap_hz | high_band_gap |
| --- | ---: | ---: | ---: | ---: |
| `anchor_step8` | `16` | `0.974278` | `4677.519043` | `0.351795` |
| `wfta005_novnc_step4` | `18` | `0.974585` | `4592.915527` | `0.344099` |
| `wfta005_novnc_step8` | `18` | `0.975373` | `4517.681152` | `0.335447` |
| `wfta005_with_vnc_step8` | `14` | `0.974407` | `4553.846680` | `0.337946` |

- reading:
  - post-gate rejects stay flat at `14/24`
  - no-gate rejects regress to `18/24`
  - the route does not show the winner pattern where late training opens up extra no-gate relief
  - diagnosis still stays at `needs_more_localization`
  - `buzz_before_predicted_activity_gate` remains `false`

## Structure Probe Reading
- probe:
  - `reports/runtime/stage5_waveform_decoder_structure_probe_finetune_corr24_fbmcrs_rs_wfta005_novnc_step8_validation24_gateoff_round1_1/`

| run | decoder_to_base_logits_voicing_jump | decoder_to_base_logits_aper_jump | decoder_to_base_logits_product_jump | waveform_frames_rms_to_voicing_corr |
| --- | ---: | ---: | ---: | ---: |
| `vnc01_maskfix_step8` | `-1.428482` | `-0.015697` | `-0.074409` | `-0.268987` |
| `wfta005_with_vnc_step8` | `+0.151222` | `+0.252332` | `+0.282437` | `+0.862340` |
| `wfta005_novnc_step8` | `-1.654157` | `+0.253980` | `+0.208904` | `-0.811305` |

- collapse summary:
  - `waveform_frames_template_cosine_mean = 0.986312`
  - `decoded_frames_template_cosine_mean = 0.975373`
  - diagnosis:
    `collapse_not_localized_to_waveform_decoder`

- reading:
  - removing `vnc` sends the route back to a strong negative voicing inversion at
    `decoder_hidden -> waveform_decoder_base_logits`
  - the positive late-stage voicing regime seen in the current winner is not reproduced
  - `waveform_frames_rms_to_voicing_corr` also flips back negative, close to the old anchor family

## Interpretation
- `wfta005` alone is real but incomplete:
  - it improves objective value and some spectral gaps versus the old corrected-manifold anchor
  - but it does not produce the heard-route breakthrough by itself
- The current evidence supports this narrower claim:
  - `vnc` is still useful as a training-time basin shaper
  - the reason it looked removable was that the late validation endpoint hid that early role
- This also means the next step should not be another `remove_vnc` attempt.

## Next Step
- Keep `vnc` in the recipe.
- Run a smaller `waveform_frames_active_template_weight` follow-up from the current winner line:
  - first candidate:
    `0.03`
- Goal:
  - keep the `12/24` post-gate and `14/24` no-gate breakthrough if possible
  - reduce the amount of internal regime drift and avoid relying on an unnecessarily strong direct template push
