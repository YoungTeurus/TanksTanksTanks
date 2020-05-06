from pygame.constants import KEYDOWN

from Menu.MenuObjects.MenuObject import MenuObject


class ButtonTrigger(MenuObject):
    """
    Невидимый объект, который выполняет какое-либо действие по нажатию определённой клавиши.
    """

    key = None  # Кнопка, на которую необходимо нажать
    function = None  # Действие по нажатию кнопки

    is_active: bool = None  # Активен ли триггер

    def __init__(self, key, function, active: bool = None):
        self.key = key
        self.function = function

        if active is not None:
            self.set_active(active)
        else:
            self.set_active(True)

    def set_active(self, active: bool):
        self.is_active = active

    def handle_event(self, event):
        if self.is_active and event.type == KEYDOWN:
            if event.key == self.key:
                self.function()
