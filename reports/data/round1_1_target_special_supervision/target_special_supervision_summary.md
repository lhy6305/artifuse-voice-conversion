# round1 target-side special supervision blueprint

## 目的
- 把 `target_special_eval` 的真实边界、训练/验证中的近邻 proxy 样本、以及更大规模的结构型 supervision pool 统一整理成正式 sidecar。
- 这一步只做数据/监督底账，不改训练逻辑。

先说人话：
- 现在需要先知道模型下一轮该重点看哪几类样本，而不是继续在全量数据上堆一个更聪明的小 loss。

## special slice 当前画像
- `target_special_eval` 记录数: `8`
- 时长范围: `0.470998 ~ 2.114989` 秒
- 时长中位数: `0.956985` 秒
- lexical char: `[0, 0, 0, 0, 0, 0, 0, 0]`
- pause boundary: `[0, 0, 0, 0, 0, 0, 0, 0]`
- terminal boundary: `[0, 0, 0, 0, 0, 0, 0, 0]`
- clause count: `[0, 0, 0, 0, 0, 0, 0, 0]`
- structure counts: `{'nonverbal': 8}`
- final terminal counts: `{'none': 8}`

结论：
- `round1.1` 的 special slice 仍然是纯 nonverbal challenge。它不能被拿去训练，但它可以明确告诉我们：
  下一轮应该先找“更像它的训练代理样本”和“更明确的结构监督池”。

## 关键 supervision pools
### `challenge_proxy_core`
- 记录数: `16`
- split counts: `{'target_train': 16}`
- lexical char 中位数: `1.0`
- 时长中位数: `0.920998` 秒
- clause 中位数: `1.0`
- pause / terminal 中位数: `1.0 / 0.0`
- structure counts: `{'other': 16}`
- final terminal counts: `{'none': 16}`
- 示例:
  - `target::chapter3_17_firefly_138` | score `0.916971` | lex `1` | dur `0.396009` | text `一，`
  - `target::chapter3_17_firefly_137` | score `0.916667` | lex `1` | dur `0.436984` | text `二，`
  - `target::chapter3_17_firefly_136` | score `0.916362` | lex `1` | dur `0.605986` | text `三，`
  - `target::chapter3_3_firefly_124` | score `0.915449` | lex `1` | dur `0.717982` | text `欸，`
  - `target::chapter3_3_firefly_249` | score `0.915145` | lex `1` | dur `0.757982` | text `一，`
  - `target::chapter3_3_firefly_250` | score `0.914536` | lex `1` | dur `0.776984` | text `二，`

### `challenge_proxy_relaxed`
- 记录数: `48`
- split counts: `{'target_train': 43, 'target_validation': 5}`
- lexical char 中位数: `4.0`
- 时长中位数: `1.265986` 秒
- clause 中位数: `1.0`
- pause / terminal 中位数: `1.0 / 0.5`
- structure counts: `{'other': 24, 'single_clause_terminal': 24}`
- final terminal counts: `{'none': 24, 'terminal_exclamation': 3, 'terminal_period': 14, 'terminal_question': 7}`
- 示例:
  - `target::chapter3_17_firefly_138` | score `0.916971` | lex `1` | dur `0.396009` | text `一，`
  - `target::chapter3_17_firefly_137` | score `0.916667` | lex `1` | dur `0.436984` | text `二，`
  - `target::chapter3_17_firefly_136` | score `0.916362` | lex `1` | dur `0.605986` | text `三，`
  - `target::chapter3_3_firefly_124` | score `0.915449` | lex `1` | dur `0.717982` | text `欸，`
  - `target::chapter3_3_firefly_249` | score `0.915145` | lex `1` | dur `0.757982` | text `一，`
  - `target::chapter3_3_firefly_250` | score `0.914536` | lex `1` | dur `0.776984` | text `二，`

