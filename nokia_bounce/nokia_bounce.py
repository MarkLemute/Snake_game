import pygame

# Initialize Pygame
pygame.init()

# Constants
TILE_SIZE = 40
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 480  # 12 rows of tiles
BALL_RADIUS = 15
ACCELERATION = 0.5
FRICTION = 0.9
MAX_SPEED = 5
GRAVITY = 0.6
MAX_FALL_SPEED = 12
JUMP_STRENGTH = -13
BOUNCE = 0.35          # How much the ball bounces back when it lands
MIN_BOUNCE_SPEED = 4   # Landing slower than this doesn't bounce
START_LIVES = 3

# Level map
# '#' = brick, '^' = spikes, 'O' = ring, 'S' = start, 'C' = checkpoint, 'E' = exit
LEVEL = [
    "############################################################",
    "#                                                          #",
    "#                                                          #",
    "#                                                          #",
    "#                                                          #",
    "#                                  O                       #",
    "#        O              O                                  #",
    "#                                                          #",
    "#                    ##           ###                      #",
    "#       ###         ###                                    #",
    "# S           ^^   ####    C  ^^^        O  ^^   ^^      E #",
    "############################################################",
]

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY = (120, 190, 230)
BRICK = (180, 60, 40)
MORTAR = (120, 40, 25)
SPIKE = (90, 90, 100)
RING = (255, 210, 0)
RING_DONE = (150, 150, 150)
RED = (220, 0, 0)
ORANGE = (255, 150, 0)
GREEN = (0, 180, 0)

# FPS
FPS = 60

class NokiaBounceGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Bounce")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.level_width = len(LEVEL[0]) * TILE_SIZE

        # Game state
        self.reset_game()

    def reset_game(self):
        # Read the level map into tiles
        self.bricks = set()
        self.spikes = []
        self.rings = []
        for row, line in enumerate(LEVEL):
            for col, char in enumerate(line):
                x, y = col * TILE_SIZE, row * TILE_SIZE
                if char == "#":
                    self.bricks.add((col, row))
                elif char == "^":
                    # Spike hitbox is the lower half of the tile
                    self.spikes.append(pygame.Rect(x + 5, y + TILE_SIZE // 2, TILE_SIZE - 10, TILE_SIZE // 2))
                elif char == "O":
                    self.rings.append({"rect": pygame.Rect(x + 10, y, TILE_SIZE - 20, TILE_SIZE), "collected": False})
                elif char == "S":
                    self.start_point = (x + TILE_SIZE // 2, y + TILE_SIZE // 2)
                elif char == "C":
                    # Tall touch zone so the checkpoint can't be bounced over
                    self.checkpoint = pygame.Rect(x, y - TILE_SIZE * 3, TILE_SIZE, TILE_SIZE * 4)
                elif char == "E":
                    self.exit = pygame.Rect(x, y - TILE_SIZE, TILE_SIZE, TILE_SIZE * 2)

        self.respawn_point = self.start_point
        self.checkpoint_reached = False
        self.lives = START_LIVES
        self.game_over = False
        self.won = False
        self.respawn()

    def respawn(self):
        self.ball_x, self.ball_y = self.respawn_point
        self.ball_dx = 0
        self.ball_dy = 0
        self.on_ground = False

    def ball_rect(self):
        return pygame.Rect(self.ball_x - BALL_RADIUS, self.ball_y - BALL_RADIUS,
                           BALL_RADIUS * 2, BALL_RADIUS * 2)

    def bricks_touching(self, rect):
        # Only check the tiles the ball overlaps instead of every brick
        hits = []
        for col in range(rect.left // TILE_SIZE, (rect.right - 1) // TILE_SIZE + 1):
            for row in range(rect.top // TILE_SIZE, (rect.bottom - 1) // TILE_SIZE + 1):
                if (col, row) in self.bricks:
                    hits.append(pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        return hits

    def all_rings_collected(self):
        return all(ring["collected"] for ring in self.rings)

    def handle_events(self):
        for event in pygame.event.get():
            # ESC quits too (goes back to the games menu)
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return False

            # Reset game on SPACE
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and (self.game_over or self.won):
                self.reset_game()

        return True

    def update(self):
        if self.game_over or self.won:
            return

        # Roll left / right with held arrow keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.ball_dx -= ACCELERATION
        elif keys[pygame.K_RIGHT]:
            self.ball_dx += ACCELERATION
        else:
            self.ball_dx *= FRICTION
        self.ball_dx = max(-MAX_SPEED, min(MAX_SPEED, self.ball_dx))

        # Jump (holding the key keeps bouncing)
        if (keys[pygame.K_UP] or keys[pygame.K_SPACE]) and self.on_ground:
            self.ball_dy = JUMP_STRENGTH

        # Apply gravity
        self.ball_dy = min(self.ball_dy + GRAVITY, MAX_FALL_SPEED)

        # Move horizontally, then push out of any brick we hit
        # (Velocity is only changed after the loop, so touching two bricks at once
        # still pushes the ball out the same way for both)
        self.ball_x += self.ball_dx
        hit_wall = False
        for brick in self.bricks_touching(self.ball_rect()):
            hit_wall = True
            if self.ball_dx > 0:
                self.ball_x = brick.left - BALL_RADIUS
            elif self.ball_dx < 0:
                self.ball_x = brick.right + BALL_RADIUS
        if hit_wall:
            self.ball_dx = 0

        # Move vertically, then push out of any brick we hit
        self.ball_y += self.ball_dy
        self.on_ground = False
        hit_floor_or_ceiling = False
        for brick in self.bricks_touching(self.ball_rect()):
            hit_floor_or_ceiling = True
            if self.ball_dy > 0:
                self.ball_y = brick.top - BALL_RADIUS
                self.on_ground = True
            elif self.ball_dy < 0:
                self.ball_y = brick.bottom + BALL_RADIUS
        if hit_floor_or_ceiling:
            if self.on_ground and self.ball_dy > MIN_BOUNCE_SPEED:
                # Small bounce on landing, like the original
                self.ball_dy = -self.ball_dy * BOUNCE
            else:
                self.ball_dy = 0

        ball = self.ball_rect()

        # Collect rings
        for ring in self.rings:
            if not ring["collected"] and ball.colliderect(ring["rect"]):
                ring["collected"] = True

        # Reach the checkpoint
        if ball.colliderect(self.checkpoint):
            self.checkpoint_reached = True
            self.respawn_point = (self.checkpoint.centerx, self.checkpoint.bottom - TILE_SIZE // 2)

        # Hit spikes: lose a life
        if ball.collidelist(self.spikes) != -1:
            self.lives -= 1
            if self.lives == 0:
                self.game_over = True
            else:
                self.respawn()

        # Exit only opens once every ring is collected
        if self.all_rings_collected() and ball.colliderect(self.exit):
            self.won = True

    def draw(self):
        self.screen.fill(SKY)

        # Camera follows the ball, but stops at the level edges
        camera_x = int(max(0, min(self.ball_x - WINDOW_WIDTH // 2, self.level_width - WINDOW_WIDTH)))

        # Draw bricks
        for col, row in self.bricks:
            rect = pygame.Rect(col * TILE_SIZE - camera_x, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            if rect.right < 0 or rect.left > WINDOW_WIDTH:
                continue
            pygame.draw.rect(self.screen, BRICK, rect)
            pygame.draw.rect(self.screen, MORTAR, rect, 2)
            pygame.draw.line(self.screen, MORTAR, (rect.left, rect.centery), (rect.right, rect.centery), 2)

        # Draw spikes
        for spike in self.spikes:
            left = spike.left - camera_x
            points = [(left, spike.bottom), (spike.centerx - camera_x, spike.top - 15), (spike.right - camera_x, spike.bottom)]
            pygame.draw.polygon(self.screen, SPIKE, points)

        # Draw rings
        for ring in self.rings:
            color = RING_DONE if ring["collected"] else RING
            pygame.draw.ellipse(self.screen, color, ring["rect"].move(-camera_x, 0), 5)

        # Draw checkpoint
        checkpoint_color = GREEN if self.checkpoint_reached else ORANGE
        pygame.draw.circle(self.screen, checkpoint_color, (self.checkpoint.centerx - camera_x, self.checkpoint.bottom - TILE_SIZE // 2), 10)

        # Draw exit (grey until all rings are collected)
        exit_color = GREEN if self.all_rings_collected() else SPIKE
        pygame.draw.rect(self.screen, exit_color, self.exit.move(-camera_x, 0))
        pygame.draw.rect(self.screen, BLACK, self.exit.move(-camera_x, 0), 2)

        # Draw ball with a highlight
        ball_pos = (int(self.ball_x) - camera_x, int(self.ball_y))
        pygame.draw.circle(self.screen, RED, ball_pos, BALL_RADIUS)
        pygame.draw.circle(self.screen, WHITE, (ball_pos[0] - 5, ball_pos[1] - 5), 4)

        # Draw lives and rings
        rings_done = sum(ring["collected"] for ring in self.rings)
        hud_text = self.font.render(f"Lives: {self.lives}   Rings: {rings_done}/{len(self.rings)}", True, WHITE)
        self.screen.blit(hud_text, (10, 8))

        # Draw game over / win message
        if self.game_over:
            self.draw_message("GAME OVER! Press SPACE to restart", RED)
        elif self.won:
            self.draw_message("YOU WIN! Press SPACE to play again", GREEN)

        pygame.display.flip()

    def draw_message(self, text, color):
        message = self.font.render(text, True, color)
        text_rect = message.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        pygame.draw.rect(self.screen, BLACK, text_rect.inflate(20, 20))
        self.screen.blit(message, text_rect)

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == "__main__":
    game = NokiaBounceGame()
    game.run()
