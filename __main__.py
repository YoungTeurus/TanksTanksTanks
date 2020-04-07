import pygame
import logging

from Consts import window_w, window_h, targetFPS, BLACK, TANK_DEFAULT_SPEED_PER_SECOND
from World.World import World



def main():
    # Инициализация PyGame и констант
    pygame.init()

    window_surface = pygame.display.set_mode((window_w, window_h))  # Основная поверхность
    pygame.display.set_caption("TANK! TANK! TANK!")
    clock = pygame.time.Clock()

    game_running = True  # Флаг продолжения игры

    world = World(window_surface, (10, 10))
    world.setup_world()
    last_moved_direction = None

    while game_running:
        clock.tick(targetFPS)  # Требуемый FPS и соответствующая задержка
        window_surface.fill(BLACK)

        # Обработка событий:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_running = False
        keyboard_pressed = pygame.key.get_pressed()

        # Движение игрока
        if keyboard_pressed[pygame.K_RIGHT]:
            if last_moved_direction is None or last_moved_direction == "RIGHT":
                world.player.move_to_direction("RIGHT")
                last_moved_direction = "RIGHT"
        elif last_moved_direction == "RIGHT":
            last_moved_direction = None
        if keyboard_pressed[pygame.K_UP]:
            if last_moved_direction is None or last_moved_direction == "UP":
                world.player.move_to_direction("UP")
                last_moved_direction = "UP"
        elif last_moved_direction == "UP":
            last_moved_direction = None
        if keyboard_pressed[pygame.K_DOWN]:
            if last_moved_direction is None or last_moved_direction == "DOWN":
                world.player.move_to_direction("DOWN")
                last_moved_direction = "DOWN"
        elif last_moved_direction == "DOWN":
            last_moved_direction = None
        if keyboard_pressed[pygame.K_LEFT]:
            if last_moved_direction is None or last_moved_direction == "LEFT":
                world.player.move_to_direction("LEFT")
                last_moved_direction = "LEFT"
        elif last_moved_direction == "LEFT":
            last_moved_direction = None

        world.draw()

        pygame.display.update()


if __name__ == "__main__":
    logging.basicConfig(filename="log.log", level=logging.INFO, filemode="w")
    main()
