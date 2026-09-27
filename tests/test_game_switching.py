import unittest
from unittest.mock import patch

from codex_arcade.app import Arcade


class FakeRoot:
    def __init__(self):
        self.cancelled = []
        self.scheduled = []

    def after(self, delay, callback):
        self.scheduled.append((delay, callback))
        return f"after-{len(self.scheduled)}"

    def after_cancel(self, callback_id):
        self.cancelled.append(callback_id)


class FakeCanvas:
    def delete(self, *_args): pass
    def create_text(self, *_args, **_kwargs): return 1
    def create_rectangle(self, *_args, **_kwargs): return 1
    def create_oval(self, *_args, **_kwargs): return 1
    def tag_bind(self, *_args, **_kwargs): pass


class FakeStore:
    def __init__(self):
        self.recorded = []

    def record_game(self, game, score, elapsed=None, best_value=None):
        self.recorded.append((game, score, elapsed))

    def load(self):
        return {"games": {name: {"best": 0} for name in ("snake", "dodge", "aim", "breakout", "pong")}}


def arcade_for_switching():
    arcade = Arcade.__new__(Arcade)
    arcade.root = FakeRoot()
    arcade.canvas = FakeCanvas()
    arcade.store = FakeStore()
    arcade.closed = False
    arcade.finishing = False
    arcade.language = "en"
    arcade.game = None
    arcade.game_after_id = None
    arcade.game_generation = 0
    arcade.runtime_state = "playing"
    arcade.round_elapsed = 0.0
    arcade.round_started_at = 0.0
    arcade.round_settled = False
    return arcade


class GameSwitchingTests(unittest.TestCase):
    def test_snake_to_games_then_dodge_records_snake_and_runs_only_dodge(self):
        arcade = arcade_for_switching()
        arcade.start_game("snake")
        arcade.return_to_games()
        arcade.start_game("dodge")

        self.assertEqual(arcade.store.recorded[0][0], "snake")
        self.assertEqual(arcade.game_name, "dodge")
        self.assertEqual(len(arcade.root.cancelled), 1)

    def test_random_switch_never_restarts_current_game(self):
        arcade = arcade_for_switching()
        arcade.start_game("snake")

        with patch("codex_arcade.app.random.choice", side_effect=lambda choices: choices[0]):
            arcade.start_random_game()

        self.assertEqual(arcade.store.recorded[0][0], "snake")
        self.assertNotEqual(arcade.game_name, "snake")

    def test_session_closing_blocks_a_pending_switch(self):
        arcade = arcade_for_switching()
        arcade.start_game("snake")
        arcade.finishing = True

        arcade.return_to_games()

        self.assertEqual(arcade.game_name, "snake")

    def test_stale_game_tick_cannot_update_the_replacement_game(self):
        arcade = arcade_for_switching()
        arcade.start_game("snake")
        stale_tick = arcade.root.scheduled[-1][1]
        arcade.return_to_games()
        arcade.start_game("dodge")
        dodge_age = arcade.game.age

        stale_tick()

        self.assertEqual(arcade.game.age, dodge_age)

    def test_restart_settles_round_without_ending_session(self):
        arcade = arcade_for_switching()
        arcade.start_game("snake")
        arcade.restart_current_game()

        self.assertEqual(arcade.game_name, "snake")
        self.assertEqual(arcade.runtime_state, "playing")
        self.assertEqual(arcade.store.recorded[0][0], "snake")

    def test_pause_excludes_elapsed_time_and_blocks_old_tick(self):
        arcade = arcade_for_switching()
        arcade.start_game("dodge")
        old_tick = arcade.root.scheduled[-1][1]
        arcade.pause_or_resume()
        age_before = arcade.game.age

        old_tick()

        self.assertEqual(arcade.runtime_state, "paused")
        self.assertEqual(arcade.game.age, age_before)

    def test_paused_wall_time_is_excluded_from_round_settlement(self):
        arcade = arcade_for_switching()
        with patch("codex_arcade.app.time.monotonic", side_effect=[0.0, 10.0, 110.0, 111.0]):
            arcade.start_game("snake")
            arcade.pause_or_resume()
            arcade.pause_or_resume()
            arcade.settle_round()

        self.assertEqual(arcade.store.recorded[0][2], 11.0)
