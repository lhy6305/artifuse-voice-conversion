# 134. `round1.1 / stage progress + route assessment` 报告

## 背景
- 当前用户问题不是再问某个单实验输赢，
  而是要评估:
  - 从旧三锚 `D22 / D29 / D33`
  - 到现在 `D80+` 这批 long-horizon 近邻
  - 是否真的取得了阶段性进展
  - 当前路线本身是否仍然正确
  - 下一步应不应该继续按现在的方式推进
- 补充说明:
  - 若这里提到“旧三锚”，按当前正式口径应理解为:
    - `D22 / D29 / D33`
  - `D39` 是后续 phase-handoff 路线里的一个实验点，
    不是旧阶段长期稳定的正式 anchor。

## 评估口径
本报告把“进展”拆成三层:

1. 是否拿到了更好的正式 route 结构
2. 是否把关键问题收窄了，而不是继续盲扫
3. 是否出现了真正能替代旧 anchor 的新单点

## 结论先行
### 1. 有阶段性进展，而且不是小进展
- 进展主要体现在:
  - route 结构从旧三锚，发展成了 long-horizon 下更清晰的四角色
  - validation 前沿被明显推低
  - `e_evt` 前沿被单独抬高
  - 一批容易误判的近邻轴已经被系统排干净

### 2. 但这还不是“已经找到最终单点赢家”
- 当前没有出现一个新 anchor，
  能同时取代:
  - `D76`
  - `D79`
  - `D82`
  - `D33`
- 更准确的状态是:
  - 我们拿到了更清晰的路线图，
  - 但还没拿到总冠军。

### 3. 当前总路线仍然正确，但战术方向该切换
- 正确的部分是:
  - 继续把问题写成 route / anchor policy 问题，
    而不是强行追一个“万能单点”
  - 继续把 official、matched20、long-horizon 三条口径分开
  - 继续先 quick-screen，再补少数代表点的长窗验证
- 应该切换的部分是:
  - 不再继续把主要预算花在:
    - late teacher source handoff
    - late `z_art_weight`
    - late `z_art_influence` retarget
    - full-priority singleton exposure

先说人话:
- 路没走错。
- 但现在这条路上的“旧旋钮”已经快被拧干了。
- 继续拧，大概率只是把同一个结论换几种写法再重复一遍。

## 阶段性进展具体在哪里
### 1. validation 前沿取得了实质推进
- 旧三锚里 validation leader 是:
  - `D29 final = 2.397175`
- 当前 long-horizon validation leader 是:
  - `D76 final = 2.107936`

这不是 epsilon 级改善，
而是明确的前沿下移。

解释:
- 即使这不代表 `D76` 就该成为所有场景下的新默认，
  也已经说明:
  - 长窗 backbone 这条线不是白跑
  - 我们确实把 validation frontier 往前推了一大段

### 2. `e_evt` 不再只能绑定在 old minimax 上
- 旧三锚阶段:
  - `D22` 是默认 minimax，
    `D33` 是 special / `e_evt` / `z_art`
- 到当前 long-horizon:
  - `D79` 已经单独拿走 `e_evt` leader
  - `D82` 又把 special leader 从 `D79` 切走

解释:
- 这说明 route 不再只是:
  - validation / minimax / special 三段粗分
- 而是进一步长成:
  - validation = `D76`
  - special = `D82`
  - `e_evt` = `D79`
  - default_minimax + `z_art` = `D33`

这就是实质性的结构进展。

### 3. long-horizon 已经证明旧 minimax 不是普适真相
- 旧 quick-screen 里:
  - `D22` 是 minimax default
- 但当前 full long-horizon route 已经稳定变成:
  - minimax = `D33`

解释:
- 这不是说 official quick-screen 要立刻废掉。
- 而是说明:
  - 旧 anchor 的制度角色是有 horizon 条件的
  - `D22` 不再能被写成“所有口径下都最稳的默认点”

### 4. 更重要的进展是“排错能力”已经显著提高
当前已经被较清楚排干净的方向包括:
- `D78`
  - 直接把 late teacher source 切回 `D33`
  - 会把 minimax 拉回 `D33`
- `D80`
  - `late z_art_weight` 抬升无效
- `D81`
  - `z_art_influence_aux` late-pool retarget 无效
- `D82`
  - 更强 singleton exposure 只能继续推成 special-only
