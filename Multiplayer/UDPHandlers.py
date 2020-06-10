import json
import os
import socketserver

from Consts import SOCKET_DEBUG, MAPS
from Files import get_script_dir
from UI.ConstPopups import add_disconnected_from_server_popupbox, remove_wait_popupbox_for_start_popupbox, \
    add_wait_for_start_popupbox
from Multiplayer.Senders import EVENT_SERVER_STOP, EVENT_CLIENT_PLAYER_QUIT, EVENT_SERVER_GAME_STARTED, \
    EVENT_CLIENT_CONNECTED, EVENT_CLIENT_READY, Client, EVENT_CLIENT_SEND_CHAT_MESSAGE, EVENT_SERVER_SEND_CHAT_MESSAGE


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
                os.mkdir(get_script_dir() + "\\assets\\maps\\downloaded")
            except OSError:
                # Если папка уже создана
                pass
            MAPS[world_id] = "\\assets\\maps\\downloaded\\map{}.txt".format(world_id)
            with open(get_script_dir() + MAPS[world_id], "w") as world_file:
                world_file.write(data_dict["world"])
            self.parent_game.world.load_map(world_id)  # Грузим карту
            self.parent_game.world.is_server = False  # Говорим миру, что он больше не сервер
            self.parent_game.clientside_sender.send_event(EVENT_CLIENT_READY)  # Говорим серверу, что мы готовы
        elif data_dict["type"] == "changes":
            # Если сервер прислал текущие изменения
            self.parent_game.world.process_many_changes(data_dict["changes"])
        elif data_dict["type"] == "event":
            # Если от сервера пришёл какой-то event...
            if data_dict["event_type"] == EVENT_SERVER_STOP:
                # Отключаем клиент
                add_disconnected_from_server_popupbox(self.parent_game)
                # self.parent_game.stop_game()
            elif data_dict["event_type"] == EVENT_SERVER_GAME_STARTED:
                # Если пришёл event начала игры
                remove_wait_popupbox_for_start_popupbox(self.parent_game)
            elif data_dict["event_type"] == EVENT_CLIENT_CONNECTED:
                # Если пришёл event, что мы подключились
                if not self.parent_game.is_connected:  # Если мы ЕЩЁ НЕ подключились...
                    # TODO: каждый клиент ловит этот пакет, нужно подумать, стоит ли это изменить
                    self.parent_game.is_connected = True  # Устанавливаем флаг подключения
                    add_wait_for_start_popupbox(self.parent_game)
            elif data_dict["event_type"] == EVENT_SERVER_SEND_CHAT_MESSAGE:
                # Если пришло сообщение в чат от сервера...
                message = data_dict["event_data"]
                self.parent_game.chat_history.add_message(message)


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
            ip_port_combo = "{}:{}".format(data_dict["ip"], data_dict["port"])
            # Если клиент хочет подключиться
            for client in self.parent_game.serverside_sender.clients:
                if ip_port_combo == client.ip_port_combo:
                    # Этот IP уже есть
                    return
            # Если этого IP ещё не было, заносим его в список клиентов
            # Заносим IP-шник, порт и имя отправителю
            temp_client = Client(ip_port_combo, data_dict["player_name"])
            self.parent_game.serverside_sender.clients.append(temp_client)
            # Присваиваем ip-шнику id игрока
            self.parent_game.serverside_sender.clients_player_id[
                ip_port_combo] = self.parent_game.serverside_sender.last_free_player_id
            self.parent_game.serverside_sender.last_free_player_id += 1
            # Говорим клиенту подгрузить такую-то карту
            self.parent_game.serverside_sender.send_event(EVENT_CLIENT_CONNECTED)
            self.parent_game.serverside_sender.send_load_world(data_dict["ip"], data_dict["port"],
                                                               self.parent_game.world.world_map.map_id)

        elif data_dict["type"] == "key":
            ip_port_combo = "{}:{}".format(data_dict["ip"], data_dict["port"])
            player_id = self.parent_game.serverside_sender.clients_player_id[ip_port_combo]
            if data_dict["button_id"] == "MOVE_UP":
                self.parent_game.world.move_player_to(player_id, "UP")
            elif data_dict["button_id"] == "MOVE_DOWN":
                self.parent_game.world.move_player_to(player_id, "DOWN")
                # self.parent_game.button_move_player(direction="DOWN", remote=False, player_id=player_id)
            elif data_dict["button_id"] == "MOVE_LEFT":
                self.parent_game.world.move_player_to(player_id, "LEFT")
                # self.parent_game.button_move_player(direction="LEFT", remote=False, player_id=player_id)
            elif data_dict["button_id"] == "MOVE_RIGHT":
                self.parent_game.world.move_player_to(player_id, "RIGHT")
                # self.parent_game.button_move_player(direction="RIGHT", remote=False, player_id=player_id)
            elif data_dict["button_id"] == "SHOOT":
                self.parent_game.world.create_bullet(self.parent_game.world.players[player_id])
        elif data_dict["type"] == "event":
            # Если от клиента пришёл какой-то event...
            if data_dict["event_type"] == EVENT_CLIENT_PLAYER_QUIT:
                # Если игрок отключился...
                pass
            elif data_dict["event_type"] == EVENT_CLIENT_READY:
                # Если игрок готов к игре...
                ip_port_combo = "{}:{}".format(data_dict["ip"], data_dict["port"])
                player_id = self.parent_game.serverside_sender.clients_player_id[ip_port_combo]

                self.parent_game.serverside_sender.clients[player_id].ready = True
            elif data_dict["event_type"] == EVENT_CLIENT_SEND_CHAT_MESSAGE:
                # Если клиент прислал сообщение...
                ip_port_combo = "{}:{}".format(data_dict["ip"], data_dict["port"])
                player_id = self.parent_game.serverside_sender.clients_player_id[ip_port_combo]

                message: str = f"[{self.parent_game.serverside_sender.clients[player_id].player_name}]" +\
                               data_dict["event_data"]  # Добавляем в начало сообщения имя игрока
                self.parent_game.chat_history.add_message(message)
                # Разсылаем клиентам это сообщение:
                self.parent_game.serverside_sender.send_event(EVENT_SERVER_SEND_CHAT_MESSAGE, message)
