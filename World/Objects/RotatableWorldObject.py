import logging

import pygame
from pygame import transform
from pygame.rect import Rect

from World.Objects.WorldObject import WorldObject

ANGLE = {
    "UP": 0,
    "RIGHT": 270,
    "DOWN": 180,
    "LEFT": 90
}


class RotatableWorldObject(WorldObject):
    """
    Класс вращаемых объектов мира
    """

    current_angle = None

    # Тестовое:
    test_font = None
    test_text = None

    def __init__(self, world):
        super().__init__(world)
        self.current_angle = "UP"

        # Тестовое:
        self.test_font = pygame.font.Font(None, 16)

    def set_angle(self, angle):
        if angle in ANGLE:  # Поворачивать можно только на заранее обговоренные углы
            self.current_angle = angle
        else:
            logging.error("There was an attempt to rotate object on wrong angle: {}".format(angle))

    def draw_in_world(self, camera=None):
        """
        Отрисовка объекта в мире.
        :param camera: Камера, относительно которой нужно отрисовывать объект
        :return:
        """
        if self.image is not None:
            surface_to_draw = self.image.get_current()
            rect_to_draw = Rect.copy(self.object_rect)  # TODO: подумать, можно ли избежать здесь ненужного копирования
            if self.image.get_size() != self.object_rect.size:
                # Если размер изображения не совпадает с размером объекта
                surface_to_draw = transform.scale(self.image.get_current(),
                                                  (self.object_rect.width, self.object_rect.height))
            if self.current_angle != "UP":
                surface_to_draw = transform.rotate(surface_to_draw, ANGLE[self.current_angle])
            if camera is not None:
                rect_to_draw.x += camera.get_coords()[0]
                rect_to_draw.y += camera.get_coords()[1]
            self.parent_world.parent_surface.blit(surface_to_draw, rect_to_draw)
            if self.need_to_animate:
                self.image.next()

            # Тестовое:
            self.test_text = self.test_font.render("id={}".format(self.world_id), 0, (255, 255, 255))
            self.parent_world.parent_surface.blit(self.test_text, (self.object_rect.x + camera.get_coords()[0],
                                                                   self.object_rect.y + camera.get_coords()[1]))

    def __str__(self):
        return "{0} {1} {2} {3} {4} {5} {8} {6} {7}".format(
            "RotatableWorldObject", self.object_rect.x, self.object_rect.y,
            self.object_rect.width, self.object_rect.height,
            self.image_name, self.current_angle, self.world_id,
            self.image.current_frame
        )
