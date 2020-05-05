from pygame import MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from pygame import Rect, Surface
from pygame.event import Event
from pygame.font import Font

from Consts import GREY, BLACK, WHITE, DARK_GREY
from Menu.MenuObjects.MenuObject import MenuObject


class Button(MenuObject):
    window_surface: Surface = None  # Поверхность окна

    rect: Rect = None
    text_str: str = None
    color: tuple = None
    selected_color: tuple = None
    text_color: tuple = None

    function = None  # Функция, выполняемая при нажатии
    font: Font = None  # Шрифт, используемый для отрисовки текста
    text_surf: Surface = None  # Отрисовываемый текст
    text_size: tuple = None  # Размер места, занимаемого текстом

    has_text_changed = None  # Изменился ли текст, чтобы его нужно было вновь render-ить?

    is_active = None  # Активна ли сейчас кнопка (можно ли на неё нажать)
    is_selected = None  # Выбрана ли сейчас кнопка

    def __init__(self, window_surface: Surface, pos: tuple = None, text: str = None, active: bool = None,
                 color: tuple = None,
                 selected_color: tuple = None, text_color: tuple = None, function=None):
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

        if function is not None:
            self.set_function(function)
        else:
            self.set_function(lambda: print(self.text_str))

        # Работа с текстом:
        self.font = Font(None, 16)  # Стандартный шрифт
        self.render_text()

    def set_pos(self, pos_x, pos_y, width, height):
        self.rect.x = pos_x
        self.rect.y = pos_y
        self.rect.width = width
        self.rect.height = height

    def set_text(self, text: str):
        self.text_str = text

    def set_active(self, active: bool):
        self.is_active = active

    def set_color(self, color: tuple):
        self.color = color

    def set_selected_color(self, selected_color: tuple):
        self.selected_color = selected_color

    def set_text_color(self, text_color: tuple):
        self.text_color = text_color

    def set_function(self, function):
        self.function = function

    def render_text(self):
        self.text_surf = self.font.render(self.text_str, 0, self.text_color)
        self.text_size = self.font.size(self.text_str)
        self.has_text_changed = False

    def handle_event(self, event):
        """
        Обработка события кнопкой.
        """
        if self.is_active:
            if event.type == MOUSEMOTION:
                if self.rect.collidepoint(event.pos):
                    self.is_selected = True
                else:
                    self.is_selected = False

            if event.type == MOUSEBUTTONUP:
                if self.rect.collidepoint(event.pos):
                    self.function()

    def draw(self):
        """
        Отрисовка кнопки. Происходит каждый такт игры.
        """
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
            darker_color = []
            darker_color.append(max(self.color[0] - 55, 0))
            darker_color.append(max(self.color[1] - 55, 0))
            darker_color.append(max(self.color[2] - 55, 0))
            self.window_surface.fill(darker_color, self.rect)
        self.window_surface.blit(self.text_surf,
                                 (self.rect.x + (self.rect.w / 2) - (self.text_size[0] / 2),
                                  self.rect.y + (self.rect.h / 2) - (self.text_size[1] / 2)))
