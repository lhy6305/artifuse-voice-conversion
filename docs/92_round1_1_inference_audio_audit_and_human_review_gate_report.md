# `round1.1 / inference-audio audit and human-review gate` 报告

## 目的
- 对当前 MVP 做一次人工审核前置校验:
  - 它现在能不能直接导出推理音频
  - 如果不能，缺口具体在哪
- 同时把后续流程里的人工听感 gate 正式写死:
  - 每次数据上出现突破/进化
  - 都必须跑一次用户人耳试听
  - 在用户确认前禁止直接升为当前最优解

## 审核结论
### 1. 当前 MVP 还不能直接导出推理音频
当前结论是:
- 不能。

理由不是“命令没封装好”，而是更底层的链路当前就不存在:
- `src/v5vc/offline_mvp/model.py`
  - 模型前向最终只输出:
    - `z_art`
    - `event_logits / event_probs`
    - `acoustic`
    - `text_aux`
  - 其中 `acoustic` 只是 frame-level 声学特征张量，不是可直接落盘播放的 waveform
- `src/v5vc/cli.py`
  - 当前 CLI 只有:
    - 训练
    - 消融
    - special eval
    - checkpoint series
    - route / handoff / stage report
  - 没有任何:
    - inference
    - synthesis
    - vocoder
    - export-audio
    的命令入口
- 全部训练配置当前都显式写着:
  - `vocoder_required = false`
  - 说明系统当前设计里并没有接入推理波形合成后端

### 2. 当前代码里唯一的 waveform 写盘能力不属于推理
- `src/v5vc/target_format_recovery.py`
  - 确实有 `write_waveform_int16`
- 但它只用于:
  - 预处理阶段的 target 格式恢复与重采样
- 它不是:
  - 模型推理后的 waveform 合成
  - 也不是运行时音频导出链路

所以当前不能把这个函数误当成“系统已支持导出推理音频”。

## 对当前请求的执行结果
- 由于当前 MVP 不具备“checkpoint -> 推理 waveform”链路，
  本轮没有生成可供人耳试听的推理音频。
- `reports/audio/` 目录已保留说明文件，
  明确记录:
  - 当前无推理音频产物
  - 原因是缺少 vocoder / synthesis/export 链路

## 当前流程约束
从本轮开始，新增人工听感 gate:

1. 只要某个分支在数据上出现突破/进化，
   不论它是:
   - 新 leader
   - 新 anchor
   - 或新的 minimax 候选
   都必须追加一次人工试听流程。

2. 人工试听的最小执行规格:
   - 选择当前数据表现最好或次好的几个分支
   - 每个分支至少导出 `3` 段不同输入音频
   - 统一落到 `reports/audio/`
   - 供用户做人耳试听

3. 在用户明确确认之前:
   - 禁止把该分支直接写成当前最优解
   - 禁止把它直接替换默认 anchor / default_minimax / special anchor 的正式口径

## 当前建议
1. 如果后续要真正执行这条人工审核流程，下一步先补:
   - checkpoint 推理入口
   - 声学特征到 waveform 的 synthesis / vocoder 链路
   - `reports/audio/` 的正式导出命令
2. 在该链路存在之前，
   当前所有“数据 leader”都只能视为:
   - 数据侧最优候选
   - 不是经过人耳审核确认的最终最优解
