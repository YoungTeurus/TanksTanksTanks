import pygame.sprite
from pygame import Rect

from Files import get_script_dir


class Drawable(pygame.sprite.Sprite):
    """
    Класс для объектов, которые будут иметь отрсовываемую текстуру
    """

    object_rect = None  # Прямоугольник, хранящий позицию и размеры спрайта объекта
    image = None  # Отображаемая картинка

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.object_rect = Rect(0, 0, 0, 0)

    def set_size(self, width, height):
        self.object_rect.size = (width, height)

    def set_pos(self, x, y):
        self.object_rect.x, self.object_rect.y = x, y

    def set_image(self, path_to_image):
        self.image = pygame.image.load(path_to_image)

    def draw(self, surface):
        if self.image is not None:
            surface_to_draw = self.image
            if self.image.get_size() != self.object_rect.size:  # Если размер изображения не совпадает с размером объекта
                surface_to_draw = pygame.transform.scale(self.image, (self.object_rect.width, self.object_rect.height))

            surface.blit(surface_to_draw, self.object_rect)

    def __str__(self):
        return "{0} {1} {2} {3} {4} {5}".format(
            "Drawable", self.object_rect.x, self.object_rect.y,
            self.object_rect.width, self.object_rect.height,
            "img_id"
        )

if __name__ == "__main__":
    a = Drawable()
    a.set_pos(50, 100)
    a.set_size(34, 56)
    a.set_image(get_script_dir() + "\\tank.png")