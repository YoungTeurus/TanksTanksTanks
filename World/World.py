from distutils.util import strtobool
from typing import List, Dict, Optional, Union

from pygame.surface import Surface

from Consts import DEFAULT_DELAY_BETWEEN_ENEMY_SPAWN, MAX_ENEMIES_ON_ONE_MOMENT, DEFAULT_ENEMIES_ON_LEVEL, \
    TILESETS, PLAYER_TANKS_COLORS, MAX_PLAYER_TANK_HP, START_MAP_NAME
from Files import ImageLoader
from Images.Tileset import Tileset
from Multiplayer.Senders import EVENT_SERVER_SEND_PLAYERS_TANKS_IDS
from World.Camera import Camera
from World.Map import Map
import random

from World.Objects.Collisionable import remove_if_exists_in
from World.Objects.RotatableWorldObject import RotatableWorldObject
from World.Objects.Tank import PlayerTank, EnemyTank, Bullet, Tank
from World.Objects.WorldTile import WorldTile
from World.Timer import Timer


class World:
    """
    Класс, содеражащий в себе информацию об отображаемой карте и всех объектах на ней.
    """
    parent_game = None  # Объект класса Game

    camera: Camera = None  # Камера
    players: List[PlayerTank] = None  # Игрок
    parent_surface: Surface = None  # Та поверхность, на которой будет происходить отрисовка всего мира
    parent_image_loader: ImageLoader = None

    tilesets: Dict[str, Tileset] = None  # Словарь всех используемых тайлсетов

    all_tanks: List[Tank] = None  # Все танки, которые необходимо отрисовывать
    all_enemies: List[EnemyTank] = None  # Все вражеские танки
    all_bullets: list = None  # Все пули, которые необходимо отрисовывать
    all_tiles: list = None  # Все тайлы, которые необходимо отрисовывать (тайлы заносятся сюда в .set_tile() )
    collisionable_objects: list = None  # Все объекты, с которыми нужно проверять столкновение
    actable_object: list = None  # Все объекты, для которых нужно вызывать Act() каждый раз

    all_drawable_client: list = None  # Все объекты, которые нужно отрисовать на стороне клиента

    enemy_spawn_timer = None  # Таймер для спавна нового врага
    current_amount_of_enemies = None  # Количество врагов на поле в данный момент
    enemies_remains = None  # Сколько врагов осталось уничтожить

    world_map = None

    auto_id_set = None  # Если данную переменную установить в True, то World будет присваивать id каждому tile
    # и объекту самостоятельно.
    need_to_log_changes = None  # Нужно ли отслеживать изменения. Только в мультиплеере.
    changes: list = None  # Различия, произошедшие за текущий такт игры. Содержит команды, которые необходимо выполнить.
    last_id: int = None  # Последний свободный id

    objects_id_dict: Dict[int, Union[RotatableWorldObject, WorldTile]] = None  # Словарь ВСЕХ объектов по их ID

    def __init__(self, parent_game, parent_surface, image_loader: ImageLoader, is_server):
        self.all_drawable_client = []
        self.all_tanks: List[Tank] = []
        self.all_enemies = []
        self.all_bullets = []
        self.all_tiles = []
        self.collisionable_objects = []
        self.actable_object = []
        self.players = []
        self.changes = []
        self.parent_game = parent_game
        self.parent_surface = parent_surface
        self.parent_image_loader = image_loader

        self.load_tilesets()
        # self.tileset = Tileset("tileset_world", image_w, image_h,
        #                        self.parent_image_loader.get_image_by_name("tileset_world"))
        # # TODO: СУПЕР-ВРЕМЕННОЕ решение:
        # self.explosion_tileset = Tileset("tileset_explosion", 96, 96,
        #                                  self.parent_image_loader.get_image_by_name("tileset_explosion"))

        self.enemy_spawn_timer = Timer(DEFAULT_DELAY_BETWEEN_ENEMY_SPAWN)
        self.current_amount_of_enemies = 0
        self.enemies_remains = DEFAULT_ENEMIES_ON_LEVEL
        # self.size = size

        self.world_map = Map(self)
        self.camera = Camera(self)
        self.need_to_log_changes = False
        self.objects_id_dict = dict()
        self.auto_id_set = is_server
        self.last_id = 0

    def load_tilesets(self) -> None:
        """
        Создаёт тайлсеты из всех файлов, начинающихся с tileset_...
        """
        self.tilesets = dict()
        for tileset_name in TILESETS:
            temp_tileset = Tileset(tileset_name, TILESETS[tileset_name], TILESETS[tileset_name],
                                   self.parent_image_loader.get_image_by_name(tileset_name))
            self.tilesets[tileset_name] = temp_tileset

    def load_world_map_by_map_name(self, map_name: str = None):
        if map_name is not None:
            self.load_map(self.parent_game.map_loader.get_map_id_by_name(map_name))
        else:
            self.load_map(self.parent_game.map_loader.get_map_id_by_name(START_MAP_NAME))  # На всякий случай
        # self.spawn_player()
        # self.center_camera_on_player()

    def load_world_map_by_map_id(self, map_id: int):
        self.load_map(map_id)

    def get_last_id(self):
        self.last_id += 1
        return self.last_id - 1

    def load_map(self, map_id, server_map: bool = False):
        """
        Загружает карту из файла по указанному map_id, а также создаёт object_map.
        :param server_map: Если True, то карта грузится из папки downloades.
        :param map_id: ID карты для загрузки.
        """
        self.world_map.load_by_id(map_id, server_map)
        self.world_map.create_object_map()
        self.world_map.check()

    def clear(self) -> None:
        """
        Очищает все поля значащие поля класса.
        """
        self.objects_id_dict.clear()
        self.all_enemies.clear()
        self.all_tanks.clear()
        self.all_drawable_client.clear()
        self.all_bullets.clear()
        self.all_tiles.clear()
        self.actable_object.clear()
        self.collisionable_objects.clear()
        self.players.clear()

        self.last_id = 0
        self.enemies_remains = DEFAULT_ENEMIES_ON_LEVEL

    def reload_map(self, map_id, server_map: bool = False) -> None:
        """
        Сбрасывает старую карту и загружает новую. Если сервер - отсылает клиентам сообщение о необходимости сделать
         то же самое.
        """
        if self.parent_game.multi and self.parent_game.is_server:
            # Сброс готовности игроков:
            self.clear()
            for client in self.parent_game.serverside_sender.clients:
                client.ready = False
            self.load_map(map_id, server_map)

            # self.parent_game.wait_for_players() <- выполнится в main_cycle
            self.parent_game.serverside_sender.send_reload_world(map_id)

            self.parent_game.game_started = False
        else:
            num_of_players = self.players.__len__()

            self.clear()

            self.load_map(map_id, server_map)
            for i in range(num_of_players):
                self.spawn_player()

    def spawn_player(self, player_id=None, start_lifes: int = MAX_PLAYER_TANK_HP,
                     send_ids_to_players: bool = False):
        """
        Спавнит игрока под айди id на одной из точек спавна
        :param send_ids_to_players: Отправить ли игрокам новые id их танков? Нужно для перерождения.
        :param start_lifes: Начальное количество жизней у танка.
        :param player_id: Айди игрока (для мультиплеера)
        :return:
        """
        if player_id is None:
            player_id = len(self.players)
        place_to_spawn = self.world_map.player_spawn_places[player_id]
        # place_to_spawn = random.choice(self.world_map.player_spawn_places)
        (place_to_spawn_x, place_to_spawn_y) = place_to_spawn.get_world_pos()
        new_player = PlayerTank(self, player_id, start_lifes)
        new_player.setup_in_world(place_to_spawn_x, place_to_spawn_y)
        new_player.add_color(PLAYER_TANKS_COLORS[player_id])
        if new_player.lifes <= 0:
            new_player.set_visible(False)

        if not self.parent_game.multi:
            self.parent_game.client_world_object_id = new_player.world_id

        if send_ids_to_players and self.parent_game.multi:
            # Срабатывает при перерождении.
            id_players_ip_combo: dict = dict()
            for (i, client) in enumerate(self.parent_game.serverside_sender.clients):
                id_players_ip_combo[client.ip_port_combo] = self.players[client.player_id].world_id
            self.parent_game.serverside_sender.send_event(EVENT_SERVER_SEND_PLAYERS_TANKS_IDS, id_players_ip_combo,
                                                          send_to_player_id=player_id)

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

    def check_level_over(self) -> bool:
        if len(self.all_enemies) <= 0 and self.enemies_remains <= 0:
            return True
        return False

    def check_game_over(self) -> Optional[dict]:
        """
        Проверяет, наступило ли условие конца игры, и если наступило - возвращает словарь, который
         содержит информацию о конце игры.
        :return:
        """
        for player in self.players:
            if player.lifes == 0:
                if self.parent_game.multi:
                    # Если это сервер и мультиплеерная игра
                    # Получаем игрока:
                    died_client = self.parent_game.serverside_sender.get_client_by_player_id(player.player_id)
                    return {
                        "type": "player_died",
                        "player_name": died_client.player_name,
                    }
                else:
                    # Если это одиночка
                    return {
                        "type": "player_died",
                        "player_name": "",
                    }
        for base in self.world_map.player_bases:
            if base.player_base_hp <= 0:
                return {
                    "type": "base_destroyed"
                }
        return None

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
                enemy = EnemyTank(self)
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
        for change in changes:
            self.process_change(changes[change])

    def process_change(self, change):
        arguments = change.split(" ")
        if arguments[0] == "create":
            if arguments[1] == "RotatableWorldObject":
                coord_x, coord_y = int(arguments[2]), int(arguments[3])
                width, height = int(arguments[4]), int(arguments[5])
                tileset_name = arguments[6]
                image_name, start_angle = arguments[7], arguments[8]
                world_id = int(arguments[9])
                temp_object = RotatableWorldObject(self, tileset_name)
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
        elif arguments[0] == "change_color":
            world_id = int(arguments[1])
            color = (int(arguments[2]), int(arguments[3]), int(arguments[4]))  # RGB цвет
            self.objects_id_dict[world_id].add_color(color)
        elif arguments[0] == "visible":
            world_id = int(arguments[1])
            is_visible = bool(strtobool(arguments[2]))
            # is_visible = bool(arguments[2])

            self.objects_id_dict[world_id].set_visible(is_visible)
