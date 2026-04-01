param(
    [Parameter(Mandatory = $true)]
    [string]$OutputDir,
    [Parameter(Mandatory = $true)]
    [string]$LeftVariantId,
    [Parameter(Mandatory = $true)]
    [string]$LeftExportManifestJson,
    [Parameter(Mandatory = $true)]
    [string]$LeftSourceFilterReviewJson,
    [string]$LeftBundleManifestJson = "",
    [string]$LeftStructureProbeJson = "",
    [string]$LeftSpeechEmergenceJson = "",
    [Parameter(Mandatory = $true)]
    [string]$RightVariantId,
    [Parameter(Mandatory = $true)]
    [string]$RightExportManifestJson,
    [Parameter(Mandatory = $true)]
    [string]$RightSourceFilterReviewJson,
    [string]$RightBundleManifestJson = "",
    [string]$RightStructureProbeJson = "",
    [string]$RightSpeechEmergenceJson = ""
)

$ErrorActionPreference = "Stop"

function Resolve-AbsolutePath {
    param([string]$PathValue)
    return (Resolve-Path $PathValue).Path
}

function Load-JsonFile {
    param([string]$PathValue)
    return Get-Content $PathValue -Raw | ConvertFrom-Json
}

function Get-SiblingMarkdownPath {
    param([string]$JsonPath)
    $candidate = [System.IO.Path]::ChangeExtension($JsonPath, ".md")
    if (Test-Path $candidate) {
        return $candidate
    }
    return $null
}

function Copy-IfExists {
    param(
        [string]$SourcePath,
        [string]$DestinationPath
    )
    if ([string]::IsNullOrWhiteSpace($SourcePath)) {
        return
    }
    if (Test-Path $SourcePath) {
        Copy-Item $SourcePath $DestinationPath -Force
    }
}

function Sanitize-RecordSlug {
    param([string]$RecordId)
    return (($RecordId -replace "[^A-Za-z0-9]+", "_").Trim("_"))
}

$leftExportManifestJson = Resolve-AbsolutePath $LeftExportManifestJson
$leftSourceFilterReviewJson = Resolve-AbsolutePath $LeftSourceFilterReviewJson
$rightExportManifestJson = Resolve-AbsolutePath $RightExportManifestJson
$rightSourceFilterReviewJson = Resolve-AbsolutePath $RightSourceFilterReviewJson
$leftBundleManifestJson = if ([string]::IsNullOrWhiteSpace($LeftBundleManifestJson)) { $null } else { Resolve-AbsolutePath $LeftBundleManifestJson }
$rightBundleManifestJson = if ([string]::IsNullOrWhiteSpace($RightBundleManifestJson)) { $null } else { Resolve-AbsolutePath $RightBundleManifestJson }
$leftStructureProbeJson = if ([string]::IsNullOrWhiteSpace($LeftStructureProbeJson)) { $null } else { Resolve-AbsolutePath $LeftStructureProbeJson }
$rightStructureProbeJson = if ([string]::IsNullOrWhiteSpace($RightStructureProbeJson)) { $null } else { Resolve-AbsolutePath $RightStructureProbeJson }
$leftSpeechEmergenceJson = if ([string]::IsNullOrWhiteSpace($LeftSpeechEmergenceJson)) { $null } else { Resolve-AbsolutePath $LeftSpeechEmergenceJson }
$rightSpeechEmergenceJson = if ([string]::IsNullOrWhiteSpace($RightSpeechEmergenceJson)) { $null } else { Resolve-AbsolutePath $RightSpeechEmergenceJson }

$outputDir = Join-Path (Get-Location) $OutputDir
if (Test-Path $outputDir) {
    Remove-Item $outputDir -Recurse -Force
}
New-Item -ItemType Directory -Path $outputDir | Out-Null
$recordsDir = Join-Path $outputDir "records"
$manifestsDir = Join-Path $outputDir "manifests"
New-Item -ItemType Directory -Path $recordsDir | Out-Null
New-Item -ItemType Directory -Path $manifestsDir | Out-Null