### `micro_pause_none_singleton_strict`
- 记录数: `8`
- split counts: `{'target_train': 8}`
- lexical char 中位数: `1.0`
- 时长中位数: `0.737982` 秒
- clause 中位数: `1.0`
- pause / terminal 中位数: `1.0 / 0.0`
- structure counts: `{'other': 8}`
- final terminal counts: `{'none': 8}`
- 示例:
  - `target::chapter3_17_firefly_138` | score `0.916971` | lex `1` | dur `0.396009` | text `一，`
  - `target::chapter3_17_firefly_137` | score `0.916667` | lex `1` | dur `0.436984` | text `二，`
  - `target::chapter3_17_firefly_136` | score `0.916362` | lex `1` | dur `0.605986` | text `三，`
  - `target::chapter3_3_firefly_124` | score `0.915449` | lex `1` | dur `0.717982` | text `欸，`
  - `target::chapter3_3_firefly_249` | score `0.915145` | lex `1` | dur `0.757982` | text `一，`
  - `target::chapter3_3_firefly_250` | score `0.914536` | lex `1` | dur `0.776984` | text `二，`

### `micro_pause_none_singleton_relaxed`
- 记录数: `10`
- split counts: `{'target_train': 10}`
- lexical char 中位数: `1.0`
- 时长中位数: `0.767483` 秒
- clause 中位数: `1.0`
- pause / terminal 中位数: `1.0 / 0.0`
- structure counts: `{'other': 10}`
- final terminal counts: `{'none': 10}`
- 示例:
  - `target::chapter3_17_firefly_138` | score `0.916971` | lex `1` | dur `0.396009` | text `一，`
  - `target::chapter3_17_firefly_137` | score `0.916667` | lex `1` | dur `0.436984` | text `二，`
  - `target::chapter3_17_firefly_136` | score `0.916362` | lex `1` | dur `0.605986` | text `三，`
  - `target::chapter3_3_firefly_124` | score `0.915449` | lex `1` | dur `0.717982` | text `欸，`
  - `target::chapter3_3_firefly_249` | score `0.915145` | lex `1` | dur `0.757982` | text `一，`
  - `target::chapter3_3_firefly_250` | score `0.914536` | lex `1` | dur `0.776984` | text `二，`

### `micro_singleton_anypunct_relaxed`
- 记录数: `13`
- split counts: `{'target_train': 13}`
- lexical char 中位数: `1.0`
- 时长中位数: `0.776984` 秒
- clause 中位数: `1.0`
- pause / terminal 中位数: `1.0 / 0.0`
- structure counts: `{'other': 10, 'single_clause_terminal': 3}`
- final terminal counts: `{'none': 10, 'terminal_exclamation': 1, 'terminal_period': 1, 'terminal_question': 1}`
- 示例:
  - `target::chapter3_17_firefly_138` | score `0.916971` | lex `1` | dur `0.396009` | text `一，`
  - `target::chapter3_17_firefly_137` | score `0.916667` | lex `1` | dur `0.436984` | text `二，`
  - `target::chapter3_17_firefly_136` | score `0.916362` | lex `1` | dur `0.605986` | text `三，`
  - `target::chapter3_3_firefly_124` | score `0.915449` | lex `1` | dur `0.717982` | text `欸，`
  - `target::chapter3_3_firefly_249` | score `0.915145` | lex `1` | dur `0.757982` | text `一，`
  - `target::chapter3_3_firefly_250` | score `0.914536` | lex `1` | dur `0.776984` | text `二，`

