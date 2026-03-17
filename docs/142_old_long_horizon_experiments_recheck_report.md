# 142. 旧 long-horizon 实验补验证报告

## 背景
- 本轮按 `docs/141_system_assessment_response_to_temp_1_2.md` 的建议，
  对旧 `200-step` long-horizon 实验补做一次制度化复核。
- 目标不是重训，也不是刷新 route，
  而是确认旧实验是否因:
  - `special_eval_series` 缺失
  - `late_step_ratio` 口径不一致
  - 历史 metrics 回写缺口
  导致 checkpoint review 结论失真。

## 本轮范围

### 补跑
- 顺序补跑以下实验的 `special_eval_series(step50/100/150/200)`：
  - `D22`
  - `D33`
  - `D59`
  - `D76`
  - `D77`
  - `D78`
  - `D79`
  - `D80`
  - `D81`
  - `D82`
  - `D83`
  - `D85`
  - `D86`
  - `D87`

### 统一复核
- 对同一批实验重新运行：
  - `checkpoint_selection`
  - `checkpoint_gate_replay`
- 统一显式使用：
  - `late_step_ratio = 0.75`

## 先说结论

### 1. 这轮补验证没有推翻当前阶段口径
- 没有出现:
  - validation leader 刷新
  - special leader 刷新
  - `e_evt` final leader 刷新
  - 新 gate 在 aggregate 上改写当前阶段判断

### 2. 这轮真正补齐的是“历史实验可复核性”
- 补跑前，这串老实验普遍存在：
  - `checkpoint_series_eval` 已在
  - 但 `special_eval_series` 缺失
- 因而它们没法被同一套 checkpoint-selection / gate replay 正式纳入。
- 这次补的是制度闭环，不是模型行为。

### 3. `late075` 口径下，旧 long-horizon 的 checkpoint 结论整体更稳了
- 所有 `200-step` 实验的 late window 都明确变成：
  - `step150 + step200`
- 因而：
  - `D86 step150`
  - `D87 step150`
  这类 late-stop option 被稳定地重新纳入正式复核。

## 补验证前的直接发现
- 对 `D76-D87` 逐个检查后发现：
  - 全部已有 `checkpoint_series_eval`
  - 全部缺 `special_eval_series`
- 这说明问题不是某一个实验损坏，
  而是这一串历史实验的 metrics 一直没有处在“checkpoint review 就绪”状态。

## 统一 checkpoint-selection 结果

### cross experiment summary
- best final validation:
  - `D76 @ step200`
- best final special:
  - `D82 @ step200`
- best final `e_evt`:
  - `D79 @ step200`
- best positive-control late special:
  - `D82 @ step150`
- best validation-guarded special:
  - `D82 @ step150`

### 解释
- 这说明本轮补验证后，
  old long-horizon 的 final / late 两层里最稳定的结论仍是：
  - `D76 final` 继续负责 validation
  - `D82 final` 继续负责 final special
  - `D79 final` 继续负责 final `e_evt`
  - `D82 step150` 是当前这批旧实验里最强的 positive-control late special 点

### 对当前阶段口径的影响
- 这不会自动改写当前 route 口径。
- 因为：
  - `checkpoint-selection` 这里是在做 cross-experiment late candidate review
  - 不是在直接刷新 full route 的 official role
- 但它证明：
  - 旧 long-horizon 家族现在已经能在统一 late075 口径下被稳定比较

## 统一 gate replay 结果

### aggregate
- 所有 late special gate 在本轮都收敛到同一组 aggregate：
  - `mean_delta_vs_final_validation = +0.034245`
  - `mean_delta_vs_final_special = -0.009003`
  - `mean_delta_vs_final_e_evt = +0.107213`
  - `mean_delta_vs_final_z_art = +0.006517`

### 解释
- 这说明在当前这批 `200-step` 实验里，
  late window 只有 `step150 / step200` 两个候选时，
  各种 special-oriented gate 实际没有再分出新的制度差异。
- 更直白地说：
  - gate 名字不同
  - 但选中的 checkpoint 基本已收敛到同一层逻辑

### 关键判断
- late-stop 在 aggregate 上仍有价值：
  - special 平均更好
  - `e_evt` 平均更好
  - `z_art` 平均仍是正收益
- 但它没有形成：
  - 一个能在 aggregate 上联合打赢 final anchor 的新 gate 制度

## 对几个关键旧实验的补充判断

### `D81`
- 本轮复核后，`D81 step150` 仍表现为：
  - special 略好
  - 但 `e_evt / z_art` 都低于 final
- 这与此前“`z_art_influence` late retarget 无法改写当前结构”的负结论一致。

### `D86`
- `D86 step150` 继续是有效 late-stop。
- 在本轮统一口径下，
  它仍保有显著的 dual-control 改善：
  - `zero_e_evt` 相对 final 继续大幅上升
  - `zero_z_art` 相对 final 继续显著上升
- 这说明此前围绕 `D86 step150` 的判断不是偶然值。

### `D87`
- `D87 step150` 继续是有效 late-stop。
- 但在跨旧实验的统一 checkpoint-selection 里，
  它没有把 “best positive-control late special” 从 `D82 step150` 手里接走。
- 因此：
  - `D87` 的制度价值仍更接近：
    - 通过 final 改写 default / minimax
    - 并让 `step150` 继续承担更强 `e_evt` / special checkpoint-option
  - 而不是“在所有旧实验 late checkpoint 里变成无条件总冠军”

## 本轮补验证后的正式判断

### 1. 旧 long-horizon 实验的 checkpoint review 现在已恢复到可统一使用状态
- 后续若再需要做 old-family route / gate / checkpoint 复核，
  不需要再先补这批 series 字段。

### 2. 当前阶段主结论不变
- validation 仍看 `D76`
- final special 仍看 `D82`
- final `e_evt` 仍看 `D79`
- `D86/D87 step150` 这类 late-stop option 仍成立

### 3. 这轮更像“补账”，不是“刷新路线”
- 它提高了历史实验的可审计性。
- 但没有产生一个需要改写阶段路线的新实验赢家。

## 产物
- `reports/eval/offline_mvp_special_eval_series_d22_200step_exp013_recheck/`
- `reports/eval/offline_mvp_special_eval_series_d33_200step_exp015_recheck/`
- `reports/eval/offline_mvp_special_eval_series_d59_200step_exp014_recheck/`
- `reports/eval/offline_mvp_special_eval_series_d76_exp20260316_032_recheck/`
- `reports/eval/offline_mvp_special_eval_series_d77_exp20260316_033_recheck/`
- `reports/eval/offline_mvp_special_eval_series_d78_exp20260316_034_recheck/`
- `reports/eval/offline_mvp_special_eval_series_d79_exp20260316_035_recheck/`
- `reports/eval/offline_mvp_special_eval_series_d80_exp20260316_036_recheck/`
- `reports/eval/offline_mvp_special_eval_series_d81_exp20260316_037_recheck/`
- `reports/eval/offline_mvp_special_eval_series_d82_exp20260316_038_recheck/`
- `reports/eval/offline_mvp_special_eval_series_d83_exp20260316_039_recheck/`
- `reports/eval/offline_mvp_special_eval_series_d85_exp20260316_041_recheck/`
- `reports/eval/offline_mvp_special_eval_series_d86_exp20260316_042_recheck/`
- `reports/eval/offline_mvp_special_eval_series_d87_exp20260316_043_recheck/`
- `reports/eval/offline_mvp_checkpoint_selection_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_d85_d86_d87_late075/`
- `reports/eval/offline_mvp_checkpoint_gate_replay_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_d85_d86_d87_late075/`
