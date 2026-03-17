from __future__ import annotations

from collections import Counter
from datetime import datetime
import json
from pathlib import Path

from v5vc.manifest_builder import load_jsonl
from v5vc.offline_mvp.data import (
    attach_target_special_supervision,
    attach_target_weak_event_hints,
    load_target_special_supervision_map,
    load_target_weak_event_hint_map,
)


IMPORTANT_POOL_NAMES = (
    "challenge_proxy_core",
    "challenge_proxy_relaxed",
    "micro_pause_none_singleton_strict",
    "micro_singleton_anypunct_expansion",
    "structural_multi_terminal",
    "structural_question_exclaim",
    "structural_clause_ge4",
    "structural_clause_ge4_no_final_terminal",
)


def build_streaming_student_calibration_assets(
    config_path: Path,
    data_output_dir: Path,
    report_output_dir: Path,
    split_dir: Path | None,
    target_duration_sec: float,
    max_records: int,
) -> None:
    config_path = config_path.resolve()
    data_output_dir = data_output_dir.resolve()
    report_output_dir = report_output_dir.resolve()
    data_output_dir.mkdir(parents=True, exist_ok=True)
    report_output_dir.mkdir(parents=True, exist_ok=True)

    config = json.loads(config_path.read_text(encoding="utf-8"))
    split_dir = resolve_split_dir(config_path=config_path, config=config, split_dir=split_dir)
    target_train_records = load_jsonl(split_dir / "target_train.jsonl")

    target_weak_event_hints_path = resolve_optional_path(
        config_path=config_path,
        raw_value=config.get("data", {}).get("target_weak_event_hints_path"),
    )
    if target_weak_event_hints_path is not None and target_weak_event_hints_path.exists():
        target_train_records = attach_target_weak_event_hints(
            target_train_records,
            load_target_weak_event_hint_map(target_weak_event_hints_path),
        )

    target_special_supervision_path = resolve_optional_path(
        config_path=config_path,
        raw_value=config.get("data", {}).get("target_special_supervision_path"),
    )
    if target_special_supervision_path is not None and target_special_supervision_path.exists():
        target_train_records = attach_target_special_supervision(
            target_train_records,
            load_target_special_supervision_map(target_special_supervision_path),
        )

    selection = select_calibration_records(
        records=target_train_records,
        target_duration_sec=float(target_duration_sec),
        max_records=int(max_records),
    )
    summary = build_calibration_summary(
        config_path=config_path,
        split_dir=split_dir,
        config=config,
        selection=selection,
        target_duration_sec=float(target_duration_sec),
        max_records=int(max_records),
    )
    asset_template = build_asset_template(config=config, summary=summary)

    selected_records_path = data_output_dir / "target_calibration_records.jsonl"
    selected_records_path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in selection["records"]) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    asset_template_path = data_output_dir / "streaming_student_calibration_asset_template.json"
    asset_template_path.write_text(
        json.dumps(asset_template, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )

    summary_json_path = report_output_dir / "streaming_student_calibration_summary.json"
    summary_md_path = report_output_dir / "streaming_student_calibration_summary.md"
    summary_json_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    summary_md_path.write_text(
        build_markdown(
            summary=summary,
            asset_template_path=asset_template_path,
            selected_records_path=selected_records_path,
        ),
        encoding="utf-8",
        newline="\n",
    )


def resolve_split_dir(
    config_path: Path,
    config: dict[str, object],
    split_dir: Path | None,
) -> Path:
    if split_dir is not None:
        return split_dir.resolve()
    raw_value = config.get("data", {}).get("split_dir")
    if raw_value in {None, ""}:
        raise ValueError("split_dir is required for calibration asset planning.")
    return (config_path.parent.parent / str(raw_value)).resolve()


def resolve_optional_path(config_path: Path, raw_value: object) -> Path | None:
    if raw_value in {None, ""}:
        return None
    return (config_path.parent.parent / str(raw_value)).resolve()


def select_calibration_records(
    records: list[dict[str, object]],
    target_duration_sec: float,
    max_records: int,
) -> dict[str, object]:
    tag_frequency: Counter[str] = Counter()
    candidates: list[dict[str, object]] = []
    for record in records:
        duration_sec = float(record["audio"]["duration_sec"])
        tags = build_record_tags(record)
        for tag in tags:
            tag_frequency[tag] += 1
        candidates.append(
            {
                "record": record,
                "record_id": str(record["record_id"]),
                "duration_sec": duration_sec,
                "tags": tags,
            }
        )

    selected: list[dict[str, object]] = []
    selected_ids: set[str] = set()
    covered_tags: set[str] = set()
    total_duration_sec = 0.0
    min_records = min(6, max(1, max_records))

    while len(selected) < min_records:
        best_candidate: dict[str, object] | None = None
        best_score: float | None = None
        for candidate in candidates:
            if candidate["record_id"] in selected_ids:
                continue
            new_tags = [tag for tag in candidate["tags"] if tag not in covered_tags]
            rarity_bonus = sum(1.0 / max(1, tag_frequency[tag]) for tag in new_tags)
            overshoot = max(0.0, total_duration_sec + float(candidate["duration_sec"]) - target_duration_sec)
            score = (
                len(new_tags) * 100.0
                + rarity_bonus * 25.0
                - float(candidate["duration_sec"]) * 0.35
                - overshoot * 0.2
            )
            if total_duration_sec >= target_duration_sec and len(selected) >= min_records:
                score -= overshoot * 2.0
            if best_score is None or score > best_score:
                best_candidate = candidate
                best_score = score
        if best_candidate is None:
            break
        selected.append(best_candidate)
        selected_ids.add(best_candidate["record_id"])
        covered_tags.update(best_candidate["tags"])
        total_duration_sec += float(best_candidate["duration_sec"])

    while len(selected) < max_records and total_duration_sec < target_duration_sec:
        best_candidate = None
        best_score = None
        for candidate in candidates:
            if candidate["record_id"] in selected_ids:
                continue
            new_tags = [tag for tag in candidate["tags"] if tag not in covered_tags]
            overshoot = max(0.0, total_duration_sec + float(candidate["duration_sec"]) - target_duration_sec)
            score = (
                float(candidate["duration_sec"]) * 1.5
                + len(new_tags) * 15.0
                - overshoot * 0.1
            )
            if best_score is None or score > best_score:
                best_candidate = candidate
                best_score = score
        if best_candidate is None:
            break
        selected.append(best_candidate)
        selected_ids.add(best_candidate["record_id"])
        covered_tags.update(best_candidate["tags"])
        total_duration_sec += float(best_candidate["duration_sec"])

    selected_records = [dict(item["record"]) for item in selected]
    return {
        "records": selected_records,
        "record_ids": [str(record["record_id"]) for record in selected_records],
        "total_duration_sec": round(total_duration_sec, 6),
        "covered_tags": sorted(covered_tags),
    }


def build_record_tags(record: dict[str, object]) -> list[str]:
    tags: set[str] = set()
    duration_sec = float(record["audio"]["duration_sec"])
    lexical_char_count = len(str(record.get("text", {}).get("clean") or ""))
    tags.add(f"duration_bucket:{bucketize_duration(duration_sec)}")
    tags.add(f"text_bucket:{bucketize_text_length(lexical_char_count)}")

    weak_event_hints = record.get("weak_event_hints")
    if isinstance(weak_event_hints, dict):
        tags.add(f"structure:{str(weak_event_hints.get('utterance_structure_type', 'unknown'))}")
        tags.add(f"final_terminal:{str(weak_event_hints.get('final_terminal_type', 'unknown'))}")
        if int(weak_event_hints.get("pause_boundary_count", 0)) >= 2:
            tags.add("pause:multi")
        if int(weak_event_hints.get("terminal_boundary_count", 0)) >= 1:
            tags.add("terminal:present")
        if int(weak_event_hints.get("clause_count", 0)) >= 4:
            tags.add("clause:ge4")
        if bool(weak_event_hints.get("nonverbal_only", False)):
            tags.add("content:nonverbal_only")
        else:
            tags.add("content:lexical")

    target_special_supervision = record.get("target_special_supervision")
    if isinstance(target_special_supervision, dict):
        tags.add(
            f"special_duration_ceiling:{bool(target_special_supervision.get('within_special_duration_ceiling', False))}"
        )
        special_proximity = float(target_special_supervision.get("special_proximity_score", 0.0))
        if special_proximity >= 0.3:
            tags.add("special_proximity:high")
        elif special_proximity >= 0.15:
            tags.add("special_proximity:mid")
        else:
            tags.add("special_proximity:low")
        memberships = dict(target_special_supervision.get("pool_memberships", {}))
        for pool_name in IMPORTANT_POOL_NAMES:
            if bool(memberships.get(pool_name, False)):
                tags.add(f"pool:{pool_name}")

    return sorted(tags)


def bucketize_duration(duration_sec: float) -> str:
    if duration_sec < 4.0:
        return "short"
    if duration_sec < 8.0:
        return "mid"
    return "long"


def bucketize_text_length(char_count: int) -> str:
    if char_count < 10:
        return "short"
    if char_count < 30:
        return "mid"
    return "long"


def build_calibration_summary(
    config_path: Path,
    split_dir: Path,
    config: dict[str, object],
    selection: dict[str, object],
    target_duration_sec: float,
    max_records: int,
) -> dict[str, object]:
    selected_records = list(selection["records"])
    weak_event_rows = [
        record.get("weak_event_hints")
        for record in selected_records
        if isinstance(record.get("weak_event_hints"), dict)
    ]
    supervision_rows = [
        record.get("target_special_supervision")
        for record in selected_records
        if isinstance(record.get("target_special_supervision"), dict)
    ]
    structure_counts = Counter(str(row.get("utterance_structure_type", "unknown")) for row in weak_event_rows)
    final_terminal_counts = Counter(str(row.get("final_terminal_type", "unknown")) for row in weak_event_rows)
    pool_counts = Counter()
    for row in supervision_rows:
        for pool_name, is_member in dict(row.get("pool_memberships", {})).items():
            if bool(is_member):
                pool_counts[str(pool_name)] += 1

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "config_path": config_path.as_posix(),
        "split_dir": split_dir.as_posix(),
        "asset_version": "stage3_calibration_asset_v1",
        "selection_policy": {
            "target_duration_sec": round(target_duration_sec, 6),
            "max_records": int(max_records),
            "selection_mode": "coverage_greedy",
        },
        "selection_summary": {
            "selected_record_count": len(selected_records),
            "selected_total_duration_sec": float(selection["total_duration_sec"]),
            "selected_record_ids": list(selection["record_ids"]),
            "covered_tags": list(selection["covered_tags"]),
            "utterance_structure_type_counts": dict(sorted(structure_counts.items())),
            "final_terminal_type_counts": dict(sorted(final_terminal_counts.items())),
            "pool_membership_counts": dict(sorted(pool_counts.items())),
        },
        "conditioning_contract": {
            "speaker_embed_dim": int(config["model"]["speaker_embed_dim"]),
            "geom_embed_dim": int(config["model"]["geom_embed_dim"]),
            "alpha_parameterization": "global_scalar",
            "alpha_default_value": 1.0,
            "alpha_suggested_bounds": [0.85, 1.15],
        },
        "notes": [
            "This stage only selects calibration records and writes a placeholder conditioning asset template.",
            "Current selection uses structural diversity already available in weak_event_hints and target_special_supervision sidecars.",
            "The output is a bootstrap asset scaffold, not a learned s_spk_target / s_geom_target / alpha estimate.",
        ],
    }


