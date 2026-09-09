# copilot-demo

一个刻意做成**多文件、强依赖**的 Python 小示例，用来验证 AI 编程助手（如 GitHub
Copilot Chat）的自然语言生成代码与**跨文件理解**能力。附带 pytest 单测与一份
覆盖 5 轮测试的小结（见 `Copilot测试小结.md`）。

## 快速运行

```bash
python main.py      # 运行 CLI 演示（装备 + 任务流程）
python -m pytest    # 运行单元测试（装备 / 任务 / 存档闭环）
```

## 目录结构

```
copilot-demo/
├── models.py    # 数据模型（Player / Item / Quest / Slot）——被其他文件引用
├── storage.py   # 持久化层：读写 JSON，import models
├── service.py   # 业务逻辑层：组合 models + storage
├── main.py      # 入口，命令行演示
└── data/
    ├── items.json
    └── quests.json
```

依赖方向：`main → service → storage/models`，`service → models`。

## 在 VS Code 里打开

1. 用 VS Code 打开 `copilot-demo` 文件夹（File > Open Folder）。
2. 确认左侧有 GitHub Copilot Chat 图标，或按 `Ctrl+I` / `Ctrl+Shift+I` 打开对话。
3. 右键对话面板选择首发模型，把上下文切到当前文件夹。

## 推荐的测试提示词（由易到难）

### 跨文件理解（重点）
- “在 `service.py` 里，给 `Player`（定义在 `models.py`）加一个 `level` 字段，并在 `main.py` 里打印出来。”
  —— 要求 Copilot 同时理解三个文件。
- “`storage.py` 里的 `save_player` 把装备序列化成了名字字符串。帮我改成直接存 `Item` 对象。注意保持 `models.py` 不变。”
  —— 考验它是否读懂跨文件的数据流。
- “为什么 `main.py` 里玩家能完成任务并把木剑交了，但木剑仍然留在背包里？帮我保持一致。”
  —— 一个非语法 bug，看它能否跨文件定位逻辑。

验证结果时还应确认：
- `Player.level` 在 `models.py`、`service.py` 和 `main.py` 中的定义、更新与输出保持一致；
- 装备的保存格式与加载逻辑匹配，并且没有修改 `models.py`；
- 任务交付后，任务状态与玩家背包状态保持一致，木剑不会重复保留。

### 自然语言生成代码（基础）
- “在 `service.py` 新增一个 `drop_item(player, item_name)` 方法，把指定物品从背包移除；若背包里没有则不报错，返回 False。”
- “给 `main.py` 加一个交互：输入 `g 物品名` 拾取、`e 物品名` 装备、`q` 退出。”

## 判定标准
- 生成的代码能直接粘贴运行（`python main.py` 不报错）。
- 提到跨文件内容时能引用正确的类名/字段/文件路径，而不是自己瞎编。
- 修改一个文件时，不会破坏其余文件的依赖。

> 提示：可用 `ctrl+z` 撤销 Copilot 的改动来反复测试。