from pygame.rect import Rect

from Menu.MenuObjects.MenuObject import MenuObject


class MenuObjectClickable(MenuObject):
    rect: Rect = None  # Прямоугольник для отрисовки

    function_onClick: list = None  # Функции, выполняемая при нажатии
    function_args: list = None

    def set_pos(self, pos_x, pos_y, width, height):
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.rect.width = width
        self.rect.height = height

    # noinspection PyPep8Naming
    def add_function_onClick(self, function, arg=None):
        if self.function_onClick is None:
            self.function_onClick = []
        if self.function_args is None:
            self.function_args = []
        self.function_onClick.append(function)
        self.function_args.append(arg)
