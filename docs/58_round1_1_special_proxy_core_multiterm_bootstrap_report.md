# `round1.1 / D1 / special-proxy-core + multi-terminal` 启动报告

## 目的
- 在 `target special supervision blueprint` 已经把 pool 边界钉死之后，把它真正接进训练采样入口。
- 本轮先做两件事：
  - 给 `targeted_sampling` 增加按 pool 名称选样的正式能力；
  - 基于 `EXP-032` 骨架准备一份最小候选配置，并完成 dry-run 校验。

先说人话：
- 现在不是只知道“该看哪些样本”了。
- 这轮已经让训练代码真的能按这些样本池子去抽。

## 代码改动
### 1. sampler 现已支持 pool membership
- `src/v5vc/offline_mvp/data.py`
  - 新增：
    - `load_target_special_supervision_map`
    - `attach_target_special_supervision`
  - `targeted_sampling` 现支持：
    - `priority_pool_memberships`
    - `exclude_pool_memberships`
  - `secondary_sampling` 也同步支持 pool membership 选样。

### 2. train entry 现已支持 special supervision sidecar
- `src/v5vc/train_entry.py`
  - 新增：
    - `resolve_target_special_supervision_path`
  - 训练计划里现在会显式记录：
    - `target_special_supervision_path`
    - `priority_pool_memberships`
    - `exclude_pool_memberships`

## 候选配置
- 配置文件：
  - `configs/offline_mvp_train_d1_round1_1_special_proxy_core_multiterm_smallscale_100_seeded_shuffle.json`

### 当前设计
- 训练骨架：
  - 直接复用 `EXP-032` 的 `clause_transition_aux + event_boundary_bias`
- 新增 sidecar：
  - `data_prep/round1_1/target_special_supervision/target_special_supervision_sidecar.jsonl`
- targeted sampling：
  - phase1 `step1-25`
    - `priority_ratio = 0.75`
    - primary:
      - `challenge_proxy_core`
    - secondary:
      - `structural_multi_terminal`
      - `max_slots = 1`
  - phase2 `step26-45`
    - `priority_ratio = 0.25`
    - primary:
      - `challenge_proxy_core`
  - `step46+`
    - seeded shuffle

解释：
- 这版不是把所有结构池重新混在一起。
- 它明确让：
  - `challenge_proxy_core`
    负责 special 邻域压力；
  - `structural_multi_terminal`
    只作为一条独立结构轴，用很小的次级配额补进来。

## dry-run 结果
- 命令：
  - `manage.py train-offline-mvp --config configs/offline_mvp_train_d1_round1_1_special_proxy_core_multiterm_smallscale_100_seeded_shuffle.json --experiment-id DRYRUN-20260315-d1-special-proxy-core-multiterm --output-dir reports/training/offline_mvp_d1_special_proxy_core_multiterm --dry-run`

### 关键摘要
- `target_special_supervision_path` 已正确接入训练计划。
- primary pool 计数：
  - `challenge_proxy_core = 16`
- phase1 union 计数：
  - `172`
  - 也就是：
    - `challenge_proxy_core`
    - 加上 `structural_multi_terminal` secondary pool 后的总 priority union
- phase2 priority 计数：
  - `16`
- dry-run 成功通过，前向和 loss 计算正常。

## 当前结论
- 现在已经具备正式跑下一轮最小数据实验的代码条件。
- 最小实验不必再把 `challenge_proxy_core` 手工翻译回：
  - `lex<=x`
  - `duration<=y`
  - `terminal=0`
  这类阈值近似。
- 它可以直接按正式 sidecar pool 采样。

## 当前建议
- 若下一轮马上起跑，优先用这份配置做第一版小规模验证。
- 这轮先不再同时加第二条、第三条结构轴。
- 若第一版没有明显收益，再考虑把 `structural_multi_terminal` 换成：
  - `structural_question_exclaim`
  - 或 `structural_clause_ge4`

先说人话：
- 到这里，下一轮实验已经不是“缺想法”了。
- 现在缺的只是决定要不要真正开跑这条 pool-aware 训练线。
