# 172. Stage3 proxy 静音泄漏审计与导出修正报告

## 背景
- 在继续试听
  `baseline48 vs proxytemporal20warm6`
  之前，
  用户提出一个关键疑问:
  - warm 版本有较大底噪
  - 甚至 `teacher_proxy`
    在静音段里
    似乎也会持续出声
- 这类问题如果不先确认，
  会直接污染人工判断，
  因为人耳会把:
  - 谁更安静
  - 谁更吵
  混进:
  - 稳定性
  - 边界
  - 节奏
    的比较里

## 本轮目标
1. 用代码和量化而不是主观印象，
   判断:
   - 静音底噪问题是否真实存在
2. 若存在，
   先修正导出链，
   再恢复试听

## 问题定位

### 1. 第一层问题: 合成器本身对所有帧都保留了最小底噪
- 文件:
  - `src/v5vc/proxy_audio_export.py`

旧实现里:
- 每帧都会强制:
  - `rms_target >= 0.005`
  - `abs_target >= 0.005`
- 同时始终混入:
  - 固定载波
  - 一定比例噪声

这意味着:
- 即使输入已经接近静音，
  只要该帧仍被纳入导出，
  `teacher_proxy / student_proxy`
  都会被合成为
  一点持续的低频底噪

### 2. 第二层问题: student 导出映射本身会把静音帧“抬活”
- 文件:
  - `src/v5vc/streaming_student/proxy_acoustic.py`

旧的 export 路径
  复用了训练侧 helper:
- `build_streaming_student_proxy_acoustic`

其中:
- `abs_mean`
  由
  - `rms_like`
  - `event_presence`
  - `voiced_prob`
    直接相加构成

结果:
- 即使 `energy`
  已经很低，
  只要
  `event_presence / voiced_prob`
  还维持在中等值，
  student export
  仍会在静音帧里
  产生明显活动

## 量化复核

### 量化方式
- 对当前 baseline48 / warm20
  两组 bundle
  的 validation + special 样本，
  以与模型一致的:
  - `frame_length = 400`
  - `hop_length = 160`
    做帧级 RMS
- 用输入帧 RMS
  小于等于:
  - `0.003`
  - `0.005`
  - `0.01`
    的帧
  作为静音近似集合
- 统计这些静音帧里:
  - `input`
  - `teacher_proxy`
  - `student_proxy`
    的平均 RMS

### 修正前的关键观察
- baseline / warm
  里，
  `teacher_proxy`
  在静音帧上的平均 RMS
  常见落在:
  - `0.005 ~ 0.008`
- warm `student_proxy`
  在静音帧上的平均 RMS
  甚至常见达到:
  - `0.012 ~ 0.022`

这说明:
- 用户听到的
  “静音段也在出声”
  不是错觉
- 而且问题不只在 warm student，
  `teacher_proxy`
  也被导出链人为抬高了

## 本轮修正

### 1. 为 proxy 合成新增静音 gate
- 文件:
  - `src/v5vc/proxy_audio_export.py`

新增逻辑:
- 根据 frame 的
  `rms_target / abs_target`
  计算:
  - `activity_gate`
- 对极低活动帧:
  - 直接跳过输出
- 对低活动帧:
  - 按 gate
    成比例压低合成振幅与噪声占比

效果:
- `teacher_proxy`
  的静音段伪底噪
  大幅下降

### 2. 新增 export 专用的 student proxy 映射
- 文件:
  - `src/v5vc/streaming_student/proxy_acoustic.py`
  - `src/v5vc/streaming_student/proxy_audio_export.py`

新增:
- `build_streaming_student_proxy_acoustic_for_export`

原则:
- 训练侧 helper
  不改，
  避免影响既有 loss / eval 口径
- 导出侧单独改成:
  - 主要由 `energy`
    决定静音/活动
  - 不再允许
    `event_presence / voiced_prob`
    在低能量时
    直接把静音帧抬成有声帧

## 修正后的量化结果

### 1. `teacher_proxy` 静音泄漏已明显下降
- 例如 `baseline48_validation`
  的静音帧里，
  旧版 `teacher_proxy`
  常见:
  - `0.007 ~ 0.008`
