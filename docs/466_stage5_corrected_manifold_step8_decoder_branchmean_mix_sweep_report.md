# 2026-03-28 Stage5 corrected-manifold `step8` decoder `branch_mean` mix sweep report

## Conclusion
- Re-ran `decoder_branch_mean_mix_alpha` on the current corrected-manifold checkpoint:
  - checkpoint:
    `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
  - dataset:
    `reports/runtime/offline_mvp_nores_vocoder_dataset_corr24_trainval_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
  - split:
    `validation`
  - sample count:
    `24`
- Sweep points:
  - `alpha = 0.00`
  - `alpha = 0.15`
  - `alpha = 0.30`
  - `alpha = 0.50`
- Result:
  - all four runs remain `24/24 auto_reject`
  - all four runs keep the same diagnosis:
    `buzz_present_by_waveform_frames_before_gate`
  - predicted activity gate still does not change rejection status
- Interpretation:
  - the corrected-manifold checkpoint is directionally responsive to decoder-side branch-mean mixing
  - but the response is still too weak to break the current Stage5 attractor
  - this does **not** justify another same-family mix sweep

## Code Change
- Added inference-time `decoder_branch_mean_mix_alpha` support to:
  - `analyze-stage5-nores-waveform-handoff`
  - `src/v5vc/stage5_waveform_handoff_probe.py`
  - `src/v5vc/cli.py`
- Scope:
  - probe-only plumbing
  - no training-path behavior changed

## Runs
- `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_step8_mix000_round1_1/`
- `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_step8_mix015_round1_1/`
- `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_step8_mix030_round1_1/`
- `reports/runtime/stage5_waveform_handoff_probe_finetune_corr24_step8_mix050_round1_1/`

## Aggregate Comparison

### `decoded_post_ola_gate`

| alpha | auto_reject | template | rms_corr | centroid_gap_hz | high_band_gap |
| --- | ---: | ---: | ---: | ---: | ---: |
| `0.00` | `24` | `0.920997` | `0.892176` | `8774.619141` | `0.660415` |
| `0.15` | `24` | `0.918552` | `0.892096` | `8765.596680` | `0.657188` |
| `0.30` | `24` | `0.914204` | `0.892803` | `8813.158203` | `0.655720` |
| `0.50` | `24` | `0.903889` | `0.897108` | `9091.202148` | `0.664367` |

### `decoded_no_gate`

| alpha | template | centroid_gap_hz | high_band_gap |
| --- | ---: | ---: | ---: |
| `0.00` | `0.924694` | `9254.138672` | `0.700916` |
| `0.15` | `0.921990` | `9247.323242` | `0.698858` |
| `0.30` | `0.917419` | `9278.309570` | `0.697595` |
| `0.50` | `0.907318` | `9452.627930` | `0.701246` |

## Stage Localization
- `fused_hidden_template_cosine_mean` stays fixed at `0.948296` across the sweep.
- `decoder_hidden_template_cosine_mean` moves with `alpha`:
  - `0.948296 -> 0.946734 -> 0.944592 -> 0.940868`
- `waveform_frame_logits_template_cosine_mean` and `waveform_frames_template_cosine_mean` also drop with `alpha`, but not enough to open route:
  - logits template:
    `0.951354 -> 0.949593 -> 0.946468 -> 0.938553`
  - frames template:
    `0.949051 -> 0.947264 -> 0.944113 -> 0.936326`
- Diagnosis remains unchanged:
  - `buzz_before_predicted_activity_gate = true`
  - `predicted_activity_gate_changes_auto_reject_status = false`
  - `primary_localization = buzz_present_by_waveform_frames_before_gate`

## Reading
- `alpha = 0.15` is the best centroid point.
- `alpha = 0.30` is the best high-band point.
- `alpha = 0.50` pushes template lower the most, but clearly over-tilts brightness/centroid back in the wrong direction.
- None of the points produce a categorical change.

## Decision
- Do not continue same-family `decoder_branch_mean_mix_alpha` micro-sweeps on corrected-manifold `step8`.
- Treat this run as confirmation that:
  - branch-mean direction is still real
  - linear decoder-side mixing is still insufficient
- Next mechanism work should stay at the stronger level:
  - `fusion_mode`
  - `branch_condition_adapter`
  - other non-linear / structured decoder-path interventions
