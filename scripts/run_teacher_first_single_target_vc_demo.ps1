param(
  [Parameter(Mandatory = $true)]
  [string]$InputAudio,
  [string]$OutputDir = "",
  [string]$Device = "auto",
  [double]$MaxAudioSec = 0.0,
  [double]$ChunkMs = 33.333333,
  [switch]$UsePostEnv,
  [switch]$UsePreOverlapAdd,
  [switch]$NoSaveIntermediates,
  [switch]$SkipFullPassVerify
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
  $OutputDir = Join-Path "reports/runtime/offline_mvp_teacher_first_vc_demo_runs" "$sanitizedStem`_$timestamp"
}

$culture = [System.Globalization.CultureInfo]::InvariantCulture
$command = @(
  ".\python.exe",
  "manage.py",
  "run-offline-mvp-teacher-first-vc-demo",
  "--input-audio",
  $resolvedInputAudio,
  "--output-dir",
  $OutputDir,
  "--device",
  $Device,
  "--chunk-ms",
  $ChunkMs.ToString($culture)
)

if ($MaxAudioSec -gt 0.0) {
  $command += @("--max-audio-sec", $MaxAudioSec.ToString($culture))
}

if ($UsePostEnv -and $UsePreOverlapAdd) {
  throw "UsePostEnv and UsePreOverlapAdd cannot be set at the same time."
}

if ($UsePostEnv) {
  $command += @("--predicted-activity-gate-apply-mode", "post_ola_envelope")
} elseif ($UsePreOverlapAdd) {
  $command += @("--predicted-activity-gate-apply-mode", "pre_overlap_add")
}

if ($NoSaveIntermediates) {
  $command += "--no-save-intermediates"
}

if ($SkipFullPassVerify) {
  $command += "--skip-full-pass-verify"
}

Write-Host "teacher-first single-target demo input : $resolvedInputAudio"
Write-Host "teacher-first single-target demo output: $OutputDir"

& $command[0] $command[1..($command.Length - 1)]

if ($LASTEXITCODE -ne 0) {
  throw "Teacher-first single-target VC demo failed with exit code $LASTEXITCODE."
}
