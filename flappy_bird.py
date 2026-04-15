

import pygame
import random
import sys

# ─────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────
SCREEN_W, SCREEN_H = 400, 600
FPS          = 60
GRAVITY      = 0.4          # pixels added to velocity each frame
FLAP_POWER   = -8           # negative = upward
PIPE_SPEED   = 3            # pixels pipes move left per frame
PIPE_GAP     = 160          # vertical space between top/bottom pipe
PIPE_INTERVAL= 1500         # ms between new pipe spawns
PIPE_WIDTH   = 60
BIRD_SIZE    = 30           # square hitbox

# Colors  (R, G, B)
SKY_TOP      = (112, 197, 206)
SKY_BOT      = ( 65, 155, 170)
GROUND_COL   = (222, 185, 103)
GRASS_COL    = ( 92, 168,  56)
PIPE_COL     = ( 80, 168,  56)
PIPE_BORDER  = ( 55, 120,  40)
BIRD_COL     = (255, 215,  50)
BIRD_WING    = (255, 170,  30)
BIRD_EYE     = (255, 255, 255)
BIRD_PUPIL   = ( 20,  20,  20)
BIRD_BEAK    = (255, 140,   0)
WHITE        = (255, 255, 255)
BLACK        = (  0,   0,   0)
RED          = (220,  50,  50)
SCORE_COL    = (255, 255, 255)
SHADOW_COL   = (  0,   0,   0)

GROUND_H     = 80           # height of ground strip at bottom
PLAYABLE_H   = SCREEN_H - GROUND_H   # sky area

# ─────────────────────────────────────────────
#  Helper: draw text with drop-shadow
# ─────────────────────────────────────────────
def draw_text(surface, text, font, color, cx, cy, shadow=True):
    if shadow:
        shadow_surf = font.render(text, True, SHADOW_COL)
        sr = shadow_surf.get_rect(center=(cx + 2, cy + 2))
        surface.blit(shadow_surf, sr)
    surf = font.render(text, True, color)
    r    = surf.get_rect(center=(cx, cy))
    surface.blit(surf, r)



#  Bird

class Bird:
    def __init__(self):
        self.x    = SCREEN_W // 4
        self.y    = PLAYABLE_H // 2
        self.vel  = 0
        self.angle= 0           # visual tilt

    # ── physics 
    def flap(self):
        self.vel = FLAP_POWER

    def update(self):
        self.vel   += GRAVITY
        self.y     += self.vel
        # tilt: point up on flap, down on fall
        target_angle = max(-30, min(90, self.vel * 4))
        self.angle  += (target_angle - self.angle) * 0.2

    # ── collision rect 
    @property
    def rect(self):
        return pygame.Rect(
            self.x - BIRD_SIZE // 2,
            int(self.y) - BIRD_SIZE // 2,
            BIRD_SIZE, BIRD_SIZE
        )

    # ── drawing
    def draw(self, surface):
        cx, cy = self.x, int(self.y)
        half   = BIRD_SIZE // 2
        angle  = -self.angle          # pygame rotates CCW, we want CW tilt

        # draw onto a temporary surface so we can rotate it
        size = BIRD_SIZE + 10
        tmp  = pygame.Surface((size, size), pygame.SRCALPHA)
        tc   = size // 2              # center of tmp surface

        # body (circle)
        pygame.draw.circle(tmp, BIRD_COL, (tc, tc), half)

        # wing (smaller ellipse offset left/down)
        wing_rect = pygame.Rect(tc - half, tc, half + 2, half - 4)
        pygame.draw.ellipse(tmp, BIRD_WING, wing_rect)

        # eye white
        pygame.draw.circle(tmp, BIRD_EYE,   (tc + 6, tc - 5), 6)
        # pupil
        pygame.draw.circle(tmp, BIRD_PUPIL, (tc + 8, tc - 5), 3)

        # beak (small triangle pointing right)
        beak_pts = [
            (tc + half - 2, tc - 2),
            (tc + half + 8, tc + 2),
            (tc + half - 2, tc + 5),
        ]
        pygame.draw.polygon(tmp, BIRD_BEAK, beak_pts)

        # rotate and blit
        rotated = pygame.transform.rotate(tmp, angle)
        rr      = rotated.get_rect(center=(cx, cy))
        surface.blit(rotated, rr)



#  Pipe pair

