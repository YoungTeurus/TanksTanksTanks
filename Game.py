import socketserver
import threading
from typing import Dict

import pygame
from pygame.surface import Surface

from Consts import targetFPS, DARK_GREY, BLACK, MOVE_RIGHT, SHOOT, MOVE_LEFT, MOVE_DOWN, MOVE_UP, \
    CHANGES_DEBUG, CHAT_BUTTON, FOLD_UNFOLD_CHATLOG, PLAYER_TANKS_COLORS, START_MAP_NAME
from Files import ImageLoader, SoundLoader, MapLoader
from Multiplayer.ChatHistory import ChatHistory
from UI.ConstPopups import add_server_started_popupbox, remove_server_started_popupbox, add_chat, \
    add_game_over_player_died_popupbox, add_game_over_player_base_destroyed_popupbox, add_you_win_popupbox
from UI.Ingame_GUI import GUI
from UI.MenuObjects.PopupBox import PopupBox
from Multiplayer.Senders import DataSenderServerSide, DataSenderClientSide, EVENT_SERVER_STOP, EVENT_CLIENT_PLAYER_QUIT, \
    EVENT_SERVER_GAME_STARTED, EVENT_CLIENT_SEND_CHAT_MESSAGE, EVENT_SERVER_SEND_PLAYERS_TANKS_IDS, EVENT_GAME_OVER, \
    EVENT_GAME_WIN
from Multiplayer.UDPHandlers import MyUDPHandlerClientSide, MyUDPHandlerServerSide
from World.Map import Map
from World.World import World


