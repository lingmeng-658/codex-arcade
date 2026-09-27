# 🎮 Codex Arcade

**Codex 干活，你先玩会儿。**

发送任务 → 小游戏弹出 → Codex 完成 → 回去干活。

[English](README.md)

![Codex Arcade 演示](assets/demo.gif)

Codex Arcade 是给 Codex Desktop 准备的本地小游戏伴侣。Codex 正在处理任务时，它会自动弹出一局轻量小游戏；任务结束或中断时，显示一句收尾提示后自动关闭。

> 当前主要测试环境：**Windows + Codex Desktop**。

## 游戏

贪吃蛇 · 躲避 · 瞄准训练 · 打砖块 · 乒乓

五个游戏都刻意做得很轻：几秒就能开始，想玩几十秒或几分钟都行，Codex 干完时被打断也不会难受。

![Codex Arcade 截图](assets/screenshot.png)

## 安装

需要：Windows、带 tkinter 的 Python 3.10+、Codex Desktop。

```bat
python install.py
```

或：

```bat
py -3 install.py
```

安装脚本会把运行文件复制到 `%LOCALAPPDATA%\CodexArcade\app`，备份 `~\.codex\hooks.json`，再安全合并 Codex Arcade 的 hooks，不会覆盖未知字段或已有 hooks。

**安装后还需要一步：**前往 **Codex Desktop → 设置 → 钩子（Hooks）**，审核并允许 Codex Arcade 新增的 hooks。

## 怎么用

- 给 Codex 发送任务；约两秒后，如果 Codex 仍在工作，Arcade 才会弹出。
- 自动启动时随机选择一个游戏。
- 首页可以手动选游戏、查看统计与成就、切换 English / 简体中文。
- Codex Stop 或 Interrupt 时，会显示短暂的“回来上班”提示，然后自动关闭。

### 快捷键

| 按键 | 功能 |
| --- | --- |
| `P` / `Space` | 暂停 / 继续 |
| `R` | 重开当前游戏 |
| `Tab` / `G` | 返回游戏列表 |
| `N` | 随机切换到另一个游戏 |
| `Esc` | 关闭 Arcade |

贪吃蛇、躲避使用 WASD / 方向键；瞄准训练使用鼠标。

也可以手动启动：

```bat
start_arcade.cmd
```

## 统计与成就

统计页面会记录：

- 今日摸鱼时间与累计游玩时间
- Codex 完成 / 等待相关统计
- 五个游戏各自的最佳成绩
- 8 个轻量成就

所有数据都只保存在本机。

## 隐私

Codex Arcade 不上传任何内容，也不会读取或发送 prompt、代码、项目数据或统计信息。本地状态保存在：

```text
%LOCALAPPDATA%\CodexArcade
```

## 卸载

```bat
python uninstall.py
```

默认保留统计数据；如需一并删除：

```bat
python uninstall.py --delete-data
```

卸载只会移除带 Codex Arcade 标记的 hooks，不会动其他 hooks。

## 开发验证

```bat
python -m unittest discover -s tests -v
python install.py --dry-run
```

## 许可证

MIT，见 [LICENSE](LICENSE)。
