import logging

import pygame

from Consts import targetFPS, DARK_GREY, BLACK
from Files import ImageLoader
from Images.Tileset import Tileset
from World.World import World


class Game:
    def __init__(self, window_surface):
        logging.basicConfig(filename="log.log", level=logging.INFO, filemode="w")
        self.window_surface = window_surface  # Основная поверхность

        minimal_dimention = min(self.window_surface.get_width(),
                                self.window_surface.get_height())  # Наименьшая сторона окна
        self.game_surface = pygame.Surface((minimal_dimention, minimal_dimention))
        # Выравнивание по левому краю
        # game_rect = pygame.Rect(0,
        #                         0,
        #                         minimal_dimention, minimal_dimention)
        # Выравнивание по центру
        self.game_rect = pygame.Rect(self.window_surface.get_width() / 2 - minimal_dimention / 2,
                                     self.window_surface.get_height() / 2 - minimal_dimention / 2,
                                     minimal_dimention, minimal_dimention)

        pygame.display.set_caption("TANK! TANK! TANK!")
        self.clock = pygame.time.Clock()
        self.imageloader = ImageLoader()
        self.tileset = Tileset(64, 64, self.imageloader.get_image_by_name("tileset.png"))

        self.game_running = True  # Флаг продолжения игры

        self.world = World(self.game_surface, self.tileset, True)
        self.world.setup_world()
        self.world.set_ready_for_server()

        self.last_moved_direction = None

    def main_cycle(self):
        while self.game_running:
            self.clock.tick(targetFPS)  # Требуемый FPS и соответствующая задержка
            self.window_surface.fill(DARK_GREY)
            self.game_surface.fill(BLACK)

            # Обработка событий:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_running = False
            keyboard_pressed = pygame.key.get_pressed()

            # Движение игрока
            if keyboard_pressed[pygame.K_RIGHT]:
                if self.last_moved_direction is None or self.last_moved_direction == "RIGHT":
                    self.world.move_player_to("RIGHT")
                    self.last_moved_direction = "RIGHT"
            elif self.last_moved_direction == "RIGHT":
                self.last_moved_direction = None
            if keyboard_pressed[pygame.K_UP]:
                if self.last_moved_direction is None or self.last_moved_direction == "UP":
                    self.world.move_player_to("UP")
                    self.last_moved_direction = "UP"
            elif self.last_moved_direction == "UP":
                self.last_moved_direction = None
            if keyboard_pressed[pygame.K_DOWN]:
                if self.last_moved_direction is None or self.last_moved_direction == "DOWN":
                    self.world.move_player_to("DOWN")
                    self.last_moved_direction = "DOWN"
            elif self.last_moved_direction == "DOWN":
                self.last_moved_direction = None
            if keyboard_pressed[pygame.K_LEFT]:
                if self.last_moved_direction is None or self.last_moved_direction == "LEFT":
                    self.world.move_player_to("LEFT")
                    self.last_moved_direction = "LEFT"
            elif self.last_moved_direction == "LEFT":
                self.last_moved_direction = None

            # Стрельба
            if keyboard_pressed[pygame.K_SPACE]:
                self.world.create_bullet(self.world.players[0])

            self.world.draw()
            self.world.act()
            if (changes := self.world.get_changes()).__len__() > 0:
                print(changes)
            self.world.clear_changes()

            if not self.world.check_if_player_is_alive():
                self.game_over(0)

            if not self.world.check_if_base_is_alive():
                self.game_over(1)

            self.window_surface.blit(self.game_surface, self.game_rect)

            pygame.display.update()

    def game_over(self, game_over_id):
        game_overs = [
            "Game over! Your tank was destroyed!",
            "Game over! Your base was destroyed!"
        ]
        print(game_overs[game_over_id])
        self.game_running = False