def build_asset_template(
    config: dict[str, object],
    summary: dict[str, object],
) -> dict[str, object]:
    speaker_dim = int(config["model"]["speaker_embed_dim"])
    geom_dim = int(config["model"]["geom_embed_dim"])
    return {
        "asset_version": "stage3_calibration_asset_v1",
        "status": "template_ready",
        "generated_at": summary["generated_at"],
        "selection_summary": summary["selection_summary"],
        "conditioning_assets": {
            "s_spk_target": {
                "dim": speaker_dim,
                "status": "placeholder_zero_vector",
                "vector": [0.0] * speaker_dim,
            },
            "s_geom_target": {
                "dim": geom_dim,
                "status": "placeholder_zero_vector",
                "vector": [0.0] * geom_dim,
            },
            "alpha": {
                "parameterization": "global_scalar",
                "status": "placeholder_identity",
                "value": 1.0,
                "suggested_bounds": [0.85, 1.15],
            },
        },
        "estimation_contract": {
            "selected_record_ids": summary["selection_summary"]["selected_record_ids"],
            "selected_total_duration_sec": summary["selection_summary"]["selected_total_duration_sec"],
            "required_outputs": ["s_spk_target", "s_geom_target", "alpha"],
        },
        "notes": [
            "Replace placeholder vectors after a real calibration estimation step is implemented.",
            "Keep the dimensions aligned with streaming_student_stage_template.json unless the Stage3 contract is intentionally changed.",
        ],
    }


