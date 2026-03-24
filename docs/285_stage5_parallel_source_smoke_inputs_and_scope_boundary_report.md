# 2026-03-24 Stage5 平行 source smoke 输入与实验线边界固化报告

## 一、背景
- 本轮用户要求核对三件事，
  并在必要时写入文档，
  避免后续继续沿用旧假设：
  1. 部分 target
     样本存在较重混响，
     集中在
     `chapter3_5 / chapter3_6`
  2. target
     提取与噪音 / 背景音去除已由另一项目接管，
     本项目只需要考虑：
     - 清晰人声
     - 少量规律底噪
     - 极轻微混响
  3. 用户向 source
     数据集补入两条同内容平行语料，
     希望指定其作为
     end-to-end smoke test
     输入

## 二、核对结果

### 1. `chapter3_5 / chapter3_6` 较重混响事实
- 已核对为真，
  且仓内已有正式落盘资产，
  不是口头信息：
  - 主文档：
    `docs/01_project_overview_and_plan.md`
    已有
    `chapter3_5 / chapter3_6`
    全量混响标注章节
  - pitfalls：
    `294 / 295 / 296`
    已记录：
    - 不要把 validation-only
      混响误判成训练污染
    - 先做章节级 sidecar
    - 再派生 clean-only
      split
  - sidecar：
    `data_prep/round1_1/annotations/target_quality_annotations_chapter3_5_3_6_reverb.jsonl`
- 因此这条本轮不需要重新发明结论，
  只需要在后续继续沿用现有治理口径。

### 2. 本项目实验线边界
- 本轮将边界正式固定为：
  - 本项目不负责：
    - target 提取
    - 重去噪
    - 背景音大幅去除
    - 较重混响治理
  - 本项目默认输入假设是：
    - 清晰人声
    - 少量规律底噪
    - 极轻微混响
- 这样后续在
  `contract_v2`
  校准和重训前准备里，
  就不会再把问题扩回上游资产治理。

### 3. 两条新增平行 source 语料
- 已检查到以下文件：
  - `data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_107.wav`
  - `data_convert/dataset_firefly_parallel_ly65_recordings/chapter3_17_firefly_132.wav`
- 它们都存在且可读，
  音频信息如下：
  - `chapter3_17_firefly_107.wav`
    - `sample_rate = 44100`
    - `waveform_samples = 171162`
    - `duration_sec = 3.881224`
  - `chapter3_17_firefly_132.wav`
    - `sample_rate = 44100`
    - `waveform_samples = 155176`
    - `duration_sec = 3.518730`
- 对应 target
  也已在当前 train manifest
  中确认：
  - `target::chapter3_17_firefly_107`
    - 文本：
      `我可未必，还是开慢点吧。`
    - target 时长约：
      `2.628980s`
  - `target::chapter3_17_firefly_132`
    - 文本：
      `这就是此前发生的一切。`
    - target 时长约：
      `2.519977s`
- 因此它们满足：
  - 内容同名同句
  - 风格尽量一致
  - 时间轴 / 语速不对齐
- 这正是当前最适合的
  source-to-target smoke
  主输入类型。

## 三、本次代码调整

### 1. 默认主听 smoke 入口
- 已将以下脚本的默认
  main-listening
  输入切换为这两条平行 source：
  - `scripts/run_teacher_first_single_target_audible_smoke_bundle.ps1`
  - `scripts/run_teacher_first_single_target_audible_compare_bundle.ps1`
- 原先的高静音边界样例
  `segment_0061`
  继续保留在
  `boundary_probe`
  配置里。

### 2. 默认 review / self-check / audit 入口
- 已更新：
  - `scripts/run_teacher_first_single_target_vc_review_bundle.ps1`
  - `scripts/self_check_teacher_first_single_target_vc_demo.ps1`
  - `src/v5vc/teacher_first_vc_demo.py`
  - `src/v5vc/source_acoustic_state_audit.py`
- 当前默认口径是：
  - 主样例：
    `chapter3_17_firefly_107 / 132`
  - 边界补充：
    `segment_0061`

### 3. 顺手修复的 plumbing
- 在切默认 self-check
  时发现：
  `teacher_first_vc_demo`
  仍按旧签名调用
  `build_contract_payload(...)`
  和
  `build_tensor_payload(...)`
- 本轮已补齐
  `waveform`
  传参，
  使
  `contract_v2`
  路径能够真正走到
  contract / scaffold
  输出阶段。

## 四、验证结果

### 1. 代码可编译
- 已执行：
```powershell
.\python.exe -m compileall src/v5vc/teacher_first_vc_demo.py src/v5vc/source_acoustic_state_audit.py
```
- 通过。

### 2. 默认 audit 已切到平行 source
- 已执行：
```powershell
.\python.exe manage.py audit-source-acoustic-state --output-dir tmp/source_acoustic_state_audit_parallel_defaults
```
- 结果中默认样例已变为：
  - `chapter3_17_firefly_107.wav`
  - `chapter3_17_firefly_132.wav`
  - `segment_0061_0000300400_0000300910.wav`
- 关键统计：
  - `107`
    `voiced_ratio = 0.466292`
    `f0_p90 = 371.530396`
  - `132`
    `voiced_ratio = 0.434917`
    `f0_p90 = 376.923096`
  - `segment_0061`
    `voiced_ratio = 0.298013`
    `f0_p90 = 205.656448`
- 当前这三条默认样例都没有触发 warning。

### 3. 默认 self-check 当前仍不应被误报为“输入失效”
- 已执行：
```powershell
.\scripts\self_check_teacher_first_single_target_vc_demo.ps1 `
  -OutputDir tmp/teacher_first_vc_demo_self_check_parallel107 `
  -MaxAudioSec 0.1
```
- 结果表明：
  - 上游已能走到：
    - `teacher_runtime_streaming`
    - `teacher_contract_write`
    - `teacher_vocoder_input_scaffold`
  - success baseline
    当前失败在：
    `vocoder_checkpoint_load`
  - 具体原因是：
    当前推荐 no-res checkpoint
    仍对应旧 scaffold
    维度，
    与新的
    `contract_v2 / scaffold_v2`
    不兼容
- 因此当前应该得出的结论不是：
  - “新的平行 source
    不能做 smoke”
- 而是：
  - “默认 smoke 输入已切换成功，
     但 decoded success path
     仍被
     v2-compatible checkpoint
     缺失所阻塞”

## 五、当前结论
- 三项用户提醒里，
  第 1 条已是既有正式事实；
  第 2 条与第 3 条本轮已补成正式边界和默认入口。
- 从现在开始，
  实验线应默认按以下口径推进：
  1. `chapter3_5 / chapter3_6`
     重混响事实继续沿用现有
     sidecar / split
     治理
  2. 本项目不接去噪 /
     重去混响，
     只做清晰人声假设下的
     `contract_v2`
     和重训前准备
  3. 默认 end-to-end smoke
     主输入优先使用：
     - `chapter3_17_firefly_107`
     - `chapter3_17_firefly_132`
  4. 旧的高静音边界样例
     留在
     boundary probe，
     不再充当默认主听入口

## 六、下一步
1. 继续以
   `107 / 132`
   为主样例扩
   source acoustic state
   校准。
2. 等
   `v2-compatible`
   no-res checkpoint
   产出后，
   重新跑默认
   audible smoke
   success path。