$leftExport = Load-JsonFile $leftExportManifestJson
$leftReview = Load-JsonFile $leftSourceFilterReviewJson
$rightExport = Load-JsonFile $rightExportManifestJson
$rightReview = Load-JsonFile $rightSourceFilterReviewJson
$leftExportManifestMd = Get-SiblingMarkdownPath $leftExportManifestJson
$leftSourceFilterReviewMd = Get-SiblingMarkdownPath $leftSourceFilterReviewJson
$leftBundleManifestMd = if ($leftBundleManifestJson) { Get-SiblingMarkdownPath $leftBundleManifestJson } else { $null }
$leftStructureProbeMd = if ($leftStructureProbeJson) { Get-SiblingMarkdownPath $leftStructureProbeJson } else { $null }
$leftSpeechEmergenceMd = if ($leftSpeechEmergenceJson) { Get-SiblingMarkdownPath $leftSpeechEmergenceJson } else { $null }
$rightExportManifestMd = Get-SiblingMarkdownPath $rightExportManifestJson
$rightSourceFilterReviewMd = Get-SiblingMarkdownPath $rightSourceFilterReviewJson
$rightBundleManifestMd = if ($rightBundleManifestJson) { Get-SiblingMarkdownPath $rightBundleManifestJson } else { $null }
$rightStructureProbeMd = if ($rightStructureProbeJson) { Get-SiblingMarkdownPath $rightStructureProbeJson } else { $null }
$rightSpeechEmergenceMd = if ($rightSpeechEmergenceJson) { Get-SiblingMarkdownPath $rightSpeechEmergenceJson } else { $null }

$leftReviewRecords = @{}
foreach ($record in $leftReview.records) {
    $leftReviewRecords[[string]$record.record_id] = $record
}
$leftExportRecords = @{}
foreach ($record in $leftExport.records) {
    $leftExportRecords[[string]$record.record_id] = $record
}
$rightReviewRecords = @{}
foreach ($record in $rightReview.records) {
    $rightReviewRecords[[string]$record.record_id] = $record
}
$rightExportRecords = @{}
foreach ($record in $rightExport.records) {
    $rightExportRecords[[string]$record.record_id] = $record
}

