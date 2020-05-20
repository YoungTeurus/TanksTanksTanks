from pygame.constants import BLEND_RGBA_MULT, SRCALPHA
from pygame.event import EventType
from pygame.rect import Rect
from pygame.surface import Surface
from typing import List

from Consts import GREY, BLACK, DARK_GREY
from Menu.MenuObjects.MenuObject import MenuObject, SKIP_EVENT

HALF_BLACK = (0, 0, 0, 64)


class PopupBox(MenuObject):
    """
    Всплывающее окно, которое полностью перехватывает управление.
    --------------------------------------
    |                                    |
    |          --------------            |
    |          |  ////////  |            |
    |          |            |            |
    |          |  V      X  |            |
    |          --------------            |
    |                                    |
    |                                    |
    --------------------------------------
    """

    box_surface: Surface = None  # Поверхность всплывшего окошка
    dark_background: Surface = None  # Полупрозрачный фон (для одноразового создания поверхности)

    rect: Rect = None
    color: tuple = None

    box_objects: List[MenuObject] = None  # Список всех объектов внутри окошка
    is_running: bool = None  # Показывается ли сейчас окошко
    need_to_darken_background: bool = None  # Нужно ли затемнять остальное окно

    def __init__(self, window_surface: Surface, pos: tuple = None, color: tuple = None, darken_background: bool = None):
        self.window_surface = window_surface
        self.box_objects = []

        self.rect = Rect(0, 0, 100, 50)  # Стандартные размер и положение окошка

        if pos is not None:
            self.set_box_pos(pos[0], pos[1], pos[2], pos[3])

        if color is not None:
            self.color = color
        else:
            self.color = GREY  # Стандартный цвет кнопки

        if darken_background is not None:
            self.need_to_darken_background = darken_background
        else:
            self.need_to_darken_background = True

    def add_object(self, obj: MenuObject):
        """
        :param obj: Объект, переданный таким образом всё ещё будет принимать event-ы, даже при запущенном меню
        """
        self.box_objects.append(obj)

    def draw(self):
        if self.need_to_darken_background:
            if self.dark_background is None:
                self.dark_background = Surface((self.window_surface.get_width(), self.window_surface.get_height()),
                                               SRCALPHA)
                self.dark_background.fill(HALF_BLACK)
            # Наложение полупрозрачного чёрного фона на картинку
            self.window_surface.blit(self.dark_background, (0, 0))
        # Отрисовка тени:
        self.window_surface.fill(BLACK, (self.rect.x + 2, self.rect.y + 2, self.rect.width, self.rect.height))
        # Отрисовка самого PopupBox-а
        self.window_surface.fill(self.color, self.rect)

        for obj in self.box_objects:
            obj.draw()

    def handle_event(self, event: EventType):
        for obj in self.box_objects:
            obj.handle_event(event)
        return SKIP_EVENT  # Передаём знак того, что ивент нужно пропустить для всех остальных объектов меню

    def update(self):
        for obj in self.box_objects:
            obj.update()

    def set_box_pos(self, pos_x, pos_y, width, height):
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.rect.width = width
        self.rect.height = height
