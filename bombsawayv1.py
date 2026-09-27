import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors (RGB)
BLACK = (10, 10, 10)
WHITE = (255, 255, 255)
RED = (255, 50, 0)
ORANGE = (255, 120, 0)
YELLOW = (255, 230, 0)
GREY = (100, 100, 100)
BLUE = (50, 150, 255)

# Setup Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("💣 BOMB CHAOS & FIRE 🔥")
clock = pygame.time.Clock()

# --- GAME OBJECT CLASSES ---

class Player:
    def __init__(self):
        self.width = 40
        self.height = 40
        self.x = WIDTH // 2
        self.y = HEIGHT - self.height - 10
        self.speed = 7
        self.health = 100

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.width:
            self.x += self.speed

    def draw(self, surface):
        # Draw player as a blue defensive block
        pygame.draw.rect(surface, BLUE, (self.x, self.y, self.width, self.height))
        # Draw health bar text
        font = pygame.font.SysFont(None, 30)
        health_text = font.render(f"HP: {self.health}", True, WHITE)
        surface.blit(health_text, (10, 10))

class Bomb:
    def __init__(self):
        self.radius = 15
        self.x = random.randint(self.radius, WIDTH - self.radius)
        self.y = -self.radius
        self.speed = random.randint(4, 8)

    def update(self):
        self.y += self.speed

    def draw(self, surface):
        # Draw bomb body
        pygame.draw.circle(surface, GREY, (self.x, int(self.y)), self.radius)
        # Draw a little spark fuse
        pygame.draw.line(surface, YELLOW, (self.x, int(self.y) - self.radius), (self.x + 5, int(self.y) - self.radius - 5), 2)

class FireParticle:
    def __init__(self, x, y, explode=False):
        self.x = x
        self.y = y
        # Chaotic explosion speeds or general fire drift
        if explode:
            self.vx = random.choice([-1, 1]) * random.uniform(2, 7)
            self.vy = random.choice([-1, 1]) * random.uniform(2, 7)
        else:
            self.vx = random.uniform(-1.5, 1.5)
            self.vy = random.uniform(-3, -0.5)
            
        self.radius = random.randint(4, 8)
        self.life = 255  # Used for transparency fading
        self.color = random.choice([RED, ORANGE, YELLOW])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 6  # Fade out speed
        if self.radius > 0.2:
            self.radius -= 0.1  # Shrink as it burns

    def draw(self, surface):
        if self.life > 0 and self.radius > 0:
            # Create a surf with per-pixel alpha for realistic fire glow
            fire_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(fire_surf, (*self.color, self.life), (int(self.radius), int(self.radius)), int(self.radius))
            surface.blit(fire_surf, (int(self.x - self.radius), int(self.y - self.radius)))

# --- MAIN GAME LOOP ---

def main():
    player = Player()
    bombs = []
    particles = []
    score = 0
    font = pygame.font.SysFont(None, 30)

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Input tracking
        keys = pygame.key.get_pressed()
        player.move(keys)

        # Spawn Bombs (Increases intensity over time)
        spawn_chance = 0.03 + (score * 0.001)
        if random.random() < min(spawn_chance, 0.15):
            bombs.append(Bomb())

        # Update and Draw Bombs
        for bomb in bombs[:]:
            bomb.update()
            bomb.draw(screen)

            # Check if bomb hits ground -> Explode!
            if bomb.y >= HEIGHT - 20:
                bombs.remove(bomb)
                score += 10
                # Generate massive fire explosion particles
                for _ in range(30):
                    particles.append(FireParticle(bomb.x, bomb.y, explode=True))

            # Check if bomb hits player
            elif (player.x < bomb.x < player.x + player.width) and (player.y < bomb.y + bomb.radius < player.y + player.height):
                bombs.remove(bomb)
                player.health -= 20
                for _ in range(40):
                    particles.append(FireParticle(bomb.x, bomb.y, explode=True))

        # Ambient ground fire chaos (keeps things burning on the floor)
        if random.random() < 0.4:
            particles.append(FireParticle(random.randint(0, WIDTH), HEIGHT - 10))

        # Update and Draw Fire Particles
        for particle in particles[:]:
            particle.update()
            particle.draw(screen)
            if particle.life <= 0 or particle.radius <= 0:
                particles.remove(particle)

        # Draw Player
        player.draw(screen)

        # Draw Score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH - 120, 10))

        # Game Over Condition
        if player.health <= 0:
            game_over_text = pygame.font.SysFont(None, 74).render("CHAOS DIED", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - 170, HEIGHT // 2 - 40))
            pygame.display.flip()
            pygame.time.wait(2000)
            running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
