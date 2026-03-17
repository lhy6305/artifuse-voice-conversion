# 133. `round1.1 / context restore continuation` 报告

## 背景
- 上一次对话已经在 `docs/119` 做过一次恢复。
- 但之后主线继续推进到了 `D82 / D83`，
  并且 route / governance / stage-report 代码也在中间发生了实装扩展。
- 本轮目标不是直接新开实验，
  而是把“现在磁盘上真实停在哪里、哪些能力已可直接复用、下一步真正该问什么”重新钉牢。

## 本次恢复范围
### 按规范读取
- 已用 UTF-8 显式读取:
  - `docs/00_context_bootstrap.md`
  - `docs/01_project_overview_and_plan.md`
  - `docs/02_pitfalls_log.md`
  - `initial_design.md`
  - `initial_design_judg.md`

### 已补读的关键专题文档
- long-horizon 最新链路:
  - `docs/126_round1_1_d77_official_validation_family_long_horizon_probe_report.md`
  - `docs/127_round1_1_d78_d76_near_neighbor_control_restore_probe_report.md`
  - `docs/128_round1_1_d79_d76_near_neighbor_teacherweight_probe_report.md`
  - `docs/129_round1_1_d80_d79_zart_weight_probe_report.md`
  - `docs/130_round1_1_d81_d79_zart_influence_retarget_probe_report.md`
  - `docs/131_round1_1_d82_d79_fullpriority_singleton_exposure_probe_report.md`
  - `docs/132_round1_1_d83_d79_phase_late_teacher_handoff_probe_report.md`

### 已核对代码入口
- `manage.py`
  - 仍会检查解释器并提示使用仓库根目录 `python.exe`
- `src/v5vc/cli.py`
  - 已接入:
    - matched-horizon shadow
    - anchor route analysis / selection / recap
    - handoff doc / stage report
- `src/v5vc/horizon_policy_shadow.py`
  - matched-horizon shadow bundle 已实装
- `src/v5vc/route_governance.py`
  - 已能区分:
    - `natural_final_anchor`
    - `horizon_equalization_anchor`
    - `checkpoint_option_anchor`
- `src/v5vc/handoff_summary.py`
  - handoff summary 已接入 governance guardrail
- `src/v5vc/stage_report.py`
  - stage report 已显式渲染 governance 信息
- `src/v5vc/experiment.py`
  - `init-experiment` 仍是按当前文件数顺序抢号，不能并发

### 已核对关键配置
- 当前最新 long-horizon 配置:
  - `configs/offline_mvp_train_d79_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_late_teacherweight_boost_200step_smallscale_seeded_shuffle.json`
  - `configs/offline_mvp_train_d82_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_late_teacherweight_fullpriority_200step_smallscale_seeded_shuffle.json`
  - `configs/offline_mvp_train_d83_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d33to22late_teacher_handoff_200step_smallscale_seeded_shuffle.json`

## 当前真实状态
### 1. official quick-screen 没变
- 当前 official quick-screen 仍是:
  - validation = `D71`
  - default_minimax = `D22`
  - special / `e_evt` / `z_art` = `D33`
- 解释:
  - 后续 long-horizon 与近邻 probe 并没有改写 official fixed handoff 口径。

### 2. matched20 shadow 仍是窄 family 问题，不是老 anchor 回归
- 当前恢复口径保持:
  - `D71` / `D72` 仍是 matched20 shadow 需要重点解释的点
  - 它已经不是“回到 `D22`”，
    而是收缩到 `D70 family`

### 3. full long-horizon 已推进到 `D83`，但四角色稳定
直接从
- `reports/eval/offline_mvp_anchor_routes_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83/anchor_route_analysis.json`
- `reports/eval/offline_mvp_anchor_route_selection_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_default_minimax/anchor_route_selection.json`
- `reports/eval/offline_mvp_route_recap_round1_1_longwindow_d22_d33_d59_d76_d77_d78_d79_d80_d81_d82_d83_default_minimax/route_recap.json`

可确认当前四角色是:
- validation = `D76`
- special = `D82`
- `e_evt` = `D79`
- default_minimax + `z_art` = `D33`

对应阈值:
- `budget_to_minimax_anchor = 0.014763`
- `budget_to_special_anchor = 0.040968`
- `best_e_evt_floor = 2.170294`
- `best_z_art_floor = 0.710849`

### 4. `D80 / D81 / D83` 都是负结果，`D82` 只是 special-only 推进
- `D80`
  - `late z_art_weight` 抬升，结果被 `D79` 完整支配
- `D81`
  - `z_art_influence_aux` retarget 到 late pool，机制命中了，但仍未补回 `z_art`
- `D82`
  - full-priority singleton exposure 确实把 special leader 从 `D79` 推到 `D82`
  - 但没有补回 `z_art`
- `D83`
  - `D33 -> D22` phase-specific late teacher handoff 已确认真实生效
  - 但 final 仍被 `D79` 完整支配

## 当前代码与流程可直接复用的能力
1. 可以继续直接做 long-horizon 训练 + final eval + checkpoint series + special eval series。
2. 可以直接生成 matched-horizon shadow bundle，不用手工拼 route/comparison/recap。
3. 可以直接生成带 governance guardrail 的:
   - route handoff
   - handoff document
   - stage report
4. 可以在训练日志里直接验证 phase-specific teacher handoff 是否真实生效。

## 当前真正待决策的分叉
### 不再值得继续优先做的方向
- `late teacher source handoff`
- `teacher_consistency.z_art_weight` 小幅扫参
- `z_art_influence_aux` 的 late-pool retarget
- 当前 singleton proxy cohort 的更强曝光 sweep

这些方向要么已经明确负结果，
要么只会把路线继续推成 special-only，
但不会解决当前 long-horizon 的 `z_art` 缺口。

### 当前更像下一步主问题的方向
- 是否存在:
  - 不依赖 late teacher source handoff
  - 比当前 singleton exposure 更外层
  - 且更直接面向 `z_art`
  的 restoration / supervision 机制

## 当前建议
- 默认把接下来的问题表述成:
  - “找新的更外层 `z_art` restoration 机制”
  - 而不是“继续在 `D79` 周围拧旧旋钮”

先说人话:
- 现在不是仓库乱了，
  也不是上次干到哪忘了。
- 当前事实已经很清楚:
  - 旧旋钮基本拧完了
  - 继续拧，大概率只是换一种方式回到同样结论
- 真正值得继续花实验预算的，
  是换一个更外层的问题。

## 操作纪律
1. 所有 Python 命令继续显式使用:
   - `.\python.exe manage.py ...`
2. `init-experiment` 继续顺序执行，不并发。
3. 恢复状态时同时核对:
   - official quick-screen
   - matched20 shadow
   - full long-horizon route
4. 评估非模板实验时，继续显式传:
   - `--config <对应训练配置>`
5. 任何 checkpoint 路径都不要靠目录命名猜，
   一律以:
   - `reports/experiments/*.metrics.json`
   - route 产物里的 `checkpoint_path`
   为准。
