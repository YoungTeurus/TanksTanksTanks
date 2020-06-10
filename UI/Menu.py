import re
import socket
from random import randint
from typing import List

import pygame

from Consts import targetFPS, SOUNDS_VOLUME, MAPS, BLACK, BUTTON_SELECTED_YELLOW, MENU_WHITE, BUTTON_YELLOW, \
    MAIN_MENU_BACKGROUND_COLOR, MAIN_MENU_DARK_BACKGROUND_COLOR
from Files import get_script_dir
from UI.MenuObjects.Button import Button
from UI.MenuObjects.ButtonTrigger import ButtonTrigger
from UI.MenuObjects.Label import Label
from UI.MenuObjects.MenuLine import MenuLine
from UI.MenuObjects.MenuObject import SKIP_EVENT
from UI.MenuObjects.MenuRect import MenuRect
from UI.MenuObjects.PopupBox import PopupBox
from UI.MenuObjects.TextBox import TextBox
from UI.MenuObjects.Timer import Timer
from Multiplayer.ServerFinder import ServerFinder

BUTTON_WIDTH = 140
BUTTON_HEIGHT = 30
AUTO_H = AUTO_W = 0

TITLE_FONT_SIZE = 48
FONT_SIZE = 38


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
        self.size = (self.window_surface.get_width(), self.window_surface.get_height())

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

        def add_quit_popup():
            self.any_popup = popupbox_quit

        def remove_quit_popup():
            self.any_popup = None

        self.objects.clear()

        button_start_solo = Button(self.window_surface,
                                   pos=(self.size[0] / 2 - BUTTON_WIDTH / 2, self.size[1] / 10 * 2,
                                        BUTTON_WIDTH, BUTTON_HEIGHT),
                                   text="Одиночная игра",
                                   transparent=True, text_color=BUTTON_YELLOW,
                                   selected_text_color=BUTTON_SELECTED_YELLOW,
                                   font_size=FONT_SIZE, font="main_menu",
                                   function_onClick_list=[self.play_sound, self.load_start_solo_group],
                                   args_list=["press", None],
                                   function_onHover=self.play_sound, arg_onHover="select")
        label_start_solo_shadow = Label(self.window_surface,
                                        pos=(self.size[0] / 2 - BUTTON_WIDTH / 2 + 2, self.size[1] / 10 * 2 + 2,
                                             BUTTON_WIDTH, BUTTON_HEIGHT),
                                        text="Одиночная игра",
                                        text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        button_start_multi = Button(self.window_surface,
                                    pos=(self.size[0] / 2 - BUTTON_WIDTH / 2, self.size[1] / 10 * 3,
                                         BUTTON_WIDTH, BUTTON_HEIGHT),
                                    text="Совместная игра",
                                    transparent=True, text_color=BUTTON_YELLOW,
                                    selected_text_color=BUTTON_SELECTED_YELLOW,
                                    font_size=FONT_SIZE, font="main_menu",
                                    function_onClick_list=[self.play_sound, self.load_start_multi_group],
                                    args_list=["press", None],
                                    function_onHover=self.play_sound, arg_onHover="select")
        label_start_milti_shadow = Label(self.window_surface,
                                         pos=(self.size[0] / 2 - BUTTON_WIDTH / 2 + 2, self.size[1] / 10 * 3 + 2,
                                              BUTTON_WIDTH, BUTTON_HEIGHT),
                                         text="Совместная игра",
                                         text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        button_settings = Button(self.window_surface,
                                 pos=(self.size[0] / 2 - BUTTON_WIDTH / 2, self.size[1] / 10 * 4,
                                      BUTTON_WIDTH, BUTTON_HEIGHT), text="Настройки",
                                 transparent=True, text_color=BUTTON_YELLOW,
                                 selected_text_color=BUTTON_SELECTED_YELLOW,
                                 font_size=FONT_SIZE, font="main_menu",
                                 function_onClick_list=[self.play_sound, self.load_settings_group],
                                 args_list=["press", None],
                                 function_onHover=self.play_sound, arg_onHover="select")
        label_settings_shadow = Label(self.window_surface,
                                      pos=(self.size[0] / 2 - BUTTON_WIDTH / 2 + 2, self.size[1] / 10 * 4 + 2,
                                           BUTTON_WIDTH, BUTTON_HEIGHT),
                                      text="Настройки",
                                      text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        button_quit = Button(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2, self.size[1] / 10 * 8, BUTTON_WIDTH, BUTTON_HEIGHT),
                             text="Выйти из игры",
                             transparent=True, text_color=BUTTON_YELLOW,
                             selected_text_color=BUTTON_SELECTED_YELLOW,
                             font_size=FONT_SIZE, font="main_menu",
                             function_onClick_list=[self.play_sound, add_quit_popup],
                             args_list=["press", None],
                             function_onHover=self.play_sound, arg_onHover="select")
        label_quit_shadow = Label(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2 + 2, self.size[1] / 10 * 8 + 2, BUTTON_WIDTH, BUTTON_HEIGHT),
                                  text="Выйти из игры",
                                  text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        label_title = Label(self.window_surface, pos=(self.size[0] / 2, self.size[1] / 10 * 1, AUTO_W, AUTO_H),
                            text="TANK! TANK! TANK!",
                            text_color=MENU_WHITE, font_size=TITLE_FONT_SIZE, font="main_menu")
        label_title_shadow = Label(self.window_surface, pos=(self.size[0] / 2 + 2, self.size[1] / 10 * 1 + 2,
                                                             AUTO_W, AUTO_H),
                                   text="TANK! TANK! TANK!",
                                   text_color=BLACK, font_size=TITLE_FONT_SIZE, font="main_menu")

        # Всплывающее окно "Вы это серьёзно?" при выходе:
        popup_size = (350, 120)  # Вспомогательные переменные
        popup_pos = (self.size[0] / 2 - popup_size[0] / 2, self.size[1] / 2 - popup_size[1] / 2)

        popupbox_quit = PopupBox(self.window_surface, pos=(popup_pos[0], popup_pos[1], popup_size[0], popup_size[1]),
                                 color=MAIN_MENU_BACKGROUND_COLOR)
        label_popupbox_quit_title = Label(self.window_surface,
                                          pos=(popup_pos[0] + popup_size[0] / 2,
                                               popup_pos[1] + popup_size[1] / 5,
                                               AUTO_W, AUTO_H),
                                          text="Вы это серьёзно?", text_color=MENU_WHITE,
                                          font_size=FONT_SIZE, font="main_menu")
        label_popupbox_quit_title_shadow = Label(self.window_surface,
                                                 pos=(popup_pos[0] + popup_size[0] / 2 + 2,
                                                      popup_pos[1] + popup_size[1] / 5 + 2,
                                                      AUTO_W, AUTO_H),
                                                 text="Вы это серьёзно?", text_color=BLACK,
                                                 font_size=FONT_SIZE, font="main_menu")
        buttontrigger_popupbox_quit_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                                        function_list=[self.play_sound, remove_quit_popup],
                                                        args_list=["press", None])
        button_popupbox_quit_yes = Button(self.window_surface,
                                          pos=(popup_pos[0] + popup_size[0] / 4,
                                               popup_pos[1] + popup_size[1] / 4 * 3,
                                               0, 0), text="Да",
                                          transparent=True, text_color=BUTTON_YELLOW,
                                          selected_text_color=BUTTON_SELECTED_YELLOW,
                                          font_size=FONT_SIZE, font="main_menu",
                                          function_onClick_list=[self.play_sound, quit_game],
                                          args_list=["press", None],
                                          function_onHover=self.play_sound, arg_onHover="select")
        label_popupbox_quit_yes_shadow = Label(self.window_surface,
                                               pos=(popup_pos[0] + popup_size[0] / 4 + 2,
                                                    popup_pos[1] + popup_size[1] / 4 * 3 + 2,
                                                    0, 0),
                                               text="Да", text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        button_popupbox_quit_no = Button(self.window_surface,
                                         pos=(popup_pos[0] + popup_size[0] / 4 * 3,
                                              popup_pos[1] + popup_size[1] / 4 * 3,
                                              0, 0), text="Нет",
                                         transparent=True, text_color=BUTTON_YELLOW,
                                         selected_text_color=BUTTON_SELECTED_YELLOW,
                                         font_size=FONT_SIZE, font="main_menu",
                                         function_onClick_list=[self.play_sound, remove_quit_popup],
                                         args_list=["press", None],
                                         function_onHover=self.play_sound, arg_onHover="select")
        label_popupbox_quit_no_shadow = Label(self.window_surface,
                                              pos=(popup_pos[0] + popup_size[0] / 4 * 3 + 2,
                                                   popup_pos[1] + popup_size[1] / 4 * 3 + 2,
                                                   0, 0),
                                              text="Нет", text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        popupbox_quit.add_object(buttontrigger_popupbox_quit_esc)
        popupbox_quit.add_object(label_popupbox_quit_yes_shadow)
        popupbox_quit.add_object(button_popupbox_quit_yes)
        popupbox_quit.add_object(label_popupbox_quit_no_shadow)
        popupbox_quit.add_object(button_popupbox_quit_no)
        popupbox_quit.add_object(label_popupbox_quit_title_shadow)
        popupbox_quit.add_object(label_popupbox_quit_title)

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

        button_start_new = Button(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2, self.size[1] / 10 * 2, BUTTON_WIDTH, BUTTON_HEIGHT),
                                  text="Начать новую",
                                  transparent=True, text_color=BUTTON_YELLOW,
                                  selected_text_color=BUTTON_SELECTED_YELLOW,
                                  font_size=FONT_SIZE, font="main_menu",
                                  function_onClick_list=[self.play_sound, self.start_solo_game],
                                  args_list=["press", None],
                                  function_onHover=self.play_sound, arg_onHover="select")
        label_start_new_shadow = Label(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2 + 2, self.size[1] / 10 * 2 + 2, BUTTON_WIDTH, BUTTON_HEIGHT),
                                       text="Начать новую",
                                       text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        button_select_level = Button(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2, self.size[1] / 10 * 3, BUTTON_WIDTH, BUTTON_HEIGHT),
                                     text="Выбрать уровень",
                                     transparent=True, text_color=BUTTON_YELLOW,
                                     selected_text_color=BUTTON_SELECTED_YELLOW,
                                     font_size=FONT_SIZE, font="main_menu",
                                     function_onClick_list=[self.play_sound, self.load_select_level_group],
                                     args_list=["press", None],
                                     function_onHover=self.play_sound, arg_onHover="select")
        label_select_level_shadow = Label(self.window_surface,
                                          pos=(self.size[0] / 2 - BUTTON_WIDTH / 2 + 2, self.size[1] / 10 * 3 + 2,
                                               BUTTON_WIDTH, BUTTON_HEIGHT),
                                          text="Выбрать уровень",
                                          text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        label_menu_name = Label(self.window_surface, pos=(self.size[0] / 2, self.size[1] / 10 * 1, AUTO_W, AUTO_H),
                                text="ОДИНОЧНАЯ ИГРА",
                                text_color=MENU_WHITE, font_size=TITLE_FONT_SIZE, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface,
                                       pos=(self.size[0] / 2 + 2, self.size[1] / 10 * 1 + 2, AUTO_W, AUTO_H),
                                       text="ОДИНОЧНАЯ ИГРА",
                                       text_color=BLACK, font_size=TITLE_FONT_SIZE, font="main_menu")
        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                          function_list=[self.play_sound, self.load_title_group],
                                          args_list=["press", None])
        button_return = Button(self.window_surface, pos=(self.size[0] / 5 - BUTTON_WIDTH, self.size[1] / 10 * 8,
                                                         BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                               transparent=True, text_color=BUTTON_YELLOW, selected_text_color=BUTTON_SELECTED_YELLOW,
                               font_size=FONT_SIZE, font="main_menu",
                               function_onClick_list=[self.play_sound, self.load_title_group],
                               args_list=["press", None],
                               function_onHover=self.play_sound, arg_onHover="select")
        label_return_shadow = Label(self.window_surface,
                                    pos=(self.size[0] / 5 - BUTTON_WIDTH + 2, self.size[1] / 10 * 8 + 2,
                                         BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                                    text_color=BLACK, font_size=FONT_SIZE, font="main_menu")

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

        label_menu_name = Label(self.window_surface, pos=(self.size[0] / 2, self.size[1] / 10 * 1, AUTO_W, AUTO_H),
                                text="ВЫБРАТЬ УРОВЕНЬ",
                                text_color=MENU_WHITE, font_size=TITLE_FONT_SIZE, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface,
                                       pos=(self.size[0] / 2 + 2, self.size[1] / 10 * 1 + 2, AUTO_W, AUTO_H),
                                       text="ВЫБРАТЬ УРОВЕНЬ",
                                       text_color=BLACK, font_size=TITLE_FONT_SIZE, font="main_menu")
        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                          function_list=[self.play_sound, self.load_start_solo_group],
                                          args_list=["press", None], )
        button_return = Button(self.window_surface, pos=(
            self.size[0] / 5 - BUTTON_WIDTH, self.size[1] / 10 * 8, BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                               transparent=True, text_color=BUTTON_YELLOW, selected_text_color=BUTTON_SELECTED_YELLOW,
                               font_size=FONT_SIZE, font="main_menu",
                               function_onClick_list=[self.play_sound, self.load_start_solo_group],
                               args_list=["press", None],
                               function_onHover=self.play_sound, arg_onHover="select")
        label_return_shadow = Label(self.window_surface, pos=(
            self.size[0] / 5 - BUTTON_WIDTH + 2, self.size[1] / 10 * 8 + 2, BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                                    text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        for (i, map_tuple) in enumerate(get_all_maps_names()):
            x = self.size[0] / 2 - BUTTON_WIDTH / 2
            y = self.size[1] / 10 * (2 + i)
            button_map_name = Button(self.window_surface, pos=(x, y, BUTTON_WIDTH, BUTTON_HEIGHT), text=map_tuple[1],
                                     transparent=True, text_color=BUTTON_YELLOW,
                                     selected_text_color=BUTTON_SELECTED_YELLOW,
                                     font_size=FONT_SIZE, font="main_menu",
                                     function_onClick_list=[self.play_sound, set_result_level],
                                     args_list=["press", map_tuple[0]],
                                     function_onHover=self.play_sound, arg_onHover="select")
            label_map_name_shadow = Label(self.window_surface, pos=(x + 2, y + 2, BUTTON_WIDTH, BUTTON_HEIGHT),
                                          text=map_tuple[1],
                                          text_color=BLACK, font_size=FONT_SIZE, font="main_menu")

            self.objects.append(label_map_name_shadow)
            self.objects.append(button_map_name)

        self.objects.append(label_return_shadow)
        self.objects.append(button_return)
        self.objects.append(label_menu_name_shadow)
        self.objects.append(label_menu_name)
        self.objects.append(buttontrigger_esc)

    def start_multi_game_client(self):
        def get_and_check_port():
            while True:
                port = randint(9999, 60000)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.bind((self.result["client_ip"], port))
                except OSError:
                    continue
                finally:
                    sock.close()
                break
            return port
        self.is_running = False
        self.result["result"] = "start"
        self.result["mode"] = "client"
        self.result["multi"] = True
        if "client_ip" not in self.result:
            self.result["client_ip"] = socket.gethostbyname(socket.getfqdn())
        if "client_port" not in self.result:
            self.result["client_port"] = get_and_check_port()

    def load_start_multi_group(self):
        """
        Загружает элементы подменю "Совместная игра"
        """

        self.objects.clear()

        button_connect_to = Button(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2, self.size[1] / 10 * 2, BUTTON_WIDTH, BUTTON_HEIGHT),
                                   text="Браузер серверов",
                                   transparent=True, text_color=BUTTON_YELLOW,
                                   selected_text_color=BUTTON_SELECTED_YELLOW,
                                   font_size=FONT_SIZE, font="main_menu",
                                   function_onClick_list=[self.play_sound, self.load_server_browser_group],
                                   args_list=["press", None],
                                   function_onHover=self.play_sound, arg_onHover="select")
        label_connect_to_shadow = Label(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2 + 2, self.size[1] / 10 * 2 + 2, BUTTON_WIDTH, BUTTON_HEIGHT),
                                        text="Браузер серверов",
                                        text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        button_create_server = Button(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2, self.size[1] / 10 * 3, BUTTON_WIDTH, BUTTON_HEIGHT),
                                      text="Создать сервер",
                                      transparent=True, text_color=BUTTON_YELLOW,
                                      selected_text_color=BUTTON_SELECTED_YELLOW,
                                      font_size=FONT_SIZE, font="main_menu",
                                      function_onClick_list=[self.play_sound, self.load_create_server_group],
                                      args_list=["press", None],
                                      function_onHover=self.play_sound, arg_onHover="select")
        label_create_server_shadow = Label(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2 + 2, self.size[1] / 10 * 3 + 2, BUTTON_WIDTH, BUTTON_HEIGHT),
                                           text="Создать сервер",
                                           text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        button_direct_connect = Button(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2, self.size[1] / 10 * 4, BUTTON_WIDTH, BUTTON_HEIGHT),
                                       text="Прямое подключение",
                                       transparent=True, text_color=BUTTON_YELLOW,
                                       selected_text_color=BUTTON_SELECTED_YELLOW,
                                       font_size=FONT_SIZE, font="main_menu",
                                       function_onClick_list=[self.play_sound, self.load_direct_connect_group],
                                       args_list=["press", None],
                                       function_onHover=self.play_sound, arg_onHover="select")
        label_direct_connect_shadow = Label(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2 + 2, self.size[1] / 10 * 4 + 2, BUTTON_WIDTH, BUTTON_HEIGHT),
                                            text="Прямое подключение",
                                            text_color=BLACK, font_size=FONT_SIZE, font="main_menu")

        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                          function_list=[self.play_sound, self.load_title_group],
                                          args_list=["press", None], )
        button_return = Button(self.window_surface, pos=(
            self.size[0] / 5 - BUTTON_WIDTH, self.size[1] / 10 * 8, BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                               transparent=True, text_color=BUTTON_YELLOW, selected_text_color=BUTTON_SELECTED_YELLOW,
                               font_size=FONT_SIZE, font="main_menu",
                               function_onClick_list=[self.play_sound, self.load_title_group],
                               args_list=["press", None],
                               function_onHover=self.play_sound, arg_onHover="select")
        label_return_shadow = Label(self.window_surface, pos=(
            self.size[0] / 5 - BUTTON_WIDTH + 2, self.size[1] / 10 * 8 + 2, BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                                    text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        label_menu_name = Label(self.window_surface, pos=(self.size[0] / 2, self.size[1] / 10 * 1, AUTO_W, AUTO_H),
                                text="СОВМЕСТНАЯ ИГРА",
                                text_color=MENU_WHITE, font_size=TITLE_FONT_SIZE, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface,
                                       pos=(self.size[0] / 2 + 2, self.size[1] / 10 * 1 + 2, AUTO_W, AUTO_H),
                                       text="СОВМЕСТНАЯ ИГРА",
                                       text_color=BLACK, font_size=TITLE_FONT_SIZE, font="main_menu")

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

    def load_server_browser_group(self):
        """
        Загружает элементы подменю "Браузер серверов"
        """

        def connect_to(server_ip: str):
            self.result["server_ip"] = server_ip
            self.start_multi_game_client()

        class ServerRecord:
            # Небольшой класс, объединяющий кнопку, её тень и линию после записи
            button_ip: Button = None
            button_ip_shadow: Label = None

            button_name: Button = None
            button_name_shadow: Button = None

            line: MenuLine = None

        def find_servers():
            # Запускает поиск серверов
            clear_servers()  # Очищаем список серверов
            server_finders[0].add_all_local_ips()  # Заносим все локальные IP-шники
            server_finders[0].start()
            timer_test.start()
            button_refresh.set_active(False)

        def clear_servers():
            # Убирает надпись "Серверы не найдены", если она есть
            if label_no_servers_found in self.objects:
                self.objects.remove(label_no_servers_found)
                self.objects.remove(label_no_servers_found_shadow)
            # Очищает список серверов
            for server_record in servers:
                self.objects.remove(server_record.button_ip)
                self.objects.remove(server_record.button_ip_shadow)
                self.objects.remove(server_record.button_name)
                self.objects.remove(server_record.button_name_shadow)
                self.objects.remove(server_record.line)
            servers.clear()

        def add_server_button(server_ip: str, server_name: str):
            for server in servers:
                if server_ip == server.button_ip.text_str:  # Избавляемся от копий
                    return
            # Добавляет кнопку для подклчючения к серверу
            temp_record = ServerRecord()
            temp_record.button_ip = Button(self.window_surface,
                                           pos=(servers_frame_pos[0] + servers_frame_size[0] / 7 * 6.5 - BUTTON_WIDTH,
                                                servers_frame_pos[1] + servers_frame_size[1] / 5 * (len(
                                                    servers) + 1) - BUTTON_HEIGHT,
                                                BUTTON_WIDTH, BUTTON_HEIGHT),
                                           text=server_ip,
                                           transparent=True, text_color=BUTTON_YELLOW,
                                           selected_text_color=BUTTON_SELECTED_YELLOW,
                                           font_size=FONT_SIZE, font="main_menu",
                                           function_onClick_list=[self.play_sound, connect_to],
                                           args_list=["press", server_ip],
                                           function_onHover=self.play_sound, arg_onHover="select")
            temp_record.button_ip_shadow = Label(self.window_surface,
                                                 pos=(servers_frame_pos[0] + servers_frame_size[
                                                     0] / 7 * 6.5 - BUTTON_WIDTH + 2,
                                                      servers_frame_pos[1] + servers_frame_size[1] / 5 * (len(
                                                          servers) + 1) - BUTTON_HEIGHT + 2,
                                                      BUTTON_WIDTH, BUTTON_HEIGHT),
                                                 text=server_ip, text_color=BLACK, font_size=FONT_SIZE,
                                                 font="main_menu")
            temp_record.button_name = Button(self.window_surface,
                                             pos=(servers_frame_pos[0] + servers_frame_size[0] / 7 * 3 - BUTTON_WIDTH,
                                                  servers_frame_pos[1] + servers_frame_size[1] / 5 * (len(
                                                      servers) + 1) - BUTTON_HEIGHT,
                                                  BUTTON_WIDTH, BUTTON_HEIGHT),
                                             text=server_name,
                                             transparent=True, text_color=BUTTON_YELLOW,
                                             selected_text_color=BUTTON_SELECTED_YELLOW,
                                             font_size=FONT_SIZE, font="main_menu",
                                             function_onClick_list=[self.play_sound, connect_to],
                                             args_list=["press", server_ip],
                                             function_onHover=self.play_sound, arg_onHover="select")
            temp_record.button_name_shadow = Label(self.window_surface,
                                                   pos=(servers_frame_pos[0] + servers_frame_size[
                                                       0] / 7 * 3 - BUTTON_WIDTH + 2,
                                                        servers_frame_pos[1] + servers_frame_size[1] / 5 * (len(
                                                            servers) + 1) - BUTTON_HEIGHT + 2,
                                                        BUTTON_WIDTH, BUTTON_HEIGHT),
                                                   text=server_name, text_color=BLACK, font_size=FONT_SIZE,
                                                   font="main_menu")
            temp_record.line = MenuLine(self.window_surface,
                                        startpos=(servers_frame_pos[0] + servers_frame_size[0] / 9,
                                                  servers_frame_pos[1] + servers_frame_size[1] / 5 *
                                                  (len(servers) + 1.2)
                                                  ),
                                        endpos=(servers_frame_pos[0] + servers_frame_size[0] / 9 * 8,
                                                servers_frame_pos[1] + servers_frame_size[1] / 5 *
                                                (len(servers) + 1.2)
                                                ),
                                        color=BUTTON_YELLOW)
            self.objects.append(temp_record.line)
            self.objects.append(temp_record.button_ip_shadow)
            self.objects.append(temp_record.button_ip)
            self.objects.append(temp_record.button_name_shadow)
            self.objects.append(temp_record.button_name)
            servers.append(temp_record)

        def check_server_finder():
            if server_finders[0].is_ready:
                # Если процесс поиска закончлся...
                if server_finders[0].good_ip_list.__len__() == 0:
                    # Если не было найдено ни одного сервера...
                    self.objects.append(label_no_servers_found_shadow)
                    self.objects.append(label_no_servers_found)
                for server_ip, server_name in server_finders[0].good_ip_list:
                    add_server_button(server_ip, server_name)

                # TODO: супер-костыль - пересоздание ServerFinder-а
                del server_finders[0]
                server_finders.clear()
                server_finders.append(ServerFinder(self.result["client_ip"], self.result["client_port"]))
                button_refresh.set_active(True)
            else:
                # Если процесс поиска ещё не закончился...
                timer_test.reset()
                timer_test.start()

        self.objects.clear()

        # Подготовка server_finder-а:
        server_finders: List[ServerFinder] = []  # TODO: супер-костыль - массив из 1-го элемента
        if "client_ip" not in self.result:
            self.result["client_ip"] = socket.gethostbyname(socket.getfqdn())
        if "client_port" not in self.result:
            self.result["client_port"] = randint(9999, 60000)
        server_finders.append(ServerFinder(self.result["client_ip"], self.result["client_port"]))

        servers: List[ServerRecord] = []  # Список кнопок с ip-адресами серверов

        servers_frame_pos = (self.size[0] / 10, self.size[1] / 5)
        servers_frame_size = (self.size[0] / 10 * 8, self.size[1] / 5 * 2)

        label_no_servers_found = Label(self.window_surface, pos=(self.size[0] / 2 - BUTTON_WIDTH / 2,
                                                                 self.size[1] / 5 * 1.5 - BUTTON_HEIGHT,
                                                                 BUTTON_WIDTH, BUTTON_HEIGHT),
                                       text="Серверы не найдены",
                                       text_color=BUTTON_YELLOW, font_size=int(FONT_SIZE * 0.75), font="main_menu")
        label_no_servers_found_shadow = Label(self.window_surface, pos=(self.size[0] / 2 - BUTTON_WIDTH / 2 + 2,
                                                                        self.size[1] / 5 * 1.5 - BUTTON_HEIGHT + 2,
                                                                        BUTTON_WIDTH, BUTTON_HEIGHT),
                                              text="Серверы не найдены",
                                              text_color=BLACK, font_size=int(FONT_SIZE * 0.75), font="main_menu")

        menurect_servers_frame = MenuRect(self.window_surface, pos=(servers_frame_pos[0], servers_frame_pos[1],
                                                                    servers_frame_size[0], servers_frame_size[1]),
                                          fill_color=MAIN_MENU_DARK_BACKGROUND_COLOR, frame_color=BUTTON_YELLOW)
        button_refresh = Button(self.window_surface, pos=(self.size[0] / 10 * 7 - BUTTON_WIDTH / 2,
                                                          self.size[1] / 5 * 3.2,
                                                          BUTTON_WIDTH, BUTTON_HEIGHT), text="Обновить",
                                transparent=True, text_color=BUTTON_YELLOW, selected_text_color=BUTTON_SELECTED_YELLOW,
                                font_size=int(FONT_SIZE * 0.75), font="main_menu",
                                function_onClick_list=[self.play_sound, find_servers],
                                args_list=["press", None],
                                function_onHover=self.play_sound, arg_onHover="select")
        label_refresh_shadow = Label(self.window_surface, pos=(self.size[0] / 10 * 7 - BUTTON_WIDTH / 2 + 2,
                                                               self.size[1] / 5 * 3.2 + 2,
                                                               BUTTON_WIDTH, BUTTON_HEIGHT), text="Обновить",
                                     text_color=BLACK, font_size=int(FONT_SIZE * 0.75), font="main_menu")

        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                          function_list=[self.play_sound, self.load_start_multi_group],
                                          args_list=["press", None])
        button_return = Button(self.window_surface, pos=(
            self.size[0] / 5 - BUTTON_WIDTH, self.size[1] / 10 * 8, BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                               transparent=True, text_color=BUTTON_YELLOW, selected_text_color=BUTTON_SELECTED_YELLOW,
                               font_size=FONT_SIZE, font="main_menu",
                               function_onClick_list=[self.play_sound, self.load_start_multi_group],
                               args_list=["press", None],
                               function_onHover=self.play_sound, arg_onHover="select")
        label_return_shadow = Label(self.window_surface, pos=(
            self.size[0] / 5 - BUTTON_WIDTH + 2, self.size[1] / 10 * 8 + 2, BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                                    text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        label_menu_name = Label(self.window_surface, pos=(self.size[0] / 2, self.size[1] / 10 * 1, AUTO_W, AUTO_H),
                                text="Браузер серверов".upper(),
                                text_color=MENU_WHITE, font_size=TITLE_FONT_SIZE, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface,
                                       pos=(self.size[0] / 2 + 2, self.size[1] / 10 * 1 + 2, AUTO_W, AUTO_H),
                                       text="Браузер серверов".upper(),
                                       text_color=BLACK, font_size=TITLE_FONT_SIZE, font="main_menu")

        timer_test = Timer(target_millis=500, function_onTarget=check_server_finder,
                           function_args=None, start_of_init=False)

        self.objects.append(timer_test)
        self.objects.append(menurect_servers_frame)
        self.objects.append(label_refresh_shadow)
        self.objects.append(button_refresh)
        self.objects.append(label_return_shadow)
        self.objects.append(button_return)
        self.objects.append(buttontrigger_esc)
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
                # TODO: делать проверку на существование серевера
            else:
                self.objects.append(label_wrong_ip_shadow)
                self.objects.append(label_wrong_ip)

        self.objects.clear()

        label_wrong_ip = Label(self.window_surface, pos=(self.size[0] / 2 - BUTTON_WIDTH / 2,
                                                         self.size[1] / 10 * 4,
                                                         BUTTON_WIDTH, BUTTON_HEIGHT),
                               text="Неправильный формат IP адреса!",
                               text_color=(224, 24, 24), font_size=int(FONT_SIZE * 0.75), font="main_menu")
        label_wrong_ip_shadow = Label(self.window_surface, pos=(self.size[0] / 2 - BUTTON_WIDTH / 2 + 2,
                                                                self.size[1] / 10 * 4 + 2,
                                                                BUTTON_WIDTH, BUTTON_HEIGHT),
                                      text="Неправильный формат IP адреса!",
                                      text_color=BLACK, font_size=int(FONT_SIZE * 0.75), font="main_menu")
        label_server_ip = Label(self.window_surface, pos=(
            self.size[0] / 3 - BUTTON_WIDTH / 2, self.size[1] / 10 * 3, BUTTON_WIDTH, BUTTON_HEIGHT),
                                text="IP сервера:",
                                text_color=BUTTON_YELLOW, font_size=FONT_SIZE, font="main_menu")
        label_server_ip_shadow = Label(self.window_surface, pos=(
            self.size[0] / 3 - BUTTON_WIDTH / 2 + 2, self.size[1] / 10 * 3 + 2, BUTTON_WIDTH, BUTTON_HEIGHT),
                                       text="IP сервера:",
                                       text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        textbox_server_ip = TextBox(self.window_surface,
                                    pos=(self.size[0] / 2, self.size[1] / 10 * 3 - BUTTON_HEIGHT / 2,
                                         self.size[0] / 3, self.size[1] / 10), font="main_menu", font_size=FONT_SIZE,
                                    function_onEnter=connect_to, empty_text="IP адрес")
        button_connect = Button(self.window_surface, pos=(self.size[0] / 2 - BUTTON_WIDTH / 2, self.size[1] / 10 * 7,
                                                          BUTTON_WIDTH, BUTTON_HEIGHT), text="Подключиться",
                                transparent=True, text_color=BUTTON_YELLOW, selected_text_color=BUTTON_SELECTED_YELLOW,
                                font_size=FONT_SIZE, font="main_menu",
                                function_onClick_list=[self.play_sound, connect_to],
                                args_list=["press", None],
                                function_onHover=self.play_sound, arg_onHover="select")
        label_connect_shadow = Label(self.window_surface, pos=(self.size[0] / 2 - BUTTON_WIDTH / 2 + 2,
                                                               self.size[1] / 10 * 7 + 2, BUTTON_WIDTH, BUTTON_HEIGHT),
                                     text="Подключиться",
                                     text_color=BLACK, font_size=FONT_SIZE, font="main_menu")

        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                          function_list=[self.play_sound, self.load_start_multi_group],
                                          args_list=["press", None], )
        button_return = Button(self.window_surface, pos=(
            self.size[0] / 5 - BUTTON_WIDTH, self.size[1] / 10 * 8, BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                               transparent=True, text_color=BUTTON_YELLOW, selected_text_color=BUTTON_SELECTED_YELLOW,
                               font_size=FONT_SIZE, font="main_menu",
                               function_onClick_list=[self.play_sound, self.load_start_multi_group],
                               args_list=["press", None],
                               function_onHover=self.play_sound, arg_onHover="select")
        label_return_shadow = Label(self.window_surface, pos=(
            self.size[0] / 5 - BUTTON_WIDTH + 2, self.size[1] / 10 * 8 + 2, BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                                    text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        label_menu_name = Label(self.window_surface, pos=(self.size[0] / 2, self.size[1] / 10 * 1, AUTO_W, AUTO_H),
                                text="ПРЯМОЕ ПОДКЛЮЧЕНИЕ",
                                text_color=MENU_WHITE, font_size=TITLE_FONT_SIZE, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface,
                                       pos=(self.size[0] / 2 + 2, self.size[1] / 10 * 1 + 2, AUTO_W, AUTO_H),
                                       text="ПРЯМОЕ ПОДКЛЮЧЕНИЕ",
                                       text_color=BLACK, font_size=TITLE_FONT_SIZE, font="main_menu")

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
            if textbox_server_ip.text_str.__len__() == 0:
                self.result["server_ip"] = socket.gethostbyname(socket.getfqdn())
                start_multi_game_server()
                return
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

        label_wrong_ip = Label(self.window_surface, pos=(self.size[0] / 2 - BUTTON_WIDTH / 2,
                                                         self.size[1] / 10 * 3.9, BUTTON_WIDTH, BUTTON_HEIGHT),
                               text="",
                               text_color=(224, 24, 24), font_size=int(FONT_SIZE * 0.75), font="main_menu")
        label_wrong_ip_shadow = Label(self.window_surface, pos=(self.size[0] / 2 - BUTTON_WIDTH / 2 + 2,
                                                                self.size[1] / 10 * 3.9 + 2, BUTTON_WIDTH,
                                                                BUTTON_HEIGHT),
                                      text="",
                                      text_color=BLACK, font_size=int(FONT_SIZE * 0.75), font="main_menu")
        self.objects.append(label_wrong_ip_shadow)
        self.objects.append(label_wrong_ip)

        label_server_ip = Label(self.window_surface, pos=(
            self.size[0] / 3 - BUTTON_WIDTH / 2, self.size[1] / 10 * 3, BUTTON_WIDTH, BUTTON_HEIGHT),
                                text="IP сервера:",
                                text_color=BUTTON_YELLOW, font_size=FONT_SIZE, font="main_menu")
        label_server_ip_shadow = Label(self.window_surface, pos=(
            self.size[0] / 3 - BUTTON_WIDTH / 2 + 2, self.size[1] / 10 * 3 + 2, BUTTON_WIDTH, BUTTON_HEIGHT),
                                       text="IP сервера:",
                                       text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        textbox_server_ip = TextBox(self.window_surface,
                                    pos=(self.size[0] / 2, self.size[1] / 10 * 3 - BUTTON_HEIGHT / 2,
                                         self.size[0] / 3, self.size[1] / 10), font="main_menu", font_size=FONT_SIZE,
                                    function_onEnter=create_server, empty_text="Локальный сервер")
        button_dedicated = Button(self.window_surface, pos=(self.size[0] / 2 - BUTTON_WIDTH / 2,
                                                            self.size[1] / 10 * 4.5,
                                                            BUTTON_WIDTH, BUTTON_HEIGHT),
                                  text="Выделенный: да",
                                  transparent=True, text_color=BUTTON_YELLOW,
                                  selected_text_color=BUTTON_SELECTED_YELLOW,
                                  font_size=int(FONT_SIZE * 0.75), font="main_menu",
                                  function_onClick_list=[self.play_sound, change_dedicated],
                                  args_list=["press", None],
                                  function_onHover=self.play_sound, arg_onHover="select")
        label_dedicated_shadow = Label(self.window_surface, pos=(self.size[0] / 2 - BUTTON_WIDTH / 2 + 2,
                                                                 self.size[1] / 10 * 4.5 + 2,
                                                                 BUTTON_WIDTH, BUTTON_HEIGHT),
                                       text="Выделенный: да",
                                       text_color=BLACK, font_size=int(FONT_SIZE * 0.75), font="main_menu")
        button_connect = Button(self.window_surface, pos=(self.size[0] / 2 - BUTTON_WIDTH / 2,
                                                          self.size[1] / 10 * 6,
                                                          BUTTON_WIDTH, BUTTON_HEIGHT), text="Создать",
                                transparent=True, text_color=BUTTON_YELLOW, selected_text_color=BUTTON_SELECTED_YELLOW,
                                font_size=FONT_SIZE, font="main_menu",
                                function_onClick_list=[self.play_sound, create_server],
                                args_list=["press", None],
                                function_onHover=self.play_sound, arg_onHover="select")
        label_connect_shadow = Label(self.window_surface, pos=(self.size[0] / 2 - BUTTON_WIDTH / 2 + 2,
                                                               self.size[1] / 10 * 6 + 2,
                                                               BUTTON_WIDTH, BUTTON_HEIGHT), text="Создать",
                                     text_color=BLACK, font_size=FONT_SIZE, font="main_menu")

        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                          function_list=[self.play_sound, self.load_start_multi_group],
                                          args_list=["press", None], )
        button_return = Button(self.window_surface, pos=(
            self.size[0] / 5 - BUTTON_WIDTH, self.size[1] / 10 * 8, BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                               transparent=True, text_color=BUTTON_YELLOW, selected_text_color=BUTTON_SELECTED_YELLOW,
                               font_size=FONT_SIZE, font="main_menu",
                               function_onClick_list=[self.play_sound, self.load_start_multi_group],
                               args_list=["press", None],
                               function_onHover=self.play_sound, arg_onHover="select")
        label_return_shadow = Label(self.window_surface, pos=(
            self.size[0] / 5 - BUTTON_WIDTH + 2, self.size[1] / 10 * 8 + 2, BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                                    text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        label_menu_name = Label(self.window_surface, pos=(self.size[0] / 2, self.size[1] / 10 * 1, AUTO_W, AUTO_H),
                                text="СОЗДАНИЕ СЕРВЕРА",
                                text_color=MENU_WHITE, font_size=TITLE_FONT_SIZE, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface,
                                       pos=(self.size[0] / 2 + 2, self.size[1] / 10 * 1 + 2, AUTO_W, AUTO_H),
                                       text="СОЗДАНИЕ СЕРВЕРА",
                                       text_color=BLACK, font_size=TITLE_FONT_SIZE, font="main_menu")

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

        button_sound_settings = Button(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2, self.size[1] / 10 * 2, BUTTON_WIDTH, BUTTON_HEIGHT), text="Звук",
                                       transparent=True, text_color=BUTTON_YELLOW,
                                       selected_text_color=BUTTON_SELECTED_YELLOW,
                                       font_size=FONT_SIZE, font="main_menu",
                                       function_onClick_list=[self.play_sound, self.load_sound_settings_group],
                                       args_list=["press", None],
                                       function_onHover=self.play_sound, arg_onHover="select")
        label_sound_settings_shadow = Label(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2 + 2, self.size[1] / 10 * 2 + 2, BUTTON_WIDTH, BUTTON_HEIGHT),
                                            text="Звук",
                                            text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        button_multi_settings = Button(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2, self.size[1] / 10 * 3, BUTTON_WIDTH, BUTTON_HEIGHT),
                                       text="Настройки подключения",
                                       transparent=True, text_color=BUTTON_YELLOW,
                                       selected_text_color=BUTTON_SELECTED_YELLOW,
                                       font_size=FONT_SIZE, font="main_menu",
                                       function_onClick_list=[self.play_sound, self.load_multi_settings_group],
                                       args_list=["press", None],
                                       function_onHover=self.play_sound, arg_onHover="select")
        label_multi_settings_shadow = Label(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2 + 2, self.size[1] / 10 * 3 + 2, BUTTON_WIDTH, BUTTON_HEIGHT),
                                            text="Настройки подключения",
                                            text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        label_menu_name = Label(self.window_surface, pos=(self.size[0] / 2, self.size[1] / 10 * 1, AUTO_W, AUTO_H),
                                text="НАСТРОЙКИ",
                                text_color=MENU_WHITE, font_size=TITLE_FONT_SIZE, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface,
                                       pos=(self.size[0] / 2 + 2, self.size[1] / 10 * 1 + 2, AUTO_W, AUTO_H),
                                       text="НАСТРОЙКИ",
                                       text_color=BLACK, font_size=TITLE_FONT_SIZE, font="main_menu")
        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                          function_list=[self.play_sound, self.load_title_group],
                                          args_list=["press", None], )
        button_return = Button(self.window_surface, pos=(
            self.size[0] / 5 - BUTTON_WIDTH, self.size[1] / 10 * 8, BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                               transparent=True, text_color=BUTTON_YELLOW, selected_text_color=BUTTON_SELECTED_YELLOW,
                               font_size=FONT_SIZE, font="main_menu",
                               function_onClick_list=[self.play_sound, self.load_title_group],
                               args_list=["press", None],
                               function_onHover=self.play_sound, arg_onHover="select")
        label_return_shadow = Label(self.window_surface, pos=(
            self.size[0] / 5 - BUTTON_WIDTH + 2, self.size[1] / 10 * 8 + 2, BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                                    text_color=BLACK, font_size=FONT_SIZE, font="main_menu")

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

        label_menu_name = Label(self.window_surface, pos=(self.size[0] / 2, self.size[1] / 10 * 1, AUTO_W, AUTO_H),
                                text="НАСТРОЙКИ ЗВУКА",
                                text_color=MENU_WHITE, font_size=TITLE_FONT_SIZE, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface,
                                       pos=(self.size[0] / 2 + 2, self.size[1] / 10 * 1 + 2, AUTO_W, AUTO_H),
                                       text="НАСТРОЙКИ ЗВУКА",
                                       text_color=BLACK, font_size=TITLE_FONT_SIZE, font="main_menu")
        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                          function_list=[self.play_sound, self.load_settings_group],
                                          args_list=["press", None], )
        button_return = Button(self.window_surface, pos=(
            self.size[0] / 5 - BUTTON_WIDTH, self.size[1] / 10 * 8, BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                               transparent=True, text_color=BUTTON_YELLOW, selected_text_color=BUTTON_SELECTED_YELLOW,
                               font_size=FONT_SIZE, font="main_menu",
                               function_onClick_list=[self.play_sound, self.load_settings_group],
                               args_list=["press", None],
                               function_onHover=self.play_sound, arg_onHover="select")
        label_return_shadow = Label(self.window_surface, pos=(
            self.size[0] / 5 - BUTTON_WIDTH + 2, self.size[1] / 10 * 8 + 2, BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                                    text_color=BLACK, font_size=FONT_SIZE, font="main_menu")

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

        label_wrong_ip = Label(self.window_surface, pos=(self.size[0] / 2 - BUTTON_WIDTH / 2,
                                                         self.size[1] / 10 * 5, BUTTON_WIDTH, BUTTON_HEIGHT,
                                                         BUTTON_WIDTH, BUTTON_HEIGHT),
                               text="Неправильный формат IP адреса!",
                               text_color=(224, 24, 24), font_size=int(FONT_SIZE * 0.75), font="main_menu")
        label_wrong_ip_shadow = Label(self.window_surface, pos=(self.size[0] / 2 - BUTTON_WIDTH / 2 + 2,
                                                                self.size[1] / 10 * 5 + 2, BUTTON_WIDTH, BUTTON_HEIGHT),
                                      text="Неправильный формат IP адреса!",
                                      text_color=BLACK, font_size=int(FONT_SIZE * 0.75), font="main_menu")
        button_is_local = Button(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2, self.size[1] / 10 * 2, BUTTON_WIDTH, BUTTON_HEIGHT),
                                 text="Локальный адрес: да",
                                 transparent=True, text_color=BUTTON_YELLOW, selected_text_color=BUTTON_SELECTED_YELLOW,
                                 font_size=FONT_SIZE, font="main_menu",
                                 function_onClick_list=[self.play_sound, change_local_remote],
                                 args_list=["press", None],
                                 function_onHover=self.play_sound, arg_onHover="select")
        label_is_local_shadow = Label(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2 + 2, self.size[1] / 10 * 2 + 2, BUTTON_WIDTH, BUTTON_HEIGHT),
                                      text="Локальный адрес: да",
                                      text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        label_client_ip = Label(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2, self.size[1] / 10 * 3, BUTTON_WIDTH, BUTTON_HEIGHT),
                                text="IP клиента:",
                                text_color=BUTTON_YELLOW, font_size=FONT_SIZE, font="main_menu")
        label_client_ip_shadow = Label(self.window_surface, pos=(
            self.size[0] / 2 - BUTTON_WIDTH / 2 + 2, self.size[1] / 10 * 3 + 2, BUTTON_WIDTH, BUTTON_HEIGHT),
                                       text="IP клиента:",
                                       text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        textbox_client_ip = TextBox(self.window_surface,
                                    pos=(self.size[0] / 2 - BUTTON_WIDTH,
                                         self.size[1] / 10 * 4, BUTTON_WIDTH * 2, BUTTON_HEIGHT * 1.5),
                                    font="main_menu",
                                    empty_text="IP адрес", font_size=FONT_SIZE)
        button_save = Button(self.window_surface, pos=(self.size[0] / 2 - BUTTON_WIDTH / 2,
                                                       self.size[1] / 10 * 6,
                                                       BUTTON_WIDTH, BUTTON_HEIGHT), text="Сохранить",
                             transparent=True, text_color=BUTTON_YELLOW, selected_text_color=BUTTON_SELECTED_YELLOW,
                             font_size=FONT_SIZE, font="main_menu",
                             function_onClick_list=[self.play_sound, save_client_ip],
                             args_list=["press", None],
                             function_onHover=self.play_sound, arg_onHover="select")
        label_save_shadow = Label(self.window_surface, pos=(self.size[0] / 2 - BUTTON_WIDTH / 2 + 2,
                                                            self.size[1] / 10 * 6 + 2,
                                                            BUTTON_WIDTH, BUTTON_HEIGHT), text="Сохранить",
                                  text_color=BLACK, font_size=FONT_SIZE, font="main_menu")
        label_menu_name = Label(self.window_surface, pos=(self.size[0] / 2, self.size[1] / 10 * 1, AUTO_W, AUTO_H),
                                text="НАСТРОЙКИ ПОДКЛЮЧЕНИЯ",
                                text_color=MENU_WHITE, font_size=TITLE_FONT_SIZE, font="main_menu")
        label_menu_name_shadow = Label(self.window_surface,
                                       pos=(self.size[0] / 2 + 2, self.size[1] / 10 * 1 + 2, AUTO_W, AUTO_H),
                                       text="НАСТРОЙКИ ПОДКЛЮЧЕНИЯ",
                                       text_color=BLACK, font_size=TITLE_FONT_SIZE, font="main_menu")
        buttontrigger_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                          function_list=[self.play_sound, self.load_settings_group],
                                          args_list=["press", None], )
        button_return = Button(self.window_surface, pos=(
            self.size[0] / 5 - BUTTON_WIDTH, self.size[1] / 10 * 8, BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                               transparent=True, text_color=BUTTON_YELLOW, selected_text_color=BUTTON_SELECTED_YELLOW,
                               font_size=FONT_SIZE, font="main_menu",
                               function_onClick_list=[self.play_sound, self.load_settings_group],
                               args_list=["press", None],
                               function_onHover=self.play_sound, arg_onHover="select")
        label_return_shadow = Label(self.window_surface, pos=(
            self.size[0] / 5 - BUTTON_WIDTH + 2, self.size[1] / 10 * 8 + 2, BUTTON_WIDTH, BUTTON_HEIGHT), text="Назад",
                                    text_color=BLACK, font_size=FONT_SIZE, font="main_menu")

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
            self.window_surface.fill(MAIN_MENU_BACKGROUND_COLOR)

            # Обработка событий:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                # TODO: избавиться от этого костыля:
                skip_objects = False
                if self.any_popup is not None:
                    if (return_code := self.any_popup.handle_event(event)) is not None:
                        if return_code == SKIP_EVENT:
                            skip_objects = True
                if not skip_objects:
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
