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

    def record_game(self, game, score, elapsed=None):
        self.recorded.append((game, score, elapsed))


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
