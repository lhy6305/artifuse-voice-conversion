# 357. Stage3 `teacher_e_evt_v1` vs `legacy_event_probs` 严格可比 12-step 短 loop 对照报告

## 结论
- 本轮已完成：
  - `teacher_e_evt_v1`
    vs
    `legacy_event_probs`
    的第一轮严格可比
    12-step short loop
- 结果明确：
  - `teacher_e_evt_v1`
    优于
    `legacy_event_probs`
- 因而当前 Stage3 event 主监督默认口径应继续保持：
  - `event_target_family = teacher_e_evt_v1`
- `legacy_event_probs`
  现在应降级为：
  - 兼容对照口径
  - 不再是默认主线

## 一、对照设计

### 1. 本轮只切一根开关
- 新增：
  - `semantic_supervision.event_target_family`
- 可选值：
  - `teacher_e_evt_v1`
  - `legacy_event_probs`

### 2. 为保证严格可比，本轮刻意不切的部分
- `teacher_label_index`
  保持一致：
  - `data_prep/round1_1/streaming_student_teacher_labels_eevt_round1_1/teacher_label_index.jsonl`
- config 主模板保持一致：
  - `configs/streaming_student_stage_template.json`
- batch / model / optimizer / learning rate / validation 采样口径
  全部保持一致
- 更关键的是：
  - `vuv_proxy`
  - `aper_proxy`
  继续固定读取：
  - `teacher_e_evt`
- 也就是说：
  - 这次 A/B
    只比较
    `teacher_event`
    与
    `teacher_event_prior`
    的 event 主监督 target family
  - 不把 proxy target family
    一起换掉

## 二、代码改动
- 更新：
  - `src/v5vc/streaming_student/losses.py`
  - `src/v5vc/streaming_student/training_loop_entry.py`
  - `configs/streaming_student_stage_template.json`
- 新增：
  - `configs/streaming_student_loss_weights_legacy_event_target_v1.json`

### 当前行为
- 默认：
  - `event_target_family = teacher_e_evt_v1`
- 兼容 override：
  - `configs/streaming_student_loss_weights_legacy_event_target_v1.json`
- validation summary
  现在会显式记录：
  - `teacher_event_target_family`
  - `teacher_event_contract_version`
  - `teacher_event_label_space_version`
  - `teacher_event_proxy_target_family`

## 三、实验产物

### 1. `teacher_e_evt_v1` 默认组
- 产物：
  - `reports/training/streaming_student_loop_eevt12_ab_default_round1_2/`
- 摘要：
  - `reports/training/streaming_student_loop_eevt12_ab_default_round1_2/logs/streaming_student_loop_eevt12_ab_default_round1_2.summary.json`

### 2. `legacy_event_probs` 对照组
- 产物：
  - `reports/training/streaming_student_loop_legacyevent12_round1_1/`
- 摘要：
  - `reports/training/streaming_student_loop_legacyevent12_round1_1/logs/streaming_student_loop_legacyevent12_round1_1.summary.json`

### 3. 无效失败产物说明
- 较早一次默认组运行：
  - `streaming_student_loop_eevt12_ab_default_round1_1`
- 在 step6 validation
  因旧聚合器把字符串 metric
  强制转 float
  而中止
- 该目录不能作为正式对照结论
- 本轮正式结论应以：
  - `round1_2`
  为准

## 四、关键结果

### 1. validation step12
- `loss_total`
  - `teacher_e_evt_v1: 8.609584`
  - `legacy_event_probs: 9.866241`
  - 差值：
    - `-1.256657`
- `loss_total_semantic_disabled_reference`
  - `teacher_e_evt_v1: 7.276324`
  - `legacy_event_probs: 8.302927`
  - 差值：
    - `-1.026603`
- `loss_teacher_event`
  - `teacher_e_evt_v1: 4.547270`
  - `legacy_event_probs: 5.525825`
  - 差值：
    - `-0.978555`
- `loss_teacher_event_prior`
  - `teacher_e_evt_v1: 5.767968`
  - `legacy_event_probs: 6.707024`
  - 差值：
    - `-0.939056`

### 2. 代理路径也未出现反向证据
- `loss_teacher_vuv_proxy`
  - `teacher_e_evt_v1: 0.716889`
  - `legacy_event_probs: 0.724479`
- `loss_teacher_aper_proxy`
  - `teacher_e_evt_v1: 0.004694`
  - `legacy_event_probs: 0.077557`

### 3. train step12
- `loss_total`
  - `teacher_e_evt_v1: 8.215662`
  - `legacy_event_probs: 9.656329`

## 五、当前判断
1. 这次已经不是：
   - plumbing 是否接通
   的问题
2. `teacher_e_evt_v1`
   在保持其余口径不变时，
   相比
   `legacy_event_probs`
   给出了明确更好的短程优化行为
3. 所以当前最合理的写法是：
   - Stage3 event 主监督
     已有第一版因果证据支持
     从 legacy
     升级到
     `teacher_e_evt_v1`
4. 但仍要保持边界：
   - 这证明的是：
     - bootstrap
       `teacher_e_evt_v1`
       优于 legacy
   - 不是证明：
     - 最终完整 design-state
       `e_evt`
       已经完成

## 六、下一步
1. 保持：
   - `teacher_e_evt_v1`
     为 Stage3 默认主线
2. 不再继续为
   `legacy_event_probs`
   做额外扫参
3. 下一条更值钱的推进应改为：
   - 把当前已站稳的
     `teacher_e_evt_v1`
     继续用于
     Stage3 -> Stage5
     下游 contract
     设计与验证
