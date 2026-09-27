# Codex Arcade v0.1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the temporary Snake hook demo into a lightweight, Windows-ready Codex Arcade release.

**Architecture:** A small Tkinter application owns window lifecycle and game selection. Pure standard-library modules provide language strings, JSON statistics, and non-destructive hook installation; `.cmd` launchers keep hook commands quoting-safe.

**Tech Stack:** Python 3 standard library, tkinter, unittest, Windows cmd.

**Spec:** User request in this task.

## Global Constraints

- Windows + Codex Desktop are the primary supported environment.
- Use only Python standard library and tkinter.
- Never overwrite unrelated Codex hook configuration.
- Store local statistics only in `%LOCALAPPDATA%\CodexArcade`.
- Do not commit, push, create a GitHub repository, or change Echo.

## Review Focus

- Existing hook matchers remain byte-for-byte present after install/uninstall.
- A prompt that stops before the two-second delay never shows a window.
- A stale lock does not prevent a future game from launching.
- Statistics gracefully recover from absent or malformed JSON.
- Stop and Interrupt use a short in-window finish sequence rather than force-killing the process.

---

### Task 1: Testable persistence, translation, and hook merge

**Files:**
- Create: `tests/test_stats.py`, `tests/test_i18n.py`, `tests/test_hooks.py`
- Create: `codex_arcade/stats.py`, `codex_arcade/i18n.py`, `codex_arcade/hooks.py`

- [ ] Write failing unit tests for default stats, best-score persistence, language persistence, and safe hook add/remove.
- [ ] Run the focused tests and confirm they fail because the package is absent.
- [ ] Implement the pure modules and rerun tests.

### Task 2: Tkinter arcade and five games

**Files:**
- Create: `codex_arcade/app.py`, `codex_arcade/games/*.py`, `codex_arcade/__main__.py`
- Modify: `tests/test_stats.py`

- [ ] Add a failing test for work-session accounting and game-score recording.
- [ ] Implement a small shared game canvas API and Snake, Dodge, Aim, Breakout, Pong implementations.
- [ ] Run the suite and manually smoke-test each game entry point.

### Task 3: Launch control and install lifecycle

**Files:**
- Create: `start.py`, `stop.py`, `install.py`, `uninstall.py`, `start_arcade.cmd`, `stop_arcade.cmd`
- Create: `tests/test_install.py`

- [ ] Add failing tests for installer dry-run and hook merge/removal in a temporary home folder.
- [ ] Implement delay-aware singleton startup, graceful finish signalling, and installer/uninstaller.
- [ ] Run the suite and dry-run lifecycle commands.

### Task 4: Release assets and final verification

**Files:**
- Replace: `README.md`, `hooks.example.json`
- Create: `README.zh-CN.md`, `LICENSE`, `.gitignore`, `requirements.txt`, `CHANGELOG.md`

- [ ] Document Windows setup, hook approval, privacy, use, uninstall, and verification limits.
- [ ] Compile modules, run all tests, exercise all game launch routes, and inspect the release file set.
