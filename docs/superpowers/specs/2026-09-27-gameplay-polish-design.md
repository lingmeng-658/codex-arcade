# Gameplay Polish Design

## Scope

Polish the five existing games without adding games, dependencies, audio,
skins, networking, leaderboards, a general power-up system, or complex level
progression. The only gameplay addition is the narrowly scoped Breakout
Multi-ball rule described below. Do not commit or push this work.

## Central Runtime Control

`Arcade` owns a small runtime state machine: `playing`, `paused`,
`game_over`, and `closing`. It owns all global keyboard input, per-round
settlement, effective play-time accounting, and Tkinter callback generations.

- `P` and `Space` toggle between `playing` and `paused`.
- `R` settles the active round and immediately starts a fresh round of the
  same game.
- `Tab` and `G` settle the active round and return to the games list.
- `N` settles the active round and starts a randomly selected different game.
- `Esc` closes Arcade.
- Stop/Interrupt enters `closing` first, freezes input, invalidates pending
  game callbacks, shows the existing short finish overlay, then closes.

The controller tracks active play segments with `time.monotonic()`. Paused
time is excluded. Restart, Games, and Random settle only the current round;
they do not end the Codex Arcade session or affect task-completion/interruption
counts. Every delayed game callback captures a generation number and returns
unless the generation matches and the state is `playing`.

## Shared UI

Every playing game renders a compact HUD with current score, game-specific
Best, and the effective controls. The game-over shell is shared and exposes
Restart, Games, and Random. The games list displays each game's Best. English
and Simplified Chinese strings cover all new labels, controls, pause, and
game-over text.

## Game Rules

### Snake

The base speed is slower than the current implementation. Each food pickup
slightly decreases the tick interval; a fixed minimum interval prevents
unplayable speed. Score and Best are highest score.

### Dodge

Score is survival seconds. Obstacle speed and spawn rate increase gradually
with survival time. Best is longest survival seconds rather than a generic
numeric score.

### Aim Trainer

Each target records its creation time and a unique target identity. A hit
invalidates that target immediately before spawning a replacement, so it can
only contribute once. Successful hits increase score and combo and add their
reaction duration to an average; misses reset combo and never affect average
reaction time. Target radii vary mildly within a bounded range.

### Breakout

Breakout manages a bounded list of balls (maximum five). Paddle collisions
only occur for downward-moving balls that cross the paddle's top boundary;
the ball is moved above the paddle and its horizontal velocity is derived from
relative impact position. This prevents embedding and repeat-frame collisions.

Brick collision resolution collects each hit brick once per tick before
mutating state. Each such brick is removed and scored once, and its 4% Multi-
ball decision is made once. Multi-ball turns one live ball into three balls;
when already multi-ball it adds at most one ball, never exceeding five. A
round continues while any ball remains. Clearing all bricks immediately
creates the next same-layout screen and slightly raises ball speed; it does
not introduce a level system.

### Pong

Player and CPU scores are tracked separately; the first side to five wins.
The CPU moves toward a delayed target with finite maximum speed, which leaves
miss opportunities. After every point, a short serve delay freezes play before
the next ball launches. A completed match enters the shared game-over shell,
where `R` starts a new match.

## Statistics

Round settlement records the game score and effective play duration. Snake,
Aim, and Breakout Best values remain high scores; Dodge Best is the maximum
survival time; Pong Best is the player's best match score. Session totals gain
only effective play time. Session completion and forced-end counters continue
to update only on an actual Arcade close.

## Testing

Add focused tests for controller lifecycle (`R` does not close the session,
`N` excludes the active game, old callbacks are inert after restart/switch,
and pause excludes elapsed time), plus rule tests for Snake speed bounds,
Dodge survival Best, Aim hit/miss accounting, Breakout single-brick and
multi-ball bounds, and Pong first-to-five/serve delay. Run the entire existing
test suite after implementation.
