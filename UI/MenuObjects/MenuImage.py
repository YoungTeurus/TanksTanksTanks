import pygame
from pygame.constants import SRCALPHA
from pygame.rect import Rect
from pygame.surface import Surface

from Consts import BLACK
from Images.ImageMethods import fill_color
from UI.MenuObjects.MenuObjectClickable import MenuObjectClickable

ALIGNMENT_HIGH_LEFT = 0  # Нет "выравнивания". Переданные координаты - координаты верхнего левого угла.
ALIGNMENT_CENTER = 1  # Выравние "по центру". Переданные координаты - координаты центра изображения.

NORMAL = 0  # Обычное изображение
FILL = 1  # Изображение, заполняющее своими копиями предоставленное пространство


class MenuImage(MenuObjectClickable):
    image: Surface = None  # Картинка для отображения
    shadow_image: Surface = None

    active: bool = None  # Нужно ли отрисовывать изображение

    alignment: int = ALIGNMENT_HIGH_LEFT  # Тип выравнивания.

    def __init__(self, window_surface: Surface, pos: tuple, image: Surface,
                 shadow: bool = False, alignment: int = ALIGNMENT_HIGH_LEFT,
                 type: int = NORMAL, one_image_size: tuple = None, active: bool = True) -> None:
        self.window_surface = window_surface
        self.rect = Rect((pos[0], pos[1], pos[2], pos[3]))
        self.image = image
        self.active = active

        if type == NORMAL:
            # Поправка размеров
            if self.rect.w != 0 or self.rect.h != 0:
                # Если одна из координат == 0, значит не нужно изменять размеры картинки.
                if self.rect.w != self.image.get_width() or self.rect.h != self.image.get_height():
                    self.image = pygame.transform.scale(self.image, (self.rect.w, self.rect.h))

            if shadow:
                self.shadow_image = self.image.copy()
                fill_color(self.shadow_image, BLACK, max_alpha=128)
        elif type == FILL:
            inserted_image = image
            if one_image_size is not None:
                # Если указан размер одного изображения...
                inserted_image = pygame.transform.scale(inserted_image, (one_image_size[0], one_image_size[1]))
            # Заполнить image картинками
            src_image_w, src_image_h = inserted_image.get_size()  # Размеры исходного изобрежения

            self.image = Surface((self.rect.w, self.rect.h), SRCALPHA)

            w_times = self.rect.w // src_image_w + 1  # Что-то вроде округления в большую сторону
            h_times = self.rect.h // src_image_h + 1

            # Заполняем self.image построчно, начиная с верхнего левого края
            done_h = 0  # Сколько высоты сделано
            for i in range(h_times):
                if done_h >= self.rect.h:  # Из-за округления мы можем закончить раньше
                    break
                incerted_h = min(src_image_h, self.rect.h - done_h)

                done_w = 0  # Сколько ширины сделано
                for j in range(w_times):
                    if done_w >= self.rect.w:  # Из-за округления мы можем закончить раньше
                        break
                    incerted_w = min(src_image_w, self.rect.w - done_w)  # Вставляемая ширина на текущем шаге

                    self.image.blit(inserted_image, (done_w, done_h), (0, 0, incerted_w, incerted_h))

                    done_w += incerted_w
                done_h += incerted_h

        self.alignment = alignment

        if self.alignment == ALIGNMENT_HIGH_LEFT:
            pass
        elif self.alignment == ALIGNMENT_CENTER:
            self.rect.x = self.rect.x - self.image.get_width() / 2
            self.rect.y = self.rect.y - self.image.get_height() / 2

    def draw(self) -> None:
        if self.active:
            if self.shadow_image:
                self.window_surface.blit(self.shadow_image, (self.rect.x + 2, self.rect.y + 2))
            self.window_surface.blit(self.image, (self.rect.x, self.rect.y))
