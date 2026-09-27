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

# Setup Screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🔥 CLICK TO EXPLODE 🔥")
clock = pygame.time.Clock()

# --- GAME OBJECT CLASSES ---

class FireParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Chaotic, high-velocity explosion speeds spraying in all directions
        self.vx = random.uniform(-8, 8)
        self.vy = random.uniform(-8, 8)
            
        self.radius = random.randint(6, 14)
        self.life = 255  # Used for transparency fading
        self.color = random.choice([RED, ORANGE, YELLOW])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 5  # Speed of the fade out
        if self.radius > 0.2:
            self.radius -= 0.15  # Shrink as it burns out

    def draw(self, surface):
        if self.life > 0 and self.radius > 0:
            # Create a surface with per-pixel alpha for realistic fire glow blending
            fire_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(fire_surf, (*self.color, self.life), (int(self.radius), int(self.radius)), int(self.radius))
            surface.blit(fire_surf, (int(self.x - self.radius), int(self.y - self.radius)))

# --- MAIN GAME LOOP ---

def main():
    particles = []
    explosion_count = 0
    font = pygame.font.SysFont(None, 40)

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(BLACK)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Detect Player Clicking
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left Click
                    mouse_x, mouse_y = event.pos
                    
                    # Count the explosion instantly upon clicking
                    explosion_count += 1 
                    
                    # Generate a massive blast of 75 fire particles at the cursor
                    for _ in range(75):
                        particles.append(FireParticle(mouse_x, mouse_y))

        # Update and Draw Fire Particles
        for particle in particles[:]:
            particle.update()
            particle.draw(screen)
            if particle.life <= 0 or particle.radius <= 0:
                particles.remove(particle)

        # Draw Score Tracker HUD
        score_text = font.render(f"Explosions Triggered: {explosion_count}", True, WHITE)
        screen.blit(score_text, (20, 20))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
