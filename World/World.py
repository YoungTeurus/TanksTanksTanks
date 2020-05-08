from Consts import DEFAULT_DELAY_BETWEEN_ENEMY_SPAWN, MAX_ENEMIES_ON_ONE_MOMENT, DEFAULT_ENEMIES_ON_LEVEL
from World.Camera import Camera
from World.Map import Map
import random

from World.Objects.Collisionable import remove_if_exists_in
from World.Objects.RotatableWorldObject import RotatableWorldObject
from World.Objects.Tank import Player, Enemy, Bullet
from World.Timer import Timer


class World:
    """
    Класс, содеражащий в себе информацию об отображаемой карте и всех объектах на ней.
    """
    camera = None  # Камера
    players = []  # Игрок
    parent_surface = None  # Та поверхность, на которой будет происходить отрисовка всего мира
    parent_tileset = None

    all_tanks = []  # Все танки, которые необходимо отрисовывать
    all_bullets = []  # Все пули, которые необходимо отрисовывать
    all_tiles = []  # Все тайлы, которые необходимо отрисовывать (тайлы заносятся сюда в .set_tile() )
    collisionable_objects = []  # Все объекты, с которыми нужно проверять столкновение
    actable_object = []  # Все объекты, для которых нужно вызывать Act() каждый раз

    all_drawable_client = []  # Все объекты, которые нужно отрисовать на стороне клиента

    enemy_spawn_timer = None  # Таймер для спавна нового врага
    current_amount_of_enemies = None  # Количество врагов на поле в данный момент
    enemies_remains = None  # Сколько врагов осталось уничтожить

    world_map = None

    is_server = None
    need_to_log_changes = None  # Нужно ли отслеживать изменения. Только в мультиплеере.
    changes = []  # Различия, произошедшие за текущий такт игры. Содержит команды, которые необходимо выполнить.
    last_id = None  # Последний свободный id

    objects_id_dict = None  # Словарь ВСЕХ объектов по их ID

    def __init__(self, parent_surface, tileset, is_server):
        self.parent_surface = parent_surface
        self.parent_tileset = tileset
        self.enemy_spawn_timer = Timer(DEFAULT_DELAY_BETWEEN_ENEMY_SPAWN)
        self.current_amount_of_enemies = 0
        self.enemies_remains = DEFAULT_ENEMIES_ON_LEVEL
        # self.size = size

        self.world_map = Map(self)
        self.camera = Camera(self)
        self.need_to_log_changes = False
        self.objects_id_dict = dict()
        self.is_server = is_server
        self.last_id = 0

    def load_world_map(self, map_id: int = None):
        if map_id is not None:
            self.load_map(map_id)
        self.load_map(0)
        # self.spawn_player()
        # self.center_camera_on_player()

    def get_last_id(self):
        self.last_id += 1
        return self.last_id - 1

    def load_map(self, map_id):
        self.world_map.load_by_id(map_id)
        self.world_map.check()

    def spawn_player(self, player_id: int = 0):
        """
        Спавнит игрока под айди id на одной из точек спавна
        :param player_id: Айди игрока (для мультиплеера)
        :return:
        """
        place_to_spawn = self.world_map.player_spawn_places[player_id]
        # place_to_spawn = random.choice(self.world_map.player_spawn_places)
        (place_to_spawn_x, place_to_spawn_y) = place_to_spawn.get_world_pos()
        new_player = Player(self)
        new_player.setup_in_world(place_to_spawn_x, place_to_spawn_y)

    def draw(self):
        # Сперва отрисовываем танки и пули
        for bullet in self.all_bullets:
            bullet.draw_in_world(self.camera)
        for tank in self.all_tanks:
            tank.draw_in_world(self.camera)

        # Это только для клиента:
        for obj in self.all_drawable_client:
            obj.draw_in_world(self.camera)

        # Затем отрисовываем тайлы
        for tile in self.all_tiles:
            tile.draw_in_world(self.camera)

    def act(self):
        for obj in self.actable_object:
            obj.act()

        self.enemy_spawn_timer.tick()

    def create_enemy(self):
        """
        Спавнит врага на одном из мест спавна для врагов. При этом проверяется максимальное число заспавенных врагов
        и свободность места для спавна.
        :return:
        """
        if self.current_amount_of_enemies < MAX_ENEMIES_ON_ONE_MOMENT:
            try:
                place_to_spawn = random.choice(self.world_map.enemy_spawn_places)
                if place_to_spawn.check_collisions(self.collisionable_objects).__len__() > 0:
                    return False
                (place_to_spawn_x, place_to_spawn_y) = place_to_spawn.get_world_pos()
                enemy = Enemy(self)
                enemy.setup_in_world(place_to_spawn_x, place_to_spawn_y)
                return True
            except IndexError:
                return False
        return False

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
        self.camera.smart_center_on(self.players[0])  # TODO: Центровать камеру не на одном игроке

    def move_player_to(self, player_id, direction):
        try:
            self.players[player_id].move_to_direction(direction)
            self.camera.smart_center_on(self.players[player_id])
        except IndexError:
            # Видимо, игрока уже убили
            pass

    def check_if_player_is_alive(self):
        return not self.players[0].is_destroyed

    def check_if_base_is_alive(self):
        return self.world_map.player_bases.__len__() > 0

    def set_ready_for_server(self):
        """
        Указывает миру, что необходимо отслеживать все изменения, происходящие с этого момента.
        """
        self.need_to_log_changes = True

    def get_changes(self):
        return self.changes

    def clear_changes(self):
        self.changes.clear()

    def process_many_changes(self, changes):
        # num_of_changes = changes.keys().__len__()
        for change in changes:
            self.process_change(changes[change])
            # self.process_change(changes[(i-1).__str__()])

    def process_change(self, change):
        arguments = change.split(" ")
        if arguments[0] == "create":
            if arguments[1] == "RotatableWorldObject":
                coord_x, coord_y = int(arguments[2]), int(arguments[3])
                width, height = int(arguments[4]), int(arguments[5])
                image_name, start_angle = arguments[6], arguments[7]
                world_id = int(arguments[8])
                temp_object = RotatableWorldObject(self)
                temp_object.set_pos(coord_x, coord_y)
                temp_object.set_size(width, height)
                temp_object.set_image(image_name)
                temp_object.set_angle(start_angle)
                temp_object.set_world_id(world_id)

                self.objects_id_dict[world_id] = temp_object
                self.all_drawable_client.append(temp_object)
        elif arguments[0] == "move":
            world_id = int(arguments[1])
            new_x, new_y = int(arguments[2]), int(arguments[3])
            new_frame, new_angle = int(arguments[4]), arguments[5]
            try:
                self.objects_id_dict[world_id].set_pos(new_x, new_y)
                self.objects_id_dict[world_id].set_angle(new_angle)
                self.objects_id_dict[world_id].image.current_frame = new_frame
            except KeyError:
                # Видимо, этот объект уже уничтожили?
                pass
        elif arguments[0] == "destroy":
            if arguments[1] == "RotatableWorldObject":
                world_id = int(arguments[2])
                try:
                    remove_if_exists_in(self.objects_id_dict[world_id], self.all_drawable_client)
                    self.objects_id_dict[world_id].destroy()
                except KeyError:
                    # Видимо, этот объект уже уничтожили?
                    pass
            elif arguments[1] == "WorldTile":
                world_id = int(arguments[2])
                self.objects_id_dict[world_id].destroy()
        elif arguments[0] == "gethit":
            world_id = int(arguments[1])
            bullet_direction = arguments[2]
            self.objects_id_dict[world_id].get_hit(bullet_direction)
        elif arguments[0] == "camera":
            camera_x, camera_y = int(arguments[2]), int(arguments[3])
            self.camera.set_coords(camera_x, camera_y)

    def check_if_all_world_ids_are_correct(self):
        for obj_id in self.objects_id_dict:
            if not self.objects_id_dict[obj_id].world_id == obj_id:
                # Если id-шники не совпадают
                return False
        return True
