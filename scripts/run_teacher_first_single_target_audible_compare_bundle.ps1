param(
  [string]$InputSpecJsonl = "",
  [string]$OutputDir = "",
  [ValidateSet("main_listening", "boundary_probe")]
  [string]$BundleProfile = "main_listening",
  [string]$VocoderSpecJsonl = "",
  [string]$Device = "cpu",
  [double]$ChunkMs = 33.333333,
  [double]$TargetReferenceMaxAudioSec = 3.0,
  [string]$CalibrationAsset = "data_prep/round1_1/streaming_student_calibration/streaming_student_calibration_asset_estimated.json",
  [string]$TargetReferenceAudio = "",
  [switch]$SaveIntermediates,
  [switch]$SkipFullPassVerify
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
  $OutputDir = Join-Path "reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundles" "audible_compare_${BundleProfile}_$timestamp"
}

$specPath = $InputSpecJsonl
if ([string]::IsNullOrWhiteSpace($specPath)) {
  if ($BundleProfile -eq "main_listening") {
    $defaultSpecs = @(
      @{
        case_id = "regular_segment_0001"
        input_audio_path = (Resolve-Path "data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav").Path
        notes = @(
          "Regular source segment used in earlier user-line smoke tests.",
          "Included in the default main-listening compare bundle because duration and speech density are suitable for quick human review."
        )
      },
      @{
        case_id = "peak_011"
        input_audio_path = (Resolve-Path "data_prep/round1/source_segments/peaks/peak_011_0002370615_top_peak.wav").Path
        notes = @(
          "Peak-energy source clip from the round1 peak export.",
          "Included in the default main-listening compare bundle because it is a compact audible case rather than a silence-heavy boundary."
        )
      }
    )
  } else {
    $defaultSpecs = @(
      @{
        case_id = "high_silence_segment_0061"
        input_audio_path = (Resolve-Path "data_prep/round1/source_segments/segments/segment_0061_0000300400_0000300910.wav").Path
        notes = @(
          "Near-extreme high-silence source segment.",
          "This case is isolated into the boundary-probe compare profile so it does not contaminate the default main-listening bundle."
        )
      }
    )
  }
  $specDir = Join-Path "tmp/teacher_first_vc_audible_compare_specs" "${BundleProfile}_$timestamp"
  New-Item -ItemType Directory -Force -Path $specDir | Out-Null
  $specPath = Join-Path $specDir "audible_compare_input_specs.jsonl"
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
  $writer = New-Object System.IO.StreamWriter($specPath, $false, $utf8NoBom)
  try {
    foreach ($spec in $defaultSpecs) {
      $writer.WriteLine(($spec | ConvertTo-Json -Compress -Depth 5))
    }
  } finally {
    $writer.Dispose()
  }
}

if (-not (Test-Path $specPath)) {
  throw "Missing audible compare spec jsonl: $specPath"
}
if (-not (Test-Path $CalibrationAsset)) {
  throw "Missing calibration asset: $CalibrationAsset"
}
if ((-not [string]::IsNullOrWhiteSpace($VocoderSpecJsonl)) -and (-not (Test-Path $VocoderSpecJsonl))) {
  throw "Missing vocoder compare spec jsonl: $VocoderSpecJsonl"
}

$resolvedSpecPath = (Resolve-Path $specPath).Path
$resolvedCalibrationAsset = (Resolve-Path $CalibrationAsset).Path
$culture = [System.Globalization.CultureInfo]::InvariantCulture
$command = @(
  ".\python.exe",
  "manage.py",
  "build-offline-mvp-teacher-first-vc-audible-compare-bundle",
  "--input-spec-jsonl",
  $resolvedSpecPath,
  "--output-dir",
  $OutputDir,
  "--device",
  $Device,
  "--chunk-ms",
  $ChunkMs.ToString($culture),
  "--calibration-asset",
  $resolvedCalibrationAsset,
  "--target-reference-max-audio-sec",
  $TargetReferenceMaxAudioSec.ToString($culture)
)

if (-not [string]::IsNullOrWhiteSpace($VocoderSpecJsonl)) {
  $resolvedVocoderSpecPath = (Resolve-Path $VocoderSpecJsonl).Path
  $command += @("--vocoder-spec-jsonl", $resolvedVocoderSpecPath)
}

if (-not [string]::IsNullOrWhiteSpace($TargetReferenceAudio)) {
  $resolvedTargetReferenceAudio = (Resolve-Path $TargetReferenceAudio).Path
  $command += @("--target-reference-audio", $resolvedTargetReferenceAudio)
}

if ($SaveIntermediates) {
  $command += "--save-intermediates"
} else {
  $command += "--no-save-intermediates"
}

if ($SkipFullPassVerify) {
  $command += "--skip-full-pass-verify"
}

Write-Host "teacher-first audible compare spec    : $resolvedSpecPath"
Write-Host "teacher-first audible compare output  : $OutputDir"
Write-Host "teacher-first audible compare profile : $BundleProfile"

& $command[0] $command[1..($command.Length - 1)]

if ($LASTEXITCODE -ne 0) {
  throw "Teacher-first audible compare bundle failed with exit code $LASTEXITCODE."
}

$summaryPath = Join-Path $OutputDir "teacher_first_vc_audible_compare_bundle.json"
if (-not (Test-Path $summaryPath)) {
  throw "Audible compare summary was not written: $summaryPath"
}

$summary = Get-Content -Path $summaryPath -Encoding utf8 | ConvertFrom-Json
Write-Host "teacher-first audible compare summary : $summaryPath"
Write-Host "teacher-first audible compare cases   : $($summary.case_count)"
Write-Host "teacher-first audible compare variants: $($summary.variant_count)"
Write-Host "positive controls ready              : $($summary.positive_controls_ready_count)/$($summary.case_count)"
Write-Host "variant runs succeeded               : $($summary.variant_succeeded_count)/$($summary.variant_run_count)"
Write-Host "variant decoded high-risk count      : $($summary.variant_decoded_high_risk_count)"

foreach ($variant in $summary.vocoder_variants) {
  Write-Host ("variant {0}: checkpoint={1} high_risk={2}/{3}" -f `
    $variant.variant_id, `
    $variant.checkpoint_path, `
    $variant.decoded_high_risk_count, `
    $variant.case_count)
}

Write-Host "teacher-first audible compare ok     : $($summary.all_cases_positive_controls_ready -and $summary.all_variant_runs_succeeded)"
