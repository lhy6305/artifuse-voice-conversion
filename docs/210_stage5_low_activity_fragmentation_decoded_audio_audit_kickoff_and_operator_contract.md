# 210. Stage5 低活动段 fragmentation decoded 听审启动与操作契约

## 背景
- `docs/209_stage5_low_activity_probe_multisource_followup_and_gui_bundle_report.md`
  已确认:
  - `decoded`
    与
    `audit_proxy`
    给出的方向不一致
  - 所以后续人工定点复核，
    默认应优先围绕:
    - `decoded`
    - `decoded_pitch_matched`
    而不是
    `audit_proxy`
- 同时，
  probe
  已可自动导出:
  - GUI 可读 segmented bundle

## 本轮目标
1. 把当前
   low-activity
   定点听审
   收成
   可直接运行的正式入口
2. 固定:
   - 听审 bundle
   - 输出目录
   - 试听重点
3. 给出:
   - 一条正式命令
   - 一个脚本入口

## 当前听审对象

### 1. 当前 bundle 目录
- `reports/audio/stage5_low_activity_fragmentation_probe_activitygate60_vs_72_multisource/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step60/`
- `reports/audio/stage5_low_activity_fragmentation_probe_activitygate60_vs_72_multisource/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step72/`

### 2. 当前 session 输出目录
- `reports/audio/audio_audit_gui_stage5_low_activity_fragmentation_decoded_session/`

### 3. 当前对比对象含义
- `offline_mvp_nores_vocoder_dataset_loop.step60`
  - 当前低活动段专项问题的保留对照点
- `offline_mvp_nores_vocoder_dataset_loop.step72`
  - 当前默认主点，
    但在低活动段上
    暴露了更多
    fragmentation
    可疑窗口

## 用户应运行的正式命令

```powershell
.\python.exe manage.py launch-audio-audit-gui `
  --bundle `
    reports/audio/stage5_low_activity_fragmentation_probe_activitygate60_vs_72_multisource/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step60 `
    reports/audio/stage5_low_activity_fragmentation_probe_activitygate60_vs_72_multisource/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step72 `
  --output-dir reports/audio/audio_audit_gui_stage5_low_activity_fragmentation_decoded_session
```

## 对应脚本入口

```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_low_activity_fragmentation_decoded_audit.ps1
```

- 若只想做启动 smoke，
  可额外传:
  - `-AutoCloseMs 1000`

## 本轮主对比目标

### 1. 主问题
- 现在不是继续问:
  - `60`
    和
    `72`
    谁整体更好听
- 而是专门回答:
  - 在
    probe
    找出的低活动段可疑窗口里，
    `72`
    是否真的比
    `60`
    更容易出现:
    - 毛刺
    - 断续
    - 瞬态跳变

### 2. 当前更该关注的记录
- `target::chapter3_22_firefly_114`
  - 当前最强可疑窗口，
    `0.98s - 1.80s`
- `target::chapter3_3_firefly_213`
  - 当前上一轮人耳已点名的
    非音节 / breath-like
    风险样本
- `target::chapter3_4_firefly_106`
  - 当前 probe
    与上一轮结论
    都反复出现的长记录

## 具体怎么听

### 1. 每条记录先听 `播放输入`
- 当前对应:
  - 该窗口导出的
    `aligned_target.wav`
- 作用:
  - 确认本窗口里
    原本应当呈现的
    静音 / 低活动
    形态

### 2. 再分别播放两路 candidate
- `step60`
- `step72`

### 3. 当前最该关注的维度
- 低活动段是否还在
  突然冒出
  碎片化发声
- 静音 / breath-like
  区间是否出现
  断续、
  毛刺、
  抖一下的感觉
- 片段结束前后
  是否有不自然跳变

### 4. 当前先不要过度关注
- 最终完整音色像不像
- 全句整体感染力
- 高频细节是否像成品声码器

## 本轮验证

### 1. probe 产物已存在
- `reports/audio/stage5_low_activity_fragmentation_probe_activitygate60_vs_72_multisource/`

### 2. decoded segmented bundle 已存在
- `audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step60/`
- `audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step72/`

### 3. GUI 正式命令已做 smoke

```powershell
.\python.exe manage.py launch-audio-audit-gui --bundle reports/audio/stage5_low_activity_fragmentation_probe_activitygate60_vs_72_multisource/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step60 reports/audio/stage5_low_activity_fragmentation_probe_activitygate60_vs_72_multisource/audio_audit_bundles/decoded/offline_mvp_nores_vocoder_dataset_loop_step72 --output-dir reports/audio/audio_audit_gui_stage5_low_activity_fragmentation_decoded_session --auto-close-ms 1000
```

- 命令返回:
  - `exit code 0`
- session 目录已生成:
  - `audio_audit_progress.json`

### 4. 启动脚本也已做 smoke

```powershell
powershell -ExecutionPolicy Bypass -File scripts/launch_stage5_low_activity_fragmentation_decoded_audit.ps1 -AutoCloseMs 1000
```

## 当前操作建议
1. 默认先跑上面的正式命令
2. 听完后直接在:
   - `reports/audio/audio_audit_gui_stage5_low_activity_fragmentation_decoded_session/`
   留下
   `audio_audit_review.json`
   和
   `audio_audit_review.md`
3. 若后续还想看
   `audit_proxy`
   只作为:
   - 技术对照补听，
   不覆盖主结论

## 一句话结论
- 当前 Stage5
  低活动段专项听审
  已经具备:
  - 固定 bundle
  - 固定输出目录
  - 固定命令
  - 固定脚本入口
- 你现在可以直接开听，
  不需要再手工拼路径。
