param()

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

$audioAuditReviewPath = "reports/audio/audio_audit_gui_stage5_low_activity_validation12_decoded_session/audio_audit_review.json"
$governanceReportPath = "reports/stage_reports/stage5_low_activity_governance_validation12_waveformrms_round1_1/stage5_low_activity_governance_report.json"

if (-not (Test-Path $audioAuditReviewPath)) {
  throw "Missing audio audit review json: $audioAuditReviewPath"
}

if (-not (Test-Path $governanceReportPath)) {
  throw "Missing governance report json: $governanceReportPath"
}

$command = @(
  ".\python.exe",
  "manage.py",
  "materialize-stage5-low-activity-audit-result-report",
  "--audio-audit-review",
  $audioAuditReviewPath,
  "--governance-report",
  $governanceReportPath,
  "--output-dir",
  "reports/stage_reports/stage5_low_activity_audit_result_validation12_waveformrms_round1_1",
  "--title",
  "stage5 low-activity audit result report - validation12 waveformrms decoded"
)

& $command[0] $command[1..($command.Length - 1)]
