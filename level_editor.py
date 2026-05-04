"""Sky Defender - Visual Level Editor.

Click to place tiles/decorations on the map grid.
Save with Ctrl+S or the SAVE button → updates level_map.txt.

Controls:
  Left Click   = Place selected item
  Right Click  = Erase (set to empty)
  Mouse Wheel  = Scroll through palette
  1-4          = Select tile: Empty, Grass, Dirt, Stone
  5-7          = Select deco: Tree, Grass, Rock
  8            = Eraser
  Ctrl+S       = Save
  Ctrl+Z       = Undo
  G            = Toggle grid
  Ctrl+N       = Clear map
  ESC          = Quit
"""
import sys
import os
import pygame

# ---- paths ----
BASE_DIR = os.path.dirname(__file__)
SHOOTER_IMG = os.path.join(BASE_DIR, "shooter_assets", "img")
OLD_IMG = os.path.join(BASE_DIR, "assets", "images")
MAP_FILE = os.path.join(BASE_DIR, "level_map.txt")

pygame.init()

# ---- constants ----
TILE_SIZE = 32
COLS = 25
ROWS = 19
MAP_W = COLS * TILE_SIZE   # 800
MAP_H = ROWS * TILE_SIZE   # 608

PANEL_W = 220
WIN_W = MAP_W + PANEL_W
WIN_H = MAP_H

screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("Sky Defender - Level Editor")
clock = pygame.time.Clock()

# ---- colors ----
C_BG       = (30, 30, 40)
C_GRID     = (255, 255, 255, 30)
C_PANEL    = (40, 40, 55)
C_SEL      = (255, 220, 50)
C_BTN      = (60, 120, 200)
C_BTN_HVR  = (80, 150, 240)
C_BTN_SAVE = (50, 180, 80)
C_BTN_SAVE_HVR = (70, 210, 100)
C_TEXT     = (220, 220, 220)
C_WHITE    = (255, 255, 255)
C_YELLOW   = (255, 220, 50)
C_RED      = (220, 60, 60)
C_GREEN    = (60, 200, 80)

# ---- load images ----
def load(path, scale=None):
    img = pygame.image.load(path).convert_alpha()
    if scale:
        img = pygame.transform.scale(img, scale)
    return img

tile_imgs = {
    ".": None,  # empty
    "G": load(os.path.join(SHOOTER_IMG, "tile", "8.png"), (TILE_SIZE, TILE_SIZE)),
    "D": load(os.path.join(SHOOTER_IMG, "tile", "0.png"), (TILE_SIZE, TILE_SIZE)),
    "S": load(os.path.join(SHOOTER_IMG, "tile", "13.png"), (TILE_SIZE, TILE_SIZE)),
}

deco_imgs = {
    "tree":  load(os.path.join(OLD_IMG, "deco_tree.png"), (28, 44)),
    "grass": load(os.path.join(OLD_IMG, "deco_grass.png"), (16, 10)),
    "rock":  load(os.path.join(OLD_IMG, "deco_rock.png"), (14, 10)),
}

# Background for preview
bg_sky = load(os.path.join(SHOOTER_IMG, "background", "sky_cloud.png"), (MAP_W, MAP_H))
bg_pine = load(os.path.join(SHOOTER_IMG, "background", "pine2.png"), (MAP_W, MAP_H))

# ---- fonts ----
font = pygame.font.SysFont("consolas", 14)
font_title = pygame.font.SysFont("consolas", 18, bold=True)
font_small = pygame.font.SysFont("consolas", 12)
font_msg = pygame.font.SysFont("consolas", 22, bold=True)

# ---- palette items ----
# Each: (key, label, type, display_image_or_color)
PALETTE = [
    (".", "Empty / Eraser", "tile"),
    ("G", "Grass Top", "tile"),
    ("D", "Dirt", "tile"),
    ("S", "Stone", "tile"),
    ("tree", "Deco: Tree", "deco"),
    ("grass", "Deco: Grass", "deco"),
    ("rock", "Deco: Rock", "deco"),
]


