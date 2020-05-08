from pygame.constants import KEYDOWN

from Menu.MenuObjects.MenuObject import MenuObject


class ButtonTrigger(MenuObject):
    """
    Невидимый объект, который выполняет какое-либо действие по нажатию определённой клавиши.
    """

    key = None  # Кнопка, на которую необходимо нажать
    functions: list = None  # Действие по нажатию кнопки

    is_active: bool = None  # Активен ли триггер

    def __init__(self, key, function=None, function_list: list = None, active: bool = None):
        self.key = key
        if function is not None:
            self.add_function(function)
        elif function_list is not None:
            for fun in function_list:
                self.add_function(fun)
        else:
            raise ValueError("ButtonTrigger не имеет функции для выполнения!")

        if active is not None:
            self.set_active(active)
        else:
            self.set_active(True)

    def add_function(self, function):
        if self.functions is None:
            self.functions = []
        self.functions.append(function)

    def set_active(self, active: bool):
        self.is_active = active

    def handle_event(self, event):
        if self.is_active and event.type == KEYDOWN:
            if event.key == self.key:
                for fun in self.functions:
                    fun()
