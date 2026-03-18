# 199. Stage5 partial human audit signal and progress decision 报告

## 背景
- `docs/197_stage5_manual_audio_audit_kickoff_and_operator_contract.md`
  已把 Stage5
  三路听审入口固定为:
  - `step72 stable_late_stop`
  - `step96 best_validation`
  - `step48 best_rms`
- `docs/198_stage5_audio_audit_proxy_retuning_and_silence_gate_fix_report.md`
  已把 GUI 默认播放内容
  改为:
  - `audit_proxy.wav`

## 本轮新增人工反馈
- 用户补充说明:
  - 当前只听了 GUI 里的前两条样本
  - 后面的 special / 无音节内容
    暂未试听
- 当前主观排序口径为:
  - 第一行 `<` 第二行 `<<` 第三行
- 结合当前 session
  的 manifest 加载顺序，
  这对应:
  - `step72 < step96 << step48`
- 当前 session 里
  已明确落盘的一条人工选择是:
  - `target::chapter3_22_firefly_114`
    - `best_rhythm = step48`
    - `overall_pick = step48`

## 本轮目标
1. 判断:
   - 在只听了前两条样本的情况下，
     是否必须强行补完试听
     才能继续推进
2. 把主观信号
   转成客观量化
3. 判断当前真正主线问题
   更偏:
   - checkpoint selection
   - 还是模型级动态 / 静音控制

## 本轮量化复核

### 1. 复核范围
- 仅针对用户已听过的两条记录:
  - `target::chapter3_22_firefly_114`
  - `target::chapter3_3_firefly_122`
- 对比对象:
  - `step72`
  - `step96`
  - `step48`

### 2. 观测指标
- `audit_proxy.wav`
  相对 `aligned_target.wav`
  的:
  - 振幅包络相关性
  - 振幅包络 MAE
  - 帧间变化相关性
  - 动态标准差比例
  - 静音帧 RMS
- 以及 raw `decoded.wav`
  的同类指标

## 核心结果

### 1. 对用户实际听到的 `audit_proxy.wav`，三者差距很小，当前不足以仅凭这两条样本就正式改默认 checkpoint
- 两条已听记录上的 aggregate:
  - `step72 audit_env_corr = 0.723078`
  - `step96 audit_env_corr = 0.724422`
  - `step48 audit_env_corr = 0.721270`
- `audit_env_mae` 也非常接近:
  - `step72 = 0.046467`
  - `step96 = 0.046137`
  - `step48 = 0.046612`
- `audit_silent_rms` 同样接近:
  - `step72 = 0.001485`
  - `step96 = 0.001571`
  - `step48 = 0.001486`

这说明:
- 当前用户的局部主观偏好
  是有效信号
- 但从已听两条样本的
  当前量化结果看，
  还不足以直接把:
  - `step48`
  升格为
  唯一正式默认点

### 2. 真正更强的负面信号，不在三者谁赢一点，而在 raw `decoded.wav` 三者都明显不对
- 两条已听记录 aggregate:
  - `step72 decoded_env_corr = 0.083333`
  - `step96 decoded_env_corr = 0.141452`
  - `step48 decoded_env_corr = 0.051597`
- `decoded_dynamic_std_ratio`
  全都很低:
  - `step72 = 0.098807`
  - `step96 = 0.100353`
  - `step48 = 0.095554`
- `decoded_silent_rms`
  全都很高:
  - `step72 = 0.118515`
  - `step96 = 0.124974`
  - `step48 = 0.118856`

这说明:
- 当前 Stage5
  raw decoded
  的主要问题
  不是:
  - `48 / 72 / 96`
    谁略好一点
- 而是:
  - 三者都还没有
    学会像样的动态跟随
  - 三者都还没有
    学会真实静音控制

### 3. 因此当前可以继续推进，而且不必为了“先选 48 还是 72 还是 96”强行补完试听
- 原因不是
  听审不重要，
  而是当前已经有更强的工程信号:
  - 模型级动态 / 静音控制
    才是主 blocker
- 在这种情况下，
  继续逼用户补完听审，
  收益不如直接推进:
  - silence-aware objective
  - 或 gate / waveform
    更强耦合

## 当前判断

### 1. 可以继续推进，不必先补完全部试听
- 现在最合理的口径是:
  - 当前人工听审结果
    记为
    provisional signal
  - 不把它当成
    正式最终裁决
- 但这不阻碍下一步
  进入模型级问题处理

### 2. 当前不建议正式改写默认 checkpoint
- 当前主观信号:
  - 对 `step48`
    有正面偏好
- 但范围只有:
  - 前两条样本
- 而且当前客观量化
  没有显示:
  - `audit_proxy`
    上的明显压倒性领先
- 所以现在更合理的是:
  - 保留
    `step72 = default stable late-stop`
  - 同时记录:
    `step48`
    在当前局部听审里
    更自然

### 3. 当前最合理的下一棒
- 不再优先做
  更多 checkpoint 听审
- 改为优先推进:
  - Stage5 dynamic-follow / silence-control
    诊断与修正

## 一句话结论
- 当前不需要为了继续推进而强行补完试听；
  现有前两条样本的主观信号
  已足够说明:
  - `step48`
    在局部听感上
    可能更自然
  但更强、更明确的工程结论其实是:
  - `48 / 72 / 96`
    三者的 raw `decoded.wav`
    都还没有解决
    动态跟随和静音控制，
  因此下一步应继续推进模型级修正，
  而不是先卡死在“必须补完全部听审”。