### `micro_singleton_anypunct_expansion`
- 记录数: `5`
- split counts: `{'target_train': 5}`
- lexical char 中位数: `2.0`
- 时长中位数: `1.051995` 秒
- clause 中位数: `1.0`
- pause / terminal 中位数: `1.0 / 1.0`
- structure counts: `{'other': 2, 'single_clause_terminal': 3}`
- final terminal counts: `{'none': 2, 'terminal_exclamation': 1, 'terminal_period': 1, 'terminal_question': 1}`
- 示例:
  - `target::chapter3_29_firefly_107` | score `0.899011` | lex `2` | dur `1.650998` | text `请问，`
  - `target::chapter3_2_firefly_235` | score `0.89688` | lex `2` | dur `1.785986` | text `天啊，`
  - `target::chapter3_22_firefly_105` | score `0.823135` | lex `1` | dur `0.229002` | text `嗯。`
  - `target::chapter3_4_firefly_144` | score `0.779452` | lex `2` | dur `0.99898` | text `你是，？`
  - `target::chapter3_3_firefly_251` | score `0.778234` | lex `2` | dur `1.051995` | text `茄子，！`

### `short_pause_no_terminal`
- 记录数: `19`
- split counts: `{'target_train': 18, 'target_validation': 1}`
- lexical char 中位数: `2.0`
- 时长中位数: `1.001995` 秒
- clause 中位数: `1.0`
- pause / terminal 中位数: `1.0 / 0.0`
- structure counts: `{'other': 19}`
- final terminal counts: `{'none': 19}`
- 示例:
  - `target::chapter3_17_firefly_138` | score `0.916971` | lex `1` | dur `0.396009` | text `一，`
  - `target::chapter3_17_firefly_137` | score `0.916667` | lex `1` | dur `0.436984` | text `二，`
  - `target::chapter3_17_firefly_136` | score `0.916362` | lex `1` | dur `0.605986` | text `三，`
  - `target::chapter3_3_firefly_124` | score `0.915449` | lex `1` | dur `0.717982` | text `欸，`
  - `target::chapter3_3_firefly_249` | score `0.915145` | lex `1` | dur `0.757982` | text `一，`
  - `target::chapter3_3_firefly_250` | score `0.914536` | lex `1` | dur `0.776984` | text `二，`

### `short_terminal_burst`
- 记录数: `49`
- split counts: `{'target_train': 42, 'target_validation': 7}`
- lexical char 中位数: `5.0`
- 时长中位数: `1.359977` 秒
- clause 中位数: `1.0`
- pause / terminal 中位数: `0.0 / 1.0`
- structure counts: `{'multi_clause_single_terminal': 12, 'multi_terminal': 4, 'single_clause_terminal': 33}`
- final terminal counts: `{'terminal_exclamation': 6, 'terminal_period': 29, 'terminal_question': 14}`
- 示例:
  - `target::chapter3_22_firefly_105` | score `0.823135` | lex `1` | dur `0.229002` | text `嗯。`
  - `target::chapter3_3_firefly_162` | score `0.811263` | lex `3` | dur `0.612993` | text `我来吧。`
  - `target::chapter3_3_firefly_102` | score `0.807915` | lex `3` | dur `0.98898` | text `，对不起。`
  - `target::chapter3_3_firefly_149` | score `0.801826` | lex `3` | dur `1.385986` | text `，是这里。`
  - `target::chapter3_29_firefly_140` | score `0.801522` | lex `4` | dur `0.762993` | text `，我明白了。`
  - `target::chapter3_29_firefly_121` | score `0.800913` | lex `4` | dur `0.842993` | text `什么意思？`

### `structural_multi_terminal`
- 记录数: `174`
- split counts: `{'target_train': 156, 'target_validation': 18}`
- lexical char 中位数: `30.0`
- 时长中位数: `8.527483` 秒
- clause 中位数: `4.0`
- pause / terminal 中位数: `2.0 / 2.0`
- structure counts: `{'multi_terminal': 174}`
- final terminal counts: `{'none': 10, 'terminal_exclamation': 16, 'terminal_period': 122, 'terminal_question': 26}`
- 示例:
  - `target::chapter3_3_firefly_248` | score `0.723896` | lex `5` | dur `1.500998` | text `，好了！开始吧。`
  - `target::chapter3_3_firefly_129` | score `0.717504` | lex `5` | dur `1.899977` | text `咦？米沙是谁？`
  - `target::chapter3_2_firefly_236` | score `0.704947` | lex `10` | dur `1.752993` | text `你怎么变成这个样子了？！`
  - `target::chapter3_3_firefly_130` | score `0.702664` | lex `6` | dur `1.835986` | text `咦？你认识她吗？`
  - `target::chapter3_2_firefly_249` | score `0.689498` | lex `6` | dur `2.400998` | text `，这是什么情况？！`
  - `target::chapter3_2_firefly_134` | score `0.670776` | lex `9` | dur `1.829977` | text `点好了吗？那我买单啦。`

