# target special_eval 报告

## 目的
本页记录当前 `target_special_eval` 的独立数据级评估结论。

当前阶段的目标不是做模型推理评估，而是先确认：

1. `target_special_eval` 是否与常规 `target_validation` 正确分离
2. 该集合是否仍保持用户确认的 challenge slice 性质

## 命令与产物
当前命令：

- `.\python.exe manage.py evaluate-round1-special-eval --experiment-metrics reports/experiments/EXP-20260314-006-offline-mvp-hybrid-split.metrics.json`
- `.\python.exe manage.py evaluate-offline-mvp-special-eval --experiment-metrics reports/experiments/EXP-20260314-007-offline-mvp-ablation-ready.metrics.json`

当前输出：

- `reports/eval/round1_special_eval/special_eval.json`
- `reports/eval/round1_special_eval/special_eval.md`
- `reports/eval/offline_mvp_special_eval/special_eval_model.json`
- `reports/eval/offline_mvp_special_eval/special_eval_model.md`

## 当前结论
- `overall_ok = True`
- `target_special_eval_record_count = 8`
- 与常规 `target_validation` 完全分离
- 当前 `group_counts = {"no_text_voice": 8}`
- 当前 `punctuation_only_count = 8`

## 当前解释口径
- 当前 `target_special_eval` 是 challenge-only stress slice。
- 这 8 条的 `clean text` 全为单个标点，因此不能把它当作普通内容验证集。
- 它更适合用于单独观察模型在极短、弱内容、近似无文本内容片段上的表现。

## 当前边界
- 数据级结论仍然成立，不应因为后续模型级结果而与常规 validation 混合解释。
- 当前模型级 special eval 已有首轮结果，但它仍基于 3 step 小规模 checkpoint。
- 后续模型级 special eval 结果必须继续与常规 validation 结果分开汇报。

## 当前模型级结论
- `target_validation.loss_total = 21.904232`
- `target_special_eval.loss_total = 18.153472`
- `delta_loss_total = -3.75076`
- `delta_loss_acoustic = -3.85686`
- `delta_loss_text_aux = 0.512051`
- `target_validation.event_prob_mean = 0.504946`
- `target_special_eval.event_prob_mean = 0.504697`

## 当前模型级解释口径
- 当前 special slice 的总 loss 更低，主要因为片段更短、更简单，acoustic 主损失更低。
- 当前 special slice 的 `text_aux` loss 显著更高，符合“文本几乎只剩标点”的预期。
- 用户已额外确认这批样本没有任何完整音节，基本都是喘气等非完整发声。
- 目前没有观察到控制量输出在 special slice 上整体崩坏，但这不等于模型已经通过最终 challenge 检验。

## 下一步
1. 继续在更长的小规模训练 checkpoint 上复查该 special slice。
2. 视需要增加更贴近运行时的非文本评估指标。

## 2026-03-14 非文本指标补强更新
- 已在 `src/v5vc/special_eval.py` 中补入更贴近运行时的非文本统计，并对：
  - `EXP-20260314-020-offline-mvp-c1-4-100step-calibration`
  重新生成模型级 `special_eval`。
- 当前新增指标包括：
  - `z_art_delta_abs_mean`
  - `event_presence_prob_mean`
  - `event_delta_prob_mean`
  - `event_rise_prob_mean`
  - `event_fall_prob_mean`
  - `event_energy_prob_mean`
  - `event_presence_peak_ratio`
  - `acoustic_energy_mean`
  - `acoustic_delta_abs_mean`
- 当前补充结论：
  - special slice 不只是 `text_aux` 更难；
  - 它还表现出：
    - 更低的持续事件激活
    - 更低的能量
    - 更小的时序变化
    - 但更高的 `event presence` 峰值集中度
- 详细报告见：
  - `docs/31_target_special_eval_nontext_metrics_report.md`

## 2026-03-14 large-scale 模型级补充结果
- 实验：
  - `EXP-20260314-011-offline-mvp-large-scale-500`
- final checkpoint：
  - `target_validation.loss_total = 1.752648`
  - `target_special_eval.loss_total = 2.118624`
  - `delta_loss_total = 0.365976`
  - `delta_loss_text_aux = 0.491746`
- 当前补充解释：
  - large-scale 收敛后，special slice 的总 loss 已高于常规 validation。
  - 这更符合它作为 nonverbal challenge slice 的定位。
  - 该结果仍不能直接用于内容保持主结论。
