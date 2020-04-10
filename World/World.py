from Consts import DEFAULT_DELAY_BETWEEN_ENEMY_SPAWN, MAX_ENEMIES_ON_ONE_MOMENT, DEFAULT_ENEMIES_ON_LEVEL
from World.Camera import Camera
from World.Map import Map
import random
from World.Objects.Tank import Tank, Player, Enemy, Bullet
from World.Timer import Timer


class World:
    """
    Класс, содеражащий в себе информацию об отображаемой карте и всех объектах на ней.
    """
    camera = None  # Камера
    player = None  # Игрок
    parent_surface = None  # Та поверхность, на которой будет происходить отрисовка всего мира
    parent_tileset = None

    all_tanks = []  # Все танки, которые необходимо отрисовывать
    all_bullets = []  # Все пули, которые необходимо отрисовывать
    all_tiles = []  # Все тайлы, которые необходимо отрисовывать
    collisionable_objects = []  # Все объекты, с которыми нужно проверять столкновение
    actable_object = []  # Все объекты, для которых нужно вызывать Act() каждый раз

    enemy_spawn_timer = None  # Таймер для спавна нового врага
    current_amount_of_enemies = None  # Количество врагов на поле в данный момент
    enemies_remains = None  # Сколько врагов осталось уничтожить

    world_map = None

    def __init__(self, parent_surface, tileset):
        self.parent_surface = parent_surface
        self.parent_tileset = tileset
        self.enemy_spawn_timer = Timer(DEFAULT_DELAY_BETWEEN_ENEMY_SPAWN)
        self.current_amount_of_enemies = 0
        self.enemies_remains = DEFAULT_ENEMIES_ON_LEVEL
        # self.size = size

        self.world_map = Map(self)
        self.camera = Camera(self)
        self.player = Player(self)

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

        # Спавн врага
        if self.enemies_remains > 0:
            if self.enemy_spawn_timer.is_ready():
                self.enemy_spawn_timer.reset()
                self.create_enemy()
                self.enemies_remains -= 1
            else:
                self.enemy_spawn_timer.tick()

    def create_enemy(self):
        if self.current_amount_of_enemies < MAX_ENEMIES_ON_ONE_MOMENT:
            try:
                place_to_spawn = random.choice(self.world_map.enemy_spawn_places)
                (place_to_spawn_x, place_to_spawn_y) = place_to_spawn.get_world_pos()
                enemy = Enemy(self)
                enemy.setup_in_world(place_to_spawn_x, place_to_spawn_y)
            except IndexError:
                return


    def create_bullet(self, tank):
        if tank.fire_timer.is_ready():
            bullet = Bullet(self, tank)
            bullet.create()
            tank.fire_timer.reset()

    def move_camera(self, dx, dy):
        self.camera.move(dx, dy)

    def center_camera_on(self, x, y):
        self.camera.set_coords(x, y)

    def center_camera_on_player(self):
        self.camera.smart_center_on(self.player)

    def move_player_to(self, direction):
        self.player.move_to_direction(direction)
        self.camera.smart_center_on(self.player)
