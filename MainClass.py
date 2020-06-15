import pygame
from pygame.surface import Surface

from Consts import window_w, window_h
from Files import ImageLoader, SoundLoader
from Game import Game
from UI.Menu import Menu


class MainClass:
    """
    Класс, совмещающий Game и Menu, а также имеющий единые загрузчики текстур и звуков.
    """
    image_loader: ImageLoader = None  # Загрузчик текстур
    sound_loader: SoundLoader = None  # Загрузчик музыки и звуков

    game: Game = None  # Игра
    menu: Menu = None  # Меню

    window_surface: Surface = None  # Поверхность окна

    def __init__(self):
        """
        Создаёт окошко, настраивает Loader-ы.
        """
        # Инициализация PyGame и констант
        pygame.init()

        self.window_surface = pygame.display.set_mode((window_w, window_h))  # Основная поверхность
        pygame.display.set_caption("TANK! TANK! TANK!")

        self.image_loader = ImageLoader()
        self.sound_loader = SoundLoader()

        pygame.display.set_icon(self.image_loader.get_image_by_name("icon"))  # Установка иконки игры

    def run(self):
        while True:
            menu = Menu(self.window_surface, self.image_loader, self.sound_loader)
            result = menu.main_cycle()
            if result["result"] == "start":
                if result["multi"]:
                    # Если сетевая игра
                    if result["mode"] == "client":
                        # Если запускается клиент
                        game = Game(self.window_surface, is_server=False,
                                    multi=True, connect_to_ip=result["server_ip"],
                                    client_ip=result["client_ip"], client_port=result["client_port"],
                                    client_name=result["client_name"],
                                    image_loader=self.image_loader, sound_loader=self.sound_loader)  # Создание игры
                    else:
                        # Если запускается сервер
                        game = Game(self.window_surface, is_server=True,
                                    multi=True, server_ip=result["server_ip"],
                                    dedicated=result["dedicated"],
                                    start_map=result["server_map"],
                                    image_loader=self.image_loader, sound_loader=self.sound_loader)  # Создание игры
                else:
                    # Если одиночная игра
                    game = Game(self.window_surface, is_server=False, multi=False,
                                start_map=result["client_map"],
                                image_loader=self.image_loader, sound_loader=self.sound_loader)  # Создание игры
            elif result["result"] == "quit":
                return
            else:
                return
            game.main_cycle()
            if not game.need_to_return_to_menu:
                # Если игру не нужно перезапускать, то прекращаем выполнение программы
                break
