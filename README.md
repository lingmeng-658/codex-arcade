# 🎮 Codex Arcade

Your AI works. You play.

Prompt Codex → Game pops up → Codex finishes → Back to work.

Codex Arcade is a tiny, local Tkinter companion for Codex Desktop. While Codex works, it opens one quick game. When the task stops, it shows a short sign-off and closes.

> Primary test environment: **Windows + Codex Desktop**.

## Games

Snake, Dodge, Aim Trainer, Breakout, and Pong. All are intentionally lightweight: start instantly, score forever, and leave without regret.

## Install

Requirements: Windows, Python 3.10+ with tkinter, and Codex Desktop.

```bat
python install.py
```

or:

```bat
py -3 install.py
```

The installer copies the runtime into `%LOCALAPPDATA%\CodexArcade\app`, backs up `~\.codex\hooks.json`, then safely merges its three hooks. It does not replace unknown JSON fields or existing hooks.

**Important:** open **Codex Desktop → Settings → Hooks** and review/approve the new Codex Arcade hooks before first use.

## Use

- Send a prompt. After about two seconds, Arcade opens only if Codex is still working.
- The automatic game is random. The home screen lets you choose a game, view stats, and switch English/简体中文.
- Use WASD / arrow keys (or mouse for Aim). `Esc` closes Arcade.
- Stop or interrupt Codex to get the brief “back to work” ending.

Run it manually with:

```bat
start_arcade.cmd
```

## Privacy and local data

Codex Arcade uploads nothing. It never reads or sends prompts, code, or project data. Its state and statistics live only in `%LOCALAPPDATA%\CodexArcade`.

## Uninstall

```bat
python uninstall.py
```

Statistics are kept by default. To remove them too:

```bat
python uninstall.py --delete-data
```

Only hooks marked as Codex Arcade are removed; your other hooks remain intact.

## Development checks

```bat
python -m unittest discover -s tests -v
python install.py --dry-run
```

## License

MIT. See [LICENSE](LICENSE).
