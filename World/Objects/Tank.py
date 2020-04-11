import logging
import random

from Consts import TANK_DEFAULT_HP, EPSILON, TANK_DEFAULT_DELAY_BEFORE_FIRE, TANK_DEFAULT_DELAY_BETWEEN_FRAMES, \
    DEFAULT_DELAY_BETWEEN_ENEMY_TRY_TO_ROTATE, DEFAULT_DELAY_BETWEEN_ENEMY_TRY_TO_SHOOT, \
    DEFAULT_DELAY_BETWEEN_ENEMY_TRY_TO_CHANGE_STATE
from World.Timer import Timer
from Consts import TANK_DEFAULT_SPEED_PER_SECOND, sprite_w, sprite_h
from World.Objects.Actable import Actable
from World.Objects.Collisionable import Collisionable, remove_if_exists_in
from World.Objects.WorldTile import WorldTile

DIRECTIONS = ["UP", "RIGHT", "DOWN", "LEFT"]


class Tank(Collisionable, Actable):
    """
    Класс танков - двигающихся объектов, взаимодействующих с миром
    """

    max_hp = None
    current_hp = None
    damage = None
    speed = TANK_DEFAULT_SPEED_PER_SECOND
    last_direction = None  # В какую сторону сейчас движется танк
    is_destroyed = None  # Уничтожен ли танк

    fire_timer = None

    # delay_before_fire = PLAYER_DEFAULT_DELAY_BEFORE_FIRE
    # current_delay_before_fire = 0

    def __init__(self, world):
        super().__init__(world)
        self.max_hp = self.current_hp = TANK_DEFAULT_HP
        self.damage = 1
        self.is_destroyed = False

        self.fire_timer = Timer(TANK_DEFAULT_DELAY_BEFORE_FIRE)

    def set_speed(self, speed):
        if speed >= 0:
            self.speed = speed
        else:
            logging.error("There was an attempt to set wrong speed for tank: {}".format(speed))

    def setup_in_world(self, x, y):
        """
        Полностью настраивает игрока, занося его в нужные массивы и применяя правильные настройки.
        :param x: Местоположение на сетке экрана
        :param y: Местоположение на сетке экрана
        :return:
        """
        self.set_pos(x * sprite_w, y * sprite_h)
        self.set_size(sprite_w, sprite_h)
        self.set_is_soild(True)

        self.parent_world.all_tanks.append(self)
        self.parent_world.collisionable_objects.append(self)
        self.parent_world.actable_object.append(self)

        if self.parent_world.need_to_log_changes:  # Для сервера
            self.parent_world.changes.append("create {}". format(self.__str__()))

    def decrease_hp(self, dmg):
        self.current_hp -= dmg
        if self.current_hp <= 0:
            self.destroy()

    def act(self):
        self.fire_timer.tick()

    def destroy(self):
        """
        Данный метод удаляет танк из нужных массивов
        :return:
        """
        remove_if_exists_in(self, self.parent_world.all_tanks)
        remove_if_exists_in(self, self.parent_world.collisionable_objects)
        remove_if_exists_in(self, self.parent_world.actable_object)
        self.is_destroyed = True
        if self.parent_world.need_to_log_changes:  # Для сервера
            self.parent_world.changes.append("destroy {}". format(self.__str__()))

    def move_to_direction(self, direction):
        if direction in DIRECTIONS:

            if direction != self.last_direction:
                # Если изменили направление движения, выполняем поправку координат
                self.correct_pos()

            if direction == "UP":
                self.smart_move(0, -self.speed)
            if direction == "RIGHT":
                self.smart_move(self.speed, 0)
            if direction == "DOWN":
                self.smart_move(0, self.speed)
            if direction == "LEFT":
                self.smart_move(-self.speed, 0)

            self.last_direction = direction

            # self.currently_moving_to = direction
            self.set_angle(self.last_direction)
            self.image.next()

            if self.parent_world.need_to_log_changes:  # Для сервера
                self.parent_world.changes.append("move {}".format(self.__str__()))
        else:
            logging.error("There was an attempt to move tank to on wrong direction: {}".format(direction))

    def correct_pos(self):
        if (x_diff := self.float_x % sprite_w) <= sprite_w * EPSILON:
            # Если близки к левой границе
            self.set_pos(self.float_x - x_diff, self.float_y)
        elif (x_diff := sprite_w - (self.float_x % sprite_w)) <= sprite_w * EPSILON:
            # Если близки к правой границе
            self.set_pos(self.float_x + x_diff, self.float_y)
            pass
        if (y_diff := self.float_y % sprite_h) <= sprite_h * EPSILON:
            # Если близки к верхней границе
            self.set_pos(self.float_x, self.float_y - y_diff)
            pass
        elif (y_diff := sprite_h - (self.float_y % sprite_h)) <= sprite_h * EPSILON:
            # Если близки к нижней границе
            self.set_pos(self.float_x, self.float_y + y_diff)
            pass

    def smart_move(self, dx, dy):
        """
        Перемещение, непозволяющее "въехать" в другие collisionable объекты
        :param dx: Перемещение по оси x
        :param dy: Перемещение по оси y
        :return:
        """
        def process_collsions(_collided_objects, _previous_x, _previous_y):
            if _collided_objects.__len__() > 0:
                for g_obj in _collided_objects:
                    distance_vector = Vector2
                    distance_vector.x = g_obj.object_rect.x + (g_obj.object_rect.width / 2) \
                                        - (self.object_rect.x + (self.object_rect.width / 2))
                    distance_vector.y = g_obj.object_rect.y + (g_obj.object_rect.height / 2) \
                                        - (self.object_rect.y + (self.object_rect.height / 2))
                    if abs(distance_vector.x) > abs(distance_vector.y):
                        # Если x больше y, значит пересекает горизонтальную грань
                        if distance_vector.x > 0:
                            # Если x больше 0, значит пересекает ЛЕВУЮ грань
                            _previous_x = g_obj.float_x - self.object_rect.width
                        else:
                            # Иначе - ПРАВУЮ
                            _previous_x = g_obj.float_x + g_obj.object_rect.width
                    else:
                        # Если y больше x, значит пересекает вертикальную грань
                        if distance_vector.y > 0:
                            # Если y больше 0, значит пересекает ВЕРХНЮЮ грань
                            _previous_y = g_obj.object_rect.y - self.object_rect.height
                        else:
                            # Иначе - НИЖНЮЮ
                            _previous_y = g_obj.float_y + g_obj.object_rect.height

                # Если с чем-то столкнулись, возвращаем прежнее положение
                self.set_pos(previous_x, previous_y)

        # Запоминаем предыдущее положение
        previous_x = self.float_x
        previous_y = self.float_y
        # previous_rect = pygame.Rect.copy(self.object_rect)

        super().move(dx, dy)

        while (collided_objects := self.check_collisions(self.parent_world.collisionable_objects)).__len__() > 0:
            # Костыль:
            # TODO: Костыль +, мозги -: пересечение танка с пулей со стороны танка
            for obj in collided_objects:
                if isinstance(obj, Bullet):
                    collided_objects.remove(obj)

            process_collsions(collided_objects, previous_x, previous_y)

        # collided_objects = self.check_collisions(self.parent_world.collisionable_objects)



    # def __str__(self):
        # return "{0} {1} {2} {3} {4} {5} {6} {7}".format(
        #     "Tank", self.object_rect.x, self.object_rect.y,
        #     self.object_rect.width, self.object_rect.height,
        #     self.image_name, self.current_angle, self.world_id
        # )


