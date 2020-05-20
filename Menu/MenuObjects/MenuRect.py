from typing import Optional

import pygame
from pygame.rect import Rect
from pygame.surface import Surface
from Menu.MenuObjects.MenuObject import MenuObject


class MenuRect(MenuObject):
    rect: Rect = None
    frame_color: Optional[tuple] = None
    fill_color: Optional[tuple] = None

    def __init__(self, window_surface: Surface, pos: tuple = None, frame_color: tuple = None,
                 fill_color: tuple = None):
        self.window_surface = window_surface
        self.rect = Rect(0, 0, 100, 50)  # Стандартные размер и положение рамки

        if pos is not None:
            self.set_pos(pos[0], pos[1], pos[2], pos[3])

        if frame_color is not None:
            self.frame_color = frame_color
        else:
            self.frame_color = None  # Стандартный цвет обводки

        if fill_color is not None:
            self.fill_color = fill_color
        else:
            self.fill_color = None  # Стандартный цвет заливки

    def set_pos(self, pos_x, pos_y, width, height):
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.rect.width = width
        self.rect.height = height

    def draw(self):
        if self.fill_color is not None:
            self.window_surface.fill(self.fill_color, self.rect)
        if self.frame_color is not None:
            pygame.draw.rect(self.window_surface, self.frame_color, self.rect, 2)
