import pygame

from Consts import targetFPS, DARK_GREY
from Files import get_script_dir
from Menu.MenuObjects.Button import Button
from Menu.MenuObjects.ButtonTrigger import ButtonTrigger
from Menu.MenuObjects.Label import Label


class Menu:
    is_running: bool = None  # Флаг запущенного меню

    objects = None  # Массив объектов меню

    result: dict = None  # Словарь, содержащий результат работы меню

    sounds: dict = None

    def __init__(self, window_surface):
        self.window_surface = window_surface  # Основная поверхность

        self.is_running = True

        self.clock = pygame.time.Clock()

        self.objects = []

        self.result = dict()
        self.result["result"] = None

        self.sounds = dict()
        self.sounds['select'] = pygame.mixer.Sound(get_script_dir() + '\\assets\\sounds\\Select.wav')
        self.sounds['press'] = pygame.mixer.Sound(get_script_dir() + '\\assets\\sounds\\Press.wav')

        self.load_title_group()

    def play_sound(self, sound: str):
        if sound in self.sounds:
            self.sounds[sound].play()

    def play_select_sound(self):
        self.play_sound('select')

    def play_press_sound(self):
        self.play_sound('press')

    def load_title_group(self):
        """
        Загружает элементы заглавного меню
        """

        def quit_game():
            self.is_running = False
            self.result["result"] = "quit"

        self.objects.clear()

        button_start_solo = Button(self.window_surface, pos=(80, 50, 140, 30), text="Одиночная игра",
                                   transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                   font_size=24, font="main_menu",
                                   function_onClick_list=[self.play_press_sound, self.load_start_solo_group],
                                   function_onHover=self.play_select_sound)
        label_start_solo_shadow = Label(self.window_surface, pos=(82, 52, 140, 30), text="Одиночная игра",
                                        text_color=(0, 0, 0), font_size=24, font="main_menu")
        button_start_multi = Button(self.window_surface, pos=(80, 90, 140, 30), text="Совместная игра",
                                    transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                    font_size=24, font="main_menu",
                                    function_onClick_list=[self.play_press_sound, self.load_start_multi_group],
                                    function_onHover=self.play_select_sound)
        label_start_milti_shadow = Label(self.window_surface, pos=(82, 92, 140, 30), text="Совместная игра",
                                         text_color=(0, 0, 0), font_size=24, font="main_menu")
        button_quit = Button(self.window_surface, pos=(90, 190, 120, 30), text="Выйти из игры",
                             transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                             font_size=24, font="main_menu",
                             function_onClick_list=[self.play_press_sound, quit_game],
                             function_onHover=self.play_select_sound)
        label_quit_shadow = Label(self.window_surface, pos=(92, 192, 120, 30), text="Выйти из игры",
                                  text_color=(0, 0, 0), font_size=24, font="main_menu")
        label_title = Label(self.window_surface, pos=(150, 25, 0, 0), text="TANK! TANK! TANK!",
                            text_color=(240, 240, 240), font_size=28, font="main_menu")
        label_title_shadow = Label(self.window_surface, pos=(152, 27, 0, 0), text="TANK! TANK! TANK!",
                                   text_color=(0, 0, 0), font_size=28, font="main_menu")

        self.objects.append(label_start_solo_shadow)
        self.objects.append(button_start_solo)
        self.objects.append(label_start_milti_shadow)
        self.objects.append(button_start_multi)
        self.objects.append(label_quit_shadow)
        self.objects.append(button_quit)
        self.objects.append(label_title_shadow)
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

        button_start_new = Button(self.window_surface, pos=(80, 50, 140, 30), text="Начать новую",
                                  transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                  font_size=24, font="main_menu",
                                  function_onClick_list=[self.play_press_sound, start_solo_game],
                                  function_onHover=self.play_select_sound)
        label_start_new_shadow = Label(self.window_surface, pos=(82, 52, 140, 30), text="Начать новую",
                                       text_color=(0, 0, 0), font_size=24, font="main_menu")
        label_menu_name = Label(self.window_surface, pos=(150, 25, 0, 0), text="ОДИНОЧНАЯ ИГРА",
                                text_color=(240, 240, 240), font_size=28, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface, pos=(152, 27, 0, 0), text="ОДИНОЧНАЯ ИГРА",
                                       text_color=(0, 0, 0), font_size=28, font="main_menu")
        button_trigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                           function_list=[self.play_press_sound, self.load_title_group])
        button_return = Button(self.window_surface, pos=(0, 200, 140, 30), text="Назад",
                               transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                               font_size=24, font="main_menu",
                               function_onClick_list=[self.play_press_sound, self.load_title_group],
                               function_onHover=self.play_select_sound)
        label_return_shadow = Label(self.window_surface, pos=(2, 202, 140, 30), text="Назад",
                                    text_color=(0, 0, 0), font_size=24, font="main_menu")

        self.objects.append(label_start_new_shadow)
        self.objects.append(button_start_new)
        self.objects.append(label_return_shadow)
        self.objects.append(button_return)
        self.objects.append(label_menu_name_shadow)
        self.objects.append(label_menu_name)
        self.objects.append(button_trigger_esc)

    def load_start_multi_group(self):
        """
        Загружает элементы подменю "Совместная игра"
        """
        self.objects.clear()

        button_trigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                           function_list=[self.play_press_sound, self.load_title_group])
        button_return = Button(self.window_surface, pos=(0, 200, 140, 30), text="Назад",
                               transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                               font_size=24, font="main_menu",
                               function_onClick_list=[self.play_press_sound, self.load_title_group],
                               function_onHover=self.play_select_sound)
        label_return_shadow = Label(self.window_surface, pos=(2, 202, 140, 30), text="Назад",
                                    text_color=(0, 0, 0), font_size=24, font="main_menu")

        self.objects.append(button_trigger_esc)
        self.objects.append(label_return_shadow)
        self.objects.append(button_return)

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
            # keyboard_pressed = pygame.key.get_pressed()

            for obj in self.objects:
                obj.update()
                obj.draw()

            pygame.display.update()

        return self.result
