import re

import pygame

from Consts import targetFPS, DARK_GREY, SOUNDS_VOLUME, MAPS
from Files import get_script_dir
from Menu.MenuObjects.Button import Button
from Menu.MenuObjects.ButtonTrigger import ButtonTrigger
from Menu.MenuObjects.Label import Label
from Menu.MenuObjects.TextBox import TextBox


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

        self.sounds['select'].set_volume(SOUNDS_VOLUME)
        self.sounds['press'].set_volume(SOUNDS_VOLUME)

        self.load_title_group()

    def play_sound(self, sound: str):
        if sound in self.sounds:
            self.sounds[sound].play()

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
                                   function_onClick_list=[self.play_sound, self.load_start_solo_group],
                                   args_list=["press", None],
                                   function_onHover=self.play_sound, arg_onHover="select")
        label_start_solo_shadow = Label(self.window_surface, pos=(82, 52, 140, 30), text="Одиночная игра",
                                        text_color=(0, 0, 0), font_size=24, font="main_menu")
        button_start_multi = Button(self.window_surface, pos=(80, 90, 140, 30), text="Совместная игра",
                                    transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                    font_size=24, font="main_menu",
                                    function_onClick_list=[self.play_sound, self.load_start_multi_group],
                                    args_list=["press", None],
                                    function_onHover=self.play_sound, arg_onHover="select")
        label_start_milti_shadow = Label(self.window_surface, pos=(82, 92, 140, 30), text="Совместная игра",
                                         text_color=(0, 0, 0), font_size=24, font="main_menu")
        button_quit = Button(self.window_surface, pos=(90, 190, 120, 30), text="Выйти из игры",
                             transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                             font_size=24, font="main_menu",
                             function_onClick_list=[self.play_sound, quit_game],
                             args_list=["press", None],
                             function_onHover=self.play_sound, arg_onHover="select")
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

    def start_solo_game(self):
        self.is_running = False
        self.result["result"] = "start"
        self.result["mode"] = "client"
        self.result["multi"] = False
        if "map_id" not in self.result:
            self.result["map_id"] = 0

    def load_start_solo_group(self):
        """
        Загружает элементы подменю "Одиночная игра"
        """

        self.objects.clear()

        button_start_new = Button(self.window_surface, pos=(80, 50, 140, 30), text="Начать новую",
                                  transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                  font_size=24, font="main_menu",
                                  function_onClick_list=[self.play_sound, self.start_solo_game],
                                  args_list=["press", None],
                                  function_onHover=self.play_sound, arg_onHover="select")
        label_start_new_shadow = Label(self.window_surface, pos=(82, 52, 140, 30), text="Начать новую",
                                       text_color=(0, 0, 0), font_size=24, font="main_menu")
        button_select_level = Button(self.window_surface, pos=(80, 90, 140, 30), text="Выбрать уровень",
                                     transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                     font_size=24, font="main_menu",
                                     function_onClick_list=[self.play_sound, self.load_select_level_group],
                                     args_list=["press", None],
                                     function_onHover=self.play_sound, arg_onHover="select")
        label_select_level_shadow = Label(self.window_surface, pos=(82, 92, 140, 30), text="Выбрать уровень",
                                          text_color=(0, 0, 0), font_size=24, font="main_menu")
        label_menu_name = Label(self.window_surface, pos=(150, 25, 0, 0), text="ОДИНОЧНАЯ ИГРА",
                                text_color=(240, 240, 240), font_size=28, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface, pos=(152, 27, 0, 0), text="ОДИНОЧНАЯ ИГРА",
                                       text_color=(0, 0, 0), font_size=28, font="main_menu")
        button_trigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                           function_list=[self.play_sound, self.load_title_group],
                                           args_list=["press", None], )
        button_return = Button(self.window_surface, pos=(0, 200, 140, 30), text="Назад",
                               transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                               font_size=24, font="main_menu",
                               function_onClick_list=[self.play_sound, self.load_title_group],
                               args_list=["press", None],
                               function_onHover=self.play_sound, arg_onHover="select")
        label_return_shadow = Label(self.window_surface, pos=(2, 202, 140, 30), text="Назад",
                                    text_color=(0, 0, 0), font_size=24, font="main_menu")

        self.objects.append(label_start_new_shadow)
        self.objects.append(button_start_new)
        self.objects.append(label_select_level_shadow)
        self.objects.append(button_select_level)
        self.objects.append(label_return_shadow)
        self.objects.append(button_return)
        self.objects.append(label_menu_name_shadow)
        self.objects.append(label_menu_name)
        self.objects.append(button_trigger_esc)

    def load_select_level_group(self):
        """
        Загружает элементы подменю "Выбор уровня"
        """

        def set_result_level(map_id: int):
            self.result["map_id"] = map_id
            self.start_solo_game()

        self.objects.clear()

        label_menu_name = Label(self.window_surface, pos=(150, 25, 0, 0), text="ВЫБРАТЬ УРОВЕНЬ",
                                text_color=(240, 240, 240), font_size=28, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface, pos=(152, 27, 0, 0), text="ВЫБРАТЬ УРОВЕНЬ",
                                       text_color=(0, 0, 0), font_size=28, font="main_menu")
        button_trigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                           function_list=[self.play_sound, self.load_start_solo_group],
                                           args_list=["press", None], )
        button_return = Button(self.window_surface, pos=(0, 200, 140, 30), text="Назад",
                               transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                               font_size=24, font="main_menu",
                               function_onClick_list=[self.play_sound, self.load_start_solo_group],
                               args_list=["press", None],
                               function_onHover=self.play_sound, arg_onHover="select")
        label_return_shadow = Label(self.window_surface, pos=(2, 202, 140, 30), text="Назад",
                                    text_color=(0, 0, 0), font_size=24, font="main_menu")
        for (i, map_tuple) in enumerate(get_all_maps_names()):
            x = 80
            y = 50 + i * 40
            button_map_name = Button(self.window_surface, pos=(x, y, 140, 30), text=map_tuple[1],
                                     transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                     font_size=24, font="main_menu",
                                     function_onClick_list=[self.play_sound, set_result_level],
                                     args_list=["press", map_tuple[0]],
                                     function_onHover=self.play_sound, arg_onHover="select")
            label_map_name_shadow = Label(self.window_surface, pos=(x + 2, y + 2, 140, 30), text=map_tuple[1],
                                          text_color=(0, 0, 0), font_size=24, font="main_menu")

            self.objects.append(label_map_name_shadow)
            self.objects.append(button_map_name)

        self.objects.append(label_return_shadow)
        self.objects.append(button_return)
        self.objects.append(label_menu_name_shadow)
        self.objects.append(label_menu_name)
        self.objects.append(button_trigger_esc)

    def start_multi_game_client(self):
        self.is_running = False
        self.result["result"] = "start"
        self.result["mode"] = "client"
        self.result["multi"] = True

    def load_start_multi_group(self):
        """
        Загружает элементы подменю "Совместная игра"
        """

        def do_nothing():
            pass

        self.objects.clear()

        button_connect_to = Button(self.window_surface, pos=(80, 50, 140, 30), text="Подключиться к серверу",
                                   transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                   font_size=24, font="main_menu",
                                   function_onClick_list=[self.play_sound, do_nothing],
                                   args_list=["press", None],
                                   function_onHover=self.play_sound, arg_onHover="select",
                                   active=False)
        label_connect_to_shadow = Label(self.window_surface, pos=(82, 52, 140, 30), text="Подключиться к серверу",
                                        text_color=(0, 0, 0), font_size=24, font="main_menu")
        button_create_server = Button(self.window_surface, pos=(80, 90, 140, 30), text="Создать сервер",
                                      transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                      font_size=24, font="main_menu",
                                      function_onClick_list=[self.play_sound, do_nothing],
                                      args_list=["press", None],
                                      function_onHover=self.play_sound, arg_onHover="select",
                                      active=False)
        label_create_server_shadow = Label(self.window_surface, pos=(82, 92, 140, 30), text="Создать сервер",
                                           text_color=(0, 0, 0), font_size=24, font="main_menu")
        button_direct_connect = Button(self.window_surface, pos=(80, 130, 140, 30), text="Прямое подключение",
                                       transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                       font_size=24, font="main_menu",
                                       function_onClick_list=[self.play_sound, self.load_direct_connect_group],
                                       args_list=["press", None],
                                       function_onHover=self.play_sound, arg_onHover="select")
        label_direct_connect_shadow = Label(self.window_surface, pos=(82, 132, 140, 30), text="Прямое подключение",
                                            text_color=(0, 0, 0), font_size=24, font="main_menu")

        button_trigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                           function_list=[self.play_sound, self.load_title_group],
                                           args_list=["press", None], )
        button_return = Button(self.window_surface, pos=(0, 200, 140, 30), text="Назад",
                               transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                               font_size=24, font="main_menu",
                               function_onClick_list=[self.play_sound, self.load_title_group],
                               args_list=["press", None],
                               function_onHover=self.play_sound, arg_onHover="select")
        label_return_shadow = Label(self.window_surface, pos=(2, 202, 140, 30), text="Назад",
                                    text_color=(0, 0, 0), font_size=24, font="main_menu")
        label_menu_name = Label(self.window_surface, pos=(150, 25, 0, 0), text="СОВМЕСТНАЯ ИГРА",
                                text_color=(240, 240, 240), font_size=28, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface, pos=(152, 27, 0, 0), text="СОВМЕСТНАЯ ИГРА",
                                       text_color=(0, 0, 0), font_size=28, font="main_menu")

        self.objects.append(label_create_server_shadow)
        self.objects.append(button_create_server)
        self.objects.append(label_direct_connect_shadow)
        self.objects.append(button_direct_connect)
        self.objects.append(label_connect_to_shadow)
        self.objects.append(button_connect_to)
        self.objects.append(button_trigger_esc)
        self.objects.append(label_return_shadow)
        self.objects.append(button_return)
        self.objects.append(label_menu_name_shadow)
        self.objects.append(label_menu_name)

    def load_direct_connect_group(self):
        """
        Загружает элементы подменю "Прямое подключение"
        """

        regex_str = r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
        regex = re.compile(regex_str)

        was_error = False  # Была ли уже допущена ошибка при вводе IP?

        def connect_to():
            if regex.match(textbox_server_ip.text_str):
                label_wrong_ip.set_text("")
                label_wrong_ip_shadow.set_text("")
                self.result["server_ip"] = textbox_server_ip.text_str
                self.start_multi_game_client()
            else:
                label_wrong_ip.set_text("Неправильный формат IP адреса!")
                label_wrong_ip_shadow.set_text("Неправильный формат IP адреса!")

        self.objects.clear()

        label_wrong_ip = Label(self.window_surface, pos=(80, 120, 140, 30),
                               text="",
                               text_color=(224, 24, 24), font_size=14, font="main_menu")
        label_wrong_ip_shadow = Label(self.window_surface, pos=(81, 121, 140, 30),
                                      text="",
                                      text_color=(0, 0, 0), font_size=14, font="main_menu")
        self.objects.append(label_wrong_ip_shadow)
        self.objects.append(label_wrong_ip)

        label_server_ip = Label(self.window_surface, pos=(80, 50, 140, 30), text="IP сервера:",
                                text_color=(224, 154, 24), font_size=24, font="main_menu")
        label_server_ip_shadow = Label(self.window_surface, pos=(82, 52, 140, 30), text="IP сервера:",
                                       text_color=(0, 0, 0), font_size=24, font="main_menu")
        textbox_server_ip = TextBox(self.window_surface, pos=(80, 90, 140, 30), font="main_menu",
                                    function_onEnter=connect_to)
        button_connect = Button(self.window_surface, pos=(80, 155, 140, 30), text="Подключиться",
                                transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                font_size=24, font="main_menu",
                                function_onClick_list=[self.play_sound, connect_to],
                                args_list=["press", None],
                                function_onHover=self.play_sound, arg_onHover="select")
        label_connect_shadow = Label(self.window_surface, pos=(82, 157, 140, 30), text="Подключиться",
                                     text_color=(0, 0, 0), font_size=24, font="main_menu")

        button_trigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                           function_list=[self.play_sound, self.load_start_multi_group],
                                           args_list=["press", None], )
        button_return = Button(self.window_surface, pos=(0, 200, 140, 30), text="Назад",
                               transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                               font_size=24, font="main_menu",
                               function_onClick_list=[self.play_sound, self.load_start_multi_group],
                               args_list=["press", None],
                               function_onHover=self.play_sound, arg_onHover="select")
        label_return_shadow = Label(self.window_surface, pos=(2, 202, 140, 30), text="Назад",
                                    text_color=(0, 0, 0), font_size=24, font="main_menu")
        label_menu_name = Label(self.window_surface, pos=(150, 25, 0, 0), text="ПРЯМОЕ ПОДКЛЮЧЕНИЕ",
                                text_color=(240, 240, 240), font_size=28, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface, pos=(152, 27, 0, 0), text="ПРЯМОЕ ПОДКЛЮЧЕНИЕ",
                                       text_color=(0, 0, 0), font_size=28, font="main_menu")

        self.objects.append(label_connect_shadow)
        self.objects.append(button_connect)
        self.objects.append(textbox_server_ip)
        self.objects.append(label_server_ip_shadow)
        self.objects.append(label_server_ip)
        self.objects.append(button_trigger_esc)
        self.objects.append(label_return_shadow)
        self.objects.append(button_return)
        self.objects.append(label_menu_name_shadow)
        self.objects.append(label_menu_name)

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


def get_all_maps_names():
    """
    Возвращает список названий карт.
    """
    return_tuple = []
    script_dir = get_script_dir()
    # files = listdir(script_dir + "\\assets\\maps")
    for (i, map_id) in enumerate(MAPS):
        filename = script_dir + MAPS[map_id]
        try:
            with open(filename, "r", encoding='utf-8') as f:
                has_read_title = False
                while (current_line := f.readline()).__len__() > 0:
                    if current_line[0] == "#":
                        mini_dict = current_line[1:-1].split("=")
                        if mini_dict[0] == "title":
                            return_tuple.append((map_id, mini_dict[1]))
                            has_read_title = True
                if not has_read_title:
                    return_tuple.append((map_id, "Map {}".format(i)))
        except FileNotFoundError:
            print("There was an attempt to open a file but it does not exist: {}".format(filename))
    return return_tuple
