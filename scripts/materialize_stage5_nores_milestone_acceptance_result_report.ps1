param()

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
$env:PYTHONPATH = if ([string]::IsNullOrWhiteSpace($env:PYTHONPATH)) { "src" } else { "src;$($env:PYTHONPATH)" }

$audioAuditReviewPath = "reports/audio/audio_audit_gui_stage5_nores_milestone_acceptance_session/audio_audit_review.json"

if (-not (Test-Path $audioAuditReviewPath)) {
  throw "Missing audio audit review json: $audioAuditReviewPath"
}

$command = @(
  ".\python.exe",
  "-m",
  "v5vc.stage5_nores_milestone_acceptance_report",
  "--audio-audit-review",
  $audioAuditReviewPath,
  "--output-dir",
  "reports/stage_reports/stage5_nores_milestone_acceptance_result_round1_1",
  "--title",
  "stage5 no-res milestone acceptance report - step72 smooth3 postenv validation12 decoded"
)

& $command[0] $command[1..($command.Length - 1)]
