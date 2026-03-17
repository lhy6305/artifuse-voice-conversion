# `round1.1 / proxy-audio export bootstrap` 报告

## 目的
- 在正式 vocoder / synthesis 链路尚未接入之前，
  先补一条最小可执行的人耳审核导出链:
  - 从 checkpoint 前向得到 `acoustic`
  - 再重建一个可试听的 proxy waveform
- 当前目标不是冒充最终运行时音频，
  而是让用户能够对不同分支做相对听感审核

## 本轮实现
### 新增命令
- `export-offline-mvp-proxy-audio`

### 代码入口
- `src/v5vc/proxy_audio_export.py`
- `src/v5vc/cli.py`

### 当前能力边界
- 当前导出的是:
  - `proxy audio`
  - 基于模型预测 `acoustic = [energy, abs_mean, zero_cross, delta_energy]` 的重建波形
- 当前不是:
  - 完整 vocoder
  - 最终 runtime-quality waveform

## 当前导出结果
按当前主分支，已导出首轮人工审核包:

### D22
- 目录:
  - `reports/audio/offline_mvp_proxy_audit_d22_exp039/`

### D29
- 目录:
  - `reports/audio/offline_mvp_proxy_audit_d29_exp045/`

### D33
- 目录:
  - `reports/audio/offline_mvp_proxy_audit_d33_exp050/`

### 统一试听输入
- `source::segment_0042_0000188800_0000190270`
- `source::segment_0230_0001311640_0001314070`
- `source::segment_0498_0003343840_0003344620`

每个分支都导出了:
- `__input.wav`
- `__proxy.wav`

## 当前结论
1. 当前已经不再是“完全不能导出音频”。
2. 当前已具备一条可供人工审核使用的最小音频导出链。
3. 但这条链当前仍应解释为:
   - 人耳审核 proxy
   - 不是最终 vocoder / runtime 音频质量结论

## 当前断点
- 停止继续做 `step10` 与 `final` 的同构互蒸。
- 下一步优先转向:
  - 更结构化的 checkpoint selection / routing
  - 或更强的 target / gate 级重构
- 当前补出的 proxy-audio 导出链，
  是为了让后续任何数据突破都必须经过一次用户人耳审核，
  而不是为了继续给简单互蒸支线加预算。

## 当前建议
1. 由用户先试听 `D22 / D29 / D33` 的首轮 proxy audio。
2. 在用户未确认前，不把任何单个数据 leader 直接升为最终最优解。
3. 若后续继续建设音频链路，下一步再补:
   - 更接近 runtime 的 waveform synthesis
   - 明确的 inference manifest / batch export
   - 正式 vocoder 接入
