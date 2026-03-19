# 204. Stage5 decoded primary listening contract 报告

## 背景
- 本轮用户明确提醒:
  - 与其继续主听
    `audit_proxy.wav`
  - 不如尽量主听
    更接近最终合成效果的
    音频
- 这个提醒成立，
  因为:
  - `audit_proxy.wav`
    不是人耳日常处理的
    正常说话音频
  - 它更适合抓:
    - dynamic-follow
    - silence-control
    - boundary leakage
  - 不适合当:
    - 成品自然度
    - 连续多音节波动
    - 整体听感
    的主判断依据

## 当前事实边界
- 当前 Stage5
  仍没有真正
  final multi-resolution /
  adversarial vocoder
  成品链路
- 现有最接近最终可听结果的
  仍是:
  - `decoded.wav`
- 所以更合理的当前口径是:
  - `decoded.wav`
    作为主试听对象
  - `audit_proxy.wav`
    退到诊断位

## 本轮代码落地

### 1. `src/v5vc/cli.py`
- 为
  `export-offline-mvp-nores-vocoder-audio`
  新增参数:
  - `--listening-audio-source`
- 当前支持:
  - `decoded`
  - `audit_proxy`
- 默认值改为:
  - `decoded`

### 2. `src/v5vc/nores_vocoder_audio_export.py`
- 当前 exporter
  会把:
  - `listening_audio_source`
  写入 summary
- 同时把 GUI-compatible manifest
  中的:
  - `proxy_audio_path`
  指向当前主试听源
- 也就是说:
  - 若选
    `decoded`
    则 GUI 默认播放
    `decoded.wav`
  - `audit_proxy.wav`
    仍保留在 bundle
    里供诊断

## 对当前工作流的影响

### 1. 当前 `activitygate60/72` bundle 已重导为主听 decoded
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate60_validation_round1_1`
- `reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_validation_round1_1`

两者现在都明确记录:
- `listening_audio_source = decoded`

### 2. GUI session 已重新 smoke

```powershell
.\python.exe manage.py launch-audio-audit-gui --bundle reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate60_validation_round1_1 reports/runtime/offline_mvp_nores_vocoder_audio_export_activitygate72_validation_round1_1 --output-dir reports/audio/audio_audit_gui_stage5_activitygate60_vs_72_decoded_session --auto-close-ms 1000
```

- 结果:
  - `exit code 0`

### 3. 启动脚本无需改路径，只需确保 bundle 已按新口径重导
- 当前脚本:
  - `scripts/launch_stage5_audio_audit_activitygate60_vs_72.ps1`
- 依旧可用，
  因为它指向的是 bundle 目录，
  而目录中的
  `proxy_audio_export.json`
  已切到:
  - `decoded.wav`

## 当前判断

### 1. 这次工作流切换是对的，但不能误写成“现在已经在听 final synth”
- 更准确的说法是:
  - 现在改成主听
    `decoded.wav`
  - 它比
    `audit_proxy.wav`
    更接近最终合成
  - 但仍不是
    真正 final vocoder

### 2. `audit_proxy.wav` 仍有价值，只是不再主导人工结论
- 它现在更适合:
  - 排查动态 / 静音 / 边界
- 不再适合:
  - 主导成品听感判断

### 3. 后续正式契约应固定为“双轨”
- 主听:
  - `decoded.wav`
- 诊断:
  - `audit_proxy.wav`
- 等真正 final synth
  落地后，
  再把主听入口
  彻底切到 final synth

先说人话:
- 这一步不是说
  现在 suddenly
  已经有最终成品了。
- 只是把当前最接近成品的
  那条音频
  提到前台，
  不再让
  `audit proxy`
  这个辅助工具
  反客为主。

## 一句话结论
- 当前 Stage5
  人工听审口径
  已正式从
  “默认主听 `audit_proxy.wav`”
  切到
  “默认主听 `decoded.wav`，`audit_proxy.wav` 只作诊断”；
  这更符合人耳判断自然语音的方式，
  但仍需明确:
  - `decoded.wav`
    只是当前最接近最终合成的可听结果，
    不是最终成品链路本身。
