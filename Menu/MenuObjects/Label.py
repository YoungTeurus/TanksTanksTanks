from pygame.font import Font
from pygame.rect import Rect
from pygame.surface import Surface

from Consts import BLACK
from Menu.MenuObjects.MenuObject import MenuObject


class Label(MenuObject):
    window_surface: Surface = None  # Поверхность окна

    rect: Rect = None
    text_str: str = None
    text_color: tuple = None
    is_text_underlined: bool = None  # Подчёркнут ли текст

    function = None  # Функция, выполняемая при нажатии
    font: Font = None  # Шрифт, используемый для отрисовки текста
    font_size: int = None  # Размер шрифта
    text_surf: Surface = None  # Отрисовываемый текст
    text_size: tuple = None  # Размер места, занимаемого текстом

    has_text_changed = None  # Изменился ли текст, чтобы его нужно было вновь render-ить?

    def __init__(self, window_surface: Surface, pos: tuple = None, text: str = None,
                 text_color: tuple = None, function=None, font_size: int = None):
        self.window_surface = window_surface
        self.rect = Rect(0, 0, 100, 50)  # Стандартные размер и положение кнопки
        if pos is not None:
            self.set_pos(pos[0], pos[1], pos[2], pos[3])

        if text is not None:
            self.set_text(text)
        else:
            self.set_text("Label")  # Стандартный текст кнопки

        if text_color is not None:
            self.set_text_color(text_color)
        else:
            self.set_text_color(BLACK)  # Стандартный цвет текста кнопки

        if function is not None:
            self.set_function(function)
        else:
            self.is_text_underlined = False

        if font_size is not None:
            self.set_font_size(font_size)
        else:
            self.set_font_size(16)

        # Работа с текстом:
        self.font = Font(None, self.font_size)  # Стандартный шрифт
        self.render_text()

    # Функции ниже дублируется в Button.py !
    def set_pos(self, pos_x, pos_y, width, height):
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.rect.width = width
        self.rect.height = height

    def set_text(self, text: str):
        self.text_str = text
        self.has_text_changed = True

    def set_text_color(self, text_color: tuple):
        self.text_color = text_color

    def set_function(self, function):
        self.function = function

    def render_text(self):
        self.text_surf = self.font.render(self.text_str, 1, self.text_color)
        self.text_size = self.font.size(self.text_str)
        self.has_text_changed = False

    def set_font_size(self, size: int):
        self.font_size = size
        self.has_text_changed = True
    # Функции выше дублируется в Button.py !

    def draw(self):
        self.window_surface.blit(self.text_surf,
                                 (self.rect.x + (self.rect.w / 2) - (self.text_size[0] / 2),
                                  self.rect.y + (self.rect.h / 2) - (self.text_size[1] / 2)))

    def update(self):
        """
        Проверка на изменение текста. Происходит каждый такт игры.
        """
        if self.has_text_changed:
            self.render_text()
