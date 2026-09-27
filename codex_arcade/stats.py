import json
import os
import shutil
import tempfile
import time
from copy import deepcopy
from datetime import date
from pathlib import Path


GAMES = ("snake", "dodge", "aim", "breakout", "pong")


def local_dir() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", str(Path.home()))) / "CodexArcade"


def atomic_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=path.stem + ".", suffix=".tmp", dir=path.parent, text=True)
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class StatsStore:
    def __init__(self, path: Path | None = None):
        self.path = path or local_dir() / "stats.json"
        self.started_at: float | None = None
        self.session_games: set[str] = set()
        self.last_unlocked: tuple[str, ...] = ()

    def default(self) -> dict:
        return {
            "version": 2, "language": "", "total_seconds": 0.0, "today": {},
            "daily": {"date": date.today().isoformat(), "arcade_sessions": 0},
            "tasks_completed": 0, "forced_ends": 0, "longest_wait_seconds": 0.0,
            "games": {game: {"best": 0, "longest": 0.0} for game in GAMES},
            "played_games": [], "achievements": [],
        }

    def load(self) -> dict:
        if not self.path.exists():
            return self.default()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise json.JSONDecodeError("statistics must be an object", "", 0)
            original = deepcopy(data)
            base = self.default()
            base.update(data)
            if not isinstance(base["today"], dict):
                base["today"] = {}
            if not isinstance(base["games"], dict):
                base["games"] = {}
            for game in GAMES:
                details = base["games"].get(game, {})
                normalized = {"best": 0, "longest": 0.0}
                if isinstance(details, dict):
                    normalized.update(details)
                base["games"][game] = normalized
            if not isinstance(base.get("achievements"), list):
                base["achievements"] = []
            base["achievements"] = sorted(set(str(item) for item in base["achievements"]))
            if not isinstance(base.get("played_games"), list):
                base["played_games"] = []
            base["played_games"] = sorted(set(game for game in base["played_games"] if game in GAMES))
            daily = base.get("daily")
            if not isinstance(daily, dict):
                daily = {}
            base["daily"] = {
                "date": daily.get("date") if isinstance(daily.get("date"), str) else date.today().isoformat(),
                "arcade_sessions": max(0, int(daily.get("arcade_sessions", 0))),
            }
            base["version"] = 2
            if base != original:
                self.save(base)
            return base
        except (OSError, json.JSONDecodeError):
            backup = self.path.with_name(f"stats.corrupt-{int(time.time())}.json")
            try:
                shutil.copy2(self.path, backup)
            except OSError:
                pass
            return self.default()

    def save(self, data: dict) -> None:
        atomic_json(self.path, data)

    def _save_with_unlocks(self, data: dict, before: set[str]) -> dict:
        unlocked = set(data["achievements"]) - before
        data["achievements"] = sorted(set(data["achievements"]))
        self.last_unlocked = tuple(sorted(unlocked))
        self.save(data)
        return data

    def _reset_daily_if_needed(self, data: dict) -> None:
        today = date.today().isoformat()
        if data["daily"]["date"] != today:
            data["daily"] = {"date": today, "arcade_sessions": 0}

    def _evaluate_play_achievements(self, data: dict) -> None:
        achievements = set(data["achievements"])
        if data["total_seconds"] >= 600:
            achievements.add("ten_minutes")
        if data["total_seconds"] >= 3600:
            achievements.add("touch_grass")
        if len(data["played_games"]) == len(GAMES):
            achievements.add("arcade_tour")
        if len(self.session_games) >= 3:
            achievements.add("multitasker")
        data["achievements"] = sorted(achievements)

    def language(self) -> str:
        return self.load().get("language") or ""

    def set_language(self, language: str) -> None:
        data = self.load()
        data["language"] = language
        self.save(data)

    def _record_game(self, data: dict, game: str, score: int, elapsed: float, best_value: float | None = None) -> None:
        duration = max(0.0, elapsed)
        today = date.today().isoformat()
        data["total_seconds"] += duration
        data["today"][today] = data["today"].get(today, 0.0) + duration
        details = data["games"].setdefault(game, {"best": 0, "longest": 0.0})
        details["best"] = max(details["best"], best_value if best_value is not None else int(score))
        details["longest"] = max(details["longest"], duration)
        data["played_games"] = sorted(set(data["played_games"]) | {game})
        self.session_games.add(game)
        achievements = set(data["achievements"])
        achievements.add("first_game")
        data["achievements"] = sorted(achievements)
        self._evaluate_play_achievements(data)

    def record_game(self, game: str, score: int, elapsed: float, best_value: float | None = None) -> dict:
        data = self.load()
        before = set(data["achievements"])
        self._record_game(data, game, score, elapsed, best_value)
        return self._save_with_unlocks(data, before)

    def start_session(self) -> dict:
        self.started_at = time.monotonic()
        self.session_games = set()
        data = self.load()
        before = set(data["achievements"])
        self._reset_daily_if_needed(data)
        data["daily"]["arcade_sessions"] += 1
        if data["daily"]["arcade_sessions"] >= 20:
            data["achievements"] = sorted(set(data["achievements"]) | {"busy_day"})
        return self._save_with_unlocks(data, before)

    def finish_arcade(self, forced: bool, elapsed: float | None = None) -> dict:
        duration = max(0.0, elapsed if elapsed is not None else time.monotonic() - (self.started_at or time.monotonic()))
        data = self.load()
        before = set(data["achievements"])
        data["tasks_completed"] += int(forced)
        data["forced_ends"] += int(forced)
        data["longest_wait_seconds"] = max(data["longest_wait_seconds"], duration)
        if duration >= 300:
            data["achievements"] = sorted(set(data["achievements"]) | {"still_thinking"})
        return self._save_with_unlocks(data, before)

    def finish_session(self, game: str, score: int, forced: bool, elapsed: float | None = None) -> dict:
        duration = max(0.0, elapsed if elapsed is not None else time.monotonic() - (self.started_at or time.monotonic()))
        self.record_game(game, score, duration)
        return self.finish_arcade(forced, duration)

    def unlock_so_close(self, game: str, value: float, historical_best: float) -> bool:
        if game not in GAMES or historical_best <= 0 or value < historical_best * 0.9 or value > historical_best:
            self.last_unlocked = ()
            return False
        data = self.load()
        before = set(data["achievements"])
        data["achievements"] = sorted(before | {"so_close"})
        if set(data["achievements"]) == before:
            self.last_unlocked = ()
            return True
        self._save_with_unlocks(data, before)
        return True
