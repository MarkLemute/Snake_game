import pygame
import random
import math
from enum import Enum
from collections import deque
from pathlib import Path

# Initialize Pygame
pygame.init()

# Constants
CELL_SIZE = 25
GRID_WIDTH = 32
GRID_HEIGHT = 24
HUD_HEIGHT = 50
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + HUD_HEIGHT

# Speed (moves per second) - the snake speeds up as it eats
START_SPEED = 8
SPEED_STEP = 0.4
MAX_SPEED = 20

# Slithering: the body waves side to side as the snake moves
SLITHER_AMOUNT = CELL_SIZE * 0.3   # How far the body swings sideways (pixels)
WAVE_LENGTH = 4                    # Length of one full wiggle (cells)

# High score is saved next to this file
HIGH_SCORE_FILE = Path(__file__).parent / "highscore.txt"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRASS_LIGHT = (170, 215, 81)
GRASS_DARK = (162, 209, 73)
HUD_COLOR = (74, 117, 44)
SHADOW = (120, 165, 55)
SNAKE_HEAD = (65, 105, 225)
SNAKE_TAIL = (140, 180, 255)
SNAKE_STRIPE = (40, 70, 170)
APPLE_RED = (231, 71, 29)
LEAF_GREEN = (60, 160, 60)
STEM_BROWN = (110, 70, 30)
YELLOW = (255, 220, 0)
RED = (220, 40, 40)

# FPS (drawing speed - separate from how fast the snake moves)
FPS = 60

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

