import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
BIRD_X = 80
BIRD_RADIUS = 15
GRAVITY = 0.5
FLAP_STRENGTH = -8
PIPE_WIDTH = 70
PIPE_GAP = 160
PIPE_SPEED = 3
PIPE_SPACING = 220  # Horizontal distance between pipes

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
SKY = (135, 206, 235)
GREEN = (0, 180, 0)
YELLOW = (255, 220, 0)
RED = (255, 0, 0)

# FPS
FPS = 60

class Pipe:
    def __init__(self, x):
        self.x = x
        self.gap_y = random.randint(120, WINDOW_HEIGHT - 120 - PIPE_GAP)
        self.passed = False

    def top_rect(self):
        return pygame.Rect(self.x, 0, PIPE_WIDTH, self.gap_y)

    def bottom_rect(self):
        bottom_y = self.gap_y + PIPE_GAP
        return pygame.Rect(self.x, bottom_y, PIPE_WIDTH, WINDOW_HEIGHT - bottom_y)

class FlappyBirdGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Flappy Bird")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)

        # Game state
        self.reset_game()

    def reset_game(self):
        self.bird_y = WINDOW_HEIGHT // 2
        self.bird_velocity = 0
        self.pipes = [Pipe(WINDOW_WIDTH + i * PIPE_SPACING) for i in range(3)]
        self.score = 0
        self.started = False
        self.game_over = False

    def handle_events(self):
        for event in pygame.event.get():
            # ESC quits too (goes back to the games menu)
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                return False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if self.game_over:
                    self.reset_game()
                else:
                    # Flap
                    self.started = True
                    self.bird_velocity = FLAP_STRENGTH

        return True

    def update(self):
        if self.game_over or not self.started:
            return

        # Apply gravity
        self.bird_velocity += GRAVITY
        self.bird_y += self.bird_velocity

        # Move pipes and recycle the ones that leave the screen
        for pipe in self.pipes:
            pipe.x -= PIPE_SPEED
        if self.pipes[0].x + PIPE_WIDTH < 0:
            self.pipes.pop(0)
            self.pipes.append(Pipe(self.pipes[-1].x + PIPE_SPACING))

        # Score when the bird passes a pipe
        for pipe in self.pipes:
            if not pipe.passed and pipe.x + PIPE_WIDTH < BIRD_X:
                pipe.passed = True
                self.score += 1

        # Check collision with ground, ceiling and pipes
        bird_rect = pygame.Rect(BIRD_X - BIRD_RADIUS, self.bird_y - BIRD_RADIUS,
                                BIRD_RADIUS * 2, BIRD_RADIUS * 2)
        if self.bird_y + BIRD_RADIUS >= WINDOW_HEIGHT or self.bird_y - BIRD_RADIUS <= 0:
            self.game_over = True
        for pipe in self.pipes:
            if bird_rect.colliderect(pipe.top_rect()) or bird_rect.colliderect(pipe.bottom_rect()):
                self.game_over = True

    def draw(self):
        self.screen.fill(SKY)

        # Draw pipes
        for pipe in self.pipes:
            pygame.draw.rect(self.screen, GREEN, pipe.top_rect())
            pygame.draw.rect(self.screen, GREEN, pipe.bottom_rect())

        # Draw bird
        pygame.draw.circle(self.screen, YELLOW, (BIRD_X, int(self.bird_y)), BIRD_RADIUS)
        pygame.draw.circle(self.screen, BLACK, (BIRD_X + 6, int(self.bird_y) - 4), 3)  # Eye

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw start / game over message
        if not self.started:
            self.draw_message("Press SPACE to flap", WHITE)
        elif self.game_over:
            self.draw_message("GAME OVER! SPACE to restart", RED)

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
    game = FlappyBirdGame()
    game.run()