- 修正后同口径下，
  多数记录下降到:
  - `0.0001 ~ 0.0025`
  或接近:
  - `0`

这说明:
- `teacher_proxy`
  原先那部分静音底噪
  主要是导出伪影，
  现在已经基本压掉

### 2. warm `student_proxy` 也显著下降，但没有完全消失
- 例如 warm special
  静音帧平均 RMS
  修正前常见:
  - `0.016 ~ 0.022`
- 修正后约降到:
  - `0.008 ~ 0.015`

### 3. 当前更准确的解释
- 旧版问题确实存在，
  而且一部分来自导出链
- 现在导出链的系统性静音伪底噪
  已经明显降低
- 但 warm student
  相比 baseline
  在静音段仍然更容易保持活动，
  这更像模型本身的残余问题，
  不是单纯导出错觉

## 本轮产物处理

### 已重导 bundle
- `reports/audio/streaming_student_proxy_audit_baseline48_step48_v1/`
- `reports/audio/streaming_student_proxy_audit_baseline48_step48_special_v1/`
- `reports/audio/streaming_student_proxy_audit_proxytemporal20warm6_step12_v1/`
- `reports/audio/streaming_student_proxy_audit_proxytemporal20warm6_step12_special_v1/`

### 已复核当前会话入口
- `reports/audio/audio_audit_gui_stage3_baseline48_vs_proxytemporal20warm6_session/`

启动方式:

```powershell
.\python.exe manage.py launch-audio-audit-gui `
  --output-dir reports/audio/audio_audit_gui_stage3_baseline48_vs_proxytemporal20warm6_session
```

## 当前结论
1. 用户关于
   `teacher_proxy`
   静音底噪的怀疑
   是正确的，
   不是错觉
2. 这部分问题
   已优先在导出链修正，
   并重导了当前要听的 bundle
3. 修正后，
   warm `student_proxy`
   仍比 baseline
   更容易在静音段保留活动，
   说明这部分差异现在更接近
   模型真实行为，
   可以再进入人工试听

## 对训练侧的影响判断

### 1. 旧版合成器的最小底噪没有直接进入 student 训练
- 原因:
  - `synthesize_proxy_waveform`
    只在导出/试听链使用
  - Stage3 训练时实际使用的是:
    - `src/v5vc/streaming_student/losses.py`
      里的 teacher-supervised losses
    - 以及训练侧
      `build_streaming_student_proxy_acoustic`
      的张量映射

这意味着:
- “合成器强制保底噪声”
  这件事本身
  没有被 student
  直接学进去

### 2. 但 warm student 确实学到了/保留了更高的静音活动
- 在输入静音帧上，
  本轮额外量化发现:
  - baseline48
    的 `energy_log`
    常在约:
    - `-7`
  - warm20
    常在约:
    - `-4`
  - baseline48
    的 `voiced_prob / event_presence`
    常在约:
    - `0.30 ~ 0.42`
  - warm20
    则常在约:
    - `0.62 ~ 0.64`

这说明:
- warm 的问题
  不是只靠导出修正
  就会自动消失
- 它在模型输出层
  也更倾向于把静音段
  预测成“还有活动”

## 是否需要重训

### 当前判断
1. 不需要因为这次导出修正
   去重训 baseline48
2. 也不需要因为旧版
   `teacher_proxy`
   有导出伪底噪，
   就回头重训所有 student
3. 但如果 warm 路线
   经过修正后试听，
   仍被确认静音段明显更吵，
   那么后续若想继续保留
   temporal supervision，
   就需要新一轮训练实验，
   显式处理:
   - 静音稳定性
   - 静音抑制
   - 或 silence-aware loss / gating

## 一句话结论
- 静音底噪问题真实存在，
  且旧版确实连 `teacher_proxy`
  也被导出链抬出了伪底噪；
  现在这部分已修正并重导。
- 当前若继续试听，
  应以修正后的 bundle 为准；
  若仍听到 warm 更吵，
  那更可能是模型自身的静音稳定性问题，
  而不是导出错觉。