class Vector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


# TODO: разнести эти классы в разные места. Как-то.

class Player(Tank):
    def __init__(self, world):
        super().__init__(world)

    def act(self):
        super().act()

    def destroy(self):
        super().destroy()
        remove_if_exists_in(self, self.parent_world.players)

    def setup_in_world(self, x, y):
        super().setup_in_world(x, y)
        self.set_image("PLAYER_TANK")
        self.image.add_timer(TANK_DEFAULT_DELAY_BETWEEN_FRAMES)
        self.fire_timer.set(0)

        self.parent_world.players.append(self)
        # self.last_direction = "UP"


class Enemy(Tank):
    change_direction_timer = None
    shoot_timer = None
    change_state_timer = None
    previous_tries_to_change_state = None  # Количество предыдущих попыток сменить состояние

    chosen_player_to_hunt = None  # Выбранный для охоты танк игрока
    chosen_base_to_hunt = None  # Выбранная для охоты база игрока

    last_chosen_hunt_direction = None  # Последнее выбранное направление для движения во время охоты
    last_chosen_hunt_direction_in_row = None  # Сколько раз это направление было выбрано подряд

    state = None  # Текущее состояние врага

    # Возможные состояния: 0 - случайное движение
    # 1 - охота на игрока
    # 2 - охота на базу игрока

    def __init__(self, world):
        super().__init__(world)
        self.parent_world.current_amount_of_enemies += 1

        self.change_direction_timer = Timer(DEFAULT_DELAY_BETWEEN_ENEMY_TRY_TO_ROTATE)
        self.shoot_timer = Timer(DEFAULT_DELAY_BETWEEN_ENEMY_TRY_TO_SHOOT)
        self.change_state_timer = Timer(DEFAULT_DELAY_BETWEEN_ENEMY_TRY_TO_CHANGE_STATE)
        self.state = 0
        self.previous_tries_to_change_state = 0
        self.last_chosen_hunt_direction_in_row = 0

    def act(self):
        super().act()

        self.move_to_direction(self.current_angle)
        if self.change_direction_timer.is_ready():
            self.try_to_change_direction()
            self.change_direction_timer.reset()
        if self.shoot_timer.is_ready():
            self.parent_world.create_bullet(self)
            self.shoot_timer.reset()
        if self.change_state_timer.is_ready():
            self.try_to_change_state()
            self.change_state_timer.reset()

        self.change_direction_timer.tick()
        self.shoot_timer.tick()
        self.change_state_timer.tick()

    def destroy(self):
        super().destroy()
        self.parent_world.current_amount_of_enemies -= 1

    def setup_in_world(self, x, y):
        super().setup_in_world(x, y)
        self.set_image("ENEMY_TANK_0")
        self.image.add_timer(TANK_DEFAULT_DELAY_BETWEEN_FRAMES)
        # self.last_direction = "DOWN"
        self.set_angle("DOWN")

    def try_to_change_state(self):
        """
        Меняет состояние врага, переводя его на следующий этап.
        :return:
        """
        base_chance = 4
        # Проверка текущего состояния
        # Проверка положения
        if self.check_pos_on_whole_tile():
            base_chance += 10  # Увеличиваем шанс изменить состояние
        base_chance += self.previous_tries_to_change_state * 10  # Каждая предыдущая попытка изменить состояние
        # увеличивает шанс сменить его.
        # Собственно изменение состояния
        generated_number = random.randint(1, 100)
        if generated_number <= base_chance:
            self.state = self.state + 1 % 3
            if self.state == 1:
                self.chosen_player_to_hunt = random.choice(self.parent_world.players)
            if self.state == 2:
                try:
                    self.chosen_base_to_hunt = random.choice(self.parent_world.world_map.player_bases)
                except IndexError: # Если нельзя выбрать базу, сбрасываемся на первое состояние
                    self.state = 0

            self.previous_tries_to_change_state = 0
        else:
            self.previous_tries_to_change_state += 1

    def try_to_change_direction(self):
        base_chance = 4
        # Проверка на положение (%sprite_w)
        if self.check_pos_on_whole_tile():
            base_chance += 20  # Увеличиваем шанс повернуть
        # Собственно изменение направления
        generated_number = random.randint(1, 100)
        if generated_number <= base_chance:
            if self.state == 0:  # Если танк находится в состоянии "случайное движение"
                possible_directions = DIRECTIONS.copy()
                if not generated_number < 25:  # 25% шанс остаться на предыдущем направлении
                    possible_directions.remove(self.current_angle)
                chosen_direction = random.choice(possible_directions)
                self.set_angle(chosen_direction)  # Меняем направление

            else:  # Если танк находится в состоянии "охоты" на что-нибудь

                if generated_number < 10:  # 10% шанс выбрать случайное направление
                    possible_directions = DIRECTIONS.copy()
                    possible_directions.remove(self.current_angle)
                    chosen_direction = random.choice(possible_directions)
                    self.set_angle(chosen_direction)  # Меняем направление
                    return
                if self.state == 1:  # Если охотимся на игрока
                    hunt_tile_x, hunt_tile_y = self.chosen_player_to_hunt.get_world_pos()
                else:  # Если охотимся на базу
                    hunt_tile_x, hunt_tile_y = self.chosen_base_to_hunt.get_world_pos()

                chosen_angle = self.get_optimal_angle_for_tile(hunt_tile_x, hunt_tile_y)
                self.set_angle(chosen_angle)

                if self.last_chosen_hunt_direction == chosen_angle:
                    self.last_chosen_hunt_direction_in_row += 1
                else:
                    self.last_chosen_hunt_direction = chosen_angle
                    self.last_chosen_hunt_direction_in_row = 0

    def check_pos_on_whole_tile(self):
        """
        Проверяет положение танка. Если одна из координат кратна целому числу тайлов мира, возвращает True.
        """
        if self.object_rect.x % sprite_w == 0:
            # Проверка кооридинаты x
            return True
        if self.object_rect.y % sprite_h == 0:
            # Проверка кооридинаты y
            return True
        return False

    def get_optimal_angle_for_tile(self, tile_x, tile_y):
        """
        Возвращает направление, на которое нужно повернуться, чтобы добраться до нужного тайла
        :return:
        """
        tank_x, tank_y = self.get_world_pos()
        x_difference = tank_x - tile_x
        y_difference = tank_y - tile_y
        if x_difference > 0:
            # Если танк правее базы:
            return_x = "LEFT"
        else:
            # Если танк левее базы:
            return_x = "RIGHT"

        if y_difference > 0:
            # Если танк ниже базы:
            return_y = "UP"
        else:
            # Если танк выше базы:
            return_y = "DOWN"

        if self.last_chosen_hunt_direction_in_row > 3:  # Если приказы повторяются
            # Передаём коориданты по другой оси
            if abs(x_difference) > abs(y_difference):
                return return_y
            else:
                return return_x

        if abs(x_difference) > abs(y_difference):
            return return_x
        else:
            return return_y


