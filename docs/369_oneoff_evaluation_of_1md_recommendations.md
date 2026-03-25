# 369. `1.md` 一次性评估与采纳边界

## 结论
- `1.md`
  的大方向应采纳，
  但不能整篇按字面原封不动照抄。
- 当前更准确的判断是：
  - 约 `80%`
    可采纳
  - 核心原则是对的：
    - 上游
      Stage3 / teacher-label / target-state
      仍在产出真实正向信息
    - 当前旧
      Stage5 no-res downstream
      不应再作为默认承接层重复回灌
  - 但有两处必须修正：
    1. 不能把
       “Stage5 还在吃旧 heuristic event family”
       写得过于绝对
    2. 不能把
       “停止旧 Stage5 route”
       误写成
       “停止一切 Stage5 验证”

## 一、评估对象
- 评估文件：
  - `F:/proj_dev/tmp/workdir4/1.md`
- 本次操作约束：
  - 仅作评估
  - 全部文件只读
  - 不修改
    `1.md`

## 二、应采纳的部分

### 1. 上游仍有真实进展
- 这一点与
  `368`
  一致：
  - `teacher_e_evt`
    generation-side
    `acoustic_directional_transition_bridge_v1`
    在：
    - full-validation step12
    - full-validation step24
    都优于上一版
      `acoustic_contextual_event_bridge_v1`
- 所以：
  - “上游 teacher-label 资产线
     仍在产出有效信息”
    这个总判断成立

### 2. 当前旧 Stage5 no-res downstream 不应继续默认回灌
- 这一点与：
  - `359`
  - `361`
  - `366`
  的正式结论一致
- 也就是：
  - 当前旧
    Stage5 no-res downstream
    已被多轮证明
    不是承接突破的有效层
- 所以：
  - 停止把每个新的上游 candidate
    机械送回同一条旧失败路线
    是合理的

### 3. 停止同层小修，改成“上游线 / 承接层识别”拆线推进
- 这部分建议应采纳：
  - 不再继续：
    - decode-side 小修
    - 同层 objective 微扫
    - current semantic/timing consumer
      小 patch
- 更合理的任务拆法是：
  - 线 A：
    继续把
    teacher-label / target-state
    做强
  - 线 B：
    重新识别
    哪个 downstream handoff layer
    真正能承接这些上游正向

## 三、必须修正后再采纳的部分

### 1. “Stage5 还长期消费旧 heuristic event family”不够准确
- 这句话的方向能理解，
  但按当前仓库真实状态，
  写法过头了
- 更准确的说法应是：
  - Stage5
    已经接通过多条显式
    `e_evt`
    路线
  - 包括：
    - consumer-side
    - supervision-side
    - downstream contract
  - 但这些承接方式
    仍然无法把上游改进
    转成可听的人声结构
- 所以当前问题
  不只是：
  - “还在吃旧字段”
- 更关键的是：
  - “当前承接方式不对”

### 2. “停止把新的上游改动扔回 Stage5 验证”不能写成绝对规则
- 如果按字面理解成：
  - 以后所有新的上游 candidate
    都不做任何 Stage5 验证
- 那就过头了
- 更准确的规则应是：
  - 不再把新上游 candidate
    机械送回
    当前这条已判死的
    旧 Stage5 no-res downstream route
  - 但如果未来定义了：
    - 真正不同的 handoff layer
    - 新的 contract family
    - 新的承接机制
  - 仍然应该做最小 fail-fast 验证

## 四、不应按字面直接采纳的部分

### 1. “立即回到 `C-prime / v2-core`”可以保留方向，但不能过早锁死实施顺序
- 方向上它是合理的
- 但当前更稳妥的执行顺序应是：
  1. 先形成
     `downstream handoff candidates`
     清单
  2. 每个候选写清：
     - 理论承接机制
     - 最小验证实验
     - stop rule
  3. 再决定
     哪条线真正进入实施

## 五、最终采纳口径
- 本次对
  `1.md`
  的正式采纳方式应是：
  - 采纳其核心原则
  - 不按原文整段照搬
- 当前应固定下来的口径是：
  1. `acoustic_directional_transition_bridge_v1`
     是新的
     Stage3 generation-side reference
  2. 当前旧
     Stage5 no-res downstream
     正式停止作为默认承接层
  3. 下一步先做：
     - 新的 downstream handoff candidates
       识别与排序
  4. 不再继续：
     - 当前旧 Stage5 route
       的重复回灌
     - 同层 decode / consumer / loss
       小修

## 六、落地建议
1. 可以采纳
   `1.md`
   的总方向，
   作为一次性评估结论
2. 但团队文档应使用
   本报告修正后的表述，
   不应直接复制
   `1.md`
   原文
