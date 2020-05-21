from typing import Optional

import pygame
from pygame.surface import Surface

from Consts import WHITE
from Menu.MenuObjects.MenuObject import MenuObject


class MenuLine(MenuObject):
    startpos: tuple = None
    endpos: tuple = None
    color: Optional[tuple] = None

    def __init__(self, window_surface: Surface, startpos: tuple, endpos: tuple, color: tuple = None):
        self.window_surface = window_surface

        self.startpos = startpos
        self.endpos = endpos

        if color is not None:
            self.color = color
        else:
            self.color = WHITE

    def draw(self):
        pygame.draw.aaline(self.window_surface, self.color, self.startpos, self.endpos)
