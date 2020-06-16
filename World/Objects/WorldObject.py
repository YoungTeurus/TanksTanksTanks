import pygame

from Consts import sprite_w, sprite_h, DESTROY_STRING, VISIBLE_STRING
from World.Objects.Drawable import Drawable
from pygame import Rect


class WorldObject(Drawable):

    parent_world = None  # Родительский мир, в котором будут отрисовываться объекты
    world_id = None  # Айди объекта для мультиплеера

    visible: bool = None  # Отрисовывается ли объект

    def __init__(self, world, tileset_name: str):
        self.visible = True
        self.parent_world = world
        super().__init__(self.parent_world.tilesets[tileset_name])
        if self.parent_world.auto_id_set:
            self.world_id = self.parent_world.get_last_id()
            self.parent_world.objects_id_dict[self.world_id] = self

    def set_visible(self, visible: bool):
        self.visible = visible

        if self.parent_world.need_to_log_changes:  # Для сервера
            self.parent_world.changes.append(VISIBLE_STRING.format(
                bool=visible,
                world_id=self.world_id
            ))

    def set_world_id(self, world_id):
        self.world_id = world_id

    def draw_in_world(self, camera=None):
        """
        Отрисовка объекта в мире.
        :param camera: Камера, относительно которой нужно отрисовывать объект
        :return:
        """
        # Внимание! Меняя что-то здесь, не забывай поменять данную функцию в RotatableWorldObject!
        if self.visible:
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
        if self.parent_world.auto_id_set:
            if self.world_id in self.parent_world.objects_id_dict:
                self.parent_world.objects_id_dict.pop(self.world_id)
        if self.parent_world.need_to_log_changes:  # Для сервера
            self.parent_world.changes.append(DESTROY_STRING.format(world_id=self.world_id,
                                                                   object_type="RotatableWorldObject"))

    def __str__(self):
        return "{0} {1} {2} {3} {4} {5} {6}".format(
            "WorldObject", self.object_rect.x, self.object_rect.y,
            self.object_rect.width, self.object_rect.height,
            self.image_name, self.world_id
        )
