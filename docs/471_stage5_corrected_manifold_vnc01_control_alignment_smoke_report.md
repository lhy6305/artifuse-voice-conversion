# 2026-03-28 Stage5 corrected-manifold `vnc01` control-alignment smoke report

## Conclusion
- Followed up the failed `vnc01` finetune with a training-side semantics check.
- Found a real target-definition mismatch:
  - structure probe `voicing_control` used
    `vuv_target / voiced_proxy_target / (1 - aper)`
  - training-side `vnc01` loss had been using
    `periodic_gate_target = max(vuv, p_voicing)`
- Patched the training loss to use the same control-resolution order as the structure probe.
- Then reran a 1-step smoke plus full validation.
- Result:
  - the loss still stayed fully dormant
  - validation-wide
    `loss_waveform_decoder_base_logits_voicing_negative_corr_relu = 0.0`
  - validation-wide
    `waveform_decoder_base_logits_to_voicing_active_zero_corr`
    remained positive across all 24 records
- So the updated conclusion is stronger than before:
  - the problem is not just target-definition mismatch
  - `negative-corr-only` is structurally too weak for the current corrected-manifold basin
  - the next step should be a stronger signed objective such as
    a positive correlation floor / target
    or a direct voiced-vs-unvoiced separation objective on `waveform_decoder_base_logits`

## Code Change
- training-side `vnc01` supervision now resolves voicing targets with the same precedence as the structure probe:
  - `vuv_target`
  - `voiced_proxy_target`
  - `1 - aper_target`
  - `1 - aperiodicity_proxy_target`
  - fallback only then to `periodic_gate_target`

## Smoke Run
- output:
  - `reports/runtime/tmp_offline_mvp_nores_vocoder_dataset_finetune_corr24_fbmcrs_rs_vnc01_probealigned_smoke_round1_1/`
- init checkpoint:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_finetune_corr24_fusionbranchmeancontrast_residualshape_round1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step8.pt`
- setup:
  - same `fbmcrs + residualshape` recipe
  - `num_steps = 1`
  - `packages_per_step = 2`
  - `waveform_decoder_base_logits_voicing_negative_corr = 0.1`

## Result
- training step:
  - `loss_total = 1.465234`
- validation:
  - `loss_total = 1.295864`
- key observation:
  - `loss_waveform_decoder_base_logits_voicing_negative_corr_relu = 0.0`
  - `waveform_decoder_base_logits_to_voicing_active_zero_corr = 0.795182`
- per-record validation stats stayed positive as well, roughly in the `0.68 - 0.91` range.

## Decision
- Keep the semantic alignment patch.
- Do not spend more runs on the current `relu(-corr)` form.
- Next mechanism iteration should supervise something that remains active inside the present basin:
  - positive correlation floor / target on the probe-aligned voicing control
  - or direct signed separation between voiced and unvoiced frame RMS / spectrum at `waveform_decoder_base_logits`

## Artifacts
- smoke summary:
  - `reports/runtime/tmp_offline_mvp_nores_vocoder_dataset_finetune_corr24_fbmcrs_rs_vnc01_probealigned_smoke_round1_1/offline_mvp_nores_vocoder_dataset_loop.summary.md`
