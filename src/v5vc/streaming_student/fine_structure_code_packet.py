from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.managed_paths import reset_managed_directory


FINE_STRUCTURE_CODEBOOK_VERSION = "streaming_student_waveform_pca_codebook_v1"


def materialize_streaming_student_fine_structure_pca_packet_export(
    *,
    packet_export_path: Path,
    output_dir: Path,
    code_dim: int,
) -> dict[str, object]:
    packet_export_path = packet_export_path.resolve()
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)
    records_dir = output_dir / "records"
    records_dir.mkdir(parents=True, exist_ok=True)

    source_summary = json.loads(packet_export_path.read_text(encoding="utf-8"))
    source_records = list(source_summary.get("records", []))
    if not source_records:
        raise ValueError("No records found in the source streaming-student packet export.")

    loaded_packets: list[dict[str, object]] = []
    waveform_chunks: list[torch.Tensor] = []
    for record in source_records:
        packet_path = Path(str(record["packet_path"])).resolve()
        payload = torch.load(packet_path, map_location="cpu", weights_only=False)
        if not isinstance(payload, dict):
            raise TypeError(f"Unsupported packet payload type: {type(payload)!r}")
        fine_structure_reference = dict(payload.get("fine_structure_reference", {}))
        waveform_reference = fine_structure_reference.get("unit_rms_waveform_frame")
        if not isinstance(waveform_reference, torch.Tensor):
            raise ValueError(
                f"Packet is missing fine_structure_reference.unit_rms_waveform_frame: {packet_path}"
            )
        waveform_tensor = waveform_reference.detach().cpu().to(torch.float32)
        loaded_packets.append(
            {
                "record": dict(record),
                "payload": payload,
                "waveform_reference": waveform_tensor,
            }
        )
        waveform_chunks.append(waveform_tensor)

    codebook = fit_waveform_pca_codebook(
        waveform_frames=torch.cat(waveform_chunks, dim=0),
        code_dim=int(code_dim),
    )
    codebook_path = output_dir / "fine_structure_pca_codebook.pt"
    torch.save(codebook, codebook_path)

    exported_records: list[dict[str, object]] = []
    for item in loaded_packets:
        record = dict(item["record"])
        payload = dict(item["payload"])
        waveform_reference = item["waveform_reference"]
        waveform_code = project_waveform_pca_code(
            waveform_reference=waveform_reference,
            codebook=codebook,
        )
        fine_structure_code = {
            "codebook_version": FINE_STRUCTURE_CODEBOOK_VERSION,
            "code_family": "waveform_pca_code",
            "code_dim": int(waveform_code.shape[-1]),
            "waveform_pca_code": waveform_code,
            "source": "analysis_only_from_target_waveform_reference",
        }
        payload["fine_structure_code"] = fine_structure_code
        control_contract = dict(payload.get("control_contract", {}))
        control_contract["fine_structure_code_status"] = "analysis_only_waveform_pca_code"
        payload["control_contract"] = control_contract
        packet_relative_path = Path(str(record["packet_relative_path"]))
        packet_output_path = output_dir / packet_relative_path
        packet_output_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(payload, packet_output_path)
        record["packet_path"] = packet_output_path.as_posix()
        record["packet_relative_path"] = packet_relative_path.as_posix()
        record["fine_structure_code_dim"] = int(waveform_code.shape[-1])
        exported_records.append(record)

    summary = dict(source_summary)
    summary["generated_at"] = datetime.now().isoformat(timespec="seconds")
    summary["source_packet_export_path"] = packet_export_path.as_posix()
    summary["fine_structure_code"] = {
        "codebook_version": FINE_STRUCTURE_CODEBOOK_VERSION,
        "code_family": "waveform_pca_code",
        "code_dim": int(codebook["components"].shape[-1]),
        "record_count": len(exported_records),
        "fit_frame_count": int(codebook["fit_frame_count"]),
        "input_waveform_dim": int(codebook["components"].shape[0]),
        "explained_variance_ratio": float(codebook["explained_variance_ratio"]),
        "codebook_path": codebook_path.as_posix(),
        "source": "analysis_only_from_target_waveform_reference",
    }
    summary["records"] = exported_records
    notes = list(summary.get("notes", []))
    notes.append(
        "fine_structure_code.waveform_pca_code is an analysis-only compact waveform-geometry code fitted on the packet export itself; it is an upper-bound consumer experiment, not a deployable student prediction."
    )
    summary["notes"] = notes
    (output_dir / "streaming_student_downstream_control_packet.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "streaming_student_downstream_control_packet.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )
    return summary


def fit_waveform_pca_codebook(*, waveform_frames: torch.Tensor, code_dim: int) -> dict[str, object]:
    frames = waveform_frames.detach().cpu().to(torch.float32)
    mean = frames.mean(dim=0, keepdim=True)
    centered = frames - mean
    max_rank = min(int(centered.shape[0]), int(centered.shape[1]), max(1, int(code_dim)))
    _, singular_values, vh = torch.linalg.svd(centered, full_matrices=False)
    components = vh[:max_rank].transpose(0, 1).contiguous()
    total_variance = float(singular_values.pow(2).sum().item())
    retained_variance = float(singular_values[:max_rank].pow(2).sum().item())
    explained_variance_ratio = 0.0 if total_variance <= 1.0e-8 else retained_variance / total_variance
    return {
        "codebook_version": FINE_STRUCTURE_CODEBOOK_VERSION,
        "fit_frame_count": int(frames.shape[0]),
        "input_waveform_dim": int(frames.shape[1]),
        "mean": mean,
        "components": components,
        "explained_variance_ratio": round(float(explained_variance_ratio), 6),
    }


def project_waveform_pca_code(*, waveform_reference: torch.Tensor, codebook: dict[str, object]) -> torch.Tensor:
    waveform = waveform_reference.detach().cpu().to(torch.float32)
    mean = codebook["mean"].to(torch.float32)
    components = codebook["components"].to(torch.float32)
    return (waveform - mean) @ components


def build_markdown(summary: dict[str, object]) -> str:
    return "\n".join(
        [
            "# Streaming Student Fine-Structure PCA Packet Export",
            "",
            f"- packet_version: {summary.get('packet_version')}",
            f"- source_packet_export_path: {summary.get('source_packet_export_path')}",
            f"- split_name: {summary.get('split_name')}",
            f"- sample_count: {summary.get('sample_count')}",
            f"- fine_structure_code: {json.dumps(summary.get('fine_structure_code', {}), ensure_ascii=False)}",
            "",
            "## Notes",
            *[f"- {note}" for note in summary.get("notes", [])],
            "",
        ]
    )
