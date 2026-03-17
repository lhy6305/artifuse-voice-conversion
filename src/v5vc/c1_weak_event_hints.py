from __future__ import annotations

import json
import shutil
from collections import Counter
from pathlib import Path

from v5vc.data_scan import summarize_numeric, write_json
from v5vc.manifest_builder import load_jsonl


PAUSE_PUNCTUATION = {"，": "pause_comma", "、": "pause_enumeration", "；": "pause_semicolon", "：": "pause_colon"}
TERMINAL_PUNCTUATION = {"。": "terminal_period", "？": "terminal_question", "！": "terminal_exclamation"}
ALL_PUNCTUATION = set(PAUSE_PUNCTUATION) | set(TERMINAL_PUNCTUATION)


def build_c1_weak_event_hints(
    split_dir: Path,
    data_output_dir: Path,
    report_output_dir: Path,
    frame_length: int,
    hop_length: int,
) -> None:
    split_dir = split_dir.resolve()
    data_output_dir = data_output_dir.resolve()
    report_output_dir = report_output_dir.resolve()
    reset_managed_directory(data_output_dir)
    reset_managed_directory(report_output_dir)

    target_records = []
    for split_name, filename in (
        ("target_train", "target_train.jsonl"),
        ("target_validation", "target_validation.jsonl"),
        ("target_special_eval", "target_special_eval.jsonl"),
    ):
        for record in load_jsonl(split_dir / filename):
            target_records.append((split_name, record))

    hint_rows = [build_hint_row(split_name, record, frame_length, hop_length) for split_name, record in target_records]
    summary = build_summary(
        split_dir=split_dir,
        hint_rows=hint_rows,
        frame_length=frame_length,
        hop_length=hop_length,
    )

    write_jsonl(data_output_dir / "target_weak_event_hints.jsonl", hint_rows)
    write_json(report_output_dir / "weak_event_hints_summary.json", summary)
    (report_output_dir / "weak_event_hints_summary.md").write_text(
        build_markdown(summary),
        encoding="utf-8",
        newline="\n",
    )


