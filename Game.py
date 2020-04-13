import json
import logging
import socket
import socketserver

import pygame

from Consts import targetFPS, DARK_GREY, BLACK
from Files import ImageLoader
from Images.Tileset import Tileset
from World.World import World
import threading


class MyUDPHandlerClientSide(socketserver.BaseRequestHandler):
    """
    Данный класс содержит handle, принимающий информацию отслылаемую сервером, то есть распарсивает полученный json и
    воздейсвтует на игру.
    """
    parent_game = None

    def handle(self):
        data = self.request[0].decode()  # Вытаскиваем data
        data_dict = json.loads(data)  # Делаем из этого словарь
        print("{} wrote: ".format(self.client_address[0]), end="")
        print(data_dict)  # Вывод дебаг-информации

        if data_dict["type"] == "ok":
            # Если сервер отправил ok
            self.parent_game.clientside_sender.server = self.client_address[0]  # Запоминаем IP сервера
            self.parent_game.clientside_sender.connect_to_server()  # Пробуем подключиться к серверу
        elif data_dict["type"] == "load_world":
            # Если сервер сказал подгрузить карту
            self.parent_game.world.load_map(0)  # Грузим карту
        elif data_dict["type"] == "changes":
            # Если сервер прислал текущие изменения
            self.parent_game.world.process_many_changes(data_dict["changes"])

        # self.parent_game.world.process_change(inp)

class MyUDPHandlerServerSide(socketserver.BaseRequestHandler):
    """
    Данный класс содержит handle, принимающий информацию отслылаемую сервером, то есть распарсивает полученный json и
    воздейсвтует на игру.
    """
    parent_game = None

    def handle(self):
        data = self.request[0].decode()  # Вытаскиваем data
        data_dict = json.loads(data)  # Делаем из этого словарь
        print("{} wrote: ".format(self.client_address[0]), end="")
        print(data_dict)  # Вывод дебаг-информации

        if data_dict["type"] == "ask_for_ok":
            # Если клиент спрашивает об OK-ее
            self.parent_game.serverside_sender.send_ok(self.client_address[0])  # Отправляем ему OK
        elif data_dict["type"] == "connect":
            # Если клиент хочет подключиться
            if self.client_address[0] not in self.parent_game.serverside_sender.clients:  # Если этого IP ещё не было, заносим его в список клиентов
                self.parent_game.serverside_sender.clients.append(self.client_address[0])  # Заносим IP-шник отправителю
            # Говорим клиенту подгрузить такую-то карту
            self.parent_game.serverside_sender.send_load_world(self.client_address[0],
                                                               self.parent_game.world.world_map.map_id)
            # TODO: отправлять карту клиенту


class DataSenderServerSide:
    """
    Данный класс отправляет клиентам необходимые данные
    """
    parent_game = None
    clients = []

    def __init__(self, parent_game):
        self.parent_game = parent_game

    def send_ok(self, ip):
        HOST, PORT = ip, 9999
        data_dict = dict()
        data_dict["type"] = "ok"
        data = json.dumps(data_dict)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), (HOST, PORT))
        print("Sent:     {}".format(data))

    def send_load_world(self, ip, world_id):
        HOST, PORT = ip, 9999
        data_dict = dict()
        data_dict["type"] = "load_world"
        data_dict["world_id"] = world_id
        data = json.dumps(data_dict)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), (HOST, PORT))
        print("Sent:     {}".format(data))

    def send_changes(self):
        for client_ip in self.clients:
            HOST, PORT = client_ip, 9999
            data_dict = dict()
            data_dict["type"] = "changes"
            changes = dict()
            i = 0
            for change in self.parent_game.world.get_changes():
                changes[i] = change
                i += 1
            data_dict["changes"] = changes
            data = json.dumps(data_dict)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(data.encode(), (HOST, PORT))
            print("Sent:     {}".format(data))


class DataSenderClientSide:
    """
        Данный класс отправляет серверу необходимые данные
    """
    parent_game = None
    server = None

    def __init__(self, parent_game):
        self.parent_game = parent_game

    def set_server(self, ip):
        self.server = ip

    def ask_for_ok(self, ip):
        HOST, PORT = ip, 9998
        data_dict = dict()
        data_dict["type"] = "ask_for_ok"
        data = json.dumps(data_dict)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), (HOST, PORT))
        print("Sent:     {}".format(data))

    def connect_to_server(self):
        HOST, PORT = self.server, 9998
        data_dict = dict()
        data_dict["type"] = "connect"
        data = json.dumps(data_dict)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), (HOST, PORT))
        print("Sent:     {}".format(data))


