import pygame

from Consts import window_w, window_h, BLACK, targetFPS
from Files import ImageLoader
from Images.Tileset import Tileset
from Game import Game
from World.Objects.Drawable import Drawable


def main():
    # Инициализация PyGame и констант
    pygame.init()

    window_surface = pygame.display.set_mode((window_w, window_h))  # Основная поверхность

    game = Game(window_surface)  # Создание игры
    game.main_cycle()  # Запуск основного цикла игры


if __name__ == "__main__":
    main()
    # window_surface = pygame.display.set_mode((window_w, window_h))
    # pygame.time.Clock().tick(targetFPS)
    # a = ImageLoader()
    # b = Tileset(64, 64, a.get_image_by_name("tileset.png"))
    # c = Drawable(b)
    # c.set_size(64, 64)
    # c.set_image("PLAYER_TANK")
    # c.image.add_timer(300)
    # while True:
    #     window_surface.fill(BLACK)
    #     c.draw(window_surface)
    #     pygame.display.update()
