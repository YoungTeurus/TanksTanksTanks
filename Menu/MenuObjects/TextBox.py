from pygame.constants import MOUSEBUTTONUP, KEYDOWN, K_RETURN, K_BACKSPACE
from pygame.font import Font
from pygame.rect import Rect
from pygame.surface import Surface

from Consts import BLACK, WHITE, DARK_GREY
from Files import get_script_dir
from Menu.MenuObjects.MenuObjectWithText import MenuObjectWithText, fonts

VERY_LIGHT_GREY = (210, 210, 210)
LIGHT_GREY = (160, 160, 160)


class TextBox(MenuObjectWithText):
    window_surface: Surface = None  # Поверхность окна

    text_str: str = None  # Строка, которую хранит TextBox
    empty_text_str: str = None  # Строка, которую хранит TextBox, пока в него ничего не введено

    function_onEnter = None  # Функция, выполняемая при нажатии Enter-а
    arg_onEnter: str = None

    is_active = None  # Активен ли сейчас кнопка (можно ли на него нажать)
    is_selected = None  # Выбран ли сейчас TextBox

    def __init__(self, window_surface: Surface, pos: tuple = None, start_text: str = None,
                 empty_text: str = None, active: bool = None, selected: bool = None,
                 function_onEnter=None, arg_onEnter: str = None, font_size: int = None, font: str = None):
        self.window_surface = window_surface

        self.rect = Rect(0, 0, 100, 50)  # Стандартные размер и положение TextBox
        if pos is not None:
            self.set_pos(pos[0], pos[1], pos[2], pos[3])

        if start_text is not None:
            self.set_text(start_text)
        else:
            self.set_text("")  # Стандартный текст TextBox - пустой

        if empty_text is not None:
            self.empty_text_str = empty_text
        else:
            self.empty_text_str = ""  # Текст подсказки пустой по умолчанию

        if selected is not None:
            self.set_selected(selected)
        else:
            self.is_selected = False

        if active is not None:
            self.set_active(active)
        else:
            self.is_active = True  # Стандартная кнопка активна

        if function_onEnter is not None:
            self.set_function_onEnter(function_onEnter)
        else:
            self.set_function_onEnter(lambda: print(self.text_str))

        if font_size is not None:
            self.set_font_size(font_size)
        else:
            self.set_font_size(16)

        if arg_onEnter is not None:
            self.arg_onEnter = arg_onEnter

        # Работа с текстом:
        if font is not None and font in fonts:
            path = get_script_dir() + fonts[font]
            self.font = Font(path, self.font_size)
        else:
            self.font = Font(None, self.font_size)
        self.textbox_render_text()

    def set_active(self, active: bool):
        self.is_active = active

    def set_selected(self, selected: bool):
        self.is_selected = selected
        self.has_text_changed = True

    def set_text(self, text: str):
        self.text_str = text
        self.has_text_changed = True

    def textbox_render_text(self):
        if self.text_str.__len__() > 0 or self.is_selected:
            # Если что-то напечатано или поле выбрано:
            super().render_text(self.text_str, BLACK)
        else:
            # Если поле пустое и не выбрано
            super().render_text(self.empty_text_str, DARK_GREY)

    def set_function_onEnter(self, function):
        self.function_onEnter = function

    def draw(self):
        if self.is_active:
            # Если активен:
            if self.is_selected:
                # Если выделен
                self.window_surface.fill(WHITE, self.rect)
            else:
                # Если не выделен
                self.window_surface.fill(VERY_LIGHT_GREY, self.rect)
        else:
            # Если не активен
            self.window_surface.fill(LIGHT_GREY, self.rect)
        self.window_surface.blit(self.text_surf,
                                 (self.rect.x,
                                  self.rect.y + (self.rect.h / 2) - (self.text_size[1] / 2)))

    def handle_event(self, event):
        if self.is_active:
            if event.type == MOUSEBUTTONUP:
                if self.rect.collidepoint(event.pos[0], event.pos[1]):
                    self.set_selected(True)
                else:
                    self.set_selected(False)
            if self.is_selected and event.type == KEYDOWN:
                if event.key == K_RETURN:
                    if self.arg_onEnter is not None:
                        self.function_onEnter(self.arg_onEnter)
                    else:
                        self.function_onEnter()
                elif event.key == K_BACKSPACE:
                    self.text_str = self.text_str[:-1]
                else:
                    self.text_str += event.unicode
                self.has_text_changed = True

    def update(self):
        if self.has_text_changed:
            self.textbox_render_text()
