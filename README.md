# 🎮 Codex Arcade

**Your AI works. You play.**

Prompt Codex → Game pops up → Codex finishes → Back to work.

[简体中文](README.zh-CN.md)

![Codex Arcade Demo](assets/demo.gif)

Codex Arcade is a tiny, local Tkinter companion for Codex Desktop. While Codex works, it opens a quick game. When the task stops, Arcade shows a short sign-off and closes automatically.

> Primary test environment: **Windows + Codex Desktop**.

## Games

Snake · Dodge · Aim Trainer · Breakout · Pong

All five are intentionally lightweight: start instantly, play for a few seconds or a few minutes, and leave without regret when Codex finishes.

![Codex Arcade Screenshot](assets/screenshot.png)

## Install

Requirements: Windows, Python 3.10+ with tkinter, and Codex Desktop.

```bat
python install.py
```

or:

```bat
py -3 install.py
```

The installer copies the runtime into `%LOCALAPPDATA%\CodexArcade\app`, backs up `~\.codex\hooks.json`, then safely merges its hooks without replacing unknown fields or existing hooks.

**After installation:** open **Codex Desktop → Settings → Hooks** and review/approve the new Codex Arcade hooks.

## Use

- Send a prompt. After about two seconds, Arcade opens only if Codex is still working.
- Automatic launches choose a random game.
- The home screen lets you choose a game, view Stats & Achievements, and switch English / 简体中文.
- When Codex stops or is interrupted, Arcade shows the brief “back to work” ending and closes.

### Controls

| Key | Action |
| --- | --- |
| `P` / `Space` | Pause / resume |
| `R` | Restart current game |
| `Tab` / `G` | Return to Games |
| `N` | Play a different random game |
| `Esc` | Close Arcade |

Snake and Dodge use WASD / arrow keys. Aim Trainer uses the mouse.

Run manually with:

```bat
start_arcade.cmd
```

## Stats & Achievements

The Stats screen keeps:

- Arcade time today and total play time
- Codex completion / wait statistics
- Best result for each game
- Eight lightweight achievements

All statistics stay local.

## Privacy

Codex Arcade uploads nothing. It does not read or send prompts, code, project data, or statistics. Local state lives in:

```text
%LOCALAPPDATA%\CodexArcade
```

## Uninstall

```bat
python uninstall.py
```

Statistics are kept by default. To remove them too:

```bat
python uninstall.py --delete-data
```

Only hooks marked as Codex Arcade are removed; other hooks are preserved.

## Development checks

```bat
python -m unittest discover -s tests -v
python install.py --dry-run
```

## License

MIT. See [LICENSE](LICENSE).
