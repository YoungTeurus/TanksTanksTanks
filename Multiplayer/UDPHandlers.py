import json
import os
import socketserver

import pygame

from Consts import SOCKET_DEBUG, MAPS, BLACK
from Files import get_script_dir
from Menu.Menu import MAIN_MENU_BACKGROUND_COLOR, BUTTON_YELLOW, MENU_WHITE
from Menu.MenuObjects.ButtonTrigger import ButtonTrigger
from Menu.MenuObjects.Label import Label
from Menu.MenuObjects.PopupBox import PopupBox
from Multiplayer.Senders import EVENT_SERVER_STOP, EVENT_PLAYER_QUIT


def add_disconnected_from_server_popupbox(game):
    # Всплывающее окно "Сервер закрыт":
    popupbox = PopupBox(game.window_surface, pos=(game.window_surface.get_width() / 2 - 100,
                                                  game.window_surface.get_height() / 2 - 50, 200, 100),
                        color=MAIN_MENU_BACKGROUND_COLOR)
    label_popupbox_title = Label(game.window_surface,
                                 pos=(popupbox.rect.x + popupbox.rect.w / 2,
                                      popupbox.rect.y + 15,
                                      0, 0),
                                 text="Отключен от сервера:", text_color=MENU_WHITE,
                                 font_size=20, font="main_menu")
    label_popupbox_title_shadow = Label(game.window_surface,
                                        pos=(popupbox.rect.x + popupbox.rect.w / 2 + 2,
                                             popupbox.rect.y + 17, 0, 0),
                                        text="Отключен от сервера:", text_color=BLACK,
                                        font_size=20, font="main_menu")
    label_popupbox_reason = Label(game.window_surface,
                                  pos=(popupbox.rect.x + popupbox.rect.w / 2,
                                       popupbox.rect.y + 45,
                                       0, 0),
                                  text="Сервер закрыт!", text_color=BUTTON_YELLOW,
                                  font_size=28, font="main_menu")
    label_popupbox_reason_shadow = Label(game.window_surface,
                                         pos=(popupbox.rect.x + popupbox.rect.w / 2 + 2,
                                              popupbox.rect.y + 47, 0, 0),
                                         text="Сервер закрыт!", text_color=BLACK,
                                         font_size=28, font="main_menu")
    label_popupbox_esc = Label(game.window_surface,
                               pos=(popupbox.rect.x + popupbox.rect.w / 2,
                                    popupbox.rect.y + 85,
                                    0, 0),
                               text="Нажмите ESC!", text_color=BUTTON_YELLOW,
                               font_size=16, font="main_menu")
    label_popupbox_esc_shadow = Label(game.window_surface,
                                      pos=(popupbox.rect.x + popupbox.rect.w / 2 + 2,
                                           popupbox.rect.y + 87, 0, 0),
                                      text="Нажмите ESC!", text_color=BLACK,
                                      font_size=16, font="main_menu")
    buttontrigger_popupbox_quit_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                                    function_list=[remove_disconnected_from_server_popupbox_and_return_to_menu],
                                                    args_list=[game])

    popupbox.add_object(buttontrigger_popupbox_quit_esc)
    popupbox.add_object(label_popupbox_title_shadow)
    popupbox.add_object(label_popupbox_title)
    popupbox.add_object(label_popupbox_reason_shadow)
    popupbox.add_object(label_popupbox_reason)
    popupbox.add_object(label_popupbox_esc_shadow)
    popupbox.add_object(label_popupbox_esc)

    game.any_popup_box = popupbox


def remove_disconnected_from_server_popupbox_and_return_to_menu(game):
    game.any_popup_box = None
    game.return_to_menu()


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
        elif data_dict["type"] == "changes":
            # Если сервер прислал текущие изменения
            self.parent_game.world.process_many_changes(data_dict["changes"])
        elif data_dict["type"] == "event":
            # Если от сервера пришёл какой-то event...
            if data_dict["event_type"] == EVENT_SERVER_STOP:
                # Отключаем клиент
                add_disconnected_from_server_popupbox(self.parent_game)
                # self.parent_game.stop_game()


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
                ip_port_combo = "{}:{}".format(data_dict["ip"], data_dict["port"])
                self.parent_game.serverside_sender.clients.append(ip_port_combo)
                # Присваиваем ip-шнику id игрока
                self.parent_game.serverside_sender.clients_player_id[
                    ip_port_combo] = self.parent_game.serverside_sender.last_free_player_id
                self.parent_game.serverside_sender.last_free_player_id += 1
            # Говорим клиенту подгрузить такую-то карту
            self.parent_game.serverside_sender.send_load_world(data_dict["ip"], data_dict["port"],
                                                               self.parent_game.world.world_map.map_id)
            self.parent_game.world.spawn_player()  # Спавн нового игрока
            self.parent_game.world.center_camera_on_player()
        elif data_dict["type"] == "key":
            ip_port_combo = "{}:{}".format(data_dict["ip"], data_dict["port"])
            player_id = self.parent_game.serverside_sender.clients_player_id[ip_port_combo]
            if data_dict["button_id"] == "MOVE_UP":
                self.parent_game.world.move_player_to(player_id, "UP", )
            elif data_dict["button_id"] == "MOVE_DOWN":
                self.parent_game.world.move_player_to(player_id, "DOWN")
            elif data_dict["button_id"] == "MOVE_LEFT":
                self.parent_game.world.move_player_to(player_id, "LEFT")
            elif data_dict["button_id"] == "MOVE_RIGHT":
                self.parent_game.world.move_player_to(player_id, "RIGHT")
            elif data_dict["button_id"] == "SHOOT":
                self.parent_game.world.create_bullet(self.parent_game.world.players[player_id])
        elif data_dict["type"] == "event":
            # Если от клиента пришёл какой-то event...
            if data_dict["event_type"] == EVENT_PLAYER_QUIT:
                # Если игрок отключился...
                pass
