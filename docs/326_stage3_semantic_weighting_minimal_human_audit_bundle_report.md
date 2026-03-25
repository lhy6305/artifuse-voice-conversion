# 326. Stage3 semantic weighting 最小人工听审包交付报告

## 结论
- 已基于
  `docs/325_stage3_semantic_weighting_short_loop_compare_and_proxy_audio_report.md`
  的现有导出结果，
  整理出一份最小人工听审包：
  - `reports/audio/stage3_semantic_weighting_quick_audit_20260325/`
- 本轮不再导大包，
  只保留两个最有代表性的 case：
  - `validation`
  - `special`
- 每个 case
  只保留：
  - `input`
  - `teacher_proxy`
  - `student_off`
  - `student_on`

## 一、为什么这一步现在最有价值
- 当前 `325`
  已经证明：
  - semantic weighting
    真的进入了损失
  - 在统一口径
    `semantic_disabled_reference`
    下，
    `on`
    相比
    `off`
    只有微弱正向信号
- 但当前还没有人工结论，
  无法判断：
  - 这点微弱收益
    是否对应可感知正向变化
  - 还是只是数值层面的轻微波动
- 因而当前最值得做的不是继续放大训练，
  而是先用极小听审成本，
  判断这条线
  是否值得继续追加时间

## 二、本轮整理出的最小听审目录
- 目录：
  - `reports/audio/stage3_semantic_weighting_quick_audit_20260325/`

### 文件列表
- `01_validation_input.wav`
- `02_validation_teacher_proxy.wav`
- `03_validation_student_off.wav`
- `04_validation_student_on.wav`
- `05_special_input.wav`
- `06_special_teacher_proxy.wav`
- `07_special_student_off.wav`
- `08_special_student_on.wav`
- `README.md`

## 三、听审问题固定

### 1. validation
- 只问：
  - `student_on`
    相比
    `student_off`
    是否更接近
    `teacher_proxy`
- 重点听：
  - 稳定性
  - 边界是否更顺
  - 是否出现新增毛刺或塌陷

### 2. special
- 只问：
  - `student_on`
    是否比
    `student_off`
    更坏
  - 若不更坏，
    是否略更稳
- 重点听：
  - nonverbal case
    是否被错误强化
  - 是否出现额外抖动、
    噪感、
    断裂

## 四、本轮刻意没做什么
- 没有重新导完整 bundle
- 没有引入 GUI
- 没有追加新的 Stage3 loop
- 没有把这次听审误写成：
  - semantic 路线已成立

## 五、下一步分叉条件
1. 如果人工听感显示：
   - `student_on`
     明显更坏
   - 或没有任何正向变化
   则：
   - 暂停继续放大 semantic weighting
2. 如果人工听感显示：
   - `student_on`
     至少不更坏，
     且略更接近
     `teacher_proxy`
   则下一步再做：
   - 更合理 subset
   - 或更大 batch
   的短程 loop 放大
   - 继续比较
     `semantic_disabled_reference`

## 一句话结论
- 当前已把
  `325`
  的现有结果收成一份
  可直接试听的最小包；
  下一步优先由人工判断：
  semantic weighting
  是否值得继续投入。
