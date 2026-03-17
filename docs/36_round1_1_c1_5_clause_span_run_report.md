# `round1.1 / C1.5 / clause-aware` 100-step 报告

## 目的
- 在 `A2-min` 已基本证明“纯约束小修补救不回 `step50`”之后，验证第一版真正消费 `clause_spans / utterance_structure_type` 的 route-C 接法。
- 当前仍保持：
  - `round1.1` 数据不变
  - `hybrid_stratified_blocked` 不变
  - `seeded_shuffle` 不变

先说人话：
- 这轮是第一版“让模型不只看边界点，还看句内分段结构”。
- 目的不是把终点再磨一点，而是看它能不能真正动到中段稳定性。

## 当前接法
- 仍保留 `C1.4` 的：
  - boundary bias
  - boundary pre/post target override
- 新增：
  - `clause_role_target_overrides`
- 当前按 `clause role` 做的事很克制：
  - `single / final / middle` clause 上，给 `presence / energy` 维度加温和 floor 和 bias
  - 只在对应 `utterance_structure_type` 下生效

解释：
- 这还不是完整的监督定义升级。
- 更像是第一版“结构化标签接线验证”。

## 关键结果
### 1. 它没有修掉 `step50`
- `EXP-021`
  - `step50 zero_z_art.delta_target_loss_total = -0.273851`
  - `step50 zero_e_evt.delta_target_loss_total = -0.854462`
- `EXP-022`
  - `step50 zero_z_art.delta_target_loss_total = -0.265417`
  - `step50 zero_e_evt.delta_target_loss_total = -0.846723`
- `EXP-023`
  - `step50 zero_z_art.delta_target_loss_total = -0.273785`
  - `step50 zero_e_evt.delta_target_loss_total = -0.853283`

结论：
- 这轮几乎没有真正改写中期依赖回落。

### 2. final checkpoint 也没有明显赢
- `EXP-021`
  - final `delta_loss_total = 0.028766`
  - final `zero_e_evt.delta_target_loss_total = 1.781482`
- `EXP-022`
  - final `delta_loss_total = -0.025956`
  - final `zero_e_evt.delta_target_loss_total = 1.803449`
- `EXP-023`
  - final `delta_loss_total = 0.008379`
  - final `zero_e_evt.delta_target_loss_total = 1.807451`

解释：
- `EXP-023` 的 final `e_evt` 依赖略高于前两轮
- 但 `special_eval` 表现不如 `EXP-022`
- 整体更像“能跑通，但没形成胜出证据”

### 3. 主验证也没有更好
- `EXP-021` model-level `target_validation.loss_total`
  - `2.760389`
- `EXP-022`
  - `2.789528`
- `EXP-023`
  - `2.777409`

解释：
- 它比 `EXP-022` 略好一点
- 但仍不如 `EXP-021`

## 当前结论
- 第一版 clause-aware 接线已经证明：
  - 新 sidecar 字段不是摆设，代码路径已经能真实消费
  - route-C 可以进入“结构化标签试验”阶段
- 但当前这版具体接法还不够：
  - 没修掉 `step50`
  - 没拿到最佳 final special-slice
  - 也没把主验证拉上去

先说人话：
- 这次不是接不上。
- 是接上了，但这版教法还不对。

## 当前建议
- 不把 `EXP-023` 升为默认训练配置。
- 当前更合理的下一步不是回去做同层小调参，而是：
  - 继续沿“结构化标签表达”走
  - 但要换接法，不要只给 clause body 做温和 `presence / energy` floor
