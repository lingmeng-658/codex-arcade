import tempfile
import unittest
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
