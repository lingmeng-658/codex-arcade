# 🎮 Codex Arcade

Codex 干活，你先玩会儿。

发送任务 → 小游戏弹出 → Codex 完成 → 回去干活。

Codex Arcade 是给 Codex Desktop 准备的本地小工具。Codex 正在处理任务时，它会弹出一局轻量小游戏；任务结束或中断时，显示一句收尾提示后自动关闭。

> 当前主要测试环境：**Windows + Codex Desktop**。

## 有什么

贪吃蛇、躲避、瞄准训练、打砖块、乒乓。每局一眼懂，随时可停，不会让人陷入“这一局还没打完”。

## 安装

需要：Windows、带 tkinter 的 Python 3.10+、Codex Desktop。

```bat
python install.py
```

或：

```bat
py -3 install.py
```

安装脚本会把运行文件复制到 `%LOCALAPPDATA%\CodexArcade\app`，备份 `~\.codex\hooks.json`，并安全合并三个 hook；不会覆盖未知字段或已有 hook。

**首次使用必须前往 Codex Desktop → Settings → Hooks，审核并允许 Codex Arcade 新增的 hook。**

## 怎么用

- 发送任务后约两秒，如果 Codex 还在工作，小游戏会自动出现。
- 自动启动时随机选游戏；首页可手选游戏、查看统计、切换 English / 简体中文。
- 使用 WASD / 方向键；瞄准训练使用鼠标；按 `Esc` 退出。
- Codex Stop 或 Interrupt 时，会先显示短暂结束提示，再安全退出。

手动启动：

```bat
start_arcade.cmd
```

## 隐私

所有数据只保存在 `%LOCALAPPDATA%\CodexArcade`。不会上传 prompt、代码、项目数据或统计信息。

## 卸载

```bat
python uninstall.py
```

默认保留统计；如需一并删除：

```bat
python uninstall.py --delete-data
```

卸载只移除带 Codex Arcade 标记的 hook，不会动你的其他 hook。

## 开发验证

```bat
python -m unittest discover -s tests -v
python install.py --dry-run
```

## 许可证

MIT，见 [LICENSE](LICENSE)。
