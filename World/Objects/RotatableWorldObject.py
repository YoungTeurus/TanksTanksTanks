import logging

from pygame import transform

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

    def __init__(self, world):
        super().__init__(world)
        self.current_angle = "UP"

    def set_angle(self, angle):
        if angle in ANGLE:  # Поворачивать можно только на заранее обговоренные углы
            self.current_angle = angle
        else:
            logging.error("There was an attempt to rotate object on wrong angle: {}".format(angle))

    def draw(self, surface=None):
        """
        Отрисовка объекта в мире.
        :param surface: В данном случае не используется
        :return:
        """
        if self.image is not None:
            surface_to_draw = self.image
            if self.image.get_size() != self.object_rect.size:  # Если размер изображения не совпадает с размером объекта
                surface_to_draw = transform.scale(self.image, (self.object_rect.width, self.object_rect.height))
            if self.current_angle != "UP":
                surface_to_draw = transform.rotate(surface_to_draw, ANGLE[self.current_angle])

            self.parent_world.parent_surface.blit(surface_to_draw, self.object_rect)
            pass

    def __str__(self):
        return "{0} {1} {2} {3} {4} {5} {6}".format(
            "RotatableWorldObject", self.object_rect.x, self.object_rect.y,
            self.object_rect.width, self.object_rect.height,
            "img_id", self.current_angle
        )