class PipePair:
    CAP_H = 20      # height of the pipe cap (wider part at top/bottom of gap)
    CAP_W = PIPE_WIDTH + 10

    def __init__(self, x):
        # random gap centre within playable area, avoiding very top/bottom
        margin   = 80
        self.gap_center = random.randint(
            margin + PIPE_GAP // 2,
            PLAYABLE_H - margin - PIPE_GAP // 2
        )
        self.x       = x
        self.scored  = False    # flag so we count score once per pair

    # ── rects ────────────────────────────────
    @property
    def top_rect(self):
        top_h = self.gap_center - PIPE_GAP // 2
        return pygame.Rect(self.x, 0, PIPE_WIDTH, top_h)

    @property
    def bot_rect(self):
        bot_y = self.gap_center + PIPE_GAP // 2
        return pygame.Rect(self.x, bot_y, PIPE_WIDTH, PLAYABLE_H - bot_y)

    def update(self):
        self.x -= PIPE_SPEED

    def off_screen(self):
        return self.x + PIPE_WIDTH < 0

    # ── drawing ───────────────────────────────
    def draw(self, surface):
        # top pipe
        tr = self.top_rect
        pygame.draw.rect(surface, PIPE_COL, tr)
        pygame.draw.rect(surface, PIPE_BORDER, tr, 2)
        # top cap
        cap_top = pygame.Rect(
            self.x - (self.CAP_W - PIPE_WIDTH) // 2,
            tr.bottom - self.CAP_H,
            self.CAP_W, self.CAP_H
        )
        pygame.draw.rect(surface, PIPE_COL, cap_top)
        pygame.draw.rect(surface, PIPE_BORDER, cap_top, 2)

        # bottom pipe
        br = self.bot_rect
        pygame.draw.rect(surface, PIPE_COL, br)
        pygame.draw.rect(surface, PIPE_BORDER, br, 2)
        # bottom cap
        cap_bot = pygame.Rect(
            self.x - (self.CAP_W - PIPE_WIDTH) // 2,
            br.top,
            self.CAP_W, self.CAP_H
        )
        pygame.draw.rect(surface, PIPE_COL, cap_bot)
        pygame.draw.rect(surface, PIPE_BORDER, cap_bot, 2)


