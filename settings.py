"""Hằng số và cấu hình Sky Defender (Top-down Shooter)."""
import os
import sys


def _is_frozen():
    return getattr(sys, "frozen", False)


def _resource_root():
    """Thư mục chứa assets read-only.

    - Khi chạy từ source: cạnh file settings.py.
    - Khi đóng gói PyInstaller --onefile: thư mục tạm sys._MEIPASS.
    """
    if _is_frozen():
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


def _user_data_root():
    """Thư mục cho file ghi (highscore.json).

    - Khi đóng gói: cạnh file .exe (portable).
    - Khi chạy source: cạnh settings.py.
    """
    if _is_frozen():
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))


# Đường dẫn (read-only)
BASE_DIR = _resource_root()
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMG_DIR = os.path.join(ASSETS_DIR, "images")
SND_DIR = os.path.join(ASSETS_DIR, "sounds")
FONT_DIR = os.path.join(ASSETS_DIR, "fonts")
SHOOTER_IMG = os.path.join(BASE_DIR, "shooter_assets", "img")
KENNEY_DIR = os.path.join(BASE_DIR, "shooter_assets",
                          "kenney_space-shooter-extension", "PNG", "Sprites")

# Màn hình (tối ưu cho laptop 1366x768 trở lên, trừ taskbar vẫn còn ~720px dọc)
WIDTH = 800
HEIGHT = 720
FPS = 60
TITLE = "Sky Defender - Bảo Vệ Bầu Trời"

# Màu
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 200, 50)
BLUE = (50, 100, 220)
YELLOW = (255, 220, 50)
GOLD = (255, 215, 0)
CYAN = (80, 210, 255)
GRAY = (150, 150, 150)
DARK_GRAY = (60, 60, 60)

# Player
PLAYER_SPEED = 7
PLAYER_MAX_HP = 6              # 25% heal = 2 HP
PLAYER_SHOOT_COOLDOWN = 200    # ms (auto-fire)
PLAYER_HURT_FLASH_MS = 400
PLAYER_INVULN_MS = 900

# Đạn
BULLET_SPEED = 10
ENEMY_BULLET_SPEED = 5
BOSS_BULLET_SPEED = 6

# Enemy
SCOUT_SPEED_MIN = 3.0
SCOUT_SPEED_MAX = 5.0
INTERCEPTOR_SPEED = 3.5
ENEMY_SPAWN_INTERVAL = 1200    # ms, khởi tạo
FORMATION_INTERVAL = 5500      # ms giữa các hàng ngang Scout
FORMATION_MIN = 3
FORMATION_MAX = 4

# Boss (Mother Ship)
BOSS_SPAWN_TIME = 90           # giây trước khi boss đầu tiên xuất hiện
BOSSES_PER_LEVEL = 3           # hạ boss lần thứ 3 thì qua màn

# Power-ups
POWERUP_DROP_CHANCE = 0.18     # rơi từ enemy thường
TRIPLE_SHOT_DURATION = 8000    # ms
SHIELD_HITS = 1

# Chế độ
MODE_TIME_ATTACK = "time_attack"
MODE_CAMPAIGN = "campaign"
TIME_OPTIONS = [5 * 60, 10 * 60]

# High Score
HIGHSCORE_FILE = os.path.join(BASE_DIR, "highscore.json")

# --- NEW setting for games ---
# Dash / Dodge Roll
DASH_SPEED      = 13     # pixels per frame while dashing
DASH_DURATION   = 170    # ms the dash lasts
DASH_COOLDOWN   = 1500   # ms before another dash is allowed
DASH_TRAIL_LEN  = 5      # number of ghost frames drawn behind the ship
 
# Combo / Score Multiplier
COMBO_WINDOW    = 1800   # ms — kills within this window chain the combo
COMBO_MAX_MULT  = 5      # combo caps at ×5
COMBO_POPUP_TTL = 900    # ms a floating score popup stays visible
MODE_HARDCORE = "hardcore"
TIME_OPTIONS = [5 * 60, 10 * 60]

# Hardcore difficulty (áp vào enemy bullet speed & spawn rate)
HARDCORE_BULLET_MULT = 1.6      # đạn địch / boss nhanh hơn 60%
HARDCORE_SPAWN_MULT = 0.55      # cooldown spawn ngắn lại → quái dày hơn
HARDCORE_FORMATION_MULT = 0.6   # formation ra dày hơn
HARDCORE_FORMATION_BONUS = 1    # +1 quái mỗi formation

# --- Chỉnh setting của player ---
HARDCORE_DROP_CHANCE = 0.08
HARDCORE_MAX_HP = 3

# High Score (file ghi - để cạnh exe khi đóng gói)
HIGHSCORE_FILE = os.path.join(_user_data_root(), "highscore.json")
