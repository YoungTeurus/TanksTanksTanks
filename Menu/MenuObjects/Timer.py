import pygame

from Menu.MenuObjects.MenuObject import MenuObject


class Timer(MenuObject):

    target_millis: int = None  # Цель (в миллисекундах), после которой произойдёт действие
    current_millis: int = None  # Текущее количество миллисекунд
    function_onTarget = None  # Функция, выполняемая по достижению цели
    function_args = None  # Аргументы для этой функции

    clock = pygame.time.Clock()

    is_running: bool = None

    def __init__(self, target_millis: int, function_onTarget, function_args=None, start_of_init=True):
        self.target_millis = target_millis
        self.current_millis = 0
        self.function_onTarget = function_onTarget
        self.function_args = function_args
        if start_of_init:
            self.start()

    def update(self):
        if self.is_running:
            self.clock.tick()
            self.current_millis += self.clock.get_time()

            if self.current_millis >= self.target_millis:
                self.stop()
                if self.function_args is not None:
                    self.function_onTarget(self.function_args)
                else:
                    self.function_onTarget()

    def reset(self):
        self.current_millis = 0

    def start(self):
        self.clock.tick()
        self.is_running = True

    def stop(self):
        self.is_running = False
