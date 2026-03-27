# 2026-03-27 Stage5 output-head high-band 人工听审失败与 GUI 降级报告

## 结论
- `docs/441_stage5_output_head_headstruct_high_band_candidate_breakthrough_report.md`
  里的
  `output_head_high_band_bhb01`
  虽然量化上明显压低了亮度，
  也摆脱了
  `440`
  那种
  native `auto_reject = 3/3`
  的直接坏死状态，
  但本轮人工听审结论已经足够明确：
  - 仍然是纯 buzz
  - 只是变成了
    “带一点明显音调变化的 buzz”
- 因而这条 high-band route
  不能再写成：
  - 待最终确认的可能 winner
- 更准确的定性应是：
  - 它是一个量化侧改善成立、
    但主观上仍未越过
    pure-buzz
    门槛的失败候选
- 同时，本轮也确认：
  - 对这类“只是判断是否仍为 pure buzz”
    的实验，
    没必要默认上
    GUI
    量化打分
  - 更合适的交付应回到：
    - 直接可听 wav 目录
    - 外加简短对比说明

## 一、人工听审结论
- 听审对象：
  - 旧 strongest native candidate
  - 对比
  - `output_head_high_band_bhb01`
- 听审入口：
  - `reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_outputhead_highband_vs_strongest_round1_1/listening/`
- 用户实际结论：
  - `bhb01`
    确实有变化
  - 但仍然是纯 buzz
  - 更像带一点明显音调变化的 buzz

## 二、当前应如何解释 `441`
- `441`
  的量化突破并不是假的：
  - brightness
    的确被压下来了
  - native validation3
    也的确从
    `auto_reject = 3/3`
    恢复到
    `0/3`
  - `waveform_handoff`
    也首次不再显示
    `frames before gate`
    已坏死
- 但这轮人工听审说明：
  - 这些改善还停留在
    “坏样本内部的形态变化”
  - 还没有跨过
    从 buzz
    到可接受人声结构
    的真正门槛
- 因而当前不能再继续沿
  `high_band_excess`
  这条线做：
  - 继续小扫权重
  - 再补一次同级别听审
  - 再把它包装成
    “也许就差最后一点”

## 三、主线如何更新
- 当前 output-head 主线应从：
  - `继续治理 bhb01`
  更新为：
  - `bhb01`
    已完成人工听审并正式失败
- 下一步不再优先做：
  - high-band 同层微调
  - pure-buzz 判别型 GUI 打分
- 更合理的后续问题应回到：
  - 为什么 `aper * noise_E`
    在
    `decoder_hidden -> waveform_decoder_base_logits`
    仍残留 jump
  - 为什么压亮度以后，
    系统只得到“有音调的 buzz”，
    而不是更接近人声的结构

## 四、GUI 这轮的结论
- 用户反馈里，
  GUI
  还出现了
  “找不到这个包”
  的报错。
- 当前确认：
  - 这类 compare bundle
    以前如果只传目录，
    `audio_audit_gui`
    的目录解析确实可能去找错默认 manifest
- 本轮已顺手补齐目录解析，
  现在会优先识别：
  - `teacher_first_vc_audible_compare_bundle.json`
  - `teacher_first_vc_audible_smoke_bundle.json`
- 但即便如此，
  当前流程建议仍应写成：
  - 对 pure-buzz / non-pure-buzz
    的快速判别，
    默认直接给 wav 目录
  - 不再默认交给
    GUI
    量化打分

## 五、当前保留的交付物
- 保留 compare bundle，
  但用途下调为：
  - 失败证据归档
  - 后续 root-cause 对比样本
- 当前真正的一线入口应写成：
  - `reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_outputhead_highband_vs_strongest_round1_1/listening/`

## 一句话结论
- `output_head_high_band_bhb01` 虽然量化上比旧 strongest 更暗、更不像 `440` 那种直接坏死，但人工听审已明确它仍是“带一点音调变化的纯 buzz”，因此这条线应正式判停；同时这类 pure-buzz 判别实验以后默认直接交 wav 目录，不再默认上 GUI 打分。
