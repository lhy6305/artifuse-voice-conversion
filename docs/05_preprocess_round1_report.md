# round1 预处理结果报告

## 报告范围
本报告对应以下实际产物：

- `data_prep/round1/firefly_mainstream/`
- `data_prep/round1/source_segments/`
- `reports/data/preprocess_round1/`

## 一、目标说话人数据结果
### 1. round1 纳入情况
- 原始总样本数：671
- round1 训练样本数：624
- round1 排除样本数：47
- round1 总时长：3826.050 秒

### 2. 当前纳入规则
- 只纳入：
  - 44100 Hz
  - 单声道
  - 文本清洗后非空
- 当前不纳入：
  - 非 44100 Hz
  - 非单声道

### 3. 文本清洗结果
- 已按当前决策保留主要标点：
  - `，。？！；：、`
- 已对特殊符号做删除或归一化。
- 已修正重复标点问题，例如：
  - `一……` 清洗后变为 `一，`
  - `（这……）` 清洗后变为 `这，`

### 4. 当前观察
- 当前排除样本数量 47，与扫描阶段发现的非主流格式样本规模基本一致。
- 清洗文本不会覆盖原始 `.lab`，而是单独输出到：
  - `data_prep/round1/firefly_mainstream/labels/`

## 二、源说话人数据结果
### 1. round1 切分结果
- 首轮检测出的候选内容段：827 段
- 人工排除区间处理后：823 段
- 边界静区规则过滤后最终保留：537 段
- 最终内容段总时长：655.350 秒
- 单段时长统计：
  - 最短 0.510 秒
  - 最长 3.510 秒
  - 平均 1.220 秒
  - 中位数 1.050 秒

### 2. 底噪判断
- 估计底噪：-74.184 dBFS
- 当前规则下未判定为“稳定底噪存在”
- 因此本轮没有启用额外噪声门静音替换

### 3. 当前切分阈值
- 分析窗长：30 ms
- 内容判定阈值：-38.0 dBFS
- 边界静区阈值：-38.0 dBFS
- 边界静区最小时长：500 ms
- 每段前保留静音：200 ms
- 每段后保留静音：250 ms
- 最大内部静音间隙合并：300 ms

### 4. 峰值试听片段
- 当前导出试听片段：11 条
- 存放位置：
  - `data_prep/round1/source_segments/peaks/`
- 当前来源：
  - `top_peak` 1 条
  - `abrupt_rise` 10 条
- 已按人工复核结论移除：
  - `peak_005_0001221975_top_peak.wav`
  - `peak_008_0001665045_abrupt_rise.wav`
  - `peak_014_0003049665_top_peak.wav`
  - `peak_015_0003614595_abrupt_rise.wav`

## 三、当前参数效果评估
### 1. 当前看起来合理的点
- 峰值片段数量已经压到可人工试听范围。
- 源录音在加入边界静区规则后，仍保留了 537 条可用片段。
- 目标文本清洗结果与原始标签分离，具备可回滚性。

### 2. 当前仍需人工复核的点
- `source_segments/segments/` 的边界静区过滤是否过严。
- `peak_010_0002051985_abrupt_rise` 对应区间在当前规则下没有留下训练片段，是否接受这一结果。
- 目标文本中部分句首逗号是否需要保留。

## 四、建议的人工复核顺序
1. 先试听 `data_prep/round1/source_segments/peaks/` 下 11 条片段。
2. 再随机抽查若干 `data_prep/round1/source_segments/segments/` 片段头尾。
3. 最后查看 `data_prep/round1/firefly_mainstream/manifest_round1_excluded.jsonl` 中被隔离的 47 条样本。

## 五、下一步
1. 根据当前 round1 结果决定是否放宽边界静区规则。
2. 若当前 537 条源片段可接受，则进入训练输入 manifest 标准化和评估基线实现。
3. 若当前边界过滤过严，则优先继续调 `source_audio` 预处理配置，不提前进入训练阶段。

## 六、当前状态更新
- 用户已确认当前严格过滤策略可接受。
- 基于该结论，已继续生成：
  - `data_prep/round1/manifests/target_train.jsonl`
  - `data_prep/round1/manifests/source_train.jsonl`
  - `data_prep/round1/manifests/combined_round1.jsonl`
- manifest 摘要位于：
  - `reports/data/round1_manifests/manifest_summary.md`
