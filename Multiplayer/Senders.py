import json
import socket
from typing import List, Optional

from Consts import SOCKET_DEBUG, MAPS
from Files import get_script_dir

EVENT_CLIENT_CONNECTED = "EVENT_CLIENT_CONNECTED"
EVENT_CLIENT_PLAYER_QUIT = "EVENT_CLIENT_PLAYER_QUIT"
EVENT_CLIENT_READY = "EVENT_CLIENT_READY"
EVENT_SERVER_GAME_STARTED = "EVENT_SERVER_GAME_STARTED"
EVENT_SERVER_STOP = "EVENT_SERVER_STOP"
EVENT_CLIENT_SEND_CHAT_MESSAGE = "EVENT_CLIENT_SEND_CHAT_MESSAGE"
EVENT_SERVER_SEND_CHAT_MESSAGE = "EVENT_SERVER_SEND_CHAT_MESSAGE"
EVENT_SERVER_SEND_PLAYERS_TANKS_IDS = "EVENT_SERVER_SEND_PLAYERS_TANKS_IDS"
EVENT_PLAYER_LOSE_LIFE = "EVENT_PLAYER_LOSE_LIFE"


class Client:
    ip_port_combo: str = None  # Запись ip адреса и порта клиента
    player_id: int = None  # id_игрока
    ready: bool = None  # Флаг готовности клиента
    player_name: str = None  # Имя игрока в чате

    def __init__(self, ip_port_combo, player_name, player_id):
        self.ip_port_combo = ip_port_combo
        self.ready = False
        self.player_name = player_name
        self.player_id = player_id


class DataSenderServerSide:
    """
    Данный класс отправляет клиентам необходимые данные
    """
    parent_game = None
    clients: List[Client] = None  # Список клиентов
    # clients_player_id: dict = None  # Словарь "ip:порт - id_игрока"

    last_free_player_id: int = None  # Последний свободный id игрока

    def __init__(self, parent_game):
        self.parent_game = parent_game
        self.clients = []
        # self.clients_player_id = dict()
        self.last_free_player_id = 0

    def send_ok(self, ip, port):
        host, port = ip, port
        data_dict = dict()
        data_dict["type"] = "ok"
        data_dict["server_name"] = "TEST SERVER"
        data_dict["ip"] = self.parent_game.server_ip
        data = json.dumps(data_dict)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), (host, port))
        if SOCKET_DEBUG:
            print("Sent:     {}".format(data))

    def send_load_world(self, ip, port, world_id):
        host, port = ip, port
        data_dict = dict()
        data_dict["type"] = "load_world"
        data_dict["world_id"] = world_id
        data_dict["world"] = open(get_script_dir() + MAPS[world_id], "r").read()
        data = json.dumps(data_dict)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), (host, port))
        if SOCKET_DEBUG:
            print("Sent:     {}".format(data))

    def send_changes(self):
        for client in self.clients:
            host, port = client.ip_port_combo.split(":")
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
            sock.sendto(data.encode(), (host, int(port)))
            if SOCKET_DEBUG:
                print("Sent:     {}".format(data))

    def send_event(self, event_type: str, event_data: object = None, send_to: int = None):
        """
        Отправляет клиентам какой-то event-сигнал.
        Если send_to содержит player_id, то сингал будет отправлен только указанному игроку.
        """
        send_to_array = self.clients
        if send_to is not None:
            send_to_array = []
            for i in self.clients:
                if i.player_id == send_to:
                    send_to_array.append(i)
                    break
        for client in send_to_array:
            host, port = client.ip_port_combo.split(":")
            data_dict = dict()
            data_dict["type"] = "event"
            data_dict["event_type"] = event_type
            if event_data is not None:
                data_dict["event_data"] = event_data
            data = json.dumps(data_dict)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(data.encode(), (host, int(port)))
            if SOCKET_DEBUG:
                print("Sent:     {}".format(data))

    def get_client_by_ip_port_combo(self, ip_port_combo: str) -> Optional[Client]:
        for client in self.clients:
            if client.ip_port_combo == ip_port_combo:
                return client
        return None


class DataSenderClientSide:
    """
        Данный класс отправляет серверу необходимые данные
    """
    parent_game = None
    server = None

    player_name = "Player"

    def __init__(self, parent_game):
        self.parent_game = parent_game

    def set_server(self, ip):
        self.server = ip

    def ask_for_ok(self, ip):
        host, port = ip, 9998
        data_dict = dict()
        data_dict["type"] = "ask_for_ok"
        data_dict["ip"] = self.parent_game.client_ip
        data_dict["port"] = self.parent_game.client_port
        data = json.dumps(data_dict)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), (host, port))
        if SOCKET_DEBUG:
            print("Sent:     {}".format(data))

    def connect_to_server(self):
        host, port = self.server, 9998
        data_dict = dict()
        data_dict["type"] = "connect"
        data_dict["ip"] = self.parent_game.client_ip
        data_dict["port"] = self.parent_game.client_port
        data_dict["player_name"] = self.player_name
        data = json.dumps(data_dict)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), (host, port))
        if SOCKET_DEBUG:
            print("Sent:     {}".format(data))

    def send_button(self, button_id):
        host, port = self.server, 9998
        data_dict = dict()
        data_dict["type"] = "key"
        data_dict["ip"] = self.parent_game.client_ip
        data_dict["port"] = self.parent_game.client_port
        data_dict["button_id"] = button_id
        data = json.dumps(data_dict)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), (host, port))
        if SOCKET_DEBUG:
            print("Sent:     {}".format(data))

    def send_event(self, event_type: str, event_data: object = None):
        """
        Отправляет серверу какой-то event-сигнал
        """
        host, port = self.server, 9998
        data_dict = dict()
        data_dict["type"] = "event"
        data_dict["ip"] = self.parent_game.client_ip
        data_dict["port"] = self.parent_game.client_port
        data_dict["event_type"] = event_type
        if event_data is not None:
            data_dict["event_data"] = event_data
        data = json.dumps(data_dict)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), (host, port))
        if SOCKET_DEBUG:
            print("Sent:     {}".format(data))
