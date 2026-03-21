param(
  [int]$AutoCloseMs = 0
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
$env:PYTHONPATH = if ([string]::IsNullOrWhiteSpace($env:PYTHONPATH)) { "src" } else { "src;$($env:PYTHONPATH)" }

$bundleDir = "reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decoded_glitchablation_smooth3postenv_validation12_round1_1"
$sessionOutputDir = "reports/audio/audio_audit_gui_stage5_nores_milestone_acceptance_session"

if (-not (Test-Path $bundleDir)) {
  throw "Required Stage5 no-res milestone bundle is missing: $bundleDir"
}

$command = @(
  ".\python.exe",
  "-m",
  "v5vc.audio_audit_gui",
  "--bundle",
  $bundleDir,
  "--output-dir",
  $sessionOutputDir,
  "--review-mode",
  "milestone_acceptance"
)

if ($AutoCloseMs -gt 0) {
  $command += @("--auto-close-ms", $AutoCloseMs.ToString())
}

& $command[0] $command[1..($command.Length - 1)]
