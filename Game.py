import socketserver
import threading
from typing import Dict

import pygame
from pygame.surface import Surface

from Consts import targetFPS, DARK_GREY, BLACK, MOVE_RIGHT, SHOOT, MOVE_LEFT, MOVE_DOWN, MOVE_UP, \
    CHANGES_DEBUG, CHAT_BUTTON, FOLD_UNFOLD_CHATLOG
from Files import ImageLoader
from Images.Tileset import Tileset
from Multiplayer.ChatHistory import ChatHistory
from UI.ConstPopups import add_server_started_popupbox, remove_server_started_popupbox, add_chat
from UI.Ingame_GUI import GUI
from UI.MenuObjects.PopupBox import PopupBox
from Multiplayer.Senders import DataSenderServerSide, DataSenderClientSide, EVENT_SERVER_STOP, EVENT_CLIENT_PLAYER_QUIT, \
    EVENT_SERVER_GAME_STARTED, EVENT_CLIENT_SEND_CHAT_MESSAGE
from Multiplayer.UDPHandlers import MyUDPHandlerClientSide, MyUDPHandlerServerSide
from World.World import World


class Game:
    clientside_sender: DataSenderClientSide = None  # Отправители пакетов
    serverside_sender: DataSenderServerSide = None
    clientside_server: socketserver.UDPServer = None
    serverside_server: socketserver.UDPServer = None

    window_surface: Surface = None  # Основная поверхность

    is_server: bool = None
    is_connected: bool = None  # Подключён ли клиент к серверу
    multi: bool = None  # Сетевой режим или нет?
    game_started: bool = None  # Флаг начала игры
    game_running: bool = None  # Флаг запущенной игры

    connect_to_ip: str = None  # Адрес, к которому будет пытаться подключиться клиент
    client_ip: str = None  # Адрес, на котором расположен клиент
    client_port: int = None  # Порт клиента
    server_ip: str = None  # Адрес, на котором расположен сервер

    any_popup_box: PopupBox = None  # Любой PopupBox должен быть здесь
    gui: GUI = None  # Весь GUI игры находится здесь.
    need_to_return_to_menu: bool = False  # Установка этого флага позволяет вернуться в меню после завершения игры

    button_actions: Dict[str, tuple] = None  # Словарь "кнопка - дейсвтие", который используется в process_inputs

    chat_history: ChatHistory = None  # История чата

    def __init__(self, window_surface, is_server, multi, start_map_id: int = None,
                 connect_to_ip: str = None, server_ip: str = None, client_ip: str = None,
                 client_port: int = None, dedicated: bool = None):
        """
        Если multi = False, значит никакой работы с сервером и клиентом проводиться не будет.
        Елси multi = True:
            Если is_server = True, значит будет запущен сервер.
            Если is_server = False, значит будет запущен клиент.
        """
        self.window_surface = window_surface

        minimal_dimention = min(self.window_surface.get_width(),
                                self.window_surface.get_height())  # Наименьшая сторона окна
        self.game_surface = pygame.Surface((minimal_dimention, minimal_dimention))

        # Выравнивание по центру:
        self.game_rect = pygame.Rect(self.window_surface.get_width() / 2 - minimal_dimention / 2,
                                     self.window_surface.get_height() / 2 - minimal_dimention / 2,
                                     minimal_dimention, minimal_dimention)

        self.clock = pygame.time.Clock()
        self.imageloader = ImageLoader()
        self.tileset = Tileset(64, 64, self.imageloader.get_image_by_name("tileset.png"))

        self.chat_history = ChatHistory()
        self.gui = GUI(self)

        self.game_running = True

        self.is_server = is_server
        self.multi = multi

        self.world = World(self.game_surface, self.tileset, True)
        if self.is_server and multi:
            # Запуск сервера для мультиплеера
            self.server_ip = server_ip
            self.world.set_ready_for_server()
            self.serverside_sender = DataSenderServerSide(self)
            self.create_serverside_server()
            self.world.load_world_map(start_map_id)
            self.world.clear_changes()
            self.server_waiting_started = False  # Флаг, который принимает значение True после первой
            # попытки ожидания клиентов.
            self.set_default_buttons(server=True)
        elif not self.is_server and self.multi:
            # Запуск клиента для мультиплеера
            self.clientside_sender = DataSenderClientSide(self)
            self.client_ip = client_ip
            self.client_port = client_port
            self.create_clientside_server()
            self.connect_to_ip = connect_to_ip
            self.is_connected = False
            self.game_started = False
            self.has_already_tried_to_connect = False
            self.server_button_pressed = False  # Флаг для однократной отработки нажатия кнопки подключения
            self.set_default_buttons(server=False)
        elif not multi:
            # Запуск одиночки
            self.world.load_world_map(start_map_id)
            self.world.spawn_player()
            self.world.center_camera_on_player()
            self.game_started = True  # TODO: Временно
            self.set_default_buttons(server=True)

        self.main_cycle()  # Основной цикл

    def wait_for_players(self, num_of_player_to_start: int = 2):

        def check_players_ready():
            for client in self.serverside_sender.clients:
                if not client.ready:
                    # Если хотя бы один клиент не готов
                    return False
            return True

        if self.serverside_sender.clients.__len__() < num_of_player_to_start:
            return
        if not check_players_ready():
            # Пока игроки не будут готовы, ждём.
            return
        # Как только к нам подключилост достаточное количество игроков, спавним их и центруем камеру
        self.serverside_sender.send_event(EVENT_SERVER_GAME_STARTED)
        for (i, player) in enumerate(self.serverside_sender.clients):
            self.world.spawn_player(i)
        self.world.center_camera_on_player()

        remove_server_started_popupbox(self)
        self.game_started = True

    def create_clientside_server(self):
        class MyUDPHandlerClientSideWithObject(MyUDPHandlerClientSide):  # Костыль(?)
            parent_game = self  # Передаю ссылку на объект
            port = self.client_port

        HOST, PORT = self.client_ip, self.client_port
        # Созадём севрер
        self.clientside_server = socketserver.UDPServer((HOST, PORT), MyUDPHandlerClientSideWithObject)
        server_thread = threading.Thread(target=self.clientside_server.serve_forever)  # Создаём поток
        server_thread.setDaemon(True)
        server_thread.start()  # Запускаем поток

        print("Clientside server was started")

    def create_serverside_server(self):
        class MyUDPHandlerServerSideWithObject(MyUDPHandlerServerSide):  # Костыль(?)
            parent_game = self  # Передаю ссылку на объект

        HOST, PORT = self.server_ip, 9998
        self.serverside_server = socketserver.UDPServer((HOST, PORT),
                                                        MyUDPHandlerServerSideWithObject)  # Созадём севрер
        server_thread = threading.Thread(target=self.serverside_server.serve_forever)  # Создаём поток
        server_thread.setDaemon(True)
        server_thread.start()  # Запускаем поток

        print("Serverside server was started")

    def set_default_buttons(self, server):
        self.button_actions = dict()
        if server:
            # Если задаём для сервера или одиночки
            self.button_actions[MOVE_RIGHT] = ((lambda: self.button_move_player("RIGHT", False)),
                                               (lambda: self.reset_move_player_direction("RIGHT", False)))
            self.button_actions[MOVE_LEFT] = ((lambda: self.button_move_player("LEFT", False)),
                                              (lambda: self.reset_move_player_direction("LEFT", False)))
            self.button_actions[MOVE_UP] = ((lambda: self.button_move_player("UP", False)),
                                            (lambda: self.reset_move_player_direction("UP", False)))
            self.button_actions[MOVE_DOWN] = ((lambda: self.button_move_player("DOWN", False)),
                                              (lambda: self.reset_move_player_direction("DOWN", False)))
            self.button_actions[SHOOT] = ((lambda: self.world.create_bullet(self.world.players[0])),
                                          None)
        else:
            # TODO: Избавиться от этой переменной и класса.
            class MoveVar:
                direction: str = None
            move_var = MoveVar()  # Переменная для хранения текущего направления движения танка

            # Если задаём для клиента
            self.button_actions[MOVE_RIGHT] = ((lambda: self.button_move_player("RIGHT", True, local_var=move_var)),
                                    (lambda: self.reset_move_player_direction("RIGHT", True, local_var=move_var)))
            self.button_actions[MOVE_LEFT] = ((lambda: self.button_move_player("LEFT", True, local_var=move_var)),
                                    (lambda: self.reset_move_player_direction("LEFT", True, local_var=move_var)))
            self.button_actions[MOVE_UP] = ((lambda: self.button_move_player("UP", True, local_var=move_var)),
                                    (lambda: self.reset_move_player_direction("UP", True, local_var=move_var)))
            self.button_actions[MOVE_DOWN] = ((lambda: self.button_move_player("DOWN", True, local_var=move_var)),
                                    (lambda: self.reset_move_player_direction("DOWN", True, local_var=move_var)))
            self.button_actions[SHOOT] = ((lambda: self.clientside_sender.send_button("SHOOT")),
                                          None)
            self.button_actions[CHAT_BUTTON] = ((lambda: add_chat(self)),
                                                None)
            self.button_actions[FOLD_UNFOLD_CHATLOG] = (self.gui.change_chatlog_action,
                                                        self.gui.reset_button)

    def process_inputs(self) -> None:
        """
        Обрабатывает все нажатые клавиши, выполняя необходимые действия.
        """
        # Кнопка в self.button_actions должна храниться так:
        # "код клавиши из PyGame": ("действие при нажатой", "действие при ненажатой")
        # Любое из действий может быть None!
        # Действие "NONE" может иметь только одно действие "при ненажатой".

        if self.any_popup_box is not None:
            if self.any_popup_box.blocking:
                # Если есть блокирующий popup_box, ничего не делаем.
                return

        keyboard_pressed = pygame.key.get_pressed()
        any_pressed = False  # Была ли нажата хоть одна клавиша

        for button in self.button_actions:
            if keyboard_pressed[button]:  # Если указанная клавиша нажата, выполняется действие при нажатии
                if self.button_actions[button][0] is not None:
                    self.button_actions[button][0]()
            else:  # Если указанная клавиша не нажата, выполняется действие при ненажатой
                if self.button_actions[button][1] is not None:
                    self.button_actions[button][1]()

        if not any_pressed:
            if "NONE" in self.button_actions and self.button_actions["NONE"][1] is not None:
                self.button_actions["NONE"][1]()  # Действие при отсутствии нажатий

    def button_move_player(self, direction, remote, player_id=0, local_var=None) -> None:
        """
        Вызывается, когда нажата кнопка движения.
        Либо посылает на сервер указание, что нажали определённую кнопку движения, либо двигает 0-ого игрока
        (в случае сервера или одиночки).
        :param local_var: Переменная, необходимая в случае remote=True,
         туда записывается последнее направление движения.
        :param player_id: Айди игрока, для которого это выполняется.
        :param direction: Направление движения
        :param remote: Если True - нужно отправлять данные на сервер, если False - локальные изменения.
        """
        if remote:
            # Если мы отправляем движение на сервер
            if local_var.direction is None or local_var.direction == direction:
                self.clientside_sender.send_button("MOVE_" + direction)

                # Смотри класс MoveVar в методе set_default_buttons:
                local_var.direction = direction
        else:
            current_player = self.world.players[player_id]
            # Если мы сами себе сервер
            if current_player.last_pressed_direction is None or current_player.last_pressed_direction == direction:
                self.world.move_player_to(player_id, direction)
                current_player.last_pressed_direction = direction

    def reset_move_player_direction(self, direction, remote, player_id=0, local_var=None) -> None:
        """
        Сбрасывает кнопку движения для игрока в локальной игре.
        :param local_var: Эта переменная используется при remote=True. Содержит текущее направление движения.
        :param remote: Если True - нужно применять доп.логику для сохранения состояния,
         если False - локальные изменения.
        :param player_id: Айди игрока, для которого это выполняется.
        :param direction: Направление, которое нужно сбросить.
        """
        if remote:
            if local_var.direction == direction:
                local_var.direction = None
        else:
            if self.world.players[player_id].last_pressed_direction == direction:
                self.world.players[player_id].last_pressed_direction = None

    def send_chat_message(self, msg_str: str):
        self.clientside_sender.send_event(EVENT_CLIENT_SEND_CHAT_MESSAGE, msg_str)

    def main_cycle(self):
        while self.game_running:
            self.clock.tick(targetFPS)  # Требуемый FPS и соответствующая задержка
            self.window_surface.fill(DARK_GREY)
            self.game_surface.fill(BLACK)

            # Обработка событий:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop_game()
                # Обработка всплывающих окон:
                if self.any_popup_box is not None:
                    self.any_popup_box.handle_event(event)
            # keyboard_pressed = pygame.key.get_pressed()

            if self.is_server and not self.game_started:
                if not self.server_waiting_started:
                    add_server_started_popupbox(self)
                    self.server_waiting_started = True
                # Пока сервер не стартанул
                self.wait_for_players()

            if self.game_started:
                self.process_inputs()

            # Попытка подключиться к серверу при запуске клиента:
            if not self.is_server and not self.is_connected and self.multi and not self.has_already_tried_to_connect:
                self.clientside_sender.ask_for_ok(self.connect_to_ip)
                self.has_already_tried_to_connect = True

            # if not self.world.check_if_player_is_alive():
            #     self.game_over(0)

            # if not self.world.check_if_base_is_alive():
            #     self.game_over(1)

            if self.game_started:
                self.world.draw()

            if self.is_server or not self.multi:
                self.world.act()
                # Спавн врагов:
                if self.world.enemy_spawn_timer.is_ready() and self.world.enemies_remains > 0:
                    if self.world.create_enemy():
                        # Если получилось заспавнить врага
                        self.world.enemies_remains -= 1
                        self.world.enemy_spawn_timer.reset()

                # Изменения в мире:
                if (changes := self.world.get_changes()).__len__() > 0 and self.multi:
                    if CHANGES_DEBUG:
                        print(changes)
                    self.serverside_sender.send_changes()
                self.world.clear_changes()

            self.window_surface.blit(self.game_surface, self.game_rect)

            if self.gui is not None:
                self.gui.draw()
                self.gui.update()

            # Отрисовка и обновление popupBox-а:
            if self.any_popup_box is not None:
                self.any_popup_box.draw()
                self.any_popup_box.update()

            pygame.display.update()

    def game_over(self, game_over_id):
        game_overs = [
            "Game over! Your tank was destroyed!",
            "Game over! Your base was destroyed!"
        ]
        print(game_overs[game_over_id])
        self.game_running = False

    def stop_game(self, send_to_server: bool = True):
        """
        Останавилвает выполнение игры, посылает на сервер сигнал об отключении клиента, если необходимо.
        """
        if self.multi and send_to_server:
            if self.is_server:
                # Если сервер
                self.serverside_sender.send_event(EVENT_SERVER_STOP)
                self.serverside_server.shutdown()
                self.serverside_server.server_close()
            else:
                # Если клиент
                self.clientside_sender.send_event(EVENT_CLIENT_PLAYER_QUIT)
                self.clientside_server.shutdown()
                self.clientside_server.server_close()
        else:
            # Если одиночка
            pass
        self.game_running = False

    def return_to_menu(self, send_to_server=False):
        self.need_to_return_to_menu = True
        self.stop_game(send_to_server)
