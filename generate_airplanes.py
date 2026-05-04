"""Generate pixel-art airplane sprites for Sky Defender."""
import pygame
import os
import math

pygame.init()

IMG_DIR = os.path.join(os.path.dirname(__file__), "assets", "images")
os.makedirs(IMG_DIR, exist_ok=True)


def save(surface, name):
    path = os.path.join(IMG_DIR, name)
    pygame.image.save(surface, path)
    print(f"  -> {name}")


def make_fighter(name, size, body_col, wing_col, accent_col, canopy_col=(150, 210, 255)):
    """Classic fighter jet - sleek, pointed nose."""
    w, h = size
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2

    # Fuselage
    bw = w // 4
    pygame.draw.rect(s, body_col, (cx - bw, 8, bw * 2, h - 16))
    # Nose cone
    pygame.draw.polygon(s, accent_col, [
        (cx, 2), (cx - bw + 2, 10), (cx + bw - 2, 10)])
    # Wings
    pygame.draw.polygon(s, wing_col, [
        (cx - bw, h // 2 - 2), (2, h // 2 + 6), (2, h // 2 - 4), (cx - bw, h // 2 - 6)])
    pygame.draw.polygon(s, wing_col, [
        (cx + bw, h // 2 - 2), (w - 3, h // 2 + 6), (w - 3, h // 2 - 4), (cx + bw, h // 2 - 6)])
    # Wing stripe
    pygame.draw.line(s, accent_col, (4, h // 2), (cx - bw, h // 2 - 3), 2)
    pygame.draw.line(s, accent_col, (w - 5, h // 2), (cx + bw, h // 2 - 3), 2)
    # Tail fins
    pygame.draw.polygon(s, wing_col, [
        (cx - 2, h - 4), (cx - bw - 4, h - 2), (cx - bw, h - 10)])
    pygame.draw.polygon(s, wing_col, [
        (cx + 2, h - 4), (cx + bw + 4, h - 2), (cx + bw, h - 10)])
    # Canopy
    pygame.draw.ellipse(s, canopy_col, (cx - 3, 12, 6, 8))
    # Engine glow
    pygame.draw.ellipse(s, (255, 180, 50, 180), (cx - 3, h - 6, 6, 5))
    # Markings
    pygame.draw.circle(s, (255, 255, 255, 80), (cx, h // 2 + 4), 3, 1)

    save(s, name)


def make_bomber(name, size, body_col, wing_col, accent_col):
    """Heavy bomber - wide body, big wings, dual engines."""
    w, h = size
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2

    # Wide fuselage
    bw = w // 5
    pygame.draw.rect(s, body_col, (cx - bw, 6, bw * 2, h - 12))
    # Rounded nose
    pygame.draw.ellipse(s, accent_col, (cx - bw + 2, 2, bw * 2 - 4, 12))
    # Big straight wings
    pygame.draw.rect(s, wing_col, (3, h // 2 - 4, w - 6, 8))
    pygame.draw.rect(s, accent_col, (3, h // 2 - 4, w - 6, 2))
    # Engine nacelles
    for ex in [w // 4, 3 * w // 4]:
        pygame.draw.rect(s, (80, 80, 90), (ex - 4, h // 2 - 2, 8, 12))
        pygame.draw.ellipse(s, (255, 160, 40, 160), (ex - 3, h // 2 + 10, 6, 4))
    # Tail
    pygame.draw.polygon(s, wing_col, [
        (cx, h - 2), (cx - bw - 6, h - 4), (cx - bw, h - 14)])
    pygame.draw.polygon(s, wing_col, [
        (cx, h - 2), (cx + bw + 6, h - 4), (cx + bw, h - 14)])
    # Vertical stabilizer
    pygame.draw.polygon(s, accent_col, [
        (cx, h - 14), (cx - 2, h - 2), (cx + 2, h - 2)])
    # Canopy
    pygame.draw.ellipse(s, (150, 210, 255), (cx - 4, 8, 8, 6))
    # Bomb bay marking
    pygame.draw.rect(s, (60, 60, 65), (cx - 3, h // 2 + 4, 6, 6))

    save(s, name)


def make_biplane(name, size, body_col, wing_col, accent_col):
    """Retro biplane - double wings, propeller."""
    w, h = size
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2

    # Fuselage (round)
    bw = w // 5
    pygame.draw.ellipse(s, body_col, (cx - bw, 6, bw * 2, h - 12))
    # Upper wing
    pygame.draw.rect(s, wing_col, (4, h // 3 - 3, w - 8, 5))
    # Lower wing
    pygame.draw.rect(s, wing_col, (6, 2 * h // 3 - 2, w - 12, 5))
    # Wing struts
    for sx in [w // 3, 2 * w // 3]:
        pygame.draw.line(s, (100, 80, 60), (sx, h // 3), (sx, 2 * h // 3), 1)
    # Propeller
    pygame.draw.rect(s, (180, 180, 180), (cx - 8, 1, 16, 3))
    pygame.draw.rect(s, (140, 140, 140), (cx - 1, 0, 2, 5))
    # Canopy
    pygame.draw.ellipse(s, (150, 210, 255, 200), (cx - 3, h // 3 + 3, 6, 6))
    # Tail
    pygame.draw.polygon(s, accent_col, [
        (cx, h - 2), (cx - 6, h - 4), (cx - 4, h - 10)])
    pygame.draw.polygon(s, accent_col, [
        (cx, h - 2), (cx + 6, h - 4), (cx + 4, h - 10)])
    # Wheels
    pygame.draw.circle(s, (50, 50, 50), (cx - 5, h - 3), 2)
    pygame.draw.circle(s, (50, 50, 50), (cx + 5, h - 3), 2)
    # Roundel marking
    pygame.draw.circle(s, accent_col, (cx, h // 2 + 2), 3, 1)

    save(s, name)


def make_stealth(name, size, body_col, edge_col):
    """Stealth jet - angular, no curves, dark."""
    w, h = size
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2

    # Angular body (diamond shape)
    pygame.draw.polygon(s, body_col, [
        (cx, 2),           # nose
        (w - 4, h // 2),   # right wing tip
        (cx, h - 4),       # tail
        (4, h // 2),       # left wing tip
    ])
    # Inner body darker
    pygame.draw.polygon(s, edge_col, [
        (cx, 8),
        (cx + w // 5, h // 2),
        (cx, h - 10),
        (cx - w // 5, h // 2),
    ])
    # Canopy (small slit)
    pygame.draw.rect(s, (80, 140, 180), (cx - 2, 12, 4, 6))
    # Engine exhaust (subtle)
    pygame.draw.polygon(s, (60, 40, 80), [
        (cx - 4, h - 6), (cx + 4, h - 6), (cx + 2, h - 2), (cx - 2, h - 2)])
    pygame.draw.rect(s, (200, 120, 255, 100), (cx - 2, h - 4, 4, 3))
    # Edge highlight
    pygame.draw.line(s, (120, 120, 130), (cx, 2), (w - 4, h // 2), 1)
    pygame.draw.line(s, (120, 120, 130), (cx, 2), (4, h // 2), 1)

    save(s, name)


def make_helicopter(name, size, body_col, accent_col):
    """Attack helicopter."""
    w, h = size
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    cx = w // 2

    # Rotor disk (translucent)
    pygame.draw.ellipse(s, (180, 180, 180, 60), (2, 2, w - 4, h // 4))
    pygame.draw.line(s, (160, 160, 160), (4, h // 8), (w - 4, h // 8), 2)
    # Rotor hub
    pygame.draw.circle(s, (100, 100, 110), (cx, h // 8), 3)
    # Body
    pygame.draw.ellipse(s, body_col, (cx - w // 4, h // 4, w // 2, h // 2))
    # Cockpit
    pygame.draw.ellipse(s, (120, 190, 230), (cx - 4, h // 4 + 2, 8, 8))
    # Tail boom
    pygame.draw.rect(s, accent_col, (cx - 2, h // 2 + h // 6, 4, h // 3))
    # Tail rotor
    pygame.draw.rect(s, (160, 160, 160), (cx - 6, h - 8, 12, 2))
    # Tail fin
    pygame.draw.polygon(s, accent_col, [
        (cx + 2, h - 10), (cx + 6, h - 4), (cx + 2, h - 4)])
    # Weapons (side pods)
    pygame.draw.rect(s, (80, 80, 80), (cx - w // 4 - 2, h // 3 + 4, 4, 8))
    pygame.draw.rect(s, (80, 80, 80), (cx + w // 4 - 2, h // 3 + 4, 4, 8))
    # Missiles
    pygame.draw.rect(s, (200, 60, 40), (cx - w // 4 - 3, h // 3 + 12, 2, 6))
    pygame.draw.rect(s, (200, 60, 40), (cx + w // 4 + 1, h // 3 + 12, 2, 6))

    save(s, name)


if __name__ == "__main__":
    print("Generating airplane sprites...")

    # 1) Normal fighter - green military
    print("\n[1] Normal Fighter")
    make_fighter("enemy_normal.png", (56, 48),
                 body_col=(70, 100, 65), wing_col=(85, 120, 75), accent_col=(100, 140, 90))

    # 2) Fast jet - red, small
    print("\n[2] Fast Jet")
    make_fighter("enemy_fast.png", (44, 38),
                 body_col=(180, 50, 40), wing_col=(200, 65, 50), accent_col=(220, 80, 60))

    # 3) Heavy bomber - gray, big
    print("\n[3] Heavy Bomber")
    make_bomber("enemy_heavy.png", (72, 56),
                body_col=(90, 95, 105), wing_col=(110, 115, 125), accent_col=(130, 135, 145))

    # 4) Stealth jet - dark angular
    print("\n[4] Stealth Jet")
    make_stealth("enemy_stealth.png", (52, 44),
                 body_col=(45, 45, 55), edge_col=(35, 35, 45))

    # 5) Biplane - retro yellow
    print("\n[5] Biplane")
    make_biplane("enemy_biplane.png", (48, 42),
                 body_col=(180, 150, 60), wing_col=(200, 170, 70), accent_col=(160, 130, 50))

    # 6) Helicopter
    print("\n[6] Helicopter")
    make_helicopter("enemy_helicopter.png", (50, 54),
                    body_col=(65, 80, 65), accent_col=(55, 70, 55))

    # 7) Boss - big red bomber
    print("\n[7] Boss")
    make_bomber("boss.png", (100, 80),
                body_col=(140, 35, 30), wing_col=(160, 45, 35), accent_col=(180, 55, 45))

    print("\nDone!")
    pygame.quit()
