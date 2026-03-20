# 228. Stage5 low-activity `validation12` 人工听审摘要报告

## 背景
- `docs/221_stage5_low_activity_validation12_decoded_audit_contract.md`
  已固定
  `validation12`
  decoded
  low-activity
  听审入口
- `docs/225_stage5_low_activity_governance_fixed_report_materializer_report.md`
  已固定
  双轴治理
  report
- `docs/227_stage5_low_activity_audit_result_fixed_report_bootstrap_report.md`
  已补齐:
  - 听审完成后
    fixed audit result report
    的物化入口
- 但本轮实际操作里，
  用户没有导出
  `audio_audit_review.json`，
  因为主观结论已经高度一致

## 当前输入来源
- 用户直接提供的人工听审结论
- 当前 session:
  - `reports/audio/audio_audit_gui_stage5_low_activity_validation12_decoded_session/audio_audit_progress.json`
- 当前仍缺:
  - `reports/audio/audio_audit_gui_stage5_low_activity_validation12_decoded_session/audio_audit_review.json`

## 本轮人工听审结论

### 1. 底噪强度从 `36 -> 48 -> 60 -> 72` 单调递减
- 用户明确反馈:
  - `36`
    底噪最重，
    且已接近
    不可接受
  - `48`
    次之
  - `60`
    继续减轻
  - `72`
    最好，
    但仍有
    轻微可辨识底噪
- 当前解释:
  - 人耳侧
    明确支持
    leakage-strength
    方向
    继续偏向:
    - `72`

### 2. `60` 与 `72` 在某些代表性问题节点上都会出现明显毛刺跳变
- 用户指出的代表性问题节点包括:
  - 清辅音渐变消失
  - 呼吸声
- 当前听感是:
  - `60`
    与
    `72`
    在这些位置上，
    都会出现
    相似程度的
    剧烈毛刺跳变
- 当前解释:
  - 这意味着
    `60`
    并没有在
    这些关键问题点上
    明显优于
    `72`

### 3. `36` 与 `48` 在对应毛刺节点上更正常
- 用户明确反馈:
  - 在上述代表性问题节点，
    `36`
    与
    `48`
    的对应位置
    更正常
- 但这条优势
  没有抵消
  它们更重的
  底噪问题
- 当前解释:
  - `36/48`
    更像:
    - 某些局部问题点
      更稳
  - 但整体底噪
    仍然太重，
    尤其
    `36`
    已接近
    不可接受

### 4. 当前四者都不适合作为成品
- 用户直接判断:
  - 当前
    `36 / 48 / 60 / 72`
    都不太适合作为成品
- 因此当前结论
  不应写成:
  - 已找到
    可直接升格的
    成品 checkpoint

### 5. 若必须硬选一个，当前主观最优仍是 `72`
- 用户明确给出:
  - 如果必须硬选，
    当前最合适的是:
    - `72`
- 当前解释:
  - 这说明在人耳侧，
    当前更难接受的主问题
    仍然偏向:
    - 持续底噪 / 窄带刺耳
  - 而不是把
    局部毛刺
    单独放大到
    足以把
    `72`
    从候选里踢掉

### 6. 从 `36 -> 72`，频带越来越宽，主观上也越来越不刺耳
- 用户额外观察到:
  - 从
    `36`
    到
    `72`
  - 音频频带
    越来越宽
  - 听起来
    也越来越不刺耳
- 当前解释:
  - 这条信息
    不是
    low-activity
    现有四项核心指标
    的直接表达
  - 但它提示:
    - 后续若还要继续补
      定量 sidecar，
      可以考虑
      频带宽度 /
      高频展开 /
      刺耳感相关的
      频谱指标

## 当前对治理口径的影响

### 1. leakage-strength 轴得到更强的人耳支持
- 当前主观结论
  与量化侧
  `waveform_rms`
  一致:
  - `72`
    仍是
    当前底噪 / 残留最弱
    的方向

### 2. fragmentation 轴需要重新克制表达
- 当前不能再简单写成:
  - `60`
    在关键毛刺问题上
    明显优于
    `72`
- 因为用户反馈是:
  - `60`
    与
    `72`
    在某些代表性问题节点上
    毛刺程度接近
- 也就是说，
  `60`
  的局部安全优势
  当前更像:
  - 不稳定
  - 非全局
  - 且不足以压过
    底噪代价

### 3. 当前 forced-choice 人耳结果支持继续把 `72` 作为最合适的临时锚点
- 注意:
  - 这里是
    “四者都不理想时，
    硬选一个”
    的临时锚点
- 不是:
  - 可直接作为成品
    的最终默认

## 当前工程边界

### 1. 本轮还不能物化 fixed audit result report
- 原因不是
  没有听审
- 而是当前缺:
  - `audio_audit_review.json`
- 因此本轮只能写成:
  - 人工听审摘要报告
- 不能写成:
  - fixed-format
    audit result report

### 2. 本轮仍建议后续补一次结构化导出
- 当前结论虽然已经一致，
  但若后续要长期保留:
  - field aggregate
  - comparable / noncomparable
  - cross-axis readout
  的正式产物，
  仍建议把
  review
  结果
  再导出一次

## 当前最合理的下一步
1. 当前若只看
   forced choice
   与整体可接受度，
   继续把
   `72`
   视为
   最合适的临时锚点
2. 后续若继续优化，
   当前最值得补的方向不是
   进一步帮
   `36/48`
   洗白，
   而是:
   - 尝试压掉
     `72`
     在
     清辅音渐变 / 呼吸声
     上的剧烈毛刺
   - 同时保持
     `72`
     现有的
     低底噪
     与更宽频带
3. 后续指标层
   可以考虑补:
   - 与频带宽度
     或刺耳感相关的
     频谱 sidecar

## 一句话结论
- 当前
  `validation12`
  人工听审
  已把主观结论收敛成:
  - `36 -> 72`
    底噪单调递减，
    `72`
    最好但仍有轻微底噪
  - `60`
    与
    `72`
    在某些关键问题节点上
    都会出现明显毛刺
  - `36/48`
    局部更稳，
    但整体底噪代价更重
  - 四者都不适合作为成品，
    若必须硬选，
    当前仍是
    `72`
    最合适。
