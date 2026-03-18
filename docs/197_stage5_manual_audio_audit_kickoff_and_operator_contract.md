# 197. Stage5 manual audio audit kickoff and operator contract 报告

## 背景
- `docs/196_stage5_audio_audit_gui_bundle_integration_report.md`
  已把 Stage5 waveform route
  接到现有
  `audio_audit_gui.py`
- 但如果下一步要交给用户
  做人工听审，
  还必须明确写死：
  - 运行命令
  - 对比对象
  - 试听重点
  - 输出目录

## 本轮目标
1. 把 Stage5 人工听审
   从“概念上可做”
   收成
   “用户现在就能运行”
2. 固定本轮主对比对象
3. 产出一条正式命令
   和一个脚本入口

## 本轮实际完成

### 1. 新增两组对比 bundle
- 已导出:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_step96_validation_round1_1`
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_step48_validation_round1_1`
- 与已有:
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_step72_validation_round1_1`
  组成三路对比

### 2. 当前听审对象固定为同一批 6 条 validation 记录
- `target::chapter3_3_firefly_162`
- `target::chapter3_22_firefly_114`
- `target::chapter3_3_firefly_213`
- `target::chapter3_3_firefly_122`
- `target::chapter3_4_firefly_109`
- `target::chapter3_4_firefly_106`

### 3. 当前三路候选含义
- `stage5_stable_late_stop_step72`
  - 主路线默认工程 checkpoint
- `stage5_best_validation_step96`
  - best-by-loss 对比目标
- `stage5_best_rms_step48`
  - 幅度平衡参照目标

## 用户应运行的正式命令

```powershell
.\python.exe manage.py launch-audio-audit-gui `
  --bundle reports/runtime/offline_mvp_nores_vocoder_audio_export_step72_validation_round1_1 `
           reports/runtime/offline_mvp_nores_vocoder_audio_export_step96_validation_round1_1 `
           reports/runtime/offline_mvp_nores_vocoder_audio_export_step48_validation_round1_1 `
  --output-dir reports/audio/audio_audit_gui_stage5_step72_vs_step96_vs_step48_session
```

## 对应脚本入口

```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_audio_audit_step72_vs_step96_vs_step48.ps1
```

- 若只想做脚本级 smoke，
  可额外传:
  - `-AutoCloseMs 1000`

## 当前听审输出目录
- `reports/audio/audio_audit_gui_stage5_step72_vs_step96_vs_step48_session/`

## 本轮主对比目标

### 1. 主对比
- `step72 stable_late_stop`
  对
  `step96 best_validation`
- 要回答的问题：
  - `step96`
    虽然平均 loss 更低，
    但是否出现更明显的：
    - 幅度过冲
    - 边界回退
    - 听感不稳定

### 2. 辅对比
- `step72 stable_late_stop`
  对
  `step48 best_rms`
- 要回答的问题：
  - `step72`
    是否在保持更好结构的同时，
    仍能维持足够接近
    `step48`
    的幅度平衡

## 具体怎么听

### 1. 每条记录先听 `播放输入`
- 这里对应:
  - `aligned_target.wav`
- 作用:
  - 作为当前训练目标对齐参考

### 2. 再逐个播放三路 candidate
- `stage5_stable_late_stop_step72`
- `stage5_best_validation_step96`
- `stage5_best_rms_step48`

### 3. 当前最该关注的维度
- 幅度稳定性
  - 有没有明显偏小声 / 偏大声 / 忽大忽小
- 边界
  - 句尾是否收得住
  - 中间停顿是否自然
- 整体可接受度
  - 是否有发飘、塌陷、毛刺、明显失真

### 4. 当前先不要过度关注
- 最终音色是否完美
- 高频细节是否接近完整 vocoder 成品
- 绝对主观“好不好听”的宽泛印象

## 本轮验证

### 1. 三路 bundle 已全部存在
- `step72`
- `step96`
- `step48`

### 2. 组合 GUI session 已做启动 smoke

```powershell
.\python.exe manage.py launch-audio-audit-gui --bundle reports/runtime/offline_mvp_nores_vocoder_audio_export_step72_validation_round1_1 reports/runtime/offline_mvp_nores_vocoder_audio_export_step96_validation_round1_1 reports/runtime/offline_mvp_nores_vocoder_audio_export_step48_validation_round1_1 --output-dir reports/audio/audio_audit_gui_stage5_step72_vs_step96_vs_step48_session --auto-close-ms 1000
```

- 命令返回:
  - `exit code 0`
- 当前 session 目录已生成:
  - `audio_audit_progress.json`

### 3. 启动脚本也已做 smoke

```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_audio_audit_step72_vs_step96_vs_step48.ps1 -AutoCloseMs 1000
```

- 命令返回:
  - `exit code 0`

## 一句话结论
- 当前 Stage5 人工听审
  已经不是
  “你自己找文件去听”，
  而是
  “有固定命令、有固定 bundle、有固定输出目录、有固定主对比问题”的正式可执行步骤。
