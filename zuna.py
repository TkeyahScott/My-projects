import pygame
import math
import random
import sys

# Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Colors (RGB)
BG_COLOR = (20, 35, 25)
TRACK_COLOR = (45, 65, 50)
GOLD = (230, 180, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Ball Colors Mapping
BALL_COLORS = {
    "red": (240, 50, 50),
    "blue": (50, 120, 240),
    "green": (50, 200, 90),
    "yellow": (240, 210, 40)
}
COLOR_KEYS = list(BALL_COLORS.keys())

# Setup Window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🔮 PYTHON ZUMA CLONE")
clock = pygame.time.Clock()

# --- TRACK MATH DEFINITION ---
# Generates a winding spiral path from coordinates calculated via parametric equations
TRACK_POINTS = []
center_x, center_y = WIDTH // 2, HEIGHT // 2

# Generate a smooth spiral track layout
for theta in range(0, 720, 2):
    rad = math.radians(theta)
    # Shrinking radius creates a spiral leading toward the center danger zone
    r = 340 - (theta * 0.35) 
    x = int(center_x + r * math.cos(rad))
    y = int(center_y + r * math.sin(rad))
    TRACK_POINTS.append((x, y))

# The very end of the spiral path is the danger zone
DANGER_ZONE = TRACK_POINTS[-1] 
BALL_RADIUS = 14
BALL_DIAMETER = BALL_RADIUS * 2

# --- GAME OBJECT CLASSES ---

class RollingBall:
    def __init__(self, color_key, path_index=0):
        self.color_key = color_key
        self.color = BALL_COLORS[color_key]
        self.path_index = path_index  # Position along the TRACK_POINTS list
        self.x, self.y = TRACK_POINTS[int(path_index)]

    def update_position(self):
        # Force position clamp inside valid path track range
        idx = max(0, min(int(self.path_index), len(TRACK_POINTS) - 1))
        self.x, self.y = TRACK_POINTS[idx]

class Projectile:
    def __init__(self, x, y, target_x, target_y, color_key):
        self.x = x
        self.y = y
        self.color_key = color_key
        self.color = BALL_COLORS[color_key]
        self.radius = 12
        self.speed = 14
        
        # Calculate straight vector components toward cursor target
        dx = target_x - x
        dy = target_y - y
        distance = math.hypot(dx, dy)
        self.vx = (dx / distance) * self.speed if distance > 0 else 0
        self.vy = (dy / distance) * self.speed if distance > 0 else 0

    def move(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, WHITE, (int(self.x) - 3, int(self.y) - 3), 3) # Highlight reflection

# --- CORE GAME MATCHING ENGINE ---

def check_matches(chain):
    """Scan chain for consecutive groups of 3+ matching colors and strip them out."""
    if not chain:
        return 0
    
    matches_to_remove = set()
    i = 0
    while i < len(chain):
        current_color = chain[i].color_key
        run = [i]
        j = i + 1
        while j < len(chain) and chain[j].color_key == current_color:
            run.append(j)
            j += 1
        
        if len(run) >= 3:
            for index in run:
                matches_to_remove.add(index)
        i = j
        
    # Re-build chain keeping unmatched elements
    if matches_to_remove:
        new_chain = [chain[k] for k in range(len(chain)) if k not in matches_to_remove]
        chain.clear()
        chain.extend(new_chain)
        return len(matches_to_remove)
    return 0

# --- MAIN LOOP ---

def main():
    # Setup elements
    shooter_x, shooter_y = center_x, center_y
    next_bullet_color = random.choice(COLOR_KEYS)
    
    chain = []
    projectiles = []
    score = 0
    font = pygame.font.SysFont(None, 36)
    
    # Spawn config variables
    spawn_timer = 0
    spawn_delay = 25  # Frames between ball generations
    chain_speed = 0.6  # Default advancement movement rate per frame
    
    game_over = False
    game_won = False

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(BG_COLOR)

        # 1. Render Path Track Lines Overview
        if len(TRACK_POINTS) > 1:
            pygame.draw.lines(screen, TRACK_COLOR, False, TRACK_POINTS, 32)
        # Golden skull destination spot
        pygame.draw.circle(screen, GOLD, DANGER_ZONE, 20)
        pygame.draw.circle(screen, BLACK, DANGER_ZONE, 12)

        # 2. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN and not (game_over or game_won):
                if event.button == 1:  # Fire Bullet
                    mx, my = event.pos
                    projectiles.append(Projectile(shooter_x, shooter_y, mx, my, next_bullet_color))
                    next_bullet_color = random.choice(COLOR_KEYS)

        # 3. Dynamic Rotation Engine for Central Shooter Turret
        mx, my = pygame.mouse.get_pos()
        angle = math.atan2(my - shooter_y, mx - shooter_x)
        
        # Draw shooter geometry baseline
        pygame.draw.circle(screen, (80, 160, 100), (shooter_x, shooter_y), 24)
        # Pointer nozzle vector indicators
        gun_tip_x = shooter_x + 35 * math.cos(angle)
        gun_tip_y = shooter_y + 35 * math.sin(angle)
        pygame.draw.line(screen, WHITE, (shooter_x, shooter_y), (gun_tip_x, gun_tip_y), 8)
        # Display next active loaded ammunition directly on top of center shooter hub
        pygame.draw.circle(screen, BALL_COLORS[next_bullet_color], (shooter_x, shooter_y), 12)

        if not (game_over or game_won):
            # 4. Handle Marble Chain Logic Spawns
            spawn_timer += 1
            if spawn_timer >= spawn_delay and len(chain) < 60:
                # Add new ball to the opening start index loop structure
                chain.insert(0, RollingBall(random.choice(COLOR_KEYS), path_index=0))
                spawn_timer = 0

            # 5. Move Entire Ball Chain Forward
            # Moves the front ball forward, making following balls push right up behind it
            if chain:
                chain[-1].path_index += chain_speed
                chain[-1].update_position()
                
                # Check for critical terminal failures (reached golden core)
                if chain[-1].path_index >= len(TRACK_POINTS) - 1:
                    game_over = True

                # Backward push constraint calculations to compress gaps smoothly
                for idx in range(len(chain) - 2, -1, -1):
                    lead_ball = chain[idx + 1]
                    curr_ball = chain[idx]
                    
                    # Ideal physical path delta matching ball diameter dimensions
                    # Estimate indexing stepping steps 
                    curr_ball.path_index = min(curr_ball.path_index + chain_speed, lead_ball.path_index - 7)
                    curr_ball.update_position()

            # 6. Update Launched Projectiles & Manage Track Intersection Collisions
            for proj in projectiles[:]:
                proj.move()
                proj.draw(screen)

                # Clear bounds checks
                if proj.x < 0 or proj.x > WIDTH or proj.y < 0 or proj.y > HEIGHT:
                    projectiles.remove(proj)
                    continue

                # Scan structural proximity for inserting shot marbles into linear chain indexes
                inserted = False
                for b_idx, ball in enumerate(chain):
                    if math.hypot(proj.x - ball.x, proj.y - ball.y) < (BALL_RADIUS + proj.radius):
                        # Insert bullet right next into position arrays layout sequences
                        new_ball = RollingBall(proj.color_key, path_index=max(0, ball.path_index - 7))
                        chain.insert(b_idx, new_ball)
                        projectiles.remove(proj)
                        inserted = True
                        
                        # Trigger evaluation scanners for match removals
                        eliminated = check_matches(chain)
                        if eliminated:
                            score += eliminated * 10
                        break
                if inserted:
                    continue

        # 7. Render Chain Contents Layout Maps
        for ball in chain:
            pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), BALL_RADIUS)
            pygame.draw.circle(screen, WHITE, (int(ball.x) - 4, int(ball.y) - 4), 3) # Shiny core 3D illusion

        # Display HUD UI metrics overlay values
        score_lbl = font.render(f"SCORE: {score}", True, WHITE)
        screen.blit(score_lbl, (20, 20))

        # Check Win Conditions
        if len(chain) == 0 and score > 0:
            game_won = True

        # Render Terminal End Screen overlays
        if game_over:
            msg = pygame.font.SysFont(None, 64).render("GAME OVER - LOSE", True, (220, 50, 50))
            screen.blit(msg, (WIDTH // 2 - 200, HEIGHT // 2 - 30))
        elif game_won:
            msg = pygame.font.SysFont(None, 64).render("STAGE CLEARED!", True, (50, 220, 100))
            screen.blit(msg, (WIDTH // 2 - 180, HEIGHT // 2 - 30))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
