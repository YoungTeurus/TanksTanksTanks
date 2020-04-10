import logging

from Consts import PLAYER_DEFAULT_HP, EPSILON, PLAYER_DEFAULT_DELAY_BEFORE_FIRE, TANK_DEFAULT_DELAY_BETWEEN_FRAMES
from World.Timer import Timer
from Consts import TANK_DEFAULT_SPEED_PER_SECOND, sprite_w, sprite_h
from World.Objects.Actable import Actable
from World.Objects.Collisionable import Collisionable, remove_if_exists_in
from World.Objects.WorldTile import WorldTile


class Tank(Collisionable, Actable):
    """
    Класс танков - двигающихся объектов, взаимодействующих с миром
    """

    max_hp = None
    current_hp = None
    damage = None
    speed = TANK_DEFAULT_SPEED_PER_SECOND
    last_direction = None  # В какую сторону сейчас движется танк

    fire_timer = None

    # delay_before_fire = PLAYER_DEFAULT_DELAY_BEFORE_FIRE
    # current_delay_before_fire = 0

    def __init__(self, world):
        super().__init__(world)
        self.max_hp = self.current_hp = PLAYER_DEFAULT_HP
        self.damage = 1

        self.fire_timer = Timer(PLAYER_DEFAULT_DELAY_BEFORE_FIRE)

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

    def decrease_hp(self, dmg):
        self.current_hp -= dmg
        if (self.current_hp <= 0):
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

    def move_to_direction(self, direction):
        # Возможнные направления для движения:
        # direction_dict = {
        #     "UP":       [0,             -self.speed],
        #     "RIGHT":    [self.speed,    0],
        #     "DOWN":     [0,             self.speed],
        #     "LEFT":     [-self.speed,   0]
        # }
        directions = ["UP", "RIGHT", "DOWN", "LEFT"]

        if direction in directions:

            if (direction != self.last_direction):
                self.correct_pos()

            if direction == "UP":
                self.smart_move(0,             -self.speed)
            if direction == "RIGHT":
                self.smart_move(self.speed,    0)
            if direction == "DOWN":
                self.smart_move(0,             self.speed)
            if direction == "LEFT":
                self.smart_move(-self.speed,   0)

            self.last_direction = direction

            self.currently_moving_to = direction
            self.set_angle(direction)
            self.image.next()
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

        # Запоминаем предыдущее положение
        previous_x = self.float_x
        previous_y = self.float_y
        # previous_rect = pygame.Rect.copy(self.object_rect)

        super().move(dx, dy)

        collided_objects = self.check_collisions(self.parent_world.collisionable_objects)

        # Костыль:
        # TODO: Костыль +, мозги -: пересечение танка с пулей со стороны танка
        for obj in collided_objects:
            if isinstance(obj, Bullet):
                collided_objects.remove(obj)

        if collided_objects.__len__() > 0:
            for obj in collided_objects:
                distance_vector = Vector2
                distance_vector.x = obj.object_rect.x + (obj.object_rect.width / 2) \
                                    - (self.object_rect.x + (self.object_rect.width / 2))
                distance_vector.y = obj.object_rect.y + (obj.object_rect.height / 2) \
                                    - (self.object_rect.y + (self.object_rect.height / 2))
                if abs(distance_vector.x) > abs(distance_vector.y):
                    # Если x больше y, значит пересекает горизонтальную грань
                    if distance_vector.x > 0:
                        # Если x больше 0, значит пересекает ЛЕВУЮ грань
                        previous_x = obj.float_x - self.object_rect.width
                    else:
                        # Иначе - ПРАВУЮ
                        previous_x = obj.float_x + obj.object_rect.width
                else:
                    # Если y больше x, значит пересекает вертикальную грань
                    if distance_vector.y > 0:
                        # Если y больше 0, значит пересекает ВЕРХНЮЮ грань
                        previous_y = obj.object_rect.y - self.object_rect.height
                    else:
                        # Иначе - НИЖНЮЮ
                        previous_y = obj.float_y + obj.object_rect.height

            # Если с чем-то столкнулись, возвращаем прежнее положение
            self.set_pos(previous_x, previous_y)


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

    def setup_in_world(self, x, y):
        super().setup_in_world(x, y)
        self.set_image("PLAYER_TANK")
        self.image.add_timer(TANK_DEFAULT_DELAY_BETWEEN_FRAMES)
        self.last_direction = "UP"

class Enemy(Tank):

    move_timer = None
    shoot_timer = None

    def __init__(self, world):
        super().__init__(world)
        self.parent_world.current_amount_of_enemies += 1

        self.move_timer = Timer(10)
        self.shoot_timer = Timer(100)

    def act(self):
        super().act()

        self.move_to_direction(self.last_direction)
        # if self.shoot_timer.is_ready():
        #     self.parent_world.create_bullet(self)
        #     self.shoot_timer.reset()

        self.move_timer.tick()
        self.shoot_timer.tick()

    def destroy(self):
        super().destroy()
        self.parent_world.current_amount_of_enemies -= 1

    def setup_in_world(self, x, y):
        super().setup_in_world(x, y)
        self.set_image("ENEMY_TANK_0")
        self.image.add_timer(TANK_DEFAULT_DELAY_BETWEEN_FRAMES)
        self.last_direction = "DOWN"
        self.set_angle("DOWN")


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

    def destroy(self):
        """
        Данный метод удаляет пулю из нужных массивов
        """
        remove_if_exists_in(self, self.parent_world.collisionable_objects)
        remove_if_exists_in(self, self.parent_world.actable_object)
        remove_if_exists_in(self, self.parent_world.all_bullets)

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
