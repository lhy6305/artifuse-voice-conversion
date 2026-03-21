param(
  [int]$AutoCloseMs = 0
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

$legacyProbeOutputDir = "reports/audio/stage5_low_activity_fragmentation_probe_activitygate72_decoded_glitchablation_smooth3_postenv_validation12_round1_1"
$probeOutputDir = "reports/audio/stage5_s72_glitch_s3_postenv_v12_probe"
$baselineExportDir = "reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decoded_glitchablation_smooth3_validation12_round1_1"
$postenvExportDir = "reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_decoded_glitchablation_smooth3postenv_validation12_round1_1"
$legacySessionOutputDir = "reports/audio/audio_audit_gui_stage5_step72_glitch_smooth3_postenv_validation12_session"
$sessionOutputDir = "reports/audio/audio_audit_gui_stage5_s72_s3_postenv_v12_session"
$baselineBundleDir = Join-Path $probeOutputDir "audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step72__decode_gate_smooth3"
$postenvBundleDir = Join-Path $probeOutputDir "audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step72__decode_gate_smooth3_postenv"

if ((Test-Path $legacyProbeOutputDir) -and (-not (Test-Path $probeOutputDir))) {
  Move-Item -LiteralPath $legacyProbeOutputDir -Destination $probeOutputDir
}

if ((Test-Path $legacySessionOutputDir) -and (-not (Test-Path $sessionOutputDir))) {
  Move-Item -LiteralPath $legacySessionOutputDir -Destination $sessionOutputDir
}

if ((-not (Test-Path $baselineBundleDir)) -or (-not (Test-Path $postenvBundleDir))) {
  Write-Host "Missing decoded audit bundles. Rebuilding them from the Stage5 export manifests..."
  $rebuildCommand = @(
    ".\python.exe",
    "manage.py",
    "analyze-stage5-low-activity-fragments",
    "--bundle",
    $baselineExportDir,
    $postenvExportDir,
    "--analysis-audio-sources",
    "decoded",
    "--output-dir",
    $probeOutputDir
  )
  & $rebuildCommand[0] $rebuildCommand[1..($rebuildCommand.Length - 1)]
  if ($LASTEXITCODE -ne 0) {
    throw "Failed to rebuild missing decoded audit bundles."
  }
}

$command = @(
  ".\python.exe",
  "manage.py",
  "launch-audio-audit-gui",
  "--bundle",
  $baselineBundleDir,
  $postenvBundleDir,
  "--output-dir",
  $sessionOutputDir
)

if ($AutoCloseMs -gt 0) {
  $command += @("--auto-close-ms", $AutoCloseMs.ToString())
}

& $command[0] $command[1..($command.Length - 1)]
