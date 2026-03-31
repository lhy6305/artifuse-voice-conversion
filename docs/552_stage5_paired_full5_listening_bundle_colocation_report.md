# Stage5 Paired Full5 Listening Bundle Colocation Report

## Summary
- Date: `2026-03-31`
- Goal: materialize the next human A/B review as a single-root bundle instead of leaving audio, spectrograms, and sidecar manifests scattered across multiple runtime directories
- Result: a new colocated full5 paired listening bundle now exists for `templatepushb` vs `dynamicheadsmokea`, and all current hearing assets for that A/B are copied into one directory tree

## New Bundle
- Root:
  - `reports/runtime/stage5_paired_listening_spectrogram_review_bundle_reviewslice_full5_templatepushb_vs_dynamicheadsmokea_round1_1`
- Summary files:
  - `stage5_paired_full5_listening_spectrogram_review_bundle.json`
  - `stage5_paired_full5_listening_spectrogram_review_bundle.md`
- Layout:
  - `manifests/`
  - `records/`

## What Is Included
- Under `records/<record_id>/aligned/`
  - `aligned_target.wav`
  - `aligned.linear_spectrogram.png`
- Under `records/<record_id>/templatepushb/`
  - `decoded.wav`
  - `audit_proxy.wav`
  - `decoded.linear_spectrogram.png`
- Under `records/<record_id>/dynamicheadsmokea/`
  - `decoded.wav`
  - `audit_proxy.wav`
  - `decoded.linear_spectrogram.png`
- Under `manifests/`
  - copied export json/md for both variants
  - copied source-filter review json/md for both variants
  - existing `templatepushb` listening-bundle json/md
  - `dynamicheadsmokea` structure-probe json/md

## Current A/B Sidecars
- `templatepushb`
  - `decoded_template_cosine_mean = 0.968295`
  - `decoded_vuv_high_band_ratio_mean = 0.111866`
  - `0/5 auto_reject + 5/5 review_required`
- `dynamicheadsmokea`
  - `decoded_template_cosine_mean = 0.965387`
  - `decoded_vuv_high_band_ratio_mean = 0.121464`
  - `0/5 auto_reject + 5/5 review_required`

## Process Update
- The project now has a reusable helper:
  - `scripts/build_stage5_paired_listening_bundle.ps1`
- It builds a single-root paired bundle from:
  - two export manifests
  - two source-filter review manifests
  - optional listening-bundle manifests
  - optional structure-probe manifests

## Next Action
- Human review should now happen from the colocated root above rather than from the scattered source runtime directories
- The review question remains narrow:
  - does `dynamicheadsmokea` add any record-specific audible or visible structure beyond `templatepushb`
  - or is it still the same pure-buzz basin with only minor machine-side shifts
