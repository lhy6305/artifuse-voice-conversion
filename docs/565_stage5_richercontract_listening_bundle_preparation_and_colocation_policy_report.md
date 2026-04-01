# 565 Stage5 Richer-Contract Listening Bundle Preparation And Colocation Policy Report

## Summary
- Date: `2026-04-01`
- Goal: prepare the first human listening A/B for the richer-contract regularized route and formalize the required artifact-colocation policy for future listening audits
- Result:
  - exported both current listening candidates on the held-out minisplit validation records
  - replayed source-filter review on the exported audio
  - colocated audio, spectrograms, and current machine sidecars into one single-root paired bundle
  - extended the paired-bundle helper so `speech-emergence json/md` now get copied into `manifests/` alongside export and source-filter-review sidecars
- Main conclusion:
  - the task is now at a real human listening stop
  - the next decision should be made from the new colocated bundle root, not from scattered runtime directories

## Listening Candidates
- Left:
  - `baseline39`
  - checkpoint:
    - `reports/runtime/stage5_richercontract_minisplit_warmstart40_r1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step39.pt`
- Right:
  - `combo20`
  - checkpoint:
    - `reports/runtime/stage5_richercontract_minisplit_warmstart40_rmsguard02_bhb01_r1_1/checkpoints/offline_mvp_nores_vocoder_dataset_loop.step20.pt`
- Record scope:
  - `target::chapter3_30_firefly_132`
  - `target::no_text_voice/chapter3_21_firefly_108`

## New Bundle
- Root:
  - `reports/runtime/stage5_paired_listening_spectrogram_review_bundle_richercontract_minisplit_baseline39_vs_combo20_round1_1/`
- Bundle summaries:
  - `stage5_paired_full5_listening_spectrogram_review_bundle.json`
  - `stage5_paired_full5_listening_spectrogram_review_bundle.md`
- Layout:
  - `manifests/`
  - `records/`

## What Is Included
- Under `records/<record_id>/aligned/`
  - `aligned_target.wav`
  - `aligned.linear_spectrogram.png`
- Under `records/<record_id>/baseline39/`
  - `decoded.wav`
  - `audit_proxy.wav`
  - `decoded.linear_spectrogram.png`
- Under `records/<record_id>/combo20/`
  - `decoded.wav`
  - `audit_proxy.wav`
  - `decoded.linear_spectrogram.png`
- Under `manifests/`
  - `baseline39.nores_vocoder_audio_export.json/md`
  - `combo20.nores_vocoder_audio_export.json/md`
  - `baseline39.stage5_source_filter_review.json/md`
  - `combo20.stage5_source_filter_review.json/md`
  - `baseline39.stage5_speech_emergence_probe.json/md`
  - `combo20.stage5_speech_emergence_probe.json/md`

## Listening Focus
- Primary question:
  - does `combo20` sound less over-loud and less harsh than `baseline39` while preserving or improving any speech-like local structure
- Secondary question:
  - does the regularized route merely darken the buzz, or does it actually make the waveform feel more localized and less template-like
- Suggested order:
  - first `target::chapter3_30_firefly_132`
    - strongest current held-out speech-like candidate
  - then `target::no_text_voice/chapter3_21_firefly_108`
    - stress test for low-energy and overshoot behavior

## Process Update
- Updated helper:
  - `scripts/build_stage5_paired_listening_bundle.ps1`
- New rule:
  - every future Stage5 listening audit should be handed off as one colocated bundle root
  - that root must already contain:
    - all listening audio
    - all paired spectrograms
    - all current review-relevant `json/md` sidecars used for the handoff decision

## Colocation Policy
- Required root layout:
  - `records/` for all per-record listening assets
  - `manifests/` for copied machine sidecars
  - bundle summary `json/md` at the root
- Required per-record layout:
  - shared aligned target under `aligned/`
  - one subdirectory per compared variant
- Required manifest scope for a listening handoff:
  - audio export `json/md`
  - source-filter review `json/md`
  - speech-emergence `json/md`
  - any other current machine artifact explicitly cited in the handoff decision
- Handoff rule:
  - when human listening becomes the next critical-path step, do not ask the user to reconstruct the comparison from multiple runtime folders
  - give the single bundle root directly

## Decision
- The richer-contract line is now paused for human listening.
- Do not run another scalar-only training continuation before this A/B is heard.
- The correct next action is manual review from the new bundle root above.