$recordEntries = New-Object System.Collections.Generic.List[object]
foreach ($recordId in $leftReviewRecords.Keys) {
    if (-not $rightReviewRecords.ContainsKey($recordId)) {
        continue
    }
    $leftRecord = $leftReviewRecords[$recordId]
    $rightRecord = $rightReviewRecords[$recordId]
    $leftExportRecord = $leftExportRecords[$recordId]
    $rightExportRecord = $rightExportRecords[$recordId]
    $recordSlug = Sanitize-RecordSlug $recordId
    $recordDir = Join-Path $recordsDir $recordSlug
    $alignedDir = Join-Path $recordDir "aligned"
    $leftDir = Join-Path $recordDir $LeftVariantId
    $rightDir = Join-Path $recordDir $RightVariantId
    foreach ($dir in @($recordDir, $alignedDir, $leftDir, $rightDir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
    }

    Copy-IfExists ([string]$leftRecord.aligned_target_audio_path) (Join-Path $alignedDir "aligned_target.wav")
    Copy-IfExists ([string]$leftRecord.aligned_spectrogram_path) (Join-Path $alignedDir "aligned.linear_spectrogram.png")

    Copy-IfExists ([string]$leftRecord.decoded_audio_path) (Join-Path $leftDir "decoded.wav")
    Copy-IfExists ([string]$leftExportRecord.audit_proxy_audio_path) (Join-Path $leftDir "audit_proxy.wav")
    Copy-IfExists ([string]$leftRecord.decoded_spectrogram_path) (Join-Path $leftDir "decoded.linear_spectrogram.png")

    Copy-IfExists ([string]$rightRecord.decoded_audio_path) (Join-Path $rightDir "decoded.wav")
    Copy-IfExists ([string]$rightExportRecord.audit_proxy_audio_path) (Join-Path $rightDir "audit_proxy.wav")
    Copy-IfExists ([string]$rightRecord.decoded_spectrogram_path) (Join-Path $rightDir "decoded.linear_spectrogram.png")

    $recordEntries.Add(
        [ordered]@{
            record_id = [string]$recordId
            review_directory = $recordDir
            aligned = [ordered]@{
                audio = (Join-Path $alignedDir "aligned_target.wav")
                spectrogram = (Join-Path $alignedDir "aligned.linear_spectrogram.png")
            }
            variants = @(
                [ordered]@{
                    variant_id = $LeftVariantId
                    directory = $leftDir
                    status = [string]$leftRecord.status
                    decoded_audio = (Join-Path $leftDir "decoded.wav")
                    audit_proxy_audio = (Join-Path $leftDir "audit_proxy.wav")
                    decoded_spectrogram = (Join-Path $leftDir "decoded.linear_spectrogram.png")
                    machine_review_metrics = $leftRecord.machine_review_metrics
                },
                [ordered]@{
                    variant_id = $RightVariantId
                    directory = $rightDir
                    status = [string]$rightRecord.status
                    decoded_audio = (Join-Path $rightDir "decoded.wav")
                    audit_proxy_audio = (Join-Path $rightDir "audit_proxy.wav")
                    decoded_spectrogram = (Join-Path $rightDir "decoded.linear_spectrogram.png")
                    machine_review_metrics = $rightRecord.machine_review_metrics
                }
            )
        }
    ) | Out-Null
}

$manifestCopySpecs = @(
    @{ path = $leftExportManifestJson; name = "$LeftVariantId.nores_vocoder_audio_export.json" },
    @{ path = $leftExportManifestMd; name = "$LeftVariantId.nores_vocoder_audio_export.md" },
    @{ path = $leftSourceFilterReviewJson; name = "$LeftVariantId.stage5_source_filter_review.json" },
    @{ path = $leftSourceFilterReviewMd; name = "$LeftVariantId.stage5_source_filter_review.md" },
    @{ path = $leftBundleManifestJson; name = "$LeftVariantId.stage5_listening_bundle.json" },
    @{ path = $leftBundleManifestMd; name = "$LeftVariantId.stage5_listening_bundle.md" },
    @{ path = $leftStructureProbeJson; name = "$LeftVariantId.stage5_waveform_decoder_structure_probe.json" },
    @{ path = $leftStructureProbeMd; name = "$LeftVariantId.stage5_waveform_decoder_structure_probe.md" },
    @{ path = $leftSpeechEmergenceJson; name = "$LeftVariantId.stage5_speech_emergence_probe.json" },
    @{ path = $leftSpeechEmergenceMd; name = "$LeftVariantId.stage5_speech_emergence_probe.md" },
    @{ path = $rightExportManifestJson; name = "$RightVariantId.nores_vocoder_audio_export.json" },
    @{ path = $rightExportManifestMd; name = "$RightVariantId.nores_vocoder_audio_export.md" },
    @{ path = $rightSourceFilterReviewJson; name = "$RightVariantId.stage5_source_filter_review.json" },
    @{ path = $rightSourceFilterReviewMd; name = "$RightVariantId.stage5_source_filter_review.md" },
    @{ path = $rightBundleManifestJson; name = "$RightVariantId.stage5_listening_bundle.json" },
    @{ path = $rightBundleManifestMd; name = "$RightVariantId.stage5_listening_bundle.md" },
    @{ path = $rightStructureProbeJson; name = "$RightVariantId.stage5_waveform_decoder_structure_probe.json" },
    @{ path = $rightStructureProbeMd; name = "$RightVariantId.stage5_waveform_decoder_structure_probe.md" },
    @{ path = $rightSpeechEmergenceJson; name = "$RightVariantId.stage5_speech_emergence_probe.json" },
    @{ path = $rightSpeechEmergenceMd; name = "$RightVariantId.stage5_speech_emergence_probe.md" }
)
foreach ($spec in $manifestCopySpecs) {
    if ($null -ne $spec.path -and -not [string]::IsNullOrWhiteSpace([string]$spec.path) -and (Test-Path $spec.path)) {
        Copy-Item $spec.path (Join-Path $manifestsDir $spec.name) -Force
    }
}

$bundle = [ordered]@{
    generated_at = (Get-Date).ToString("s")
    bundle_type = "stage5_paired_full5_listening_spectrogram_review_bundle_v1"
    review_focus = "$LeftVariantId`_vs_$RightVariantId"
    root_directory = $outputDir
    variants = @(
        [ordered]@{
            variant_id = $LeftVariantId
            checkpoint_path = $leftExport.checkpoint_path
            export_manifest_path = $leftExportManifestJson
            source_filter_review_path = $leftSourceFilterReviewJson
            bundle_manifest_path = $leftBundleManifestJson
            structure_probe_path = $leftStructureProbeJson
            speech_emergence_path = $leftSpeechEmergenceJson
            aggregate = $leftReview.aggregates
            buzz_reject_summary = $leftExport.buzz_reject_summary
        },
        [ordered]@{
            variant_id = $RightVariantId
            checkpoint_path = $rightExport.checkpoint_path
            export_manifest_path = $rightExportManifestJson
            source_filter_review_path = $rightSourceFilterReviewJson
            bundle_manifest_path = $rightBundleManifestJson
            structure_probe_path = $rightStructureProbeJson
            speech_emergence_path = $rightSpeechEmergenceJson
            aggregate = $rightReview.aggregates
            buzz_reject_summary = $rightExport.buzz_reject_summary
        }
    )
    records = $recordEntries
    notes = @(
        "All listening assets for this A/B are copied under one root directory.",
        "Use records/<record_id>/aligned for the shared target reference.",
        "Use records/<record_id>/$LeftVariantId and records/<record_id>/$RightVariantId for the compared decoded routes.",
        "manifests/ contains copied json/md sidecars from the original export and review runs."
    )
}

$bundleJsonPath = Join-Path $outputDir "stage5_paired_full5_listening_spectrogram_review_bundle.json"
$bundle | ConvertTo-Json -Depth 8 | Set-Content -Path $bundleJsonPath -Encoding UTF8

$mdLines = New-Object System.Collections.Generic.List[string]
$mdLines.Add("# Stage5 Paired Full5 Listening And Spectrogram Review Bundle")
$mdLines.Add("")
$mdLines.Add("- generated_at: " + $bundle.generated_at)
$mdLines.Add("- root_directory: " + $outputDir)
$mdLines.Add("- compared_variants: ``$LeftVariantId`` vs ``$RightVariantId``")
$mdLines.Add("")
$mdLines.Add("## Aggregate Sidecars")
$mdLines.Add("- $LeftVariantId decoded_template_cosine_mean: ``" + [string]$leftReview.aggregates.decoded_template_cosine_mean + "``")
$mdLines.Add("- $RightVariantId decoded_template_cosine_mean: ``" + [string]$rightReview.aggregates.decoded_template_cosine_mean + "``")
$mdLines.Add("- $LeftVariantId decoded_vuv_high_band_ratio_mean: ``" + [string]$leftReview.aggregates.decoded_vuv_high_band_ratio_mean + "``")
$mdLines.Add("- $RightVariantId decoded_vuv_high_band_ratio_mean: ``" + [string]$rightReview.aggregates.decoded_vuv_high_band_ratio_mean + "``")
$mdLines.Add("- $LeftVariantId buzz_reject_summary: ``" + ($leftExport.buzz_reject_summary | ConvertTo-Json -Compress) + "``")
$mdLines.Add("- $RightVariantId buzz_reject_summary: ``" + ($rightExport.buzz_reject_summary | ConvertTo-Json -Compress) + "``")
$mdLines.Add("")
$mdLines.Add("## Layout")
$mdLines.Add("- manifests: ``" + $manifestsDir + "``")
$mdLines.Add("- records: ``" + $recordsDir + "``")
$mdLines.Add("- manifests now also copy optional speech-emergence json/md when provided.")
$mdLines.Add("")
$mdLines.Add("## Records")
foreach ($record in $recordEntries) {
    $mdLines.Add("- " + $record.record_id)
    $mdLines.Add("  aligned: " + $record.aligned.audio + " | " + $record.aligned.spectrogram)
    foreach ($variant in $record.variants) {
        $mdLines.Add("  " + $variant.variant_id + ": " + $variant.decoded_audio + " | " + $variant.audit_proxy_audio + " | " + $variant.decoded_spectrogram)
    }
}
$mdLines.Add("")
$mdLines.Add("## Notes")
$mdLines.Add("- This bundle keeps every current A/B listening artifact in one directory tree.")
$mdLines.Add("- Human review should ask whether the right-hand variant adds any record-specific audible or visible structure beyond the left-hand variant, not just whether it changes buzz brightness or envelope following.")
$bundleMdPath = Join-Path $outputDir "stage5_paired_full5_listening_spectrogram_review_bundle.md"
$mdLines | Set-Content -Path $bundleMdPath -Encoding UTF8

Write-Output $outputDir
