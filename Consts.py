import pygame

ID_DEBUG = False  # Нужно ли отрисовывать id-шники у каждого объекта
CHANGES_DEBUG = False  # Нужно ли выводить все изменения в мире
SOCKET_DEBUG = True  # Нужно ли выводить все принятые и отправленные данные

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
MAIN_MENU_BACKGROUND_COLOR = (27, 35, 44)
MAIN_MENU_DARK_BACKGROUND_COLOR = (19, 28, 32)
BUTTON_YELLOW = (224, 154, 24)
BUTTON_SELECTED_YELLOW = (237, 210, 7)
MENU_WHITE = (240, 240, 240)
CLICKED_LINK_COLOR = (128, 0, 128)
PLAYER_TANKS_COLORS = (
    (255, 255, 0),
    (0, 255, 0),
    (255, 0, 0),
    (0, 0, 255),
    (0, 200, 200),
    (200, 0, 200),
    (200, 200, 200)
)

# Некоторые константные значения в игре
DEFAULT_PLAYER_BASE_HP = 3
MAX_PLAYER_TANK_HP = 3  # Максимальное количество жизней у игрока
TANK_DEFAULT_HP = 1
TANK_DEFAULT_SPEED_PER_SECOND = 5 * (sprite_w / 64)
TANK_DEFAULT_DELAY_BEFORE_FIRE = 90
WATER_DEFAULT_DELAY_BETWEEN_FRAMES = 90
TANK_DEFAULT_DELAY_BETWEEN_FRAMES = 5
DEFAULT_DELAY_BETWEEN_ENEMY_SPAWN = 180
MAX_ENEMIES_ON_ONE_MOMENT = 3
DEFAULT_ENEMIES_ON_LEVEL = 10
DEFAULT_DELAY_BETWEEN_ENEMY_TRY_TO_ROTATE = 20
DEFAULT_DELAY_BETWEEN_ENEMY_TRY_TO_SHOOT = 100
DEFAULT_DELAY_BETWEEN_ENEMY_TRY_TO_CHANGE_STATE = 500

# Переменная "приближения" - на сколько процентов координата танка должна отличаться от целого значения ширины
# тайла, чтобы произошла поправка
EPSILON = 0.15

# Все доступные стандартные карты и пути к ним
START_MAP_NAME = "map0"  # Имя стандартно-первой карты
MAPS = {
    # 0: {"path": "\\assets\\maps\\map0.txt",
    #     "name": "map0"},
    # 1: {"path": "\\assets\\maps\\map1.txt",
    #     "name": "map1"},
    # 2: {"path": "\\assets\\maps\\map2.txt",
    #     "name": "map2"},
    # 3: {"path": "\\assets\\maps\\map3.txt",
    #     "name": "map3"}
}
SERVER_MAPS = {

}

# Все тайлсеты, используемые в игре.
# Словарь вида "название файла с тайлсетом" : "размер одного изображения".
TILESET_WORLD = "tileset_world"
TILESET_EXPLOSION = "tileset_explosion"
TILESETS = {
    TILESET_WORLD: image_w,
    TILESET_EXPLOSION: 96
}

# Все тайлы, используемые в tileset_world.png
TILES = {
    "PLAYER_TANK": [(0, 0), (1, 0), (2, 0), (3, 0)],
    "ENEMY_TANK_0": [(3, 2), (3, 3)],
    "BRICK": [(0, 1)],
    "GRAY_BRICK": [(1, 1)],
    "WATER": [(2, 1), (3, 1)],
    "BUSH": [(0, 2)],
    "BASE": [(1, 2), (0, 3), (1, 3), (2, 3)],
    "BULLET": [(2, 2)],
    "EXPLOSION": [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)]
}

# Кнопки для управления танком
MOVE_RIGHT = pygame.K_RIGHT
MOVE_LEFT = pygame.K_LEFT
MOVE_UP = pygame.K_UP
MOVE_DOWN = pygame.K_DOWN
SHOOT = pygame.K_SPACE
CHAT_BUTTON = pygame.K_t
FOLD_UNFOLD_CHATLOG = pygame.K_TAB

# Сообщения для сервера:
CREATE_STRING = "create {object_type} {x} {y} {width} {height} {tileset_name} {image_name} {start_angle} {world_id}"
CHANGE_COLOR_STRING = "change_color {world_id} {R} {G} {B}"
MOVE_STRING = "move {world_id} {x} {y} {frame} {angle}"
DESTROY_STRING = "destroy {object_type} {world_id}"
GETHIT_STRING = "gethit {world_id} {bullet_direction}"
VISIBLE_STRING = "visible {world_id} {bool}"

# Для мультиплеера:
# CLIENT_IP = "127.0.0.1"
# CONNECT_TO_IP = "192.168.0.104"

# Настройки в игре:
SOUNDS_VOLUME = 0.33