def build_markdown(
    summary: dict[str, object],
    asset_template_path: Path,
    selected_records_path: Path,
) -> str:
    selection_summary = summary["selection_summary"]
    contract = summary["conditioning_contract"]
    lines = [
        "# Stage3 Streaming Student Calibration Asset Summary",
        "",
        f"- generated_at: {summary['generated_at']}",
        f"- config_path: {summary['config_path']}",
        f"- split_dir: {summary['split_dir']}",
        f"- asset_version: {summary['asset_version']}",
        "",
        "## Selection",
        f"- selected_record_count: {selection_summary['selected_record_count']}",
        f"- selected_total_duration_sec: {selection_summary['selected_total_duration_sec']}",
        f"- target_duration_sec: {summary['selection_policy']['target_duration_sec']}",
        f"- max_records: {summary['selection_policy']['max_records']}",
        "",
        "## Conditioning Contract",
        f"- speaker_embed_dim: {contract['speaker_embed_dim']}",
        f"- geom_embed_dim: {contract['geom_embed_dim']}",
        f"- alpha_parameterization: {contract['alpha_parameterization']}",
        f"- alpha_default_value: {contract['alpha_default_value']}",
        "",
        "## Coverage",
        f"- utterance_structure_type_counts: {json.dumps(selection_summary['utterance_structure_type_counts'], ensure_ascii=False)}",
        f"- final_terminal_type_counts: {json.dumps(selection_summary['final_terminal_type_counts'], ensure_ascii=False)}",
        f"- pool_membership_counts: {json.dumps(selection_summary['pool_membership_counts'], ensure_ascii=False)}",
        f"- covered_tags: {json.dumps(selection_summary['covered_tags'], ensure_ascii=False)}",
        "",
        "## Artifacts",
        f"- selected_records_path: {selected_records_path.as_posix()}",
        f"- asset_template_path: {asset_template_path.as_posix()}",
        "",
        "## Notes",
    ]
    for note in summary["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"
