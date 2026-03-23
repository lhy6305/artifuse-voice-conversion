param(
  [string]$InputSpecJsonl = "",
  [string]$OutputDir = "",
  [ValidateSet("main_listening", "boundary_probe")]
  [string]$BundleProfile = "main_listening",
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
  $OutputDir = Join-Path "reports/runtime/offline_mvp_teacher_first_vc_audible_smoke_bundles" "audible_smoke_${BundleProfile}_$timestamp"
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
          "Included in the default main-listening bundle because duration and speech density are suitable for quick human review."
        )
      },
      @{
        case_id = "peak_011"
        input_audio_path = (Resolve-Path "data_prep/round1/source_segments/peaks/peak_011_0002370615_top_peak.wav").Path
        notes = @(
          "Peak-energy source clip from the round1 peak export.",
          "Included in the default main-listening bundle because it is a compact audible case rather than a silence-heavy boundary."
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
          "This case is isolated into the boundary-probe profile so it does not contaminate the default main-listening bundle."
        )
      }
    )
  }
  $specDir = Join-Path "tmp/teacher_first_vc_audible_smoke_specs" "${BundleProfile}_$timestamp"
  New-Item -ItemType Directory -Force -Path $specDir | Out-Null
  $specPath = Join-Path $specDir "audible_smoke_input_specs.jsonl"
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
  throw "Missing audible smoke spec jsonl: $specPath"
}
if (-not (Test-Path $CalibrationAsset)) {
  throw "Missing calibration asset: $CalibrationAsset"
}

$resolvedSpecPath = (Resolve-Path $specPath).Path
$resolvedCalibrationAsset = (Resolve-Path $CalibrationAsset).Path
$culture = [System.Globalization.CultureInfo]::InvariantCulture
$command = @(
  ".\python.exe",
  "manage.py",
  "build-offline-mvp-teacher-first-vc-audible-smoke-bundle",
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

Write-Host "teacher-first audible smoke spec   : $resolvedSpecPath"
Write-Host "teacher-first audible smoke output : $OutputDir"
Write-Host "teacher-first audible smoke profile: $BundleProfile"

& $command[0] $command[1..($command.Length - 1)]

if ($LASTEXITCODE -ne 0) {
  throw "Teacher-first audible smoke bundle failed with exit code $LASTEXITCODE."
}

$summaryPath = Join-Path $OutputDir "teacher_first_vc_audible_smoke_bundle.json"
if (-not (Test-Path $summaryPath)) {
  throw "Audible smoke summary was not written: $summaryPath"
}

$summary = Get-Content -Path $summaryPath -Encoding utf8 | ConvertFrom-Json
Write-Host "teacher-first audible smoke summary : $summaryPath"
Write-Host "teacher-first audible smoke cases   : $($summary.case_count)"
Write-Host "positive controls ready             : $($summary.positive_controls_ready_count)/$($summary.case_count)"
Write-Host "decoded high-risk count             : $($summary.decoded_high_risk_count)"
Write-Host "teacher-first audible smoke ok      : $($summary.all_cases_pipeline_succeeded -and $summary.all_cases_positive_controls_ready)"
