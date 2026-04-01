# Archive Directory Notes

## Purpose
- This directory stores large historical snapshots of the main handoff documents.
- These files are for historical recovery and old-stage tracing, not for default takeover reading.

## Current Snapshots
- `00_context_bootstrap_snapshot_20260401.md`
  - full pre-compression snapshot of active `00` taken during the 2026-04-01 archive pass
- `01_project_overview_and_plan_snapshot_20260326.md`
  - pre-compression long-form `01` snapshot from 2026-03-26
- `01_project_overview_and_plan_snapshot_20260328.md`
  - active-history snapshot of `01` from 2026-03-28
- `01_project_overview_and_plan_snapshot_20260401.md`
  - full pre-compression snapshot of active `01` taken during the 2026-04-01 archive pass
- `02_pitfalls_log_snapshot_20260326.md`
  - pre-compression long-form `02` snapshot from 2026-03-26
- `02_pitfalls_log_snapshot_20260328.md`
  - active-history snapshot of `02` from 2026-03-28
- `02_pitfalls_log_snapshot_20260401.md`
  - full pre-compression snapshot of active `02` taken during the 2026-04-01 archive pass

## Usage Rules
- Read these first by default:
  - `docs/00_context_bootstrap.md`
  - `docs/01_project_overview_and_plan.md`
  - `docs/02_pitfalls_log.md`
- Only enter `docs/archive/` when old long-form history is actually needed.
- If `00/01/02` become bulky again, add new date-stamped snapshots here before compressing the active versions.
