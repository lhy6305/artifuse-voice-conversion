from __future__ import annotations

from collections import Counter


NATURAL_FINAL_ANCHOR = "natural_final_anchor"
HORIZON_EQUALIZATION_ANCHOR = "horizon_equalization_anchor"
CHECKPOINT_OPTION_ANCHOR = "checkpoint_option_anchor"


def infer_reference_horizon(rows: list[dict[str, object]]) -> int | None:
    natural_steps = [
        int(row.get("completed_steps", 0))
        for row in rows
        if not is_synthetic_checkpoint_anchor(row) and int(row.get("completed_steps", 0)) > 0
    ]
    candidate_steps = natural_steps or [
        int(row.get("completed_steps", 0)) for row in rows if int(row.get("completed_steps", 0)) > 0
    ]
    if not candidate_steps:
        return None
    counts = Counter(candidate_steps)
    return max(counts.items(), key=lambda item: (item[1], item[0]))[0]


def is_synthetic_checkpoint_anchor(payload: dict[str, object]) -> bool:
    experiment_id = str(payload.get("experiment_id", ""))
    experiment_metrics_path = str(payload.get("experiment_metrics_path", ""))
    return "checkpoint-step" in experiment_id or ".checkpoint-step" in experiment_metrics_path


def classify_anchor(
    payload: dict[str, object],
    reference_horizon_completed_steps: int | None,
) -> str:
    if not is_synthetic_checkpoint_anchor(payload):
        return NATURAL_FINAL_ANCHOR

    completed_steps = int(payload.get("completed_steps", 0))
    if (
        reference_horizon_completed_steps is not None
        and reference_horizon_completed_steps > 0
        and completed_steps == reference_horizon_completed_steps
    ):
        return HORIZON_EQUALIZATION_ANCHOR
    return CHECKPOINT_OPTION_ANCHOR


def build_anchor_governance(
    payload: dict[str, object],
    reference_horizon_completed_steps: int | None,
) -> dict[str, object]:
    anchor_class = classify_anchor(
        payload=payload,
        reference_horizon_completed_steps=reference_horizon_completed_steps,
    )
    note = build_anchor_governance_note(
        experiment_id=str(payload["experiment_id"]),
        anchor_class=anchor_class,
        reference_horizon_completed_steps=reference_horizon_completed_steps,
        completed_steps=int(payload.get("completed_steps", 0)),
    )
    return {
        "anchor_class": anchor_class,
        "is_synthetic_checkpoint_anchor": is_synthetic_checkpoint_anchor(payload),
        "reference_horizon_completed_steps": reference_horizon_completed_steps,
        "formal_default_eligible": anchor_class == NATURAL_FINAL_ANCHOR,
        "shadow_matched_horizon_eligible": anchor_class in {NATURAL_FINAL_ANCHOR, HORIZON_EQUALIZATION_ANCHOR},
        "note": note,
    }


def annotate_anchor(
    payload: dict[str, object],
    reference_horizon_completed_steps: int | None,
) -> dict[str, object]:
    annotated = dict(payload)
    annotated["governance"] = build_anchor_governance(
        payload=payload,
        reference_horizon_completed_steps=reference_horizon_completed_steps,
    )
    return annotated


def build_route_governance_summary(
    route_anchor: dict[str, object],
    alternatives: dict[str, dict[str, object]],
    reference_horizon_completed_steps: int | None,
) -> dict[str, object]:
    checkpoint_option_ids = unique_strings([
        str(item["experiment_id"])
        for item in alternatives.values()
        if str(item["governance"]["anchor_class"]) == CHECKPOINT_OPTION_ANCHOR
    ])
    horizon_equalization_ids = unique_strings([
        str(item["experiment_id"])
        for item in alternatives.values()
        if str(item["governance"]["anchor_class"]) == HORIZON_EQUALIZATION_ANCHOR
    ])
    route_anchor_class = str(route_anchor["governance"]["anchor_class"])

    if route_anchor_class == NATURAL_FINAL_ANCHOR:
        summary_line = (
            f"Formal default remains final-only: {route_anchor['experiment_id']} is a natural final anchor "
            "and remains eligible for official handoff/stage-report wording."
        )
        if checkpoint_option_ids:
            guardrail_line = (
                "Synthetic checkpoint alternatives "
                f"{', '.join(checkpoint_option_ids)} stay option-only and should not be promoted into the formal default route "
                "unless route policy is explicitly upgraded."
            )
        elif horizon_equalization_ids:
            guardrail_line = (
                "Synthetic checkpoint alternatives "
                f"{', '.join(horizon_equalization_ids)} align to the matched horizon and can support shadow comparisons, "
                "but official handoff/stage-report wording should remain final-only."
            )
        else:
            guardrail_line = (
                "No synthetic checkpoint anchor is currently affecting the formal default wording."
            )
    elif route_anchor_class == HORIZON_EQUALIZATION_ANCHOR:
        summary_line = (
            f"{route_anchor['experiment_id']} is a synthetic horizon-equalization anchor aligned to the "
            f"{reference_horizon_completed_steps}-step reference horizon."
        )
        guardrail_line = (
            "Treat this output as matched-horizon shadow wording only; do not paste it as the official fixed handoff "
            "or stage-report default without an explicit policy override."
        )
    else:
        summary_line = (
            f"{route_anchor['experiment_id']} is a synthetic checkpoint-option anchor rather than a natural final anchor."
        )
        guardrail_line = (
            "Treat this output as checkpoint-selection or option-study wording only; do not upgrade it into the formal "
            "default route without an explicit governance change."
        )

    return {
        "reference_horizon_completed_steps": reference_horizon_completed_steps,
        "route_anchor_class": route_anchor_class,
        "checkpoint_option_ids": checkpoint_option_ids,
        "horizon_equalization_ids": horizon_equalization_ids,
        "summary_line": summary_line,
        "guardrail_line": guardrail_line,
    }


def build_anchor_governance_note(
    experiment_id: str,
    anchor_class: str,
    reference_horizon_completed_steps: int | None,
    completed_steps: int,
) -> str:
    if anchor_class == NATURAL_FINAL_ANCHOR:
        return (
            f"{experiment_id} is a natural final anchor and is eligible for official/fixed handoff wording."
        )
    if anchor_class == HORIZON_EQUALIZATION_ANCHOR:
        return (
            f"{experiment_id} is a synthetic checkpoint anchor aligned to the {reference_horizon_completed_steps}-step "
            "reference horizon; use it for matched-horizon shadow comparisons, not as the formal default anchor."
        )
    return (
        f"{experiment_id} is a synthetic checkpoint option at step {completed_steps}; keep it in checkpoint-selection, "
        "gate replay, or option-study lanes unless route policy is explicitly upgraded."
    )


def build_alternative_reference_line(payload: dict[str, object], purpose_label: str) -> str:
    anchor_class = str(payload["governance"]["anchor_class"])
    if anchor_class == NATURAL_FINAL_ANCHOR:
        return f"cite {payload['experiment_id']} only when {purpose_label} is explicitly requested"
    if anchor_class == HORIZON_EQUALIZATION_ANCHOR:
        return (
            f"cite {payload['experiment_id']} only inside matched-horizon shadow wording when {purpose_label} is needed"
        )
    return (
        f"cite {payload['experiment_id']} only as a checkpoint option when {purpose_label} is needed, not as a new default anchor"
    )


def unique_strings(items: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        unique.append(item)
    return unique
