# 2026-03-26 Stage5 dataset split builder `ProcessPoolExecutor` 接管与主进程统一打点报告

## 本轮目标
- 接续上轮已完成的参数入口改动：
  - `build-offline-mvp-nores-vocoder-dataset-packages`
    已新增 `--worker-processes`
- 本轮要完成的是：
  - 保留原串行路径
  - 当 `worker_processes > 1` 时，让核心 split builder 改走 `ProcessPoolExecutor`
  - 由主进程按 future 完成数统一打印进度
  - 把真实生效的 `worker_processes` 落进 dataset index，避免再出现“CLI 有参数、产物里看不出来”的假接线

## 代码改动

### 1. 顶层参数真实透传到底
- 文件：
  - `src/v5vc/cli.py`
  - `src/v5vc/offline_vocoder_training.py`
- 当前状态：
  - CLI 的 `--worker-processes`
    已传入 `build_offline_mvp_nores_vocoder_dataset_packages(...)`
  - 本轮进一步补齐：
    - `build_offline_mvp_nores_vocoder_dataset_packages(...)`
      -> `build_dataset_packages_for_split(..., worker_processes=...)`
    - `train`
      与 `validation`
      两个 split 都会收到同一个 `worker_processes`

### 2. 核心 split builder 改为“先建任务，再按模式执行”
- `build_dataset_packages_for_split(...)`
  不再直接在单个大循环里一边导出一边记 summary。
- 现在先把每条 record 组装成 `task`，
  再交给：
  - `build_dataset_packages_from_tasks(...)`
- 这样把“任务准备”和“串行/并行执行策略”拆开了，
  后续更容易继续做并行治理或吞吐测量。

### 3. 串行路径保留
- 当 `worker_processes == 1` 时：
  - 继续逐条调用 `build_dataset_package_for_record(...)`
  - 返回结果顺序保持与原始 split 顺序一致
  - 进度仍按主循环推进

### 4. 并行路径改走 `ProcessPoolExecutor`
- 当 `worker_processes > 1` 时：
  - 使用 `ProcessPoolExecutor(max_workers=worker_processes)`
  - 每条 record 作为一个独立 future 提交
  - 主进程使用 `as_completed(...)`
    按 future 完成顺序聚合结果
- 结果仍会按原始 `record_index`
  排序回写到 `train_packages / validation_packages`，
  所以 dataset index 的记录顺序不会因为并行完成先后而乱掉。

### 5. 统一主进程打点
- 本轮新增：
  - `log_stage5_dataset_package_progress(...)`
- 无论串行还是并行，
  都只由主进程调用这一个进度打印函数。
- 并行模式下的 `completed=x/y`
  现在明确表示：
  - 已完成 future 数
  - 不是原始 split 序号
- 这解决了并行路径最容易出现的两个问题：
  - 子进程乱序打印导致日志不可读
  - 进度数字看起来像“跳号”但其实只是原始 record index

### 6. 复用判断被抽成独立函数
- 本轮把原来内联在循环里的
  `skip_existing` 复用判断抽成：
  - `should_reuse_existing_stage5_training_package(...)`
- 这样并行 worker 端可以直接复用同一套判断，
  减少串行和并行逻辑分叉。

### 7. 运行元数据落盘
- dataset index 现在新增：
  - `worker_processes`
- dataset index markdown 也同步新增：
  - `worker_processes`
  - `spectral_target_mode`
- `notes`
  里已明确写入：
  - `worker_processes=1`
    保留原串行 split builder
  - `worker_processes>1`
    切到 `ProcessPoolExecutor`
  - 进度由主进程按 future 完成数统一打印

## 验证

### 1. 静态校验
- 命令：
```powershell
.\python.exe -m py_compile src/v5vc/cli.py src/v5vc/offline_vocoder_training.py
```
- 结果：
  - 通过

### 2. CLI 解析校验
- 命令：
```powershell
.\python.exe manage.py build-offline-mvp-nores-vocoder-dataset-packages --help
```
- 结果：
  - `--worker-processes`
    已正常显示在帮助文本中

### 3. 最小真 smoke
- 命令：
```powershell
.\python.exe manage.py build-offline-mvp-nores-vocoder-dataset-packages `
  --output-dir tmp/stage5_dataset_parallel_smoke `
  --device cpu `
  --worker-processes 2 `
  --max-train-records 1 `
  --max-validation-records 1 `
  --selection-mode shortest_duration
```

### 4. smoke 输出
- 关键日志：
  - `worker_processes=2`
  - `split=train completed=1/1 ...`
  - `split=validation completed=1/1 ...`
- 完成耗时：
  - `duration_sec = 5.964929`
- 输出目录：
  - `tmp/stage5_dataset_parallel_smoke/`
- dataset index：
  - `tmp/stage5_dataset_parallel_smoke/offline_mvp_nores_vocoder_dataset_index.json`
- 关键字段已确认：
  - `"worker_processes": 2`

## 当前结论
- `worker_processes`
  已不是停留在 CLI 层的悬空参数，
  而是已经真实接到 Stage5 dataset package split builder。
- 当前语义已明确：
  - `worker_processes == 1`
    保留原串行路径
  - `worker_processes > 1`
    使用 `ProcessPoolExecutor`
  - 进度由主进程按 future 完成数统一打点
- 最小 smoke 说明：
  - 调用链成立
  - 产物落盘成立
  - metadata 落盘成立
- 但本轮还没有做：
  - 正式 full-split 吞吐对比
  - 不同 `worker_processes`
    下的 CPU / I/O / checkpoint 重载开销测量
- 因此当前能下的结论是：
  - 并行 split builder 已可用
  - 还不能把这次 1+1 smoke
    外推成 full-split 一定线性提速

## 下一步建议
1. 先用当前正式 full-split 导出命令，
   做一次 `worker_processes=1 vs 2/4`
   的真实导出耗时对比。
2. 重点观察：
   - 总耗时
   - train/validation 两段日志节奏
   - `skip_existing` 场景下并行是否仍有意义
3. 如果 full-split 证明收益稳定，
   再决定是否把某个 `worker_processes`
   设成新的默认值；
   在此之前不建议直接改默认。
