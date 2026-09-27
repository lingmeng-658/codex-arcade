import unittest
from unittest.mock import patch

from codex_arcade.games.arcade_games import Aim, Breakout, Dodge, Pong, Snake


class Canvas:
    def delete(self, *_args): pass
    def create_text(self, *_args, **_kwargs): return 1
    def create_rectangle(self, *_args, **_kwargs): return 1
    def create_oval(self, *_args, **_kwargs): return 1


class Event:
    def __init__(self, x, y): self.x, self.y = x, y


class GameplayPolishTests(unittest.TestCase):
    def test_snake_speed_increases_but_respects_minimum_interval(self):
        snake = Snake(Canvas(), 360, 410)
        initial = snake.tick_ms
        for _ in range(100):
            snake.score += 1
            snake.update_speed()
        self.assertLess(snake.tick_ms, initial)
        self.assertGreaterEqual(snake.tick_ms, snake.min_tick_ms)

    def test_dodge_best_metric_is_survival_duration(self):
        dodge = Dodge(Canvas(), 360, 410)
        self.assertEqual(dodge.best_value(12.5), 12.5)

    def test_aim_counts_only_successful_hits_and_invalidates_target(self):
        aim = Aim(Canvas(), 360, 410)
        x, y, _ = aim.target
        first_id = aim.target_id
        with patch("codex_arcade.games.arcade_games.time.monotonic", side_effect=[10.0, 10.4]):
            aim.target_started_at = 10.0
            aim.click(Event(x, y))
        self.assertEqual(aim.score, 1)
        self.assertEqual(aim.combo, 1)
        self.assertEqual(aim.reaction_count, 1)
        self.assertNotEqual(aim.target_id, first_id)
        aim.click(Event(0, 0))
        self.assertEqual(aim.combo, 0)
        self.assertEqual(aim.reaction_count, 1)

    def test_breakout_resolves_one_brick_once_with_multiple_balls(self):
        game = Breakout(Canvas(), 360, 410)
        game.bricks = [(100, 100)]
        game.balls = [[110, 105, 0, 1], [110, 105, 0, 1]]
        with patch("codex_arcade.games.arcade_games.random.random", return_value=1.0):
            game.resolve_bricks()
        self.assertEqual(game.score, 1)
        self.assertEqual(game.bricks, [])

    def test_breakout_multiball_never_exceeds_five_balls(self):
        game = Breakout(Canvas(), 360, 410)
        game.balls = [[1, 1, 1, 1]] * 5
        game.add_multiball(game.balls[0])
        self.assertEqual(len(game.balls), 5)

    def test_pong_ends_when_player_reaches_five(self):
        game = Pong(Canvas(), 360, 410)
        game.player_points = 4
        game.award_point("player")
        self.assertTrue(game.ended)
        self.assertEqual(game.player_points, 5)

    def test_pong_point_starts_short_serve_delay(self):
        game = Pong(Canvas(), 360, 410)
        game.award_point("cpu")
        self.assertGreater(game.serve_delay_ticks, 0)
