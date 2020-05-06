from pygame.font import Font
from pygame.surface import Surface

from Menu.MenuObjects.MenuObjectClickable import MenuObjectClickable


class MenuObjectWithText(MenuObjectClickable):
    font: Font = None  # Шрифт, используемый для отрисовки текста
    font_size: int = None  # Размер шрифта
    text_surf: Surface = None  # Отрисовываемый текст
    text_size: tuple = None  # Размер места, занимаемого текстом

    has_text_changed = None  # Изменился ли текст, чтобы его нужно было вновь render-ить?

    def render_text(self, text_str: str, text_color: tuple):
        self.text_surf = self.font.render(text_str, 1, text_color)
        self.text_size = self.font.size(text_str)
        self.has_text_changed = False

    def set_font_size(self, size: int):
        self.font_size = size
        self.has_text_changed = True
