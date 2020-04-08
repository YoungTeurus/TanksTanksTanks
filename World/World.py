from Consts import sprite_w, sprite_h
from Files import get_script_dir
from World.Objects.Collisionable import Collisionable
from World.Objects.Tank import Tank
from World.Objects.WorldTile import WorldTile


class World:
    """
    Класс, содеражащий в себе информацию об отображаемой карте и всех объектах на ней.
    """

    player = None  # Игрок
    parent_surface = None  # Та поверхность, на которой будет происходить отрисовка всего мира

    all_tanks = []  # Все танки, которые необходимо отрисовывать
    all_tiles = []  # Все тайлы, которые необходимо отрисовывать
    collisionable_objects = []  # Все объекты, с которыми нужно проверять столкновение
    player_spawn_points = []  # Все места спавна игрока(-ов)
    enemy_spawn_points = []  # Все места спавна врагов

    world_map = [
        [2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 2],
        [2, 0, 1, 0, 1, 0, 0, 0, 0, 2],
        [2, 0, 1, 0, 1, 1, 0, 0, 0, 2],
        [2, 0, 1, 0, 0, 1, 0, 0, 0, 2],
        [2, 0, 1, 1, 0, 0, 0, 0, 0, 2],
        [2, 0, 0, 0, 0, 0, 0, 1, 1, 2],
        [2, 1, 1, 0, 0, 0, 0, 1, 1, 2],
        [2, 0, 1, 1, 0, 0, 0, 0, 0, 2],
        [2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    ]

    def __init__(self, parent_surface, size):
        self.parent_surface = parent_surface
        self.size = size
        # self.player.set_angle("LEFT")

    def setup_world(self):
        self.player = Tank(self)
        self.player.set_pos(32, 32)
        self.player.set_size(sprite_w, sprite_h)
        self.player.set_image(get_script_dir() + "\\assets\\textures\\tank.png")
        self.player.set_is_soild(True)

        self.all_tanks.append(self.player)
        self.collisionable_objects.append(self.player)

        tile_x = 0
        tile_y = 0
        for row in self.world_map:
            for tile in row:
                temp_tile = WorldTile(self)
                temp_tile.set_tile(tile, tile_x, tile_y)
                tile_x += 1
            tile_y += 1
            tile_x = 0

    def draw(self):
        # Сперва отрисовываем танки
        for tank in self.all_tanks:
            tank.draw()
        # Затем отрисовываем тайлы
        for tile in self.all_tiles:
            tile.draw()

    def test_add_object(self, x, y):
        just_an_object = Collisionable(self)
        just_an_object.set_pos(sprite_w * x + sprite_w, sprite_h * y + sprite_h)
        just_an_object.set_size(sprite_w, sprite_h)
        just_an_object.set_image(get_script_dir() + "\\assets\\textures\\bricks.png")
        just_an_object.set_is_soild(True)

        self.all_tiles.append(just_an_object)
        self.collisionable_objects.append(just_an_object)
