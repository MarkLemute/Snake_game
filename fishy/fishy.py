import pygame
import random
import math
from pathlib import Path

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 650
HUD_HEIGHT = 50
SAND_HEIGHT = 40
WATER_TOP = HUD_HEIGHT
WATER_BOTTOM = WINDOW_HEIGHT - SAND_HEIGHT

# Player fish
START_SIZE = 30
WIN_SIZE = 160          # Grow this big to win
GROWTH = 0.08           # How much of an eaten fish's size you gain
ACCELERATION = 0.6
WATER_DRAG = 0.92       # Slows you down when you stop swimming
MAX_SPEED = 6
SAFE_TIME = 1500        # Milliseconds you can't be eaten at the start

# Other fish
MAX_FISH = 14
SPAWN_EVERY = (500, 1100)  # Random time between new fish (milliseconds)
SMALL_FISH_CHANCE = 0.65   # How often a new fish is smaller than you

# High score is saved next to this file
HIGH_SCORE_FILE = Path(__file__).parent / "highscore.txt"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WATER_TOP_COLOR = (40, 140, 200)
WATER_BOTTOM_COLOR = (10, 40, 90)
SAND = (220, 190, 120)
SAND_DARK = (200, 170, 100)
SEAWEED = (40, 150, 70)
HUD_COLOR = (10, 50, 90)
PLAYER_COLOR = (255, 140, 0)
FISH_COLORS = [(250, 90, 120), (120, 220, 120), (180, 120, 255), (255, 220, 60), (90, 200, 230)]
YELLOW = (255, 220, 0)
RED = (220, 40, 40)

# FPS
FPS = 60

class Fish:
    def __init__(self, player_size):
        # Most fish are smaller than you (food), some are bigger (danger)
        if random.random() < SMALL_FISH_CHANCE:
            self.size = player_size * random.uniform(0.35, 0.9)
        else:
            self.size = player_size * random.uniform(1.15, 2.0)
        self.size = max(12, min(260, self.size))

        # Start just off the left or right edge and swim across
        self.facing = random.choice([-1, 1])
        self.x = -self.size if self.facing == 1 else WINDOW_WIDTH + self.size
        self.y = random.uniform(WATER_TOP + self.size / 2, WATER_BOTTOM - self.size / 2)
        self.speed = random.uniform(1, 3) * (1.3 - min(self.size, 200) / 300)  # Small fish are quicker
        self.color = random.choice(FISH_COLORS)
        self.wiggle_offset = random.uniform(0, 1000)

    def update(self, time):
        self.x += self.speed * self.facing
        self.y += math.sin((time + self.wiggle_offset) / 400) * 0.3  # Gentle bobbing

    def off_screen(self):
        return self.x < -self.size * 2 or self.x > WINDOW_WIDTH + self.size * 2

    def hitbox(self):
        return hitbox(self.x, self.y, self.size)

def hitbox(x, y, size):
    # A bit smaller than the drawing, so touches feel fair
    return pygame.Rect(x - size * 0.4, y - size * 0.22, size * 0.8, size * 0.44)

def draw_fish(screen, x, y, size, facing, color, time, angry=False):
    # Tail swishes side to side, like the snake's slither
    wag = math.sin(time / 90) * size * 0.12
    back_x = x - facing * size * 0.45
    tail = [(back_x + facing * size * 0.05, y),
            (back_x - facing * size * 0.3, y - size * 0.3 + wag),
            (back_x - facing * size * 0.3, y + size * 0.3 + wag)]
    darker = tuple(max(0, c - 50) for c in color)
    pygame.draw.polygon(screen, darker, tail)

    # Fin on top
    fin = [(x - facing * size * 0.15, y - size * 0.22),
           (x - facing * size * 0.05, y - size * 0.45),
           (x + facing * size * 0.15, y - size * 0.22)]
    pygame.draw.polygon(screen, darker, fin)

    # Body and lighter belly
    body = pygame.Rect(0, 0, size, size * 0.6)
    body.center = (x, y)
    pygame.draw.ellipse(screen, color, body)
    lighter = tuple(min(255, c + 60) for c in color)
    belly = pygame.Rect(0, 0, size * 0.6, size * 0.22)
    belly.center = (x + facing * size * 0.05, y + size * 0.12)
    pygame.draw.ellipse(screen, lighter, belly)

    # Eye
    eye_x, eye_y = x + facing * size * 0.27, y - size * 0.07
    eye_radius = max(2, size * 0.08)
    pygame.draw.circle(screen, WHITE, (eye_x, eye_y), eye_radius)
    pygame.draw.circle(screen, BLACK, (eye_x + facing * eye_radius * 0.3, eye_y), eye_radius * 0.55)

    # Bigger fish get an angry eyebrow so you know to stay away
    if angry:
        brow_start = (eye_x - facing * eye_radius * 1.2, eye_y - eye_radius * 1.8)
        brow_end = (eye_x + facing * eye_radius * 1.2, eye_y - eye_radius * 0.9)
        pygame.draw.line(screen, BLACK, brow_start, brow_end, max(2, int(size / 25)))

class FishyGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Fishy")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 80)
        self.small_font = pygame.font.Font(None, 28)

        # Water background is drawn once and reused every frame
        self.background = self.make_background()
        self.seaweed = [(random.randint(0, WINDOW_WIDTH), random.randint(50, 120), random.uniform(0, 6))
                        for _ in range(12)]
        self.bubbles = []

        self.high_score = self.load_high_score()
        self.state = "menu"  # "menu", "playing", "paused", "game_over" or "won"
        self.particles = []
        self.time = 0

        # Game state
        self.reset_game()

    def make_background(self):
        surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        # Water fades from light at the top to dark at the bottom
        for y in range(WATER_TOP, WATER_BOTTOM):
            t = (y - WATER_TOP) / (WATER_BOTTOM - WATER_TOP)
            color = tuple(int(WATER_TOP_COLOR[c] + (WATER_BOTTOM_COLOR[c] - WATER_TOP_COLOR[c]) * t) for c in range(3))
            pygame.draw.line(surface, color, (0, y), (WINDOW_WIDTH, y))
        # Light rays coming down from the surface
        rays = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        for x in range(60, WINDOW_WIDTH, 170):
            pygame.draw.polygon(rays, (255, 255, 255, 18),
                                [(x, WATER_TOP), (x + 60, WATER_TOP), (x + 160, WATER_BOTTOM), (x + 60, WATER_BOTTOM)])
        surface.blit(rays, (0, 0))
        # Sandy floor with a few pebbles
        pygame.draw.rect(surface, SAND, (0, WATER_BOTTOM, WINDOW_WIDTH, SAND_HEIGHT))
        for _ in range(40):
            px, py = random.randint(0, WINDOW_WIDTH), random.randint(WATER_BOTTOM + 5, WINDOW_HEIGHT - 5)
            pygame.draw.circle(surface, SAND_DARK, (px, py), random.randint(2, 4))
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
        self.player_x = WINDOW_WIDTH / 2
        self.player_y = (WATER_TOP + WATER_BOTTOM) / 2
        self.player_dx = 0
        self.player_dy = 0
        self.player_size = START_SIZE
        self.facing = 1
        self.fish = []
        self.spawn_timer = 0
        self.safe_timer = SAFE_TIME
        self.score = 0
        self.new_high_score = False

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

            elif self.state == "playing":
                if event.key == pygame.K_p:
                    self.state = "paused"

            elif self.state == "paused":
                if event.key in (pygame.K_p, pygame.K_SPACE):
                    self.state = "playing"

            elif self.state in ("game_over", "won"):
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
        self.update_bubbles()

        if self.state != "playing":
            return

        self.move_player()
        self.safe_timer = max(0, self.safe_timer - dt)

        # Spawn new fish every so often
        self.spawn_timer -= dt
        if self.spawn_timer <= 0 and len(self.fish) < MAX_FISH:
            self.fish.append(Fish(self.player_size))
            self.spawn_timer = random.randint(*SPAWN_EVERY)

        for fish in self.fish:
            fish.update(self.time)
        self.fish = [fish for fish in self.fish if not fish.off_screen()]

        # Eat smaller fish, get eaten by bigger ones
        player_box = hitbox(self.player_x, self.player_y, self.player_size)
        for fish in self.fish[:]:
            if not player_box.colliderect(fish.hitbox()):
                continue
            if fish.size < self.player_size:
                self.eat(fish)
            elif self.safe_timer == 0:
                self.end_game("game_over")
                return

        if self.player_size >= WIN_SIZE:
            self.end_game("won")

    def move_player(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_dx -= ACCELERATION
            self.facing = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_dx += ACCELERATION
            self.facing = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player_dy -= ACCELERATION
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player_dy += ACCELERATION

        # Water slowly brings you to a stop
        self.player_dx = max(-MAX_SPEED, min(MAX_SPEED, self.player_dx * WATER_DRAG))
        self.player_dy = max(-MAX_SPEED, min(MAX_SPEED, self.player_dy * WATER_DRAG))
        self.player_x += self.player_dx
        self.player_y += self.player_dy

        # Stay inside the water
        half_width, half_height = self.player_size / 2, self.player_size * 0.3
        self.player_x = max(half_width, min(WINDOW_WIDTH - half_width, self.player_x))
        self.player_y = max(WATER_TOP + half_height, min(WATER_BOTTOM - half_height, self.player_y))

        # Tiny bubbles trail behind you when swimming fast
        if abs(self.player_dx) + abs(self.player_dy) > 4 and random.random() < 0.2:
            self.bubbles.append([self.player_x - self.facing * self.player_size / 2, self.player_y, random.uniform(2, 4)])

    def eat(self, fish):
        self.fish.remove(fish)
        self.player_size = min(WIN_SIZE, self.player_size + fish.size * GROWTH)
        self.score += max(1, int(fish.size / 3))
        self.burst(fish.x, fish.y, fish.color)

    def end_game(self, result):
        self.state = result
        if result == "game_over":
            self.burst(self.player_x, self.player_y, PLAYER_COLOR)
        if self.score > self.high_score:
            self.high_score = self.score
            self.new_high_score = True
            self.save_high_score()

    def burst(self, x, y, color):
        # Little explosion of particles
        for _ in range(18):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.05, 0.2)
            self.particles.append({
                "x": x, "y": y,
                "vx": math.cos(angle) * speed, "vy": math.sin(angle) * speed,
                "life": random.uniform(300, 600), "color": color,
            })

    def update_particles(self, dt):
        for particle in self.particles:
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["life"] -= dt
        self.particles = [p for p in self.particles if p["life"] > 0]

    def update_bubbles(self):
        # Background bubbles drift up from the sand
        if random.random() < 0.05:
            self.bubbles.append([random.randint(0, WINDOW_WIDTH), WATER_BOTTOM, random.uniform(2, 6)])
        for bubble in self.bubbles:
            bubble[1] -= bubble[2] * 0.5
            bubble[0] += math.sin((self.time + bubble[1]) / 200) * 0.3
        self.bubbles = [b for b in self.bubbles if b[1] > WATER_TOP]

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.draw_seaweed()

        for x, y, radius in self.bubbles:
            pygame.draw.circle(self.screen, (200, 230, 255), (x, y), radius, 1)

        for fish in self.fish:
            draw_fish(self.screen, fish.x, fish.y, fish.size, fish.facing, fish.color,
                      self.time + fish.wiggle_offset, angry=fish.size >= self.player_size)

        # Player blinks while it can't be eaten
        blinking = self.safe_timer > 0 and (self.time // 120) % 2 == 0
        if self.state != "game_over" and not blinking:
            draw_fish(self.screen, self.player_x, self.player_y, self.player_size, self.facing, PLAYER_COLOR, self.time)

        self.draw_particles()
        self.draw_hud()

        if self.state == "menu":
            self.draw_overlay("FISHY", [
                "Eat fish smaller than you to grow",
                "Stay away from bigger fish (they look angry!)",
                "Arrow keys or WASD to swim",
                "Press SPACE to start",
            ])
        elif self.state == "paused":
            self.draw_overlay("PAUSED", ["Press P to continue"])
        elif self.state in ("game_over", "won"):
            title = "YOU WIN!" if self.state == "won" else "EATEN!"
            lines = []
            if self.state == "won":
                lines.append("You're the biggest fish in the sea!")
            lines.append(f"Score: {self.score}    Best: {self.high_score}")
            if self.new_high_score:
                lines.append("NEW HIGH SCORE!")
            lines.append("SPACE to play again   M for menu")
            self.draw_overlay(title, lines)

        pygame.display.flip()

    def draw_seaweed(self):
        for x, height, offset in self.seaweed:
            # Each strand sways a little, more at the top
            points = []
            for k in range(8):
                y = WATER_BOTTOM - height * k / 7
                sway = math.sin(self.time / 700 + offset + k * 0.5) * k * 2
                points.append((x + sway, y))
            pygame.draw.lines(self.screen, SEAWEED, False, points, 6)

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

        # Growth bar: how close you are to being the biggest fish
        bar = pygame.Rect(0, 0, 220, 16)
        bar.center = (WINDOW_WIDTH // 2, HUD_HEIGHT // 2)
        progress = (self.player_size - START_SIZE) / (WIN_SIZE - START_SIZE)
        pygame.draw.rect(self.screen, BLACK, bar, border_radius=8)
        pygame.draw.rect(self.screen, PLAYER_COLOR, (bar.x, bar.y, bar.width * progress, bar.height), border_radius=8)
        pygame.draw.rect(self.screen, WHITE, bar, 2, border_radius=8)

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
    game = FishyGame()
    game.run()
