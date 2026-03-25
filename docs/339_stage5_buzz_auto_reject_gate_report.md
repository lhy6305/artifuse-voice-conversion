# 339. Stage5 obvious-buzz 自动否定门禁接入报告

## 结论
- 可以。
- 我已经把一个保守的
  `Stage5`
  obvious-buzz
  自动否定门禁接到了
  `export-offline-mvp-nores-vocoder-audio`
  产物里。
- 这套门禁的边界非常明确：
  - 只用于
    **自动否定明显失败样本**
  - 不用于
    **自动证明样本已经可听**
- 当前用它回放你刚刚确认过的
  paired overfit24
  baseline / semantic
  两份 export，
  结果都是：
  - `all_records_auto_reject = true`
  - 因而这类明显 pure buzz / pure fuzz
    结果，后续可以先由机器挡掉，
    不再默认再麻烦你听一次

## 一、这次新增了什么
- 文件：
  - `src/v5vc/nores_vocoder_audio_export.py`
- 新增内容：
  - 每条 export record
    现在都会写出：
    - `buzz_reject_assessment`
  - bundle summary
    现在会写出：
    - `buzz_reject_summary`

## 二、判定逻辑为什么是“保守否定”
- 这次没有再回到旧的
  `teacher_first_runtime_risk_v1`
  固定高频阈值，
  因为那套阈值已经在历史上被证明：
  - 不能直接等同于
    “当前仍然一定是 buzz”
- 当前新门禁采用的是：
  1. target-relative
     的短时模板塌缩信号
  2. target-relative
     的极端频谱亮度偏离信号
- 更准确地说，
  它要抓的是：
  - `template-buzz`
  - 或极端
    harsh-buzz / fuzz
    明显越界
- 它不尝试回答：
  - “是不是已经像人声”

## 三、当前自动否定器抓的是什么

### 1. 模板塌缩信号
- 关注：
  - `decoded_frame_template_cosine_mean`
  - `decoded_frame_adjacent_cosine_mean`
  - `decoded_frame_template_cosine_gap_vs_aligned`
- 含义：
  - 如果 decoded
    的短时帧几乎都贴着同一模板，
    且相对 aligned target
    的结构多样性差距极大，
    这是已知
    `template-buzz`
    失败形态

### 2. 极端亮度越界信号
- 关注：
  - `decoded_spectral_summary.high_band_energy_ratio`
  - `spectral_high_band_energy_ratio_gap`
  - `spectral_centroid_gap_hz`
- 含义：
  - 如果 decoded
    的高频占比和频谱中心
    相对 target
    极度漂移，
    就把它视为明显失败，
    先自动否掉

## 四、当前回放验证结果

### baseline export
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit24_semanticplumb_baseline_validation_trainingsync_round1_1/`
- 结果：
  - `buzz_reject_summary.all_records_auto_reject = true`

### semantic export
- 目录：
  - `reports/runtime/offline_mvp_nores_vocoder_audio_export_paired_parallel_overfit24_semanticweight_validation_trainingsync_round1_1/`
- 结果：
  - `buzz_reject_summary.all_records_auto_reject = true`

### case 级证据
- `case107`
  semantic：
  - `decoded_frame_template_cosine_mean = 0.997549`
  - `decoded_frame_adjacent_cosine_mean = 0.998774`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.973717`
  - `decoded_high_band_ratio = 0.622708`
  - `aligned_high_band_ratio = 0.060494`
  - `centroid_gap_hz = 10733.209308`
- `case132`
  semantic：
  - `decoded_frame_template_cosine_mean = 0.997508`
  - `decoded_frame_adjacent_cosine_mean = 0.998758`
  - `decoded_frame_template_cosine_gap_vs_aligned = 0.958198`
  - `decoded_high_band_ratio = 0.620739`
  - `aligned_high_band_ratio = 0.143502`
  - `centroid_gap_hz = 10009.701948`

## 五、这对后续流程的意义
- 以后面对这类
  Stage5 quick-audit /
  training-sync export，
  可以先看：
  - `buzz_reject_summary`
- 如果出现：
  - `all_records_auto_reject = true`
- 那我就直接把它写成：
  - obvious-buzz
    自动否定
  - 不再默认拉你来听

## 六、边界
- 这套门禁只能做：
  - negative gate
- 它不能做：
  - positive promotion
- 也就是说：
  - `auto_reject_obvious_buzz`
    可以直接判失败
  - `review_required`
    仍然只表示：
    - 机器不敢判死
    - 不是“机器认定已经成功”

## 七、下一步
1. 后续 quick-audit
   默认先跑这套门禁
2. 只有当：
   - `review_required`
   且量化也没有明显负向信号
   时，
   才值得把样本交给你做人工听审
3. 当前 semantic
   这条线已经可直接按：
   - obvious-buzz
     自动否定
   收口，
   不需要你再为同类失败样本重复听审
