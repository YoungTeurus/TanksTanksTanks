import socketserver
import threading

import pygame

from Consts import targetFPS, DARK_GREY, BLACK, MOVE_RIGHT, SHOOT, MOVE_LEFT, MOVE_DOWN, MOVE_UP, \
    CHANGES_DEBUG
from Files import ImageLoader
from Images.Tileset import Tileset
from Menu.MenuObjects.PopupBox import PopupBox
from Multiplayer.Senders import DataSenderServerSide, DataSenderClientSide, EVENT_SERVER_STOP, EVENT_PLAYER_QUIT
from Multiplayer.UDPHandlers import MyUDPHandlerClientSide, MyUDPHandlerServerSide
from World.World import World


class Game:
    clientside_sender: DataSenderClientSide = None  # Отправители пакетов
    serverside_sender: DataSenderServerSide = None
    clientside_server: socketserver.UDPServer = None
    serverside_server: socketserver.UDPServer = None

    window_surface = None  # Основная поверхность

    is_server: bool = None
    is_connected: bool = None  # Подключён ли клиент к серверу
    multi = None  # Сетевой режим или нет?
    game_running = None  # Флаг запущенной игры

    connect_to_ip: str = None  # Адрес, к которому будет пытаться подключиться клиент
    client_ip: str = None  # Адрес, на котором расположен клиент
    client_port: int = None  # Порт клиента
    server_ip: str = None  # Адрес, на котором расположен сервер

    any_popup_box: PopupBox = None  # PopupBox должен быть здесь
    need_to_return_to_menu: bool = False  # Уставнока этого флага позволяет вернуться в меню после завершения игры

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
        elif not self.is_server and self.multi:
            # Запуск клиента для мультиплеера
            self.clientside_sender = DataSenderClientSide(self)
            self.client_ip = client_ip
            self.client_port = client_port
            self.create_clientside_server()
            self.connect_to_ip = connect_to_ip
            self.is_connected = False

        if not multi:
            # Запуск одиночки
            self.world.load_world_map(start_map_id)
            self.world.spawn_player()
            self.world.center_camera_on_player()

        self.server_button_pressed = False  # Флаг для однократной отработки нажатия кнопки подключения

        self.last_moved_direction = None

        if self.is_server and multi:
            self.world.load_world_map(start_map_id)
            self.world.clear_changes()
            # Если мы сервер, то мы ничего не делаем до тех пор, пока не подключится хотя бы 1 клиент
            # TODO: сделать проверку на количество подключённых игроков
            while self.serverside_sender.clients.__len__() < 2 and self.game_running:
                # Обработка событий:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.stop_game()
            # Как только к нам подключились, спавним игрока и центруем на нём камеру
            # self.world.spawn_player()
            # self.world.center_camera_on_player()

        self.main_cycle()

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
                    self.game_running = False
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

            # Тестовая попытка подключиться к серверу:
            if not self.is_server and not self.is_connected and self.multi:
                self.clientside_sender.ask_for_ok(self.connect_to_ip)
                self.is_connected = True

            # if not self.world.check_if_player_is_alive():
            #     self.game_over(0)

            # if not self.world.check_if_base_is_alive():
            #     self.game_over(1)

            self.world.draw()

            if self.is_server or not self.multi:
                self.world.act()
                # Спавн врагов:
                if self.world.enemy_spawn_timer.is_ready():
                    if self.world.create_enemy():
                        # Если получилось заспавнить врага
                        self.world.enemies_remains -= 1
                        self.world.enemy_spawn_timer.reset()

                # Изменения в мире:
                if (changes := self.world.get_changes()).__len__() > 0 and self.multi:
                    if CHANGES_DEBUG:
                        print(changes)
                    self.serverside_sender.send_changes()  # Вместо "localhost" - все клиенты
                self.world.clear_changes()

            self.window_surface.blit(self.game_surface, self.game_rect)

            # Отрисовка и обновление popupBox-а:
            if self.any_popup_box is not None:
                self.any_popup_box.draw()
                self.any_popup_box.update()

            pygame.display.update()

            # if not self.is_server:
            #     self.check_id_timer.tick()
            #     if self.check_id_timer.is_ready():
            #         if not self.world.check_if_all_world_ids_are_correct():
            #             raise Exception("IDs are not correct!")

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
            else:
                # Если клиент
                self.clientside_sender.send_event(EVENT_PLAYER_QUIT)
        else:
            # Если одиночка
            pass
        self.game_running = False

    def return_to_menu(self):
        self.need_to_return_to_menu = True
        self.stop_game(send_to_server=False)
