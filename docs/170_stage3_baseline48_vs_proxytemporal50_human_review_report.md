# 170. Stage3 baseline48 vs `proxytemporal50` 人工复听对照报告

## 背景
- `docs/168_stage3_proxy_stability_probe_and_temporal_supervision_report.md`
  已经把当前问题收敛到:
  - `proxytemporal50`
    是否能比 baseline48
    更稳、更少毛刺
- 为避免只做
  “单次 teacher vs student”
  的纵向比较，
  本轮专门建立了:
  - baseline48
  - `proxytemporal50`
    的并排复听会话

## 听审会话
- 会话目录:
  - `reports/audio/audio_audit_gui_stage3_baseline48_vs_proxytemporal50_session/`
- bundle:
  - `reports/audio/streaming_student_proxy_audit_baseline48_step48_v1/`
  - `reports/audio/streaming_student_proxy_audit_baseline48_step48_special_v1/`
  - `reports/audio/streaming_student_proxy_audit_proxytemporal50_step12_v1/`
  - `reports/audio/streaming_student_proxy_audit_proxytemporal50_step12_special_v1/`
- 总记录数:
  - `6`
- 已完成数:
  - `6`

## 本轮人工比较口径

### 1. 两个 teacher 只作为锚点，不作为主要胜负对象
- 用户明确反馈:
  - 两次实验里的 `teacher_proxy`
    全程听下来
    无明显差别
- 因此本轮真正的主问题
  不是:
  - 某次 `teacher vs student`
    是否更接近
- 而是:
  - baseline48 的 `student_proxy`
    与
    `proxytemporal50` 的 `student_proxy`
    谁更好

### 2. 未填写的维度按平手解释
- 本轮延续已有人工约定:
  - 未选择的字段
    不是漏评，
    而是:
    - 平手
    - 无明显差异

## 汇总结果

### 可比较性
- `6 / 6`
  记录都被标记为:
  - 可比较

### 节奏
- baseline48 `student_proxy`
  获得:
  - `3`
    条明确胜出
- `proxytemporal50`
  获得:
  - `0`
    条
- 其余:
  - `3`
    条平手

### 边界
- baseline48 `student_proxy`
  获得:
  - `3`
    条明确胜出
- `proxytemporal50`
  获得:
  - `0`
    条
- 其余:
  - `3`
    条平手

### 稳定性
- baseline48 `student_proxy`
  获得:
  - `2`
    条明确胜出
- `proxytemporal50` `student_proxy`
  获得:
  - `3`
    条明确胜出
- 其余:
  - `1`
    条平手

### 综合首选
- baseline48 `student_proxy`
  获得:
  - `3`
    条明确胜出
- `proxytemporal50` `student_proxy`
  获得:
  - `2`
    条明确胜出
- 其余:
  - `1`
    条平手

## 单条关键信息

### validation 三条
- `target::chapter3_3_firefly_138`
  - 节奏:
    baseline48 胜
  - 边界:
    baseline48 胜
  - 稳定性:
    `proxytemporal50` 胜
  - 综合:
    baseline48 胜
  - 备注:
    - `proxytmp50`
      的 `student`
      出现边界模糊

- `target::chapter3_3_firefly_162`
  - baseline48
    在:
    - 节奏
    - 边界
    - 稳定性
    - 综合
      全部胜出

- `target::chapter3_4_firefly_106`
  - baseline48
    在:
    - 节奏
    - 边界
    - 稳定性
    - 综合
      全部胜出

### special 三条
- `target::no_text_voice/chapter3_17_firefly_106`
  - 所有维度平手
  - 备注:
    - 不是漏评，
      而是几乎无差别

- `target::no_text_voice/chapter3_29_firefly_139`
  - `proxytemporal50`
    在:
    - 稳定性
    - 综合
      胜出

- `target::no_text_voice/chapter3_3_firefly_110`
  - `proxytemporal50`
    在:
    - 稳定性
    - 综合
      胜出

## 当前结论

### 1. `proxytemporal50` 不是无效尝试
- 它并没有被人耳判成
  全面更差
- 在 special 两条里，
  它确实表现出:
  - 更稳
  - 综合更优
    的优势

### 2. 但它也没有形成足够强的整体替代证据
- validation 三条里，
  baseline48
  在:
  - 节奏
  - 边界
  - 综合
    上明显更占优
- 其中至少有一条
  还出现了:
  - `proxytemporal50`
    边界模糊

### 3. 因此当前不应直接把 `proxytemporal50` 升级为新默认
- 更准确的解释是:
  - temporal supervision
    确实可能改善
    一部分稳定性问题
  - 但当前这版权重与短程训练结果
    仍带来了:
    - 边界代价
    - validation 侧综合退化风险

## 当前最合理的下一步
1. 维持:
   - baseline48
     作为当前默认 Stage3 checkpoint
2. 把 `proxytemporal50`
   视为:
   - “special 稳定性方向有信号，
      但不能直接替代默认基线”
     的候选
3. 若继续沿 temporal supervision
   推进，
   下一步不该直接拉长 horizon，
   而应优先尝试:
   - 降低权重
   - 调整 schedule
   - 或只把 temporal 约束
     叠到更局部的稳定性目标上
4. 若短期目标是稳妥推进主线，
   当前仍优先保留:
   - baseline48

## 一句话结论
- 本轮人工复听表明:
  `proxytemporal50`
  在部分 special 样本上
  确实更稳，
  但整体上仍不足以替代 baseline48；
  当前最合理的口径
  是保留 baseline48 为默认，
  并把 temporal supervision
  继续当作“有方向但未收口”的局部候选。
