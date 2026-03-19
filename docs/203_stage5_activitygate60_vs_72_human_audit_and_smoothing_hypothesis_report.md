# 203. Stage5 `activitygate60 vs 72` human audit 与 smoothing hypothesis 报告

## 背景
- `docs/202_stage5_activitygate_checkpoint_governance_and_audio_audit_kickoff_report.md`
  已把本轮
  activity-gate family
  的主听审对象
  固定为:
  - `step60`
  - `step72`
- 本轮用户完成听审后，
  给出新的关键信号:
  - 两者在人耳上
    几乎不可分辨
  - `72`
    主观上
    似乎更“柔和”一点
  - 两者都像是
    少了上一轮
    第三条候选那种
    连续多音节内的波动性

## 本轮目标
1. 把这轮人工听审信号
   正式落盘
2. 判断:
   - “更柔和”
     是否能被量化支持
   - “波动被平滑化”
     是否更像真实问题，
     还是更像
     旧 route
     的噪声式起伏消失了
3. 判断当前是否需要
   因听审结果
   改写默认 checkpoint

## 本轮人工反馈

### 听感结论
- 本轮
  `step60`
  与
  `step72`
  在当前试听维度上:
  - 节奏
  - 边界
  - 稳定性
  - 综合印象
  主观上
  基本打平
- 额外主观印象:
  - `72`
    似乎比
    `60`
    更柔和一点
- 新疑点:
  - 两者在连续多音节内
    的主观波动感
    都比上一轮
    未听完对比中的
    第三条候选
    更平

## 量化复核

### 1. 当前 `60 vs 72` 同批 6 条样本 aggregate

#### `step60`
- `loss_total = 0.582758`
- `decoded_to_target_rms_ratio = 0.953562`
- `audit_env_corr = 0.817808`
- `audit_env_mae = 0.037470`
- `audit_delta_corr = 0.202479`
- `audit_dynamic_std_ratio = 0.784445`
- `audit_delta_abs_ratio = 0.922910`
- `audit_peak_to_peak_ratio = 0.535859`
- `audit_silent_rms = 0.001772`

#### `step72`
- `loss_total = 0.564981`
- `decoded_to_target_rms_ratio = 0.891505`
- `audit_env_corr = 0.829826`
- `audit_env_mae = 0.036091`
- `audit_delta_corr = 0.219937`
- `audit_dynamic_std_ratio = 0.748449`
- `audit_delta_abs_ratio = 0.874959`
- `audit_peak_to_peak_ratio = 0.508709`
- `audit_silent_rms = 0.001612`

### 2. 对“`72` 更柔和”的判断
- 这条主观印象
  与量化结果
  是一致的
- 因为相比
  `step60`，
  `step72`
  的:
  - `audit_dynamic_std_ratio`
    更低
  - `audit_delta_abs_ratio`
    更低
  - `audit_peak_to_peak_ratio`
    也更低

这说明:
- `72`
  的确更像
  把整体起伏
  收了一点
- 所以
  “更柔和”
  不是纯心理作用

### 3. 对“是否比上一轮第三条更平”的判断
- 若拿旧
  `offline_mvp_nores_vocoder_audio_export_step48_validation_round1_1`
  的同批 6 条样本
  做 aggregate 对照，
  其
  `audit_proxy.wav`
  指标约为:
  - `audit_env_corr = 0.725575`
  - `audit_delta_corr = 0.067082`
  - `audit_dynamic_std_ratio = 0.605765`
  - `audit_delta_abs_ratio = 0.758115`
  - `audit_peak_to_peak_ratio = 0.402735`
  - `audit_silent_rms = 0.002152`

这说明:
- 如果按
  “整体 envelope 起伏”
  来看，
  当前
  `step60 / step72`
  其实都比旧
  `step48`
  更接近目标、
  也更有 target-aligned
  波动
- 所以当前没有证据支持:
  - “新 route
     比旧第三条
     更平到发死”

更准确的解释更像是:
- 旧第三条让人感觉
  “更有波动”，
  其中可能混着:
  - 噪声式起伏
  - 不稳定的局部能量抖动
- 新 route
  把这些
  非目标式抖动
  清掉了，
  于是主观上
  会显得更平、
  更柔和

### 4. 当前真正保留的不确定性
- 不能因为上述结果
  就认定:
  - 当前 smoothing
    一定完全无害
- 因为:
  - 现在量化的是
    `audit_proxy.wav`
  - 不是最终成品
  - 也不是更高层的
    语义/韵律可懂度

所以更准确的边界是:
- 当前没有证据支持
  “已被过度抹平成坏结果”
- 但仍值得在后续
  继续盯:
  - 多音节内部
    的 modulation preservation

## 当前判断

### 1. 本轮听审不足以改写默认点
- 原因:
  - `60` 和 `72`
    主观上基本打平
  - 量化上
    `72`
    仍保持:
    - 更低 loss
    - 更低静音泄漏
    - 更强目标对齐
  - 只是:
    - `72`
      比 `60`
      略柔和一点

### 2. 当前更合理的默认口径
- 继续保留:
  - `step72`
    作为当前
    best-validation
    主点
- 同时记录:
  - `step60`
    作为
    loudness-balanced
    对照点
- 不因本轮打平听审
  立即把默认点
  从 `72`
  切回 `60`

### 3. 下一棒更值得做什么
- 不再优先继续
  同一对
  `60 vs 72`
  上反复盲听
- 更值钱的是:
  - 为后续 selector
    增加 modulation /
    smoothing 监控口径
  - 或在更大样本上
    复核这种
    “柔和但不明显更差”
    是否仍成立

先说人话:
- 你听到的
  “72 更柔和一点”
  这件事，
  量化上是成立的。
- 但目前没有证据显示
  它已经柔和到
  把该有的起伏
  全部抹掉了；
  更像是
  把旧路线里
  那些不太受控的抖动
  压下去了。

## 一句话结论
- 当前人耳结果
  只支持:
  - `72`
    比 `60`
    略柔和
  - 但整体几乎不可分辨
- 当前量化结果则进一步说明:
  - 这种“柔和”
    更像
    起伏幅度略收，
    不是整体被抹平成平线
- 因此现在不应因这轮听审
  改写默认点；
  `step72`
  仍可保留为
  当前主点，
  而下一步更值钱的是
  把 modulation-preservation
  纳入后续治理口径。
