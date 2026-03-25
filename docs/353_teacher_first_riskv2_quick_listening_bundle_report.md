# 353. teacher-first riskv2 最小试听包报告

## 结论
- 当前 teacher-first
  用户线
  已经可以稳定导出
  可听 wav，
  所以这一步不是
  “还不能试听”。
- 但 buzz
  问题并没有被正式宣布解决。
- 本轮真正做的事是：
  - 把旧的误报型风险门
    改成更接近现实的
    reference-relative
    风险门
  - 再把当前两条 user-line
    候选整理成最小试听包，
    方便直接听

## 一、大白话解释
- 现在不是在“抠一个小参数”。
- 更像是在修：
  - 仪表盘
  而不是修：
  - 发动机
- 因为前一版的问题是：
  - 只要频谱高一点，
    风险门就一律报
    `high_risk`
  - 但当前 checkpoint
    的健康 reference
    自身频谱就不低，
    所以这个判法已经不准了
- 这轮修完后，
  我们至少能更准确地区分：
  - “还是明显坏”
  - “还没转正，
     但已经更接近参考分布”

## 二、试听包位置
- 目录：
  - `reports/audio/teacher_first_riskv2_quick_compare_20260325/`
- 说明：
  - `reports/audio/teacher_first_riskv2_quick_compare_20260325/README.md`

## 三、包内内容
- `source_input_parallel107.wav`
- `fixed_target_reference_firefly135.wav`
- `default_postenv_decoded.wav`
- `affine_refmean_gateoff_decoded.wav`

## 四、当前判断
- 现在可以明确说：
  1. 能试听
  2. 还不能说
     buzz
     已解决
  3. 当前最佳
     inference-only
     候选
     相比默认链路，
     更接近 reference
     decoder 行为
  4. 但它是否已经真正脱离
     buzz，
     还需要你最后一耳朵确认

## 五、下一步
1. 先听这个最小包
2. 如果听下来：
   - 两条都还是明显 buzz，
     我就停止继续扫
     inference-only
     小改动
3. 只有在你明确听到：
   - 某条已经开始出现
     人声轮廓
   的前提下，
   我才继续沿那条线推进
