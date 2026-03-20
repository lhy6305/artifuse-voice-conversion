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
  "reports/audio/stage5_low_activity_fragmentation_probe_activitygate72_decoded_glitchablation_smooth3_validation12_round1_1/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step72",
  "reports/audio/stage5_low_activity_fragmentation_probe_activitygate72_decoded_glitchablation_smooth3_validation12_round1_1/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step72__decode_gate_smooth3",
  "--output-dir",
  "reports/audio/audio_audit_gui_stage5_step72_glitch_smooth3_validation12_session"
)

if ($AutoCloseMs -gt 0) {
  $command += @("--auto-close-ms", $AutoCloseMs.ToString())
}

& $command[0] $command[1..($command.Length - 1)]