class Game:
    clientside_sender: DataSenderClientSide = None  # Отправители пакетов
    serverside_sender: DataSenderServerSide = None
    clientside_server: socketserver.UDPServer = None
    serverside_server: socketserver.UDPServer = None

    window_surface: Surface = None  # Основная поверхность

    image_loader: ImageLoader = None  # Загрузчик изображений
    sound_loader: SoundLoader = None  # Загрузчик звуков
    map_loader: MapLoader = None  # Загрузчик карт

    world: World = None  # Мир

    main_cycle_lock: threading.Lock()

    is_dedicated: bool = None  # Является ли выделенным сервером?
    is_server: bool = None
    is_connected: bool = None  # Подключён ли клиент к серверу
    multi: bool = None  # Сетевой режим или нет?
    game_started: bool = None  # Флаг начала игры
    game_running: bool = None  # Флаг запущенной игры

    connect_to_ip: str = None  # Адрес, к которому будет пытаться подключиться клиент
    client_ip: str = None  # Адрес, на котором расположен клиент
    # TODO: подумать, куда засунуть эту переменную V V V
    client_world_object_id: int = None  # ID объекта, которым управляет данный клиент
    client_port: int = None  # Порт клиента
    server_ip: str = None  # Адрес, на котором расположен сервер

    any_popup_box: PopupBox = None  # Любой PopupBox должен быть здесь
    any_popup_box_lock: threading.Lock = None  # Lock для критической секции
    gui: GUI = None  # Весь GUI игры находится здесь.
    need_to_return_to_menu: bool = False  # Установка этого флага позволяет вернуться в меню после завершения игры

    button_actions: Dict[str, tuple] = None  # Словарь "кнопка - дейсвтие", который используется в process_inputs

    chat_history: ChatHistory = None  # История чата

    need_to_quit: bool = False  # Флаг необходимости выхода из игры TODO: попытаться избавиться от этого?

    def __init__(self, window_surface, is_server, multi, image_loader: ImageLoader, sound_loader: SoundLoader,
                 map_loader: MapLoader, start_map: Map = None,
                 connect_to_ip: str = None, server_ip: str = None, client_ip: str = None,
                 client_port: int = None, dedicated: bool = False, client_name: str = None) -> None:
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

        self.any_popup_box_lock = threading.Lock()
        self.main_cycle_lock = threading.Lock()

        # Выравнивание по центру:
        self.game_rect = pygame.Rect(self.window_surface.get_width() / 2 - minimal_dimention / 2,
                                     self.window_surface.get_height() / 2 - minimal_dimention / 2,
                                     minimal_dimention, minimal_dimention)

        self.clock = pygame.time.Clock()
        self.image_loader = image_loader
        self.sound_loader = sound_loader
        self.map_loader = map_loader

        self.chat_history = ChatHistory()

        self.game_running = True

        self.is_server = is_server
        self.multi = multi
        self.is_dedicated = dedicated

        self.world = World(self, self.game_surface, self.image_loader, True)

        if start_map is not None:
            start_map_id = start_map.map_id
        else:
            start_map_id = self.map_loader.get_map_id_by_name(START_MAP_NAME)  # Стартовый ID карты

        if self.is_server and multi:
            # Запуск сервера для мультиплеера
            if not self.is_dedicated:
                self.gui = GUI(self)
            self.server_ip = server_ip
            self.world.set_ready_for_server()
            self.serverside_sender = DataSenderServerSide(self)
            self.create_serverside_server()
            self.world.load_world_map_by_map_id(start_map_id)
            self.world.clear_changes()
            self.server_waiting_started = False  # Флаг, который принимает значение True после первой
            # попытки ожидания клиентов.
            self.set_default_buttons(is_server=True)
        elif not self.is_server and self.multi:
            # Запуск клиента для мультиплеера
            self.gui = GUI(self)
            self.clientside_sender = DataSenderClientSide(self)
            self.client_ip = client_ip
            self.client_port = client_port
            self.create_clientside_server()
            self.connect_to_ip = connect_to_ip
            self.is_connected = False
            self.game_started = False
            self.has_already_tried_to_connect = False
            self.server_button_pressed = False  # Флаг для однократной отработки нажатия кнопки подключения
            self.set_default_buttons(is_server=False)
            if client_name is not None:
                self.clientside_sender.player_name = client_name
        elif not multi:
            # Запуск одиночки
            self.gui = GUI(self)
            self.world.load_world_map_by_map_id(start_map_id)
            self.world.spawn_player()
            self.world.players[0].add_color(PLAYER_TANKS_COLORS[0])
            self.world.center_camera_on_player()
            self.game_started = True  # TODO: Временно
            self.set_default_buttons(is_server=True)

        self.main_cycle()  # Основной цикл

    def send_changes_and_clear(self) -> None:
        self.serverside_sender.send_changes()
        self.world.clear_changes()

    def wait_for_players(self, num_of_player_to_start: int = 2) -> None:
        """
        Реализует цикл ожидания игроков. Пока не наберётся num_of_player_to_start игроков, игра не начнётся.
        :param num_of_player_to_start: Число игроков для начала.
        """

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
        for (i, player) in enumerate(self.serverside_sender.clients):
            self.world.spawn_player(i)

        self.send_changes_and_clear()  # Отправляем только сообщение о создании танков игроков

        # Отправка клиентам ID их танков, чтобы они могли сами центрировать камеры
        id_players_ip_combo: dict = dict()
        for (i, client) in enumerate(self.serverside_sender.clients):
            id_players_ip_combo[client.ip_port_combo] = self.world.players[client.player_id].world_id
        self.serverside_sender.send_event(EVENT_SERVER_SEND_PLAYERS_TANKS_IDS, id_players_ip_combo)

        self.world.center_camera_on_player()

        self.serverside_sender.send_event(EVENT_SERVER_GAME_STARTED)

        remove_server_started_popupbox(self)
        self.game_started = True

    def create_clientside_server(self) -> None:
        """
        Запускает сервер на стороне клиента.
        """
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
        """
        Запускает сервер на стороне сервера.
        """
        class MyUDPHandlerServerSideWithObject(MyUDPHandlerServerSide):  # Костыль(?)
            parent_game = self  # Передаю ссылку на объект

        HOST, PORT = self.server_ip, 9998
        self.serverside_server = socketserver.UDPServer((HOST, PORT),
                                                        MyUDPHandlerServerSideWithObject)  # Созадём севрер
        server_thread = threading.Thread(target=self.serverside_server.serve_forever)  # Создаём поток
        server_thread.setDaemon(True)
        server_thread.start()  # Запускаем поток

        print("Serverside server was started")

    def set_default_buttons(self, is_server: bool) -> None:
        """
        Привязывает клавиши к event-ам, заполняя словарь.
        :param is_server: Является ли текущий Game сервером.
        """
        self.button_actions = dict()
        if is_server:
            # Если задаём для сервера или одиночки
            self.button_actions[MOVE_RIGHT] = ((lambda: self.button_move_player("RIGHT", False)),
                                               (lambda: self.reset_move_player_direction("RIGHT", False)))
            self.button_actions[MOVE_LEFT] = ((lambda: self.button_move_player("LEFT", False)),
                                              (lambda: self.reset_move_player_direction("LEFT", False)))
            self.button_actions[MOVE_UP] = ((lambda: self.button_move_player("UP", False)),
                                            (lambda: self.reset_move_player_direction("UP", False)))
            self.button_actions[MOVE_DOWN] = ((lambda: self.button_move_player("DOWN", False)),
                                              (lambda: self.reset_move_player_direction("DOWN", False)))
            self.button_actions[SHOOT] = ((lambda: self.world.create_bullet(self.world.players[0])),
                                          None)
        else:
            # TODO: Избавиться от этой переменной и класса.
            class MoveVar:
                direction: str = None

            move_var = MoveVar()  # Переменная для хранения текущего направления движения танка

            # Если задаём для клиента
            self.button_actions[MOVE_RIGHT] = ((lambda: self.button_move_player("RIGHT", True, local_var=move_var)),
                                               (lambda: self.reset_move_player_direction("RIGHT", True,
                                                                                         local_var=move_var)))
            self.button_actions[MOVE_LEFT] = ((lambda: self.button_move_player("LEFT", True, local_var=move_var)),
                                              (lambda: self.reset_move_player_direction("LEFT", True,
                                                                                        local_var=move_var)))
            self.button_actions[MOVE_UP] = ((lambda: self.button_move_player("UP", True, local_var=move_var)),
                                            (lambda: self.reset_move_player_direction("UP", True, local_var=move_var)))
            self.button_actions[MOVE_DOWN] = ((lambda: self.button_move_player("DOWN", True, local_var=move_var)),
                                              (lambda: self.reset_move_player_direction("DOWN", True,
                                                                                        local_var=move_var)))
            self.button_actions[SHOOT] = ((lambda: self.clientside_sender.send_button("SHOOT")),
                                          None)
            self.button_actions[CHAT_BUTTON] = ((lambda: add_chat(self)),
                                                None)
            self.button_actions[FOLD_UNFOLD_CHATLOG] = (self.gui.change_chatlog_action,
                                                        self.gui.reset_button)

    def process_inputs(self) -> None:
        """
        Обрабатывает все нажатые клавиши, выполняя необходимые действия.
        """
        # Кнопка в self.button_actions должна храниться так:
        # "код клавиши из PyGame": ("действие при нажатой", "действие при ненажатой")
        # Любое из действий может быть None!
        # Действие "NONE" может иметь только одно действие "при ненажатой".

        if self.any_popup_box is not None and self.any_popup_box.blocking:
            # Если есть блокирующий popup_box, ничего не делаем.
            return

        keyboard_pressed = pygame.key.get_pressed()
        any_pressed = False  # Была ли нажата хоть одна клавиша

        for button in self.button_actions:
            if keyboard_pressed[button]:  # Если указанная клавиша нажата, выполняется действие при нажатии
                if self.button_actions[button][0] is not None:
                    self.button_actions[button][0]()
            else:  # Если указанная клавиша не нажата, выполняется действие при ненажатой
                if self.button_actions[button][1] is not None:
                    self.button_actions[button][1]()

        if not any_pressed:
            if "NONE" in self.button_actions and self.button_actions["NONE"][1] is not None:
                self.button_actions["NONE"][1]()  # Действие при отсутствии нажатий

    def button_move_player(self, direction, remote, player_id=0, local_var=None) -> None:
        """
        Вызывается, когда нажата кнопка движения.
        Либо посылает на сервер указание, что нажали определённую кнопку движения, либо двигает 0-ого игрока
        (в случае сервера или одиночки).
        :param local_var: Переменная, необходимая в случае remote=True,
         туда записывается последнее направление движения.
        :param player_id: Айди игрока, для которого это выполняется.
        :param direction: Направление движения
        :param remote: Если True - нужно отправлять данные на сервер, если False - локальные изменения.
        """
        if remote:
            # Если мы отправляем движение на сервер
            if local_var.direction is None or local_var.direction == direction:
                self.clientside_sender.send_button("MOVE_" + direction)

                # Смотри класс MoveVar в методе set_default_buttons:
                local_var.direction = direction
        else:
            current_player = self.world.players[player_id]
            # Если мы сами себе сервер
            if current_player.last_pressed_direction is None or current_player.last_pressed_direction == direction:
                self.world.move_player_to(player_id, direction)
                current_player.last_pressed_direction = direction

    def reset_move_player_direction(self, direction, remote, player_id=0, local_var=None) -> None:
        """
        Сбрасывает кнопку движения для игрока в локальной игре.
        :param local_var: Эта переменная используется при remote=True. Содержит текущее направление движения.
        :param remote: Если True - нужно применять доп.логику для сохранения состояния,
         если False - локальные изменения.
        :param player_id: Айди игрока, для которого это выполняется.
        :param direction: Направление, которое нужно сбросить.
        """
        if remote:
            if local_var.direction == direction:
                local_var.direction = None
        else:
            if self.world.players[player_id].last_pressed_direction == direction:
                self.world.players[player_id].last_pressed_direction = None

    def send_chat_message(self, msg_str: str) -> None:
        """
        Отправляет сообщение со стороны клиента.
        :param msg_str: Сообщение для отправки.
        """
        self.clientside_sender.send_event(EVENT_CLIENT_SEND_CHAT_MESSAGE, msg_str)

    def main_cycle(self) -> None:
        """
        Главный цикл - здесь происходит отрисовка объектов, обработка событий и все проверки.
        """
        while self.game_running:
            with self.main_cycle_lock:
                self.clock.tick(targetFPS)  # Требуемый FPS и соответствующая задержка
                self.window_surface.fill(DARK_GREY)
                self.game_surface.fill(BLACK)
    
                # Обработка событий:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.stop_game()
                    # Обработка всплывающих окон:
                    with self.any_popup_box_lock:
                        if self.any_popup_box is not None:
                            self.any_popup_box.handle_event(event)
                if self.need_to_quit:
                    self.stop_game()
                # keyboard_pressed = pygame.key.get_pressed()
    
                if self.is_server and not self.game_started:
                    if not self.server_waiting_started:
                        add_server_started_popupbox(self)
                        self.server_waiting_started = True
                    # Пока сервер не стартанул
                    self.wait_for_players(int(self.world.world_map.properties["max_players"]))
    
                if self.game_started:
                    self.process_inputs()
    
                    # TODO: подумать, куда засунуть это V V V
                    if self.multi and not self.is_server:
                        # Центируемся на своём танке
                        try:
                            self.world.camera.smart_center_on(self.world.objects_id_dict[self.client_world_object_id])
                        except KeyError:
                            # Не можем сцентрироваться - видимо, танка уже нет.
                            pass
    
                # Попытка подключиться к серверу при запуске клиента:
                if not self.is_server and not self.is_connected and self.multi and not self.has_already_tried_to_connect:
                    self.clientside_sender.ask_for_ok(self.connect_to_ip)
                    self.has_already_tried_to_connect = True
    
                # if self.game_started and (not self.multi or not self.is_server or not self.is_dedicated):
                if self.game_started:
                    # Отрисовка происходит только, когда игра началась И
                    #  либо игра одиночная
                    #  либо игра - клиент
                    #  либо игра - не выделенный сервер
                    self.world.draw()
    
                if self.game_started and (self.is_server or not self.multi):
                    self.world.act()
                    # Проверка на конец игры:
                    game_over_dict = self.world.check_game_over()
                    if game_over_dict is not None:
                        # Проверка на конец игры здесь.
                        self.game_over(game_over_dict)
                    # Спавн врагов:
                    if self.world.enemy_spawn_timer.is_ready() and self.world.enemies_remains > 0:
                        if self.world.create_enemy():
                            # Если получилось заспавнить врага
                            self.world.enemies_remains -= 1
                            self.world.enemy_spawn_timer.reset()
                    # Если уровень завершён.
                    if self.world.check_level_over():
                        if "next_map" in self.world.world_map.properties:
                            next_map_name = self.world.world_map.properties["next_map"]
                            next_map_id = self.map_loader.get_map_id_by_name(next_map_name)
                            self.world.reload_map(next_map_id)
                            self.world.clear_changes()  # На всякий случай очищаем изменения.
                        else:
                            # Если нет следующего уровня, выводим экран победы
                            if self.is_server and self.multi:
                                # ...либо клиентам.
                                self.serverside_sender.send_event(EVENT_GAME_WIN)
                                self.stop_game(send_to_server=False)
                            else:
                                # ...либо себе.
                                add_you_win_popupbox(self)
                                self.game_started = False
    
                    # Изменения в мире:
                    if (changes := self.world.get_changes()).__len__() > 0 and self.multi:
                        if CHANGES_DEBUG:
                            print(changes)
                        self.serverside_sender.send_changes()
                    self.world.clear_changes()
    
                self.window_surface.blit(self.game_surface, self.game_rect)
    
                if self.game_started and self.gui is not None:
                    self.gui.draw()
                    self.gui.update()
    
                # Отрисовка и обновление popupBox-а:
                with self.any_popup_box_lock:
                    if self.any_popup_box is not None:
                        self.any_popup_box.draw()
                        self.any_popup_box.update()
    
                pygame.display.update()

    def game_over(self, game_over_dict: dict):
        if self.multi and self.is_server:
            self.serverside_sender.send_event(EVENT_GAME_OVER, game_over_dict)
            self.stop_game(send_to_server=False)
        if game_over_dict["type"] == "player_died":
            add_game_over_player_died_popupbox(self, game_over_dict["player_name"])
        elif game_over_dict["type"] == "base_destroyed":
            add_game_over_player_base_destroyed_popupbox(self)

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
