import json
import os
import socketserver

from Consts import SOCKET_DEBUG, MAPS
from Files import get_script_dir


class MyUDPHandlerClientSide(socketserver.BaseRequestHandler):
    """
    Данный класс содержит handle, принимающий информацию отслылаемую сервером, то есть распарсивает полученный json и
    воздейсвтует на игру.
    """
    parent_game = None
    port = None

    def handle(self):
        data = self.request[0].decode()  # Вытаскиваем data
        data_dict = json.loads(data)  # Делаем из этого словарь
        if SOCKET_DEBUG:
            print("{} wrote: ".format(self.client_address[0]), end="")
            print(data_dict)  # Вывод дебаг-информации

        if data_dict["type"] == "ok":
            # Если сервер отправил ok
            self.parent_game.clientside_sender.server = data_dict["ip"]  # Запоминаем IP сервера
            self.parent_game.clientside_sender.connect_to_server()  # Пробуем подключиться к серверу
        elif data_dict["type"] == "load_world":
            # Если сервер сказал подгрузить карту
            world_id = 100 + data_dict["world_id"]
            try:
                os.mkdir(get_script_dir()+"\\assets\\maps\\downloaded")
            except OSError:
                # Если папка уже создана
                pass
            MAPS[world_id] = "\\assets\\maps\\downloaded\\map{}.txt".format(world_id)
            with open(get_script_dir()+MAPS[world_id], "w") as world_file:
                world_file.write(data_dict["world"])
            self.parent_game.world.load_map(world_id)  # Грузим карту
            self.parent_game.world.is_server = False  # Говорим миру, что он больше не сервер
        elif data_dict["type"] == "changes":
            # Если сервер прислал текущие изменения
            self.parent_game.world.process_many_changes(data_dict["changes"])


class MyUDPHandlerServerSide(socketserver.BaseRequestHandler):
    """
    Данный класс содержит handle, принимающий информацию отслылаемую сервером, то есть распарсивает полученный json и
    воздейсвтует на игру.
    """
    parent_game = None

    def handle(self):
        data = self.request[0].decode()  # Вытаскиваем data
        data_dict = json.loads(data)  # Делаем из этого словарь
        if SOCKET_DEBUG:
            print("{} wrote: ".format(self.client_address[0]), end="")
            print(data_dict)  # Вывод дебаг-информации

        if data_dict["type"] == "ask_for_ok":
            # Если клиент спрашивает об OK-ее
            self.parent_game.serverside_sender.send_ok(data_dict["ip"], data_dict["port"])  # Отправляем ему OK
        elif data_dict["type"] == "connect":
            # Если клиент хочет подключиться
            if self.client_address[0] not in self.parent_game.serverside_sender.clients:
                # Если этого IP ещё не было, заносим его в список клиентов
                # Заносим IP-шник и порт отправителю
                self.parent_game.serverside_sender.clients[data_dict["ip"]] = data_dict["port"]
                # Присваиваем ip-шнику id игрока
                self.parent_game.serverside_sender.clients_player_id[data_dict["ip"]] = self.parent_game.serverside_sender.last_free_player_id
                self.parent_game.serverside_sender.last_free_player_id += 1
            # Говорим клиенту подгрузить такую-то карту
            self.parent_game.serverside_sender.send_load_world(data_dict["ip"], data_dict["port"], self.parent_game.world.world_map.map_id)
            self.parent_game.world.spawn_player()  # Спавн нового игрока
            self.parent_game.world.center_camera_on_player()
        elif data_dict["type"] == "key":
            player_id = self.parent_game.serverside_sender.clients_player_id[data_dict["ip"]]
            if data_dict["button_id"] == "MOVE_UP":
                self.parent_game.world.move_player_to(player_id, "UP",)
            elif data_dict["button_id"] == "MOVE_DOWN":
                self.parent_game.world.move_player_to(player_id, "DOWN")
            elif data_dict["button_id"] == "MOVE_LEFT":
                self.parent_game.world.move_player_to(player_id, "LEFT")
            elif data_dict["button_id"] == "MOVE_RIGHT":
                self.parent_game.world.move_player_to(player_id, "RIGHT")
            elif data_dict["button_id"] == "SHOOT":
                self.parent_game.world.create_bullet(self.parent_game.world.players[player_id])
