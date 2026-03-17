# 187. Stage5 checkpoint review 广覆盖收益报告

## 背景
- `docs/186_stage5_seeded_gpu_baseline96_marginal_gain_review_report.md`
  已确认:
  - `96-step`
    仍优于
    `48-step`
  - 但边际收益
    已明显收窄
- 下一步必须回答的，
  不只是:
  - 平均 validation `loss_total`
    还在不在下降
- 还包括:
  - 改善是否广覆盖
  - 还是只靠少数 validation package
    拉低平均值

## 本轮动作

### 1. 新增可复用 review 入口
- 新增:
  - `src/v5vc/nores_vocoder_checkpoint_review.py`
- CLI:
  - `review-offline-mvp-nores-vocoder-checkpoints`
- 输入:
  - Stage5 dataset loop
    的 `summary.json`
- 输出:
  - checkpoint 级 marginal gain
  - validation package 级
    improved / worsened 分布
  - top improved / least-improved records

### 2. 本轮 review 命令

```powershell
.\python.exe manage.py review-offline-mvp-nores-vocoder-checkpoints --summary reports/runtime/offline_mvp_nores_vocoder_fullsplit_training_gpu_seeded_baseline96_round1_1/logs/offline_mvp_nores_vocoder_dataset_loop.summary.json --output-dir reports/runtime/offline_mvp_nores_vocoder_checkpoint_review_baseline96_round1_1 --top-k 10
```

## review 结果

### checkpoint 级轨迹
- step24:
  - `0.469644`
- step48:
  - `0.441292`
  - 相对 step24:
    `delta = -0.028352`
- step72:
  - `0.435399`
  - 相对 step48:
    `delta = -0.005893`
- step96:
  - `0.432645`
  - 相对 step72:
    `delta = -0.002754`

### package 级覆盖情况

#### 1. `24 -> 48`
- improved:
  - `66 / 66`
- worsened:
  - `0 / 66`
- 说明:
  - 这段收益不是局部样本特例，
    而是全 validation package
    普遍一起变好

#### 2. `48 -> 72`
- improved:
  - `64 / 66`
- worsened:
  - `2 / 66`
- 仅有轻微回退的记录:
  - `target::chapter3_3_firefly_207`
    `0.430987 -> 0.433185`
  - `target::chapter3_3_firefly_162`
    `0.416348 -> 0.417780`
- 说明:
  - 边际收益虽然收窄，
    但整体仍主要由广覆盖改善驱动

#### 3. `72 -> 96`
- improved:
  - `66 / 66`
- worsened:
  - `0 / 66`
- 说明:
  - 后段收益虽然更小，
    但仍然不是
    “少数样本换来均值变好”
  - 而是全体 validation package
    继续小幅同步改善

#### 4. `24 -> 96`
- improved:
  - `66 / 66`
- worsened:
  - `0 / 66`
- average delta:
  - `-0.036999`

## 当前判断

### 1. 当前 marginal gain 虽然变小，但仍然是 broad-based gain
- 这轮 review
  最关键的价值在于:
  - 把
    “平均值还在降”
    进一步核实为
    “几乎全部 validation package
     都还在降”

### 2. 当前不该把 `96-step` 误判成过拟合式改善
- 如果是过拟合式改善，
  更常见的表现会是:
  - 少数样本改善
  - 同时更多样本回退
- 但本轮看到的是:
  - `24 -> 48`:
    `66 / 66` improved
  - `72 -> 96`:
    `66 / 66` improved
- 所以更合理的写法是:
  - gain is smaller
  - but still broad-based

### 3. 下一步更适合精细 review，而不是盲目加步数
- 当前证据支持:
  - 继续训练还有收益
- 但收益已进入:
  - 小幅
  - 广覆盖
  - 边际收窄
    的区间
- 所以下一步更合理的是:
  - checkpoint review
  - 低频更远程 probe
  - 或开始准备 objective 切换

## 当前产物
- review 输出:
  - `reports/runtime/offline_mvp_nores_vocoder_checkpoint_review_baseline96_round1_1`

## 一句话结论
- Stage5 当前不只是
  `96-step` 平均 validation
  还在下降，
  而且这份收益在
  validation `66 / 66`
  package 上表现为
  广覆盖同步改善；
  因此当前更合理的口径是
  “收益已收窄但仍广覆盖”，
  而不是
  “已经只剩局部样本在拖均值”。
