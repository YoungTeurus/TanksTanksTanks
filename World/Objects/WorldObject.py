import pygame

from Consts import sprite_w, sprite_h
from World.Objects.Drawable import Drawable
from pygame import Rect


class WorldObject(Drawable):

    parent_world = None  # Родительский мир, в котором будут отрисовываться объекты

    def __init__(self, world):
        self.parent_world = world
        super().__init__(self.parent_world.parent_tileset)

    def draw_in_world(self, camera=None):
        """
        Отрисовка объекта в мире.
        :param camera: Камера, относительно которой нужно отрисовывать объект
        :return:
        """

        # Внимание! Меняя что-то здесь, не забывай поменять данную функцию в RotatableWorldObject!
        if self.image is not None:
            surface_to_draw = self.image.get_current_and_next()
            rect_to_draw = Rect.copy(self.object_rect)  # TODO: подумать, можно ли избежать здесь ненужного копирования
            if self.image.get_size() != self.object_rect.size:
                # Если размер изображения не совпадает с размером объекта
                surface_to_draw = pygame.transform.scale(self.image.get_current(), (self.object_rect.width, self.object_rect.height))
            if camera is not None:
                rect_to_draw.x += camera.get_coords()[0]
                rect_to_draw.y += camera.get_coords()[1]
            self.parent_world.parent_surface.blit(surface_to_draw, rect_to_draw)
            if self.need_to_animate:
                self.image.next()

    def get_world_pos(self):
        return (self.object_rect.x / sprite_w,
                self.object_rect.y / sprite_h)

    def destroy(self):
        """
        Функция, которая должна удалять объект из всех массивов, в которые он был добавлен при создании
        :return:
        """
        pass

    def __str__(self):
        return "{0} {1} {2} {3} {4} {5}".format(
            "WorldObject", self.object_rect.x, self.object_rect.y,
            self.object_rect.width, self.object_rect.height,
            "img_id"
        )
