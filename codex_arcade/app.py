import json
import logging
import os
import random
import time
import tkinter as tk
from pathlib import Path

from .games import GAMES
from .i18n import saved_or_system_language, text
from .stats import StatsStore, atomic_json, local_dir

WIDTH, HEIGHT = 360, 410
LOGGER = logging.getLogger(__name__)
SHORTCUT_BINDTAG = "CodexArcadeShortcuts"


def session_path() -> Path: return local_dir() / "session.json"


def read_session() -> dict:
    try: return json.loads(session_path().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return {}


class Arcade:
    def __init__(self, token: str | None = None, workspace: str = ""):
        self.token, self.workspace, self.closed, self.finishing = token, workspace, False, False
        self.game_after_id = self.session_after_id = self.close_after_id = None
        self.game_generation, self.game_started_at, self.round_elapsed, self.round_settled = 0, None, 0.0, False
        self.round_historical_best, self.round_metric, self.stats_finished = 0, None, False
        self.runtime_state, self.game = "playing", None
        self.store = StatsStore(); self.language = saved_or_system_language(self.store.language()); self.store.start_session()
        self.root = tk.Tk(); self.root.title("Codex Arcade"); self.root.geometry(f"{WIDTH}x{HEIGHT}"); self.root.resizable(False, False); self.root.configure(bg="#111318")
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="#111318", highlightthickness=0); self.canvas.pack()
        self.root.protocol("WM_DELETE_WINDOW", self.close); self.bind_shortcuts(); self.canvas.bind("<Button-1>", self.click)
        self.home(); self.show_unlocked(self.store.last_unlocked)
        if token: self.start_game(random.choice(list(GAMES)))
        self.root.after(200, self.focus_once); self.schedule_session(100, self.watch_session)

    def is_closing(self): return self.closed or self.finishing or self.runtime_state == "closing"
    def focus_once(self):
        if not self.is_closing(): self.root.deiconify(); self.root.lift(); self.root.focus_force(); self.canvas.focus_set()
    def bind_shortcuts(self):
        self.root.bind_class(SHORTCUT_BINDTAG, "<KeyPress>", lambda event: self.on_key(event, True), add="+")
        self.root.bind_class(SHORTCUT_BINDTAG, "<KeyRelease>", lambda event: self.on_key(event, False), add="+")
        for widget in (self.root, self.canvas):
            tags = widget.bindtags()
            if SHORTCUT_BINDTAG not in tags:
                widget.bindtags((SHORTCUT_BINDTAG,) + tags)
    def schedule_session(self, delay, callback):
        if not self.is_closing(): self.session_after_id = self.root.after(delay, callback)
    def schedule_game(self, delay, generation):
        if not self.is_closing() and self.runtime_state == "playing": self.game_after_id = self.root.after(delay, lambda: self.tick(generation))
    def cancel_game_tick(self):
        self.game_generation += 1
        if self.game_after_id:
            try: self.root.after_cancel(self.game_after_id)
            except tk.TclError: pass
        self.game_after_id = None

    def t(self, key): return text(key, self.language)
    def button(self, label, x, y, callback, width=150):
        ident = self.canvas.create_rectangle(x, y, x+width, y+30, fill="#202733", outline="#3a4657", tags=("button",))
        self.canvas.create_text(x+width/2, y+15, text=label, fill="#e6edf7", font=("Segoe UI", 9, "bold"), tags=("button",)); self.canvas.tag_bind(ident, "<Button-1>", lambda _e: callback())
    def header(self, game=False):
        self.canvas.delete("all"); self.canvas.create_text(12, 14, anchor="w", text="CODEX ARCADE", fill="#f1f5f9", font=("Segoe UI", 13, "bold"))
        if game:
            self.button(self.t("games"), 190, 4, self.return_to_games, 68); self.button(self.t("random_next"), 264, 4, self.start_random_game, 82)
        else: self.canvas.create_text(12, 34, anchor="w", text=self.t("working"), fill="#8592a3", font=("Segoe UI", 9))
    def controls(self): return self.t("game_controls")
    def draw_hud(self):
        if not self.game: return
        self.canvas.delete("hud"); data = self.store.load(); best = data["games"].get(self.game_name, {}).get("best", 0)
        best_text = format_time(best) if self.game_name == "dodge" else str(best)
        self.canvas.create_text(12, 48, anchor="w", text=f"{self.t('best')}: {best_text}", fill="#aab8cc", font=("Segoe UI", 9), tags="hud")
        self.canvas.create_text(12, HEIGHT-12, anchor="w", text=self.controls(), fill="#738094", font=("Segoe UI", 8), tags="hud")

    def home(self):
        self.game = None; self.header(); data = self.store.load(); choices = [("random", "random"), ("snake", "snake"), ("dodge", "dodge"), ("aim", "aim"), ("breakout", "breakout"), ("pong", "pong")]
        for i, (key, label) in enumerate(choices):
            best = "" if key == "random" else f" · {self.t('best')} {format_time(data['games'][key]['best']) if key == 'dodge' else data['games'][key]['best']}"
            self.button(self.t(label) + best, 20+(i % 2)*165, 62+(i // 2)*48, (self.start_random_game if key == "random" else lambda k=key: self.start_game(k)), 155)
        self.button(self.t("stats"), 20, 215, self.show_stats); self.button("中文 / English", 185, 215, self.toggle_language)
    def show_unlocked(self, achievement_ids):
        if not achievement_ids: return
        achievement_id = achievement_ids[-1]
        self.canvas.delete("achievement")
        self.canvas.create_text(WIDTH/2, HEIGHT-28, text=f"{self.t('achievement_unlocked')}: {self.t('achievement_' + achievement_id)}", fill="#8ee6a0", font=("Segoe UI", 9, "bold"), tags="achievement")
        self.root.after(1800, lambda: self.canvas.delete("achievement") if not self.closed else None)

    def toggle_language(self): self.language = "zh-CN" if self.language == "en" else "en"; self.store.set_language(self.language); self.home()
    def show_stats(self):
        self.header(); data = self.store.load(); today = data["today"].get(__import__("datetime").date.today().isoformat(), 0)
        metrics = [("today", format_time(today)), ("total", format_time(data["total_seconds"])), ("tasks", data["tasks_completed"]), ("longest_wait", format_time(data["longest_wait_seconds"])), ("forced_ends", data["forced_ends"]), ("snake_best", data["games"]["snake"]["best"]), ("dodge_best", format_time(data["games"]["dodge"]["best"])), ("aim_best", data["games"]["aim"]["best"]), ("breakout_best", data["games"]["breakout"]["best"]), ("pong_best", data["games"]["pong"]["best"])]
        for i, (label, value) in enumerate(metrics):
            x, y = 16 + (i % 2) * 176, 58 + (i // 2) * 19
            self.canvas.create_text(x, y, anchor="w", text=f"{self.t(label)}: {value}", fill="#d7e1ee", font=("Segoe UI", 8))
        self.canvas.create_text(16, 164, anchor="w", text=self.t("achievements"), fill="#ffcf70", font=("Segoe UI", 10, "bold"))
        for i, achievement_id in enumerate(("first_game", "ten_minutes", "touch_grass", "still_thinking", "busy_day", "so_close", "multitasker", "arcade_tour")):
            marker = "✓" if achievement_id in data["achievements"] else "□"
            self.canvas.create_text(16, 181 + i * 17, anchor="w", text=f"{marker} {self.t('achievement_' + achievement_id)}", fill="#8ee6a0" if marker == "✓" else "#8592a3", font=("Segoe UI", 8, "bold"))
        self.button(self.t("home"), 20, 330, self.home)

    def effective_elapsed(self):
        return self.round_elapsed + (time.monotonic() - self.game_started_at if self.runtime_state == "playing" and self.game_started_at is not None else 0.0)
    def settle_round(self):
        if not self.game or self.round_settled: return
        elapsed = self.effective_elapsed(); self.round_metric = self.game.best_value(elapsed); self.store.record_game(self.game_name, self.game.score, elapsed, self.round_metric); self.show_unlocked(getattr(self.store, "last_unlocked", ())); self.round_settled = True; self.round_elapsed = elapsed; self.game_started_at = None
    def clear_game(self): self.cancel_game_tick(); self.game = None; self.game_started_at = None
    def stop_current_game(self): self.settle_round(); self.clear_game()
    def start_game(self, name):
        if self.is_closing(): return
        if self.game: self.stop_current_game()
        self.runtime_state, self.round_elapsed, self.round_settled = "playing", 0.0, False; self.header(True); self.game_name = name; self.round_historical_best = self.store.load()["games"][name]["best"]; self.round_metric = None; self.game = GAMES[name](self.canvas, WIDTH, HEIGHT); self.game_started_at = time.monotonic(); self.game_generation += 1; self.tick(self.game_generation)
    def restart_current_game(self):
        if self.is_closing() or not self.game: return
        name = self.game_name; self.stop_current_game(); self.start_game(name)
    def return_to_games(self):
        if self.is_closing(): return
        self.stop_current_game(); self.home()
    def start_random_game(self):
        if self.is_closing(): return
        current = self.game_name if self.game else None; choices = [name for name in GAMES if name != current]
        if self.game: self.stop_current_game()
        self.start_game(random.choice(choices or list(GAMES)))
    def pause_or_resume(self):
        if self.is_closing() or not self.game or self.runtime_state == "game_over": return
        if self.runtime_state == "playing": self.round_elapsed = self.effective_elapsed(); self.game_started_at = None; self.runtime_state = "paused"; self.cancel_game_tick(); self.canvas.create_text(WIDTH/2, HEIGHT/2, text=self.t("paused"), fill="#ffcf70", font=("Segoe UI", 20, "bold"), tags="pause")
        else: self.canvas.delete("pause"); self.runtime_state = "playing"; self.game_started_at = time.monotonic(); self.game_generation += 1; self.tick(self.game_generation)
    def show_game_over(self):
        self.settle_round(); self.runtime_state = "game_over"; self.cancel_game_tick(); self.canvas.create_rectangle(32, 145, WIDTH-32, 265, fill="#111318", outline="#3a4657", tags="over"); self.canvas.create_text(WIDTH/2, 172, text=self.t("game_over"), fill="#ffcf70", font=("Segoe UI", 16, "bold"), tags="over"); self.button(self.t("restart"), 48, 205, self.restart_current_game, 76); self.button(self.t("games"), 142, 205, self.return_to_games, 76); self.button(self.t("random_next"), 236, 205, self.start_random_game, 76)
    def tick(self, generation):
        if self.is_closing() or generation != self.game_generation or not self.game or self.runtime_state != "playing": return
        self.game.update(); self.game.draw(); self.draw_hud()
        if self.game.ended: self.show_game_over()
        else: self.schedule_game(self.game.tick_ms, generation)
    def click(self, event):
        self.canvas.focus_set()
        if self.game and self.runtime_state == "playing" and hasattr(self.game, "click"): self.game.click(event); self.game.draw(); self.draw_hud()
    def on_key(self, event, down):
        key = event.keysym.lower()
        LOGGER.debug("central shortcut keysym=%s down=%s", event.keysym, down)
        if key == "escape" and down: self.close(); return "break"
        if not down:
            if self.game and self.runtime_state == "playing": self.game.key(key, False)
            return "break"
        if key in ("p", "space"): self.pause_or_resume(); return "break"
        if key == "r": self.restart_current_game(); return "break"
        if key in ("tab", "g"): self.return_to_games(); return "break"
        if key == "n": self.start_random_game(); return "break"
        if self.game and self.runtime_state == "playing": self.game.key(key, True)
        return "break"
    def watch_session(self):
        if self.is_closing(): return
        session = read_session()
        if self.token and (session.get("token") != self.token or session.get("status") == "stop"): self.finish()
        else: self.schedule_session(100, self.watch_session)
    def finish(self):
        if self.is_closing(): return
        self.settle_round(); self.runtime_state = "closing"; self.finishing = True; self.cancel_game_tick()
        if self.session_after_id:
            try: self.root.after_cancel(self.session_after_id)
            except tk.TclError: pass
        unlocked = set(self.store.last_unlocked)
        if self.game and self.round_metric is not None and self.store.unlock_so_close(self.game_name, self.round_metric, self.round_historical_best): unlocked.update(self.store.last_unlocked)
        self.store.finish_arcade(True); self.stats_finished = True; unlocked.update(self.store.last_unlocked)
        self.canvas.delete("all"); self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#111318", outline=""); self.canvas.create_text(WIDTH/2, 170, text=self.t("finished"), fill="#ffcf70", font=("Segoe UI", 17, "bold")); self.canvas.create_text(WIDTH/2, 205, text=self.t("back"), fill="#f2f5f9", font=("Segoe UI", 13, "bold")); self.show_unlocked(tuple(sorted(unlocked))); self.close_after_id = self.root.after(1900 if unlocked else 750, self.close)
    def close(self):
        if self.closed: return
        self.closed = True; self.cancel_game_tick()
        for callback_id in (self.session_after_id, self.close_after_id):
            if callback_id:
                try: self.root.after_cancel(callback_id)
                except tk.TclError: pass
        self.settle_round()
        if not self.stats_finished: self.store.finish_arcade(self.finishing)
        if self.token:
            session = read_session()
            if session.get("token") == self.token:
                try: session_path().unlink()
                except OSError: pass
        try: self.root.destroy()
        except tk.TclError: pass
    def run(self): self.root.mainloop()


def format_time(seconds):
    seconds = max(0, int(seconds)); return f"{seconds//60}m {seconds%60:02d}s"


def launch(token=None, workspace=""):
    if token:
        session = read_session()
        if session.get("token") != token or session.get("status") != "running": return
        session["pid"] = os.getpid(); atomic_json(session_path(), session)
    try:
        Arcade(token, workspace).run()
    except Exception:
        if token and read_session().get("token") == token:
            try: session_path().unlink()
            except OSError: pass
        raise
