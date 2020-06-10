from pygame.constants import KEYDOWN

from UI.MenuObjects.MenuObjectClickable import MenuObjectClickable


class ButtonTrigger(MenuObjectClickable):
    """
    Невидимый объект, который выполняет какое-либо действие по нажатию определённой клавиши.
    """

    key = None  # Кнопка, на которую необходимо нажать

    is_active: bool = None  # Активен ли триггер

    def __init__(self, key, function=None, function_list: list = None,
                 active: bool = None, args_list: list = None):
        self.key = key
        if function is not None:
            self.add_function_onClick(function)
        elif function_list is not None:
            if args_list is not None and function_list.__len__() != args_list.__len__():
                raise ValueError("Список аргументов не равен по размеру со списком функций!")
            for (i, fun) in enumerate(function_list):
                if args_list is not None:
                    self.add_function_onClick(fun, args_list[i])
                else:
                    self.add_function_onClick(fun)
        else:
            raise ValueError("ButtonTrigger не имеет функции для выполнения!")

        if active is not None:
            self.set_active(active)
        else:
            self.set_active(True)

    def set_active(self, active: bool):
        self.is_active = active

    def handle_event(self, event):
        if self.is_active and event.type == KEYDOWN:
            if event.key == self.key:
                for (i, fun) in enumerate(self.function_onClick):
                    if (arg := self.function_args[i]) is not None:
                        fun(arg)
                    else:
                        fun()
