import json
import socket


class DataSenderServerSide:
    """
    Данный класс отправляет клиентам необходимые данные
    """
    parent_game = None
    clients = []

    def __init__(self, parent_game):
        self.parent_game = parent_game

    def send_ok(self, ip):
        host, port = ip, 9999
        data_dict = dict()
        data_dict["type"] = "ok"
        data = json.dumps(data_dict)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), (host, port))
        print("Sent:     {}".format(data))

    def send_load_world(self, ip, world_id):
        host, port = ip, 9999
        data_dict = dict()
        data_dict["type"] = "load_world"
        data_dict["world_id"] = world_id
        data = json.dumps(data_dict)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), (host, port))
        print("Sent:     {}".format(data))

    def send_changes(self):
        for client_ip in self.clients:
            host, port = client_ip, 9999
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
            sock.sendto(data.encode(), (host, port))
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
        host, port = ip, 9998
        data_dict = dict()
        data_dict["type"] = "ask_for_ok"
        data = json.dumps(data_dict)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), (host, port))
        print("Sent:     {}".format(data))

    def connect_to_server(self):
        host, port = self.server, 9998
        data_dict = dict()
        data_dict["type"] = "connect"
        data = json.dumps(data_dict)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), (host, port))
        print("Sent:     {}".format(data))

    def send_button(self, button_id):
        host, port = self.server, 9998
        data_dict = dict()
        data_dict["type"] = "button"
        data_dict["button_id"] = button_id
        data = json.dumps(data_dict)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), (host, port))
        print("Sent:     {}".format(data))
