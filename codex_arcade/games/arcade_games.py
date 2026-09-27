import math
import random
import time


class Game:
    tick_ms = 35

    def __init__(self, canvas, width, height):
        self.canvas, self.width, self.height = canvas, width, height
        self.score, self.keys, self.ended = 0, set(), False

    def key(self, key, down):
        self.keys.discard(key) if not down else self.keys.add(key)

    def best_value(self, elapsed): return self.score

    def draw_score(self):
        self.canvas.delete("score")
        self.canvas.create_text(self.width - 12, 48, anchor="e", text=str(self.score), fill="#d7e1ee", font=("Consolas", 12, "bold"), tags="score")


class Snake(Game):
    base_tick_ms, min_tick_ms = 190, 105

    def __init__(self, *args):
        super().__init__(*args)
        self.cell, self.tick_ms = 18, self.base_tick_ms
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = self.pending = (1, 0)
        self.food = self._food()

    def _food(self):
        choices = [(x, y) for x in range(self.width // self.cell) for y in range(3, self.height // self.cell) if (x, y) not in self.snake]
        return random.choice(choices)

    def update_speed(self): self.tick_ms = max(self.min_tick_ms, self.base_tick_ms - self.score * 4)

    def update(self):
        maps = {"w": (0, -1), "up": (0, -1), "s": (0, 1), "down": (0, 1), "a": (-1, 0), "left": (-1, 0), "d": (1, 0), "right": (1, 0)}
        for key, direction in maps.items():
            if key in self.keys and direction != (-self.direction[0], -self.direction[1]): self.pending = direction
        self.direction = self.pending; x, y = self.snake[0]
        head = ((x + self.direction[0]) % (self.width // self.cell), 3 + (y - 3 + self.direction[1]) % ((self.height // self.cell) - 3))
        if head in self.snake[:-1]: self.ended = True; return
        self.snake.insert(0, head)
        if head == self.food:
            self.score += 1; self.update_speed(); self.food = self._food()
        else: self.snake.pop()

    def draw(self):
        self.canvas.delete("game"); c = self.cell
        for i, (x, y) in enumerate(self.snake): self.canvas.create_rectangle(x*c+2, y*c+2, (x+1)*c-2, (y+1)*c-2, fill="#e8f0ff" if i == 0 else "#8796aa", outline="", tags="game")
        x, y = self.food; self.canvas.create_oval(x*c+4, y*c+4, (x+1)*c-4, (y+1)*c-4, fill="#ff6767", outline="", tags="game"); self.draw_score()


class Dodge(Game):
    def __init__(self, *args):
        super().__init__(*args); self.x, self.blocks, self.age = self.width / 2, [], 0

    def best_value(self, elapsed): return elapsed

    def update(self):
        self.age += 1; self.score = round(self.age * self.tick_ms / 1000, 1)
        self.x = max(12, min(self.width - 12, self.x + (("d" in self.keys or "right" in self.keys) - ("a" in self.keys or "left" in self.keys)) * 8))
        difficulty = min(7, self.age // 240); interval = max(9, 20 - difficulty)
        if self.age % interval == 0: self.blocks.append([random.randint(8, self.width - 24), 45, random.randint(4, 7) + difficulty * .45])
        for block in self.blocks: block[1] += block[2]
        self.blocks = [block for block in self.blocks if block[1] < self.height + 20]
        if any(abs(block[0] - self.x) < 18 and block[1] > self.height - 45 for block in self.blocks): self.ended = True

    def draw(self):
        self.canvas.delete("game"); self.canvas.create_oval(self.x-11, self.height-35, self.x+11, self.height-13, fill="#77e0b0", outline="", tags="game")
        for x, y, _ in self.blocks: self.canvas.create_rectangle(x, y, x+18, y+18, fill="#ff6b6b", outline="", tags="game")
        self.draw_score()


class Aim(Game):
    def __init__(self, *args):
        super().__init__(*args); self.combo, self.reaction_total, self.reaction_count, self.target_id = 0, 0.0, 0, 0; self.new_target()

    @property
    def average_reaction(self): return self.reaction_total / self.reaction_count if self.reaction_count else 0.0

    def new_target(self):
        radius = random.randint(11, 17); self.target = (random.randint(24, self.width-24), random.randint(60, self.height-24), radius); self.target_id += 1; self.target_started_at = time.monotonic()

    def click(self, event):
        x, y, radius = self.target
        if (event.x-x)**2 + (event.y-y)**2 <= radius**2:
            self.reaction_total += max(0.0, time.monotonic() - self.target_started_at); self.reaction_count += 1; self.score += 1; self.combo += 1; self.target = None; self.new_target()
        else: self.combo = 0

    def update(self): pass

    def draw(self):
        self.canvas.delete("game"); x, y, radius = self.target
        self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius, fill="#ff6767", outline="#fff", tags="game"); self.canvas.create_oval(x-3, y-3, x+3, y+3, fill="#fff", outline="", tags="game")
        self.draw_score(); self.canvas.create_text(12, 48, anchor="w", text=f"Combo {self.combo} · {self.average_reaction:.2f}s", fill="#aab8cc", font=("Segoe UI", 9), tags="aim_info")


class Breakout(Game):
    def __init__(self, *args):
        super().__init__(*args); self.paddle, self.speed = self.width / 2, 1.0; self.balls = []; self.new_screen()

    def new_screen(self):
        self.bricks = [(12+c*42, 62+r*20) for r in range(4) for c in range(8)]
        if not self.balls: self.balls = [[self.width/2, self.height-65, 4*self.speed, -4*self.speed]]

    def add_multiball(self, ball):
        room = 5 - len(self.balls)
        if room <= 0: return
        copies = min(room, 2 if len(self.balls) == 1 else 1)
        for direction in (-1, 1)[:copies]: self.balls.append([ball[0], ball[1], direction * max(2, abs(ball[2])), -abs(ball[3])])

    def resolve_bricks(self):
        hit = set()
        for ball in self.balls:
            for brick in self.bricks:
                if brick not in hit and brick[0] < ball[0] < brick[0]+36 and brick[1] < ball[1] < brick[1]+14:
                    hit.add(brick); ball[3] *= -1; break
        for brick in hit:
            self.bricks.remove(brick); self.score += 1
            if random.random() < .04 and self.balls: self.add_multiball(self.balls[0])

    def update(self):
        self.paddle = max(35, min(self.width-35, self.paddle + (("d" in self.keys or "right" in self.keys) - ("a" in self.keys or "left" in self.keys)) * 9))
        live = []
        paddle_top = self.height - 28
        for ball in self.balls:
            previous_y = ball[1]; ball[0] += ball[2]; ball[1] += ball[3]
            if ball[0] < 6 or ball[0] > self.width-6: ball[2] *= -1; ball[0] = max(6, min(self.width-6, ball[0]))
            if ball[1] < 52: ball[3] = abs(ball[3]); ball[1] = 52
            crossed = ball[3] > 0 and previous_y <= paddle_top and ball[1] >= paddle_top
            if crossed and abs(ball[0] - self.paddle) <= 42:
                offset = (ball[0] - self.paddle) / 42; speed = max(4, math.hypot(ball[2], ball[3])); ball[2] = speed * offset * .9; ball[3] = -max(2.4, speed * (1 - abs(offset) * .35)); ball[1] = paddle_top - 1
            if ball[1] <= self.height + 8: live.append(ball)
        self.balls = live; self.resolve_bricks()
        if not self.balls: self.ended = True
        elif not self.bricks: self.speed = min(1.8, self.speed + .08); self.balls = []; self.new_screen()

    def draw(self):
        self.canvas.delete("game")
        for x, y in self.bricks: self.canvas.create_rectangle(x, y, x+36, y+14, fill="#819cff", outline="", tags="game")
        for x, y, _, _ in self.balls: self.canvas.create_oval(x-5, y-5, x+5, y+5, fill="#fff", outline="", tags="game")
        self.canvas.create_rectangle(self.paddle-35, self.height-28, self.paddle+35, self.height-20, fill="#77e0b0", outline="", tags="game"); self.draw_score()


class Pong(Game):
    def __init__(self, *args):
        super().__init__(*args); self.player, self.cpu = self.height/2, self.height/2; self.player_points = self.cpu_points = 0; self.serve_delay_ticks = 0; self.launch_ball()

    def launch_ball(self): self.ball = [self.width/2, self.height/2, random.choice((-4, 4)), random.choice((-3, 3))]

    def award_point(self, side):
        if side == "player": self.player_points += 1
        else: self.cpu_points += 1
        self.score = self.player_points
        if max(self.player_points, self.cpu_points) >= 5: self.ended = True
        else: self.serve_delay_ticks = 22

    def update(self):
        self.player = max(45, min(self.height-28, self.player + (("s" in self.keys or "down" in self.keys) - ("w" in self.keys or "up" in self.keys)) * 7))
        if self.serve_delay_ticks:
            self.serve_delay_ticks -= 1
            if not self.serve_delay_ticks: self.launch_ball()
            return
        b = self.ball; target = b[1] if b[2] < 0 else self.height / 2; self.cpu += max(-3.4, min(3.4, (target-self.cpu) * .12)); b[0] += b[2]; b[1] += b[3]
        if b[1] < 52 or b[1] > self.height-5: b[3] *= -1
        if b[0] > self.width-25 and abs(b[1]-self.player) < 35: b[2] = -abs(b[2])
        if b[0] < 25 and abs(b[1]-self.cpu) < 35: b[2] = abs(b[2])
        if b[0] < 0: self.award_point("player")
        elif b[0] > self.width: self.award_point("cpu")

    def draw(self):
        self.canvas.delete("game"); b = self.ball
        if not self.serve_delay_ticks: self.canvas.create_oval(b[0]-5, b[1]-5, b[0]+5, b[1]+5, fill="#fff", outline="", tags="game")
        self.canvas.create_rectangle(self.width-18, self.player-28, self.width-10, self.player+28, fill="#77e0b0", outline="", tags="game"); self.canvas.create_rectangle(10, self.cpu-28, 18, self.cpu+28, fill="#9aa7b8", outline="", tags="game")
        self.draw_score(); self.canvas.create_text(12, 48, anchor="w", text=f"{self.player_points} - {self.cpu_points}", fill="#aab8cc", font=("Consolas", 10, "bold"), tags="pong_info")
