from __future__ import annotations

import json
import shutil
from pathlib import Path

from v5vc.data_scan import summarize_numeric, write_json
from v5vc.manifest_builder import load_jsonl


def evaluate_round1_baseline(
    manifest_dir: Path,
    output_dir: Path,
    experiment_metrics_path: Path | None,
    r_res_enabled: bool,
) -> None:
    manifest_dir = manifest_dir.resolve()
    output_dir = output_dir.resolve()
    reset_managed_directory(output_dir)

    target_records = load_jsonl(manifest_dir / "target_train.jsonl")
    source_records = load_jsonl(manifest_dir / "source_train.jsonl")
    combined_records = load_jsonl(manifest_dir / "combined_round1.jsonl")

    result = build_baseline_result(
        target_records=target_records,
        source_records=source_records,
        combined_records=combined_records,
        r_res_enabled=r_res_enabled,
    )

    write_json(output_dir / "baseline_eval.json", result)
    write_markdown(output_dir / "baseline_eval.md", result)

    if experiment_metrics_path is not None:
        update_experiment_metrics(experiment_metrics_path.resolve(), result)


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def build_baseline_result(
    target_records: list[dict[str, object]],
    source_records: list[dict[str, object]],
    combined_records: list[dict[str, object]],
    r_res_enabled: bool,
) -> dict[str, object]:
    target_durations = [float(record["audio"]["duration_sec"]) for record in target_records]
    source_durations = [float(record["audio"]["duration_sec"]) for record in source_records]
    target_text_nonempty = sum(1 for record in target_records if record["text"]["clean"])
    target_text_runtime_required = sum(
        1 for record in target_records if record["labels"]["text_is_runtime_required"]
    )
    source_text_present = sum(1 for record in source_records if record["text"]["clean"])

    checks = {
        "target_manifest_nonempty": len(target_records) > 0,
        "source_manifest_nonempty": len(source_records) > 0,
        "combined_manifest_matches_parts": len(combined_records) == len(target_records) + len(source_records),
        "target_text_coverage_full": target_text_nonempty == len(target_records),
        "source_text_absent_expected": source_text_present == 0,
        "runtime_text_not_required": target_text_runtime_required == 0,
        "r_res_disabled_required": not r_res_enabled,
    }

    ablation_slots = {
        "z_art_ablation": "pending",
        "e_evt_ablation": "pending",
        "r_res_ablation": "pending",
        "latency_measurement": "pending",
    }

    return {
        "overall_ok": all(checks.values()),
        "checks": checks,
        "summary": {
            "target_record_count": len(target_records),
            "source_record_count": len(source_records),
            "combined_record_count": len(combined_records),
            "target_duration_stats_sec": summarize_numeric(target_durations),
            "source_duration_stats_sec": summarize_numeric(source_durations),
        },
        "ablation_slots": ablation_slots,
        "notes": [
            "offline MVP baseline still expects r_res to remain disabled",
            "target text is available only for training-side alignment and supervision",
            "source training candidates currently do not carry text",
        ],
    }


def write_markdown(path: Path, result: dict[str, object]) -> None:
    lines = [
        "# round1 离线 MVP 基线评估",
        "",
        f"- overall_ok: {result['overall_ok']}",
        "",
        "## 检查项",
    ]
    for key, value in result["checks"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## 数据摘要",
            f"- target_record_count: {result['summary']['target_record_count']}",
            f"- source_record_count: {result['summary']['source_record_count']}",
            f"- combined_record_count: {result['summary']['combined_record_count']}",
            "",
            "## 消融槽位",
        ]
    )
    for key, value in result["ablation_slots"].items():
        lines.append(f"- {key}: {value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_experiment_metrics(path: Path, result: dict[str, object]) -> None:
    if path.exists():
        payload = json.loads(path.read_text(encoding="utf-8"))
    else:
        payload = {
            "experiment_id": path.stem.replace(".metrics", ""),
            "status": "initialized",
            "created_at": None,
            "metrics": {},
            "notes": [],
        }

    payload["metrics"]["baseline_eval"] = result
    payload["status"] = "baseline_evaluated"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
