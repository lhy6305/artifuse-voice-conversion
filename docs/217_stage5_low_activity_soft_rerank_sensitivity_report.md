# 217. Stage5 low-activity soft rerank 敏感性分析报告

## 背景
- `docs/216_stage5_low_activity_soft_rerank_integration_report.md`
  已把
  low-activity soft rerank
  接进
  checkpoint selection
  payload
- 但上一轮仍未回答两个关键问题:
  1. 当前
     `--low-activity-soft-validation-ratio 1.05`
     是否真的敏感
  2. 当前四项权重下
     `step72`
     的推荐是否很容易翻盘

## 本轮目标
1. 复用已有
   `nores_vocoder_checkpoint_selection.json`
2. 对当前
   soft rerank
   做:
   - near-best validation ratio sweep
   - fragmentation emphasis sweep
   - 四维权重网格扫描
3. 把当前推荐的稳定性边界落盘

## 本轮代码与命令

### 1. 使用的代码入口
- `src/v5vc/nores_vocoder_low_activity_sensitivity.py`
- `manage.py analyze-offline-mvp-nores-vocoder-low-activity-sensitivity`

### 2. 实际运行命令

```powershell
.\python.exe manage.py analyze-offline-mvp-nores-vocoder-low-activity-sensitivity `
  --checkpoint-selection reports/runtime/offline_mvp_nores_vocoder_checkpoint_selection_waveform_rmsguard02_activitygate02_gate72_deterministic_round1_1/nores_vocoder_checkpoint_selection.json `
  --output-dir reports/runtime/offline_mvp_nores_vocoder_low_activity_sensitivity_waveform_rmsguard02_activitygate02_gate72_deterministic_round1_1 `
  --weight-step 0.05
```

### 3. 产物
- `reports/runtime/offline_mvp_nores_vocoder_low_activity_sensitivity_waveform_rmsguard02_activitygate02_gate72_deterministic_round1_1/nores_vocoder_low_activity_sensitivity.json`
- `reports/runtime/offline_mvp_nores_vocoder_low_activity_sensitivity_waveform_rmsguard02_activitygate02_gate72_deterministic_round1_1/nores_vocoder_low_activity_sensitivity.md`

## 当前输入集合

### 1. 当前真正进入 low-activity soft rerank 的只有两个候选
- `step72`
  - `loss_total = 0.564671`
  - `entry_soft_validation_ratio = 1.0`
- `step60`
  - `loss_total = 0.584654`
  - `entry_soft_validation_ratio = 1.035389`

### 2. 当前默认权重
- `mean_activity_alignment_mae = 0.35`
- `mean_activity_excess_mean = 0.35`
- `mean_active_fraction = 0.2`
- `mean_fragmentation_score = 0.1`

### 3. 当前默认推荐
- `selected_step = 72`
- `selected_score = 0.1`

## 敏感性结果

### 1. 当前 `1.05` near-best 门槛没有改写结果
- ratio sweep:
  - `1.0`
    时只有
    `step72`
    入围
  - `1.035389`
    起
    `step60`
    才进入集合
  - `1.035389`
    和
    `1.05`
    下，
    选中的都仍然是
    `step72`
- 说明:
  - 当前证据只能说明
    `1.05`
    没有把推荐改坏
  - 还不能反过来证明
    `1.05`
    是已经被调优出来的最佳门槛

### 2. `step72` 对 fragmentation 单项加权并不脆弱，但超过半权重后会翻盘
- fragmentation emphasis sweep
  显示:
  - `fragmentation_weight <= 0.50`
    时，
    推荐仍是
    `step72`
  - `fragmentation_weight = 0.55`
    起，
    推荐翻为
    `step60`
- 当前默认仅
  `0.10`
  给
  fragmentation，
  离翻盘边界还有明显距离

### 3. 四维权重网格里，`step72` 在当前候选对上占主导
- `weight_step = 0.05`
- 共扫描:
  - `1771`
    组权重
- 结果:
  - `step72 selected_share = 0.875776`
  - `step60 selected_share = 0.124224`
- 当前只有在权重明显向
  fragmentation
  偏置时，
  `step60`
  才更容易被选中

## 当前解释边界

### 1. 这轮结果是“局部稳健”，不是“全局定论”
- 当前 probe
  只覆盖:
  - `step60`
  - `step72`
- 所以:
  - 这轮敏感性结论
    只对
    当前这对 late candidates
    成立
- 不能直接写成:
  - 所有 family
    都应固定使用
    同一套权重和门槛

### 2. 两候选 + min-max 归一化会让当前分数带有明显“离散投票”特征
- 当前只有两个候选
- 并且四项指标上
  两边各自一边倒
- 因此当前 score
  更像:
  - 各项权重在
    “底音泄漏/动态跟随”
    和
    “fragmentation”
    之间的投票
- 不能把
  `0.1`
  与
  `0.9`
  当成可跨 family
  复用的绝对刻度

## 对当前策略的影响
1. 当前可以继续保留:
   - `soft_validation_ratio = 1.05`
   - 当前四项权重
   作为:
   - 暂行默认值
2. 但文档表述必须克制:
   - 只能写
     “当前配置在 `step60 vs step72` 上较稳”
   - 不能写
     “当前配置已被系统性调优完成”
3. 后续若继续升级:
   - 优先扩大
     probe
     覆盖的 checkpoint
   - 再讨论
     是否按 family
     自适应调整门槛或权重

## 一句话结论
- 这轮敏感性分析说明:
  - 当前 soft rerank
    在
    `step60 vs step72`
    这组候选上
    推荐
    `step72`
    是相对稳的
  - 但这种稳健性
    目前仍是
    “局部二选一稳健”，
    还不是
    “跨 family 已定型策略”。
