import pygame
import logging

from Consts import window_w, window_h, targetFPS, BLACK, TANK_DEFAULT_SPEED_PER_SECOND, GREY, DARK_GREY
from Files import ImageLoader
from Game import Game
from World.World import World


def main():
    # Инициализация PyGame и констант
    pygame.init()

    window_surface = pygame.display.set_mode((window_w, window_h))  # Основная поверхность

    game = Game(window_surface)  # Создание игры
    game.main_cycle()  # Запуск основного цикла игры


if __name__ == "__main__":
    logging.basicConfig(filename="log.log", level=logging.INFO, filemode="w")
    main()
