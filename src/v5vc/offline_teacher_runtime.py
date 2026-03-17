from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path

import torch

from v5vc.ablation_eval import load_checkpoint
from v5vc.offline_mvp.data import load_waveform
from v5vc.streaming_student.teacher_labels import resolve_teacher_source
from v5vc.train_entry import instantiate_offline_mvp_model


RUNTIME_OUTPUT_KEYS = (
    "hidden",
    "fused_hidden",
    "z_art",
    "event_logits",
    "event_probs",
    "acoustic",
)


@dataclass
class OfflineTeacherRuntimeChunk:
    frame_count: int
    frame_start_samples: torch.Tensor
    outputs: dict[str, torch.Tensor]


class OfflineMVPTeacherRuntime:
    def __init__(
        self,
        model: torch.nn.Module,
        device: torch.device,
        frame_length: int,
        hop_length: int,
    ) -> None:
        self.model = model.to(device)
        self.device = device
        self.frame_length = int(frame_length)
        self.hop_length = int(hop_length)
        self.reset()

    def reset(self) -> None:
        self._pending_waveform = torch.zeros((0,), dtype=torch.float32)
        self._emitted_frame_count = 0

    def push_audio_chunk(self, chunk_waveform: torch.Tensor) -> OfflineTeacherRuntimeChunk:
        chunk = self._normalize_chunk(chunk_waveform)
        if chunk.numel() == 0:
            return self._empty_chunk()
        buffered = torch.cat((self._pending_waveform, chunk), dim=0)
        if buffered.numel() < self.frame_length:
            self._pending_waveform = buffered
            return self._empty_chunk()
        frame_count = ((buffered.numel() - self.frame_length) // self.hop_length) + 1
        outputs = self._run_model(buffered)
        emit_outputs = {
            key: outputs[key][0, :frame_count].detach().cpu()
            for key in RUNTIME_OUTPUT_KEYS
        }
        frame_start_samples = (
            torch.arange(frame_count, dtype=torch.long) * self.hop_length
            + (self._emitted_frame_count * self.hop_length)
        )
        consumed_samples = frame_count * self.hop_length
        self._pending_waveform = buffered[consumed_samples:].clone()
        self._emitted_frame_count += frame_count
        return OfflineTeacherRuntimeChunk(
            frame_count=frame_count,
            frame_start_samples=frame_start_samples,
            outputs=emit_outputs,
        )

    def flush(self) -> OfflineTeacherRuntimeChunk:
        if self._pending_waveform.numel() == 0:
            return self._empty_chunk()
        if self._emitted_frame_count > 0:
            self._pending_waveform = torch.zeros((0,), dtype=torch.float32)
            return self._empty_chunk()
        outputs = self._run_model(self._pending_waveform)
        emit_outputs = {
            key: outputs[key][0, :1].detach().cpu()
            for key in RUNTIME_OUTPUT_KEYS
        }
        frame_start_samples = torch.tensor(
            [self._emitted_frame_count * self.hop_length],
            dtype=torch.long,
        )
        self._pending_waveform = torch.zeros((0,), dtype=torch.float32)
        self._emitted_frame_count += 1
        return OfflineTeacherRuntimeChunk(
            frame_count=1,
            frame_start_samples=frame_start_samples,
            outputs=emit_outputs,
        )

    def _run_model(self, waveform: torch.Tensor) -> dict[str, torch.Tensor]:
        waveform_batch = waveform.unsqueeze(0).to(self.device)
        lengths = torch.tensor([waveform.numel()], dtype=torch.long, device=self.device)
        with torch.no_grad():
            outputs = self.model(waveform=waveform_batch, lengths=lengths)
        return outputs

    def _normalize_chunk(self, chunk_waveform: torch.Tensor) -> torch.Tensor:
        if chunk_waveform.ndim != 1:
            raise ValueError(f"Expected waveform chunk shape [T], got {tuple(chunk_waveform.shape)}")
        return chunk_waveform.to(torch.float32).detach().cpu().clone()

    def _empty_chunk(self) -> OfflineTeacherRuntimeChunk:
        return OfflineTeacherRuntimeChunk(
            frame_count=0,
            frame_start_samples=torch.zeros((0,), dtype=torch.long),
            outputs={
                "hidden": torch.zeros((0, 64), dtype=torch.float32),
                "fused_hidden": torch.zeros((0, 64), dtype=torch.float32),
                "z_art": torch.zeros((0, 8), dtype=torch.float32),
                "event_logits": torch.zeros((0, 8), dtype=torch.float32),
                "event_probs": torch.zeros((0, 8), dtype=torch.float32),
                "acoustic": torch.zeros((0, 4), dtype=torch.float32),
            },
        )


def run_offline_mvp_teacher_runtime(
    input_audio_path: Path,
    output_dir: Path,
    route_handoff_path: Path | None,
    checkpoint_path: Path | None,
    chunk_samples: int | None,
    chunk_ms: float | None,
    device: str,
    verify_against_full_pass: bool,
    max_audio_sec: float | None,
) -> None:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    resolved_source = resolve_teacher_source(
        route_handoff_path=route_handoff_path,
        experiment_metrics_path=None,
        checkpoint_path=checkpoint_path,
        split_dir=Path("data_prep/round1_1/splits/hybrid_stratified_blocked"),
    )
    checkpoint_payload = load_checkpoint(Path(resolved_source["checkpoint_path"]))
    checkpoint_config = checkpoint_payload.get("config")
    if not isinstance(checkpoint_config, dict):
        raise ValueError("Teacher checkpoint does not contain a valid config payload.")
    model_config = checkpoint_config.get("model")
    if not isinstance(model_config, dict):
        raise ValueError("Teacher checkpoint config.model is missing.")

    resolved_device = resolve_runtime_device(device)
    model = instantiate_offline_mvp_model(dict(model_config))
    model.load_state_dict(checkpoint_payload["model_state_dict"])
    model.eval()
    for parameter in model.parameters():
        parameter.requires_grad_(False)

    waveform, sample_rate = load_waveform(input_audio_path.resolve(), max_duration_sec=max_audio_sec)
    frame_length = int(model_config["frame_length"])
    hop_length = int(model_config["hop_length"])
    effective_chunk_samples = resolve_chunk_samples(
        chunk_samples=chunk_samples,
        chunk_ms=chunk_ms,
        sample_rate=sample_rate,
        frame_length=frame_length,
        hop_length=hop_length,
    )

    runtime = OfflineMVPTeacherRuntime(
        model=model,
        device=resolved_device,
        frame_length=frame_length,
        hop_length=hop_length,
    )
    streaming_outputs = run_streaming_pass(
        runtime=runtime,
        waveform=waveform,
        chunk_samples=effective_chunk_samples,
        sample_rate=sample_rate,
        hidden_dim=int(model_config["hidden_dim"]),
        z_art_dim=int(model_config["z_art_dim"]),
        event_dim=int(model_config["event_dim"]),
        acoustic_dim=int(model_config["acoustic_dim"]),
    )
    verification = None
    full_pass_path = None
    if verify_against_full_pass:
        full_pass_outputs = run_full_pass(
            model=model,
            device=resolved_device,
            waveform=waveform,
        )
        verification = compare_runtime_outputs(
            full_pass_outputs=full_pass_outputs,
            streaming_outputs=streaming_outputs,
        )
        full_pass_path = output_dir / "teacher_runtime_full_pass.pt"
        torch.save(full_pass_outputs, full_pass_path)

    streaming_output_path = output_dir / "teacher_runtime_streaming_outputs.pt"
    torch.save(streaming_outputs, streaming_output_path)

    summary = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "input_audio_path": input_audio_path.resolve().as_posix(),
        "teacher_checkpoint_path": Path(resolved_source["checkpoint_path"]).resolve().as_posix(),
        "teacher_experiment_id": str(resolved_source["teacher_anchor"]["experiment_id"]),
        "route_handoff_path": (
            None
            if resolved_source.get("route_handoff_path") is None
            else Path(resolved_source["route_handoff_path"]).resolve().as_posix()
        ),
        "device": str(resolved_device),
        "sample_rate": int(sample_rate),
        "audio_samples": int(waveform.numel()),
        "audio_sec": round(float(waveform.numel() / sample_rate), 6),
        "frame_length": frame_length,
        "hop_length": hop_length,
        "frame_ms": round(float(frame_length / sample_rate * 1000.0), 6),
        "hop_ms": round(float(hop_length / sample_rate * 1000.0), 6),
        "chunk_samples": int(effective_chunk_samples),
        "chunk_ms": round(float(effective_chunk_samples / sample_rate * 1000.0), 6),
        "streaming_frame_count": int(streaming_outputs["frame_count"]),
        "runtime_outputs_path": streaming_output_path.as_posix(),
        "full_pass_outputs_path": None if full_pass_path is None else full_pass_path.as_posix(),
        "verification": verification,
        "notes": [
            "The runtime wrapper emits only teacher control tensors required for downstream integration.",
            "text_aux is excluded because current runtime does not consume text and pooled text_aux is not stream-critical.",
            "Verification compares chunked runtime outputs against a single full forward pass on the same waveform.",
        ],
    }
    (output_dir / "teacher_runtime_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "teacher_runtime_summary.md").write_text(
        build_runtime_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def resolve_runtime_device(raw_device: str) -> torch.device:
    normalized = str(raw_device).strip().lower()
    if normalized == "auto":
        return torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    if normalized == "cuda":
        return torch.device("cuda:0")
    return torch.device(normalized)


def resolve_chunk_samples(
    chunk_samples: int | None,
    chunk_ms: float | None,
    sample_rate: int,
    frame_length: int,
    hop_length: int,
) -> int:
    if chunk_samples is not None and chunk_ms is not None:
        raise ValueError("Specify either chunk_samples or chunk_ms, not both.")
    if chunk_samples is not None:
        resolved = int(chunk_samples)
    elif chunk_ms is not None:
        resolved = int(round(float(chunk_ms) / 1000.0 * sample_rate))
    else:
        resolved = frame_length * 4
    return max(hop_length, resolved)


def run_streaming_pass(
    runtime: OfflineMVPTeacherRuntime,
    waveform: torch.Tensor,
    chunk_samples: int,
    sample_rate: int,
    hidden_dim: int,
    z_art_dim: int,
    event_dim: int,
    acoustic_dim: int,
) -> dict[str, object]:
    runtime.reset()
    output_chunks: list[OfflineTeacherRuntimeChunk] = []
    cursor = 0
    while cursor < waveform.numel():
        next_cursor = min(waveform.numel(), cursor + chunk_samples)
        output_chunks.append(runtime.push_audio_chunk(waveform[cursor:next_cursor]))
        cursor = next_cursor
    output_chunks.append(runtime.flush())

    empty_tensors = {
        "hidden": torch.zeros((0, hidden_dim), dtype=torch.float32),
        "fused_hidden": torch.zeros((0, hidden_dim), dtype=torch.float32),
        "z_art": torch.zeros((0, z_art_dim), dtype=torch.float32),
        "event_logits": torch.zeros((0, event_dim), dtype=torch.float32),
        "event_probs": torch.zeros((0, event_dim), dtype=torch.float32),
        "acoustic": torch.zeros((0, acoustic_dim), dtype=torch.float32),
    }
    concatenated_outputs: dict[str, torch.Tensor] = {}
    for key in RUNTIME_OUTPUT_KEYS:
        parts = [chunk.outputs[key] for chunk in output_chunks if chunk.frame_count > 0]
        concatenated_outputs[key] = torch.cat(parts, dim=0) if parts else empty_tensors[key]
    frame_start_samples = (
        torch.cat([chunk.frame_start_samples for chunk in output_chunks if chunk.frame_count > 0], dim=0)
        if any(chunk.frame_count > 0 for chunk in output_chunks)
        else torch.zeros((0,), dtype=torch.long)
    )
    return {
        "sample_rate": int(sample_rate),
        "frame_count": int(frame_start_samples.numel()),
        "frame_start_samples": frame_start_samples,
        "frame_start_ms": frame_start_samples.to(torch.float32) / float(sample_rate) * 1000.0,
        **concatenated_outputs,
    }


def run_full_pass(
    model: torch.nn.Module,
    device: torch.device,
    waveform: torch.Tensor,
) -> dict[str, object]:
    waveform_batch = waveform.unsqueeze(0).to(device)
    lengths = torch.tensor([waveform.numel()], dtype=torch.long, device=device)
    with torch.no_grad():
        outputs = model(waveform=waveform_batch, lengths=lengths)
    frame_mask = outputs["frame_mask"][0].to(torch.bool).detach().cpu()
    frame_count = int(frame_mask.sum().item())
    return {
        "frame_count": frame_count,
        "frame_start_samples": torch.arange(frame_count, dtype=torch.long) * int(model.hop_length),
        **{
            key: outputs[key][0, :frame_count].detach().cpu()
            for key in RUNTIME_OUTPUT_KEYS
        },
    }


def compare_runtime_outputs(
    full_pass_outputs: dict[str, object],
    streaming_outputs: dict[str, object],
) -> dict[str, object]:
    full_frame_count = int(full_pass_outputs["frame_count"])
    streaming_frame_count = int(streaming_outputs["frame_count"])
    if full_frame_count != streaming_frame_count:
        raise ValueError(f"Frame count mismatch: {streaming_frame_count} != {full_frame_count}")
    frame_alignment_equal = bool(
        torch.equal(
            full_pass_outputs["frame_start_samples"].to(torch.long),
            streaming_outputs["frame_start_samples"].to(torch.long),
        )
    )
    output_metrics: dict[str, object] = {}
    for key in RUNTIME_OUTPUT_KEYS:
        full_tensor = full_pass_outputs[key].to(torch.float32)
        streaming_tensor = streaming_outputs[key].to(torch.float32)
        diff = (full_tensor - streaming_tensor).abs()
        output_metrics[key] = {
            "shape_equal": list(full_tensor.shape) == list(streaming_tensor.shape),
            "max_abs_diff": round(float(diff.max().item()) if diff.numel() > 0 else 0.0, 9),
            "mean_abs_diff": round(float(diff.mean().item()) if diff.numel() > 0 else 0.0, 9),
            "allclose_atol_5e-6": bool(torch.allclose(full_tensor, streaming_tensor, atol=5e-6, rtol=0.0)),
        }
    return {
        "frame_count_equal": True,
        "frame_alignment_equal": frame_alignment_equal,
        "output_metrics": output_metrics,
    }


def build_runtime_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Offline MVP Teacher Runtime Summary",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- input_audio_path: {summary['input_audio_path']}",
        f"- teacher_experiment_id: {summary['teacher_experiment_id']}",
        f"- teacher_checkpoint_path: {summary['teacher_checkpoint_path']}",
        f"- device: {summary['device']}",
        f"- sample_rate: {summary['sample_rate']}",
        f"- audio_sec: {summary['audio_sec']}",
        f"- frame_length: {summary['frame_length']}",
        f"- hop_length: {summary['hop_length']}",
        f"- frame_ms: {summary['frame_ms']}",
        f"- hop_ms: {summary['hop_ms']}",
        f"- chunk_samples: {summary['chunk_samples']}",
        f"- chunk_ms: {summary['chunk_ms']}",
        f"- streaming_frame_count: {summary['streaming_frame_count']}",
        f"- runtime_outputs_path: {summary['runtime_outputs_path']}",
    ]
    if summary["full_pass_outputs_path"] is not None:
        lines.append(f"- full_pass_outputs_path: {summary['full_pass_outputs_path']}")
    verification = summary.get("verification")
    if isinstance(verification, dict):
        lines.extend(
            [
                "",
                "## Verification",
                f"- frame_count_equal: {verification.get('frame_count_equal')}",
                f"- frame_alignment_equal: {verification.get('frame_alignment_equal')}",
            ]
        )
        output_metrics = verification.get("output_metrics", {})
        if isinstance(output_metrics, dict):
            for key in RUNTIME_OUTPUT_KEYS:
                payload = output_metrics.get(key)
                if not isinstance(payload, dict):
                    continue
                lines.append(
                    f"- {key}: shape_equal={payload.get('shape_equal')} "
                    f"max_abs_diff={payload.get('max_abs_diff')} "
                    f"mean_abs_diff={payload.get('mean_abs_diff')} "
                    f"allclose_atol_5e-6={payload.get('allclose_atol_5e-6')}"
                )
    return "\n".join(lines) + "\n"
