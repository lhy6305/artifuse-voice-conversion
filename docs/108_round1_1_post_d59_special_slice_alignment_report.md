# `round1.1 / post-D59 / target special slice alignment diagnostic` 报告

## 目的
- `D58 / D59` 已经证明:
  - formal special 的 late exposure 可以工程上打满
  - 但稳定命中的 `short_pause + clause>=2 + duration ceiling` cohort 会把轨迹推向 validation-first
- 这说明当前问题不再是:
  - “有没有命中”
- 而是:
  - “命中的 cohort 到底像不像 final `target_special_eval`”
- 这轮新增一个更基础的诊断:
  - 直接比较 `target_special_eval` 与 train-side candidate cohort 的结构签名
  - 看是否还值得继续沿 `clause-shape` 代理原则微调

先说人话:
- 这次不是继续开训练。
- 是先把“特殊切片本人到底长什么样”看清楚。
- 免得后面一直拿错替身做监督。

## 代码与命令
### 新增代码能力
- `src/v5vc/special_slice_alignment.py`
  - 合并 `split / target_weak_event_hints / target_special_supervision`
  - 计算 `target_special_eval` 的结构画像
  - 计算 train-side pool / heuristic cohort / nearest records 的 `special_distance`
  - 输出 machine-readable json 与 markdown 摘要
- `src/v5vc/cli.py`
  - 新增正式命令:
    - `analyze-offline-mvp-special-slice-alignment`

### 实跑命令
```powershell
.\python.exe manage.py analyze-offline-mvp-special-slice-alignment
```

### 产物
- `reports/data/round1_1_special_slice_alignment/special_slice_alignment_summary.json`
- `reports/data/round1_1_special_slice_alignment/special_slice_alignment_summary.md`

## 关键事实
### 1. `target_special_eval` 的真实结构签名非常极端，而且 train / validation 中完全不存在同签名样本
- `target_special_eval`
  - `record_count = 8`
  - `nonverbal_only_count = 8`
  - `lexical_char_count_zero = 8`
  - `pause_boundary_count_zero = 8`
  - `terminal_boundary_count_zero = 8`
  - `clause_count_zero = 8`
  - `clause_span_count_zero = 8`
- `target_train`
  - `record_count = 592`
  - `nonverbal_only_count = 0`
  - `lexical_char_count_zero = 0`
  - `clause_span_count_zero = 0`
  - `special_signature_count = 0`
- `target_validation`
  - `special_signature_count = 0`

解释:
- 这不是“train 里有一些类似样本，只是筛得不够准”。
- 是 train / validation 根本没有任何一条和 final special slice 同结构签名的样本。

### 2. 现有 pool 里最接近 `target_special_eval` 的也不是 `D58 / D59` 命中的那类样本
- 现有 pool 对齐结果前几名:
  - `challenge_proxy_core`
    - `count = 16`
    - `mean_special_distance = 3.184231`
  - `short_pause_no_terminal`
    - `count = 18`
    - `mean_special_distance = 3.732884`
  - `challenge_proxy_relaxed`
    - `count = 43`
    - `mean_special_distance = 4.623756`

解释:
- `D58 / D59` 依赖的那条 `short_pause_no_terminal + clause>=2` 路线，
  从更基础的结构距离看就不是最接近 special slice 的代理。

### 3. 真正更接近的 train-side proxy 是“极短单句 filler”，不是 multi-clause formal short-pause
- 启发式 cohort 重排后最接近的是:
  - `micro_pause_none_singleton_strict`
    - `count = 8`
    - `mean_special_distance = 2.047626`
    - `min_special_distance = 2.000764`
- 它的定义是:
  - `duration <= 2.114989`
  - `lexical <= 1`
  - `pause = 1`
  - `terminal = 0`
  - `clause = 1`
  - `final_terminal_type = none`

解释:
- 当前最像 `target_special_eval` 的 train-side 代理，
  不是更 formal 的多 clause 样本，
  而是一批极短的单 token / 单 pause filler。

### 4. 但这些最近邻仍然和 final special slice 有硬结构差异
- 最近邻 train records 包括:
  - `target::chapter3_2_firefly_141 = 唔，`
  - `target::chapter3_3_firefly_250 = 二，`
  - `target::chapter3_3_firefly_249 = 一，`
  - `target::chapter3_3_firefly_124 = 欸，`
  - `target::chapter3_17_firefly_136 = 三，`
  - `target::chapter3_2_firefly_248 = 这，`
- 它们共同特征:
  - `lexical_char_count = 1`
  - `pause_boundary_count = 1`
  - `terminal_boundary_count = 0`
  - `clause_count = 1`
  - `clause_span_count = 1`

解释:
- 它们虽然是目前最接近的 proxy，
  但依然不是:
  - `nonverbal_only`
  - `zero lexical`
  - `zero clause-span`
- 所以当前差异不是“再收一收阈值”就能消失，
  而是 supervision 原则本身要跟着改。

### 5. 诊断器已经给出明确建议: 继续训练可以，但不要继续 `D58 / D59` 这条线
- `continue_training = true`
- `continue_current_d58_d59_line = false`
- `principle_change_required = true`
- `recommended_proxy_cohort = micro_pause_none_singleton_strict`
- `recommended_supervision_direction = Pivot from clause-shape supervision to clause-free singleton sparse-frame supervision over the closest micro-utterance cohort.`

解释:
- 这不是要求停工。
- 是要求换原则:
  - 从 `clause-shape` 转向 `clause-free`
  - 从 `formal short-pause multi-clause` 转向 `micro singleton sparse-frame`

## 当前结论
1. `D58 / D59` 已经把“命中率问题”做完了，新的 special-slice 诊断进一步说明:
   - 当前主矛盾不在 exposure
   - 而在 proxy principle mismatch
2. `target_special_eval` 的结构本质是:
   - `nonverbal_only`
   - `zero lexical`
   - `zero pause / terminal / clause / clause-span`
3. train-side 最接近的可用代理并不是多 clause formal short-pause，
   而是一批 `lexical=1 + pause=1 + clause_span=1` 的极短 singleton filler。
4. 所以若继续 formal special supervision，
   - 不应再优先围绕 `D56-D59` 做 role / weight / sampler / teacher 微调
   - 更值得转向 `clause-free singleton sparse-frame supervision`

## 当前建议
1. 保留 `special_slice_alignment` 命令作为 `D59` 之后的固定诊断入口。
2. 暂停继续做:
   - `D56 / D57` 的 clause-shape 权重与 role 排列
   - `D58 / D59` 的 short-pause cohort ratio / teacher gate 微调
3. 若继续开下一轮训练，更值得先设计:
   - 基于 `micro_pause_none_singleton_strict` 的新 proxy cohort
   - 不再显式依赖 `clause_spans / clause_transition` 的 sparse-frame special supervision
4. 当前 route 结构继续保持:
   - `D29 = validation`
   - `D22 = default_minimax`
   - `D33 = special / e_evt / z_art`
