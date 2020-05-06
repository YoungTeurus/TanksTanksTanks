import pygame

from Consts import window_w, window_h
from Game import Game
from Menu.Menu import Menu


def main():
    # Инициализация PyGame и констант
    pygame.init()

    window_surface = pygame.display.set_mode((window_w, window_h))  # Основная поверхность

    menu = Menu(window_surface)
    result = menu.main_cycle()

    if result["result"] == "start":
        game = Game(window_surface, is_server=False)  # Создание игры
        game.main_cycle()


if __name__ == "__main__":
    main()
