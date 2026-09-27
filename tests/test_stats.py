import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from codex_arcade.stats import StatsStore


class StatsStoreTests(unittest.TestCase):
    def test_records_scores_and_session_totals(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StatsStore(Path(tmp) / "stats.json")
            store.start_session()
            store.finish_session("snake", 7, forced=True, elapsed=12.5)
            data = store.load()
            self.assertEqual(data["games"]["snake"]["best"], 7)
            self.assertEqual(data["tasks_completed"], 1)
            self.assertEqual(data["forced_ends"], 1)
            self.assertGreaterEqual(data["total_seconds"], 12.5)

    def test_language_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StatsStore(Path(tmp) / "stats.json")
            store.set_language("zh-CN")
            self.assertEqual(StatsStore(Path(tmp) / "stats.json").language(), "zh-CN")

    def test_records_each_switched_game_without_ending_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StatsStore(Path(tmp) / "stats.json")
            store.record_game("snake", 7, 12.5)
            data = store.load()
            self.assertEqual(data["games"]["snake"]["best"], 7)
            self.assertEqual(data["tasks_completed"], 0)
            self.assertGreaterEqual(data["total_seconds"], 12.5)

    def test_backs_up_malformed_statistics(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.json"; path.write_text("not json", encoding="utf-8")
            self.assertEqual(StatsStore(path).load()["tasks_completed"], 0)
            self.assertTrue(list(Path(tmp).glob("stats.corrupt-*.json")))

    def test_upgrades_partial_game_statistics_before_recording(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.json"
            path.write_text('{"games": {"snake": {"best": 3}}}', encoding="utf-8")

            StatsStore(path).record_game("snake", 4, 1.0)

            self.assertEqual(StatsStore(path).load()["games"]["snake"], {"best": 4, "longest": 1.0})

    def test_unlocks_ten_minutes_after_cumulative_effective_play(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StatsStore(Path(tmp) / "stats.json")
            store.record_game("snake", 1, 599)
            store.record_game("dodge", 1, 1)

            self.assertIn("ten_minutes", store.load()["achievements"])

    def test_unlocks_still_thinking_after_five_minute_codex_wait(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StatsStore(Path(tmp) / "stats.json")
            store.start_session()
            store.finish_arcade(True, elapsed=300)

            self.assertIn("still_thinking", store.load()["achievements"])

    def test_unlocks_arcade_tour_after_all_games_are_played(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StatsStore(Path(tmp) / "stats.json")
            for game in ("snake", "dodge", "aim", "breakout", "pong"):
                store.record_game(game, 1, 1)

            self.assertIn("arcade_tour", store.load()["achievements"])

    def test_achievement_unlock_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StatsStore(Path(tmp) / "stats.json")
            store.record_game("snake", 1, 600)
            store.record_game("snake", 1, 600)

            self.assertEqual(store.load()["achievements"].count("ten_minutes"), 1)

    def test_old_stats_gain_achievement_and_daily_fields(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "stats.json"
            path.write_text('{"total_seconds": 4, "games": {"snake": {"best": 3}}}', encoding="utf-8")

            data = StatsStore(path).load()

            self.assertEqual(data["achievements"], [])
            self.assertEqual(data["daily"]["arcade_sessions"], 0)
            self.assertEqual(data["played_games"], [])
            persisted = __import__("json").loads(path.read_text(encoding="utf-8"))
            self.assertIn("achievements", persisted)
            self.assertIn("daily", persisted)

    def test_so_close_requires_ninety_percent_without_exceeding_historical_best(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StatsStore(Path(tmp) / "stats.json")
            self.assertFalse(store.unlock_so_close("snake", 89, 100))
            self.assertTrue(store.unlock_so_close("snake", 90, 100))
            self.assertFalse(store.unlock_so_close("snake", 101, 100))
            self.assertEqual(store.load()["achievements"].count("so_close"), 1)

    def test_daily_arcade_counter_resets_when_the_date_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = StatsStore(Path(tmp) / "stats.json")
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            data = store.default()
            data["daily"] = {"date": yesterday, "arcade_sessions": 19}
            store.save(data)

            store.start_session()

            daily = store.load()["daily"]
            self.assertEqual(daily["date"], date.today().isoformat())
            self.assertEqual(daily["arcade_sessions"], 1)
