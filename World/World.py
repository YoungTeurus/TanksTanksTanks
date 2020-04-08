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
    # camera = Camera(self)
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

    def setup_world(self):
        self.player = Tank(self)
        self.player.setup_in_world(5, 13)

    def draw(self):
        # Сперва отрисовываем танки и пули
        for bullet in self.all_bullets:
            bullet.draw()
        for tank in self.all_tanks:
            tank.draw()
        # Затем отрисовываем тайлы
        for tile in self.all_tiles:
            tile.draw()

    def act(self):
        for obj in self.actable_object:
            obj.act()

    def create_bullet(self, tank):
        if tank.current_delay_before_fire <= 0:
            bullet = Bullet(self, tank)
            bullet.create()
            tank.set_current_delay_before_fire_to_zero()