# ─────────────────────────────────────────────
#  Background  (sky gradient + scrolling clouds)
# ─────────────────────────────────────────────
class Background:
    def __init__(self):
        # pre-render the static sky gradient
        self.sky = pygame.Surface((SCREEN_W, PLAYABLE_H))
        for y in range(PLAYABLE_H):
            t   = y / PLAYABLE_H
            col = tuple(int(SKY_TOP[i] + (SKY_BOT[i] - SKY_TOP[i]) * t) for i in range(3))
            pygame.draw.line(self.sky, col, (0, y), (SCREEN_W, y))

        # a few simple clouds: (x, y, width, height)
        self.clouds = [
            [random.randint(0, SCREEN_W), random.randint(30, 150),
             random.randint(60, 120), random.randint(20, 40)]
            for _ in range(5)
        ]
        self.cloud_speed = 0.5

    def update(self):
        for c in self.clouds:
            c[0] -= self.cloud_speed
            if c[0] + c[2] < 0:
                c[0] = SCREEN_W + 10
                c[1] = random.randint(30, 150)

    def draw(self, surface):
        # sky
        surface.blit(self.sky, (0, 0))

        # clouds
        for cx, cy, cw, ch in self.clouds:
            self._draw_cloud(surface, int(cx), cy, cw, ch)

        # ground
        ground_rect = pygame.Rect(0, PLAYABLE_H, SCREEN_W, GROUND_H)
        pygame.draw.rect(surface, GROUND_COL, ground_rect)
        grass_rect  = pygame.Rect(0, PLAYABLE_H, SCREEN_W, 12)
        pygame.draw.rect(surface, GRASS_COL, grass_rect)

    @staticmethod
    def _draw_cloud(surface, x, y, w, h):
        pygame.draw.ellipse(surface, WHITE, (x,          y + h // 4, w,     h * 3 // 4))
        pygame.draw.ellipse(surface, WHITE, (x + w // 4, y,          w // 2, h))
        pygame.draw.ellipse(surface, WHITE, (x + w // 2, y + h // 5, w // 2, h * 3 // 4))


# ─────────────────────────────────────────────
#  Game
# ─────────────────────────────────────────────
class Game:
    STATE_MENU    = "menu"
    STATE_PLAYING = "playing"
    STATE_DEAD    = "dead"

    def __init__(self):
        pygame.init()
        self.screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Flappy Bird")
        self.clock   = pygame.time.Clock()

        # fonts
        self.font_big   = pygame.font.SysFont("Arial", 52, bold=True)
        self.font_med   = pygame.font.SysFont("Arial", 30, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 20)

        self.bg = Background()
        self._reset()
        self.state      = self.STATE_MENU
        self.high_score = 0

    # ── reset per round ───────────────────────
    def _reset(self):
        self.bird       = Bird()
        self.pipes      = []
        self.score      = 0
        self.last_pipe  = pygame.time.get_ticks() - PIPE_INTERVAL   # spawn immediately

    # ── main loop ─────────────────────────────
    def run(self):
        while True:
            dt = self.clock.tick(FPS)
            self._handle_events()
            self._update()
            self._draw()
            pygame.display.flip()

    # ── input ─────────────────────────────────
    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
                if event.key == pygame.K_SPACE:
                    self._on_action()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._on_action()

    def _on_action(self):
        if self.state == self.STATE_MENU:
            self.state = self.STATE_PLAYING
        elif self.state == self.STATE_PLAYING:
            self.bird.flap()
        elif self.state == self.STATE_DEAD:
            self._reset()
            self.state = self.STATE_PLAYING

    # ── update ────────────────────────────────
    def _update(self):
        self.bg.update()

        if self.state != self.STATE_PLAYING:
            return

        # bird
        self.bird.update()

        # spawn pipes on interval
        now = pygame.time.get_ticks()
        if now - self.last_pipe >= PIPE_INTERVAL:
            self.pipes.append(PipePair(SCREEN_W + 10))
            self.last_pipe = now

        # update pipes + scoring
        for pipe in self.pipes:
            pipe.update()
            # score: bird passed the pipe's right edge
            if not pipe.scored and pipe.x + PIPE_WIDTH < self.bird.x:
                pipe.scored = True
                self.score += 1
                if self.score > self.high_score:
                    self.high_score = self.score

        # remove off-screen pipes
        self.pipes = [p for p in self.pipes if not p.off_screen()]

        # ── collision detection ────────────────
        bird_rect = self.bird.rect

        # hit ground or ceiling
        if self.bird.y + BIRD_SIZE // 2 >= PLAYABLE_H or self.bird.y - BIRD_SIZE // 2 <= 0:
            self._die()
            return

        # hit pipe
        for pipe in self.pipes:
            # shrink bird rect slightly for forgiving hitbox
            shrunk = bird_rect.inflate(-6, -6)
            if shrunk.colliderect(pipe.top_rect) or shrunk.colliderect(pipe.bot_rect):
                self._die()
                return

    def _die(self):
        self.state = self.STATE_DEAD

    # ── draw ──────────────────────────────────
    def _draw(self):
        self.bg.draw(self.screen)

        for pipe in self.pipes:
            pipe.draw(self.screen)

        self.bird.draw(self.screen)

        # score (always visible while playing / dead)
        if self.state in (self.STATE_PLAYING, self.STATE_DEAD):
            draw_text(self.screen, str(self.score),
                      self.font_big, SCORE_COL, SCREEN_W // 2, 60)

        # ── overlays ──────────────────────────
        if self.state == self.STATE_MENU:
            self._draw_menu()
        elif self.state == self.STATE_DEAD:
            self._draw_game_over()

    def _draw_menu(self):
        # semi-transparent panel
        panel = pygame.Surface((320, 220), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 120))
        self.screen.blit(panel, (SCREEN_W // 2 - 160, SCREEN_H // 2 - 130))

        draw_text(self.screen, "FLAPPY BIRD",
                  self.font_big, (255, 220, 0), SCREEN_W // 2, SCREEN_H // 2 - 80)
        draw_text(self.screen, "Press SPACE or click to start",
                  self.font_small, WHITE, SCREEN_W // 2, SCREEN_H // 2 - 20)
        draw_text(self.screen, "SPACE / Click = Flap",
                  self.font_small, (200, 255, 200), SCREEN_W // 2, SCREEN_H // 2 + 20)
        draw_text(self.screen, "ESC = Quit",
                  self.font_small, (200, 200, 200), SCREEN_W // 2, SCREEN_H // 2 + 50)

        if self.high_score > 0:
            draw_text(self.screen, f"Best: {self.high_score}",
                      self.font_med, (255, 200, 50), SCREEN_W // 2, SCREEN_H // 2 + 85)

    def _draw_game_over(self):
        panel = pygame.Surface((300, 220), pygame.SRCALPHA)
        panel.fill((0, 0, 0, 150))
        self.screen.blit(panel, (SCREEN_W // 2 - 150, SCREEN_H // 2 - 110))

        draw_text(self.screen, "GAME OVER",
                  self.font_big, RED, SCREEN_W // 2, SCREEN_H // 2 - 70)
        draw_text(self.screen, f"Score: {self.score}",
                  self.font_med, WHITE, SCREEN_W // 2, SCREEN_H // 2 - 15)
        draw_text(self.screen, f"Best:  {self.high_score}",
                  self.font_med, (255, 215, 0), SCREEN_W // 2, SCREEN_H // 2 + 25)
        draw_text(self.screen, "SPACE or click to restart",
                  self.font_small, (180, 255, 180), SCREEN_W // 2, SCREEN_H // 2 + 70)


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    Game().run()

