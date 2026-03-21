# 2026-03-21 Stage5 `step72__decode_gate_smooth3_postenv` 人工听审后默认提升报告

## 结论
- 当前 Stage5 decode-side 默认 apply mode
  正式提升为：
  - `post_ola_envelope`
- 这次提升同时覆盖：
  - `export-offline-mvp-nores-vocoder-audio`
  - `run-offline-mvp-teacher-first-vc-demo`
- 当前旧默认
  `pre_overlap_add`
  不再作为默认，
  但仍保留显式回退能力

## 提升依据

### 1. 量化不反转
- `docs/236_stage5_step72_decode_gate_smooth3_postenv_validation_report.md`
  已记录：
  - `validation3`
    与
    `validation12`
    上，
    `postenv`
    相比
    `smooth3`
    在
    fragmentation、
    alignment、
    waveform RMS、
    sample delta peak、
    spectral centroid / bandwidth / HF ratio gap
    上同向改善
  - 只有
    `rolloff95 gap`
    小幅变差

### 2. focused human audit 不反转
- 当前正式听审结果：
  - `reports/audio/audio_audit_gui_stage5_s72_s3_postenv_v12_session/audio_audit_review.json`
- aggregate:
  - `record_count = 10`
  - `completed_count = 10`
  - `overall_pick = 打平 10`
  - `best_boundary = 打平 10`
  - `most_stable = 打平 10`
- session note:
  - `postenv版本有误差级别的感觉更柔和，但除此之外与不带postenv版本完全一致。`

### 3. 当前工程解释
- 这次人工听审没有给出：
  - 对旧默认
    `pre_overlap_add`
    的任何反向支持
- 更准确的结论是：
  - 在人耳上，
    两者已接近等价
  - 量化上，
    `postenv`
    继续更优
  - 因此满足：
    - “量化支持”
    - “focused human audit 不反转”
    的默认提升条件

## 本次工程动作

### 1. 默认值调整
- `src/v5vc/cli.py`
  中：
  - `run-offline-mvp-teacher-first-vc-demo`
    的
    `--predicted-activity-gate-apply-mode`
    默认值改为：
    `post_ola_envelope`
  - `export-offline-mvp-nores-vocoder-audio`
    的
    `--predicted-activity-gate-apply-mode`
    默认值改为：
    `post_ola_envelope`

### 2. 用户线包装脚本兼容性
- `scripts/run_teacher_first_single_target_vc_demo.ps1`
  当前默认不再显式传旧值，
  因而会自然继承新的
  `postenv`
  默认
- 同时新增显式回退开关：
  - `-UsePreOverlapAdd`
- 旧的：
  - `-UsePostEnv`
    仍保留，
    作为显式声明当前默认分支的兼容写法

## 为什么现在可以默认化
- 在 focused human audit
  完成前，
  `postenv`
  只能被写成：
  - 待审主分支
- 现在这个前置条件已经补齐：
  - 量化已支持
  - focused human audit 没有反转
  - session note
    还轻微偏向
    `postenv`
    更柔和
- 所以继续把
  `postenv`
  留在“只有懂上下文的人才会手动切”的状态，
  已经没有工程意义

## 兼容性口径
- 旧实验与旧报告不回写
- 如需复现旧 decode 行为，
  仍可显式传：

```powershell
.\python.exe manage.py run-offline-mvp-teacher-first-vc-demo `
  ... `
  --predicted-activity-gate-apply-mode pre_overlap_add
```

或：

```powershell
.\scripts\run_teacher_first_single_target_vc_demo.ps1 `
  -InputAudio <wav> `
  -UsePreOverlapAdd
```

## 一句话结论
- 当前 `postenv`
  已经从
  “待审主分支”
  正式升级为
  Stage5 decode-side
  默认 apply mode；
  旧的
  `pre_overlap_add`
  仅保留为显式回退路径。
