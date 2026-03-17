from __future__ import annotations

import json
import shutil
from pathlib import Path

from v5vc.data_scan import write_json, write_manifest
from v5vc.manifest_builder import load_jsonl


def materialize_round1_split(
    manifest_dir: Path,
    option_path: Path,
    output_dir: Path,
) -> None:
    manifest_dir = manifest_dir.resolve()
    option_path = option_path.resolve()
    output_dir = output_dir.resolve()

    reset_managed_directory(output_dir)

    option = json.loads(option_path.read_text(encoding="utf-8"))
    target_records = load_jsonl(manifest_dir / "target_train.jsonl")
    source_records = load_jsonl(manifest_dir / "source_train.jsonl")
    target_index = {record["record_id"]: record for record in target_records}
    source_index = {record["record_id"]: record for record in source_records}

    target_val_ids = list(option["target"]["validation_record_ids"])
    target_special_eval_ids = list(option["target"]["special_eval_record_ids"])
    source_val_ids = list(option["source"]["validation_record_ids"])

    target_val = gather_records(target_index, target_val_ids, label="target.validation_record_ids")
    target_special_eval = gather_records(
        target_index,
        target_special_eval_ids,
        label="target.special_eval_record_ids",
    )
    source_val = gather_records(source_index, source_val_ids, label="source.validation_record_ids")

    target_excluded_ids = set(target_val_ids) | set(target_special_eval_ids)
    source_excluded_ids = set(source_val_ids)
    target_train = [record for record in target_records if record["record_id"] not in target_excluded_ids]
    source_train = [record for record in source_records if record["record_id"] not in source_excluded_ids]

    write_manifest(output_dir / "target_train.jsonl", target_train)
    write_manifest(output_dir / "target_validation.jsonl", target_val)
    write_manifest(output_dir / "target_special_eval.jsonl", target_special_eval)
    write_manifest(output_dir / "source_train.jsonl", source_train)
    write_manifest(output_dir / "source_validation.jsonl", source_val)

    summary = {
        "option_name": option["option_name"],
        "description": option["description"],
        "source_option_path": option_path.as_posix(),
        "source_manifest_dir": manifest_dir.as_posix(),
        "counts": {
            "target_train": len(target_train),
            "target_validation": len(target_val),
            "target_special_eval": len(target_special_eval),
            "source_train": len(source_train),
            "source_validation": len(source_val),
        },
    }
    write_json(output_dir / "split_summary.json", summary)
    (output_dir / "split_summary.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )
    write_json(
        output_dir / "split_assignment.json",
        {
            "option_name": option["option_name"],
            "target_validation_record_ids": target_val_ids,
            "target_special_eval_record_ids": target_special_eval_ids,
            "source_validation_record_ids": source_val_ids,
        },
    )


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def gather_records(
    index: dict[str, dict[str, object]],
    record_ids: list[str],
    label: str,
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for record_id in record_ids:
        if record_id not in index:
            raise KeyError(f"Missing record id {record_id!r} in {label}")
        records.append(index[record_id])
    return records


def build_markdown(summary: dict[str, object]) -> str:
    return "\n".join(
        [
            "# round1 正式 split 摘要",
            "",
            f"- option_name: {summary['option_name']}",
            f"- description: {summary['description']}",
            f"- source_option_path: {summary['source_option_path']}",
            f"- source_manifest_dir: {summary['source_manifest_dir']}",
            "",
            "## 计数",
            f"- target_train: {summary['counts']['target_train']}",
            f"- target_validation: {summary['counts']['target_validation']}",
            f"- target_special_eval: {summary['counts']['target_special_eval']}",
            f"- source_train: {summary['counts']['source_train']}",
            f"- source_validation: {summary['counts']['source_validation']}",
        ]
    ) + "\n"
