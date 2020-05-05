import random
import socketserver

import pygame

from Consts import targetFPS, DARK_GREY, BLACK, MOVE_RIGHT, SHOOT, MOVE_LEFT, MOVE_DOWN, MOVE_UP, CLIENT_IP, \
    CONNECT_TO_IP, CHANGES_DEBUG
from Files import ImageLoader
from Images.Tileset import Tileset
from Multiplayer.Senders import DataSenderServerSide, DataSenderClientSide
from Multiplayer.UDPHandlers import MyUDPHandlerClientSide, MyUDPHandlerServerSide
from World.Timer import Timer
from World.World import World
import threading


class Game:
    clientside_sender: DataSenderClientSide = None  # Отправители пакетов
    serverside_sender: DataSenderServerSide = None
    clientside_server: socketserver.UDPServer = None
    serverside_server: socketserver.UDPServer = None

    clientside_server_port = None  # Порт для подключения сервера к клиенту

    window_surface = None  # Основная поверхность

    is_server = None
    game_running = None  # Флаг запущенной игры

    # check_id_timer = None

    def __init__(self, window_surface, is_server):
        self.window_surface = window_surface

        minimal_dimention = min(self.window_surface.get_width(),
                                self.window_surface.get_height())  # Наименьшая сторона окна
        self.game_surface = pygame.Surface((minimal_dimention, minimal_dimention))
        # Выравнивание по левому краю:
        # game_rect = pygame.Rect(0,
        #                         0,
        #                         minimal_dimention, minimal_dimention)
        # Выравнивание по центру:
        self.game_rect = pygame.Rect(self.window_surface.get_width() / 2 - minimal_dimention / 2,
                                     self.window_surface.get_height() / 2 - minimal_dimention / 2,
                                     minimal_dimention, minimal_dimention)

        pygame.display.set_caption("TANK! TANK! TANK!")
        self.clock = pygame.time.Clock()
        self.imageloader = ImageLoader()
        self.tileset = Tileset(64, 64, self.imageloader.get_image_by_name("tileset.png"))

        self.game_running = True

        self.is_server = is_server

        if self.is_server:
            self.world = World(self.game_surface, self.tileset, True)
            self.world.set_ready_for_server()
            self.serverside_sender = DataSenderServerSide(self)
            self.create_serverside_server()
        else:
            self.world = World(self.game_surface, self.tileset, True)
            self.clientside_sender = DataSenderClientSide(self)
            self.clientside_server_port = random.randint(9999, 60000)
            self.create_clientside_server(self.clientside_server_port)
            # self.check_id_timer = Timer(100)

        if self.is_server:
            self.world.setup_world()
            self.world.clear_changes()

        self.server_button_pressed = False  # Флаг для однократной отработки нажатия кнопки подключения

        self.last_moved_direction = None

        if self.is_server:
            # Если мы сервер, то мы ничего не делаем до тех пор, пока не подключится хотя бы 1 клиент
            # TODO: сделать проверку на количество подключённых игроков
            while self.serverside_sender.clients.__len__() < 2 and self.game_running:
                # Обработка событий:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.game_running = False
            # Как только к нам подключились, спавним игрока и центруем на нём камеру
            # self.world.spawn_player()
            # self.world.center_camera_on_player()

        self.main_cycle()

    def create_clientside_server(self, client_port):
        class MyUDPHandlerClientSideWithObject(MyUDPHandlerClientSide):  # Костыль(?)
            parent_game = self  # Передаю ссылку на объект
            port = client_port

        HOST, PORT = CLIENT_IP, client_port
        # Созадём севрер
        self.clientside_server = socketserver.UDPServer((HOST, PORT), MyUDPHandlerClientSideWithObject)
        server_thread = threading.Thread(target=self.clientside_server.serve_forever)  # Создаём поток
        server_thread.setDaemon(True)
        server_thread.start()  # Запускаем поток

        print("Clientside server was started")

    def create_serverside_server(self):
        class MyUDPHandlerServerSideWithObject(MyUDPHandlerServerSide):  # Костыль(?)
            parent_game = self  # Передаю ссылку на объект

        HOST, PORT = CLIENT_IP, 9998
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
            keyboard_pressed = pygame.key.get_pressed()

            # Движение игрока
            if self.is_server:
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
            if not self.is_server:
                if keyboard_pressed[pygame.K_0]:
                    if not self.server_button_pressed:
                        self.clientside_sender.ask_for_ok(CONNECT_TO_IP)
                        self.server_button_pressed = True
                else:
                    self.server_button_pressed = False

            # if not self.world.check_if_player_is_alive():
            #     self.game_over(0)

            # if not self.world.check_if_base_is_alive():
            #     self.game_over(1)

            self.world.draw()
            if self.is_server:
                self.world.act()
                # Спавн врагов:
                if self.world.enemy_spawn_timer.is_ready():
                    if self.world.create_enemy():
                        # Если получилось заспавнить врага
                        self.world.enemies_remains -= 1
                        self.world.enemy_spawn_timer.reset()

                # Изменения в мире:
                if (changes := self.world.get_changes()).__len__() > 0:
                    if CHANGES_DEBUG:
                        print(changes)
                    self.serverside_sender.send_changes()  # Вместо "localhost" - все клиенты
                self.world.clear_changes()

            self.window_surface.blit(self.game_surface, self.game_rect)

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
