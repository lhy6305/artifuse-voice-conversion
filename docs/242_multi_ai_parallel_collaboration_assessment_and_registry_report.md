# 2026-03-21 多 AI 并行协作结构评估与会话登记机制报告

## 结论
- 当前仓库已经具备：
  - 强恢复文档
  - 清晰的
    `reports/ / docs/ / tmp/`
    分层
  - 双线任务拆分
  - 大量正式 CLI
  - 固定 handoff / stage report
    产物
- 所以它对
  “多 AI 顺序接班”
  的支持已经比较强
- 但在
  “多 AI 同时并行改同一仓库”
  这个层面，
  之前还缺少：
  - 实时写域占坑
  - 当前会话索引
  - 谁在改什么的正式登记面
- 本轮已补上一个最小正式机制：
  - `register-ai-work-session`
  - `materialize-ai-work-session-index`

## 当前评估

### 1. 已经支持并行协作的部分
- `docs/00_context_bootstrap.md`
  已定义：
  - 恢复顺序
  - 双线入口
  - 文档维护纪律
- `docs/01_project_overview_and_plan.md`
  已长期维护：
  - 当前断点
  - 下一步
  - 重要文档入口
- `docs/02_pitfalls_log.md`
  已记录多类并行冲突：
  - 训练与评估强依赖不能混跑
  - 同一 metrics
    文件不能并行回写
  - 同一 managed 输出目录不能并行生成与读取
  - `init-experiment`
    不能并行
- 当前双线拆分
  也天然适合：
  - 用户线
  - 实验线
  分头推进

### 2. 之前不够支持并行协作的部分
- 没有一个正式位置记录：
  - 当前有哪些 AI 会话在活跃
  - 每个会话的 write roots
  - 每个会话依赖哪些 handoff 文档
- 这会导致：
  - 两个 AI
    可能同时写同一目录
  - 接班者只能从 git diff
    或临时对话里反推
    “谁在干什么”
- 也就是说，
  旧结构更像：
  - 强 handoff
  - 弱 live coordination

## 本轮代码变更

### 1. 新增模块
- `src/v5vc/ai_work_session_registry.py`

### 2. 新增 CLI
- `register-ai-work-session`
- `materialize-ai-work-session-index`

### 3. 当前能力
- 可登记：
  - `session_id`
  - `owner`
  - `lane`
  - `status`
  - `objective`
  - `write_roots`
  - `read_roots`
  - `handoff_docs`
  - `depends_on`
  - `notes`
- 会自动生成：
  - 单会话
    `json / md`
  - 总索引
    `ai_work_sessions_index.json / md`

## 当前正式目录
- `reports/collab/ai_work_sessions/`

## 推荐使用方式

### 1. 启动并行会话前先登记
```powershell
.\python.exe manage.py register-ai-work-session `
  --session-id experiment_line_stage5_decode `
  --owner codex-a `
  --lane experiment_line `
  --status active `
  --objective "continue Stage5 decode-side governance after postenv promotion" `
  --write-root reports/audio `
  --write-root docs `
  --handoff-doc docs/240_stage5_step72_glitch_smooth3_postenv_human_audit_reactivation_report.md
```

### 2. 另一条线用独立 write roots
```powershell
.\python.exe manage.py register-ai-work-session `
  --session-id user_line_minimal_runtime `
  --owner codex-b `
  --lane user_line `
  --status active `
  --objective "continue terminal-user minimal source-to-target runtime hardening" `
  --write-root reports/runtime/offline_mvp_teacher_first_vc_demo_runs `
  --write-root scripts/run_teacher_first_single_target_vc_demo.ps1 `
  --write-root docs `
  --handoff-doc docs/239_teacher_first_single_target_multisource_smoke_and_wrapper_report.md
```

### 3. 会话变化后可重登记同一 `session_id`
- 当前命令会覆盖更新同一会话卡，
  并自动重建总索引

## 当前建议的协作纪律
1. 同一时间只允许一个 AI
   拥有同一个 write root
2. 共享：
   `docs/01_project_overview_and_plan.md`
   和
   `docs/02_pitfalls_log.md`
   时，
   应在同一轮结束前再统一回写，
   不要并行频繁覆盖
3. 会重写 managed 输出目录的命令，
   不要由两个 AI
   同时操作同一目录
4. 训练、
   checkpoint selection、
   评估汇总、
   GUI session
   这类命令，
   默认都先登记会话和 write roots

## 一句话结论
- 当前仓库原本已经很适合
  “断线后继续接班”，
  但还不够适合
  “多个 AI 同时写同一仓库”；
  本轮新增的会话登记 CLI，
  把它补到了
  “至少能正式占坑、声明写域、生成活跃索引”
  的最低可用并行协作水平。

## 2026-03-21 补充：write-root 冲突已升级为显式告警
### 当前结论
- 当前 registry
  不再只是
  “登记 write roots”，
  还会主动计算：
  - 同路径冲突
  - 父子路径冲突
- 冲突信息现在会同时写进：
  - 单会话
    `json / md`
  - 总索引
    `ai_work_sessions_index.json / md`
- 若检测到冲突，
  CLI 还会在命令行打印：
  - `WARNING: write-root conflicts detected...`

### 当前新增字段
#### 1. 单会话
- `write_root_conflicts`
- `warnings`

#### 2. 总索引
- `conflict_count`
- `conflicted_session_count`
- `write_root_conflicts`

### 本轮验证
#### 命令
```powershell
.\python.exe manage.py register-ai-work-session `
  --session-id alpha `
  --owner codex-a `
  --lane user_line `
  --status active `
  --objective "validate conflict warning alpha" `
  --write-root docs `
  --write-root reports/runtime/offline_mvp_teacher_first_vc_demo_runs `
  --output-dir tmp/ai_work_session_registry_validation_b

.\python.exe manage.py register-ai-work-session `
  --session-id beta `
  --owner codex-b `
  --lane experiment_line `
  --status active `
  --objective "validate conflict warning beta" `
  --write-root docs `
  --write-root reports `
  --output-dir tmp/ai_work_session_registry_validation_b
```

#### 结果
- 第二条命令打印了显式告警
- index 关键字段：
  - `conflict_count = 2`
  - `conflicted_session_count = 2`
- 本轮实际识别出的两类冲突：
  1. `docs`
     对
     `docs`
     的同路径冲突
  2. `reports`
     对
     `reports/runtime/offline_mvp_teacher_first_vc_demo_runs`
     的父子路径冲突

### 当前意义
- 多 AI 协作结构现在从：
  - 能登记
  提升到了：
  - 能发现冲突
  - 能把冲突明确写在会话卡和总索引里
- 这样接班者不必再只靠：
  - git diff
  - 对话记忆
  去反推
  “现在是不是已经有人占了这个写域”

### 下一步建议
1. 若后续并行会话更多，
   可再考虑是否把：
   - 冲突等级
   - 建议处置动作
   也模板化写进 warning
2. 若未来要接 GUI / 训练类重写目录，
   可再评估是否把冲突从
   “告警”
   升级为
   “默认阻止”
