# 2026-03-24 Stage5 `contractv2_normfix` `active_template=0.05 + frame_delta=6.0` 人工听审失败报告

## 结论
- 用户已完成对以下两组 fixed-record
  导出包的人工试听：
  - baseline：
    `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_baseline_smoke_round1_2/`
  - candidate：
    `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_active_template005_delta6_smoke_round1_1/`
- 当前正式主观结论是：
  - **彻底的 buzz**
  - **不带任何人声成分**
- 这意味着：
  - `active_template = 0.05`
    `frame_delta = 6.0`
    这轮最小 objective smoke
    虽然改写了 objective-side
    指标，
    但在可听结果上
    仍属于明确失败。

## 一、听审对象

### baseline 包
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_baseline_smoke_round1_2/`

### candidate 包
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_contractv2_normfix_active_template005_delta6_smoke_round1_1/`

### 固定记录集
- `target::chapter3_2_firefly_212`
- `target::chapter3_2_firefly_155`
- `target::chapter3_3_firefly_162`
- `target::chapter3_17_firefly_133`
- `target::chapter3_3_firefly_245`
- `target::chapter3_2_firefly_163`

## 二、当前人工听审结论
- baseline：
  - 彻底的 buzz
  - 不带任何人声成分
- candidate：
  - 同样是彻底的 buzz
  - 不带任何人声成分

## 三、这条结论如何解释
- 结合
  `docs/294`
  的量化结果，
  当前更准确的解释不是：
  - 这条 objective
    已接近成功，
    只是还差一点
- 而是：
  - 当前 objective
    只是在
    anti-template
    指标上推动了模型，
  - 但这种推动
    还没有转成
    任何可辨识语音，
  - 系统在可听层面
    仍停留在
    buzz-only
    失败区。

## 四、当前对路线的直接含义
1. 不应继续把：
   - `active_template = 0.05`
   - `frame_delta = 6.0`
   这条线
   写成
   “已出现可听萌芽”
2. 也不建议直接沿这条线：
   - 只靠增加训练步数
   - 或只做同类小权重微调
   继续推进
3. 当前更合理的阶段判断应是：
   - objective-side
     小修
     已经验证过方向，
     但不足以让系统脱离
     buzz-only
4. 下一步默认应转向：
   - 更强的
     decoder / waveform head
     结构级诊断
   - 或更明显改变
     waveform objective
     形态的路线

## 一句话结论
- 当前这轮
  `active_template=0.05 + frame_delta=6.0`
  最小 smoke
  已经被人工听审正式判定为失败：
  - 输出仍是彻底的 buzz，
    没有任何人声成分；
  因此下一步不该再把它当成
  “继续细调就可能转正”的近成功路线。
