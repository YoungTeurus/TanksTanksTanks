import re
import socket

import pygame

from Consts import targetFPS, DARK_GREY, SOUNDS_VOLUME, MAPS
from Files import get_script_dir
from Menu.MenuObjects.Button import Button
from Menu.MenuObjects.ButtonTrigger import ButtonTrigger
from Menu.MenuObjects.Label import Label
from Menu.MenuObjects.MenuObject import SKIP_EVENT
from Menu.MenuObjects.PopupBox import PopupBox
from Menu.MenuObjects.TextBox import TextBox


class Menu:
    is_running: bool = None  # Флаг запущенного меню

    objects = None  # Массив объектов меню

    result: dict = None  # Словарь, содержащий результат работы меню

    sounds: dict = None

    # TODO: придумать способ избавить от этого:
    any_popup: PopupBox = None  # Ужасный костыль. Если эта ссылка не None, значит данный объект должен первым получить

    # любой event и при этом отрисовываться последним.

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

        def add_popup():
            self.any_popup = popupbox_test

        def delete_popup():
            self.any_popup = None

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
        button_settings = Button(self.window_surface, pos=(80, 130, 140, 30), text="Настройки",
                                 transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                 font_size=24, font="main_menu",
                                 function_onClick_list=[self.play_sound, self.load_settings_group],
                                 args_list=["press", None],
                                 function_onHover=self.play_sound, arg_onHover="select")
        label_settings_shadow = Label(self.window_surface, pos=(82, 132, 140, 30), text="Настройки",
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

        button_test_popup = Button(self.window_surface, pos=(280, 50, 140, 30), text="Вызвать PopUp",
                                   transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                   font_size=24, font="main_menu",
                                   function_onClick_list=[self.play_sound, add_popup],
                                   args_list=["press", None],
                                   function_onHover=self.play_sound, arg_onHover="select")
        popupbox_test = PopupBox(self.window_surface, pos=(100, 100, 100, 150))
        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                          function_list=[self.play_sound, delete_popup],
                                          args_list=["press", None])
        popupbox_test.add_object(buttontrigger_esc)

        self.objects.append(button_test_popup)

        self.objects.append(label_start_solo_shadow)
        self.objects.append(button_start_solo)
        self.objects.append(label_start_milti_shadow)
        self.objects.append(button_start_multi)
        self.objects.append(label_settings_shadow)
        self.objects.append(button_settings)
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
        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                          function_list=[self.play_sound, self.load_title_group],
                                          args_list=["press", None])
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
        self.objects.append(buttontrigger_esc)

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
        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
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
        self.objects.append(buttontrigger_esc)

    def start_multi_game_client(self):
        self.is_running = False
        self.result["result"] = "start"
        self.result["mode"] = "client"
        self.result["multi"] = True
        if "client_ip" not in self.result:
            self.result["client_ip"] = socket.gethostbyname(socket.getfqdn())

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
                                      function_onClick_list=[self.play_sound, self.load_create_server_group],
                                      args_list=["press", None],
                                      function_onHover=self.play_sound, arg_onHover="select")
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

        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
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
        self.objects.append(buttontrigger_esc)
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

        def connect_to():
            if regex.match(textbox_server_ip.text_str):
                self.result["server_ip"] = textbox_server_ip.text_str
                self.start_multi_game_client()
            else:
                self.objects.append(label_wrong_ip_shadow)
                self.objects.append(label_wrong_ip)

        self.objects.clear()

        label_wrong_ip = Label(self.window_surface, pos=(80, 120, 140, 30),
                               text="Неправильный формат IP адреса!",
                               text_color=(224, 24, 24), font_size=14, font="main_menu")
        label_wrong_ip_shadow = Label(self.window_surface, pos=(81, 121, 140, 30),
                                      text="Неправильный формат IP адреса!",
                                      text_color=(0, 0, 0), font_size=14, font="main_menu")
        label_server_ip = Label(self.window_surface, pos=(80, 50, 140, 30), text="IP сервера:",
                                text_color=(224, 154, 24), font_size=24, font="main_menu")
        label_server_ip_shadow = Label(self.window_surface, pos=(82, 52, 140, 30), text="IP сервера:",
                                       text_color=(0, 0, 0), font_size=24, font="main_menu")
        textbox_server_ip = TextBox(self.window_surface, pos=(80, 90, 140, 30), font="main_menu",
                                    function_onEnter=connect_to, empty_text="IP адрес")
        button_connect = Button(self.window_surface, pos=(80, 155, 140, 30), text="Подключиться",
                                transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                font_size=24, font="main_menu",
                                function_onClick_list=[self.play_sound, connect_to],
                                args_list=["press", None],
                                function_onHover=self.play_sound, arg_onHover="select")
        label_connect_shadow = Label(self.window_surface, pos=(82, 157, 140, 30), text="Подключиться",
                                     text_color=(0, 0, 0), font_size=24, font="main_menu")

        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
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
        self.objects.append(buttontrigger_esc)
        self.objects.append(label_return_shadow)
        self.objects.append(button_return)
        self.objects.append(label_menu_name_shadow)
        self.objects.append(label_menu_name)

    def load_create_server_group(self):
        """
        Загружает элементы подменю "Создать сервер"
        """

        def start_multi_game_server():
            self.is_running = False
            self.result["result"] = "start"
            self.result["mode"] = "server"
            self.result["multi"] = True

        regex_str = r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
        regex = re.compile(regex_str)
        self.result["dedicated"] = True

        def create_server():
            if regex.match(textbox_server_ip.text_str):
                label_wrong_ip.set_text("")
                label_wrong_ip_shadow.set_text("")
                self.result["server_ip"] = textbox_server_ip.text_str
                start_multi_game_server()
            else:
                label_wrong_ip.set_text("Неправильный формат IP адреса!")
                label_wrong_ip_shadow.set_text("Неправильный формат IP адреса!")

        def change_dedicated():
            self.result["dedicated"] = not self.result["dedicated"]
            if self.result["dedicated"]:
                button_dedicated.set_text("Выделенный: да")
                label_dedicated_shadow.set_text("Выделенный: да")
            else:
                button_dedicated.set_text("Выделенный: нет")
                label_dedicated_shadow.set_text("Выделенный: нет")

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
                                    function_onEnter=create_server)
        button_dedicated = Button(self.window_surface, pos=(80, 135, 140, 30), text="Выделенный: да",
                                  transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                  font_size=18, font="main_menu",
                                  function_onClick_list=[self.play_sound, change_dedicated],
                                  args_list=["press", None],
                                  function_onHover=self.play_sound, arg_onHover="select")
        label_dedicated_shadow = Label(self.window_surface, pos=(82, 137, 140, 30), text="Выделенный: да",
                                       text_color=(0, 0, 0), font_size=18, font="main_menu")
        button_connect = Button(self.window_surface, pos=(80, 175, 140, 30), text="Создать",
                                transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                font_size=24, font="main_menu",
                                function_onClick_list=[self.play_sound, create_server],
                                args_list=["press", None],
                                function_onHover=self.play_sound, arg_onHover="select")
        label_connect_shadow = Label(self.window_surface, pos=(82, 177, 140, 30), text="Создать",
                                     text_color=(0, 0, 0), font_size=24, font="main_menu")

        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
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
        label_menu_name = Label(self.window_surface, pos=(150, 25, 0, 0), text="СОЗДАНИЕ СЕРВЕРА",
                                text_color=(240, 240, 240), font_size=28, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface, pos=(152, 27, 0, 0), text="СОЗДАНИЕ СЕРВЕРА",
                                       text_color=(0, 0, 0), font_size=28, font="main_menu")

        self.objects.append(label_connect_shadow)
        self.objects.append(button_connect)
        self.objects.append(label_dedicated_shadow)
        self.objects.append(button_dedicated)
        self.objects.append(textbox_server_ip)
        self.objects.append(label_server_ip_shadow)
        self.objects.append(label_server_ip)
        self.objects.append(buttontrigger_esc)
        self.objects.append(label_return_shadow)
        self.objects.append(button_return)
        self.objects.append(label_menu_name_shadow)
        self.objects.append(label_menu_name)

    def load_settings_group(self):
        """
        Загружает элементы подменю "Настройки"
        """
        self.objects.clear()

        button_sound_settings = Button(self.window_surface, pos=(80, 50, 140, 30), text="Звук",
                                       transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                       font_size=24, font="main_menu",
                                       function_onClick_list=[self.play_sound, self.load_sound_settings_group],
                                       args_list=["press", None],
                                       function_onHover=self.play_sound, arg_onHover="select")
        label_sound_settings_shadow = Label(self.window_surface, pos=(82, 52, 140, 30), text="Звук",
                                            text_color=(0, 0, 0), font_size=24, font="main_menu")
        button_multi_settings = Button(self.window_surface, pos=(80, 90, 140, 30), text="Настройки подключения",
                                       transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                       font_size=24, font="main_menu",
                                       function_onClick_list=[self.play_sound, self.load_multi_settings_group],
                                       args_list=["press", None],
                                       function_onHover=self.play_sound, arg_onHover="select")
        label_multi_settings_shadow = Label(self.window_surface, pos=(82, 92, 140, 30), text="Настройки подключения",
                                            text_color=(0, 0, 0), font_size=24, font="main_menu")
        label_menu_name = Label(self.window_surface, pos=(150, 25, 0, 0), text="НАСТРОЙКИ",
                                text_color=(240, 240, 240), font_size=28, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface, pos=(152, 27, 0, 0), text="НАСТРОЙКИ",
                                       text_color=(0, 0, 0), font_size=28, font="main_menu")
        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
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

        self.objects.append(label_sound_settings_shadow)
        self.objects.append(button_sound_settings)
        self.objects.append(label_multi_settings_shadow)
        self.objects.append(button_multi_settings)
        self.objects.append(label_return_shadow)
        self.objects.append(button_return)
        self.objects.append(label_menu_name_shadow)
        self.objects.append(label_menu_name)
        self.objects.append(buttontrigger_esc)

    def load_sound_settings_group(self):
        """
        Загружает элементы подменю "Звук"
        """
        self.objects.clear()

        label_menu_name = Label(self.window_surface, pos=(150, 25, 0, 0), text="НАСТРОЙКИ ЗВУКА",
                                text_color=(240, 240, 240), font_size=28, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface, pos=(152, 27, 0, 0), text="НАСТРОЙКИ ЗВУКА",
                                       text_color=(0, 0, 0), font_size=28, font="main_menu")
        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                          function_list=[self.play_sound, self.load_settings_group],
                                          args_list=["press", None], )
        button_return = Button(self.window_surface, pos=(0, 200, 140, 30), text="Назад",
                               transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                               font_size=24, font="main_menu",
                               function_onClick_list=[self.play_sound, self.load_settings_group],
                               args_list=["press", None],
                               function_onHover=self.play_sound, arg_onHover="select")
        label_return_shadow = Label(self.window_surface, pos=(2, 202, 140, 30), text="Назад",
                                    text_color=(0, 0, 0), font_size=24, font="main_menu")

        self.objects.append(label_return_shadow)
        self.objects.append(button_return)
        self.objects.append(label_menu_name_shadow)
        self.objects.append(label_menu_name)
        self.objects.append(buttontrigger_esc)

    is_client_ip_local = None

    def load_multi_settings_group(self):
        """
        Загружает элементы подменю "Настройки подключения"
        """

        regex_str = r"((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
        regex = re.compile(regex_str)

        if "client_ip" in self.result:
            self.is_client_ip_local = False
        else:
            self.is_client_ip_local = True

        def save_client_ip():
            if self.is_client_ip_local:
                self.result.pop("client_ip", None)
                self.load_settings_group()
            else:
                if regex.match(textbox_client_ip.text_str):
                    self.result["client_ip"] = textbox_client_ip.text_str
                    self.load_settings_group()
                else:
                    self.objects.append(label_wrong_ip_shadow)
                    self.objects.append(label_wrong_ip)

        def change_local_remote():
            if self.is_client_ip_local:
                # Если идёт первое изменение "локальности" или локальность сейчас в положении True
                button_is_local.set_text("Локальный адрес: нет")
                label_is_local_shadow.set_text("Локальный адрес: нет")
                self.objects.append(textbox_client_ip)
                self.objects.append(label_client_ip_shadow)
                self.objects.append(label_client_ip)
            else:
                # Если локальность сейчас в положении False
                button_is_local.set_text("Локальный адрес: да")
                label_is_local_shadow.set_text("Локальный адрес: да")
                self.objects.remove(textbox_client_ip)
                self.objects.remove(label_client_ip_shadow)
                self.objects.remove(label_client_ip)
            self.is_client_ip_local = not self.is_client_ip_local

        self.objects.clear()

        label_wrong_ip = Label(self.window_surface, pos=(80, 150, 140, 30),
                               text="Неправильный формат IP адреса!",
                               text_color=(224, 24, 24), font_size=14, font="main_menu")
        label_wrong_ip_shadow = Label(self.window_surface, pos=(81, 151, 140, 30),
                                      text="Неправильный формат IP адреса!",
                                      text_color=(0, 0, 0), font_size=14, font="main_menu")
        button_is_local = Button(self.window_surface, pos=(80, 50, 140, 30), text="Локальный адрес: да",
                                 transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                                 font_size=24, font="main_menu",
                                 function_onClick_list=[self.play_sound, change_local_remote],
                                 args_list=["press", None],
                                 function_onHover=self.play_sound, arg_onHover="select")
        label_is_local_shadow = Label(self.window_surface, pos=(82, 52, 140, 30), text="Локальный адрес: да",
                                      text_color=(0, 0, 0), font_size=24, font="main_menu")
        label_client_ip = Label(self.window_surface, pos=(80, 90, 140, 30), text="IP клиента:",
                                text_color=(224, 154, 24), font_size=24, font="main_menu")
        label_client_ip_shadow = Label(self.window_surface, pos=(82, 92, 140, 30), text="IP клиента:",
                                       text_color=(0, 0, 0), font_size=24, font="main_menu")
        textbox_client_ip = TextBox(self.window_surface, pos=(80, 120, 140, 30), font="main_menu",
                                    empty_text="IP адрес")
        button_save = Button(self.window_surface, pos=(80, 175, 140, 30), text="Сохранить",
                             transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                             font_size=24, font="main_menu",
                             function_onClick_list=[self.play_sound, save_client_ip],
                             args_list=["press", None],
                             function_onHover=self.play_sound, arg_onHover="select")
        label_save_shadow = Label(self.window_surface, pos=(82, 177, 140, 30), text="Сохранить",
                                  text_color=(0, 0, 0), font_size=24, font="main_menu")
        label_menu_name = Label(self.window_surface, pos=(150, 25, 0, 0), text="НАСТРОЙКИ ПОДКЛЮЧЕНИЯ",
                                text_color=(240, 240, 240), font_size=28, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface, pos=(152, 27, 0, 0), text="НАСТРОЙКИ ПОДКЛЮЧЕНИЯ",
                                       text_color=(0, 0, 0), font_size=28, font="main_menu")
        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                          function_list=[self.play_sound, self.load_settings_group],
                                          args_list=["press", None], )
        button_return = Button(self.window_surface, pos=(0, 200, 140, 30), text="Назад",
                               transparent=True, text_color=(224, 154, 24), selected_text_color=(237, 210, 7),
                               font_size=24, font="main_menu",
                               function_onClick_list=[self.play_sound, self.load_settings_group],
                               args_list=["press", None],
                               function_onHover=self.play_sound, arg_onHover="select")
        label_return_shadow = Label(self.window_surface, pos=(2, 202, 140, 30), text="Назад",
                                    text_color=(0, 0, 0), font_size=24, font="main_menu")

        self.objects.append(label_is_local_shadow)
        self.objects.append(button_is_local)
        self.objects.append(label_return_shadow)
        self.objects.append(button_return)
        self.objects.append(label_menu_name_shadow)
        self.objects.append(label_menu_name)
        self.objects.append(buttontrigger_esc)
        self.objects.append(label_save_shadow)
        self.objects.append(button_save)

        if not self.is_client_ip_local:
            button_is_local.set_text("Локальное подключение: нет")
            label_is_local_shadow.set_text("Локальное подключение: нет")
            textbox_client_ip.set_text(self.result["client_ip"])
            self.objects.append(textbox_client_ip)
            self.objects.append(label_client_ip_shadow)
            self.objects.append(label_client_ip)

    def main_cycle(self):
        while self.is_running:
            self.clock.tick(targetFPS)  # Требуемый FPS и соответствующая задержка
            self.window_surface.fill(DARK_GREY)

            # Обработка событий:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                # TODO: избавиться от этого костыля:
                if self.any_popup is not None:
                    if (return_code := self.any_popup.handle_event(event)) is not None:
                        if return_code == SKIP_EVENT:
                            break
                for obj in self.objects:
                    if (return_code := obj.handle_event(event)) is not None:
                        if return_code == SKIP_EVENT:
                            break

            if self.any_popup is not None:
                self.any_popup.update()
            for obj in self.objects:
                obj.update()
                obj.draw()
            if self.any_popup is not None:
                self.any_popup.draw()

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
