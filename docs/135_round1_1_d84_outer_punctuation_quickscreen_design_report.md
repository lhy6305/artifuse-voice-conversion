# 135. round1.1 `D84 / outer punctuation quick-screen` 设计与 dry-run 报告

## 目的
- `D80-D83` 已说明:
  - 继续围绕 `D79` 拧 late teacher source / `z_art_weight` / singleton exposure
    不会自然补回当前 `z_art` 缺口。
- 这轮改成一个新的 quick-screen 探针:
  - 保留 `post-D59` singleton sparse 主骨架
  - 不改 late teacher source
  - 只新增一个更外层、且不与 strict sparse proxy 重叠的 micro-utterance outer pool
  - 再把 `punctuation_profile_aux` 真正挂到这个 outer pool 上

先说人话:
- 这轮不是再拧 `D80-D83` 的旧旋钮。
- 是把“strict sparse 内核”和“outer punctuation restoration”明确拆成两层，
  看这种更外层补法在 quick-screen 上会不会先打开新形状。

## 数据与代码准备
### 1. `target_special_supervision` 正式扩展了两个 micro pool
- 文件:
  - `src/v5vc/target_special_supervision.py`
- 新增正式 pool:
  - `micro_singleton_anypunct_relaxed`
    - `13` 条
    - 定义:
      - `duration <= 2.2`
      - `lexical <= 2`
      - `pause <= 1`
      - `terminal <= 1`
      - `clause = 1`
  - `micro_singleton_anypunct_expansion`
    - `5` 条
    - 定义:
      - 落在 `micro_singleton_anypunct_relaxed`
      - 但不落在 `micro_pause_none_singleton_strict`

这 `5` 条具体是:
- `请问，`
- `天啊，`
- `嗯。`
- `你是，？`
- `茄子，！`

解释:
- `micro_singleton_anypunct_relaxed` 是 strict singleton 外面最近的一圈。
- `micro_singleton_anypunct_expansion` 则是这圈里“新增出来”的差分 outer pool，
  适合做外层 supervision，
  不会和现有 strict sparse proxy 在同一批样本上直接打架。

### 2. `punctuation_profile_aux` 已补成真正 sidecar-aware
- 文件:
  - `src/v5vc/offline_mvp/losses.py`
- 新改动:
  - `compute_punctuation_profile_aux_loss(...)`
    现在接收 `target_special_supervision`
  - 若配置里声明 `pool_memberships`
    就会复用 `build_special_supervision_sample_mask(...)`
    先按 sidecar pool / proximity / terminal / structure gate 过滤样本，
    再计算标点 profile loss

解释:
- 之前即使在 config 里写了 `pool_memberships`
  `punctuation_profile_aux` 也不会真正按 sidecar pool 过滤。
- 现在这条 gate 才算真实接通，
  `D84` 才是“outer pool + 现有 aux”的有效实验，
  不是假 gate。

## `D84` 设计
### 配置
- `configs/offline_mvp_train_d84_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_20step_smallscale_seeded_shuffle.json`

### 骨架选择
- 以 `D75` quick-screen family 为底，
  因为它是当前 `D76` 长窗主线的直接 `20-step` 对应骨架。

### 三个主改动
1. late `teacher_consistency.weight`
   - `step11-20: 0.15 -> 0.20`
   - 让 quick-screen 更接近 `D79` 的 late teacher-strength 思路
2. late `targeted_sampling`
   - 主 priority 仍是:
     - `micro_pause_none_singleton_strict`
   - 但新增:
     - `secondary_sampling.max_slots = 1`
     - `secondary_sampling.priority_pool_memberships = ['micro_singleton_anypunct_expansion']`
   - 目标是:
     - 不破坏 strict sparse 主骨架
     - 同时保证 outer pool 在 late batch 里稳定曝光
3. late `punctuation_profile_aux`
   - `pool_memberships = ['micro_singleton_anypunct_expansion']`
   - `min_punctuation_ratio = 0.3`
   - `weight_schedule = step11-15 linear ramp to 0.12`

解释:
- strict singleton 继续负责内层 sparse-frame 行为。
- outer expansion pool 只负责更外层的 punctuation / `z_art` restoration 探针。
- 这轮故意不再叠新的 teacher-source handoff、
  也不改 `z_art_influence_aux` 的目标池，
  保持问题尽量单纯。

## dry-run 执行链
### 已完成
- `.\python.exe manage.py analyze-round1-target-special-supervision`
- `.\python.exe manage.py analyze-offline-mvp-special-slice-alignment`
- `.\python.exe manage.py init-experiment --slug offline-mvp-d84-round1-1-d26-init-post-d59-singleton-sparse-micropause-sampler-d22late-teacherweight-outer-punctuation-20step-calibration --config-path configs/offline_mvp_train_d84_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_20step_smallscale_seeded_shuffle.json`
- `.\python.exe manage.py train-offline-mvp --config configs/offline_mvp_train_d84_round1_1_d26_init_post_d59_singleton_sparse_micropause_sampler_d22late_teacherweight_outer_punctuation_20step_smallscale_seeded_shuffle.json --experiment-id EXP-20260316-040 --dry-run`

### dry-run 结果
- experiment:
  - `EXP-20260316-040`
- status:
  - `dry_run_ready`
- 时间:
  - `run_started_at = 2026-03-16T22:02:20`
  - `ended_at = 2026-03-16T22:02:21`
  - `duration_sec = 1.633452`

### dry-run 确认到的关键点
- late sampling plan 已显式落出:
  - primary:
    - `micro_pause_none_singleton_strict`
  - secondary:
    - `micro_singleton_anypunct_expansion`
    - `max_slots = 1`
- `phase_priority_record_counts` 为:
  - `step1-10 = 19`
  - `step11-20 = 13`
- late `teacher_consistency` 已显式变成:
  - `weight = 0.20`
- `punctuation_profile_aux` 已出现在 effective config 中，
  且 pool 已是:
  - `micro_singleton_anypunct_expansion`

解释:
- 当前不是“先写配置，等正式训练时再看会不会接通”。
- dry-run 已经证明:
  - 新 outer pool 在 sampler 里是活的
  - 新 pool gate 在 punctuation aux 里也是活的
  - `D84` 已经具备正式 quick-screen 开跑条件

## 当前结论
1. `D84` 已完成设计、sidecar 扩展、loss gate 补齐、`init-experiment` 和 dry-run。
2. 当前得到的是:
   - 一个“真 outer pool + 真 pool-gated punctuation aux”的 quick-screen 候选
   - 不是旧 `punctuation_profile_aux` 的重跑
3. 这轮还没有启动正式训练，
   所以当前没有新的 route 结论；
   只有设计和执行准备已经就绪。

## 下一步
1. 直接运行 `D84` 正式 quick-screen 训练。
2. 完成:
   - final `ablation_eval`
   - final `special_eval`
   - checkpoint series
   - special eval series
3. 再判断:
   - 它是否真的打开了和 `D75 / D70 / D71` 不同的新形状
   - 若没有，
     则说明“outer punctuation restoration”这条题也基本可以收口

