# 仓库健康度整改跟进

## 文档目的
- 本文档用于承接 `docs/447_repo_health_and_compliance_audit_20260328.md` 的整改结果。
- 记录本轮已完成修复、验证结果与剩余结构债务。
- 根目录预期存在的 `ssh` 私钥未被视为风险。

## 本轮已完成修复
### 1. Stage3 paired split 污染入口已封堵
- 文件：
  - `src/v5vc/streaming_student/data.py`
- 修复：
  - 新增 paired split 到 formal target split 的显式映射。
  - `attach_streaming_student_paired_contract_metadata()` 现在会硬校验 teacher label 的 `split_name`。
  - pair spec 若把 `train / validation` target 混写，现会直接报错，不再静默混用 teacher label。

### 2. Stage3 -> Stage5 最小桥接不再按“文件存在即复用”
- 文件：
  - `src/v5vc/streaming_student/stage5_handoff.py`
  - `src/v5vc/artifact_reuse.py`
- 修复：
  - 新增 Stage5 handoff package reuse signature。
  - 复用时会校验：
    - `packet_path`
    - `target_audio_path`
    - `semantic_consumer_mode`
    - `target_contract_mode`
    - `noise_event_family`
  - 旧产物若没有签名文件，将强制重建一次。

### 3. Stage5 dataset package 复用失效判定已收紧
- 文件：
  - `src/v5vc/offline_vocoder_training.py`
  - `src/v5vc/artifact_reuse.py`
- 修复：
  - 新增 Stage5 training package reuse signature。
  - 复用时会校验：
    - `source_audio_path`
    - `target_audio_path`
    - `route_handoff_path`
    - `checkpoint_path`
    - `calibration_asset_path`
    - semantic / timing / parity sidecar 内容指纹
    - `semantic_consumer_mode`
    - `target_contract_mode`
    - `spectral_target_mode`
    - `teacher_e_evt_bridge_mode`
    - `teacher_e_evt_target_shaping_mode`
  - 没有签名或签名不一致时会强制重建，不再静默沿用旧 package。

### 4. Stage5 dataset markdown 摘要口径已修正
- 文件：
  - `src/v5vc/streaming_student/stage5_handoff.py`
- 修复：
  - `build_dataset_markdown()` 现在根据当前 `split_name` 选择 active split summary。
  - train-only 输出不再误读 `validation` 维度统计。

### 5. 危险目录清空 helper 已统一并加边界保护
- 文件：
  - `src/v5vc/managed_paths.py`
  - `src/v5vc/**/*.py` 多处调用点
- 修复：
  - 将 38 处复制粘贴的 `reset_managed_directory()` 收口到统一 helper。
  - 新 helper 会拒绝：
    - 仓库根外路径
    - 顶层过宽路径
    - 实际是文件的路径
  - 这样后续再修目录安全边界时，不需要全仓重复改 38 份。

### 6. teacher-first 相关默认运行目录已改短
- 文件：
  - `src/v5vc/cli.py`
- 修复：
  - teacher-first demo / review / smoke / compare / applicability probe 的默认输出目录已改成短名：
    - `reports/runtime/tfd_demo`
    - `reports/runtime/tfd_review_bundle`
    - `reports/runtime/tfd_smoke_bundle`
    - `reports/runtime/tfd_compare_bundle`
    - `reports/runtime/tfd_app_probe/*`
- 作用：
  - 新产物默认路径明显缩短。
  - 以后继续生成 runtime 输出时，更不容易逼近 Windows / Git 深路径边界。

### 7. 主文档已瘦身并归档当前快照
- 文件：
  - `docs/01_project_overview_and_plan.md`
  - `docs/02_pitfalls_log.md`
  - `docs/archive/01_project_overview_and_plan_snapshot_20260328.md`
  - `docs/archive/02_pitfalls_log_snapshot_20260328.md`
- 修复：
  - 将两份主文档重新压回“现行索引”形态。
  - 详细历史保留在 `docs/archive/`，不再继续堆进主入口文档。
- 当前行数：
  - `docs/01_project_overview_and_plan.md = 70`
  - `docs/02_pitfalls_log.md = 55`

### 8. ignored 缓存已清理
- 处理：
  - 删除了工作区中残留的：
    - `__pycache__/`
    - `configs/__pycache__/`
    - `src/v5vc/__pycache__/`
    - `src/v5vc/offline_mvp/__pycache__/`
    - `src/v5vc/streaming_student/__pycache__/`

## 验证结果
- `python -m compileall src/v5vc manage.py` 通过。
- `PYTHONPATH=src` 下对以下符号的 import smoke 通过：
  - `v5vc.managed_paths.reset_managed_directory`
  - `resolve_expected_teacher_split_name_for_paired_split`
  - `build_streaming_student_stage5_package_reuse_signature`
  - `build_stage5_training_package_reuse_signature`

## 当前仍然存在的结构债务
### 1. 三个核心 megafile 仍然偏大
- 当前行数：
  - `src/v5vc/cli.py = 6486`
  - `src/v5vc/teacher_first_vc_demo.py = 6679`
  - `src/v5vc/offline_vocoder_training.py = 5987`
- 说明：
  - 本轮已先拆掉系统性重复 helper、缩短默认路径、把文档入口压回可维护规模。
  - 但这三份源码还没有完成模块级拆分，仍属于后续应继续处理的真实维护债务。

### 2. 历史 `reports/` 深路径树仍在磁盘上
- 说明：
  - 本轮只修改了新产物默认路径，不对既有历史 runtime 树做迁移。
  - 原因是历史树体量大、层级深，直接批量搬迁会改变既有实验引用关系。
- 当前判断：
  - 新默认路径问题已缓解。
  - 旧历史树仍然建议在单独窗口做归档或迁移。