class Game:
    # clientside_server = None  # Сервера
    # serverside_server = None
    clientside_sender = None  # Отправители пакетов
    serverside_sender = None

    is_server = None

    def __init__(self, window_surface, is_server):
        logging.basicConfig(filename="log.log", level=logging.INFO, filemode="w")
        self.window_surface = window_surface  # Основная поверхность

        minimal_dimention = min(self.window_surface.get_width(),
                                self.window_surface.get_height())  # Наименьшая сторона окна
        self.game_surface = pygame.Surface((minimal_dimention, minimal_dimention))
        # Выравнивание по левому краю
        # game_rect = pygame.Rect(0,
        #                         0,
        #                         minimal_dimention, minimal_dimention)
        # Выравнивание по центру
        self.game_rect = pygame.Rect(self.window_surface.get_width() / 2 - minimal_dimention / 2,
                                     self.window_surface.get_height() / 2 - minimal_dimention / 2,
                                     minimal_dimention, minimal_dimention)

        pygame.display.set_caption("TANK! TANK! TANK!")
        self.clock = pygame.time.Clock()
        self.imageloader = ImageLoader()
        self.tileset = Tileset(64, 64, self.imageloader.get_image_by_name("tileset.png"))

        self.game_running = True  # Флаг продолжения игры

        self.is_server = is_server

        if self.is_server:
            self.world = World(self.game_surface, self.tileset, True)
            self.world.set_ready_for_server()
            self.serverside_sender = DataSenderServerSide(self)
            self.create_serverside_server()
        else:
            self.world = World(self.game_surface, self.tileset, True)
            self.clientside_sender = DataSenderClientSide(self)
            self.create_clientside_server()

        if self.is_server:
            self.world.setup_world()
            self.world.clear_changes()

        self.server_button_pressed = False  # Флаг для однократной отработки нажатия кнопки подключения

        self.last_moved_direction = None

        if self.is_server:
            # Если мы сервер, то мы ничего не делаем до тех пор, пока не подключится хотя бы 1 клиент
            while self.serverside_sender.clients.__len__() <= 0:
                pass
            # Как только к нам подключились, спавним игрока и центруем на нём камеру
            self.world.spawn_player()
            self.world.center_camera_on_player()

        self.main_cycle()

    def create_clientside_server(self):
        class MyUDPHandlerClientSideWithObject(MyUDPHandlerClientSide):  # Костыль(?)
            parent_game = self  # Передаю ссылку на объект

        HOST, PORT = "localhost", 9999
        self.clientside_server = socketserver.UDPServer((HOST, PORT), MyUDPHandlerClientSideWithObject)  # Созадём севрер
        server_thread = threading.Thread(target=self.clientside_server.serve_forever)  # Создаём поток
        server_thread.setDaemon(True)
        server_thread.start()  # Запускаем поток

        print("Clientside server was started")

    def create_serverside_server(self):
        class MyUDPHandlerServerSideWithObject(MyUDPHandlerServerSide):  # Костыль(?)
            parent_game = self  # Передаю ссылку на объект

        HOST, PORT = "localhost", 9998
        self.clientside_server = socketserver.UDPServer((HOST, PORT),
                                                        MyUDPHandlerServerSideWithObject)  # Созадём севрер
        server_thread = threading.Thread(target=self.clientside_server.serve_forever)  # Создаём поток
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
                        self.world.move_player_to("RIGHT")
                        self.last_moved_direction = "RIGHT"
                elif self.last_moved_direction == "RIGHT":
                    self.last_moved_direction = None
                if keyboard_pressed[pygame.K_UP]:
                    if self.last_moved_direction is None or self.last_moved_direction == "UP":
                        self.world.move_player_to("UP")
                        self.last_moved_direction = "UP"
                elif self.last_moved_direction == "UP":
                    self.last_moved_direction = None
                if keyboard_pressed[pygame.K_DOWN]:
                    if self.last_moved_direction is None or self.last_moved_direction == "DOWN":
                        self.world.move_player_to("DOWN")
                        self.last_moved_direction = "DOWN"
                elif self.last_moved_direction == "DOWN":
                    self.last_moved_direction = None
                if keyboard_pressed[pygame.K_LEFT]:
                    if self.last_moved_direction is None or self.last_moved_direction == "LEFT":
                        self.world.move_player_to("LEFT")
                        self.last_moved_direction = "LEFT"
                elif self.last_moved_direction == "LEFT":
                    self.last_moved_direction = None

                # Стрельба
                if keyboard_pressed[pygame.K_SPACE]:
                    self.world.create_bullet(self.world.players[0])

            # Тестовая попытка подключиться к серверу:
            if not self.is_server:
                if keyboard_pressed[pygame.K_0]:
                    if not self.server_button_pressed:
                        self.clientside_sender.ask_for_ok("localhost")
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
                    print(changes)
                    self.serverside_sender.send_changes()  # Вместо "localhost" - все клиенты
                self.world.clear_changes()

            self.window_surface.blit(self.game_surface, self.game_rect)

            pygame.display.update()

    def game_over(self, game_over_id):
        game_overs = [
            "Game over! Your tank was destroyed!",
            "Game over! Your base was destroyed!"
        ]
        print(game_overs[game_over_id])
        self.game_running = False
