# 198. Stage5 audio audit proxy retuning and silence-gate fix 报告

## 背景
- 在 `docs/197_stage5_manual_audio_audit_kickoff_and_operator_contract.md`
  之后进入人工试听时，
  用户给出两个明确反馈:
  1. 当前分支音频的主观基频 / 载波感过高，
     心理上可能引起不适
  2. 三条分支在输入静音段也几乎全程出声，
     听起来像持续叠着固定噪声
- 在这种状态下，
  人工听审不应该继续硬做，
  而应先修听审导出链

## 本轮目标
1. 确认问题是否来自 Stage5 听审导出链本身
2. 把 GUI 默认播放的 Stage5 分支音频
   调整为更低刺激的听审代理
3. 保留原始 `decoded.wav`
   作为技术排查入口

## 问题定位

### 1. 当前 Stage5 GUI 播放的并不是“真实最终 vocoder 成品”
- 代码位置:
  - `src/v5vc/nores_vocoder_audio_export.py`
  - `src/v5vc/offline_vocoder_training.py`
- 现状是:
  - checkpoint 输出
    `waveform_frames`
  - 再经
    `reconstruct_waveform_from_frames(...)`
    overlap-add
    成
    `decoded.wav`
- 这条路径当前:
  - 不是最终 multi-resolution / adversarial vocoder
  - 也没有显式静音门控

### 2. “静音段全程不静音”不是错觉
- 本轮对 `step72` bundle
  的 `6` 条 validation 记录，
  按:
  - `frame_length = 400`
  - `hop_length = 160`
  - 目标帧 RMS `<= 0.003`
    作为静音近似
  做帧级复核
- 结果:
  - 原始 `decoded.wav`
    在目标静音帧上的平均 RMS
    约为:
    - `0.121756`
  - 这说明:
    - 当前 raw decoded
      几乎处于持续出声状态
    - 直接拿它进入 GUI
      会严重污染听感判断

## 本轮修正

### 1. Stage5 导出链新增 `audit_proxy.wav`
- 文件:
  - `src/v5vc/nores_vocoder_audio_export.py`
- 当前导出不再只有:
  - `aligned_target.wav`
  - `decoded.wav`
- 而是新增:
  - `audit_proxy.wav`

### 2. `audit_proxy.wav` 采用低频固定载波
- 当前载波频率固定为:
  - `185.0 Hz`
- 这是回到 Stage3
  proxy 听审里
  已证明可接受的低频风格，
  不再让 GUI 直接播放
  当前 raw decoded
  的高刺激版本

### 3. 静音 gate 由 `aligned_target.wav` 驱动
- 当前 `audit_proxy.wav`
  不再无条件播放全程活动
- 而是用:
  - `aligned_target`
    的帧级活动
  作为 gate 参考
- 这样目标静音段
  会被直接压回接近静音，
  不再被 decoded 自身的持续活动顶起来

### 4. GUI 默认播放目标已切换
- `proxy_audio_export.json`
  现在默认把:
  - `proxy_audio_path`
    指向
    `audit_proxy.wav`
- 同时保留:
  - `decoded_audio_path`
    供技术排查
- 也就是说:
  - GUI 继续能用
  - 但默认播放内容
    已从 raw decoded
    变成低频 audit proxy

## 实际验证

### 1. 三组 bundle 已全部重导
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_step72_validation_round1_1`
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_step96_validation_round1_1`
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_step48_validation_round1_1`

### 2. 现有导出目录已包含三类 wav
- `aligned_target.wav`
- `decoded.wav`
- `audit_proxy.wav`

### 3. 静音泄漏量化结果
- 口径:
  - `step72`
  - 6 条 validation 记录
  - 目标帧 RMS `<= 0.003`
- 结果:
  - `decoded.wav`
    静音帧平均 RMS:
    - `0.121756`
  - `audit_proxy.wav`
    静音帧平均 RMS:
    - `0.002147`

这说明:
- 当前听审导出链的静音污染
  已显著下降
- 至少从
  “全程明显持续出声”
  降到了
  “接近静音 gate 目标”

### 4. GUI session 已重新 smoke
- 启动脚本:
  - `scripts/launch_stage5_audio_audit_step72_vs_step96_vs_step48.ps1`
- smoke 命令:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_audio_audit_step72_vs_step96_vs_step48.ps1 -AutoCloseMs 1000
```

- 返回:
  - `exit code 0`
- 当前 session 目录:
  - `reports/audio/audio_audit_gui_stage5_step72_vs_step96_vs_step48_session/`
  已继续可用

## 当前结论

### 1. 用户提出的两点问题都成立，而且首先该修导出链，不该强推继续试听
- 高刺激听感
  与持续静音泄漏
  已经足够严重，
  会直接污染人工判断
- 在这一步继续听，
  收到的结论
  不可信

### 2. 当前更合理的 Stage5 听审口径
- GUI 默认播放:
  - `audit_proxy.wav`
- raw 技术排查仍保留:
  - `decoded.wav`
- 这样做的意义是:
  - 先恢复可执行的人工听审
  - 不把当前 bootstrap 解码头
    误当成最终可听成品

### 3. 这不等于 Stage5 waveform route 已解决真实静音问题
- 当前修的是:
  - 听审导出链
- 不是训练目标本身
- raw `decoded.wav`
  在静音段仍然活动很高，
  说明模型侧静音控制
  仍然是后续主问题之一

## 对用户当前应运行命令的影响
- 启动命令不变:

```powershell
.\python.exe manage.py launch-audio-audit-gui `
  --bundle reports/runtime/offline_mvp_nores_vocoder_audio_export_step72_validation_round1_1 `
           reports/runtime/offline_mvp_nores_vocoder_audio_export_step96_validation_round1_1 `
           reports/runtime/offline_mvp_nores_vocoder_audio_export_step48_validation_round1_1 `
  --output-dir reports/audio/audio_audit_gui_stage5_step72_vs_step96_vs_step48_session
```

- 但现在 GUI 实际播放的是:
  - `audit_proxy.wav`
  不是 raw `decoded.wav`

## 一句话结论
- 当前 Stage5 听审链
  已从
  “GUI 直接播放高刺激、静音泄漏严重的 raw decoded”
  修成
  “默认播放 `185 Hz` 低频 `audit_proxy.wav`，
   且按 `aligned_target` 做静音 gate”；
  raw `decoded.wav`
  仍保留用于技术排查，
  但不再作为当前人工听审默认入口。
