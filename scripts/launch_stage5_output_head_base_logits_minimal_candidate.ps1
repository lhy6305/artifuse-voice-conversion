param(
  [string]$DatasetIndex = "reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_contractv2_normfix_round1_1/offline_mvp_nores_vocoder_dataset_index.json",
  [string]$OutputDir = "",
  [string]$Device = "cuda:0",
  [int]$NumSteps = 24,
  [int]$PackagesPerStep = 4,
  [int]$ValidationInterval = 12,
  [int]$CheckpointInterval = 12,
  [int]$Seed = 20260328,
  [double]$WaveformDecoderBaseLogitsHighBandExcessWeight = 0.1,
  [double]$WaveformDecoderBaseLogitsActiveTemplateWeight = 0.1,
  [double]$WaveformDecoderBaseLogitsAperAbsZeroLagCorrWeight = 0.1,
  [double]$WaveformDecoderBaseLogitsNoiseEnergyAbsZeroLagCorrWeight = 0.1,
  [double]$WaveformDecoderBaseLogitsAperNoiseEnergyAbsZeroLagCorrWeight = 0.1,
  [double]$WaveformResidualShapeDeltaNoiseEnergyAbsZeroLagCorrWeight = 0.0,
  [switch]$Deterministic,
  [switch]$SmokeOnly
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path $DatasetIndex)) {
  throw "Missing dataset index: $DatasetIndex"
}

$resolvedDatasetIndex = (Resolve-Path $DatasetIndex).Path
$culture = [System.Globalization.CultureInfo]::InvariantCulture

if ($SmokeOnly) {
  $NumSteps = 1
  $PackagesPerStep = 4
  $ValidationInterval = 1
  $CheckpointInterval = 1
}

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
  if ($SmokeOnly) {
    $OutputDir = "reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_headstruct_bhb01_bpae01_bta01_baa01_bna01_fbmc_rs_smoke_fullsplit1step_round1_1"
  } else {
    $OutputDir = "reports/runtime/offline_mvp_nores_vocoder_dataset_training_loop_headstruct_bhb01_bpae01_bta01_baa01_bna01_fbmc_rs_fs24_r1_1"
  }
}

$command = @(
  ".\python.exe",
  "manage.py",
  "run-offline-mvp-nores-vocoder-dataset-training-loop",
  "--dataset-index",
  $resolvedDatasetIndex,
  "--output-dir",
  $OutputDir,
  "--device",
  $Device,
  "--num-steps",
  $NumSteps.ToString($culture),
  "--packages-per-step",
  $PackagesPerStep.ToString($culture),
  "--validation-interval",
  $ValidationInterval.ToString($culture),
  "--checkpoint-interval",
  $CheckpointInterval.ToString($culture),
  "--sampler-mode",
  "shuffle",
  "--seed",
  $Seed.ToString($culture),
  "--learning-rate",
  "0.001",
  "--max-grad-norm",
  "5.0",
  "--harmonic-weight",
  "1.0",
  "--noise-weight",
  "1.0",
  "--periodic-gate-weight",
  "0.2",
  "--noise-gate-weight",
  "0.2",
  "--activity-gate-weight",
  "0.2",
  "--waveform-weight",
  "0.5",
  "--stft-weight",
  "0.5",
  "--rms-guard-weight",
  "0.2",
  "--use-predicted-activity-gate",
  "--reconstruction-frame-gain-apply-mode",
  "pre_overlap_add",
  "--fusion-mode",
  "branch_mean_contrast_residual_v1",
  "--waveform-decoder-mode",
  "fused_single",
  "--use-residual-shape-branch-condition-adapter",
  "--residual-shape-branch-condition-scale",
  "1.0",
  "--residual-shape-branch-condition-mode",
  "raw_additive_v1",
  "--waveform-decoder-base-logits-high-band-excess-weight",
  $WaveformDecoderBaseLogitsHighBandExcessWeight.ToString($culture),
  "--waveform-decoder-base-logits-active-template-weight",
  $WaveformDecoderBaseLogitsActiveTemplateWeight.ToString($culture),
  "--waveform-decoder-base-logits-aper-abs-zero-lag-corr-weight",
  $WaveformDecoderBaseLogitsAperAbsZeroLagCorrWeight.ToString($culture),
  "--waveform-decoder-base-logits-noise-energy-abs-zero-lag-corr-weight",
  $WaveformDecoderBaseLogitsNoiseEnergyAbsZeroLagCorrWeight.ToString($culture),
  "--waveform-decoder-base-logits-aper-noise-energy-abs-zero-lag-corr-weight",
  $WaveformDecoderBaseLogitsAperNoiseEnergyAbsZeroLagCorrWeight.ToString($culture),
  "--waveform-residual-shape-delta-noise-energy-abs-zero-lag-corr-weight",
  $WaveformResidualShapeDeltaNoiseEnergyAbsZeroLagCorrWeight.ToString($culture)
)

if ($Deterministic) {
  $command += "--deterministic"
}

Write-Host "stage5 base-logits candidate dataset: $resolvedDatasetIndex"
Write-Host "stage5 base-logits candidate output : $OutputDir"
Write-Host "stage5 base-logits candidate mode   : $(if ($SmokeOnly) { 'smoke' } else { 'formal' })"

& $command[0] $command[1..($command.Length - 1)]

if ($LASTEXITCODE -ne 0) {
  throw "Stage5 base-logits minimal candidate run failed with exit code $LASTEXITCODE."
}
