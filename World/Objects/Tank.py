import logging

from Consts import PLAYER_DEFAULT_HP, TANK_DEFAULT_SPEED_PER_SECOND, sprite_w, EPSILON, sprite_h, \
    PLAYER_DEFAULT_DELAY_BEFORE_FIRE, TANK_DEFAULT_DELAY_BETWEEN_FRAMES
from World.Objects.Actable import Actable
from World.Objects.Collisionable import Collisionable, remove_if_exists_in


class Tank(Collisionable, Actable):
    """
    Класс танков - двигающихся объектов, взаимодействующих с миром
    """

    max_hp = None
    current_hp = None
    speed = TANK_DEFAULT_SPEED_PER_SECOND
    last_direction = None  # В какую сторону сейчас движется танк

    delay_before_fire = PLAYER_DEFAULT_DELAY_BEFORE_FIRE
    current_delay_before_fire = 0

    def __init__(self, world):
        super().__init__(world)
        self.max_hp = self.current_hp = PLAYER_DEFAULT_HP

    def set_speed(self, speed):
        if speed >= 0:
            self.speed = speed
        else:
            logging.error("There was an attempt to set wrong speed for tank: {}".format(speed))

    def set_current_delay_before_fire_to_full(self):
        self.current_delay_before_fire = self.delay_before_fire

    def set_current_delay_before_fire_to(self, value):
        self.current_delay_before_fire = value

    def setup_in_world(self, x, y):
        """
        Полностью настраивает игрока, занося его в нужные массивы и применяя правильные настройки.
        :param x: Местоположение на сетке экрана
        :param y: Местоположение на сетке экрана
        :return:
        """
        self.set_pos(x * sprite_w, y * sprite_h)
        self.set_size(sprite_w, sprite_h)
        self.set_image("PLAYER_TANK")
        self.image.add_timer(TANK_DEFAULT_DELAY_BETWEEN_FRAMES)
        self.set_is_soild(True)
        self.last_direction = "UP"

        self.parent_world.all_tanks.append(self)
        self.parent_world.collisionable_objects.append(self)
        self.parent_world.actable_object.append(self)

    def decrease_hp(self):
        pass

    def act(self):
        if self.current_delay_before_fire > 0:
            self.current_delay_before_fire -= 1

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
