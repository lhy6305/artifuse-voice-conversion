# `round1.1 / proxy-audio re-synthesis after user audit` 报告

## 目的
- 记录首轮用户试听反馈
- 明确首版 `proxy audio` 是否足以支撑人工审核
- 若不足，则直接修正重建器并重导试听包

## 首轮用户试听结论
用户对首版试听包的反馈是:
- 音频基本表现为高频啸叫
- 几乎无法稳定比较分支差异
- 唯一还能勉强听出的粗差异是:
  - 基准频率大致呈现 `D22 < D29 < D33`
  - `D33` 有少许不稳定感

这意味着:
- 首版 `proxy audio` 没有达到“可稳定做人耳相对比较”的最低标准
- 这轮试听结果不能直接当成正式的分支听感判优依据

## 根因定位
首版 `proxy audio` 的核心问题在于:
- `src/v5vc/proxy_audio_export.py`
  - 直接把 `zero_cross` 映射为可听主频
  - 具体等价于把高零交叉率直接推向更高的 audible tone

但在当前 MVP 里:
- `zero_cross` 更接近粗糙度 / 亮度 / 噪声倾向指标
- 它并不是可信的 `F0`
- 因此把它直接当主频，会把代理音频推成:
  - 高频化
  - 啸叫化
  - 难以比较节奏 / 断句 / 稳定性

## 本轮修正
已将 `proxy audio` 重建器改成更保守的低频包络代理:
- 不再让 `zero_cross` 直接决定可听主频
- 改为:
  - 用平滑后的低频 carrier 承载整体节奏
  - 用 `zero_cross` 仅调节 brightness / noise mix
  - 对噪声与最终输出都增加平滑，压低刺耳高频

当前新版本更适合听:
- 节奏
- 停顿
- 边界收束
- 粗粒度稳定性

当前仍不适合听:
- 最终音色
- speaker identity
- 高频真实感
- 绝对音高

## 重导状态
已基于修正后的重建器，重新导出:
- `reports/audio/offline_mvp_proxy_audit_d22_exp039/`
- `reports/audio/offline_mvp_proxy_audit_d29_exp045/`
- `reports/audio/offline_mvp_proxy_audit_d33_exp050/`

## 最小数值复核
对重导后的 `proxy.wav` 做粗粒度零交叉率检查:
- `D22 mean_zcr = 0.0138`
- `D29 mean_zcr = 0.0139`
- `D33 mean_zcr = 0.0166`

这说明:
- 当前代理波形整体已落到低零交叉率区间
- `D33` 仍保留了相对更亮 / 更不稳一点的粗差异
- 但新的审核结论仍需用户重新试听确认

## 当前结论
1. 首版 `proxy audio` 试听包无效，不应继续作为正式人工审核依据。
2. 当前已完成一轮去啸叫重建器修正与试听包重导。
3. 下一步应由用户对重导后的 `D22 / D29 / D33` 再试听一轮。
4. 在用户确认前，仍不把任何分支直接升为当前最优解。
