from pygame import MOUSEMOTION, MOUSEBUTTONUP
from pygame import Rect, Surface

from Consts import GREY, BLACK, WHITE
from UI.MenuObjects.MenuObjectWithText import MenuObjectWithText


class Button(MenuObjectWithText):

    text_str: str = None
    color: tuple = None
    selected_color: tuple = None
    text_color: tuple = None
    selected_text_color: tuple = None

    function_onHover = None  # Функция, выполняемая при наведении курсором на кнопку
    arg_onHover: str = None  # Аргумент для этой функции

    is_active = None  # Активна ли сейчас кнопка (можно ли на неё нажать)
    is_selected = None  # Выбрана ли сейчас кнопка
    is_transparent = None  # Прозрачность фона для кнопки

    def __init__(self, window_surface: Surface, pos: tuple = None, text: str = None, active: bool = None,
                 color: tuple = None, selected_color: tuple = None, text_color: tuple = None, transparent: bool = None,
                 selected_text_color: tuple = None, function_onClick=None, font_size: int = None, font: str = None,
                 function_onClick_list: list = None, function_onHover=None, args_list: list = None, arg_onHover=None,
                 auto_adjust: bool = True):
        self.window_surface = window_surface
        self.rect = Rect(0, 0, 100, 50)  # Стандартные размер и положение кнопки

        if pos is not None:
            self.set_pos(pos[0], pos[1], pos[2], pos[3])

        if text is not None:
            self.set_text(text)
        else:
            self.set_text("Button")  # Стандартный текст кнопки

        if active is not None:
            self.set_active(active)
        else:
            self.is_active = True  # Стандартная кнопка активна

        if color is not None:
            self.set_color(color)
        else:
            self.set_color(GREY)  # Стандартный цвет кнопки

        if selected_color is not None:
            self.set_selected_color(selected_color)
        else:
            self.set_selected_color(WHITE)  # Стандартный цвет выбранной кнопки

        if text_color is not None:
            self.set_text_color(text_color)
        else:
            self.set_text_color(BLACK)  # Стандартный цвет текста кнопки

        if selected_text_color is not None:
            self.set_selected_text_color(selected_text_color)

        if function_onClick is not None:
            self.add_function_onClick(function_onClick)
        elif function_onClick_list is not None:
            if args_list is not None and function_onClick_list.__len__() != args_list.__len__():
                raise ValueError("Список аргументов не равен по размеру со списком функций!")
            for (i, fun) in enumerate(function_onClick_list):
                if args_list is not None:
                    self.add_function_onClick(fun, args_list[i])
                else:
                    self.add_function_onClick(fun)
        else:
            self.add_function_onClick(lambda: print(self.text_str))

        if font_size is not None:
            self.set_font_size(font_size)
        else:
            self.set_font_size(16)

        if transparent is not None:
            self.is_transparent = transparent
        else:
            self.is_transparent = False

        if function_onHover is not None:
            if arg_onHover is not None:
                self.arg_onHover = arg_onHover
            self.function_onHover = function_onHover

        # Работа с текстом:
        self.set_font(self.font_size, font)
        self.render_text(self.text_str, self.text_color)
        if auto_adjust:
            self.adjust_size()

    def set_text(self, text: str):
        self.text_str = text
        self.has_text_changed = True

    def set_active(self, active: bool):
        self.is_active = active

    def set_color(self, color: tuple):
        self.color = color

    def set_selected_color(self, selected_color: tuple):
        self.selected_color = selected_color

    def set_text_color(self, text_color: tuple):
        self.text_color = text_color
        self.has_text_changed = True

    def set_selected_text_color(self, selected_text_color):
        self.selected_text_color = selected_text_color
        self.has_text_changed = True

    def handle_event(self, event):
        """
        Обработка события кнопкой.
        """
        if self.is_active:
            if event.type == MOUSEMOTION:
                if self.rect.collidepoint(event.pos[0], event.pos[1]):
                    if self.function_onHover is not None and not self.is_selected:
                        if self.arg_onHover is not None:
                            self.function_onHover(self.arg_onHover)
                        else:
                            self.function_onHover()
                    self.is_selected = True
                    if self.selected_text_color is not None:
                        self.has_text_changed = True
                        self.update()
                else:
                    self.is_selected = False
                    if self.selected_text_color is not None:
                        self.has_text_changed = True
                        self.update()

            if self.is_selected and event.type == MOUSEBUTTONUP:
                if self.rect.collidepoint(event.pos[0], event.pos[1]):
                    for (i, fun) in enumerate(self.function_onClick):
                        if (arg := self.function_args[i]) is not None:
                            fun(arg)
                        else:
                            fun()

    def update(self):
        """
        Проверка на изменение текста. Происходит каждый такт игры.
        """
        if self.has_text_changed:
            if self.is_selected and self.selected_text_color is not None:
                self.render_text(self.text_str, self.selected_text_color)
            else:
                self.render_text(self.text_str, self.text_color)

    def draw(self):
        """
        Отрисовка кнопки. Происходит каждый такт игры.
        """
        if not self.is_transparent:
            if self.is_active:
                # Если кнопка активна:
                if self.is_selected:
                    # Если кнопка выделена
                    self.window_surface.fill(self.selected_color, self.rect)
                else:
                    # Если кнопка не выделена
                    self.window_surface.fill(self.color, self.rect)
            else:
                # Если кнопка не активна
                darker_color = (max(self.color[0] - 55, 0), max(self.color[1] - 55, 0), max(self.color[2] - 55, 0))
                self.window_surface.fill(darker_color, self.rect)
        self.window_surface.blit(self.text_surf,
                                 (self.rect.x + (self.rect.w / 2) - (self.text_size[0] / 2),
                                  self.rect.y + (self.rect.h / 2) - (self.text_size[1] / 2)))
