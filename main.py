"""Sky Defender - Top-down 2D Airplane Shooter (SMART rewrite)."""
import sys
import os
import random
import math
import json
import pygame
from settings import *

AUDIO_DIR = os.path.join(BASE_DIR, "shooter_assets", "audio")

pygame.init()
pygame.display.set_caption(TITLE)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


# ============================================================
# ASSET LOADING
# ============================================================
def load_img(path, scale=None, flip_v=False, rotate=0):
    img = pygame.image.load(path).convert_alpha()
    if rotate:
        img = pygame.transform.rotate(img, rotate)
    if flip_v:
        img = pygame.transform.flip(img, False, True)
    if scale:
        img = pygame.transform.scale(img, scale)
    return img


def kenney(sub, filename, **kw):
    return load_img(os.path.join(KENNEY_DIR, sub, filename), **kw)


def asset(name, **kw):
    return load_img(os.path.join(IMG_DIR, name), **kw)


def shooter(name, **kw):
    return load_img(os.path.join(SHOOTER_IMG, name), **kw)


# --- Player (chỉ lên, dùng sprite Kenney mặc định) ---
player_img = kenney("Ships", "spaceShips_007.png", scale=(60, 60))

# --- Enemies (chỉ xuống → flip) ---
scout_img = kenney("Ships", "spaceShips_003.png", scale=(44, 44), flip_v=True)
interceptor_img = kenney("Ships", "spaceShips_005.png", scale=(56, 56), flip_v=True)

# --- Boss (Mother Ship, flip) ---
boss_img = kenney("Rockets", "spaceRockets_001.png", scale=(180, 250), flip_v=True)

# --- Đạn ---
bullet_player_img = kenney("Missiles", "spaceMissiles_013.png", scale=(14, 28))
bullet_enemy_img = kenney("Missiles", "spaceMissiles_037.png", scale=(14, 24), flip_v=True)
bullet_boss_img = kenney("Missiles", "spaceMissiles_025.png", scale=(18, 32))

# --- Power-ups (asset sẵn có) ---
pu_imgs = {
    "triple": asset("powerup_firerate.png", scale=(32, 32)),  # Blue Crystal
    "heal":   asset("powerup_health.png", scale=(32, 32)),    # Red Heart
    "shield": asset("powerup_shield.png", scale=(32, 32)),    # Golden Shield
}

# --- Explosion (giữ asset cũ) ---
explosion_frames = [shooter(f"explosion/exp{i}.png", scale=(64, 64))
                    for i in range(1, 6)]

# --- HUD ---
heart_img = asset("heart.png", scale=(20, 18))

# --- Nút menu ---
btn_start = shooter("start_btn.png", scale=(220, 64))
btn_restart = shooter("restart_btn.png", scale=(220, 64))
btn_exit = shooter("exit_btn.png", scale=(220, 64))

# --- Fonts ---
font16 = pygame.font.SysFont("consolas", 16)
font18 = pygame.font.SysFont("consolas", 18)
font20 = pygame.font.SysFont("consolas", 20, bold=True)
font26 = pygame.font.SysFont("consolas", 26, bold=True)
font32 = pygame.font.SysFont("consolas", 32, bold=True)
font48 = pygame.font.SysFont("consolas", 48, bold=True)
font52 = pygame.font.SysFont("consolas", 52, bold=True)


# ============================================================
# HIGH SCORE PERSISTENCE
# ============================================================
def load_highscores():
    try:
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {
                "time_5": int(data.get("time_5", 0)),
                "time_10": int(data.get("time_10", 0)),
                "campaign": int(data.get("campaign", 0)),
                "hardcore": int(data.get("hardcore", 0)),
            }
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {"time_5": 0, "time_10": 0, "campaign": 0, "hardcore": 0}


def save_highscore(mode, score):
    hs = load_highscores()
    if score > hs.get(mode, 0):
        hs[mode] = int(score)
        try:
            with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
                json.dump(hs, f)
        except OSError:
            pass
        return True
    return False


# ============================================================
# STAR FIELD (background cuộn vô tận, 2 lớp parallax)
# ============================================================
class StarField:
    def __init__(self):
        self.far = [[random.randint(0, WIDTH), random.randint(0, HEIGHT),
                     random.choice([1, 1, 2])] for _ in range(90)]
        self.near = [[random.randint(0, WIDTH), random.randint(0, HEIGHT),
                      random.choice([2, 3])] for _ in range(45)]

    def update(self):
        for s in self.far:
            s[1] += 0.7
            if s[1] > HEIGHT:
                s[1] = 0
                s[0] = random.randint(0, WIDTH)
        for s in self.near:
            s[1] += 2.2
            if s[1] > HEIGHT:
                s[1] = 0
                s[0] = random.randint(0, WIDTH)

    def draw(self, surface):
        surface.fill((8, 10, 26))
        for x, y, r in self.far:
            pygame.draw.circle(surface, (120, 120, 160), (int(x), int(y)), r)
        for x, y, r in self.near:
            pygame.draw.circle(surface, (230, 230, 255), (int(x), int(y)), r)


# ============================================================
# SCREEN SHAKE
# ============================================================
class ScreenShake:
    def __init__(self):
        self.amount = 0
        self.decay = 1

    def shake(self, amount=10, decay=1):
        self.amount = max(self.amount, amount)
        self.decay = decay

    def offset(self):
        if self.amount <= 0:
            return (0, 0)
        ox = random.randint(-self.amount, self.amount)
        oy = random.randint(-self.amount, self.amount)
        self.amount = max(0, self.amount - self.decay)
        return (ox, oy)


shake = ScreenShake()


# ============================================================
# DIFFICULTY (module-level state, set khi vào game_loop)
# ============================================================
class Difficulty:
    bullet_mult = 1.0
    spawn_mult = 1.0
    formation_mult = 1.0
    formation_bonus = 0

    @classmethod
    def normal(cls):
        cls.bullet_mult = 1.0
        cls.spawn_mult = 1.0
        cls.formation_mult = 1.0
        cls.formation_bonus = 0

    @classmethod
    def hardcore(cls):
        cls.bullet_mult = HARDCORE_BULLET_MULT
        cls.spawn_mult = HARDCORE_SPAWN_MULT
        cls.formation_mult = HARDCORE_FORMATION_MULT
        cls.formation_bonus = HARDCORE_FORMATION_BONUS


