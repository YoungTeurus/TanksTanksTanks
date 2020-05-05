from pygame.rect import Rect


class MenuObject:
    rect: Rect = None  # Прямоугольник для отрисовки

    function_onClick = None  # Функция, выполняемая при нажатии

    def draw(self):
        pass

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def set_pos(self, pos_x, pos_y, width, height):
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.rect.width = width
        self.rect.height = height

    # noinspection PyPep8Naming
    def set_function_onClick(self, function):
        self.function_onClick = function