- `D83`
  - `D33 -> D22` phase handoff 真实命中，
    但 final 仍被 `D79` 支配

解释:
- 这类“负结果成串出现”不是坏消息。
- 它的价值在于:
  - 当前问题已经被收窄到相当具体的层面
  - 后面不需要再在这些旧轴上反复试错

## 当前还没有取得的突破
### 1. 还没有新的单点总冠军
当前没有任何一个 `D80+` 实验能够同时拿下:
- validation
- special
- `e_evt`
- `z_art`
- minimax

所以不能把当前状态写成:
- “已经找到最终最优 anchor”

### 2. `z_art` 缺口依然没有被真正补上
- 当前 best `z_art` floor 仍然是:
  - `D33`
- `D79` 虽然把 special + `e_evt` 拉回来了，
  但 `z_art` 还是不够
- `D80 / D81 / D82 / D83`
  都没有把这个缺口补上

这就是当前最核心的剩余问题。

### 3. official quick-screen 还没有被推翻
- 当前 official quick-screen 仍是:
  - validation = `D71`
  - default_minimax = `D22`
  - special / `e_evt` / `z_art` = `D33`

所以当前也不能写成:
- “旧体系已经完全被新体系取代”

## 当前路线是否仍正确/合理
### 结论
- 战略上: 正确
- 战术上: 需要切换

### 为什么战略上仍正确
1. 继续用 route / policy 视角，而不是单点视角，是对的。
2. 继续把 official、matched20、full long-horizon 分开，是对的。
3. 继续用少量代表点做 `200-step` probe，而不是全家桶一起拉长，是对的。
4. 继续保留 governance guardrail，避免 shadow / checkpoint option 混写成正式默认，是对的。

### 为什么战术上需要切换
因为当前 `D80+` 已经说明:
- teacher family 内部小旋钮
- current singleton cohort 的更强曝光
- `z_art_influence` 的 pool retarget
- phase-specific source handoff

都不足以解决当前 long-horizon 的 `z_art` 缺口。

继续做这些，
信息量已经明显下降。

## 下一步做什么
### 推荐主线
- 下一步不要继续做 `D80-D83` 这种同 family 近邻微调。
- 更合理的是:
  - 新开一轮“更外层 `z_art` restoration”问题
  - 但优先复用仓库里已经实现过的外层监督能力，
    而不是再发明一整套新基础设施

### 推荐执行顺序
1. 先做一个 quick-screen 级新 probe，
   不直接上 full `200-step`
2. 基线优先继承:
   - `D79` 的 long-horizon骨架思路
   - 或其 quick-screen 对应 family
3. 主改动不再放在:
   - teacher source
   - teacher per-head weight
   - current singleton exposure
4. 主改动优先放在:
   - 比 `teacher_consistency` / `z_art_influence_aux` 更外层的 supervision
   - 且 cohort 定义要比当前 `micro_pause_none_singleton_strict` 更接近真正想保的 `z_art` 形状

### 更具体的建议
当前最值得优先尝试的，
不是“再做一个新老师”，
而是“换一个更像目标现象的题”。

优先级建议:
1. 新 cohort + 现有外层 supervision
   - 例如复用已落地的:
     - `formal_special_clause_shape_aux`
     - `punctuation_profile_aux`
     - 或其它 frame-local / structure-local 监督
   - 但不要再沿旧的 `D56-D59` cohort 定义原样平移
2. 先 quick-screen 验证方向
   - 有信号再补 `matched20`
   - 最后才补 `200-step`
3. 若 quick-screen 都没有打开新形状，
   再考虑是否要设计真正新的 proxy principle

先说人话:
- 下一步最该做的，
  不是再换老师怎么说。
- 而是换一道更对路的题，
  看模型会不会因此把 `z_art` 真留住。

## 当前建议的正式表述
1. 已取得阶段性进展。
2. 进展主要体现在:
   - validation frontier 前移
   - `e_evt` 与 special 角色拆分更清楚
   - long-horizon route 结构从三锚进化成四角色
   - 多条低信息量近邻轴被正式排除
3. 当前路线总体仍正确合理。
4. 但当前阶段不应继续主要依赖 `D80-D83` 这一类 teacher-family / singleton-family 微调。
5. 下一步应转向:
   - 更外层 `z_art` restoration / supervision 机制
   - 并继续遵守 quick-screen -> matched -> long-horizon 的验证顺序。
