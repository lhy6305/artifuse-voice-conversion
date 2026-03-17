# 方案 `B` 启动报告

## 目的
- 记录用户确认转向方案 `B` 之后，当前工作区已经补齐了哪些监督底账。
- 说明在完全离线、且不新增外部依赖的前提下，方案 `B` 现在能先落哪一部分。

先说人话：
- 方案 `B` 现在已经不是一句口号了。
- 我已经把“哪些样本有文本监督、哪些只有音频启发式监督、哪些根本不能当正常语音监督”做成了正式 sidecar。
- 这让后续的标签升级不用再靠临时脚本或聊天记忆。

## 已完成产物
### 1. 代码入口
- `src/v5vc/b1_supervision_inventory.py`
- `manage.py build-b1-supervision-inventory`

### 2. 数据 sidecar
- `data_prep/round1/b1_supervision/target_supervision_inventory.jsonl`
- `data_prep/round1/b1_supervision/source_supervision_inventory.jsonl`

### 3. 报告
- `reports/data/b1_supervision_inventory/b1_supervision_inventory.md`
- `reports/data/b1_supervision_inventory/b1_supervision_inventory.json`

## 当前已确认事实
### 1. 目标侧
- `624` 条目标记录已经全部进入 supervision inventory。
- 其中：
  - `554` 条 `target_train`
  - `62` 条 `target_validation`
  - `8` 条 `target_special_eval`
- 目标侧全部有清洗后文本。
- 目标侧全部有标点停顿线索。
- 平均每条记录约 `21.762821` 个 lexical 字符。
- 平均音频时长约 `6.13149s`。

### 2. `target_special_eval`
- `8` 条全部被 inventory 识别为 `nonverbal_only`。
- 这和之前的人耳复核结论一致。

### 3. 源侧
- `537` 条源记录已经全部进入 supervision inventory。
- 源侧文本仍然是 `0` 覆盖。
- 也就是说：
  - 方案 `B` 现在能立即离线升级的是目标侧文本监督。
  - 源侧暂时仍然只能靠音频启发式监督，除非以后补转写或接入外部流程。

## 当前最现实的 `B` 子路线
### `B1-offline-minimal`
- 不引入外部依赖。
- 先利用现成的目标侧文本和标点停顿线索。
- 把新的监督分支限定在：
  - punctuation / pause boundary hints
  - utterance-level lexical text auxiliaries
  - future label slots 预留

大白话讲：
- 这条路像是“先把目标侧文本这位老师用起来”。
- 不求一步到位做 phone/manner 全套，但至少不再只靠能量门限瞎猜事件。

### `B2-richer-label-pipeline`
- 为未来 phone / manner / place / alignment 做更完整的标签流水线。
- 但当前本地环境没有：
  - G2P 工具
  - 强制对齐工具
  - 源侧转写
- 所以这条路现在只能先做接口和字段预留，暂时不能在完全离线下直接完成。

大白话讲：
- 这条路更强，但现在材料不齐。
- 可以准备工位，不能今天就在本地闭门做完。

## 我的当前建议
- 下一步先走 `B1-offline-minimal`。

### 原因
1. 完全符合当前离线约束
2. 立刻能基于现有数据落代码
3. 能把目标侧文本监督真正接进训练，而不是继续停在 inventory 层
4. 不会假装 source 侧已经有并不存在的转写/对齐标签

## 需要用户拍板的点
接下来我建议你在下面两条里拍板一条：

1. 走 `B1-offline-minimal`
- 大白话：先把目标侧文本和标点停顿监督接进训练，先做一版真的能跑的“新老师”。

2. 直接准备 `B2` 接口与字段
- 大白话：先不急着训练接入，而是优先把 phone/manner/alignment 的长线管线框架搭好。
