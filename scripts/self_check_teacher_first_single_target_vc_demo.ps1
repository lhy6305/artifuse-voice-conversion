param(
  [string]$InputAudio = "data_prep/round1/source_segments/segments/segment_0001_0000020110_0000021640.wav",
  [string]$OutputDir = "",
  [string]$Device = "cpu",
  [double]$MaxAudioSec = 0.1
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path $InputAudio)) {
  throw "Missing input audio: $InputAudio"
}

$resolvedInputAudio = (Resolve-Path $InputAudio).Path

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
  $inputStem = [System.IO.Path]::GetFileNameWithoutExtension($resolvedInputAudio)
  $sanitizedStem = ($inputStem -replace "[^A-Za-z0-9_-]", "_").Trim("_")
  if ([string]::IsNullOrWhiteSpace($sanitizedStem)) {
    $sanitizedStem = "input"
  }
  $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
  $OutputDir = Join-Path "reports/runtime/offline_mvp_teacher_first_vc_demo_self_checks" "$sanitizedStem`_$timestamp"
}

$culture = [System.Globalization.CultureInfo]::InvariantCulture
$command = @(
  ".\python.exe",
  "manage.py",
  "self-check-offline-mvp-teacher-first-vc-demo",
  "--input-audio",
  $resolvedInputAudio,
  "--output-dir",
  $OutputDir,
  "--device",
  $Device,
  "--max-audio-sec",
  $MaxAudioSec.ToString($culture)
)

Write-Host "teacher-first VC demo self-check input : $resolvedInputAudio"
Write-Host "teacher-first VC demo self-check output: $OutputDir"

& $command[0] $command[1..($command.Length - 1)]

if ($LASTEXITCODE -ne 0) {
  throw "Teacher-first VC demo self-check failed with exit code $LASTEXITCODE."
}

$summaryPath = Join-Path $OutputDir "teacher_first_vc_demo_self_check.json"
if (-not (Test-Path $summaryPath)) {
  throw "Self-check summary was not written: $summaryPath"
}

$summary = Get-Content -Path $summaryPath -Encoding utf8 | ConvertFrom-Json
Write-Host "teacher-first VC demo self-check summary : $summaryPath"
Write-Host "teacher-first VC demo self-check cases   : $($summary.case_count)"
Write-Host "teacher-first VC demo self-check passed  : $($summary.passed_count)"
Write-Host "teacher-first VC demo self-check failed  : $($summary.failed_count)"
Write-Host "teacher-first VC demo self-check ok      : $($summary.all_passed)"
