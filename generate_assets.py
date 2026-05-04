"""Tạo tài nguyên pixel art cho Sky Defender - phong cách platformer chi tiết."""
import pygame
import os
import random
import math

pygame.init()

IMG_DIR = os.path.join(os.path.dirname(__file__), "assets", "images")
os.makedirs(IMG_DIR, exist_ok=True)

TILE = 32


def save(surface, name):
    path = os.path.join(IMG_DIR, name)
    pygame.image.save(surface, path)
    print(f"  -> {name}")


# ============================================================
# 1. BACKGROUND - parallax layers
# ============================================================
def make_sky():
    s = pygame.Surface((800, 600))
    for y in range(600):
        t = y / 600
        r = int(70 + t * 50)
        g = int(130 + t * 40)
        b = int(210 - t * 40)
        pygame.draw.line(s, (r, g, b), (0, y), (800, y))
    # Mây
    for cx, cy, sw, sh in [(120, 60, 120, 35), (350, 40, 100, 30),
                            (600, 80, 140, 38), (200, 130, 80, 24), (700, 30, 90, 28)]:
        cloud = pygame.Surface((sw, sh), pygame.SRCALPHA)
        pygame.draw.ellipse(cloud, (255, 255, 255, 120), (0, sh // 3, sw * 2 // 3, sh * 2 // 3))
        pygame.draw.ellipse(cloud, (255, 255, 255, 150), (sw // 4, 0, sw // 2, sh))
        pygame.draw.ellipse(cloud, (255, 255, 255, 120), (sw // 3, sh // 4, sw * 2 // 3, sh * 2 // 3))
        s.blit(cloud, (cx, cy))
    save(s, "bg_sky.png")


def make_mountains():
    s = pygame.Surface((800, 600), pygame.SRCALPHA)
    # Núi xa (xám nhạt)
    peaks = [(0, 350), (80, 200), (200, 260), (320, 180), (450, 230),
             (550, 170), (680, 220), (780, 250), (800, 350)]
    pygame.draw.polygon(s, (120, 135, 155), peaks)
    # Tuyết trên đỉnh
    for i in range(1, len(peaks) - 1):
        px, py = peaks[i]
        snow = [(px, py), (px - 15, py + 30), (px + 15, py + 30)]
        pygame.draw.polygon(s, (220, 230, 240, 180), snow)

    # Núi gần (xanh đậm hơn)
    peaks2 = [(0, 400), (100, 300), (220, 340), (350, 280), (480, 320),
              (600, 270), (720, 310), (800, 400)]
    pygame.draw.polygon(s, (70, 95, 75), peaks2)
    save(s, "bg_mountains.png")


def make_trees_bg():
    s = pygame.Surface((800, 600), pygame.SRCALPHA)
    # Hàng cây xa (nhỏ, tối)
    for x in range(0, 800, 20):
        h = random.randint(60, 100)
        base_y = 420
        # Thân
        pygame.draw.rect(s, (50, 35, 25), (x + 7, base_y - h + 30, 6, h - 30))
        # Tán lá - tam giác xếp chồng
        for i in range(3):
            w = 22 - i * 4
            ty = base_y - h + i * 18
            pygame.draw.polygon(s, (30 + i * 8, 65 + i * 10, 30 + i * 5),
                                [(x + 10, ty), (x + 10 - w // 2, ty + 22), (x + 10 + w // 2, ty + 22)])
    # Hàng cây gần (lớn hơn)
    for x in range(0, 800, 35):
        h = random.randint(80, 130)
        base_y = 450
        pygame.draw.rect(s, (60, 40, 28), (x + 12, base_y - h + 40, 8, h - 40))
        for i in range(3):
            w = 32 - i * 6
            ty = base_y - h + i * 22
            pygame.draw.polygon(s, (35 + i * 10, 80 + i * 12, 30 + i * 8),
                                [(x + 16, ty), (x + 16 - w // 2, ty + 28), (x + 16 + w // 2, ty + 28)])
    save(s, "bg_trees.png")


# ============================================================
# 2. TERRAIN TILES 32x32
# ============================================================
def make_tile(name, top_color, body_color, detail_color, has_grass=False, grass_color=None):
    s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    # Thân tile
    pygame.draw.rect(s, body_color, (0, 0, TILE, TILE))
    # Viền trên
    pygame.draw.rect(s, top_color, (0, 0, TILE, 6))
    # Chi tiết ngẫu nhiên (đá, đất)
    random.seed(hash(name))
    for _ in range(5):
        rx, ry = random.randint(2, TILE - 6), random.randint(6, TILE - 6)
        rw, rh = random.randint(2, 5), random.randint(2, 4)
        pygame.draw.rect(s, detail_color, (rx, ry, rw, rh))
    # Cỏ trên đỉnh
    if has_grass and grass_color:
        for x in range(0, TILE, 3):
            gh = random.randint(2, 6)
            pygame.draw.rect(s, grass_color, (x, -gh + 4, 2, gh))
        pygame.draw.rect(s, grass_color, (0, 0, TILE, 4))
    # Viền tối cạnh
    pygame.draw.rect(s, (0, 0, 0, 40), (0, 0, TILE, TILE), 1)
    save(s, name)


def make_tiles():
    # Grass top
    make_tile("tile_grass_top.png",
              top_color=(80, 160, 60), body_color=(110, 75, 45),
              detail_color=(90, 60, 35), has_grass=True, grass_color=(65, 145, 50))
    # Dirt (dưới grass)
    make_tile("tile_dirt.png",
              top_color=(110, 75, 45), body_color=(100, 65, 38),
              detail_color=(85, 55, 30))
    # Stone
    make_tile("tile_stone.png",
              top_color=(130, 130, 140), body_color=(110, 110, 120),
              detail_color=(90, 90, 100))
    # Grass top bên trái (có cạnh trái)
    make_tile("tile_grass_left.png",
              top_color=(80, 160, 60), body_color=(110, 75, 45),
              detail_color=(90, 60, 35), has_grass=True, grass_color=(65, 145, 50))
    # Grass top bên phải
    make_tile("tile_grass_right.png",
              top_color=(80, 160, 60), body_color=(110, 75, 45),
              detail_color=(90, 60, 35), has_grass=True, grass_color=(65, 145, 50))


# ============================================================
# 3. PLAYER - 32x48 soldier sprite
# ============================================================
def make_player_sprite():
    w, h = 32, 48
    surf = pygame.Surface((w, h), pygame.SRCALPHA)

    # Giày (nâu đậm)
    pygame.draw.rect(surf, (50, 35, 25), (8, 42, 7, 6))
    pygame.draw.rect(surf, (50, 35, 25), (17, 42, 7, 6))
    # Chân (quần xanh đậm)
    pygame.draw.rect(surf, (45, 65, 45), (9, 32, 6, 11))
    pygame.draw.rect(surf, (45, 65, 45), (17, 32, 6, 11))
    # Thân (áo xanh quân đội)
    pygame.draw.rect(surf, (65, 90, 55), (8, 16, 16, 17))
    # Túi áo
    pygame.draw.rect(surf, (55, 78, 45), (9, 22, 5, 4))
    pygame.draw.rect(surf, (55, 78, 45), (18, 22, 5, 4))
    # Belt
    pygame.draw.rect(surf, (40, 30, 20), (8, 30, 16, 3))
    pygame.draw.rect(surf, (180, 160, 60), (14, 30, 4, 3))  # buckle
    # Cổ
    pygame.draw.rect(surf, (220, 185, 150), (12, 13, 8, 4))
    # Đầu
    pygame.draw.rect(surf, (220, 185, 150), (10, 4, 12, 10))
    # Mũ sắt (helmet)
    pygame.draw.rect(surf, (60, 75, 55), (9, 1, 14, 5))
    pygame.draw.rect(surf, (50, 65, 45), (8, 4, 16, 3))
    # Mắt
    pygame.draw.rect(surf, (30, 30, 30), (18, 7, 2, 2))
    # Miệng
    pygame.draw.rect(surf, (180, 140, 110), (18, 11, 3, 1))
    # Tay trái (phía sau)
    pygame.draw.rect(surf, (65, 90, 55), (5, 17, 4, 10))
    pygame.draw.rect(surf, (220, 185, 150), (5, 27, 4, 3))
    # Tay phải + súng (phía trước)
    pygame.draw.rect(surf, (65, 90, 55), (23, 17, 4, 8))
    pygame.draw.rect(surf, (220, 185, 150), (23, 25, 4, 3))
    # Súng hướng lên
    pygame.draw.rect(surf, (80, 80, 80), (24, 4, 3, 22))
    pygame.draw.rect(surf, (60, 60, 60), (23, 2, 5, 4))
    # Nòng súng
    pygame.draw.rect(surf, (100, 100, 100), (25, 0, 2, 4))

    save(surf, "player.png")

    # Player nhìn trái
    flipped = pygame.transform.flip(surf, True, False)
    save(flipped, "player_left.png")


# ============================================================
# 4. ENEMIES - máy bay chi tiết
# ============================================================
def make_airplane(name, body_color, accent_color, size, wing_style="straight"):
    w, h = size
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cx, cy = w // 2, h // 2

    # Thân chính
    bw = w // 3
    pygame.draw.rect(s, body_color, (cx - bw // 2, cy - h // 6, bw, h // 3))
    # Mũi
    pygame.draw.polygon(s, accent_color, [
        (cx, 2), (cx - bw // 3, cy - h // 6), (cx + bw // 3, cy - h // 6)
    ])
    # Cánh
    if wing_style == "straight":
        pygame.draw.rect(s, accent_color, (3, cy - 2, w - 6, 6))
        pygame.draw.rect(s, body_color, (3, cy - 2, w - 6, 2))
    elif wing_style == "swept":
        pygame.draw.polygon(s, accent_color, [(cx, cy), (2, cy + 6), (2, cy - 2)])
        pygame.draw.polygon(s, accent_color, [(cx, cy), (w - 2, cy + 6), (w - 2, cy - 2)])
    # Đuôi
    pygame.draw.polygon(s, body_color, [
        (cx, h - 3), (cx - w // 6, cy + h // 6), (cx + w // 6, cy + h // 6)
    ])
    # Buồng lái (kính)
    pygame.draw.rect(s, (150, 210, 255), (cx - 2, cy - h // 6 + 2, 5, 4))
    # Động cơ
    pygame.draw.circle(s, (200, 200, 200), (cx - bw // 2, cy + 2), 3)
    pygame.draw.circle(s, (200, 200, 200), (cx + bw // 2, cy + 2), 3)
    # Cánh quạt (propeller phía trước)
    pygame.draw.rect(s, (180, 180, 180), (cx - 6, 0, 12, 2))
    # Viền
    # Star marking
    pygame.draw.circle(s, (220, 220, 220, 100), (cx, cy + 2), 3, 1)

    save(s, name)


def make_enemies():
    # Normal - xanh lá quân sự
    make_airplane("enemy_normal.png", (70, 100, 65), (85, 115, 75), (56, 48), "straight")
    # Fast - đỏ nhỏ
    make_airplane("enemy_fast.png", (160, 50, 45), (185, 65, 55), (44, 36), "swept")
    # Heavy - xám bạc to
    make_airplane("enemy_heavy.png", (90, 95, 100), (110, 115, 120), (72, 56), "straight")


def make_boss():
    w, h = 100, 80
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2
    # Thân to
    pygame.draw.rect(s, (120, 35, 30), (cx - 16, 15, 32, 40))
    # Mũi
    pygame.draw.polygon(s, (150, 45, 35), [(cx, 3), (cx - 12, 15), (cx + 12, 15)])
    # Cánh lớn
    pygame.draw.rect(s, (140, 40, 35), (5, 28, w - 10, 10))
    pygame.draw.rect(s, (160, 50, 40), (5, 28, w - 10, 3))
    # Đuôi
    pygame.draw.polygon(s, (120, 35, 30), [(cx, h - 3), (cx - 16, 55), (cx + 16, 55)])
    # Buồng lái
    pygame.draw.rect(s, (150, 210, 255), (cx - 4, 18, 8, 6))
    # Động cơ
    for ox in [18, w - 22]:
        pygame.draw.rect(s, (80, 80, 85), (ox, 32, 8, 12))
        pygame.draw.ellipse(s, (200, 100, 40), (ox, 44, 8, 6))
    # Vũ khí dưới cánh
    for ox in [12, w - 16]:
        pygame.draw.rect(s, (60, 60, 65), (ox, 38, 4, 14))
    # Star marking
    pygame.draw.circle(s, (200, 200, 50), (cx, 35), 5, 1)
    save(s, "boss.png")


# ============================================================
# 5. BULLETS
# ============================================================
def make_bullets():
    # Đạn player (vàng sáng)
    s = pygame.Surface((6, 16), pygame.SRCALPHA)
    pygame.draw.rect(s, (255, 240, 80), (1, 4, 4, 12))
    pygame.draw.rect(s, (255, 255, 180), (2, 0, 2, 8))
    # Trail glow
    pygame.draw.rect(s, (255, 200, 50, 120), (0, 8, 6, 8))
    save(s, "bullet_player.png")

    # Bom địch
    s = pygame.Surface((8, 14), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (180, 50, 40), (1, 0, 6, 10))
    pygame.draw.polygon(s, (140, 40, 30), [(4, 14), (1, 10), (7, 10)])
    pygame.draw.rect(s, (220, 80, 50), (3, 1, 2, 3))
    save(s, "bullet_enemy.png")

    # Đạn boss
    s = pygame.Surface((10, 18), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (220, 40, 30), (1, 0, 8, 14))
    pygame.draw.polygon(s, (180, 30, 25), [(5, 18), (1, 14), (9, 14)])
    pygame.draw.rect(s, (255, 120, 80), (3, 1, 4, 4))
    save(s, "bullet_boss.png")


# ============================================================
# 6. POWER-UPS
# ============================================================
def make_powerups():
    def make_box(name, bg_color, icon_func):
        s = pygame.Surface((24, 24), pygame.SRCALPHA)
        # Hộp gỗ
        pygame.draw.rect(s, (160, 120, 70), (2, 2, 20, 20))
        pygame.draw.rect(s, (130, 95, 50), (2, 2, 20, 20), 2)
        pygame.draw.line(s, (130, 95, 50), (2, 12), (22, 12), 1)
        # Icon
        icon_func(s)
        save(s, name)

    def health_icon(s):
        pygame.draw.rect(s, (220, 40, 40), (10, 5, 4, 10))
        pygame.draw.rect(s, (220, 40, 40), (7, 8, 10, 4))

    def firerate_icon(s):
        pygame.draw.polygon(s, (255, 220, 50), [
            (13, 4), (9, 11), (11, 11), (10, 18), (15, 10), (13, 10)])

    def shield_icon(s):
        pygame.draw.polygon(s, (60, 140, 255), [
            (12, 5), (6, 8), (6, 14), (12, 19), (18, 14), (18, 8)])
        pygame.draw.polygon(s, (100, 170, 255), [
            (12, 7), (8, 9), (8, 13), (12, 17), (16, 13), (16, 9)])

    def damage_icon(s):
        pygame.draw.polygon(s, (255, 80, 50), [
            (12, 4), (7, 11), (10, 11), (10, 18), (14, 18), (14, 11), (17, 11)])

    make_box("powerup_health.png", (40, 180, 40), health_icon)
    make_box("powerup_firerate.png", (220, 180, 30), firerate_icon)
    make_box("powerup_shield.png", (50, 100, 220), shield_icon)
    make_box("powerup_damage.png", (200, 50, 50), damage_icon)


# ============================================================
# 7. EXPLOSION frames
# ============================================================
def make_explosion():
    colors = [
        [(255, 255, 120), (255, 200, 50)],
        [(255, 200, 50), (255, 140, 30)],
        [(255, 140, 30), (200, 80, 20)],
        [(200, 80, 20), (100, 50, 20)],
    ]
    for i, (c1, c2) in enumerate(colors):
        size = 32 + i * 8
        s = pygame.Surface((size, size), pygame.SRCALPHA)
        alpha = 255 - i * 40
        pygame.draw.circle(s, (*c2, alpha), (size // 2, size // 2), size // 2)
        pygame.draw.circle(s, (*c1, min(255, alpha + 30)), (size // 2, size // 2), size // 3)
        # Tia lửa
        for _ in range(6):
            angle = random.random() * 6.28
            dist = size // 3 + random.randint(0, size // 4)
            sx = int(size // 2 + math.cos(angle) * dist)
            sy = int(size // 2 + math.sin(angle) * dist)
            pygame.draw.circle(s, (*c1, alpha), (sx, sy), 2)
        save(s, f"explosion_{i}.png")


# ============================================================
# 8. UI
# ============================================================
def make_ui():
    # Heart
    s = pygame.Surface((16, 15), pygame.SRCALPHA)
    pts = [(8, 14), (1, 7), (1, 4), (2, 2), (4, 1), (6, 1), (8, 4),
           (10, 1), (12, 1), (14, 2), (15, 4), (15, 7)]
    pygame.draw.polygon(s, (200, 30, 30), pts)
    pygame.draw.polygon(s, (240, 60, 60), [(8, 12), (3, 7), (3, 4), (5, 2), (8, 5)])
    save(s, "heart.png")

    # Crosshair
    s = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.circle(s, (255, 255, 255, 200), (16, 16), 12, 2)
    pygame.draw.line(s, (255, 255, 255, 200), (16, 2), (16, 30), 1)
    pygame.draw.line(s, (255, 255, 255, 200), (2, 16), (30, 16), 1)
    pygame.draw.circle(s, (255, 50, 50), (16, 16), 3)
    save(s, "crosshair.png")


# ============================================================
# 9. DECORATIONS (cây, bụi cỏ cho trên platform)
# ============================================================
def make_decorations():
    # Cây nhỏ
    s = pygame.Surface((24, 40), pygame.SRCALPHA)
    pygame.draw.rect(s, (80, 55, 35), (10, 20, 4, 20))
    for i in range(3):
        w = 22 - i * 5
        y = 2 + i * 10
        pygame.draw.polygon(s, (45 + i * 12, 100 + i * 15, 35 + i * 8),
                            [(12, y), (12 - w // 2, y + 14), (12 + w // 2, y + 14)])
    save(s, "deco_tree.png")

    # Bụi cỏ
    s = pygame.Surface((16, 10), pygame.SRCALPHA)
    for x in range(0, 16, 3):
        h = random.randint(4, 9)
        pygame.draw.rect(s, (50 + random.randint(0, 30), 130 + random.randint(0, 40), 40), (x, 10 - h, 2, h))
    save(s, "deco_grass.png")

    # Đá nhỏ
    s = pygame.Surface((12, 8), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (120, 115, 110), (0, 2, 12, 6))
    pygame.draw.ellipse(s, (140, 135, 130), (1, 2, 10, 4))
    save(s, "deco_rock.png")


# ============================================================
# RUN
# ============================================================
if __name__ == "__main__":
    random.seed(42)
    print("Generating Sky Defender assets...")

    print("\n[1/9] Sky background")
    make_sky()

    print("\n[2/9] Mountains")
    make_mountains()

    print("\n[3/9] Trees background")
    make_trees_bg()

    print("\n[4/9] Terrain tiles")
    make_tiles()

    print("\n[5/9] Player")
    make_player_sprite()

    print("\n[6/9] Enemies")
    make_enemies()
    make_boss()

    print("\n[7/9] Bullets")
    make_bullets()

    print("\n[8/9] Power-ups & Explosions")
    make_powerups()
    make_explosion()

    print("\n[9/9] UI & Decorations")
    make_ui()
    make_decorations()

    print("\nDone! All assets saved to assets/images/")
    pygame.quit()
