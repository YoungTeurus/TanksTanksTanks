import logging

import pygame

from Consts import PLAYER_DEFAULT_HP, TANK_DEFAULT_SPEED_PER_SECOND
from World.Objects.Collisionable import Collisionable


class Tank(Collisionable):
    """
    Класс танков - двигающихся объектов, взаимодействующих с миром
    """

    max_hp = None
    current_hp = None
    speed = TANK_DEFAULT_SPEED_PER_SECOND
    currently_moving_to = None  # В какую сторону сейчас движется танк

    def __init__(self, world):
        super().__init__(world)
        self.max_hp = self.current_hp = PLAYER_DEFAULT_HP

    def set_speed(self, speed):
        if speed >= 0:
            self.speed = speed
        else:
            logging.error("There was an attempt to set wrong speed for tank: {}".format(speed))

    def move_to_direction(self, direction):
        # Возможнные направления для движения:
        direction_dict = {
            "UP":       [0,             -self.speed],
            "RIGHT":    [self.speed,    0],
            "DOWN":     [0,             self.speed],
            "LEFT":     [-self.speed,   0]
        }

        # Двигаемся только если сейчас никуда не двигаемся или уже двигаемся в ту сторону
        # if direction in direction_dict and (self.currently_moving_to is None or self.currently_moving_to == direction):
        if direction in direction_dict:

            previous_rect = pygame.Rect.copy(self.object_rect)

            self.smart_move(direction_dict[direction][0], direction_dict[direction][1])

            # super().move(direction_dict[direction][0], direction_dict[direction][1])

            # if self.check_collsions(self.parent_world.collisionable_objects).__len__() > 0:
            #     # Если с чем-то столкнулись, останавливаем движение
            #     # TODO: Не останавливаться, если столкнулись с пулей, например
            #     self.object_rect = previous_rect
            #     print("I bumped something!")

            self.currently_moving_to = direction
            self.set_angle(direction)
        else:
            logging.error("There was an attempt to move tank to on wrong direction: {}".format(direction))

    def stop_moving(self):
        """
        Сбрасывает флаг движения
        :return:
        """
        self.currently_moving_to = None
