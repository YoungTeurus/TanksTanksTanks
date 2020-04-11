import pygame.sprite
from pygame import Rect

from Consts import image_w, image_h, TILES
from Files import get_script_dir
from Images.AnimatedImage import AnimatedImage


class Drawable(pygame.sprite.Sprite):
    """
    Класс для объектов, которые будут иметь отрсовываемую текстуру
    """
    float_x = 0
    float_y = 0
    object_rect = None  # Прямоугольник, хранящий позицию и размеры спрайта объекта
    image = None  # Отображаемая картинка
    image_name = None  # Название отображаемой картинки
    # animated_image = None
    # parent_imageloader = None  # Загрузчик картинок
    parent_tileset = None  # Тайлсет для картинок
    need_to_animate = False

    def __init__(self, tileset):
        pygame.sprite.Sprite.__init__(self)
        self.object_rect = Rect(0, 0, 0, 0)
        self.parent_tileset = tileset

    def set_animated(self):
        self.need_to_animate = True

    def set_size(self, width, height):
        self.object_rect.size = (width, height)

    def set_pos(self, x, y):
        self.float_x = x
        self.float_y = y
        self.object_rect.x = int(self.float_x)
        self.object_rect.y = int(self.float_y)

    def set_image(self, image_name):
        if image_name in TILES:
            self.image = AnimatedImage()
            for pair_of_tile_coord in TILES[image_name]:
                self.image.add_frame(self.parent_tileset.get_image(pair_of_tile_coord[0], pair_of_tile_coord[1]))
            self.image_name = image_name
        # self.image = self.parent_imageloader.get_image_by_name(image_name)

    # def set_test_animation(self, tileset):
    #     self.animated_image = AnimatedImage((image_w, image_h))
    #     for i in range(4):
    #        self.animated_image.add_frame(tileset.get_image(i, 0))

    def draw(self, surface):
        if self.image is not None:
            surface_to_draw = self.image.get_current()
            if self.image.get_size() != self.object_rect.size:  # Если размер изображения не совпадает с размером объекта
                surface_to_draw = pygame.transform.scale(self.image.get_current(), (self.object_rect.width, self.object_rect.height))

            surface.blit(surface_to_draw, self.object_rect)
            if self.need_to_animate:
                self.image.next()

    def __str__(self):
        return "{0} {1} {2} {3} {4} {5}".format(
            "Drawable", self.object_rect.x, self.object_rect.y,
            self.object_rect.width, self.object_rect.height,
            self.image_name
        )


if __name__ == "__main__":
    a = Drawable()
    a.set_pos(50, 100)
    a.set_size(34, 56)
    a.set_image(get_script_dir() + "\\tank.png")
