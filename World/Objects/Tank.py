import logging

import pygame

from Consts import PLAYER_DEFAULT_HP, TANK_DEFAULT_SPEED_PER_SECOND, sprite_w, EPSILON, sprite_h
from World.Objects.Collisionable import Collisionable


class Tank(Collisionable):
    """
    Класс танков - двигающихся объектов, взаимодействующих с миром
    """

    max_hp = None
    current_hp = None
    speed = TANK_DEFAULT_SPEED_PER_SECOND
    last_direction = None  # В какую сторону сейчас движется танк

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
        # direction_dict = {
        #     "UP":       [0,             -self.speed],
        #     "RIGHT":    [self.speed,    0],
        #     "DOWN":     [0,             self.speed],
        #     "LEFT":     [-self.speed,   0]
        # }
        directions = ["UP", "RIGHT", "DOWN", "LEFT"]
        # TODO: Подумать, на что можно заменить данный словарь

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

    # def stop_moving(self):
    #     """
    #     Сбрасывает флаг движения
    #     :return:
    #     """
    #     self.currently_moving_to = None
