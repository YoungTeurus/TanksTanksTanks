import threading
from threading import Thread

import pygame

from Consts import window_w, window_h
from Game import Game


class MyThread(Thread):
    fun = None
    need_to_repeat = None

    def __init__(self, fun, need_to_repeat):
        Thread.__init__(self)
        self.fun = fun
        self.need_to_repeat = need_to_repeat

    def run(self) -> None:
        if self.need_to_repeat:
            while True:
                self.fun()
        else:
            self.fun()


class small_inputter:
    def __init__(self, game):
        self.game = game

    def do_input(self):
        inp = input()
        self.game.world.process_change(inp)


def main():
    # Инициализация PyGame и констант
    pygame.init()

    window_surface = pygame.display.set_mode((window_w, window_h))  # Основная поверхность

    game = Game(window_surface)  # Создание игры

    a = MyThread(game.main_cycle, False)

    a.start()

    inputter = small_inputter(game)
    b = MyThread(inputter.do_input, False)
    b.start()

    # a.join()
    # b.join()

    # game.main_cycle()  # Запуск основного цикла игры



if __name__ == "__main__":
    main()
