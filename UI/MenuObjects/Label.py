from pygame.constants import MOUSEBUTTONUP
from pygame.font import Font
from pygame.rect import Rect
from pygame.surface import Surface

from Consts import BLACK
from UI.MenuObjects.MenuObjectWithText import MenuObjectWithText

CLICKED_LINK_COLOR = (128, 0, 128)


class Label(MenuObjectWithText):

    text_str: str = None
    text_color: tuple = None
    is_text_underlined: bool = None  # Подчёркнут ли текст

    font: Font = None  # Шрифт, используемый для отрисовки текста
    font_size: int = None  # Размер шрифта
    text_surf: Surface = None  # Отрисовываемый текст
    text_size: tuple = None  # Размер места, занимаемого текстом

    has_text_changed = None  # Изменился ли текст, чтобы его нужно было вновь render-ить?

    def __init__(self, window_surface: Surface, pos: tuple = None, text: str = None,
                 text_color: tuple = None, function=None, font_size: int = None, font: str = None):
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
            self.add_function_onClick(function)
            self.is_text_underlined = True
        else:
            self.is_text_underlined = False

        if font_size is not None:
            self.set_font_size(font_size)
        else:
            self.set_font_size(16)

        # Работа с текстом:
        self.set_font(self.font_size, font)  # Стандартный шрифт
        self.label_render_text()

    def set_text(self, text: str):
        if self.text_str is None or text != self.text_str:
            self.text_str = text
            self.has_text_changed = True

    def set_text_color(self, text_color: tuple):
        self.text_color = text_color
        self.has_text_changed = True

    def label_render_text(self):
        self.font.set_underline(self.is_text_underlined)
        super().render_text(self.text_str, self.text_color)

    def handle_event(self, event):
        """
        Обработка события кнопкой.
        """
        if event.type == MOUSEBUTTONUP:
            if self.function_onClick is not None and self.rect.collidepoint(event.pos[0], event.pos[1]):
                for fun in self.function_onClick:
                    fun()
                self.set_text_color(CLICKED_LINK_COLOR)

    def draw(self):
        self.window_surface.blit(self.text_surf,
                                 (self.rect.x + (self.rect.w / 2) - (self.text_size[0] / 2),
                                  self.rect.y + (self.rect.h / 2) - (self.text_size[1] / 2)))

    def update(self):
        """
        Проверка на изменение текста. Происходит каждый такт игры.
        """
        if self.has_text_changed:
            self.label_render_text()
