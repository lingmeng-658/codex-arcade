import json
import os
import random
import time
import tkinter as tk
from pathlib import Path

from .games import GAMES
from .i18n import saved_or_system_language, text
from .stats import StatsStore, atomic_json, local_dir

WIDTH, HEIGHT = 360, 410


def session_path() -> Path: return local_dir() / "session.json"


def read_session() -> dict:
    try: return json.loads(session_path().read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError): return {}


class Arcade:
    def __init__(self, token: str | None = None, workspace: str = ""):
        self.token, self.workspace, self.closed, self.finishing = token, workspace, False, False
        self.game_after_id = self.session_after_id = self.close_after_id = None
        self.game_generation, self.game_started_at, self.round_elapsed, self.round_settled = 0, None, 0.0, False
        self.runtime_state, self.game = "playing", None
        self.store = StatsStore(); self.language = saved_or_system_language(self.store.language()); self.store.start_session()
        self.root = tk.Tk(); self.root.title("Codex Arcade"); self.root.geometry(f"{WIDTH}x{HEIGHT}"); self.root.resizable(False, False); self.root.configure(bg="#111318")
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg="#111318", highlightthickness=0); self.canvas.pack()
        self.root.protocol("WM_DELETE_WINDOW", self.close); self.root.bind("<KeyPress>", lambda e: self.on_key(e, True)); self.root.bind("<KeyRelease>", lambda e: self.on_key(e, False)); self.canvas.bind("<Button-1>", self.click)
        self.home()
        if token: self.start_game(random.choice(list(GAMES)))
        self.root.after(200, self.focus_once); self.schedule_session(100, self.watch_session)

    def is_closing(self): return self.closed or self.finishing or self.runtime_state == "closing"
    def focus_once(self):
        if not self.is_closing(): self.root.deiconify(); self.root.lift(); self.root.focus_force()
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
    def toggle_language(self): self.language = "zh-CN" if self.language == "en" else "en"; self.store.set_language(self.language); self.home()
    def show_stats(self):
        self.header(); data = self.store.load(); today = data["today"].get(__import__("datetime").date.today().isoformat(), 0); lines = [f"{self.t('today')}: {format_time(today)}", f"{self.t('tasks')}: {data['tasks_completed']}", f"{self.t('total')}: {format_time(data['total_seconds'])}"]
        for game in GAMES: lines.append(f"{self.t(game)} {self.t('best')}: {format_time(data['games'][game]['best']) if game == 'dodge' else data['games'][game]['best']}")
        for i, line in enumerate(lines): self.canvas.create_text(24, 70+i*31, anchor="w", text=line, fill="#d7e1ee", font=("Segoe UI", 11))
        self.button(self.t("home"), 20, 330, self.home)

    def effective_elapsed(self):
        return self.round_elapsed + (time.monotonic() - self.game_started_at if self.runtime_state == "playing" and self.game_started_at is not None else 0.0)
    def settle_round(self):
        if not self.game or self.round_settled: return
        elapsed = self.effective_elapsed(); self.store.record_game(self.game_name, self.game.score, elapsed, self.game.best_value(elapsed)); self.round_settled = True; self.round_elapsed = elapsed; self.game_started_at = None
    def clear_game(self): self.cancel_game_tick(); self.game = None; self.game_started_at = None
    def stop_current_game(self): self.settle_round(); self.clear_game()
    def start_game(self, name):
        if self.is_closing(): return
        if self.game: self.stop_current_game()
        self.runtime_state, self.round_elapsed, self.round_settled = "playing", 0.0, False; self.header(True); self.game_name = name; self.game = GAMES[name](self.canvas, WIDTH, HEIGHT); self.game_started_at = time.monotonic(); self.game_generation += 1; self.tick(self.game_generation)
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
        if self.game and self.runtime_state == "playing" and hasattr(self.game, "click"): self.game.click(event); self.game.draw(); self.draw_hud()
    def on_key(self, event, down):
        key = event.keysym.lower()
        if key == "escape" and down: self.close(); return
        if not down:
            if self.game and self.runtime_state == "playing": self.game.key(key, False)
            return
        if key in ("p", "space"): self.pause_or_resume(); return
        if key == "r": self.restart_current_game(); return
        if key in ("tab", "g"): self.return_to_games(); return
        if key == "n": self.start_random_game(); return
        if self.game and self.runtime_state == "playing": self.game.key(key, True)
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
        self.canvas.delete("all"); self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#111318", outline=""); self.canvas.create_text(WIDTH/2, 170, text=self.t("finished"), fill="#ffcf70", font=("Segoe UI", 17, "bold")); self.canvas.create_text(WIDTH/2, 205, text=self.t("back"), fill="#f2f5f9", font=("Segoe UI", 13, "bold")); self.close_after_id = self.root.after(750, self.close)
    def close(self):
        if self.closed: return
        self.closed = True; self.cancel_game_tick()
        for callback_id in (self.session_after_id, self.close_after_id):
            if callback_id:
                try: self.root.after_cancel(callback_id)
                except tk.TclError: pass
        self.settle_round(); self.store.finish_arcade(self.finishing)
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
