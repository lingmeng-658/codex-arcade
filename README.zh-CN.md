# 🎮 Codex Arcade

**Codex 干活，你先玩会儿。**

发送任务 → 小游戏弹出 → Codex 完成 → 回去干活。

[English](README.md)

![Codex Arcade 演示](assets/demo.gif)

## 为什么做这个？

我发现自己等 Codex 跑任务的时候，经常顺手拿起手机，结果 Codex 早就跑完了，我还在刷。

所以做了这个小玩意：

**Codex 开始工作 → 自动弹游戏 → Codex 完成 → 游戏自动关闭。**

## 有什么？

- 🎮 贪吃蛇、躲避、瞄准训练、打砖块、乒乓
- 🔀 随时重开或切换游戏
- 🏆 本地统计、最高分和 8 个成就
- 🌐 简体中文 / English
- 🔒 完全本地，不上传 prompt、代码或项目内容

![Codex Arcade 截图](assets/screenshot.png)

## 安装

需要 **Windows**、**Python 3.10+（带 tkinter）** 和 **Codex Desktop**。

```bat
git clone https://github.com/lingmeng-658/codex-arcade.git
cd codex-arcade
python install.py
```

然后打开：

**Codex Desktop → 设置 → 钩子（Hooks）**

批准 Codex Arcade 新增的 hooks。

就这样。之后给 Codex 发任务，如果它两秒后还在工作，Arcade 就会自动弹出来。

## 快捷键

| 按键 | 功能 |
| --- | --- |
| `P` / `Space` | 暂停 / 继续 |
| `R` | 重开 |
| `N` | 随机换一个游戏 |
| `Tab` / `G` | 游戏列表 |
| `Esc` | 关闭 Arcade |

贪吃蛇、躲避使用 WASD / 方向键；瞄准训练使用鼠标。

## 隐私

所有东西都留在本机。

Codex Arcade **不会读取或上传**你的 prompt、代码或项目文件；运行数据和统计保存在 `%LOCALAPPDATA%\CodexArcade`。

## 卸载

```bat
python uninstall.py
```

连本地统计一起删除：

```bat
python uninstall.py --delete-data
```

## 许可证

MIT，见 [LICENSE](LICENSE)。