# ============================================================
# PLAYER
# ============================================================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.base_image = player_img
        self.image = self.base_image
        self.rect = self.image.get_rect(midbottom=(WIDTH // 2, HEIGHT - 40))

        # --- Existing stats ---
        self.max_hp = PLAYER_MAX_HP
        self.hp = self.max_hp
        self.last_shot = 0
        self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN
        self.damage = 1
        self.hurt_until = 0
        self.invuln_until = 0
        self.triple_shot_until = 0
        self.shield_hits = 0

        # --- NEW: dash state ---
        self.dash_until    = 0          # ticks khi dash hiện tại kết th
        self.last_dash     = -DASH_COOLDOWN   # allow instant first dash
        self.dash_vx       = 0.0
        self.dash_vy       = 0.0
        self._trail        = []         # list of (surface, rect) ghost frames

    # --- Existing properties (unchanged) ---
    @property
    def triple_shot(self):
        return pygame.time.get_ticks() < self.triple_shot_until

    @property
    def shielded(self):
        return self.shield_hits > 0

    @property
    def hurt(self):
        return pygame.time.get_ticks() < self.hurt_until

    @property
    def invulnerable(self):
        return pygame.time.get_ticks() < self.invuln_until

    # --- NEW properties ---
    @property
    def dashing(self):
        return pygame.time.get_ticks() < self.dash_until
 
    @property
    def dash_ready(self):
        return pygame.time.get_ticks() - self.last_dash >= DASH_COOLDOWN
 
    @property
    def dash_cooldown_pct(self):
        """0.0 (just dashed) → 1.0 (ready).  Used by HUD bar."""
        elapsed = pygame.time.get_ticks() - self.last_dash
        return min(1.0, elapsed / DASH_COOLDOWN)

    # --- Cập nhật ---
    def update(self):
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()

        dx = dy = 0
        if keys[pygame.K_LEFT]  or keys[pygame.K_a]:  dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:  dx += 1
        if keys[pygame.K_UP]    or keys[pygame.K_w]:  dy -= 1
        if keys[pygame.K_DOWN]  or keys[pygame.K_s]:  dy += 1

        # Kích hoạt dash
        dash_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        if dash_pressed and not self.dashing and self.dash_ready:
            d = math.hypot(dx, dy)
            if d > 0:
                self.dash_vx = dx / d * DASH_SPEED
                self.dash_vy = dy / d * DASH_SPEED
            else:
                # Lướt thẳng lên nếu đang không di chuyển
                self.dash_vx, self.dash_vy = 0.0, -DASH_SPEED
            self.dash_until = now + DASH_DURATION
            self.last_dash = now
            # Bất tử trong khi dash
            self.invuln_until = now + DASH_DURATION + 80

        # Di chuyển
        if self.dashing:
            # Store ghost for trail effect (every other frame)
            if len(self._trail) == 0 or \
               (now // 30) % 2 == 0:          # ← sample every ~30 ms
                ghost_surf = self.base_image.copy()
                ghost_surf.set_alpha(90)
                self._trail.append((ghost_surf, self.rect.copy()))
                if len(self._trail) > DASH_TRAIL_LEN:
                    self._trail.pop(0)
            self.rect.x += int(self.dash_vx)
            self.rect.y += int(self.dash_vy)
        else:
            self._trail.clear()              # wipe trail when not dashing
            dx = dx * PLAYER_SPEED
            dy = dy * PLAYER_SPEED
            if dx and dy:            # diagonal normalisation
                dx *= 0.7071
                dy *= 0.7071
            self.rect.x += int(dx)
            self.rect.y += int(dy)
 
        # Clamp to screen
        self.rect.left   = max(0,     self.rect.left)
        self.rect.right  = min(WIDTH, self.rect.right)
        self.rect.top    = max(0,     self.rect.top)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot < self.shoot_cooldown:
            return []
        self.last_shot = now
        bullets = []
        cx, cy = self.rect.centerx, self.rect.top
        if self.triple_shot:
            bullets.append(Bullet(cx, cy, 0, -BULLET_SPEED,
                                  bullet_player_img, self.damage))
            a = math.radians(15)
            vx = math.sin(a) * BULLET_SPEED
            vy = -math.cos(a) * BULLET_SPEED
            bullets.append(Bullet(cx, cy, vx, vy, bullet_player_img, self.damage,
                                  rotate_to_dir=True))
            bullets.append(Bullet(cx, cy, -vx, vy, bullet_player_img, self.damage,
                                  rotate_to_dir=True))
        else:
            bullets.append(Bullet(cx, cy, 0, -BULLET_SPEED,
                                  bullet_player_img, self.damage))
        return bullets

    def take_damage(self, amount=1):
        if self.invulnerable:
            return False
        if self.shielded:
            self.shield_hits -= 1
            self.invuln_until = pygame.time.get_ticks() + PLAYER_INVULN_MS
            shake.shake(4, 1)
            return False
        self.hp -= amount
        now = pygame.time.get_ticks()
        self.hurt_until = now + PLAYER_HURT_FLASH_MS
        self.invuln_until = now + PLAYER_INVULN_MS
        shake.shake(7, 1)
        return True

    def apply_powerup(self, ptype):
        now = pygame.time.get_ticks()
        if ptype == "heal":
            heal = max(1, self.max_hp // 4)
            self.hp = min(self.hp + heal, self.max_hp)
        elif ptype == "triple":
            self.triple_shot_until = now + TRIPLE_SHOT_DURATION
        elif ptype == "shield":
            self.shield_hits = max(self.shield_hits, SHIELD_HITS)


    # --- Được mở rộng với tính năng hiển thị vệt sáng ---
    def draw(self, surface, ox, oy):
        now = pygame.time.get_ticks()

        # Vẽ vệt dash sau thuyền
        for i, (ghost_surf, ghost_rect) in enumerate(self._trail):
            alpha = int(40 + 50 * (i / max(1, len(self._trail))))
            ghost_surf.set_alpha(alpha)
            surface.blit(ghost_surf, (ghost_rect.x + ox, ghost_rect.y + oy))

        # Nháy khi bất tử
        if self.invulnerable and not self.hurt and not self.dashing and (now // 90) % 2 == 0:
            return
        
        img = self.base_image

        # Red tint when hurt
    def draw(self, surface, ox, oy):
        now = pygame.time.get_ticks()
        if self.invulnerable and not self.hurt and (now // 90) % 2 == 0:
            return
        img = self.base_image
        if self.hurt and (now // 60) % 2 == 0:
            img = self.base_image.copy()
            tint = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            tint.fill((255, 70, 70, 200))
            img.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        elif self.dashing:
            img  = self.base_image.copy()
            tint = pygame.Surface(img.get_size(), pygame.SRCALPHA)
            tint.fill((100, 220, 255, 160))
            img.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        surface.blit(img, (self.rect.x + ox, self.rect.y + oy))
        if self.shielded:
            cx = self.rect.centerx + ox
            cy = self.rect.centery + oy
            r = max(self.rect.w, self.rect.h) // 2 + 10
            s = pygame.Surface((r * 2 + 6, r * 2 + 6), pygame.SRCALPHA)
            alpha = 130 + int(math.sin(now * 0.008) * 50)
            pygame.draw.circle(s, (*GOLD, alpha), (r + 3, r + 3), r, 3)
            surface.blit(s, (cx - r - 3, cy - r - 3))

# ============================================================
# Combo System (New class)
# ============================================================
class ComboSystem:
    """
    Theo dõi chuỗi hạ gục. Gọi register_kill() thay vì cho điểm trực tiếp;
    Trả về Điểm thực sau khi tính theo combo.
    Dùng draw() mỗi frame để render popup combo.
    """

    def __init__(self):
        self.count          = 0  # Số kill hiện tại
        self.last_kill_ms   = 0
        self._popups        = [] # [(text, cx, cy, born_ms)]

    # Public
    def register_kill(self, base_points: int, cx: int, cy: int) -> int:
        """
        Register a kill at screen position (cx, cy).
        Returns the points to add to score (already multiplied).
        """
        now = pygame.time.get_ticks()
 
        if now - self.last_kill_ms <= COMBO_WINDOW:
            self.count += 1
        else:
            self.count = 1          # Chuỗi hết -> reset
 
        self.last_kill_ms = now
        mult   = min(self.count, COMBO_MAX_MULT)
        earned = base_points * mult
 
        # Build popup label
        if mult > 1:
            label = f"×{mult}  +{earned}"
            color = (255, 210, 40)       # gold for combos
        else:
            label = f"+{earned}"
            color = (255, 255, 255)
 
        self._popups.append((label, color, cx, cy, now))
        return earned
 
    def reset(self):
        self.count        = 0
        self.last_kill_ms = 0
 
    @property
    def multiplier(self) -> int:
        now = pygame.time.get_ticks()
        if now - self.last_kill_ms > COMBO_WINDOW:
            return 1
        return min(self.count, COMBO_MAX_MULT)
 
    @property
    def active(self) -> bool:
        return self.multiplier > 1
 
    def draw(self, surface):
        # Gọi lên mỗi frame - render popup kill combo kiểu nổi.
        now   = pygame.time.get_ticks()
        alive = []
        for label, color, cx, cy, born in self._popups:
            age = now - born
            if age > COMBO_POPUP_TTL:
                continue
            progress = age / COMBO_POPUP_TTL        # 0.0 → 1.0
            alpha    = int(255 * (1.0 - progress))
            rise     = int(40 * progress)           # float up 40 px
 
            surf = font20.render(label, True, color)
            surf.set_alpha(alpha)
            surface.blit(surf, (cx - surf.get_width() // 2, cy - rise))
            alive.append((label, color, cx, cy, born))
        self._popups = alive

# ============================================================
# BULLET
# ============================================================
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, image, damage=1, rotate_to_dir=False):
        super().__init__()
        if rotate_to_dir and (vx != 0 or vy != 0):
            angle = math.degrees(math.atan2(-vy, vx)) - 90
            self.image = pygame.transform.rotate(image, angle)
        else:
            self.image = image
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = vx
        self.vy = vy
        self.damage = damage

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
        if (self.rect.bottom < -30 or self.rect.top > HEIGHT + 30 or
                self.rect.right < -30 or self.rect.left > WIDTH + 30):
            self.kill()


# ============================================================
# SCOUT (Tier 1)
# ============================================================
class Scout(pygame.sprite.Sprite):
    POINTS = 10

    def __init__(self, speed_mult=1.0):
        super().__init__()
        self.image = scout_img
        self.rect = self.image.get_rect(
            midtop=(random.randint(30, WIDTH - 30), -40))
        self.hp = 1
        self.speed = random.uniform(SCOUT_SPEED_MIN, SCOUT_SPEED_MAX) * speed_mult
        self.next_shot = pygame.time.get_ticks() + random.randint(1200, 3200)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT + 20:
            self.kill()

    def try_shoot(self):
        now = pygame.time.get_ticks()
        if now >= self.next_shot and random.random() < 0.02:
            self.next_shot = now + random.randint(2200, 4500)
            return Bullet(self.rect.centerx, self.rect.bottom,
                          0, ENEMY_BULLET_SPEED * Difficulty.bullet_mult,
                          bullet_enemy_img)
        return None

    def take_hit(self, dmg):
        self.hp -= dmg
        return self.hp <= 0


# ============================================================
# INTERCEPTOR (Tier 2)
# ============================================================
class Interceptor(pygame.sprite.Sprite):
    POINTS = 25

    def __init__(self, speed_mult=1.0, hp_mult=1.0):
        super().__init__()
        self.image = interceptor_img
        from_left = random.random() < 0.5
        if from_left:
            start_x = -40
            self.vx = INTERCEPTOR_SPEED * 0.6 * speed_mult
        else:
            start_x = WIDTH + 40
            self.vx = -INTERCEPTOR_SPEED * 0.6 * speed_mult
        self.rect = self.image.get_rect(midtop=(start_x, -20))
        self.vy = INTERCEPTOR_SPEED * speed_mult
        self.hp = max(1, int(2 * hp_mult))
        self.next_shot = pygame.time.get_ticks() + random.randint(700, 1800)

    def update(self):
        self.rect.x += int(self.vx)
        self.rect.y += int(self.vy)
        if (self.rect.top > HEIGHT + 40 or
                self.rect.right < -60 or self.rect.left > WIDTH + 60):
            self.kill()

    def try_shoot(self):
        now = pygame.time.get_ticks()
        if now >= self.next_shot and random.random() < 0.03:
            self.next_shot = now + random.randint(1300, 2800)
            return Bullet(self.rect.centerx, self.rect.bottom,
                          0, (ENEMY_BULLET_SPEED + 1) * Difficulty.bullet_mult,
                          bullet_enemy_img)
        return None

    def take_hit(self, dmg):
        self.hp -= dmg
        return self.hp <= 0


# ============================================================
# BOSS (Mother Ship, 3 phase theo HP)
# ============================================================
class Boss(pygame.sprite.Sprite):
    def __init__(self, boss_number, level=1):
        super().__init__()
        self.image = boss_img
        self.rect = self.image.get_rect(
            midtop=(WIDTH // 2, -self.image.get_height()))
        base_hp = 40
        self.max_hp = int(base_hp * (1 + 0.4 * (boss_number - 1))
                          * (1 + 0.3 * (level - 1)))
        self.hp = self.max_hp
        self.points = 200 * boss_number * level
        self.speed_x = 1.8 + 0.2 * (boss_number - 1)
        self.direction = 1
        self.entering = True
        self.phase = 1
        self.last_shot = pygame.time.get_ticks() + 1000
        self.last_summon = pygame.time.get_ticks()
        self.boss_number = boss_number
        self.level = level

    def _compute_phase(self):
        r = self.hp / self.max_hp
        if r > 0.66:
            return 1
        if r > 0.33:
            return 2
        return 3

    def update(self):
        if self.entering:
            self.rect.y += 2
            if self.rect.top >= 30:
                self.entering = False
                shake.shake(14, 1)
            return
        new_phase = self._compute_phase()
        if new_phase != self.phase:
            self.phase = new_phase
            shake.shake(10, 1)
        self.rect.x += self.speed_x * self.direction
        if self.rect.right >= WIDTH - 10:
            self.direction = -1
        elif self.rect.left <= 10:
            self.direction = 1

    def try_attack(self, player_pos):
        if self.entering:
            return [], []
        now = pygame.time.get_ticks()
        bullets = []
        minions = []
        bspeed = BOSS_BULLET_SPEED * Difficulty.bullet_mult
        shoot_cd = {1: 950, 2: 750, 3: 620}[self.phase]
        if now - self.last_shot >= shoot_cd:
            self.last_shot = now
            cx, cy = self.rect.centerx, self.rect.bottom
            if self.phase == 1:
                dx = player_pos[0] - cx
                dy = player_pos[1] - cy
                d = max(1, math.hypot(dx, dy))
                vx = dx / d * BOSS_BULLET_SPEED
                vy = dy / d * BOSS_BULLET_SPEED
                vx = dx / d * bspeed
                vy = dy / d * bspeed
                bullets.append(Bullet(cx, cy, vx, vy, bullet_boss_img, 1,
                                      rotate_to_dir=True))
            elif self.phase == 2:
                for ang in (-30, -15, 0, 15, 30):
                    a = math.radians(ang)
                    vx = math.sin(a) * BOSS_BULLET_SPEED
                    vy = math.cos(a) * BOSS_BULLET_SPEED
                    vx = math.sin(a) * bspeed
                    vy = math.cos(a) * bspeed
                    bullets.append(Bullet(cx, cy, vx, vy, bullet_boss_img, 1,
                                          rotate_to_dir=True))
            else:
                for ang in (-45, -22, 0, 22, 45):
                    a = math.radians(ang)
                    vx = math.sin(a) * BOSS_BULLET_SPEED
                    vy = math.cos(a) * BOSS_BULLET_SPEED
                    vx = math.sin(a) * bspeed
                    vy = math.cos(a) * bspeed
                    bullets.append(Bullet(cx, cy, vx, vy, bullet_boss_img, 1,
                                          rotate_to_dir=True))
        if self.phase == 3 and now - self.last_summon >= 3500:
            self.last_summon = now
            for _ in range(2):
                s = Scout(speed_mult=1.15)
                s.rect.midtop = (self.rect.centerx
                                 + random.randint(-70, 70), self.rect.bottom)
                minions.append(s)
        return bullets, minions

    def take_hit(self, dmg):
        self.hp -= dmg
        return self.hp <= 0

    def draw_hp_bar(self, surface, ox=0, oy=0):
        bw, bh = 240, 12
        x = WIDTH // 2 - bw // 2 + ox
        y = 44 + oy
        ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (30, 30, 30),
                         (x - 2, y - 2, bw + 4, bh + 4), border_radius=3)
        col = [GREEN, YELLOW, RED][self.phase - 1]
        pygame.draw.rect(surface, col,
                         (x, y, int(bw * ratio), bh), border_radius=2)
        label = font16.render(
            f"MOTHER SHIP  #{self.boss_number}  -  PHASE {self.phase}",
            True, WHITE)
        surface.blit(label,
                     (WIDTH // 2 - label.get_width() // 2 + ox, y - 20 + oy))


# ============================================================
# EXPLOSION
# ============================================================
class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, scale=1.0):
        super().__init__()
        if scale != 1.0:
            self.frames = [pygame.transform.scale(
                f, (int(f.get_width() * scale), int(f.get_height() * scale)))
                for f in explosion_frames]
        else:
            self.frames = explosion_frames
        self.index = 0
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=center)
        self.timer = pygame.time.get_ticks()

    def update(self):
        if pygame.time.get_ticks() - self.timer > 70:
            self.timer = pygame.time.get_ticks()
            self.index += 1
            if self.index >= len(self.frames):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.frames[self.index]
                self.rect = self.image.get_rect(center=center)


# ============================================================
# POWER-UP
# ============================================================
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, ptype):
        super().__init__()
        self.ptype = ptype
        self.image = pu_imgs[ptype]
        self.rect = self.image.get_rect(center=(x, y))
        self.vy = 2.2
        self.bob = random.uniform(0, math.tau)

    def update(self):
        self.rect.y += int(self.vy)
        self.bob += 0.1
        if self.rect.top > HEIGHT:
            self.kill()

# ============================================================
# HUD
# ============================================================
def dhud(surface, player, score, high_score, combo,
             time_left=None, level=None, boss_count=None):
    """Mở rộng HUD: tim, điểm, thời gian/bàn, trạng thái sức mạnh, thanh hồi dash và hệ số nhân combo"""


# ============================================================
# PAUSE BUTTON (nút tam giác trên HUD) + PAUSE MENU
# ============================================================
PAUSE_BTN_RECT = pygame.Rect(WIDTH - 48, 56, 36, 36)


def draw_pause_button(surface, hover):
    rect = PAUSE_BTN_RECT
    bg_col = (90, 90, 130) if hover else (40, 40, 60)
    border = YELLOW if hover else WHITE
    pygame.draw.rect(surface, bg_col, rect, border_radius=6)
    pygame.draw.rect(surface, border, rect, 2, border_radius=6)
    pad = 9
    pts = [
        (rect.left + pad, rect.top + pad),
        (rect.right - pad + 1, rect.centery),
        (rect.left + pad, rect.bottom - pad),
    ]
    pygame.draw.polygon(surface, border, pts)


def pause_menu():
    """Hiển thị pause menu trên trạng thái hiện tại của màn hình.
    Trả về 'resume' / 'menu' / 'quit'."""
    bg = screen.copy()
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    resume_rect = pygame.Rect(0, 0, 280, 64)
    resume_rect.center = (WIDTH // 2, HEIGHT // 2 - 20)
    exit_rect = pygame.Rect(0, 0, 280, 64)
    exit_rect.center = (WIDTH // 2, HEIGHT // 2 + 70)

    while True:
        clock.tick(FPS)
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_p):
                    return "resume"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        screen.blit(bg, (0, 0))
        screen.blit(overlay, (0, 0))

        title = font48.render("PAUSED", True, WHITE)
        screen.blit(title,
                    (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 160))

        mouse = pygame.mouse.get_pos()
        for rect, label in ((resume_rect, "RESUME"),
                            (exit_rect, "MAIN MENU")):
            hover = rect.collidepoint(mouse)
            bg_col = (90, 90, 130) if hover else (60, 60, 90)
            border = YELLOW if hover else WHITE
            pygame.draw.rect(screen, bg_col, rect, border_radius=10)
            pygame.draw.rect(screen, border, rect, 3, border_radius=10)
            txt = font26.render(label, True, WHITE)
            screen.blit(txt, (rect.centerx - txt.get_width() // 2,
                              rect.centery - txt.get_height() // 2))

        ctrls = font16.render(
            "ESC tiep tuc  |  Click chuot de chon",
            True, (200, 200, 200))
        screen.blit(ctrls,
                    (WIDTH // 2 - ctrls.get_width() // 2, HEIGHT - 40))

        if mouse_clicked:
            if resume_rect.collidepoint(mouse):
                return "resume"
            if exit_rect.collidepoint(mouse):
                return "menu"

        pygame.display.flip()


# ============================================================
# HUD
# ============================================================
def draw_hud(surface, player, score, high_score, combo,
             time_left=None, level=None, boss_count=None):
    # Hearts
    pygame.draw.rect(surface, (30, 30, 30),
                     (8, 8, player.max_hp * 22 + 10, 26), border_radius=4)
    for i in range(player.hp):
        surface.blit(heart_img, (12 + i * 22, 11))

    # Score
    s_text = font20.render(f"SCORE {score}", True, WHITE)
    surface.blit(s_text, (WIDTH - s_text.get_width() - 12, 8))
    hs_text = font16.render(f"HI {high_score}", True, YELLOW)
    surface.blit(hs_text, (WIDTH - hs_text.get_width() - 12, 32))

    # Timer hoặc Level info (giữa)
    if time_left is not None:
        mins = int(time_left) // 60
        secs = int(time_left) % 60
        col = RED if time_left < 30 else CYAN
        t = font26.render(f"{mins:02d}:{secs:02d}", True, col)
        surface.blit(t, (WIDTH // 2 - t.get_width() // 2, 8))
    elif level is not None:
        l = font20.render(f"LEVEL {level}   BOSS {boss_count}/{BOSSES_PER_LEVEL}",
                          True, YELLOW)
        surface.blit(l, (WIDTH // 2 - l.get_width() // 2, 12))

    # Power-up indicators (dưới góc trái)
    # Power-up indicators (dưới)
    now = pygame.time.get_ticks()
    ind_y = HEIGHT - 26
    if player.triple_shot:
        rem = max(0, (player.triple_shot_until - now) // 1000 + 1)
        t = font16.render(f"TRIPLE SHOT  {rem}s", True, CYAN)
        surface.blit(t, (12, ind_y))
    if player.shielded:
        t = font16.render("SHIELD", True, GOLD)
        surface.blit(t, (WIDTH - t.get_width() - 12, ind_y))

    # NEW: Thanh hồi chiêu Dash (Bên dưới dòng chữ hiện power-up)
    bar_x, bar_y, bar_w, bar_h = 12, HEIGHT - 48, 90, 6
    pct = player.dash_cooldown_pct      # 0.0 -> 1.0
    pygame.draw.rect(surface, (40, 40, 40), 
                    (bar_x, bar_y, bar_w, bar_h), border_radius = 3)
    bar_color = CYAN if pct >= 1.0 else (80, 160, 200)
    pygame.draw.rect(surface, bar_color,
                    (bar_x, bar_y, int(bar_w * pct), bar_h), border_radius = 3)
    dash_label = font16.render("Dash", True, CYAN if pct >= 1.0 else (120, 120, 120))
    surface.blit(dash_label, (bar_x + bar_w + 6, bar_y -2))

    # --- NEW: Hiện combo (Phía dưới bộ đếm thời gian)
    if combo.active:
        mult = combo.multiplier
        pulse = int(180 + 75 * math.sin(now * 0.008))
        cx_label = font26.render(f"x{mult} COMBO!", True, YELLOW)
        cx_label.set_alpha(pulse)
        surface.blit(cx_label,
                     (WIDTH // 2 - cx_label.get_width() // 2, 44))

# ============================================================
# Pause Menu - Hàm mới
# ============================================================
def pause_menu(frozen_surface):
    """
    Menu tạm dừng hiện đè lên frozen_surface (Frame cuối cùng được render).
    Trả hiện các lựa chọn: "resume" | "restart" | "menu" | "quit"
    """
    options = [
        ("RESUME",      "resume"),
        ("RESTART",     "restart"),
        ("MAIN MENU",   "menu"),
        ("QUIT",        "quit"),
    ]
    sel = 0
    option_rects = [
        pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 - 80 + i * 72, 340, 52)
        for i in range(len(options))
    ]

    # Lớp phủ mờ được vẽ một lần lên trên Frame trò chơi đã ngừng.
    overlay = pygame.Surface ((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 175))

    while True:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "resume"
                if event.key in (pygame.K_UP, pygame.K_w):
                    sel = (sel - 1) % len(options)
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    sel = (sel + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    return options[sel][1]
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse = pygame.mouse.get_pos()
                for i, r in enumerate(option_rects):
                    if r.collidepoint(mouse):
                        return options[i][1]

        # --- render ---
        screen.blit(frozen_surface, (0, 0))   # game frozen behind menu
        screen.blit(overlay, (0, 0))
 
        title = font48.render("PAUSED", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2,
                             HEIGHT // 2 - 200))
 
        mouse = pygame.mouse.get_pos()
        for i, (label, _) in enumerate(options):
            r        = option_rects[i]
            hovered  = r.collidepoint(mouse)
            if hovered:
                sel = i
            is_sel   = (i == sel)
            col      = YELLOW if is_sel else (160, 160, 160)
            if is_sel:
                pygame.draw.rect(screen, YELLOW, r, 2, border_radius=6)
                # subtle fill highlight
                hi = pygame.Surface((r.w, r.h), pygame.SRCALPHA)
                hi.fill((255, 220, 0, 25))
                screen.blit(hi, r.topleft)
 
            txt = font26.render(label, True, col)
            screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2,
                               r.y + (r.h - txt.get_height()) // 2))
 
        hint = font16.render(
            "ESC  resume   ↑↓ navigate   ENTER confirm",
            True, (160, 160, 160))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 38))
 
        pygame.display.flip()

# ============================================================
# GAME LOOP (dùng chung cho Time Attack và Campaign)
# ============================================================
def game_loop(mode_key, time_limit=None, hardcore=False):
    """mode_key: 'time_5' | 'time_10' | 'campaign' | 'hardcore'.
    Returns (result, score)."""
    if hardcore:
        Difficulty.hardcore()
    else:
        Difficulty.normal()

    player = Player()
    # Apply hardcore player settings
    if hardcore:
        player.max_hp = HARDCORE_MAX_HP
        player.hp = HARDCORE_MAX_HP
    
    # Store the drop chance for this mode
    drop_chance = HARDCORE_DROP_CHANCE if hardcore else POWERUP_DROP_CHANCE
    starfield = StarField()
    pygame.mixer.music.load(os.path.join(AUDIO_DIR, 'music2.mp3'))
    pygame.mixer.music.play(-1)
    music_playing = True
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    explosions = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    boss = None

    score = 0
    start_time = pygame.time.get_ticks()
    last_spawn = start_time
    last_formation = start_time
    last_boss_died_ms = None   # timestamp boss trước tắt
    boss_count = 0
    level = 1
    game_over = False
    game_won = False
    result_label = ""
    saved = False

    is_campaign = (mode_key == "campaign")
    highscores = load_highscores()
    hi = highscores.get(mode_key, 0)

    combo = ComboSystem()
    
    def finish(result):
        nonlocal saved
        if not saved:
            save_highscore(mode_key, score)
            saved = True
        pygame.mixer.music.stop()
        return result, score

    def trigger_pause():
        """Mở pause menu, sau đó dịch tất cả timestamp lên để skip thời gian
        đã pause (tránh spawn dồn dập / cooldown trượt khi resume)."""
        nonlocal start_time, last_spawn, last_formation, last_boss_died_ms
        pygame.mixer.music.pause()
        pause_start = pygame.time.get_ticks()
        result = pause_menu()
        if result != "resume":
            pygame.mixer.music.stop()
            return result
        pygame.mixer.music.unpause()
        dur = pygame.time.get_ticks() - pause_start
        start_time += dur
        last_spawn += dur
        last_formation += dur
        if last_boss_died_ms is not None:
            last_boss_died_ms += dur
        player.last_shot += dur
        if player.hurt_until > 0:
            player.hurt_until += dur
        if player.invuln_until > 0:
            player.invuln_until += dur
        if player.triple_shot_until > 0:
            player.triple_shot_until += dur
        for e in enemies:
            if hasattr(e, "next_shot"):
                e.next_shot += dur
        if boss:
            boss.last_shot += dur
            boss.last_summon += dur
        return "resume"

    while True:
        clock.tick(FPS)
        now = pygame.time.get_ticks()
        elapsed = (now - start_time) / 1000.0
        mouse_clicked = False
        wants_pause = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return finish("quit")
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not game_over:
                    # Capture current frame so pause menu can freeze it
                    frozen = screen.copy()
                    pygame.mixer.music.pause()
                    result = pause_menu(frozen)
                    pygame.mixer.music.unpause()
                    if result == "resume":
                        pass                           # just continue
                    elif result == "restart":
                        pygame.mixer.music.stop()
                        return finish("restart")
                    elif result == "menu":
                        pygame.mixer.music.stop()
                        return finish("menu")
                    elif result == "quit":
                        pygame.mixer.music.stop()
                        return finish("quit")
                if (game_over or game_won) and event.key == pygame.K_RETURN:
                    return finish("restart")
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
                if (not game_over and not game_won
                        and PAUSE_BTN_RECT.collidepoint(event.pos)):
                    wants_pause = True

        if wants_pause:
            r = trigger_pause()
            if r == "menu":
                return finish("menu")
            if r == "quit":
                return finish("quit")
            # 'resume' → tiếp tục vòng lặp với timestamps đã shift
            continue

        starfield.update()

        if not game_over and not game_won:
            # --- Player (auto-fire) ---
            player.update()
            for b in player.shoot():
                player_bullets.add(b)

            # --- Groups ---
            player_bullets.update()
            enemy_bullets.update()
            enemies.update()
            explosions.update()
            powerups.update()

            # --- Boss ---
            if boss:
                boss.update()
                b_bullets, b_minions = boss.try_attack(player.rect.center)
                for b in b_bullets:
                    enemy_bullets.add(b)
                for m in b_minions:
                    enemies.add(m)

            # --- Enemy bắn ---
            for e in enemies:
                b = e.try_shoot()
                if b:
                    enemy_bullets.add(b)

            # --- Spawn enemy thường ---
            spawn_cd = max(450, int(ENEMY_SPAWN_INTERVAL - elapsed * 4))
            spawn_cd = max(250, int(spawn_cd * Difficulty.spawn_mult))
            if boss is not None:
                spawn_cd = max(spawn_cd, 1600)
            if now - last_spawn >= spawn_cd:
                last_spawn = now
                speed_mult = 1.0 + elapsed / 220 + (level - 1) * 0.15
                hp_mult = 1.0 + (level - 1) * 0.2
                if random.random() < 0.7:
                    enemies.add(Scout(speed_mult))
                else:
                    enemies.add(Interceptor(speed_mult, hp_mult))

            # --- Formation: hàng ngang 3-4 Scout cùng tốc độ ---
            form_cd = FORMATION_INTERVAL if boss is None else FORMATION_INTERVAL * 2
            if now - last_formation >= form_cd:
                last_formation = now
                count = random.randint(FORMATION_MIN, FORMATION_MAX)
            form_cd = int(form_cd * Difficulty.formation_mult)
            if now - last_formation >= form_cd:
                last_formation = now
                count = random.randint(
                    FORMATION_MIN + Difficulty.formation_bonus,
                    FORMATION_MAX + Difficulty.formation_bonus)
                spacing = WIDTH // (count + 1)
                speed_mult = 1.0 + elapsed / 260 + (level - 1) * 0.12
                shared_speed = random.uniform(
                    SCOUT_SPEED_MIN, SCOUT_SPEED_MAX) * speed_mult
                for i in range(count):
                    s = Scout(speed_mult=speed_mult)
                    s.rect.midtop = (spacing * (i + 1), -40)
                    s.speed = shared_speed
                    s.next_shot = now + random.randint(800, 1800)
                    enemies.add(s)

            # --- Trigger Boss ---
            if is_campaign:
                if boss is None and boss_count < BOSSES_PER_LEVEL:
                    ready = False
                    if last_boss_died_ms is None and elapsed >= BOSS_SPAWN_TIME:
                        ready = True
                    elif last_boss_died_ms is not None and \
                            (now - last_boss_died_ms) / 1000.0 >= BOSS_SPAWN_TIME:
                        ready = True
                    if ready:
                        boss_count += 1
                        boss = Boss(boss_count, level)
                        shake.shake(16, 1)
            else:
                if boss is None:
                    expected = int(elapsed // BOSS_SPAWN_TIME)
                    if expected > boss_count:
                        boss_count += 1
                        boss = Boss(boss_count, 1 + (boss_count - 1) // 3)
                        shake.shake(16, 1)

            # --- Va chạm: đạn player ↔ địch / boss ---
            for b in list(player_bullets):
                if boss and b.rect.colliderect(boss.rect) and not boss.entering:
                    dead = boss.take_hit(b.damage)
                    b.kill()
                    if dead:
                        score += combo.register_kill(boss.points, boss.rect.centerx, boss.rect.centery)
                        score += boss.points
                        explosions.add(Explosion(boss.rect.center, scale=2.0))
                        shake.shake(22, 1)
                        last_boss_died_ms = now
                        # Power-up chắc chắn rơi
                        cx, cy = boss.rect.centerx, boss.rect.centery
                        for pt, ox in zip(("triple", "heal", "shield"),
                                          (-60, 0, 60)):
                            powerups.add(PowerUp(cx + ox, cy, pt))
                        boss = None
                        # Campaign: hạ boss thứ 3 → qua màn
                        if is_campaign and boss_count >= BOSSES_PER_LEVEL:
                            level += 1
                            boss_count = 0
                            last_boss_died_ms = now
                            player.hp = min(player.hp + 2, player.max_hp)
                    continue
                killed = False
                for e in list(enemies):
                    if b.rect.colliderect(e.rect):
                        if e.take_hit(b.damage):
                            score += combo.register_kill(e.POINTS, e.rect.centerx, e.rect.centery)
                            score += e.POINTS
                            explosions.add(Explosion(e.rect.center))
                            if random.random() < drop_chance:
                                pt = random.choice(
                                    ["triple", "heal", "shield"])
                                powerups.add(PowerUp(
                                    e.rect.centerx, e.rect.centery, pt))
                            e.kill()
                        b.kill()
                        killed = True
                        break
                if killed:
                    continue

            # --- Va chạm: đạn địch ↔ player ---
            for b in list(enemy_bullets):
                if b.rect.colliderect(player.rect):
                    player.take_damage(b.damage)
                    explosions.add(Explosion(b.rect.center, scale=0.5))
                    b.kill()

            # --- Va chạm: địch đâm player ---
            for e in list(enemies):
                if e.rect.colliderect(player.rect):
                    player.take_damage(1)
                    explosions.add(Explosion(e.rect.center))
                    e.kill()

            # --- Boss đâm player ---
            if boss and not boss.entering and boss.rect.colliderect(player.rect):
                player.take_damage(2)

            # --- Nhặt power-up ---
            for pu in list(powerups):
                if pu.rect.colliderect(player.rect):
                    player.apply_powerup(pu.ptype)
                    pu.kill()

            # --- Kết thúc ---
            if player.hp <= 0:
                explosions.add(Explosion(player.rect.center, scale=1.6))
                shake.shake(22, 1)
                game_over = True
                if is_campaign:
                    result_label = f"DIED AT LEVEL {level}  -  BOSS {boss_count}/{BOSSES_PER_LEVEL}"
                else:
                    result_label = "YOU DIED"

            if time_limit is not None:
                remain = max(0, time_limit - elapsed)
                if remain <= 0 and not game_over:
                    game_over = True
                    game_won = True
                    mins = time_limit // 60
                    result_label = f"SURVIVED {mins} MINUTES!"

        # ================= RENDER =================
        ox, oy = shake.offset()
        starfield.draw(screen)
        combo.draw(screen)

        for s in powerups:
            screen.blit(s.image, (s.rect.x + ox, s.rect.y + oy))
        for s in enemies:
            screen.blit(s.image, (s.rect.x + ox, s.rect.y + oy))
        if boss:
            screen.blit(boss.image, (boss.rect.x + ox, boss.rect.y + oy))
        for s in player_bullets:
            screen.blit(s.image, (s.rect.x + ox, s.rect.y + oy))
        for s in enemy_bullets:
            screen.blit(s.image, (s.rect.x + ox, s.rect.y + oy))
        if not game_over or game_won:
            player.draw(screen, ox, oy)
        for ex in explosions:
            screen.blit(ex.image, (ex.rect.x + ox, ex.rect.y + oy))

        if boss:
            boss.dhp_bar(screen, ox, oy)

        # HUD
        if is_campaign:
            draw_hud(screen, player, score, hi, combo,
                     level=level, boss_count=boss_count)
        elif hardcore:
            draw_hud(screen, player, score, hi, combo, time_left=elapsed)
            tag = font18.render("HARDCORE", True, RED)
            screen.blit(tag, (WIDTH // 2 - tag.get_width() // 2, 38))
        else:
            rem = max(0, time_limit - elapsed) if time_limit else None
            draw_hud(screen, player, score, hi, combo, time_left=rem)

        # Draw boss HP bar if boss exists
        if boss and not boss.entering:
            boss.draw_hp_bar(screen, ox, oy)

        # Pause button (chỉ khi đang chơi)
        if not game_over and not game_won:
            mouse_pos = pygame.mouse.get_pos()
            draw_pause_button(screen, PAUSE_BTN_RECT.collidepoint(mouse_pos))

        # Boss approaching warning (campaign)
        if is_campaign and boss is None and boss_count < BOSSES_PER_LEVEL:
            if last_boss_died_ms is None:
                countdown = BOSS_SPAWN_TIME - elapsed
            else:
                countdown = BOSS_SPAWN_TIME - (now - last_boss_died_ms) / 1000.0
            if 0 < countdown <= 8:
                msg = font26.render(
                    f"! BOSS INCOMING  {int(countdown) + 1} !", True, RED)
                screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 70))

        if (game_over or game_won) and music_playing:
            pygame.mixer.music.stop()
            music_playing = False

        # Game over / Win overlay
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            col = GREEN if game_won else RED
            t = font48.render(result_label, True, col)
            screen.blit(t, (WIDTH // 2 - t.get_width() // 2, HEIGHT // 2 - 150))
            s_t = font32.render(f"Score: {score}", True, WHITE)
            screen.blit(s_t, (WIDTH // 2 - s_t.get_width() // 2, HEIGHT // 2 - 80))

            if score > hi:
                hs_t = font20.render("NEW HIGH SCORE!", True, YELLOW)
                screen.blit(hs_t, (WIDTH // 2 - hs_t.get_width() // 2, HEIGHT // 2 - 44))

            restart_rect = btn_restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
            exit_rect = btn_exit.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))
            mouse = pygame.mouse.get_pos()
            for img, r in ((btn_restart, restart_rect), (btn_exit, exit_rect)):
                if r.collidepoint(mouse):
                    big = pygame.transform.scale(
                        img, (int(r.w * 1.06), int(r.h * 1.06)))
                    screen.blit(big, big.get_rect(center=r.center))
                else:
                    screen.blit(img, r)

            if mouse_clicked:
                if restart_rect.collidepoint(mouse):
                    return finish("restart")
                if exit_rect.collidepoint(mouse):
                    return finish("menu")

        pygame.display.flip()


# ============================================================
# MODE SELECT MENU
# ============================================================
def mode_select_menu():
    starfield = StarField()
    options = [
        ("TIME ATTACK  -  5 MIN", "time_5"),
        ("TIME ATTACK  - 10 MIN", "time_10"),
        ("CAMPAIGN  -  3 BOSS / LEVEL", "campaign"),
        ("HARDCORE  -  ENDLESS", "hardcore"),
        ("BACK", "back"),
    ]
    descs = {
        "time_5": "Sống sót 5 phút. Boss xuất hiện mỗi 90s.",
        "time_10": "Sống sót 10 phút. Boss mạnh dần.",
        "campaign": "3 boss mỗi màn. Hạ boss thứ 3 để qua màn.",
        "hardcore": "Endless. Đạn nhanh hơn, quái dày hơn - khó nhất!",
        "back": "",
    }
    sel = 0
    option_rects = [pygame.Rect(WIDTH // 2 - 220, 130 + i * 96, 440, 60)
                    for i in range(len(options))]
    hs = load_highscores()

    while True:
        clock.tick(FPS)
        starfield.update()
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "back"
                if event.key == pygame.K_UP:
                    sel = (sel - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    sel = (sel + 1) % len(options)
                if event.key == pygame.K_RETURN:
                    return options[sel][1]
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        starfield.draw(screen)
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 90))
        screen.blit(ov, (0, 0))

        title = font48.render("SELECT MODE", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        mouse = pygame.mouse.get_pos()
        for i, (label, key) in enumerate(options):
            rect = option_rects[i]
            if rect.collidepoint(mouse):
                sel = i
            col = YELLOW if i == sel else GRAY
            txt = font26.render(label, True, col)
            tx = WIDTH // 2 - txt.get_width() // 2
            if i == sel:
                pygame.draw.rect(screen, YELLOW, rect, 2, border_radius=6)
                if descs[key]:
                    d = font16.render(descs[key], True, (200, 200, 200))
                    screen.blit(d, (WIDTH // 2 - d.get_width() // 2,
                                    rect.y + 36))
                if key in hs:
                    hst = font16.render(
                        f"High Score: {hs[key]}", True, YELLOW)
                    screen.blit(hst, (WIDTH // 2 - hst.get_width() // 2,
                                      rect.bottom + 6))
            screen.blit(txt, (tx, rect.y + 6))
            if mouse_clicked and rect.collidepoint(mouse):
                return key

        ctrls = font16.render(
            "UP/DOWN chon  |  ENTER xac nhan  |  ESC quay lai",
            True, (180, 180, 180))
        screen.blit(ctrls, (WIDTH // 2 - ctrls.get_width() // 2, HEIGHT - 40))
        pygame.display.flip()


# ============================================================
# MAIN MENU
# ============================================================
def main_menu():
    starfield = StarField()
    while True:
        clock.tick(FPS)
        starfield.update()
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "play"
                if event.key == pygame.K_ESCAPE:
                    return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        starfield.draw(screen)

        title = font52.render("SKY DEFENDER", True, WHITE)
        sub = font18.render("- Bao Ve Bau Troi -", True, YELLOW)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))
        screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 150))

        start_rect = btn_start.get_rect(center=(WIDTH // 2, 290))
        exit_rect = btn_exit.get_rect(center=(WIDTH // 2, 380))
        mouse = pygame.mouse.get_pos()
        for img, r in ((btn_start, start_rect), (btn_exit, exit_rect)):
            if r.collidepoint(mouse):
                big = pygame.transform.scale(
                    img, (int(r.w * 1.08), int(r.h * 1.08)))
                screen.blit(big, big.get_rect(center=r.center))
            else:
                screen.blit(img, r)

        if mouse_clicked:
            if start_rect.collidepoint(mouse):
                return "play"
            if exit_rect.collidepoint(mouse):
                return "quit"

        ctrls = font16.render(
            "ARROWS / WASD di chuyen  |  AUTO-FIRE  |  ESC menu",
            True, (200, 200, 200))
        screen.blit(ctrls, (WIDTH // 2 - ctrls.get_width() // 2, HEIGHT - 40))
        pygame.display.flip()


# ============================================================
# MAIN
# ============================================================
def main():
    while True:
        if main_menu() == "quit":
            break
        mode = mode_select_menu()
        if mode == "quit":
            break
        if mode == "back":
            continue
        while True:
            if mode == "time_5":
                result, _ = game_loop("time_5", 5 * 60)
            elif mode == "time_10":
                result, _ = game_loop("time_10", 10 * 60)
            elif mode == "hardcore":
                result, _ = game_loop("hardcore", hardcore=True)
            else:
                result, _ = game_loop("campaign")
            if result == "restart":
                continue
            break
        if result == "quit":
            break
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
