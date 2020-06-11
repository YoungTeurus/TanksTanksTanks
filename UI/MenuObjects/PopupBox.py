from pygame.constants import BLEND_RGBA_MULT, SRCALPHA
from pygame.event import EventType
from pygame.rect import Rect
from pygame.surface import Surface
from typing import List

from Consts import GREY, BLACK, DARK_GREY
from UI.MenuObjects.MenuObject import MenuObject, SKIP_EVENT

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

    dark_background: Surface = None  # Полупрозрачный фон (для одноразового создания поверхности)

    rect: Rect = None
    color: tuple = None

    box_objects: List[MenuObject] = None  # Список всех объектов внутри окошка
    is_running: bool = None  # Показывается ли сейчас окошко
    need_to_darken_background: bool = None  # Нужно ли затемнять остальное окно

    blocking: bool = None  # Блокирует ли PopupBox остальные input-ы
    fill: bool = None  # Нужно ли заливать PopupBox цветом color

    transparent_background_shadow: Surface = None  # Полупрозрачный фон для тени fill-а
    transparent_background: Surface = None  # Полупрозрачный фон для fill-а
    transparent: bool = None  # Использует ли цвет заливки прозрачность
    transparent_alpha: int = None  # Сила alpha-канала цвета фона

    def __init__(self, window_surface: Surface, pos: tuple = None, color: tuple = None, darken_background: bool = None,
                 blocking: bool = True, fill: bool = True, transparent: bool = False, alpha_color: int = 0):
        self.window_surface = window_surface
        self.box_objects = []

        self.rect = Rect(0, 0, 100, 50)  # Стандартные размер и положение окошка

        if pos is not None:
            self.set_box_pos(pos[0], pos[1], pos[2], pos[3])

        if color is not None:
            self.color = color
        else:
            self.color = GREY  # Стандартный цвет заливки PopupBox-а.

        if darken_background is not None:
            self.need_to_darken_background = darken_background
        else:
            self.need_to_darken_background = True

        self.transparent = transparent
        if self.transparent:
            self.transparent_alpha = alpha_color

        self.blocking = blocking
        self.fill = fill

    def add_object(self, obj: MenuObject):
        """
        :param obj: Объект, переданный таким образом всё ещё будет принимать event-ы, даже при запущенном меню
        """
        self.box_objects.append(obj)

    def clear(self) -> None:
        """
        Удаляеет все объекты в PopubBox-е.
        """
        self.box_objects.clear()

    def draw(self):
        # Затемнение фона
        if self.need_to_darken_background:
            if self.dark_background is None:
                self.dark_background = Surface((self.window_surface.get_width(), self.window_surface.get_height()),
                                               SRCALPHA)
                self.dark_background.fill(HALF_BLACK)
            # Наложение полупрозрачного чёрного фона на картинку
            self.window_surface.blit(self.dark_background, (0, 0))

        # Заливка rect-а.
        if self.fill:
            if self.transparent:
                # Если прозрачный цвет заливки
                if self.transparent_background is None:
                    self.transparent_background = Surface((self.rect.w, self.rect.h), SRCALPHA)
                    self.transparent_background.fill((self.color[0], self.color[1],
                                                      self.color[2], self.transparent_alpha))
                if self.transparent_background_shadow is None:
                    self.transparent_background_shadow = Surface((self.rect.w, self.rect.h), SRCALPHA)
                    self.transparent_background_shadow.fill(HALF_BLACK)
                # Отрисовка тени:
                self.window_surface.blit(self.transparent_background_shadow, (self.rect.x + 2, self.rect.y + 2))
                # Отрисовка самого PopupBox-а
                self.window_surface.blit(self.transparent_background, (self.rect.x, self.rect.y))
            else:
                # Если непрозрачный цвет заливки
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
