# Стандартные размеры окна
window_w = 800
window_h = 600

# Стандартные размеры спрайта на экране
sprite_w = 32
sprite_h = 32

# Стандартные размеры изображения в файле
image_w = 64
image_h = 64

# Требуемый FPS
targetFPS = 60

# Некоторые основные цвета
BLACK = (0, 0, 0)
DARK_GREY = (64, 64, 64)
GREY = (192, 192, 192)
WHITE = (255, 255, 255)

# Некоторые константные значения в игре
PLAYER_DEFAULT_HP = 1
TANK_DEFAULT_SPEED_PER_SECOND = 5 * (sprite_w / 64)
PLAYER_DEFAULT_DELAY_BEFORE_FIRE = 90
WATER_DEFAULT_DELAY_BETWEEN_FRAMES = 90
TANK_DEFAULT_DELAY_BETWEEN_FRAMES = 5
DEFAULT_DELAY_BETWEEN_ENEMY_SPAWN = 180
MAX_ENEMIES_ON_ONE_MOMENT = 1
DEFAULT_ENEMIES_ON_LEVEL = 5

# Переменная "приближения" - на сколько процентов координата танка должна отличаться от целого значения ширины
# тайла, чтобы произошла поправка
EPSILON = 0.15

# Все доступные стандартные карты и пути к ним
MAPS = {
    0: "\\assets\\maps\\map0.txt"
}

# Все тайлы, используемые в tileset.png
TILES = {
    "PLAYER_TANK": [(0, 0), (1, 0), (2, 0), (3, 0)],
    "ENEMY_TANK_0": [(3, 2), (3, 3)],
    "BRICK": [(0, 1)],
    "GRAY_BRICK": [(1, 1)],
    "WATER": [(2, 1), (3, 1)],
    "BUSH": [(0, 2)],
    "BASE": [(1, 2)],
    "BULLET": [(2, 2)]
}
