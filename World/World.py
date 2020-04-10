from Consts import sprite_w, sprite_h
from Files import get_script_dir
from World.Camera import Camera
from World.Map import Map
from World.Objects.Bullet import Bullet
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
    player_spawn_points = []  # Все места спавна игрока(-ов)
    enemy_spawn_points = []  # Все места спавна врагов

    parent_imageloader = None

    world_map = None

    def __init__(self, parent_surface, imageloader):
        self.parent_surface = parent_surface
        # self.size = size
        self.parent_imageloader = imageloader

        self.world_map = Map(self)
        self.world_map.load_by_id(0)

        self.camera = Camera(self)

    def setup_world(self):
        self.player = Tank(self)
        self.player.setup_in_world(5, 13)
        self.center_camera_on_player()

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