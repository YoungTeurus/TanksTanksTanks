import pygame

from Consts import window_w, window_h
from Game import Game
from Menu.Menu import Menu


def main():
    # Инициализация PyGame и констант
    pygame.init()

    window_surface = pygame.display.set_mode((window_w, window_h))  # Основная поверхность
    pygame.display.set_caption("TANK! TANK! TANK!")

    need_to_restart = False

    while True:
        menu = Menu(window_surface)
        result = menu.main_cycle()

        if result["result"] == "start":
            if result["multi"]:
                # Если сетевая игра
                if result["mode"] == "client":
                    # Если запускается клиент
                    game = Game(window_surface, is_server=False,
                                multi=True, connect_to_ip=result["server_ip"],
                                client_ip=result["client_ip"], client_port=result["client_port"])  # Создание игры
                else:
                    # Если запускается сервер
                    game = Game(window_surface, is_server=True,
                                multi=True, server_ip=result["server_ip"])  # Создание игры
            else:
                # Если одиночная игра
                game = Game(window_surface, is_server=False, multi=False)  # Создание игры
        elif result["result"] == "quit":
            return
        else:
            return
        game.main_cycle()
        if not game.need_to_return_to_menu:
            # Если игру не нужно перезапускать, то прекращаем выполнение программы
            break


if __name__ == "__main__":
    main()
