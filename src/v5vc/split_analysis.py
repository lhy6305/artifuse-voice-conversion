from __future__ import annotations

from v5vc.managed_paths import reset_managed_directory

import json
import math
import random
import statistics
from collections import Counter
from pathlib import Path

from v5vc.manifest_builder import load_jsonl

TARGET_VAL_RATIO = 0.1
SOURCE_VAL_RATIO = 0.1
RANDOM_SEED = 20260314
PUNCTUATION_SET = set("，。？！；：、")


def analyze_round1_split_options(
    manifest_dir: Path,
    output_dir: Path,
) -> None:
    manifest_dir = manifest_dir.resolve()
    output_dir = output_dir.resolve()
    options_dir = output_dir / "options"
    reset_managed_directory(output_dir)
    options_dir.mkdir(parents=True, exist_ok=True)

    target_records = load_jsonl(manifest_dir / "target_train.jsonl")
    source_records = load_jsonl(manifest_dir / "source_train.jsonl")

    dataset_summary = {
        "target": summarize_target_population(target_records),
        "source": summarize_source_population(source_records),
    }
    options = build_candidate_options(target_records=target_records, source_records=source_records)

    for option_name, option_payload in options.items():
        option_path = options_dir / f"{option_name}.json"
        option_path.write_text(
            json.dumps(option_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
            newline="\n",
        )

    summary = {
        "manifest_dir": manifest_dir.as_posix(),
        "dataset_summary": dataset_summary,
        "options": options,
        "recommendation": {
            "recommended_option": "hybrid_stratified_blocked",
            "reason": (
                "目标侧当前尾部 8 条全部来自 no_text_voice 子组，源侧当前尾部 8 条全部集中在录音尾部。"
                "推荐将目标主集做分布覆盖抽样，把 no_text_voice 作为单独 challenge eval，"
                "同时把源录音验证集改为跨时间轴的分段 blocked holdout。"
            ),
        },
    }

    (output_dir / "split_analysis_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    (output_dir / "split_analysis_summary.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )



def build_candidate_options(
    target_records: list[dict[str, object]],
    source_records: list[dict[str, object]],
) -> dict[str, dict[str, object]]:
    current_target_val = target_records[-8:]
    current_source_val = source_records[-8:]

    random_target_val_count = max(8, round(len(target_records) * TARGET_VAL_RATIO))
    random_source_val_count = max(8, round(len(source_records) * SOURCE_VAL_RATIO))
    random_target_val, random_target_train = random_split(
        target_records,
        validation_count=random_target_val_count,
        seed=RANDOM_SEED,
    )
    random_source_val, random_source_train = random_split(
        source_records,
        validation_count=random_source_val_count,
        seed=RANDOM_SEED,
    )

    target_special_eval = [
        record for record in target_records if infer_target_group(record) != "<root>"
    ]
    target_main_pool = [
        record for record in target_records if infer_target_group(record) == "<root>"
    ]
    hybrid_target_val_count = max(8, round(len(target_main_pool) * TARGET_VAL_RATIO))
    hybrid_target_val, hybrid_target_train = evenly_spaced_sorted_split(
        target_main_pool,
        validation_count=hybrid_target_val_count,
        sort_key=lambda record: (
            float(record["audio"]["duration_sec"]),
            target_char_count(record),
            target_punctuation_count(record),
            str(record["record_id"]),
        ),
    )
    hybrid_source_val_count = max(8, round(len(source_records) * SOURCE_VAL_RATIO))
    hybrid_source_val, hybrid_source_train = blocked_time_split(
        source_records,
        validation_count=hybrid_source_val_count,
        num_blocks=6,
    )

    return {
        "current_tail_holdout": build_option_payload(
            option_name="current_tail_holdout",
            description="当前实现：目标/源都取尾部 8 条作为固定验证切片。",
            pros=[
                "实现最简单，已在当前训练入口中验证可运行。",
                "源侧尾部切片连续，时间轴泄漏边界少。",
            ],
            cons=[
                "目标侧 8 条全部来自 no_text_voice 子组，严重偏离主训练分布。",
                "源侧 8 条全部位于录音尾部，只覆盖极窄时间区域。",
                "验证样本过少，波动大，不适合作为正式评估拆分。",
            ],
            target_train=target_records[:-8],
            target_val=current_target_val,
            source_train=source_records[:-8],
            source_val=current_source_val,
            target_special_eval=[],
        ),
        "random_split_seed20260314": build_option_payload(
            option_name="random_split_seed20260314",
            description="目标/源都按 10% 做固定随机拆分，使用种子 20260314。",
            pros=[
                "分布覆盖通常优于尾部切片，验证集规模更接近正式训练需求。",
                "实现成本低，后续复现实验方便。",
            ],
            cons=[
                "源侧来自同一长录音，随机拆分会把时间上相邻片段打散到 train/val，泄漏风险高。",
                "目标侧 no_text_voice 子组会混入常规验证集，难以区分主分布和特殊子组表现。",
            ],
            target_train=random_target_train,
            target_val=random_target_val,
            source_train=random_source_train,
            source_val=random_source_val,
            target_special_eval=[],
        ),
        "hybrid_stratified_blocked": build_option_payload(
            option_name="hybrid_stratified_blocked",
            description=(
                "推荐方案：目标主集按时长/文本长度做均匀覆盖抽样，"
                "no_text_voice 8 条单独作为 challenge eval；"
                "源侧按时间轴做跨全局的 blocked holdout。"
            ),
            pros=[
                "目标主验证集更接近主训练分布，同时保留 no_text_voice 独立观察位。",
                "源侧验证集跨越整段录音，分布覆盖明显优于尾部切片。",
                "相比随机拆分，源侧 blocked holdout 能减少相邻片段泄漏。",
            ],
            cons=[
                "实现与维护成本高于随机拆分。",
                "blocked holdout 仍不是严格按语义或场景分层，后续仍需用户确认是否采用。",
            ],
            target_train=hybrid_target_train,
            target_val=hybrid_target_val,
            source_train=hybrid_source_train,
            source_val=hybrid_source_val,
            target_special_eval=target_special_eval,
        ),
    }


def build_option_payload(
    option_name: str,
    description: str,
    pros: list[str],
    cons: list[str],
    target_train: list[dict[str, object]],
    target_val: list[dict[str, object]],
    source_train: list[dict[str, object]],
    source_val: list[dict[str, object]],
    target_special_eval: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "option_name": option_name,
        "description": description,
        "pros": pros,
        "cons": cons,
        "target": {
            "train_count": len(target_train),
            "validation_count": len(target_val),
            "special_eval_count": len(target_special_eval),
            "validation_summary": summarize_target_selection(target_val),
            "special_eval_summary": summarize_target_selection(target_special_eval),
            "validation_record_ids": [record["record_id"] for record in target_val],
            "special_eval_record_ids": [record["record_id"] for record in target_special_eval],
        },
        "source": {
            "train_count": len(source_train),
            "validation_count": len(source_val),
            "validation_summary": summarize_source_selection(source_val),
            "validation_record_ids": [record["record_id"] for record in source_val],
            "boundary_contacts": compute_boundary_contacts(source_train, source_val),
        },
    }


def summarize_target_population(records: list[dict[str, object]]) -> dict[str, object]:
    return {
        "record_count": len(records),
        "duration_sec": summarize_numeric(float(record["audio"]["duration_sec"]) for record in records),
        "clean_char_count": summarize_numeric(target_char_count(record) for record in records),
        "punctuation_ratio": summarize_numeric(target_punctuation_ratio(record) for record in records),
        "group_counts": dict(sorted(Counter(infer_target_group(record) for record in records).items())),
    }


def summarize_source_population(records: list[dict[str, object]]) -> dict[str, object]:
    return {
        "record_count": len(records),
        "duration_sec": summarize_numeric(float(record["audio"]["duration_sec"]) for record in records),
        "start_sec": summarize_numeric(float(record["source_metadata"]["start_sec"]) for record in records),
        "end_sec": summarize_numeric(float(record["source_metadata"]["end_sec"]) for record in records),
    }


def summarize_target_selection(records: list[dict[str, object]]) -> dict[str, object]:
    if not records:
        return {
            "record_count": 0,
            "duration_sec": {},
            "clean_char_count": {},
            "punctuation_ratio": {},
            "group_counts": {},
        }
    return {
        "record_count": len(records),
        "duration_sec": summarize_numeric(float(record["audio"]["duration_sec"]) for record in records),
        "clean_char_count": summarize_numeric(target_char_count(record) for record in records),
        "punctuation_ratio": summarize_numeric(target_punctuation_ratio(record) for record in records),
        "group_counts": dict(sorted(Counter(infer_target_group(record) for record in records).items())),
    }


def summarize_source_selection(records: list[dict[str, object]]) -> dict[str, object]:
    if not records:
        return {
            "record_count": 0,
            "duration_sec": {},
            "start_sec": {},
            "end_sec": {},
        }
    return {
        "record_count": len(records),
        "duration_sec": summarize_numeric(float(record["audio"]["duration_sec"]) for record in records),
        "start_sec": summarize_numeric(float(record["source_metadata"]["start_sec"]) for record in records),
        "end_sec": summarize_numeric(float(record["source_metadata"]["end_sec"]) for record in records),
    }


def summarize_numeric(values: list[float] | tuple[float, ...] | object) -> dict[str, float]:
    values = list(values)
    if not values:
        return {}
    sorted_values = sorted(float(value) for value in values)
    return {
        "min": round(sorted_values[0], 6),
        "p50": round(statistics.median(sorted_values), 6),
        "mean": round(sum(sorted_values) / len(sorted_values), 6),
        "max": round(sorted_values[-1], 6),
    }


def random_split(
    records: list[dict[str, object]],
    validation_count: int,
    seed: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    shuffled = list(records)
    rng = random.Random(seed)
    rng.shuffle(shuffled)
    validation = shuffled[:validation_count]
    validation_ids = {record["record_id"] for record in validation}
    train = [record for record in records if record["record_id"] not in validation_ids]
    return validation, train


def evenly_spaced_sorted_split(
    records: list[dict[str, object]],
    validation_count: int,
    sort_key,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    ordered = sorted(records, key=sort_key)
    effective_validation_count = min(validation_count, max(1, len(ordered) - 1))
    selected_indices: set[int] = set()
    stride = len(ordered) / effective_validation_count
    for slot in range(effective_validation_count):
        index = min(len(ordered) - 1, int((slot + 0.5) * stride))
        while index in selected_indices and index + 1 < len(ordered):
            index += 1
        selected_indices.add(index)
    validation = [ordered[index] for index in sorted(selected_indices)]
    validation_ids = {record["record_id"] for record in validation}
    train = [record for record in records if record["record_id"] not in validation_ids]
    return validation, train


def blocked_time_split(
    records: list[dict[str, object]],
    validation_count: int,
    num_blocks: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    ordered = sorted(records, key=lambda record: float(record["source_metadata"]["start_sec"]))
    effective_validation_count = min(validation_count, max(1, len(ordered) - 1))
    block_count = max(1, min(num_blocks, effective_validation_count))
    base_block_size = effective_validation_count // block_count
    remainder = effective_validation_count % block_count
    chunk_size = math.ceil(len(ordered) / block_count)
    selected_indices: set[int] = set()

    for block_index in range(block_count):
        chunk_start = block_index * chunk_size
        chunk_end = min(len(ordered), (block_index + 1) * chunk_size)
        if chunk_start >= chunk_end:
            continue
        current_block_size = base_block_size + (1 if block_index < remainder else 0)
        current_block_size = min(current_block_size, chunk_end - chunk_start)
        center = (chunk_start + chunk_end) // 2
        start = max(chunk_start, center - current_block_size // 2)
        end = min(chunk_end, start + current_block_size)
        start = max(chunk_start, end - current_block_size)
        for index in range(start, end):
            selected_indices.add(index)

    validation = [ordered[index] for index in sorted(selected_indices)]
    validation_ids = {record["record_id"] for record in validation}
    train = [record for record in records if record["record_id"] not in validation_ids]
    return validation, train


def compute_boundary_contacts(
    train_records: list[dict[str, object]],
    validation_records: list[dict[str, object]],
) -> dict[str, int]:
    all_records = sorted(train_records + validation_records, key=lambda record: float(record["source_metadata"]["start_sec"]))
    validation_ids = {record["record_id"] for record in validation_records}
    train_ids = {record["record_id"] for record in train_records}
    contact_count = 0
    for index, record in enumerate(all_records):
        if record["record_id"] not in validation_ids:
            continue
        left_is_train = index > 0 and all_records[index - 1]["record_id"] in train_ids
        right_is_train = index + 1 < len(all_records) and all_records[index + 1]["record_id"] in train_ids
        if left_is_train:
            contact_count += 1
        if right_is_train:
            contact_count += 1
    return {
        "validation_record_count": len(validation_records),
        "adjacent_train_contacts": contact_count,
    }


def infer_target_group(record: dict[str, object]) -> str:
    original_lab_path = str(record["source_metadata"]["original_lab_path"]).replace("\\", "/")
    parts = [part for part in original_lab_path.split("/") if part]
    return parts[0] if len(parts) > 1 else "<root>"


def target_char_count(record: dict[str, object]) -> int:
    clean_text = str(record["text"]["clean"] or "")
    return len(clean_text)


def target_punctuation_count(record: dict[str, object]) -> int:
    clean_text = str(record["text"]["clean"] or "")
    return sum(1 for char in clean_text if char in PUNCTUATION_SET)


def target_punctuation_ratio(record: dict[str, object]) -> float:
    char_count = max(1, target_char_count(record))
    return target_punctuation_count(record) / char_count


def build_markdown(summary: dict[str, object]) -> str:
    dataset_summary = summary["dataset_summary"]
    options = summary["options"]
    lines = [
        "# round1 训练/验证拆分候选分析",
        "",
        f"- manifest_dir: {summary['manifest_dir']}",
        "",
        "## 全量数据概况",
        f"- target.record_count: {dataset_summary['target']['record_count']}",
        f"- target.group_counts: {json.dumps(dataset_summary['target']['group_counts'], ensure_ascii=False)}",
        f"- target.duration_sec: {json.dumps(dataset_summary['target']['duration_sec'], ensure_ascii=False)}",
        f"- target.clean_char_count: {json.dumps(dataset_summary['target']['clean_char_count'], ensure_ascii=False)}",
        f"- source.record_count: {dataset_summary['source']['record_count']}",
        f"- source.start_sec: {json.dumps(dataset_summary['source']['start_sec'], ensure_ascii=False)}",
        f"- source.duration_sec: {json.dumps(dataset_summary['source']['duration_sec'], ensure_ascii=False)}",
        "",
        "## 当前建议",
        f"- recommended_option: {summary['recommendation']['recommended_option']}",
        f"- reason: {summary['recommendation']['reason']}",
    ]

    for option_name, option in options.items():
        lines.extend(
            [
                "",
                f"## 方案 {option_name}",
                f"- description: {option['description']}",
                f"- target.validation_count: {option['target']['validation_count']}",
                f"- target.special_eval_count: {option['target']['special_eval_count']}",
                f"- target.validation_groups: {json.dumps(option['target']['validation_summary']['group_counts'], ensure_ascii=False)}",
                f"- source.validation_count: {option['source']['validation_count']}",
                f"- source.validation_start_sec: {json.dumps(option['source']['validation_summary']['start_sec'], ensure_ascii=False)}",
                f"- source.boundary_contacts: {json.dumps(option['source']['boundary_contacts'], ensure_ascii=False)}",
                "- pros:",
            ]
        )
        lines.extend(f"  - {item}" for item in option["pros"])
        lines.append("- cons:")
        lines.extend(f"  - {item}" for item in option["cons"])

    lines.extend(
        [
            "",
            "## 产物",
            "- `split_analysis_summary.json` / `split_analysis_summary.md`",
            "- `options/*.json`",
            "",
            "## 注意",
            "- 本报告只生成候选方案，不修改正式训练 manifest。",
            "- 方案最终选择必须由用户确认后再落地到实际训练拆分逻辑。",
        ]
    )
    return "\n".join(lines) + "\n"