class Bullet(Collisionable, Actable):
    parent_tank = None  # Танк, который выстрелил данной пулей
    bullet_direction = None  # Направление, в котором летит пуля

    speed = TANK_DEFAULT_SPEED_PER_SECOND * 2

    def __init__(self, world, parent_tank):
        super().__init__(world)
        self.parent_tank = parent_tank
        self.on_collision = bullet_collision
        self.set_is_soild(True)  # Пуля - твёрдая

    def create(self):
        """
        Данный метод помещает пулю в нужные массивы, даёт ей направление движения
        :return:
        """
        self.set_image("BULLET")

        self.bullet_direction = self.parent_tank.last_direction
        self.set_angle(self.bullet_direction)  # Установка поворота спрайта
        self.set_size(sprite_w / 12, sprite_h / 4)  # Относительный размер пули от размера спрайта

        # Поправка координат для того, чтобы пуля вылетала из ствола
        if self.bullet_direction == "UP":
            self.set_pos(self.parent_tank.float_x + self.parent_tank.object_rect.width / 2 - self.object_rect.width / 2,
                         self.parent_tank.float_y)
        if self.bullet_direction == "DOWN":
            self.set_pos(self.parent_tank.float_x + self.parent_tank.object_rect.width / 2 - self.object_rect.width / 2,
                         self.parent_tank.float_y + self.parent_tank.object_rect.height)
        if self.bullet_direction == "LEFT":
            self.set_pos(self.parent_tank.float_x,
                         self.parent_tank.float_y + self.parent_tank.object_rect.height / 2 - self.object_rect.width / 2)
        if self.bullet_direction == "RIGHT":
            self.set_pos(self.parent_tank.float_x + self.parent_tank.object_rect.width,
                         self.parent_tank.float_y + self.parent_tank.object_rect.height / 2 - self.object_rect.width / 2)

        self.parent_world.collisionable_objects.append(self)
        self.parent_world.actable_object.append(self)
        self.parent_world.all_bullets.append(self)
        if self.parent_world.need_to_log_changes:  # Для сервера
            self.parent_world.changes.append("create {}". format(self.__str__()))

    def destroy(self):
        """
        Данный метод удаляет пулю из нужных массивов
        """
        remove_if_exists_in(self, self.parent_world.collisionable_objects)
        remove_if_exists_in(self, self.parent_world.actable_object)
        remove_if_exists_in(self, self.parent_world.all_bullets)
        if self.parent_world.need_to_log_changes:  # Для сервера
            self.parent_world.changes.append("destroy {}". format(self.__str__()))

    def act(self):
        self.check_and_process_collisions(self.parent_world.collisionable_objects)  # Проверяем коллижены
        self.bullet_move()  # Двигаем пулю

    def bullet_move(self):
        if self.bullet_direction == "UP":
            self.move(0, -self.speed)
        if self.bullet_direction == "DOWN":
            self.move(0, self.speed)
        if self.bullet_direction == "LEFT":
            self.move(-self.speed, 0)
        if self.bullet_direction == "RIGHT":
            self.move(self.speed, 0)
        if self.parent_world.need_to_log_changes:  # Для сервера
            self.parent_world.changes.append("move {}". format(self.__str__()))