# ============================================================
# MAP DATA
# ============================================================
class MapData:
    def __init__(self):
        self.grid = [["." for _ in range(COLS)] for _ in range(ROWS)]
        self.decos = []  # list of (col, row, dtype)
        self.undo_stack = []

    def snapshot(self):
        import copy
        self.undo_stack.append((
            [row[:] for row in self.grid],
            list(self.decos)
        ))
        if len(self.undo_stack) > 50:
            self.undo_stack.pop(0)

    def undo(self):
        if self.undo_stack:
            self.grid, self.decos = self.undo_stack.pop()

    def set_tile(self, col, row, tile_type):
        if 0 <= col < COLS and 0 <= row < ROWS:
            if self.grid[row][col] != tile_type:
                self.snapshot()
                self.grid[row][col] = tile_type

    def add_deco(self, col, row, dtype):
        if 0 <= col < COLS and 0 <= row < ROWS:
            # Remove existing deco at same position
            for d in self.decos:
                if d[0] == col and d[1] == row:
                    self.snapshot()
                    self.decos.remove(d)
                    break
            else:
                self.snapshot()
            self.decos.append((col, row, dtype))

    def remove_at(self, col, row):
        """Right click: erase tile + deco at this cell."""
        changed = False
        if 0 <= col < COLS and 0 <= row < ROWS:
            if self.grid[row][col] != ".":
                if not changed:
                    self.snapshot()
                    changed = True
                self.grid[row][col] = "."
            for d in list(self.decos):
                if d[0] == col and d[1] == row:
                    if not changed:
                        self.snapshot()
                        changed = True
                    self.decos.remove(d)

    def clear(self):
        self.snapshot()
        self.grid = [["." for _ in range(COLS)] for _ in range(ROWS)]
        self.decos = []

    def load_from_file(self, path):
        if not os.path.exists(path):
            return
        rows = []
        decos = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if line.startswith("#") or line.strip() == "":
                    continue
                if line.startswith("DECO "):
                    parts = line.split()
                    decos.append((int(parts[1]), int(parts[2]), parts[3]))
                    continue
                if all(c in ".GDS" for c in line) and len(line) > 0:
                    rows.append(line)
        # Fill grid
        for r in range(ROWS):
            for c in range(COLS):
                if r < len(rows) and c < len(rows[r]):
                    self.grid[r][c] = rows[r][c]
                else:
                    self.grid[r][c] = "."
        self.decos = decos

    def save_to_file(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Sky Defender - Level Map\n")
            f.write("# G=Grass  D=Dirt  S=Stone  .=Empty\n")
            f.write("# Edit with level_editor.py or by hand\n")
            f.write("#\n")
            f.write("# ===== MAP DATA =====\n")
            for row in self.grid:
                f.write("".join(row) + "\n")
            f.write("\n# ===== DECORATIONS =====\n")
            for col, row, dtype in self.decos:
                f.write(f"DECO {col} {row} {dtype}\n")


# ============================================================
# BUTTON
# ============================================================
class Button:
    def __init__(self, x, y, w, h, text, color, hover_color, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.callback = callback

    def draw(self, surface, mouse_pos):
        col = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        pygame.draw.rect(surface, col, self.rect, border_radius=6)
        pygame.draw.rect(surface, (255, 255, 255, 60), self.rect, 1, border_radius=6)
        txt = font.render(self.text, True, C_WHITE)
        surface.blit(txt, (self.rect.centerx - txt.get_width() // 2,
                           self.rect.centery - txt.get_height() // 2))

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()
            return True
        return False


# ============================================================
# MAIN EDITOR
# ============================================================
def main():
    mapdata = MapData()
    mapdata.load_from_file(MAP_FILE)

    selected = 0  # index in PALETTE
    show_grid = True
    saved_msg_timer = 0
    drawing = False
    erasing = False

    # --- Panel layout ---
    px = MAP_W + 10  # panel x start

    def do_save():
        nonlocal saved_msg_timer
        mapdata.save_to_file(MAP_FILE)
        saved_msg_timer = pygame.time.get_ticks()

    def do_clear():
        mapdata.clear()

    def do_undo():
        mapdata.undo()

    btn_save  = Button(px, WIN_H - 130, PANEL_W - 20, 36, "SAVE  (Ctrl+S)", C_BTN_SAVE, C_BTN_SAVE_HVR, do_save)
    btn_undo  = Button(px, WIN_H - 86, PANEL_W - 20, 32, "UNDO  (Ctrl+Z)", C_BTN, C_BTN_HVR, do_undo)
    btn_clear = Button(px, WIN_H - 46, PANEL_W - 20, 32, "CLEAR (Ctrl+N)", C_RED, (240, 80, 80), do_clear)
    buttons = [btn_save, btn_undo, btn_clear]

    while True:
        clock.tick(60)
        mouse = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                # Number keys for quick select
                if event.key == pygame.K_1: selected = 0
                elif event.key == pygame.K_2: selected = 1
                elif event.key == pygame.K_3: selected = 2
                elif event.key == pygame.K_4: selected = 3
                elif event.key == pygame.K_5: selected = 4
                elif event.key == pygame.K_6: selected = 5
                elif event.key == pygame.K_7: selected = 6
                elif event.key == pygame.K_8: selected = 0  # eraser
                elif event.key == pygame.K_g:
                    show_grid = not show_grid
                # Ctrl shortcuts
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_CTRL:
                    if event.key == pygame.K_s:
                        do_save()
                    elif event.key == pygame.K_z:
                        do_undo()
                    elif event.key == pygame.K_n:
                        do_clear()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Check panel buttons
                    clicked_btn = False
                    for b in buttons:
                        if b.check_click(event.pos):
                            clicked_btn = True
                            break
                    # Check palette click
                    if not clicked_btn and event.pos[0] >= MAP_W:
                        pal_y_start = 80
                        for i, item in enumerate(PALETTE):
                            iy = pal_y_start + i * 48
                            item_rect = pygame.Rect(px, iy, PANEL_W - 20, 42)
                            if item_rect.collidepoint(event.pos):
                                selected = i
                                clicked_btn = True
                                break
                    # Place on map
                    if not clicked_btn and event.pos[0] < MAP_W:
                        drawing = True
                elif event.button == 3:
                    if event.pos[0] < MAP_W:
                        erasing = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    drawing = False
                if event.button == 3:
                    erasing = False

            if event.type == pygame.MOUSEWHEEL:
                selected = (selected - event.y) % len(PALETTE)

        # --- Continuous drawing while mouse held ---
        if mouse[0] < MAP_W:
            col = mouse[0] // TILE_SIZE
            row = mouse[1] // TILE_SIZE
            if drawing:
                key, label, ptype = PALETTE[selected]
                if ptype == "tile":
                    mapdata.set_tile(col, row, key)
                elif ptype == "deco":
                    # Only place once per cell (not continuous spam)
                    exists = any(d[0] == col and d[1] == row and d[2] == key for d in mapdata.decos)
                    if not exists:
                        mapdata.add_deco(col, row, key)
            if erasing:
                mapdata.remove_at(col, row)

        # ============ RENDER ============
        screen.fill(C_BG)

        # Background preview
        screen.blit(bg_sky, (0, 0))
        bg_dark = pygame.Surface((MAP_W, MAP_H), pygame.SRCALPHA)
        bg_dark.fill((0, 0, 0, 40))
        screen.blit(bg_dark, (0, 0))
        screen.blit(bg_pine, (0, 0))
        bg_dark2 = pygame.Surface((MAP_W, MAP_H), pygame.SRCALPHA)
        bg_dark2.fill((0, 0, 0, 30))
        screen.blit(bg_dark2, (0, 0))

        # Draw tiles
        for r in range(ROWS):
            for c in range(COLS):
                ch = mapdata.grid[r][c]
                if ch != "." and tile_imgs[ch]:
                    screen.blit(tile_imgs[ch], (c * TILE_SIZE, r * TILE_SIZE))

        # Draw decorations
        for col, row, dtype in mapdata.decos:
            img = deco_imgs.get(dtype)
            if img:
                rect = img.get_rect(midbottom=(col * TILE_SIZE + TILE_SIZE // 2, row * TILE_SIZE))
                screen.blit(img, rect)

        # Grid
        if show_grid:
            grid_surf = pygame.Surface((MAP_W, MAP_H), pygame.SRCALPHA)
            for c in range(COLS + 1):
                pygame.draw.line(grid_surf, (255, 255, 255, 25), (c * TILE_SIZE, 0), (c * TILE_SIZE, MAP_H))
            for r in range(ROWS + 1):
                pygame.draw.line(grid_surf, (255, 255, 255, 25), (0, r * TILE_SIZE), (MAP_W, r * TILE_SIZE))
            screen.blit(grid_surf, (0, 0))

        # Hover highlight on map
        if mouse[0] < MAP_W:
            hc = mouse[0] // TILE_SIZE
            hr = mouse[1] // TILE_SIZE
            hover_rect = pygame.Rect(hc * TILE_SIZE, hr * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, C_SEL, hover_rect, 2)
            # Preview of what will be placed
            key, label, ptype = PALETTE[selected]
            if ptype == "tile" and key != "." and tile_imgs[key]:
                preview = tile_imgs[key].copy()
                preview.set_alpha(120)
                screen.blit(preview, hover_rect.topleft)
            elif ptype == "deco":
                img = deco_imgs[key]
                preview = img.copy()
                preview.set_alpha(120)
                prect = preview.get_rect(midbottom=(hc * TILE_SIZE + TILE_SIZE // 2, hr * TILE_SIZE))
                screen.blit(preview, prect)

        # ---- PANEL ----
        pygame.draw.rect(screen, C_PANEL, (MAP_W, 0, PANEL_W, WIN_H))
        pygame.draw.line(screen, (80, 80, 100), (MAP_W, 0), (MAP_W, WIN_H), 2)

        # Title
        title_txt = font_title.render("LEVEL EDITOR", True, C_YELLOW)
        screen.blit(title_txt, (px, 10))

        # Coordinates
        if mouse[0] < MAP_W:
            coord = font_small.render(f"Col:{mouse[0]//TILE_SIZE}  Row:{mouse[1]//TILE_SIZE}", True, C_TEXT)
            screen.blit(coord, (px, 35))

        # Palette
        pal_y = 56
        pal_label = font_small.render("--- PALETTE (1-7) ---", True, (150, 150, 160))
        screen.blit(pal_label, (px, pal_y))
        pal_y += 22

        for i, (key, label, ptype) in enumerate(PALETTE):
            iy = pal_y + i * 48
            item_rect = pygame.Rect(px, iy, PANEL_W - 20, 42)

            # Selection highlight
            if i == selected:
                pygame.draw.rect(screen, C_SEL, item_rect, 2, border_radius=4)
            elif item_rect.collidepoint(mouse):
                pygame.draw.rect(screen, (100, 100, 120), item_rect, 1, border_radius=4)

            # Icon
            icon_x = px + 6
            icon_y = iy + 6
            if ptype == "tile":
                if key == ".":
                    # Eraser icon
                    pygame.draw.rect(screen, (80, 80, 80), (icon_x, icon_y, 30, 30), border_radius=4)
                    x_surf = font.render("X", True, C_RED)
                    screen.blit(x_surf, (icon_x + 9, icon_y + 7))
                else:
                    screen.blit(tile_imgs[key], (icon_x, icon_y))
            elif ptype == "deco":
                img = deco_imgs[key]
                di_rect = img.get_rect(center=(icon_x + 15, icon_y + 15))
                screen.blit(img, di_rect)

            # Label
            num = font_small.render(f"[{i+1}]", True, C_SEL if i == selected else (120, 120, 130))
            screen.blit(num, (icon_x + 36, iy + 6))
            lbl = font_small.render(label, True, C_WHITE if i == selected else C_TEXT)
            screen.blit(lbl, (icon_x + 36, iy + 22))

        # Buttons
        for b in buttons:
            b.draw(screen, mouse)

        # Grid toggle hint
        g_txt = font_small.render(f"Grid: {'ON' if show_grid else 'OFF'}  [G]", True, (130, 130, 140))
        screen.blit(g_txt, (px, WIN_H - 155))

        # Saved message
        if saved_msg_timer and pygame.time.get_ticks() - saved_msg_timer < 2000:
            msg = font_msg.render("SAVED!", True, C_GREEN)
            msg_rect = msg.get_rect(center=(MAP_W // 2, 20))
            bg_r = pygame.Rect(msg_rect.x - 12, msg_rect.y - 4, msg_rect.w + 24, msg_rect.h + 8)
            pygame.draw.rect(screen, (0, 0, 0, 200), bg_r, border_radius=6)
            pygame.draw.rect(screen, C_GREEN, bg_r, 2, border_radius=6)
            screen.blit(msg, msg_rect)

        pygame.display.flip()


if __name__ == "__main__":
    main()
