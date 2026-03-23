# 2026-03-23 Stage5 hard-case failure signature 报告

## 结论
- 本轮在
  `docs/266`
  的
  `pattern_summary`
  基础上，
  又补了一层
  `failure_signature`。
- 当前这 3 条 corrected hard cases
  已经可以更明确地写成：
  1. `target::chapter3_3_firefly_162`
     - `boundary_high_motion_flux_gap`
  2. `target::chapter3_17_firefly_133`
     - `interior_high_motion_flux_gap`
  3. `target::chapter3_6_firefly_106`
     - `steady_zero_target_jitter`

先说人话：
- 这 3 条 hard cases
  的共同点
  不是
  “delta 还不够强”，
  而是：
  - 在当前
    `delta_lambda=1.5`
    `flux_lambda=2.0`
    口径下，
    它们的失败优势
    都主要由
    `flux`
    侧贡献。
- 真正把它们分开的，
  是 target transition
  落在什么 regime：
  - 一条主要输在
    边界高运动窗口
  - 一条主要输在
    interior 高运动窗口
  - 还有一条
    明显带
    near-zero / plateau
    抖动问题

## 本轮工程动作

### 1. 给 hard-case breakdown 正式补了 `failure_signature`
- 文件：
  - `src/v5vc/stage5_waveform_objective_collapse_probe.py`
- 当前新增字段：
  - `failure_signature`
- 当前输出的核心量包括：
  - `component_label`
  - `signature_label`
  - `target_transition_strength_q25/q75`
  - `low/high_motion_advantage_share`
  - `boundary/interior_high_motion_advantage_share`
  - `near_zero_target_advantage_share_0p1`
  - `near_zero_reference_oracle_error_advantage_share_0p1`
  - `flux_dominant_advantage_share`
  - `delta_dominant_advantage_share`

### 2. 这层 summary 的目的
- 不是再给 hard case
  换一个名字，
- 而是把
  “到底是边界高运动、
  interior 高运动，
  还是近零稳态抖动”
  这个差异正式量化，
  避免继续靠人工读窗口。

## 当前 hard-case failure signatures

### 1. `target::chapter3_3_firefly_162`
- `pattern_label = boundary_dominated`
- `signature_label = boundary_high_motion_flux_gap`
- `component_label = flux_dominated`
- 关键量化：
  - `flux_dominant_advantage_share = 0.980406`
  - `boundary_share = 0.848822`
  - `boundary_high_motion_advantage_share_q75 = 0.247853`
  - `near_zero_target_advantage_share_0p1 = 0.0`
- 这说明：
  - 它不是 plateau / near-zero 型问题
  - 主要是
    边界高运动窗口里，
    baseline 的 flux-side mismatch
    比 fixed-template oracle 更差

### 2. `target::chapter3_17_firefly_133`
- `pattern_label = mixed_failure`
- `signature_label = interior_high_motion_flux_gap`
- `component_label = flux_dominated`
- 关键量化：
  - `flux_dominant_advantage_share = 0.889372`
  - `boundary_share = 0.090681`
  - `interior_high_motion_advantage_share_q75 = 0.340417`
  - `near_zero_target_advantage_share_0p1 = 0.0`
- 这说明：
  - 它虽然有醒目的 onset / offset anchor，
    但更主要的问题
    仍然在 interior 高运动窗口
  - 继续只盯边界
    已经不够

### 3. `target::chapter3_6_firefly_106`
- `pattern_label = mixed_failure`
- `signature_label = steady_zero_target_jitter`
- `component_label = flux_dominated`
- 关键量化：
  - `flux_dominant_advantage_share = 0.818928`
  - `near_zero_target_advantage_share_0p1 = 0.161233`
  - `near_zero_reference_oracle_error_advantage_share_0p1 = 0.161233`
  - dominant window:
    - `5.333333s ~ 5.340590s`
- 这说明：
  - 它和前两条
    不该再写成同一类
  - 当前最醒目的失败
    就是：
    - target transition
      几乎为零
    - oracle 也几乎零误差
    - 但 baseline
      仍残留明显 jitter / flux mismatch

## 当前判断
- 当前更准确的实验线结论应更新为：
  1. corrected hard cases
     不是
     `delta-side`
     约束不足
     这么简单
  2. 当前三条 hard cases
     都更像：
     - `flux-dominated`
       failure
  3. 它们的真正差异
     在于：
     - boundary high-motion
     - interior high-motion
     - near-zero steady-window

## 对下一步的直接含义
1. 下一步不该先回去做：
   - 更大范围的
     `delta/flux`
     权重扫网格
2. 更合理的下一题应改成：
   - 继续停留在离线 probe 层，
     直接做
     flux-side targeted diagnosis
3. 当前最自然的拆法是：
   - `chapter3_3_firefly_162`
     - boundary high-motion flux
       targeted diagnosis
   - `chapter3_17_firefly_133`
     - interior high-motion flux
       targeted diagnosis
   - `chapter3_6_firefly_106`
     - near-zero plateau jitter
       targeted diagnosis

## 产物
- 更新后的 probe 输出目录：
  - `reports/runtime/stage5_waveform_objective_collapse_probe_round1_1/`
- 当前新增可复查字段：
  - `failure_signature`

## 一句话结论
- 当前 corrected hard cases
  的共性已经收紧成：
  - 都是
    `flux-dominated`
    failure；
- 差异则应正式写成：
  - `boundary high-motion`
  - `interior high-motion`
  - `steady zero-target jitter`
