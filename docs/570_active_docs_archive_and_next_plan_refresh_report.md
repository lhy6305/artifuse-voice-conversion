# 570 Active Docs Archive And Next Plan Refresh Report

## Scope
- This round is documentation maintenance only.
- No new experiment, training run, export, or listening task is launched here.

## Why This Archive Pass Was Needed
- The active handoff documents `00/01/02` had started accumulating too much historical material again.
- That made takeover slower and increased the risk that future sessions would read obsolete detail as if it were still active guidance.

## Actions Completed
- Added new archive snapshots:
  - `docs/archive/00_context_bootstrap_snapshot_20260401.md`
  - `docs/archive/01_project_overview_and_plan_snapshot_20260401.md`
  - `docs/archive/02_pitfalls_log_snapshot_20260401.md`
- Rewrote active `docs/00_context_bootstrap.md` into a compact bootstrap document.
- Rewrote active `docs/01_project_overview_and_plan.md` into a compact takeover and next-step document.
- Rewrote active `docs/02_pitfalls_log.md` into a compact active-pitfall set.
- Updated `docs/archive/README.md` so the new snapshots are discoverable.

## Resulting Documentation State
- `00` now points directly at the current upstream fine-structure redesign breakpoint and the latest active reports.
- `01` now states the current project goal, the current stage judgment, and the next implementation plan without carrying old report-by-report history.
- `02` now keeps only the pitfalls that still change current decisions, especially:
  - stop Stage5-local polish once repeated listening still hears the same buzz basin
  - do not confuse oracle sufficiency with deployable producer-side success
  - do not reopen broad Stage5 regularizer search before a new upstream code exists

## Updated Next-Step Plan
- The next work phase should focus on producer-side waveform-geometry code design.
- The implementation order is:
  1. define the deployable fine-structure code contract
  2. wire packet fields and metadata
  3. add Stage3 supervision plumbing
  4. reuse the existing oracle family as the first gate
  5. only then run bounded smoke and oracle validation

## Explicit Non-Actions
- No experiment was advanced in this round.
- No checkpoint ranking changed in this round.
- No listening conclusion changed in this round.
