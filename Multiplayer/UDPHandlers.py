import json
import socketserver


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
            self.parent_game.world.is_server = False  # Говорим миру, что он больше не сервер
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
            if self.client_address[
                0] not in self.parent_game.serverside_sender.clients:  # Если этого IP ещё не было, заносим его в список клиентов
                self.parent_game.serverside_sender.clients.append(self.client_address[0])  # Заносим IP-шник отправителю
            # Говорим клиенту подгрузить такую-то карту
            self.parent_game.serverside_sender.send_load_world(self.client_address[0],
                                                               self.parent_game.world.world_map.map_id)
            # TODO: отправлять карту клиенту
        elif data_dict["type"] == "button":
            player_id = self.parent_game.serverside_sender.clients.index(self.client_address[0])
            # TODO: разделять управление для разных клиентов
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