def reset_managed_directory(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def build_hint_row(
    split_name: str,
    record: dict[str, object],
    frame_length: int,
    hop_length: int,
) -> dict[str, object]:
    text = str(record["text"]["clean"] or "")
    duration_sec = float(record["audio"]["duration_sec"])
    sample_rate = int(record["audio"].get("sample_rate", 44100))
    lexical_char_count = sum(1 for char in text if char not in ALL_PUNCTUATION)
    estimated_frame_count = estimate_frame_count(
        duration_sec=duration_sec,
        sample_rate=sample_rate,
        frame_length=frame_length,
        hop_length=hop_length,
    )
    pause_boundaries, terminal_boundaries = extract_boundaries(
        text=text,
        lexical_char_count=lexical_char_count,
        frame_count=estimated_frame_count,
    )
    clause_spans = extract_clause_spans(
        text=text,
        lexical_char_count=lexical_char_count,
        frame_count=estimated_frame_count,
    )
    utterance_structure_type = infer_utterance_structure_type(
        lexical_char_count=lexical_char_count,
        clause_count=len(clause_spans),
        terminal_boundary_count=len(terminal_boundaries),
    )
    final_terminal_type = infer_final_terminal_type(text)
    return {
        "record_id": str(record["record_id"]),
        "split": split_name,
        "audio_path": str(record["audio_path"]),
        "duration_sec": round(duration_sec, 6),
        "sample_rate": sample_rate,
        "estimated_frame_count": estimated_frame_count,
        "text_clean": text,
        "lexical_char_count": lexical_char_count,
        "nonverbal_only": lexical_char_count == 0,
        "pause_boundary_count": len(pause_boundaries),
        "terminal_boundary_count": len(terminal_boundaries),
        "pause_boundaries": pause_boundaries,
        "terminal_boundaries": terminal_boundaries,
        "clause_count": len(clause_spans),
        "clause_spans": clause_spans,
        "utterance_structure_type": utterance_structure_type,
        "final_terminal_type": final_terminal_type,
        "structure_flags": {
            "has_pause_and_terminal": bool(pause_boundaries and terminal_boundaries),
            "multi_pause": len(pause_boundaries) >= 2,
            "multi_terminal": len(terminal_boundaries) >= 2,
            "multi_clause": len(clause_spans) >= 2,
            "question_utterance": final_terminal_type == "terminal_question",
            "exclamation_utterance": final_terminal_type == "terminal_exclamation",
        },
    }


def estimate_frame_count(
    duration_sec: float,
    sample_rate: int,
    frame_length: int,
    hop_length: int,
) -> int:
    total_samples = max(int(round(duration_sec * sample_rate)), frame_length)
    return max(1, ((total_samples - frame_length) // hop_length) + 1)


def extract_boundaries(
    text: str,
    lexical_char_count: int,
    frame_count: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    pause_boundaries: list[dict[str, object]] = []
    terminal_boundaries: list[dict[str, object]] = []
    lexical_index = 0
    for char_index, char in enumerate(text):
        if char in ALL_PUNCTUATION:
            if lexical_char_count <= 0 or lexical_index <= 0:
                continue
            lexical_ratio = lexical_index / lexical_char_count
            frame_index = min(frame_count - 1, max(0, int(round(lexical_ratio * max(0, frame_count - 1)))))
            payload = {
                "symbol": char,
                "symbol_type": PAUSE_PUNCTUATION.get(char, TERMINAL_PUNCTUATION.get(char, "unknown")),
                "char_index": char_index,
                "lexical_index": lexical_index,
                "lexical_ratio": round(lexical_ratio, 6),
                "frame_index": frame_index,
            }
            if char in PAUSE_PUNCTUATION:
                pause_boundaries.append(payload)
            else:
                terminal_boundaries.append(payload)
            continue
        lexical_index += 1
    return pause_boundaries, terminal_boundaries


def extract_clause_spans(
    text: str,
    lexical_char_count: int,
    frame_count: int,
) -> list[dict[str, object]]:
    clause_spans: list[dict[str, object]] = []
    if lexical_char_count <= 0:
        return clause_spans

    clause_start_char_index: int | None = None
    clause_start_lexical_index: int | None = None
    lexical_index = 0

    for char_index, char in enumerate(text):
        if char in ALL_PUNCTUATION:
            if clause_start_char_index is None or clause_start_lexical_index is None or lexical_index <= clause_start_lexical_index:
                continue
            clause_spans.append(
                build_clause_span(
                    clause_index=len(clause_spans),
                    clause_start_char_index=clause_start_char_index,
                    clause_end_char_index=char_index - 1,
                    clause_start_lexical_index=clause_start_lexical_index,
                    clause_end_lexical_index=lexical_index - 1,
                    boundary_symbol=char,
                    lexical_char_count=lexical_char_count,
                    frame_count=frame_count,
                )
            )
            clause_start_char_index = None
            clause_start_lexical_index = None
            continue

        if clause_start_char_index is None:
            clause_start_char_index = char_index
            clause_start_lexical_index = lexical_index
        lexical_index += 1

    if clause_start_char_index is not None and clause_start_lexical_index is not None and lexical_index > clause_start_lexical_index:
        clause_spans.append(
            build_clause_span(
                clause_index=len(clause_spans),
                clause_start_char_index=clause_start_char_index,
                clause_end_char_index=max(clause_start_char_index, len(text) - 1),
                clause_start_lexical_index=clause_start_lexical_index,
                clause_end_lexical_index=lexical_index - 1,
                boundary_symbol=None,
                lexical_char_count=lexical_char_count,
                frame_count=frame_count,
            )
        )

    clause_count = len(clause_spans)
    for clause_index, clause in enumerate(clause_spans):
        clause["role"] = infer_clause_role(clause_index=clause_index, clause_count=clause_count)
    return clause_spans


def build_clause_span(
    clause_index: int,
    clause_start_char_index: int,
    clause_end_char_index: int,
    clause_start_lexical_index: int,
    clause_end_lexical_index: int,
    boundary_symbol: str | None,
    lexical_char_count: int,
    frame_count: int,
) -> dict[str, object]:
    boundary_symbol_type = "none"
    if boundary_symbol is not None:
        boundary_symbol_type = PAUSE_PUNCTUATION.get(
            boundary_symbol,
            TERMINAL_PUNCTUATION.get(boundary_symbol, "unknown"),
        )
    lexical_start_ratio = clause_start_lexical_index / lexical_char_count
    lexical_end_ratio = (clause_end_lexical_index + 1) / lexical_char_count
    frame_start_index = lexical_progress_to_frame_index(
        lexical_ratio=lexical_start_ratio,
        frame_count=frame_count,
    )
    frame_end_index = lexical_progress_to_frame_index(
        lexical_ratio=lexical_end_ratio,
        frame_count=frame_count,
    )
    return {
        "clause_index": clause_index,
        "char_start_index": clause_start_char_index,
        "char_end_index": clause_end_char_index,
        "lexical_start_index": clause_start_lexical_index,
        "lexical_end_index": clause_end_lexical_index,
        "lexical_char_count": (clause_end_lexical_index - clause_start_lexical_index) + 1,
        "lexical_start_ratio": round(lexical_start_ratio, 6),
        "lexical_end_ratio": round(lexical_end_ratio, 6),
        "frame_start_index": frame_start_index,
        "frame_end_index": frame_end_index,
        "closing_symbol": boundary_symbol,
        "closing_symbol_type": boundary_symbol_type,
    }


def lexical_progress_to_frame_index(
    lexical_ratio: float,
    frame_count: int,
) -> int:
    return min(frame_count - 1, max(0, int(round(lexical_ratio * max(0, frame_count - 1)))))


def infer_clause_role(
    clause_index: int,
    clause_count: int,
) -> str:
    if clause_count <= 1:
        return "single"
    if clause_index == 0:
        return "initial"
    if clause_index == clause_count - 1:
        return "final"
    return "middle"


def infer_final_terminal_type(text: str) -> str:
    for char in reversed(text):
        if char in TERMINAL_PUNCTUATION:
            return TERMINAL_PUNCTUATION[char]
        if char in PAUSE_PUNCTUATION:
            return "none"
    return "none"


def infer_utterance_structure_type(
    lexical_char_count: int,
    clause_count: int,
    terminal_boundary_count: int,
) -> str:
    if lexical_char_count <= 0:
        return "nonverbal"
    if terminal_boundary_count >= 2:
        return "multi_terminal"
    if clause_count <= 1 and terminal_boundary_count >= 1:
        return "single_clause_terminal"
    if clause_count >= 2 and terminal_boundary_count == 1:
        return "multi_clause_single_terminal"
    return "other"


def build_summary(
    split_dir: Path,
    hint_rows: list[dict[str, object]],
    frame_length: int,
    hop_length: int,
) -> dict[str, object]:
    split_counter = Counter(str(row["split"]) for row in hint_rows)
    final_terminal_counter = Counter(str(row["final_terminal_type"]) for row in hint_rows)
    utterance_structure_counter = Counter(str(row["utterance_structure_type"]) for row in hint_rows)
    pause_boundary_total = sum(int(row["pause_boundary_count"]) for row in hint_rows)
    terminal_boundary_total = sum(int(row["terminal_boundary_count"]) for row in hint_rows)
    lexical_rows = [row for row in hint_rows if not bool(row["nonverbal_only"])]
    pause_rows = [row for row in lexical_rows if int(row["pause_boundary_count"]) > 0]
    terminal_rows = [row for row in lexical_rows if int(row["terminal_boundary_count"]) > 0]
    return {
        "split_dir": split_dir.as_posix(),
        "record_count": len(hint_rows),
        "split_counts": dict(sorted(split_counter.items())),
        "frame_length": frame_length,
        "hop_length": hop_length,
        "nonverbal_only_count": sum(1 for row in hint_rows if bool(row["nonverbal_only"])),
        "records_with_pause_boundaries": len(pause_rows),
        "records_with_terminal_boundaries": len(terminal_rows),
        "pause_boundary_total": pause_boundary_total,
        "terminal_boundary_total": terminal_boundary_total,
        "final_terminal_type_counts": dict(sorted(final_terminal_counter.items())),
        "utterance_structure_type_counts": dict(sorted(utterance_structure_counter.items())),
        "lexical_char_count_stats": summarize_numeric(
            [int(row["lexical_char_count"]) for row in hint_rows]
        ),
        "clause_count_stats": summarize_numeric(
            [int(row["clause_count"]) for row in hint_rows]
        ),
        "estimated_frame_count_stats": summarize_numeric(
            [int(row["estimated_frame_count"]) for row in hint_rows]
        ),
        "pause_boundaries_per_lexical_record_stats": summarize_numeric(
            [int(row["pause_boundary_count"]) for row in lexical_rows]
        ) if lexical_rows else {},
        "terminal_boundaries_per_lexical_record_stats": summarize_numeric(
            [int(row["terminal_boundary_count"]) for row in lexical_rows]
        ) if lexical_rows else {},
        "notes": [
            "Weak event hints are target-side only and remain fully offline.",
            "Boundary positions are estimated from clean text punctuation and lexical progress, not forced alignment.",
            "These sidecars are intended as route-C bootstrap assets for later e_evt supervision experiments.",
        ],
    }


def write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def build_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# `C1` 弱事件提示 sidecar 摘要",
        "",
        "## 总览",
        f"- 记录数: `{summary['record_count']}`",
        f"- split_counts: `{summary['split_counts']}`",
        f"- nonverbal_only_count: `{summary['nonverbal_only_count']}`",
        f"- records_with_pause_boundaries: `{summary['records_with_pause_boundaries']}`",
        f"- records_with_terminal_boundaries: `{summary['records_with_terminal_boundaries']}`",
        f"- pause_boundary_total: `{summary['pause_boundary_total']}`",
        f"- terminal_boundary_total: `{summary['terminal_boundary_total']}`",
        "",
        "## 句末类型分布",
        f"- final_terminal_type_counts: `{summary['final_terminal_type_counts']}`",
        "",
        "## 句型结构分布",
        f"- utterance_structure_type_counts: `{summary['utterance_structure_type_counts']}`",
        f"- clause_count_stats: `{summary['clause_count_stats']}`",
        "",
        "## 说明",
        "- 当前边界位置来自文本标点和字面进度的弱估计，不是强制对齐。",
        "- 这批 sidecar 的目标是为后续 route-C 提供 target-side 弱事件监督底账。",
        "- 当前 sidecar 已补充 clause 级跨度与句型结构类型，供后续 richer label expression 使用。",
    ]
    return "\n".join(lines) + "\n"
