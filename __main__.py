import pygame

from Consts import window_w, window_h
from Game import Game


def main():
    # Инициализация PyGame и констант
    pygame.init()

    window_surface = pygame.display.set_mode((window_w, window_h))  # Основная поверхность

    game = Game(window_surface)  # Создание игры
    game.main_cycle()  # Запуск основного цикла игры


if __name__ == "__main__":
    main()
