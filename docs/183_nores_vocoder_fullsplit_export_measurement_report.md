# 183. no-residual vocoder full-split export measurement 报告

## 背景
- `docs/182_nores_vocoder_fullsplit_export_budget_report.md`
  已给出 first-pass 预算:
  - `~194 sec`
  - `~2.26 GiB`
- 但预算毕竟只是 probe 外推，
  还缺:
  - full-split 实测
  - `skip-existing`
    复用实测

## 本轮目标
1. 直接跑一版
   `target_train + target_validation`
   full-split package export
2. 对比:
   - 预算 vs 实测
3. 再跑一版
   `--skip-existing`
   验证当前 package 复用是否已经足够快

## full-split export 实测

### 命令

```powershell
.\python.exe manage.py build-offline-mvp-nores-vocoder-dataset-packages --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1 --device cpu
```

### 结果
- package 数:
  - `train = 592`
  - `validation = 66`
  - `total = 658`
- 导出总耗时:
  - `253.765723 sec`
  - `4.229 min`
- 包总体积:
  - `2430235216 bytes`
  - `2.263 GiB`
- train summary:
  - `avg_package_build_sec = 0.352697`
  - `avg_package_size_bytes = 3692455.34`
- validation summary:
  - `avg_package_build_sec = 0.636469`
  - `avg_package_size_bytes = 3701540.23`

## 与预算对比
- 时间:
  - 预算 `194.054 sec`
  - 实测 `253.765723 sec`
  - 比预算高:
    - `1.308x`
    - 约 `+30.8%`
- 体积:
  - 预算 `2.263 GiB`
  - 实测 `2.263 GiB`
  - 基本打准

## skip-existing 复用实测

### 命令

```powershell
.\python.exe manage.py build-offline-mvp-nores-vocoder-dataset-packages --output-dir reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1 --device cpu --skip-existing
```

### 结果
- 总耗时:
  - `3.983004 sec`
- 复用计数:
  - `train reused_existing_count = 592`
  - `validation reused_existing_count = 66`
- 新建计数:
  - `train built_now_count = 0`
  - `validation built_now_count = 0`
- 复用态平均单包开销:
  - train `avg_package_build_sec = 0.001801`
  - validation `avg_package_build_sec = 0.001873`

## 当前判断

### 1. full-split export 已经真实可做
- 首次导出虽然比预算慢
  `~30.8%`，
  但量级仍是:
  - `4.2 分钟`
  - `2.26 GiB`
- 这还属于:
  - 可接受的工程成本

### 2. 当前不需要把 cache / loader 重构提到最高优先级
- 关键原因不是首次导出多快，
  而是:
  - 复用已有 package
    只要 `3.983s`
- 这说明:
  - 现有 `--skip-existing`
    已经把重复导出成本压得很低
- 所以当前更合理的顺序是:
  - 先继续 Stage5 dataset-level training
  - 而不是先停下来重写 package cache 基础设施

### 3. 仍要保留后手
- 虽然现在不用立刻重构，
  但如果后面继续叠加:
  - 多 objective 版本
  - 多轮 full rerun
  - 多套 package 分支
- 包体积和导出时间
  仍可能快速放大

## 当前边界
- 本轮实测覆盖的是:
  - package export
- 不是:
  - full-split dataset training
- 当前 package
  仍然是:
  - proxy spectral/gate target
  - 不是最终 waveform decoder objective

## 当前产物
- full export:
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.json`
  - `reports/runtime/offline_mvp_nores_vocoder_dataset_fullsplit_export_round1_1/offline_mvp_nores_vocoder_dataset_index.md`

## 下一步
1. 以当前 full-split package 池
   为基础，
   正式推进:
   - Stage5 dataset-level proxy training
2. 训练推进时继续观察:
   - 逐包加载是否成为瓶颈
   - checkpoint / validation
     是否需要 bucket 化
3. 若训练侧吞吐开始明显吃紧，
   再把:
   - packed loader
   - package cache 升级
     提到更高优先级

## 一句话结论
- Stage5 full-split package export
  已完成实测，
  结果是
  `4.229 分钟 / 2.263 GiB`；
  再加上 `--skip-existing`
  复用只需 `3.983s`，
  当前可以先继续推进
  dataset-level training，
  暂不必优先重写 cache / loader。
