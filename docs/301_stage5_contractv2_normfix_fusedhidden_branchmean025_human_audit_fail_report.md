# 2026-03-24 Stage5 `contractv2_normfix` `fused_hidden_branch_mean=0.25` 人工听审失败报告

## 结论
- 用户已完成对以下两组 fixed-record
  导出包的人工试听：
  - baseline：
    `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_baseline_smoke_round1_2/`
  - candidate：
    `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_fusedhidden_branchmean025_smoke_round1_1/`
- 当前正式主观结论是：
  - 两组包中的
    `decode_*.wav`
    **仍然都是 buzz**
  - **没有可标记的人声成分**
- 因而当前必须把
  `fused_hidden_branch_mean=0.25`
  这条最小候选
  定位为：
  - **量化上首次触达了更合理层级**
  - 但**可听上仍然明确失败**

## 一、听审对象

### baseline 包
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_baseline_smoke_round1_2/`

### candidate 包
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_fusedhidden_branchmean025_smoke_round1_1/`

### 固定记录集
- `target::chapter3_2_firefly_212`
- `target::chapter3_2_firefly_155`
- `target::chapter3_3_firefly_162`
- `target::chapter3_17_firefly_133`
- `target::chapter3_3_firefly_245`
- `target::chapter3_2_firefly_163`

## 二、当前人工听审结论
- baseline：
  - 仍是纯 buzz
  - 没有可标记人声
- candidate：
  - 同样仍是纯 buzz
  - 没有可标记人声

## 三、这条结论如何解释
1. `docs/300`
   的量化改善
   不能再被写成：
   - 已经出现可听萌芽
2. 更准确的解释是：
   - `branch_mean`
     约束
     确实碰到了
     更合理的问题层级
   - 但当前
     `0.25`
     这一级别的 loss-only
     训练改动，
     还不足以把系统推出
     buzz-only
     失败区
3. 因此这条结果更支持：
   - 现在需要的不是
     同类小权重继续磨
   - 而是更大的
     forward-path
     或 loss 形态变化

## 四、当前对路线的直接含义
1. 不应继续把
   `fused_hidden_branch_mean=0.25`
   写成：
   - 只差长训
   - 或只差小 sweep
2. 当前更合理的判断是：
   - `fusion`
     层级是对的
   - 但
     **仅靠轻量 loss 拉近**
     还不够
3. 下一步默认不建议：
   - 回到
     decode-side
     quant-only
     小 loss
4. 下一步更合理的主线应转向：
   - 直接改
     decoder 实际看到的
     hidden 输入分布
   - 或采用更强的
     fusion-side
     forward-path
     干预

## 一句话结论
- `fused_hidden_branch_mean=0.25`
  虽然是目前量化上最像样的
  fusion-side
  候选，
  但人工听审已正式确认：
  - `decode_*.wav`
    仍然全是 buzz，
    没有可标记语音；
  所以下一步不该继续沿这条
  loss-only
  小调路线打转，
  而应升级为更大的
  forward-path
  或 loss 形态改动。
