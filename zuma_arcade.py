import pygame
import math
import random
import sys

# Initialize Pygame
pygame.init()

# Game Constants
WIDTH, HEIGHT = 1000, 750
FPS = 60

# Colors (RGB)
BG_COLOR = (15, 25, 20)
TRACK_COLOR = (38, 54, 42)
GOLD = (235, 190, 35)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREY = (80, 80, 80)
LIGHT_GREY = (180, 180, 180)
BLUE = (50, 120, 240)
GREEN = (50, 200, 90)

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
pygame.display.set_caption("🔮 ADVANCED ZUMA ARCADE")
clock = pygame.time.Clock()

# --- MATH TRACK GENERATORS FOR 3 LEVELS ---
def generate_track_points(level):
    points = []
    if level == 1: # Easy Spiral
        for theta in range(0, 760, 2):
            rad = math.radians(theta)
            r = 340 - (theta * 0.38)
            if r < 10: break
            x = int(500 + r * math.cos(rad))
            y = int(350 + r * math.sin(rad))
            points.append((x, y))
    elif level == 2: # Medium Figure 8 Wave
        for t in range(0, 600):
            rad = math.radians(t * 1.5)
            x = int(500 + 350 * math.sin(rad))
            y = int(350 + 200 * math.sin(rad * 2))
            points.append((x, y))
    else: # Hard Concentric Overlapping Tight Loops
        for theta in range(0, 1200, 2):
            rad = math.radians(theta)
            r = 360 - (theta * 0.28)
            if r < 10: break
            x = int(500 + r * math.sin(rad * 1.5))
            y = int(350 + r * math.cos(rad))
            points.append((x, y))
    return points

# Global System State Variables
leaderboard = [0, 0, 0, 0, 0]
current_state = "MENU" # MENU, PLAYING, GAME_OVER, GAME_WON
current_level = 1
is_paused = False
is_muted = False
score = 0

# --- CLASSES ---

class RollingBall:
    def __init__(self, color_key, path_index=0):
        self.color_key = color_key
        self.color = BALL_COLORS[color_key]
        self.path_index = path_index
        self.x, self.y = 0, 0

    def update_position(self, track_points):
        idx = max(0, min(int(self.path_index), len(track_points) - 1))
        self.x, self.y = track_points[idx]

class Projectile:
    def __init__(self, x, y, target_x, target_y, color_key):
        self.x = x
        self.y = y
        self.color_key = color_key
        self.color = BALL_COLORS[color_key]
        self.radius = 14
        self.speed = 16
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
        pygame.draw.circle(surface, WHITE, (int(self.x) - 4, int(self.y) - 4), 3)

class BurstParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(2, 6)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.radius = random.randint(4, 8)
        self.alpha = 255

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.alpha -= 8
        if self.radius > 0.2:
            self.radius -= 0.1

    def draw(self, surface):
        if self.alpha > 0 and self.radius > 0:
            p_surf = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(p_surf, (*self.color, self.alpha), (int(self.radius), int(self.radius)), int(self.radius))
            surface.blit(p_surf, (int(self.x - self.radius), int(self.y - self.radius)))

