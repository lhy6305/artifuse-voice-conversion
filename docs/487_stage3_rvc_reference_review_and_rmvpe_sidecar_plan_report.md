# 487 Stage3 RVC reference review and RMVPE sidecar plan report

## Scope
- Review the local reference repository `Retrieval-based-Voice-Conversion-WebUI-7ef1986`.
- Extract the ideas that are relevant to the current Stage3 F0 bottleneck.
- Decide what should be borrowed, what should not be borrowed, and what to do next.
- Record whether the reference repository should remain in the current workspace root.

## Why this review happened
- Stage3 `coarse_log_f0` is now formally diagnosed as structurally blocked in the current waveform-only frontend route.
- The next valid decision is no longer another F0 loss-weight probe.
- The next valid decision is whether Stage3 should consume an explicit pitch expert signal.
- The user additionally confirmed an external prior:
  - RVC realtime mode already uses RMVPE successfully
  - the practical latency is acceptable for realtime use

## Reviewed RVC components
- `README.md`
- `infer/lib/rmvpe.py`
- `infer/lib/rtrvc.py`
- `infer/modules/vc/pipeline.py`
- `infer/modules/vc/modules.py`
- `infer/modules/vc/utils.py`
- `api_240604.py`
- `gui_v1.py`

## Main findings from RVC

### 1. RVC does not force the main model to discover F0 from waveform by itself
- RVC treats F0 extraction as an external expert module.
- The realtime path accepts multiple F0 providers:
  - `pm`
  - `harvest`
  - `crepe`
  - `rmvpe`
  - `fcpe`
- The voice conversion model consumes F0 as an explicit control input instead of requiring its content encoder to recover pitch from raw waveform statistics alone.

### 2. RMVPE is implemented as a strong specialist module, not as a tiny helper
- RVC `RMVPE` is a dedicated mel-based pitch network in `infer/lib/rmvpe.py`.
- It uses:
  - 16 kHz audio
  - 128-bin mel features
  - 10 ms hop
  - U-Net style encoder-decoder
  - recurrent temporal refinement
  - salience-bin decoding instead of direct scalar regression
- This is relevant because the current Stage3 failure mode is exactly the opposite:
  - a small scalar F0 head attached to a waveform frontend collapses to a near-constant mean prediction

### 3. RVC realtime success comes from runtime engineering, not from RMVPE alone
- RVC keeps the RMVPE model resident in memory.
- It extracts F0 only on the required rolling window instead of recomputing full-history signals.
- It maintains pitch caches across blocks.
- It uses:
  - chunked processing
  - resampling
  - overlap handling
  - SOLA alignment
  - crossfade blending
- Therefore the correct conclusion is:
  - RMVPE is realtime-usable when embedded in a suitable runtime
  - not that every naive RMVPE call is automatically free

### 4. RVC accepts modular pragmatism over architectural purity
- RVC combines:
  - HuBERT content features
  - optional FAISS retrieval
  - external F0 extraction
  - generator-side controls
  - runtime overlap alignment
- This is an important design lesson for the current project:
  - if a control variable is structurally hard to recover from the current frontend, it is valid to inject a specialist sidecar rather than insisting on a monolithic pure frontend

### 5. RVC contains ideas worth borrowing beyond RMVPE
- Explicit provider abstraction for interchangeable pitch backends.
- Runtime cache design for blockwise control updates.
- Input and output overlap management for low-latency audio conversion.
- Selective protection logic that reduces damage on fragile regions instead of applying the same transform strength everywhere.
- Consumer-side loudness stabilization.

## What should be borrowed for this project

### Borrow now
- The main idea:
  - treat F0 as an explicit expert signal when the Stage3 waveform-only route fails
- A provider abstraction:
  - `deterministic_extractor_v1`
  - `rmvpe_v1`
- A unified Stage3 pitch sidecar contract:
  - `f0_hz`
  - `log2_f0`
  - `vuv`
  - optional confidence or voiced mask metadata
- The runtime mindset:
  - cache and update low-rate control signals incrementally

### Borrow later if realtime delivery becomes active
- Blockwise cache update pattern
- SOLA or equivalent overlap alignment
- Optional phase-vocoder style overlap refinement
- Explicit latency accounting by block, overlap, and device path

## What should not be borrowed as a mainline decision
- Do not replace the current project with the full RVC architecture.
- Do not adopt retrieval-based feature replacement as the current mainline answer.
- Do not let a black-box retrieval stack hide the unresolved Stage3 control-contract questions.
- Do not use RVC-style generator success as proof that the current project no longer needs explicit control readiness gates.

## Project-specific interpretation
- The current Stage3 problem is not "which F0 loss weight is best".
- The current Stage3 problem is:
  - the current frontend cannot produce a meaningful F0 control from waveform alone
- RVC is useful here because it validates a practical alternative:
  - explicit pitch sidecar input is a normal engineering choice, not a concession of failure

## Recommended next-step plan

### Step A
- Formalize the existing repository acoustic-state extractor as the first official Stage3 pitch provider.
- Purpose:
  - minimal integration cost
  - no new external weights
  - keeps the first structural probe fully reproducible inside the current repo

### Step B
- Add RMVPE as the second official Stage3 pitch provider.
- Purpose:
  - test whether a stronger external pitch expert improves F0 readiness beyond the deterministic extractor
  - keep the provider contract unchanged while swapping the backend

### Step C
- Compare A vs B on the same Stage3 packet and readiness metrics.
- The comparison should decide:
  - whether deterministic extraction is already sufficient
  - whether RMVPE materially improves voiced tracking and useful F0 variance
  - whether the extra runtime dependency is justified

## Retention decision for the local RVC repository
- The reviewed repository does not need to remain in the current workspace root after this review has been captured on disk.
- Recommended policy:
  1. do not keep third-party reference repositories mixed into the main project root long-term
  2. if future code reading is still expected, move it under a clearly marked non-mainline location such as:
     - `tmp/reference_repos/`
     - or another external sibling workspace
  3. if no more direct code reading is expected, remove it after the extracted conclusions are preserved in docs
- Current recommendation:
  - do not treat `Retrieval-based-Voice-Conversion-WebUI-7ef1986` as a permanent root-level project directory

## Final conclusion
- RVC confirms that explicit external F0 extraction is a practical realtime-capable design.
- RMVPE is a valid candidate for this project.
- The best next route is:
  - `A -> B`
  - first integrate the existing deterministic extractor as a formal Stage3 pitch provider
  - then add RMVPE behind the same provider interface
- Keep the lessons, not the full reference repository, as the permanent asset in this workspace.
