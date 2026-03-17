# `e_evt` 约束增强 A1 首轮实跑报告

## 目的
- 记录方案 `D` 的第一步，也就是 `A1` 真实 `500 step` large-scale 实验的执行结果。
- 判断这条“只加训练约束、不改主结构”的路线，是否足够把 `e_evt` 的后期依赖拉回来。

先说人话：
- 这次实验不是没效果。
- 它确实把 `e_evt` 稍微往回拉了一点。
- 但代价比收益大，整体训练结果比 `EXP-011` 更差，所以这条参数组合不适合直接继续放大。

## 实验信息
- 实验编号：
  - `EXP-20260314-013-offline-mvp-evt-a1-large-scale`
- 配置文件：
  - `configs/offline_mvp_train_large_scale_seeded_500_evt_a1_candidate.json`
- 主要改动：
  - `event_weight_schedule`
    - `step100 -> step250`
    - `0.5 -> 0.8` 线性爬升
  - `event_dimension_weights`
    - `[0.75, 1.25, 1.25, 0.75, 0.75, 1.25, 1.25, 0.75]`
- 运行结果入口：
  - `reports/experiments/EXP-20260314-013-offline-mvp-evt-a1-large-scale.metrics.json`
  - `reports/training/offline_mvp/EXP-20260314-013-offline-mvp-evt-a1-large-scale.train_plan.json`
  - `reports/eval/offline_mvp_ablations_exp013/ablation_eval.json`
  - `reports/eval/offline_mvp_checkpoint_series_exp013/checkpoint_series_eval.json`
  - `reports/eval/offline_mvp_special_eval_exp013/special_eval_model.json`
  - `reports/eval/offline_mvp_special_eval_series_exp013/special_eval_series.json`

## 训练结果摘要
### 1. 基本运行状态
- 训练已正常完成：
  - `500 step`
  - `20` 次 validation
  - `20` 个 checkpoint
- 耗时：
  - `10.793655s`

### 2. 与 baseline `EXP-011` 的最终点对比
| 指标 | `EXP-011` | `EXP-013 A1` | 解释 |
|---|---:|---:|---|
| final validation `loss_total` | `3.321292` | `5.714126` | A1 明显更差 |
| final target `loss_event` | `3.534690` | `3.813887` | 事件损失没有更好收敛 |
| final source `loss_event` | `2.814789` | `3.154472` | 源侧同样更差 |
| best validation step | `500` | `125` | A1 后期继续变差 |
| best validation `loss_total` | `3.321292` | `5.266743` | 连最佳点也明显弱于 baseline |

先说人话：
- `A1` 不是“后面更强了”，而是“中段勉强还能看，后面越训越不划算”。
- 也就是说，它没把 `e_evt` 变成一个更健康的长期控制量，反而把整体训练拖重了。

### 3. A1 权重爬升阶段的观测
- `step100`
  - `event weight = 0.5`
  - validation `loss_total = 5.427892`
- `step125`
  - `event weight = 0.55`
  - validation `loss_total = 5.266743`
  - 这是本轮最佳点
- `step150`
  - `event weight = 0.6`
  - validation `loss_total = 5.416430`
- `step200`
  - `event weight = 0.7`
  - validation `loss_total = 5.694270`
- `step250`
  - `event weight = 0.8`
  - validation `loss_total = 6.054470`

解释：
- 权重爬升刚开始时还有一点收益。
- 但随着 `event` 约束继续加重，整体 validation 开始稳定变差。

## 消融结果
### 1. final checkpoint 对比
| 指标 | `EXP-011` | `EXP-013 A1` | 解释 |
|---|---:|---:|---|
| `zero_z_art.delta_target_loss_total` | `1.410600` | `0.949323` | `z_art` 后期贡献变弱 |
| `zero_e_evt.delta_target_loss_total` | `0.286237` | `0.378181` | `e_evt` 后期依赖略有提升 |
| `zero_e_evt.delta_source_loss_total` | `0.292809` | `0.292809` | 源侧没有出现决定性改善 |

