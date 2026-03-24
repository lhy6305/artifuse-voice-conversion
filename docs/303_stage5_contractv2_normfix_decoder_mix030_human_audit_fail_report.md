# 2026-03-24 Stage5 `contractv2_normfix` `decoder_mix030` 人工听审失败报告

## 结论
- 用户已完成对以下两组 fixed-record
  导出包的人工试听：
  - baseline：
    `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_baseline_smoke_round1_2/`
  - candidate：
    `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_decoder_mix030_smoke_round1_1/`
- 当前正式主观结论是：
  - 两组包中的
    `decode_*.wav`
    **仍然都是 pure buzz**
  - **没有可标记的人声成分**
- 因而当前必须把
  `decoder_branch_mean_mix_alpha=0.30`
  这条 forward-path
  线性 mix
  候选定位为：
  - **量化上进一步证明了 forward-path 方向是对的**
  - 但**可听上仍然明确失败**

## 一、听审对象

### baseline 包
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_baseline_smoke_round1_2/`

### candidate 包
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_decoder_mix030_smoke_round1_1/`

### 固定记录集
- `target::chapter3_2_firefly_212`
- `target::chapter3_2_firefly_155`
- `target::chapter3_3_firefly_162`
- `target::chapter3_17_firefly_133`
- `target::chapter3_3_firefly_245`
- `target::chapter3_2_firefly_163`

## 二、当前人工听审结论
- baseline：
  - 仍是 pure buzz
  - 没有可标记人声
- candidate：
  - 同样仍是 pure buzz
  - 没有可标记人声

## 三、这条结论如何解释
1. `docs/302`
   中
   `decoder_mix030`
   在量化上的改善，
   不能再被写成：
   - 已接近语音出现
   - 或只差长训
2. 更准确的解释是：
   - 直接改
     decoder
     输入分布
     确实比
     loss-only
     更有效
   - 但当前这种
     **静态线性 mix**
     仍不足以把系统推出
     buzz-only
     失败区
3. 因此这条结果更支持：
   - 下一步需要的不是
     `alpha`
     微扫
   - 而是更强的
     结构变化

## 四、当前对路线的直接含义
1. 不应继续把
   `decoder_mix030`
   写成：
   - 最佳候选只差长训
   - 或再试
     `0.20 / 0.35 / 0.40`
     就可能出来
2. 当前更合理的判断是：
   - 主问题仍在
     decoder
     实际消费的
     hidden manifold
   - 但
     **简单线性插值还不够**
3. 下一步默认不建议：
   - 继续做
     static linear mix
     小 sweep
4. 下一步更合理的主线应转向：
   - 带条件门控的
     结构化双路 decoder
   - 或至少是
     frame-wise / activity-aware
     的动态 mixing

## 一句话结论
- `decoder_mix030`
  虽然比
  loss-only
  更清楚地证明了
  forward-path
  是对的，
  但人工听审已正式确认：
  - `decode_*.wav`
    仍然全是 pure buzz，
    没有可标记语音；
  所以下一步不该继续做
  线性 mix
  小调参，
  而应升级为真正的
  结构级改动。
