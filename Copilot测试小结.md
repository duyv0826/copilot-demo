# GitHub Copilot Chat 跨文件理解能力测试小结

- 测试日期：2026-09-09
- 测试工具：VS Code + GitHub Copilot Chat（Agent 模式，GPT-5.6 Luna）
- 测试项目：`copilot-demo`（多文件、强依赖的 Python 小应用）
- 项目结构：`main → service → models/storage`

---

## 一、测试目的

验证 Copilot Chat 三件事：
1. 能否用自然语言生成可运行的代码
2. 能否理解跨文件依赖（引用 `models.py` 里的类型/字段并正确联动）
3. 能否定位并修复跨文件之间的逻辑 bug

---

## 二、判定标准

| 标准 | 说明 |
|---|---|
| 可运行 | 生成的改动能直接 `python main.py` 跑通，无语法/属性错误 |
| 引用正确 | 涉及跨文件内容时，用的是真实存在的类名/字段/路径，而非臆造 |
| 不破坏依赖 | 改一个文件不破坏其它文件的既有依赖 |

---

## 三、用例与结果

### 用例 1：自然语言 → 跨文件生成代码

**指令**：在 `service.py` 里给 `Player`（定义在 `models.py`）加 `level` 字段，并在 `main.py` 里打印出来。

| 轮次 | Copilot 表现 | 判定 |
|---|---|---|
| 第 1 轮（Ctrl+I 内联补全） | 只在 `main.py` 光标处给了引用 `player.level` 的补全，但 **`models.py` 从未加过该字段** → 接受即报 `AttributeError` | ✗ 跨文件失败（靠猜） |
| 第 2 轮（Agent + "直接改文件"指令） | 真正编辑了 `models.py`（加 `level: int = 1`，带默认值）和 `main.py`（打印），并自行运行验证输出 `等级 -> 1` | ✓ 全部通过 |

**结论**：默认内联补全的跨文件感知弱、倾向猜测；明确要求"直接改文件"并切 Agent 模式后，才能触发真实的跨文件编辑与验证。

### 用例 2：跨文件逻辑 bug 定位与修复

**指令**：为什么玩家完成"讨伐史莱姆"交了木剑，但木剑还在背包里？帮我保持一致。

| 检查点 | Copilot 表现 | 判定 |
|---|---|---|
| 定位根源 | 直接修改 `service.py` 的 `try_complete_quest`，未在 `main.py` 打补丁 | ✓ |
| 修复完整性 | 从 `player.inventory` 移除木剑；且因木剑正装备在手，还从 `player.equipped` 卸下 | ✓（比预期更周全） |
| 不破坏依赖 | `models.py` 的 `level`/`storage.py` 均未受影响 | ✓ |

**验证输出**（我另行复跑）：
```
任务后装备: []
任务后背包: ['铁盾']
```
木剑从背包与装备栏都被正确消耗。

### 用例 3：跨四文件架构重构（Repository 模式）

**指令**：把玩家数据读写抽象成 `PlayerRepository` 类，并重构 `storage.py` / `service.py` / `main.py`，保留 `load_items`/`load_quests` 不动，且 `python main.py` 仍须正常运行。

| # | 判定标准 | 结果 | 说明 |
|---|---|---|---|
| 1 | 新增 `PlayerRepository` 且方法合理 | ✓ | `__init__(path)` + `load(items)` + `save(player)` |
| 2 | `service.py` / `main.py` 真正接入 | ✓ | `GameService` 持有 repo 并提供 `load_player`；`main.py` 创建并用其保存 |
| 3 | `python main.py` 正常运行 | ✓ | 实测行为与重构前一致 |
| 4 | 未误删 `load_items`/`load_quests`（陷阱） | ✓ | 两函数保留，`GameService._init_` 依旧调用 |

**亮点**：Copilot 正确识别"存档里物品按名字字符串存储"，`load(items)` 接收 `items` 字典把名字还原成 `Item`，并按 `Slot` 重建 `equipped`——说明读懂了 JSON ↔ 模型映射。

**已知小偏差**：`main.py` 仍以 `Player(name="Mario")` 新建实例，repo 的 `load()` 已实现但未被 main 走到；`save()` 未持久化 `level`，重载后等级回落默认 1。→ 见「用例 4」继续验证 load 闭环。

### 用例 4：load() 闭环 + 幂等修复

**起因**：用例 3 后 `load()` 只实现未使用。补上"读档继续游戏"时，发现更深的坑——闭环**能读档但不够幂等**。

**Copilot 的表现（部分正确）**：
- `storage.py` 的 `save()` 补写 `level`、`load()` 读回 —— ✓
- `main.py` 改为"先 `load()`，无存档才新建" —— ✓ load 被真正消费

**但存在逻辑上下文盲区**：`main.py` 每轮仍无条件执行 `give_item` + `try_complete_quest`，导致读档后物品翻倍、任务奖励重复结算。实测二次运行 `attack 15 → 20`、`defense 7 → 9`，数值逐轮增长。

**根因**：Copilot 补上了"读档"这一步（字段/引用都对），却没意识到"已加载的会话不该再发物品 / 不该再结算"——把新建流程与读档流程当成同一流程。这属于比字段错误更深的**跨文件逻辑上下文**盲区。

**修正方案（持久化已完成任务，保证幂等）**：

| 文件 | 改动 |
|---|---|
| `models.py` | `Player` 新增 `completed_quests: list[str]` |
| `service.py` | `try_complete_quest` 用 `quest.fid in completed_quests` 判重并记录 |
| `storage.py` | `save()` 写 `completed_quests`，`load()` 用默认值读回（向后兼容） |
| `main.py` | 按 `quest.fid not in completed_quests` 决定"结算"or"[读档]"分支 |

