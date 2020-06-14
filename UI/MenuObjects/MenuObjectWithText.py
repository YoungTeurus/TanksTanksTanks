from pygame.font import Font
from pygame.surface import Surface

from Files import get_script_dir
from UI.MenuObjects.MenuObjectClickable import MenuObjectClickable

fonts = {
    'main_menu': '\\assets\\fonts\\main_menu.ttf'
}

LEFT_ALIGNMENT = 1
ALIGNMENTS = [LEFT_ALIGNMENT]


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

    def adjust_size(self, dont_change_width=False):
        """
        Размеры кнопки всегда соответствуют размеру текста
        """
        if not dont_change_width:
            if (difference := self.text_size[0] - self.rect.width) != 0:  # Если ширина надписи больше кнопки
                self.rect.width = self.text_size[0]
                self.rect.x -= (difference / 2)
        if (difference := self.text_size[1] - self.rect.height) != 0:  # Если высота надписи больше кнопки
            self.rect.height = self.text_size[1]
            self.rect.y -= (difference / 2)

    def set_font_size(self, size: int):
        self.font_size = size
        self.has_text_changed = True

    def set_font(self, size: int, font: str = None):
        if font is not None and font in fonts:
            path = get_script_dir() + fonts[font]
            self.font = Font(path, size)
        else:
            self.font = Font(None, size)
