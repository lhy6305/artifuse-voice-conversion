# 2026-03-27 Stage5 output-head `bpae01` 人工听审失败与频谱图佐证报告

## 结论
- `docs/444_stage5_output_head_bpae01_relocalization_and_minimal_listening_contract_report.md`
  里的
  `output_head_bpae01`
  现已完成最小人工听审。
- 人工结论已经足够明确：
  - `bpae01`
    与
    `bhb01`
    几乎完全一致
  - `segment_0061`
    这类边界样本上仍然完全是 buzz
  - `peak_011`
    上也没有出现任何可称为
    voice structure
    的迹象，
    仍然是纯 buzz
- 因而这条线应正式判停：
  - 它不是
    `bhb01`
    的主观升级版
  - 更准确的定性应是：
    - 量化 anti-brightness
      继续改善
    - 但主观听感与上一轮失败候选几乎无差别，
      仍是 pure buzz
- 本轮用户还额外给出了一组线性频谱图，
  其说明与听审结论一致：
  - `1.png ~ 3.png`
    是三条导出片段中
    `bpae01`
    与
    `bhb01`
    交替播放得到的频谱图
  - `4.png`
    是第一条片段对应 target 的频谱图
  - 当前用户给出的直接解释是：
    - `1 ~ 3`
      主要表现为等距分布的直线
    - `4`
      则明显同时包含：
      - unvoice 的宽带砂状区
      - voice 的低频共振峰结构
- 因而这轮结论不仅是：
  - “听起来还是 buzz”
- 更应写成：
  - `bpae01`
    在频谱形态上也没有显著离开
    `bhb01`
    的稳定纯 buzz 轨道

## 一、人工听审结论
- 听审对象：
  - `strongest_native_candidate`
  - `output_head_high_band_bhb01`
  - `output_head_bpae01`
- 听审入口：
  - `reports/runtime/offline_mvp_teacher_first_vc_audible_compare_bundle_outputhead_bpae01_vs_bhb01_vs_strongest_round1_1/listening/`
- 用户实际结论：
  1. `bpae01`
     与
     `bhb01`
     几乎完全一致
  2. `segment_0061`
     上完全是 buzz
  3. `peak_011`
     上没有出现结构，
     仍然完全是纯 buzz

## 二、这轮应如何解释 `444`
- `444`
  的量化结论并不是假的：
  - `bpae01`
    的确继续压低了
    centroid / high-band
  - native validation3
    也的确维持住了
    `auto_reject = 0/3`
  - `aper * noise_E`
    在
    `decoder_hidden -> waveform_decoder_base_logits`
    的旧大 jump
    也确实被压平了
- 但人工听审现在说明：
  - 这些量化变化并没有转化成
    可听的人声结构
  - 反而更像：
    - 在 pure buzz 家族内部
      做了亮度与耦合分配的重写
    - 但没有跨过
      从 buzz
      到 voice-like structure
      的门槛
- 因而当前不能再继续把
  `bpae01`
  写成：
  - 值得治理的新主候选
  - 或者
  - 只差最后一点人工确认

## 三、频谱图佐证
- 本轮用户额外给出了四张临时线性频谱图：
  - `1.png`
  - `2.png`
  - `3.png`
  - `4.png`
- 为避免后续临时文件被删除，
  已归档到：
  - `reports/audio/outputhead_bpae01_human_audit_spectrograms_round1_1/`
- 当前归档文件：
  - `reports/audio/outputhead_bpae01_human_audit_spectrograms_round1_1/1.png`
  - `reports/audio/outputhead_bpae01_human_audit_spectrograms_round1_1/2.png`
  - `reports/audio/outputhead_bpae01_human_audit_spectrograms_round1_1/3.png`
  - `reports/audio/outputhead_bpae01_human_audit_spectrograms_round1_1/4.png`
- 用户提供的解释为：
  - `1 ~ 3`
    代表
    `bpae01 / bhb01`
    交替播放时的导出片段频谱
  - 这些图主要是
    等距分布的直线，
    说明两者都停留在稳定单调的 buzz 形态
  - `4`
    代表 target，
    明显同时含有：
    - unvoice 的宽带砂状区
    - voice 的低频共振峰
- 这组频谱图的意义不是替代听审，
  而是进一步确认：
  - `bpae01`
    和
    `bhb01`
    的差别，
    至少在当前这组三样本上，
    没有形成“结构型改变”

## 四、当前主线应如何更新
- 当前 output-head 主线应从：
  - `最小 wav 听审后再决定 bpae01 是否 promoted`
  更新为：
  - `bpae01`
    已完成人工听审并正式失败
- 当前不再继续做：
  - `bpae01`
    同层权重微调
  - 围绕
    `aper * noise_E`
    base-logits product penalty
    的进一步小 sweep
  - 再发一轮同类 pure-buzz 听审
- 下一步应继续上收到：
  - residual-shape interface
  - 以及 output head
    上单项
    `aper / noise_E`
    的重新放大
- 更准确的问题应写成：
  - 为什么把乘积 jump
    压平以后，
    系统仍然只会生成
    与
    `bhb01`
    几乎等价的 pure buzz

## 五、一句话结论
- `output_head_bpae01` 虽然量化上继续压低了亮度并压平了旧的 `aper * noise_E` base-logits jump，但人工听审已明确它与 `bhb01` 几乎完全一致、仍然完全是 pure buzz；用户补充的线性频谱图也给出一致佐证，因此这条线应正式判停。