**验证**（删档后连续运行 3 次）：

```
第1次(新建): 任务完成 True → attack 15, defense 7
第2次(读档): [读档] 任务已完成，无新结算 → attack 15, defense 7
第3次(读档): 一致 → attack 15, defense 7   （幂等）
```

> 补充：第一版曾用 `quest.completed` 当守卫，跑起来才发现任务完成状态未持久化（任务每次从 JSON 重读、默认 False），守卫形同虚设——这也是跨文件状态一致性的一个隐蔽点。

### 用例 5：让 Copilot 从零自写 pytest 测试

**指令**：在空 `tests/` 目录下，让 Copilot 针对装备、任务结算、重复结算、存档闭环写一组 pytest，不修改源文件与 `data/`。

**实验过程**：
- 第 1 轮因磁盘已有参考测试，Copilot 直接认领现有 `test_basic.py` 而未重写（说明了它会**优先复用工作区已有测试**）；删除清空后再测。
- 第 2 轮真正从零生成 `test_service.py` + `test_storage.py` 两个文件、共 6 个用例，`Completed 10 steps in 1m 33s`。

**终审判分**（逐行读码 + 独立复跑 `python -m pytest` = 6 passed）：

| 判分点 | 结果 | 证据 |
|---|---|---|
| 卸下装备（背包+装备栏消失） | ✓ | 断言 `inventory == []` 且 `equipped == {}` |
| 重复任务返回 False、奖励只涨一次 | ✓ | 断言第二次 `is False`，attack/defense 不变 |
| 存档往返含 completed_quests | ✓ | 断言 `completed_quests == ["q1"]` |
| 未拥有物品 equip → False | ✓ | 断言返回 False 且 `equipped == {}` |
| 存档缺失 → None | ✓ | 断言 `load({}) is None` |
| 不削断言/不绕逻辑 | ✓ | 断言均校验真实业务值，无"只测不崩"敷衍 |

**亮点**：测试是全新命名与结构（未照抄参考）、用 `next(q for q in quests if q.fid=="q1")` 精准定位任务、存档用 `tmp_path` 隔离；主动覆盖了此前人类盲区的三个"不该发生"边界（卸下装备 / 重复任务 / 存档缺失）。

---

## 四、总体评估

**强项**
- Agent 模式下能跨文件编辑并自行运行验证。
- 能定位到应用层的真正 bug 根源，修复考虑周全（连装备栏都覆盖到）。

**短板**
- 纯内联补全（`Ctrl+I`）默认不主动核实其它文件，会基于猜测生成引用不存在字段的代码。
- "跨文件理解"需要靠明确指令（"直接改文件"）+ Agent 模式才会真正生效。

**横向总结**

| 能力 | 用例 1 | 用例 2 | 用例 3 | 用例 4 | 用例 5 |
|---|---|---|---|---|---|
| 基础字段跨文件添加 | △→✓（内联差 / Agent 好） | ✓ | ✓ | ✓ | / |
| 定位深层逻辑bug/修复 |  / | ✓ | ✓ | ⚠️（一半对，缺幂等） | / |
| 跨文件架构重构 | / | / | ✓ | ✓ | / |
| 遵守不删指定函数约束 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 自写测试并覆盖边界 | / | / | / | / | ✓ |

**核心结论**：Copilot Chat 的跨文件理解在 **Agent 模式下表现扎实**——
- ✅ 能读真实文件、按其格式还原对象、遵守"保留哪些函数"的约束，字段/类名基本不会错。
- ✅ 浅层字段级、方法级的跨文件重构，基本可以一步做成。
- ✅ 能"旁观式"读懂自身业务逻辑，从零写出覆盖关键边界（卸下装备 / 重复任务 / 存档缺失）的测试，且一次跑绿。
- ⚠️ 遇到**跨文件状态一致性**问题（比如读档是否该重发物品），需要人来点破逻辑盲区——它能做"把读完档之后该做什么"，但不一定能想到"读完档之后不该做什么"。

短板：**纯内联补全（`Ctrl+I`）默认不主动核实其它文件**，会基于猜测生成引用不存在字段的代码；"跨文件理解"需要**明确指令 + Agent 模式**才会真正生效。

**实操建议**：测试/使用跨文件能力时，优先用 Agent 模式并明确要求改动文件，而非单纯内联补全。

---

## 五、附：`service.py` 修复后的 `try_complete_quest`（装备卸下逻辑）

Copilot 在修复任务 bug 时，额外补上了"若上交物品正被装备则同时卸下"的逻辑，比仅移除背包更符合游戏直觉。改进后的完整方法如下：

```python
def try_complete_quest(self, player: Player, quest: Quest) -> bool:
    if quest.completed:
        return False
    need = self.items.get(quest.required_item or "")
    if need and need not in player.inventory:
        return False
    if need:
        player.inventory.remove(need)
        if player.equipped.get(need.slot) is need:   # 若正装备着，同步卸下
            del player.equipped[need.slot]
    quest.completed = True
    player.attack += quest.reward_exp
    player.defense += quest.reward_gold // 10
    return True
```

要点：
- 先校验 `required_item` 是否在背包，不在则任务不可完成。
- `inventory.remove(need)` 消耗上交物品。
- `player.equipped.get(need.slot) is need` 用**同一对象身份**判断，避免误删同名不同物。
- 该改动与 `models.py` 上轮新增的 `level: int = 1` 兼容，未破坏其它模块。