### `structural_question_exclaim`
- 记录数: `144`
- split counts: `{'target_train': 131, 'target_validation': 13}`
- lexical char 中位数: `14.0`
- 时长中位数: `3.675488` 秒
- clause 中位数: `2.0`
- pause / terminal 中位数: `1.0 / 1.0`
- structure counts: `{'multi_clause_single_terminal': 84, 'multi_terminal': 42, 'single_clause_terminal': 18}`
- final terminal counts: `{'terminal_exclamation': 42, 'terminal_question': 102}`
- 示例:
  - `target::chapter3_29_firefly_121` | score `0.800913` | lex `4` | dur `0.842993` | text `什么意思？`
  - `target::chapter3_3_firefly_117` | score `0.798174` | lex `3` | dur `1.679977` | text `，怎么了？`
  - `target::chapter3_3_firefly_119` | score `0.794521` | lex `4` | dur `1.325986` | text `，钟表小子？`
  - `target::chapter3_2_firefly_124` | score `0.793912` | lex `4` | dur `1.346984` | text `这边这边！`
  - `target::chapter3_2_firefly_242` | score `0.780746` | lex `5` | dur `1.729977` | text `你没事就好！`
  - `target::chapter3_4_firefly_144` | score `0.779452` | lex `2` | dur `0.99898` | text `你是，？`

### `structural_clause_ge4_no_final_terminal`
- 记录数: `46`
- split counts: `{'target_train': 38, 'target_validation': 8}`
- lexical char 中位数: `34.5`
- 时长中位数: `9.83449` 秒
- clause 中位数: `5.0`
- pause / terminal 中位数: `4.0 / 1.0`
- structure counts: `{'multi_clause_single_terminal': 30, 'multi_terminal': 7, 'other': 9}`
- final terminal counts: `{'none': 46}`
- 示例:
  - `target::chapter3_20_firefly_140` | score `0.513318` | lex `8` | dur `3.894989` | text `准备好了吗？一，二，三，`
  - `target::chapter3_3_firefly_235` | score `0.426865` | lex `11` | dur `5.977982` | text `讲笑话？啊，我，没什么幽默感，`
  - `target::chapter3_4_firefly_132` | score `0.368113` | lex `16` | dur `5.942993` | text `呃，只有一个宝箱？好可疑，要打开看看吗，`
  - `target::chapter3_2_firefly_220` | score `0.321689` | lex `22` | dur `5.565986` | text `你认识这么一个人吗？酒红色外套，绿眼睛，深蓝色头发，`
  - `target::chapter3_22_firefly_124` | score `0.304262` | lex `30` | dur `9.155986` | text `属于我的那一块，它曾经刻着格拉默铁骑，如今刻着星核猎手，而总有一天，`
  - `target::chapter3_3_firefly_127` | score `0.296423` | lex `33` | dur `8.157982` | text `我没有怀疑你，毕竟在梦里什么都有可能发生，我说的地方，晚点再去也没问题的，`