class Button:
    def __init__(self, x, y, w, h, text, base_color, hover_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.base_color = base_color
        self.hover_color = hover_color

    def draw(self, surface, font):
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.base_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, WHITE, self.rect, width=2, border_radius=8)
        lbl = font.render(self.text, True, WHITE)
        surface.blit(lbl, (self.rect.x + (self.rect.w - lbl.get_width()) // 2, self.rect.y + (self.rect.h - lbl.get_height()) // 2))

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

# --- SYSTEM UTILITIES ---
def play_beep(freq, duration):
    if is_muted: return
    try:
        sample_rate = 22050
        n_samples = int(sample_rate * duration)
        buf = bytearray()
        for i in range(n_samples):
            t = float(i) / sample_rate
            val = 127 if (int(t * freq * 2) % 2 == 0) else -128
            buf.append(val & 0xFF)
        sound = pygame.mixer.Sound(buffer=buf)
        sound.play()
    except:
        pass

def check_matches(chain, particles):
    if not chain: return 0
    matches = set()
    i = 0
    while i < len(chain):
        color = chain[i].color_key
        run = [i]
        j = i + 1
        while j < len(chain) and chain[j].color_key == color:
            run.append(j)
            j += 1
        if len(run) >= 3:
            for idx in run: matches.add(idx)
        i = j

    if matches:
        play_beep(523, 0.15)
        for idx in sorted(matches, reverse=True):
            ball = chain[idx]
            for _ in range(25):
                particles.append(BurstParticle(ball.x, ball.y, ball.color))
            chain.pop(idx)
        return len(matches)
    return 0

def update_leaderboard(new_score):
    global leaderboard
    leaderboard.append(new_score)
    leaderboard = sorted(list(set(leaderboard)), reverse=True)[:5]

# --- MAIN ENGINE RUNNER ---
def main():
    global current_state, current_level, is_paused, is_muted, score
    
    font_sm = pygame.font.SysFont(None, 24)
    font_md = pygame.font.SysFont(None, 36)
    font_lg = pygame.font.SysFont(None, 64)

    # Track data caching
    track_points = generate_track_points(current_level)
    
    # State items
    chain = []
    projectiles = []
    particles = []
    next_color = random.choice(COLOR_KEYS)
    
    spawn_timer = 0
    spawn_delay = 18 # Tightly packed spacing
    base_chain_speed = 0.28 # Slower pace base rate
    
    # Interface Buttons definitions
    menu_btn_play = Button(150, 480, 220, 50, "PLAY NOW (LVL 1)", GREEN, (40, 170, 75))
    menu_btn_lvl2 = Button(390, 480, 220, 50, "PLAY LEVEL 2", BLUE, (40, 100, 210))
    menu_btn_lvl3 = Button(630, 480, 220, 50, "PLAY LEVEL 3", (200, 50, 50), (170, 40, 40))
    
    hud_pause = Button(20, 700, 100, 35, "PAUSE", GREY, LIGHT_GREY)
    hud_mute = Button(130, 700, 100, 35, "MUTE", GREY, LIGHT_GREY)
    hud_restart = Button(240, 700, 110, 35, "RESTART", GREY, LIGHT_GREY)
    hud_home = Button(360, 700, 100, 35, "HOME", GREY, LIGHT_GREY)
    
    retry_btn = Button(320, 480, 160, 50, "TRY AGAIN", GREEN, (40, 170, 75))
    home_btn = Button(520, 480, 160, 50, "HOME", BLUE, (40, 100, 210))

    def reset_game(level):
        nonlocal chain, projectiles, particles, next_color, spawn_timer
        global score, current_level, is_paused, track_points
        current_level = level
        track_points = generate_track_points(current_level)
        chain.clear()
        projectiles.clear()
        particles.clear()
        score = 0
        spawn_timer = 0
        is_paused = False
        next_color = random.choice(COLOR_KEYS)

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(BG_COLOR)
        
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        # --- MENU STATE RENDERER ---
        if current_state == "MENU":
            title = font_lg.render("🔮 PY-ZUMA CHAOS ARCADE", True, GOLD)
            screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
            
            # Leaderboard rendering
            lead_title = font_md.render("🏆 LOCAL LEADERBOARD (TOP 5)", True, WHITE)
            screen.blit(lead_title, (WIDTH // 2 - lead_title.get_width() // 2, 180))
            for r_idx, high_score in enumerate(leaderboard):
                score_text = font_md.render(f"Rank {r_idx + 1}: {high_score} PTS", True, LIGHT_GREY if high_score == 0 else GOLD)
                screen.blit(score_text, (WIDTH // 2 - 120, 230 + r_idx * 35))

            menu_btn_play.draw(screen, font_md)
            menu_btn_lvl2.draw(screen, font_md)
            menu_btn_lvl3.draw(screen, font_md)
            
            for event in events:
                if menu_btn_play.is_clicked(event):
                    reset_game(1)
                    current_state = "PLAYING"
                elif menu_btn_lvl2.is_clicked(event):
                    reset_game(2)
                    current_state = "PLAYING"
                elif menu_btn_lvl3.is_clicked(event):
                    reset_game(3)
                    current_state = "PLAYING"

        # --- PLAYING STATE RENDERER ---
        elif current_state == "PLAYING":
            # Track rendering
            if len(track_points) > 1:
                pygame.draw.lines(screen, TRACK_COLOR, False, track_points, 32)
            danger_zone = track_points[-1]
            pygame.draw.circle(screen, GOLD, danger_zone, 22)
            pygame.draw.circle(screen, BLACK, danger_zone, 14)

            # Draw Shooter Turret
            s_x, s_y = 500, 350
            mx, my = pygame.mouse.get_pos()
            angle = math.atan2(my - s_y, mx - s_x)
            pygame.draw.circle(screen, (55, 95, 70), (s_x, s_y), 26)
            tip_x = s_x + 38 * math.cos(angle)
            tip_y = s_y + 38 * math.sin(angle)
            pygame.draw.line(screen, WHITE, (s_x, s_y), (tip_x, tip_y), 8)
            pygame.draw.circle(screen, BALL_COLORS[next_color], (s_x, s_y), 12)

            # HUD Navigation Controls panel
            hud_pause.text = "RESUME" if is_paused else "PAUSE"
            hud_mute.text = "UNMUTE" if is_muted else "MUTE"
            hud_pause.draw(screen, font_sm)
            hud_mute.draw(screen, font_sm)
            hud_restart.draw(screen, font_sm)
            hud_home.draw(screen, font_sm)

            # Check HUD Interactions
            for event in events:
                if hud_pause.is_clicked(event): is_paused = not is_paused
                elif hud_mute.is_clicked(event): is_muted = not is_muted
                elif hud_restart.is_clicked(event): reset_game(current_level)
                elif hud_home.is_clicked(event): current_state = "MENU"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not is_paused:
                    if not (hud_pause.rect.collidepoint(event.pos) or hud_mute.rect.collidepoint(event.pos) or hud_restart.rect.collidepoint(event.pos) or hud_home.rect.collidepoint(event.pos)):
                        projectiles.append(Projectile(s_x, s_y, event.pos[0], event.pos[1], next_color))
                        play_beep(880, 0.05)
                        next_color = random.choice(COLOR_KEYS)

            # Simulation updates if not frozen
            if not is_paused:
                spawn_timer += 1
                level_max_capacity = 40 + current_level * 10
                if spawn_timer >= spawn_delay and len(chain) < level_max_capacity:
                    chain.insert(0, RollingBall(random.choice(COLOR_KEYS), path_index=0))
                    spawn_timer = 0

                # Ball Chain Advancements
                level_speed_modifier = base_chain_speed * (1.0 + (current_level - 1) * 0.35)
                if chain:
                    chain[-1].path_index += level_speed_modifier
                    chain[-1].update_position(track_points)
                    
                    if chain[-1].path_index >= len(track_points) - 1:
                        update_leaderboard(score)
                        current_state = "GAME_OVER"

                    # Anti-Gap Packed Compression Engine
                    for idx in range(len(chain) - 2, -1, -1):
                        lead = chain[idx + 1]
                        curr = chain[idx]
                        curr.path_index = min(curr.path_index + level_speed_modifier, lead.path_index - 7)
                        curr.update_position(track_points)

                # Projectile Updates
                for proj in projectiles[:]:
                    proj.move()
                    if proj.x < 0 or proj.x > WIDTH or proj.y < 0 or proj.y > HEIGHT:
                        projectiles.remove(proj)
                        continue

                    for b_idx, ball in enumerate(chain):
                        if math.hypot(proj.x - ball.x, proj.y - ball.y) < (14 + proj.radius):
                            new_ball = RollingBall(proj.color_key, path_index=max(0, ball.path_index - 7))
                            chain.insert(b_idx, new_ball)
                            projectiles.remove(proj)
                            
                            matches_removed = check_matches(chain, particles)
                            if matches_removed:
                                score += matches_removed * 15
                            break

                # Particle trail decays
                for p in particles[:]:
                    p.update()
                    if p.alpha <= 0 or p.radius <= 0:
                        particles.remove(p)

            # Rendering balls and explosions
            for ball in chain:
                pygame.draw.circle(screen, ball.color, (int(ball.x), int(ball.y)), 14)
                pygame.draw.circle(screen, WHITE, (int(ball.x) - 4, int(ball.y) - 4), 3)
            
            for p in particles:
                p.draw(screen)

            # Display Stats
            score_lbl = font_md.render(f"SCORE: {score}", True, WHITE)
            lvl_lbl = font_md.render(f"LEVEL: {current_level}", True, GOLD)
            screen.blit(score_lbl, (20, 20))
            screen.blit(lvl_lbl, (WIDTH - 150, 20))

            if len(chain) == 0 and score > 0:
                update_leaderboard(score)
                current_state = "GAME_WON"

        # --- TERMINAL SCREENS ---
        elif current_state in ["GAME_OVER", "GAME_WON"]:
            title_text = "STAGE CLEARED!" if current_state == "GAME_WON" else "GAME OVER - MATCHING FAILED"
            title_color = GREEN if current_state == "GAME_WON" else (240, 50, 50)
            
            lbl = font_lg.render(title_text, True, title_color)
            screen.blit(lbl, (WIDTH // 2 - lbl.get_width() // 2, 200))
            
            final_lbl = font_md.render(f"Your Final Score: {score} Points", True, WHITE)
            screen.blit(final_lbl, (WIDTH // 2 - final_lbl.get_width() // 2, 280))
            
            retry_btn.draw(screen, font_md)
            home_btn.draw(screen, font_md)
            
            for event in events:
                if retry_btn.is_clicked(event):
                    reset_game(current_level)
                    current_state = "PLAYING"
                elif home_btn.is_clicked(event):
                    current_state = "MENU"

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
