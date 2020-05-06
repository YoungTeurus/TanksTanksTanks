import pygame

from Consts import targetFPS, DARK_GREY
from Menu.MenuObjects.Button import Button
from Menu.MenuObjects.ButtonTrigger import ButtonTrigger
from Menu.MenuObjects.Label import Label
from Menu.MenuObjects.TextBox import TextBox


class Menu:
    is_running: bool = None  # Флаг запущенного меню

    objects = None  # Массив объектов меню

    result: dict = None  # Словарь, содержащий результат работы меню

    def __init__(self, window_surface):
        self.window_surface = window_surface  # Основная поверхность

        self.is_running = True

        self.clock = pygame.time.Clock()

        self.objects = []

        self.result = dict()

        self.load_title_group()

    def load_title_group(self):
        """
        Загружает элементы заглавного меню
        """
        self.objects.clear()

        button_start_solo = Button(self.window_surface, pos=(80, 50, 140, 50), text="Одиночная игра",
                                   color=(192, 60, 60),
                                   selected_color=(215, 120, 120), font_size=24, function=self.load_start_solo_group)
        button_start_multi = Button(self.window_surface, pos=(80, 110, 140, 50), text="Совместная игра",
                                    color=(60, 192, 60),
                                    selected_color=(120, 215, 120), font_size=24, function=self.load_start_multi_group)
        button_quit = Button(self.window_surface, pos=(100, 190, 100, 30), text="Выйти из игры", color=(60, 60, 192),
                             selected_color=(90, 90, 192), text_color=(230, 230, 230),
                             font_size=18)
        label_title = Label(self.window_surface, font_size=24, text="TANK! TANK! TANK!", pos=(150, 25, 0, 0))

        self.objects.append(button_start_solo)
        self.objects.append(button_start_multi)
        self.objects.append(button_quit)
        self.objects.append(label_title)

    def load_start_solo_group(self):
        """
        Загружает элементы подменю "Одиночная игра"
        """

        def start_solo_game():
            self.is_running = False
            self.result["result"] = "start"
            self.result["mode"] = "client"
            self.result["multi"] = False

        self.objects.clear()

        button_start_new = Button(self.window_surface, pos=(80, 50, 140, 50), text="Начать с начала",
                                  color=(192, 60, 60),
                                  selected_color=(215, 120, 120), font_size=24, function=start_solo_game)
        label_menu_name = Label(self.window_surface, pos=(150, 25, 0, 0), text="Одиночная игра", font_size=28)
        button_trigger_esc = ButtonTrigger(key=pygame.K_ESCAPE, function=self.load_title_group)
        label_esc = Label(self.window_surface, pos=(150, 200, 0, 0), text="Нажмите ESC, чтобы вернуться в главное меню",
                          font_size=14)

        self.objects.append(button_start_new)
        self.objects.append(label_menu_name)
        self.objects.append(button_trigger_esc)
        self.objects.append(label_esc)

    def load_start_multi_group(self):
        """
        Загружает элементы подменю "Совместная игра"
        """
        self.objects.clear()

        button_trigger_esc = ButtonTrigger(key=pygame.K_ESCAPE, function=self.load_title_group)

        self.objects.append(button_trigger_esc)

    def main_cycle(self):
        while self.is_running:
            self.clock.tick(targetFPS)  # Требуемый FPS и соответствующая задержка
            self.window_surface.fill(DARK_GREY)

            # Обработка событий:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                for obj in self.objects:
                    obj.handle_event(event)
            keyboard_pressed = pygame.key.get_pressed()

            for obj in self.objects:
                obj.update()
                obj.draw()

            pygame.display.update()

        return self.result
