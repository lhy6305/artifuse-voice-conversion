# `round1.1 / C1.4 / A2-min` 100-step 报告

## 目的
- 在 `EXP-021` 已确认：
  - `round1.1` 能让终点 special slice 更顺一点
  - 但 `step50` 的 route-C 依赖回落仍更严重
- 当前做一个最低成本的稳定性修正：
  - 不改 split
  - 不改 sampler
  - 不加全局 `event` ramp
  - 只加 `event_dimension_weights`

先说人话：
- 这轮不是再换老师，也不是再改数据。
- 只是让现有 event 判卷时，更重视“变化/瞬态类维度”，少重视“更像稳态门限”的维度。

## 当前配置
- 实验：
  - `EXP-20260314-022-offline-mvp-c1-4-round1-1-evt-a2-dimonly-100step-calibration`
- 配置：
  - `configs/offline_mvp_train_c1_4_round1_1_evt_a2_dimonly_smallscale_100_seeded_shuffle.json`
- 相比 `EXP-021` 的唯一区别：
  - 新增 `event_dimension_weights`
  - 使用：
    - `[0.75, 1.25, 1.25, 0.75, 0.75, 1.25, 1.25, 0.75]`
- 没有新增：
  - `event_weight_schedule`
  - `weak_event` 权重
  - 新 sidecar 形式

## 执行内容
- 已完成 dry-run
- 已完成正式 `100 step`
- 已完成：
  - final `special_eval`
  - final ablation
  - checkpoint-series ablation
  - `special_eval_series`

## 关键结果
### 1. formal full-validation 比 `EXP-021` 略差
- `EXP-021` model-level `target_validation.loss_total`：
  - `2.760389`
- `EXP-022` model-level `target_validation.loss_total`：
  - `2.789528`

这说明：
- 只靠维度重权，没有把主验证往前推。

### 2. final special slice 更顺了一点
- `EXP-021`
  - `target_special_eval.loss_total = 2.789155`
  - `delta_loss_total = 0.028766`
- `EXP-022`
  - `target_special_eval.loss_total = 2.763572`
  - `delta_loss_total = -0.025956`

解释：
- 在 final checkpoint 上，`EXP-022` 的 special slice 已经不比常规 validation 更难。
- 这说明维度重权确实有一点终点收益。

### 3. final `e_evt` 依赖继续略增
- `EXP-021`
  - `zero_e_evt.delta_target_loss_total = 1.781482`
- `EXP-022`
  - `zero_e_evt.delta_target_loss_total = 1.803449`

同时：
- `zero_z_art.delta_target_loss_total`
  - `0.886715 -> 0.899777`

解释：
- 这轮没有像旧 `A1` 那样明显压坏 `z_art`
- 但增益幅度也很小

### 4. `step50` 依赖回落几乎没变
- `EXP-021`
  - `step50 zero_z_art.delta_target_loss_total = -0.273851`
  - `step50 zero_e_evt.delta_target_loss_total = -0.854462`
- `EXP-022`
  - `step50 zero_z_art.delta_target_loss_total = -0.265417`
  - `step50 zero_e_evt.delta_target_loss_total = -0.846723`

解释：
- 这不是“修好了，只是还不够强”。
- 更准确地说，是：
  - 它几乎没有真正改写中期行为
  - 只是终点更顺了一点

## 当前结论
- `A2-min` 比 `A1` 健康得多：
  - 没有明显拖垮整体训练
  - 也没有明显把 `z_art` 打坏
- 但它仍然不够：
  - 主验证没提升
  - `step50` 负依赖几乎没变
- 因此当前更准确的判断是：
  - `A2-min` 只能算“确认还有一点终点修饰空间”
  - 不能算“稳定性问题已经被纯约束修复”

先说人话：
- 这轮像是把收尾动作磨顺了一点。
- 但中途打摆子的核心毛病还在。

## 建议
- 不把 `EXP-022` 升为新默认配置。
- 若继续按当前计划推进，更合理的是：
  - 结束“纯约束小修小补”的尝试
  - 转向下一层，也就是更明确的标签表达升级或监督定义升级
