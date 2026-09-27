import json
import os
import shutil
import tempfile
import time
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

    def default(self) -> dict:
        return {"version": 1, "language": "", "total_seconds": 0.0, "today": {},
                "tasks_completed": 0, "forced_ends": 0, "longest_wait_seconds": 0.0,
                "games": {game: {"best": 0, "longest": 0.0} for game in GAMES}, "achievements": []}

    def load(self) -> dict:
        if not self.path.exists():
            return self.default()
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            base = self.default()
            base.update(data)
            if not isinstance(base["games"], dict):
                base["games"] = self.default()["games"]
            for game in GAMES:
                details = base["games"].get(game, {})
                normalized = {"best": 0, "longest": 0.0}
                if isinstance(details, dict):
                    normalized.update(details)
                base["games"][game] = normalized
            return base
        except (OSError, json.JSONDecodeError):
            backup = self.path.with_name(f"stats.corrupt-{int(time.time())}.json")
            try: shutil.copy2(self.path, backup)
            except OSError: pass
            return self.default()

    def save(self, data: dict) -> None:
        atomic_json(self.path, data)

    def language(self) -> str:
        return self.load().get("language") or ""

    def set_language(self, language: str) -> None:
        data = self.load(); data["language"] = language; self.save(data)

    def _record_game(self, data: dict, game: str, score: int, elapsed: float, best_value: float | None = None) -> None:
        duration = max(0.0, elapsed)
        today = date.today().isoformat()
        data["total_seconds"] += duration
        data["today"][today] = data["today"].get(today, 0.0) + duration
        data["longest_wait_seconds"] = max(data["longest_wait_seconds"], duration)
        details = data["games"].setdefault(game, {"best": 0, "longest": 0.0})
        details["best"] = max(details["best"], best_value if best_value is not None else int(score))
        details["longest"] = max(details["longest"], duration)
        achievements = set(data.get("achievements", [])); achievements.add("first_game")
        if data["total_seconds"] >= 600: achievements.add("ten_minutes")
        if data["total_seconds"] >= 3600: achievements.add("one_hour")
        if duration >= 300: achievements.add("still_thinking")
        if data["today"][today] >= 20 * 2: achievements.add("touch_grass")
        data["achievements"] = sorted(achievements)

    def record_game(self, game: str, score: int, elapsed: float, best_value: float | None = None) -> dict:
        data = self.load(); self._record_game(data, game, score, elapsed, best_value); self.save(data); return data

    def finish_arcade(self, forced: bool) -> dict:
        data = self.load(); data["tasks_completed"] += int(forced); data["forced_ends"] += int(forced); self.save(data); return data

    def start_session(self) -> None:
        self.started_at = time.monotonic()

    def finish_session(self, game: str, score: int, forced: bool, elapsed: float | None = None) -> dict:
        duration = max(0.0, elapsed if elapsed is not None else time.monotonic() - (self.started_at or time.monotonic()))
        data = self.load(); self._record_game(data, game, score, duration)
        data["tasks_completed"] += int(forced); data["forced_ends"] += int(forced)
        details = data["games"][game]
        if forced and score >= max(1, details["best"] - 1):
            data["achievements"] = sorted(set(data["achievements"]) | {"so_close"})
        self.save(data); return data
