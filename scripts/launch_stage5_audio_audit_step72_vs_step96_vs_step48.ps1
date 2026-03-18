param(
  [int]$AutoCloseMs = 0
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

$command = @(
  ".\python.exe",
  "manage.py",
  "launch-audio-audit-gui",
  "--bundle",
  "reports/runtime/offline_mvp_nores_vocoder_audio_export_step72_validation_round1_1",
  "reports/runtime/offline_mvp_nores_vocoder_audio_export_step96_validation_round1_1",
  "reports/runtime/offline_mvp_nores_vocoder_audio_export_step48_validation_round1_1",
  "--output-dir",
  "reports/audio/audio_audit_gui_stage5_step72_vs_step96_vs_step48_session"
)

if ($AutoCloseMs -gt 0) {
  $command += @("--auto-close-ms", $AutoCloseMs.ToString())
}

& $command[0] $command[1..($command.Length - 1)]