KEY_DIRECTIONS = {
    pygame.K_UP: Direction.UP, pygame.K_w: Direction.UP,
    pygame.K_DOWN: Direction.DOWN, pygame.K_s: Direction.DOWN,
    pygame.K_LEFT: Direction.LEFT, pygame.K_a: Direction.LEFT,
    pygame.K_RIGHT: Direction.RIGHT, pygame.K_d: Direction.RIGHT,
}

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 80)
        self.small_font = pygame.font.Font(None, 28)

        # Grass background is drawn once and reused every frame
        self.background = self.make_background()

        self.high_score = self.load_high_score()
        self.walls = False  # False = snake wraps around the edges
        self.state = "menu"  # "menu", "playing", "paused" or "game_over"
        self.particles = []
        self.time = 0

        # Game state
        self.reset_game()

    def make_background(self):
        surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT - HUD_HEIGHT))
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                color = GRASS_LIGHT if (x + y) % 2 == 0 else GRASS_DARK
                pygame.draw.rect(surface, color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        return surface

    def load_high_score(self):
        try:
            return int(HIGH_SCORE_FILE.read_text())
        except (OSError, ValueError):
            return 0

    def save_high_score(self):
        try:
            HIGH_SCORE_FILE.write_text(str(self.high_score))
        except OSError:
            pass  # Not being able to save the high score shouldn't crash the game

    def reset_game(self):
        # Snake starts in the middle, 3 segments long
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        self.snake = deque([(start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y)])
        self.prev_snake = list(self.snake)  # Where each segment was before the last move
        self.moves = 0                      # Total moves made, used to keep the wiggle flowing
        self.direction = Direction.RIGHT
        self.direction_queue = deque()  # Remembers quick key presses so turns aren't lost
        self.food = self.spawn_food()
        self.score = 0
        self.speed = START_SPEED
        self.move_timer = 0
        self.new_high_score = False

    def spawn_food(self):
        while True:
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            if (x, y) not in self.snake:
                return (x, y)

    def queue_direction(self, new_direction):
        # Compare against the last queued turn, so two fast presses can't reverse the snake
        last = self.direction_queue[-1] if self.direction_queue else self.direction
        dx, dy = new_direction.value
        last_dx, last_dy = last.value
        is_reverse = (dx, dy) == (-last_dx, -last_dy)
        if new_direction != last and not is_reverse and len(self.direction_queue) < 3:
            self.direction_queue.append(new_direction)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                return False

            if self.state == "menu":
                if event.key == pygame.K_SPACE:
                    self.state = "playing"
                elif event.key == pygame.K_TAB:
                    self.walls = not self.walls

            elif self.state == "playing":
                if event.key in KEY_DIRECTIONS:
                    self.queue_direction(KEY_DIRECTIONS[event.key])
                elif event.key == pygame.K_p:
                    self.state = "paused"

            elif self.state == "paused":
                if event.key in (pygame.K_p, pygame.K_SPACE):
                    self.state = "playing"

            elif self.state == "game_over":
                if event.key == pygame.K_SPACE:
                    self.reset_game()
                    self.state = "playing"
                elif event.key == pygame.K_m:
                    self.reset_game()
                    self.state = "menu"

        return True

    def update(self, dt):
        self.time += dt
        self.update_particles(dt)

        if self.state != "playing":
            return

        # Move the snake a fixed number of times per second
        self.move_timer += dt
        move_interval = 1000 / self.speed
        while self.move_timer >= move_interval and self.state == "playing":
            self.move_timer -= move_interval
            self.step()

    def step(self):
        self.prev_snake = list(self.snake)
        self.moves += 1
        if self.direction_queue:
            self.direction = self.direction_queue.popleft()

        # Calculate new head position
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_x = head_x + dx
        new_y = head_y + dy

        # Hitting the edge: wrap around, or die if walls are on
        if self.walls:
            if not (0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT):
                self.end_game()
                return
        else:
            new_x %= GRID_WIDTH
            new_y %= GRID_HEIGHT

        # Check collision with self (the tail moves away this step, so it's safe)
        if (new_x, new_y) in list(self.snake)[:-1]:
            self.end_game()
            return

        # Add new head
        self.snake.appendleft((new_x, new_y))

        # Check if food is eaten
        if (new_x, new_y) == self.food:
            self.score += 10
            self.speed = min(MAX_SPEED, self.speed + SPEED_STEP)
            self.burst(self.food, APPLE_RED)
            self.food = self.spawn_food()
        else:
            # Remove tail if no food eaten
            self.snake.pop()

    def end_game(self):
        self.state = "game_over"
        self.burst(self.snake[0], SNAKE_HEAD)
        if self.score > self.high_score:
            self.high_score = self.score
            self.new_high_score = True
            self.save_high_score()

    def burst(self, cell, color):
        # Little explosion of particles from the center of a cell
        cx, cy = self.cell_center(cell)
        for _ in range(18):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.05, 0.25)
            self.particles.append({
                "x": cx, "y": cy,
                "vx": math.cos(angle) * speed, "vy": math.sin(angle) * speed,
                "life": random.uniform(300, 600), "color": color,
            })

    def update_particles(self, dt):
        for particle in self.particles:
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["life"] -= dt
        self.particles = [p for p in self.particles if p["life"] > 0]

    def cell_center(self, cell):
        x, y = cell
        return (x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2 + HUD_HEIGHT)

    def draw(self):
        self.screen.blit(self.background, (0, HUD_HEIGHT))
        if self.walls:
            pygame.draw.rect(self.screen, HUD_COLOR, (0, HUD_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT - HUD_HEIGHT), 4)

        self.draw_food()
        self.draw_snake()
        self.draw_particles()
        self.draw_hud()

        if self.state == "menu":
            self.draw_menu()
        elif self.state == "paused":
            self.draw_overlay("PAUSED", ["Press P to continue"])
        elif self.state == "game_over":
            lines = [f"Score: {self.score}    Best: {self.high_score}"]
            if self.new_high_score:
                lines.append("NEW HIGH SCORE!")
            lines.append("SPACE to play again   M for menu")
            self.draw_overlay("GAME OVER", lines)

        pygame.display.flip()

    def draw_snake(self):
        # How far (0 to 1) the snake has glided from its last cell to its next one
        if self.state in ("playing", "paused"):
            progress = min(1, self.move_timer / (1000 / self.speed))
        else:
            progress = 1

        points = self.glide_points(progress)
        samples = self.slither(self.body_samples(points), self.moves + progress)
        total = samples[-1][2] or 1
        base_radius = CELL_SIZE // 2 - 1

        def radius_at(s):
            return base_radius * (1 - 0.4 * s / total)  # Thinner toward the tail

        def color_at(s):
            # Dark stripes every so often, otherwise fade from head color to tail color
            if s > CELL_SIZE and (s / CELL_SIZE) % 1.5 < 0.3:
                return SNAKE_STRIPE
            t = s / total
            return tuple(int(SNAKE_HEAD[c] + (SNAKE_TAIL[c] - SNAKE_HEAD[c]) * t) for c in range(3))

        # Draw tail to head so the head ends up on top: shadow first, then the body
        for x, y, s in reversed(samples):
            pygame.draw.circle(self.screen, SHADOW, (x + 3, y + 3), radius_at(s))
        for x, y, s in reversed(samples):
            pygame.draw.circle(self.screen, color_at(s), (x, y), radius_at(s))

        self.draw_head(points)

    def glide_points(self, progress):
        # Slide each segment from where it was to where it is now, so movement is smooth
        points = []
        for i, (x, y) in enumerate(self.snake):
            px, py = self.prev_snake[min(i, len(self.prev_snake) - 1)]
            if abs(x - px) + abs(y - py) > 1:
                px, py = x, y  # Wrapped around the edge: jump instead of sliding across the screen
            gx = px + (x - px) * progress
            gy = py + (y - py) * progress
            points.append((gx * CELL_SIZE + CELL_SIZE / 2, gy * CELL_SIZE + CELL_SIZE / 2 + HUD_HEIGHT))
        return points

    def body_samples(self, points):
        # Walk along the body from head to tail, placing a point every few pixels.
        # Each sample is (x, y, distance from the head).
        samples = []
        s = 0
        for (ax, ay), (bx, by) in zip(points, points[1:]):
            d = math.hypot(bx - ax, by - ay)
            if d < 0.01:
                continue  # Segments on top of each other (the tail right after eating)
            if d > CELL_SIZE * 1.5:
                samples.append((ax, ay, s))  # Gap where the snake wraps around the screen
                continue
            steps = max(1, int(d / 4))
            for k in range(steps):
                f = k / steps
                samples.append((ax + (bx - ax) * f, ay + (by - ay) * f, s + d * f))
            s += d
        samples.append((points[-1][0], points[-1][1], s))
        return samples

    def slither(self, samples, distance_moved):
        # Push each sample sideways along a sine wave. The wave is tied to how far the
        # snake has travelled, so the body follows the same wiggly path as the head.
        result = []
        side_x, side_y = 0, 1
        for k, (x, y, s) in enumerate(samples):
            # Sideways direction, averaged over nearby samples so corners stay smooth
            ax, ay, _ = samples[max(0, k - 3)]
            bx, by, _ = samples[min(len(samples) - 1, k + 3)]
            dx, dy = ax - bx, ay - by
            length = math.hypot(dx, dy)
            if 0 < length < CELL_SIZE * 1.5:
                side_x, side_y = -dy / length, dx / length

            wave = math.sin(2 * math.pi * (distance_moved - s / CELL_SIZE) / WAVE_LENGTH)
            near_head = min(1, s / (CELL_SIZE * 2))  # Keep the head steady, wiggle the body
            amount = SLITHER_AMOUNT * wave * near_head
            result.append((x + side_x * amount, y + side_y * amount, s))
        return result

    def draw_head(self, points):
        hx, hy = points[0]
        # Face the way the head is actually moving
        dx, dy = self.direction.value
        if len(points) > 1:
            mx, my = hx - points[1][0], hy - points[1][1]
            length = math.hypot(mx, my)
            if 0 < length < CELL_SIZE * 1.5:
                dx, dy = mx / length, my / length
        side_x, side_y = -dy, dx  # Perpendicular to the direction the snake faces

        # Flick the tongue out every couple of seconds
        if self.time % 1800 < 250:
            tip_x, tip_y = hx + dx * 20, hy + dy * 20
            pygame.draw.line(self.screen, RED, (hx + dx * 12, hy + dy * 12), (tip_x, tip_y), 2)
            for side in (-1, 1):
                fork = (tip_x + dx * 4 + side_x * side * 3, tip_y + dy * 4 + side_y * side * 3)
                pygame.draw.line(self.screen, RED, (tip_x, tip_y), fork, 2)

        for side in (-1, 1):
            eye_x = hx + dx * 4 + side_x * side * 6
            eye_y = hy + dy * 4 + side_y * side * 6
            pygame.draw.circle(self.screen, WHITE, (eye_x, eye_y), 5)
            pygame.draw.circle(self.screen, BLACK, (eye_x + dx * 2, eye_y + dy * 2), 2)

    def draw_food(self):
        cx, cy = self.cell_center(self.food)
        # Gentle pulsing so the apple stands out
        radius = CELL_SIZE // 2 - 2 + math.sin(self.time / 150) * 1.5
        pygame.draw.circle(self.screen, SHADOW, (cx + 3, cy + 4), radius)
        pygame.draw.circle(self.screen, APPLE_RED, (cx, cy + 1), radius)
        pygame.draw.circle(self.screen, (255, 160, 140), (cx - 4, cy - 3), 3)  # Shine
        pygame.draw.line(self.screen, STEM_BROWN, (cx, cy - radius + 2), (cx + 2, cy - radius - 4), 3)
        pygame.draw.ellipse(self.screen, LEAF_GREEN, (cx + 2, cy - radius - 6, 9, 5))

    def draw_particles(self):
        for particle in self.particles:
            size = max(1, int(particle["life"] / 120))
            pygame.draw.circle(self.screen, particle["color"], (int(particle["x"]), int(particle["y"])), size)

    def draw_hud(self):
        pygame.draw.rect(self.screen, HUD_COLOR, (0, 0, WINDOW_WIDTH, HUD_HEIGHT))
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (15, 13))
        best_text = self.font.render(f"Best: {self.high_score}", True, YELLOW)
        self.screen.blit(best_text, best_text.get_rect(topright=(WINDOW_WIDTH - 15, 13)))
        hint = "P: pause" if self.state == "playing" else ""
        hint_text = self.small_font.render(hint, True, WHITE)
        self.screen.blit(hint_text, hint_text.get_rect(center=(WINDOW_WIDTH // 2, HUD_HEIGHT // 2)))

    def draw_menu(self):
        mode = "ON (hitting the edge ends the game)" if self.walls else "OFF (wrap around the edges)"
        self.draw_overlay("SNAKE", [
            "Arrow keys or WASD to move",
            f"Walls: {mode}",
            "TAB to change walls",
            "Press SPACE to start",
        ])

    def draw_overlay(self, title, lines):
        # Darken the game behind the message
        shade = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 150))
        self.screen.blit(shade, (0, 0))

        title_text = self.big_font.render(title, True, WHITE)
        y = WINDOW_HEIGHT // 2 - 40 - len(lines) * 18
        self.screen.blit(title_text, title_text.get_rect(center=(WINDOW_WIDTH // 2, y)))
        y += 70
        for line in lines:
            color = YELLOW if "HIGH SCORE" in line else WHITE
            text = self.font.render(line, True, color)
            self.screen.blit(text, text.get_rect(center=(WINDOW_WIDTH // 2, y)))
            y += 40

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            running = self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()

if __name__ == "__main__":
    game = SnakeGame()
    game.run()
