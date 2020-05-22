import socketserver
import threading
from time import sleep

import pygame
from pygame.surface import Surface

from Consts import targetFPS, DARK_GREY, BLACK, MOVE_RIGHT, SHOOT, MOVE_LEFT, MOVE_DOWN, MOVE_UP, \
    CHANGES_DEBUG
from Files import ImageLoader
from Images.Tileset import Tileset
from Menu.ConstPopups import add_server_started_popupbox, remove_server_started_popupbox
from Menu.MenuObjects.PopupBox import PopupBox
from Multiplayer.Senders import DataSenderServerSide, DataSenderClientSide, EVENT_SERVER_STOP, EVENT_CLIENT_PLAYER_QUIT, \
    EVENT_SERVER_GAME_STARTED
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

    any_popup_box: PopupBox = None  # PopupBox должен быть здесь
    need_to_return_to_menu: bool = False  # Установка этого флага позволяет вернуться в меню после завершения игры

    def __init__(self, window_surface, is_server, multi, start_map_id: int = None,
                 connect_to_ip: str = None, server_ip: str = None, client_ip: str = None,
                 client_port: int = None):
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
            # Флаг, который принимает значение True после первой попытки ожидания клиентов.
            self.server_waiting_started = False
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

        if not multi:
            # Запуск одиночки
            self.world.load_world_map(start_map_id)
            self.world.spawn_player()
            self.world.center_camera_on_player()
            self.game_started = True  #TODO: Временно

        self.server_button_pressed = False  # Флаг для однократной отработки нажатия кнопки подключения

        self.last_moved_direction = None

        if self.is_server and multi:
            self.world.load_world_map(start_map_id)
            self.world.clear_changes()

        self.main_cycle()

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
            keyboard_pressed = pygame.key.get_pressed()

            # Перехватываем управление для popupbox-а:
            if self.any_popup_box is None:
                # Движение игрока
                if self.is_server or not self.multi:
                    if keyboard_pressed[pygame.K_RIGHT]:
                        if self.last_moved_direction is None or self.last_moved_direction == "RIGHT":
                            self.world.move_player_to(0, "RIGHT")
                            self.last_moved_direction = "RIGHT"
                    elif self.last_moved_direction == "RIGHT":
                        self.last_moved_direction = None
                    if keyboard_pressed[pygame.K_UP]:
                        if self.last_moved_direction is None or self.last_moved_direction == "UP":
                            self.world.move_player_to(0, "UP")
                            self.last_moved_direction = "UP"
                    elif self.last_moved_direction == "UP":
                        self.last_moved_direction = None
                    if keyboard_pressed[pygame.K_DOWN]:
                        if self.last_moved_direction is None or self.last_moved_direction == "DOWN":
                            self.world.move_player_to(0, "DOWN")
                            self.last_moved_direction = "DOWN"
                    elif self.last_moved_direction == "DOWN":
                        self.last_moved_direction = None
                    if keyboard_pressed[pygame.K_LEFT]:
                        if self.last_moved_direction is None or self.last_moved_direction == "LEFT":
                            self.world.move_player_to(0, "LEFT")
                            self.last_moved_direction = "LEFT"
                    elif self.last_moved_direction == "LEFT":
                        self.last_moved_direction = None

                    # Стрельба
                    if keyboard_pressed[pygame.K_SPACE]:
                        self.world.create_bullet(self.world.players[0])
                else:
                    if keyboard_pressed[MOVE_RIGHT]:
                        if self.last_moved_direction is None or self.last_moved_direction == "RIGHT":
                            self.clientside_sender.send_button("MOVE_RIGHT")
                            self.last_moved_direction = "RIGHT"
                    elif self.last_moved_direction == "RIGHT":
                        self.last_moved_direction = None
                    if keyboard_pressed[MOVE_UP]:
                        if self.last_moved_direction is None or self.last_moved_direction == "UP":
                            self.clientside_sender.send_button("MOVE_UP")
                            self.last_moved_direction = "UP"
                    elif self.last_moved_direction == "UP":
                        self.last_moved_direction = None
                    if keyboard_pressed[MOVE_DOWN]:
                        if self.last_moved_direction is None or self.last_moved_direction == "DOWN":
                            self.clientside_sender.send_button("MOVE_DOWN")
                            self.last_moved_direction = "DOWN"
                    elif self.last_moved_direction == "DOWN":
                        self.last_moved_direction = None
                    if keyboard_pressed[MOVE_LEFT]:
                        if self.last_moved_direction is None or self.last_moved_direction == "LEFT":
                            self.clientside_sender.send_button("MOVE_LEFT")
                            self.last_moved_direction = "LEFT"
                    elif self.last_moved_direction == "LEFT":
                        self.last_moved_direction = None

                    # Стрельба
                    if keyboard_pressed[SHOOT]:
                        self.clientside_sender.send_button("SHOOT")

            # Попытка подключиться к серверу при запуске клиента:
            if not self.is_server and not self.is_connected and self.multi and not self.has_already_tried_to_connect:
                self.clientside_sender.ask_for_ok(self.connect_to_ip)
                self.has_already_tried_to_connect = True

            # if not self.world.check_if_player_is_alive():
            #     self.game_over(0)

            # if not self.world.check_if_base_is_alive():
            #     self.game_over(1)

            if self.is_server and not self.game_started:
                if not self.server_waiting_started:
                    add_server_started_popupbox(self)
                    self.server_waiting_started = True
                # Пока сервер не стартанул
                self.wait_for_players()

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
