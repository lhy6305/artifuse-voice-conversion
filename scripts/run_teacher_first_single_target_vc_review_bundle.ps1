param(
  [string]$InputSpecJsonl = "",
  [string]$OutputDir = "",
  [string]$Device = "cpu",
  [double]$ChunkMs = 33.333333,
  [switch]$SaveIntermediates,
  [switch]$SkipFullPassVerify
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
if ([string]::IsNullOrWhiteSpace($OutputDir)) {
  $OutputDir = Join-Path "reports/runtime/offline_mvp_teacher_first_vc_demo_review_bundles" "review_bundle_$timestamp"
}

$specPath = $InputSpecJsonl
if ([string]::IsNullOrWhiteSpace($specPath)) {
  $defaultSpecs = @(
    @{
      case_id = "raw_front_2s"
      input_audio_path = (Resolve-Path "data_convert/dataset_ly65_raw.wav").Path
      max_audio_sec = 2.0
      notes = @("Front 2 seconds of the long raw source recording.")
    },
    @{
      case_id = "parallel_firefly_107"
      input_audio_path = (Resolve-Path "data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_107.wav").Path
      notes = @("Parallel source utterance matching target chapter3_17_firefly_107 content.")
    },
    @{
      case_id = "parallel_firefly_132"
      input_audio_path = (Resolve-Path "data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_132.wav").Path
      notes = @("Parallel source utterance matching target chapter3_17_firefly_132 content.")
    },
    @{
      case_id = "high_silence_segment_0061"
      input_audio_path = (Resolve-Path "data_prep/round1/source_segments/segments/segment_0061_0000300400_0000300910.wav").Path
      notes = @("Near-extreme high-silence source segment.")
    }
  )
  $specDir = Join-Path "tmp/teacher_first_vc_review_bundle_specs" $timestamp
  New-Item -ItemType Directory -Force -Path $specDir | Out-Null
  $specPath = Join-Path $specDir "review_bundle_input_specs.jsonl"
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
  throw "Missing review bundle spec jsonl: $specPath"
}

$resolvedSpecPath = (Resolve-Path $specPath).Path
$culture = [System.Globalization.CultureInfo]::InvariantCulture
$command = @(
  ".\python.exe",
  "manage.py",
  "build-offline-mvp-teacher-first-vc-review-bundle",
  "--input-spec-jsonl",
  $resolvedSpecPath,
  "--output-dir",
  $OutputDir,
  "--device",
  $Device,
  "--chunk-ms",
  $ChunkMs.ToString($culture)
)

if ($SaveIntermediates) {
  $command += "--save-intermediates"
} else {
  $command += "--no-save-intermediates"
}

if ($SkipFullPassVerify) {
  $command += "--skip-full-pass-verify"
}

Write-Host "teacher-first VC review bundle spec   : $resolvedSpecPath"
Write-Host "teacher-first VC review bundle output : $OutputDir"

& $command[0] $command[1..($command.Length - 1)]

if ($LASTEXITCODE -ne 0) {
  throw "Teacher-first VC review bundle failed with exit code $LASTEXITCODE."
}

$summaryPath = Join-Path $OutputDir "teacher_first_vc_review_bundle.json"
if (-not (Test-Path $summaryPath)) {
  throw "Review bundle summary was not written: $summaryPath"
}

$summary = Get-Content -Path $summaryPath -Encoding utf8 | ConvertFrom-Json
Write-Host "teacher-first VC review bundle summary : $summaryPath"
Write-Host "teacher-first VC review bundle cases   : $($summary.case_count)"
Write-Host "teacher-first VC review bundle ok      : $($summary.all_succeeded)"
Write-Host "teacher-first VC review listening dir  : $($summary.listening_dir)"