def bullet_collision(bullet, obj):
    if obj is bullet.parent_tank:  # Не реагируем на коллизию с танком, который выстрелил
        return
    if obj.is_solid:  # Если объект твёрдый
        if isinstance(obj, Player) or isinstance(obj, Enemy):
            bullet.destroy()
            bullet.parent_tank.fire_timer.set(min(bullet.parent_tank.fire_timer.current_delay, 10))
            # Если столкнулись с танком:
            if isinstance(obj, Player):
                # Если попали в игрока
                if isinstance(bullet.parent_tank, Enemy):
                    # Если стрелял враг
                    obj.decrease_hp(bullet.parent_tank.damage)
                    # bullet.destroy()
                    # bullet.parent_tank.fire_timer.set(min(bullet.parent_tank.fire_timer.current_delay, 10))
                # Если игрок попал в игрока - ничего не будет
                # TODO: сделать PvP режим!
            elif isinstance(obj, Enemy):
                # Если попали во врага
                if isinstance(bullet.parent_tank, Player):
                    # Если стрелял игрок
                    obj.decrease_hp(bullet.parent_tank.damage)
                    # bullet.destroy()
                    # bullet.parent_tank.fire_timer.set(min(bullet.parent_tank.fire_timer.current_delay, 10))
                # Если враг попал в игрока - ничего не будет
        elif isinstance(obj, Bullet):
            bullet.destroy()
            obj.destroy()
            bullet.parent_tank.fire_timer.set(min(bullet.parent_tank.fire_timer.current_delay, 10))
        elif isinstance(obj, WorldTile):
            # Если столкнулись с тайлом мира
            obj.get_hit(bullet.bullet_direction)
            if not obj.is_passable_for_bullets:
                bullet.destroy()
                bullet.parent_tank.fire_timer.set(min(bullet.parent_tank.fire_timer.current_delay, 10))