### 2. A1 内部 checkpoint 趋势
| step | `zero_z_art.delta_target_loss_total` | `zero_e_evt.delta_target_loss_total` |
|---:|---:|---:|
| `25` | `0.251646` | `1.789467` |
| `100` | `1.364030` | `1.434572` |
| `250` | `0.545283` | `0.360349` |
| `500` | `0.949323` | `0.378181` |

解释：
- `e_evt` 没有像 `EXP-011` 那样继续掉到更低，但也没有达到“重新成为强控制量”的程度。
- `z_art` 在 `step100` 以后被明显压弱，这说明 A1 不是“净增益”，而是在抢主干里的控制份额。

先说人话：
- 这更像是“把模型注意力硬拽到 `e_evt` 一点点”，
- 但没拽到足够值，
- 反而把原本更有用的 `z_art` 也带偏了。

## `special_eval` 结果
### final checkpoint
- `target_validation.loss_total = 1.903484`
- `target_special_eval.loss_total = 2.192053`
- `delta_loss_total = 0.288569`
- `target_validation.text_aux = 0.013008`
- `target_special_eval.text_aux = 0.520022`

### selected checkpoint series
| step | regular validation | special eval | delta |
|---:|---:|---:|---:|
| `25` | `13.587198` | `9.704168` | `-3.883030` |
| `100` | `2.685433` | `2.893407` | `0.207974` |
| `250` | `2.016988` | `2.292754` | `0.275766` |
| `500` | `1.903484` | `2.192053` | `0.288569` |

解释：
- `special_eval` 的翻转规律仍然存在。
- `A1` 没有把这个 challenge slice 拉坏到失控，但也没有带来额外收益。
- 它仍然只能解释为 nonverbal challenge，不参与主内容结论。

## 对照通过标准
本轮使用 `docs/17_e_evt_constraint_a1_draft.md` 里的建议门槛。

### 主约束检查
1. `step500 zero_e_evt.delta_target_loss_total >= 0.45`
- 实际：`0.378181`
- 结论：未通过

2. `step250` 到 `step500` 不应继续滑到接近 `0`
- 实际：`0.360349 -> 0.378181`
- 结论：部分通过
- 说明：没有继续明显下滑，但强度仍然偏弱

### 副约束检查
1. final validation `loss_total` 不应比 baseline 恶化超过约 `+0.2`
- baseline：`3.321292`
- A1：`5.714126`
- 差值：`+2.392833`
- 结论：严重未通过

2. `z_art` 不应被明显打散
- baseline final `zero_z_art.delta_target_loss_total = 1.410600`
- A1 final `zero_z_art.delta_target_loss_total = 0.949323`
- 结论：未通过

## 当前结论
- 方案 `D` 的总体方向不变。
- 但 `D` 里的第一步 `A1`，以当前这组具体参数来看，不适合作为通过方案继续放大。
- 当前最合理的解释是：
  - 单靠“中后期加一点 `event` 权重 + 维度重权”不够解决根因；
  - 它只能稍微拉住 `e_evt`，但会明显伤到整体收敛和 `z_art` 后期贡献。

先说人话：
- 这次不是完全白跑。
- 它给了一个很明确的否定信息：
  - 不能指望靠这组温和调参，就把 `e_evt` 问题解决掉。
- 这反而帮我们缩小了下一步范围。

## 下一步建议
- 不把 `A1` 升为默认训练配置。
- 保持当前默认仍为：
  - `configs/offline_mvp_train_large_scale_seeded_500.json`
- 下一轮应该在两条路里二选一，由用户拍板：
  1. `A2`
  - 继续走方案 `A`，但改成更谨慎的约束设计，例如更短的后期窗口、只做维度重权、或加明确 early-stop 门槛。
  2. `B`
  - 转向事件标签/监督升级，不再继续靠现有粗标签硬拉损失权重。
