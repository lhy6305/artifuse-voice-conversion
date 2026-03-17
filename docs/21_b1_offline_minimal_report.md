# `B1-offline-minimal` 首轮实现与小规模验证报告

## 目的
- 记录 `B1-offline-minimal` 的首轮代码落地情况。
- 验证“目标侧文本监督 + 源侧纯音频监督”的不对称训练方案是否能稳定接入现有 offline MVP。

先说人话：
- 这轮已经不是纸上方案了。
- 新老师已经接进训练里，并且小规模真实训练跑通了。
- 目前看，它至少没有把系统搞坏；但现在还不能说它已经明显优于旧方案。

## 已完成实现
### 1. 数据特征升级
- 文件：
  - `src/v5vc/offline_mvp/data.py`
- 新增：
  - `target_text_feature_version`
  - `legacy_v0`
  - `b1_punct_v1`

### 2. `B1` 目标侧文本特征
当前 `b1_punct_v1` 使用 7 维目标侧监督：
1. token length norm
2. lexical chars per second
3. pause punctuation density
4. terminal punctuation density
5. question ratio
6. exclamation ratio
7. nonverbal-only flag

解释：
- 这不是 phone/manner 全量标签。
- 这是在完全离线、无新依赖、无源侧转写的前提下，能先落地的一版文本/标点监督。

### 3. 模型与训练入口升级
- 文件：
  - `src/v5vc/offline_mvp/model.py`
  - `src/v5vc/train_entry.py`
  - `src/v5vc/ablation_eval.py`
  - `src/v5vc/special_eval.py`
- 改动：
  - `text_aux_head` 改为按配置决定输出维度
  - 训练、消融、special_eval 全部支持 `target_text_feature_version`
  - 源侧继续保持 `text_aux_target = None`

先说人话：
- 目标侧现在会学更丰富的文本节律提示。
- 源侧依然不强塞文本，这和你对数据质量的判断是一致的。

### 4. 独立配置
- 文件：
  - `configs/offline_mvp_train_b1_smallscale_seeded_shuffle.json`
- 当前设置：
  - `target_text_feature_version = b1_punct_v1`
  - `text_aux_dim = 7`
  - `20 step`
  - `seeded_shuffle`

## 已完成验证
### 1. 训练验证
- 实验：
  - `EXP-20260314-014-offline-mvp-b1-smallscale`
- 训练计划：
  - `reports/training/offline_mvp/EXP-20260314-014-offline-mvp-b1-smallscale.train_plan.json`
- 运行状态：
  - `20 step` 真实训练完成
  - 总耗时 `1.28162s`
  - `target_batch_text_feature_shape = [4, 7]`
  - `target_text_feature_version = b1_punct_v1`

### 2. 与旧 seeded-shuffle 小规模基线对比
对比对象：
- 旧基线：
  - `EXP-20260314-009-offline-mvp-seeded-shuffle`
- 新实验：
  - `EXP-20260314-014-offline-mvp-b1-smallscale`

关键数值：
- final validation `loss_total`
  - `EXP-009`: `35.849232`
  - `EXP-014`: `35.865547`
- target `loss_text_aux`
  - `EXP-009`: `0.119148`
  - `EXP-014`: `0.181097`

解释：
- 总体验证损失几乎打平。
- 这说明 `B1` 至少是稳定接入的，没有明显破坏主流程。
- 但当前还看不出它已经带来总 loss 层面的明确收益。

### 3. 控制消融
- 结果文件：
  - `reports/eval/offline_mvp_ablations_exp014/ablation_eval.json`

关键数值：
- `zero_z_art.delta_target_loss_total`
  - `EXP-009`: `0.079066`
  - `EXP-014`: `0.207014`
- `zero_e_evt.delta_target_loss_total`
  - `EXP-009`: `1.015739`
  - `EXP-014`: `1.733871`

解释：
- 在这轮 20 step 小规模训练里，`B1` 之后控制链路的敏感度是更强的。
- 尤其 `e_evt` 的退化量更大，说明文本/标点辅助监督至少没有削弱事件路径。

先说人话：
- 虽然总分还没明显变好，
- 但把 `z_art / e_evt` 拔掉时，模型掉得更厉害了，
- 这通常说明控制主链没有被新老师稀释，反而更像被扶住了一点。

### 4. `special_eval`
- 结果文件：
  - `reports/eval/offline_mvp_special_eval_exp014/special_eval_model.json`

关键数值：
- regular validation `loss_total = 15.784263`
- special eval `loss_total = 11.882978`
- delta `= -3.901285`
- regular `loss_text_aux = 0.125794`
- special `loss_text_aux = 0.446290`

解释：
- 当前 special slice 仍然只是 nonverbal challenge。
- `B1` 没有把它带坏，也没有改变它的解释边界。

## 当前结论
- `B1-offline-minimal` 已经完成首轮可训练接入。
- 它满足三件事：
  1. 符合离线约束
  2. 符合“目标侧文本监督、源侧纯音频监督”的不对称设计
  3. 小规模真实训练与评估均已跑通

- 当前还不能下的结论：
  - 不能说 `B1` 已经在总体效果上明显优于旧方案
  - 不能说它已经完成了 `B` 路线的标签升级目标

## 我的建议
- 当前 `B1` 已经通过“可以继续放大验证”的门槛。
- 下一步最合理的是二选一：
  1. 继续做 `B1` 的更长小规模或大规模训练验证
  2. 在不扩大训练前，先把 `B1` 的文本监督口径再细化一轮

先说人话：
- 现在这位新老师已经证明自己能正常上课。
- 下一步要么让它多带几堂课，看长期效果；
- 要么先微调一下教案，再扩大试验。
