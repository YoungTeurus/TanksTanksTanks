import logging

from Consts import sprite_w, sprite_h
from Files import get_script_dir
from World.Camera import Camera
from World.Map import Map
from World.Objects.Bullet import Bullet
import random
from World.Objects.Collisionable import Collisionable
from World.Objects.Tank import Tank
from World.Objects.WorldTile import WorldTile


class World:
    """
    Класс, содеражащий в себе информацию об отображаемой карте и всех объектах на ней.
    """
    camera = None  # Камера
    player = None  # Игрок
    parent_surface = None  # Та поверхность, на которой будет происходить отрисовка всего мира

    all_tanks = []  # Все танки, которые необходимо отрисовывать
    all_bullets = []  # Все пули, которые необходимо отрисовывать
    all_tiles = []  # Все тайлы, которые необходимо отрисовывать
    collisionable_objects = []  # Все объекты, с которыми нужно проверять столкновение
    actable_object = []  # Все объекты, для которых нужно вызывать Act() каждый раз

    parent_imageloader = None

    world_map = None

    def __init__(self, parent_surface, imageloader):
        self.parent_surface = parent_surface
        # self.size = size
        self.parent_imageloader = imageloader

        self.world_map = Map(self)
        self.camera = Camera(self)
        self.player = Tank(self)

    def setup_world(self):
        self.load_map(0)
        self.spawn_player()
        self.center_camera_on_player()

    def load_map(self, map_id):
        self.world_map.load_by_id(map_id)
        self.world_map.check()

    def spawn_player(self, player_id=0):
        """
        Спавнит игрока под айди id на одной из точек спавна
        :param player_id: Айди игрока (для мультиплеера)
        :return:
        """
        place_to_spawn = random.choice(self.world_map.player_spawn_places)
        (place_to_spawn_x, place_to_spawn_y) = place_to_spawn.get_world_pos()
        self.player.setup_in_world(place_to_spawn_x, place_to_spawn_y)


    def draw(self):
        # Сперва отрисовываем танки и пули
        for bullet in self.all_bullets:
            bullet.draw_in_world(self.camera)
        for tank in self.all_tanks:
            tank.draw_in_world(self.camera)
        # Затем отрисовываем тайлы
        for tile in self.all_tiles:
            tile.draw_in_world(self.camera)

    def act(self):
        for obj in self.actable_object:
            obj.act()

    def create_bullet(self, tank):
        if tank.current_delay_before_fire <= 0:
            bullet = Bullet(self, tank)
            bullet.create()
            tank.set_current_delay_before_fire_to_full()

    def move_camera(self, dx, dy):
        self.camera.move(dx, dy)

    def center_camera_on(self, x, y):
        self.camera.set_coords(x, y)

    def center_camera_on_player(self):
        self.camera.smart_center_on(self.player)

    def move_player_to(self, direction):
        self.player.move_to_direction(direction)
        self.camera.smart_center_on(self.player)
