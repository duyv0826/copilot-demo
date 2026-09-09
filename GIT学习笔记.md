# Git 新手实战笔记

> 基于 copilot-demo 项目的亲身操作整理，每一步都真实执行过，可直接照着练。
> 环境：Windows + PowerShell。分支策略：main（默认）。

## 0. 心态：git 在做什么

git 是给项目拍"快照"的工具。每次 `commit` = 保存那一刻所有文件的状态，之后可以：
- 回看历史（`git log`）
- 对比改动（`git diff`）
- 回到过去（`restore` / `revert`）
- 和远程仓库同步（`push` / `pull`）

## 1. 初始化与首次提交

```bash
git init              # 在当前文件夹建仓库
git branch -M main    # 默认分支命名为 main
git add .             # 把所有文件放"暂存区"（准备提交）
git commit -m "Initial commit"   # 存成第一个快照
```

- `.gitignore` 用来排除不该提交的东西（缓存、临时/运行生成文件），例如：
  ```
  __pycache__/
  .pytest_cache/
  *.pyc
  data/player_save.json
  ```

## 2. 日常循环（90% 的操作）

```bash
git status          # 看哪些文件改了/删了/新增了
git diff            # 看具体改了什么内容
git add <文件>       # 把改动放进暂存区（可用 git add . 全加）
git commit -m "说明" # 存成一次快照
git log --oneline   # 看提交历史（一行一条）
git status -s       # 精简状态；输出为空 = 工作区干净
```

### 提交信息前缀（推荐规范，历史更好读）
| 前缀 | 含义 |
|------|------|
| `feat:` | 新增功能 |
| `docs:` | 文档、注释、README |
| `fix:`  | 修 bug |
| `refactor:` | 重构（不动功能）|

例如：`docs: 完善 README`、`feat: 新增 drop_item 功能`、`fix: 修复存档重复结算`。

## 3. 撤销与回退（安全版，不删历史）

| 场景 | 命令 | 效果 |
|------|------|------|
| 改了但还没 commit，想丢掉这个改动 | `git restore <文件>` | 文件回到上次提交的样子 |
| 已经 commit 了，想反悔 | `git revert HEAD` | 新增一条"反悔提交"，抵消那次改动，但历史保留 |

> **新手不要用** `git reset --hard`：它会直接抹掉提交，无法恢复。
> 我也因此给"已提交"命令配了护栏，避免误删。日常用 `restore` + `revert` 足够。

## 4. 和远程（GitHub）同步

### 连接远程
```bash
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
```

### 推送（本地 → 远程）
```bash
git push -u origin main   # -u = 记住关联，之后只需 git push
```

### 拉取（远程 → 本地）
```bash
git fetch          # 只看远程有没有新提交（不合并）
git status -sb     # 如果显示 [behind N]，说明远程领先 N 个提交
git pull           # 把远程新提交拉下来并合并
```

`fetch` 和 `pull` 的区别：fetch 只"看"，pull = fetch + 自动合并。

## 5. 冲突（最劝退，但练过就不怕）

**什么时候会冲突**：你改了文件 A 的同时，别人（或网页端）也改了文件 A 的同一行。git 无法替你做决定 → 停下等你拍板。

**流程**：
```bash
git pull / git merge origin/main
# 报 CONFLICT (content) 冲突，停在半途

# ① 打开冲突文件，看到这样的标记：
# <<<<<<< HEAD
# 我这边（本地）的内容
# =======
# 远程的内容
# >>>>>>> origin/main

# ② 删掉三行标记 <<<<<<<  =======  >>>>>>>，只留你确实想要的那份内容
# ③ 告诉 git 你解决了：
git add <文件>
# ④ 完成合并提交：
git commit
```

**关键认知**：冲突不是 bug，是 git 在让你决定"到底留哪边"。谁都没做错，只是同一行改了两次。

## 6. 我踩过的坑 / 关键提醒

1. **网络不稳**：国内直连 GitHub 可能 `Connection reset` / `443 超时`。可用 v2rayN 等代理软件的 **TUN/全局代理** 让 git 直连，或用 SSH 方式连接。
   - 验证连通：`Test-NetConnection github.com -Port 443` → `True` 表示通。
   - 若配了代理工具，可能需要：`git config --global http.proxy http://127.0.0.1:<端口>`
2. **不要拿 System32 当仓库目录**：`git` 命令必须在仓库文件夹内运行，否则报 `not a git repository`。
3. **网页端也可以改代码**：GitHub 网页能直接编辑/新建文件并 commit——这段"远程改动"必须用 `git pull` 才能同步回本地。
4. **push 前用 `git status -sb` 看 `[ahead] / [behind]`**：ahead = 本地领先、behind = 本地落后，是判断该 push 还是 pull 的信号。

## 7. 命令速查表

| 命令 | 作用 |
|------|------|
| `git init` | 初始化仓库 |
| `git status [-s]` | 看状态 / 精简状态 |
| `git add <文件>` | 加入暂存区 |
| `git commit -m "..."` | 提交 |
| `git log --oneline` | 提交历史 |
| `git diff` | 内容差异 |
| `git restore <文件>` | 丢弃未提交改动 |
| `git revert HEAD` | 撤销一次已提交的改动 |
| `git branch -M main` | 分支命名 |
| `git branch -D <名>` | 删除分支 |
| `git remote add origin <url>` | 连远程 |
| `git push [-u origin main]` | 推送 |
| `git fetch` | 看远程更新 |
| `git pull` | 拉取并合并 |
| `git merge origin/main` | 合并远程分支 |

## 8. 下一步可学

- 分支工作流（feature / dev / main）
- `git log --graph` 看分支图
- `git stash` 临时藏起未完成改动
- GitHub 的 PR（Pull Request）协作