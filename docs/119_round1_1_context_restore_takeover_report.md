# 119. `round1.1 / context restore + takeover state` 报告

## 背景
- 上一轮对话因上下文过长被迫中止。
- 本轮任务不是直接开新实验，
  而是先把当前工作状态从磁盘完整恢复出来，
  确认:
  - 最近一轮到底停在哪
  - 哪些代码和流程已经落地
  - 接下来真正待决策的分叉点是什么

## 本次恢复范围
### 按规范读取
- 已使用 UTF-8 显式读取:
  - `docs/00_context_bootstrap.md`
  - `docs/01_project_overview_and_plan.md`
  - `docs/02_pitfalls_log.md`
  - `initial_design.md`
  - `initial_design_judg.md`

### 已核对代码入口
- `manage.py`
  - 已具备仓库 `python.exe` 路径 / 版本 warning
- `src/v5vc/cli.py`
  - 已接入 `build-offline-mvp-matched-horizon-shadow`
- `src/v5vc/horizon_policy_shadow.py`
  - matched-horizon shadow bundle 自动化已落地
- `src/v5vc/experiment.py`
  - `init-experiment` 仍按现有文件数分配编号，
    所以并行初始化仍会抢号

### 已核对最新配置与产物
- 最新训练配置:
  - `configs/offline_mvp_train_d70_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_teacher_gate_late_20step_smallscale_seeded_shuffle.json`
  - `configs/offline_mvp_train_d72_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_teacher_source_d22late_20step_smallscale_seeded_shuffle.json`
  - `configs/offline_mvp_train_d73_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22like_latehandoff_20step_smallscale_seeded_shuffle.json`
- 最新实验记录:
  - `D70 = EXP-20260316-025`
  - `D71 = EXP-20260316-026`
  - `D72 = EXP-20260316-027`
  - `D73 = EXP-20260316-029`
- 已核对最新评估产物:
  - official quick-screen:
    - `reports/eval/offline_mvp_anchor_routes_round1_1_d22_d29_d33_d60_d68_d69_d70_d71_d72_d73/`
  - matched20 shadow:
    - `reports/eval/offline_mvp_matched_horizon_shadow_round1_1_d22step20_d29_d33_d60_d68_d69_d70_d71_d72_d73/`

## 当前真实状态
### 1. official quick-screen 没变
- 仍然是:
  - validation = `D71`
  - default_minimax = `D22`
  - special / `e_evt` / `z_art` = `D33`
- 解释:
  - `D70 / D72 / D73` 没有推翻 official fixed handoff
  - 当前 official 问题仍不是“新 anchor 已经替换旧 anchor”

### 2. matched20 shadow 已收缩到 `D70 family`
- 当前 shadow minimax:
  - `D72`
- 关键阈值:
  - `budget_to_minimax_anchor = 0.058874`
- selector:
  - `matched20@0.05 -> D71`
  - `matched20@0.13 -> D72`
- 解释:
  - shadow 不是回到 `D22`
  - 也不是继续停在 `D68`
  - 它已经缩到 `D70 / D72 / D73` 这个很窄的盆地里

### 3. `D72 / D73` 提供的是 epsilon 级再平衡，不是新路线
- `D72`
  - 更偏 `special + e_evt`
- `D73`
  - 更偏 `validation + special`
- 共同点:
  - 都没有脱离 `D70` 盆地
  - 都没有产生足以单独立项的新 regime

## 当前待决策分叉
### 方向 A: 继续沿 `D70 family` 做更明确的 control-target restoration
- 数据事实:
  - `D70` 已显著削掉 `D60` validation tax
  - `D72 / D73` 证明纯 late source / handoff 旋钮只剩弱杠杆
- 优点:
  - 直接针对当前缺口:
    - special push
    - `e_evt / z_art` control
  - 成本低于直接上 `200+`
- 缺点:
  - 仍需要新增训练轮次
  - 可能继续停留在 family 内的小幅重排

### 方向 B: 把 `D70 / D72 / D73` 当作 family 候选，准备 matched long horizon(`200+`)
- 数据事实:
  - shadow minimax 已不再是老 family
  - 但 family 内部还没完全坐实单点
- 优点:
  - 能直接回答:
    - 这条新 family 是否真的具备更长 horizon 优势
    - 是否值得挑战 official fixed handoff
- 缺点:
  - 成本更高
  - 在 family 代表点尚未完全选定时，
    容易把长周期预算花在错误单点上

## 当前建议
- 默认建议选择方向 A。
- 理由:
  - 当前真正收敛的是 family，不是单点
  - 先做更明确的 control-target restoration，
    比直接把某一个 epsilon 领先点拉去做 `200+` 更稳
  - 如果后续 family 内代表点继续稳定在 `D72`
    或出现更清晰的单点赢家，
    再上 matched long horizon 更划算

先说人话:
- 现在最像“该做的下一件事”的，
  不是继续拧 handoff 小旋钮，
  也不是立刻宣告要打总决赛。
- 更像是先在这条已经收缩出来的新盆地里，
  找到一个更像正式代表的点。

## 接班后的操作纪律
1. 所有 Python 命令继续显式使用:
   - `.\python.exe manage.py ...`
2. `init-experiment` 一律顺序执行，不并发
3. 恢复状态时不要只看最新编号文档，
   必须同时核对:
   - official quick-screen json
   - matched20 shadow json
4. 当前若提到“最新最好”，必须先说明口径:
   - official
   - matched20 shadow
   - 或 family 内局部比较