### `structural_clause_ge4`
- 记录数: `206`
- split counts: `{'target_train': 185, 'target_validation': 21}`
- lexical char 中位数: `37.0`
- 时长中位数: `10.615488` 秒
- clause 中位数: `5.0`
- pause / terminal 中位数: `3.0 / 2.0`
- structure counts: `{'multi_clause_single_terminal': 77, 'multi_terminal': 120, 'other': 9}`
- final terminal counts: `{'none': 46, 'terminal_exclamation': 11, 'terminal_period': 132, 'terminal_question': 17}`
- 示例:
  - `target::chapter3_20_firefly_140` | score `0.513318` | lex `8` | dur `3.894989` | text `准备好了吗？一，二，三，`
  - `target::chapter3_3_firefly_235` | score `0.426865` | lex `11` | dur `5.977982` | text `讲笑话？啊，我，没什么幽默感，`
  - `target::chapter3_20_firefly_166` | score `0.381279` | lex `15` | dur `3.999977` | text `，呃，不是，没什么。我们赶紧去下一关吧。`
  - `target::chapter3_4_firefly_132` | score `0.368113` | lex `16` | dur `5.942993` | text `呃，只有一个宝箱？好可疑，要打开看看吗，`
  - `target::chapter3_30_firefly_132` | score `0.3379` | lex `18` | dur `4.585986` | text `别过来，这颗炸弹很危险！还有，我是真的流萤！`
  - `target::chapter3_2_firefly_220` | score `0.321689` | lex `22` | dur `5.565986` | text `你认识这么一个人吗？酒红色外套，绿眼睛，深蓝色头发，`

### `structural_no_final_terminal`
- 记录数: `174`
- split counts: `{'target_train': 153, 'target_validation': 21}`
- lexical char 中位数: `15.0`
- 时长中位数: `4.952981` 秒
- clause 中位数: `2.0`
- pause / terminal 中位数: `2.0 / 0.0`
- structure counts: `{'multi_clause_single_terminal': 53, 'multi_terminal': 10, 'other': 111}`
- final terminal counts: `{'none': 174}`
- 示例:
  - `target::chapter3_17_firefly_138` | score `0.916971` | lex `1` | dur `0.396009` | text `一，`
  - `target::chapter3_17_firefly_137` | score `0.916667` | lex `1` | dur `0.436984` | text `二，`
  - `target::chapter3_17_firefly_136` | score `0.916362` | lex `1` | dur `0.605986` | text `三，`
  - `target::chapter3_3_firefly_124` | score `0.915449` | lex `1` | dur `0.717982` | text `欸，`
  - `target::chapter3_3_firefly_249` | score `0.915145` | lex `1` | dur `0.757982` | text `一，`
  - `target::chapter3_3_firefly_250` | score `0.914536` | lex `1` | dur `0.776984` | text `二，`

## 当前建议
- `challenge_anchor` 继续严格保持 eval-only。
- 下一轮数据/监督实验应优先从 `micro_pause_none_singleton_strict` 入手，把 special supervision 从 `clause-shape` 转到 clause-free singleton proxy。
- `challenge_proxy_core` 继续保留为 special-adjacent stress pool，但不再默认它就是最贴近 final challenge 的第一代理。
- `micro_singleton_anypunct_expansion` 适合作为 strict singleton 之外的差分 outer pool，用于更外层的 punctuation / `z_art` restoration 探针。
- `structural_multi_terminal / structural_question_exclaim / structural_clause_ge4` 应视为三条独立 supervision 轴，不要再混成一个统称的 structural proxy。
- 若需要更稳的样本量，可以把 `micro_pause_none_singleton_relaxed` 作为第二层 singleton proxy pool，但不要直接替代 strict pool。

## 产物
- `data_output_dir`: `F:/proj_dev/tmp/workdir4/data_prep/round1_1/target_special_supervision`
- `report_output_dir`: `F:/proj_dev/tmp/workdir4/reports/data/round1_1_target_special_supervision`
- sidecar:
  - `target_special_supervision_sidecar.jsonl`
  - `target_special_supervision_pools.json`
- reports:
  - `target_special_supervision_summary.json`
  - `target_special_supervision_summary.md`
