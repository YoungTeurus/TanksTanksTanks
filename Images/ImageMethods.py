from pygame.constants import SRCALPHA
from pygame.surface import Surface


def fill_color(surface: Surface, color: tuple, max_alpha: int = 255) -> None:
    """
    Заливает картинку новым цветом, сохраняя прозрачность исходного изображения.
    :param surface: Исходное изображение.
    :param color: Цвет в виде tuple из 3-х int-ов.
    :param max_alpha: Максимальная непрозрачность получившегося изображения.
    """
    w, h = surface.get_size()
    r, g, b = color
    for x in range(w):
        for y in range(h):
            a = min(surface.get_at((x, y))[3], max_alpha)
            surface.set_at((x, y), (r, g, b, a))


def add_color(src_surface: Surface, color: tuple, alpha: int = 128) -> Surface:
    """
    Накладывает color на переданный surface, добавляя цвет к исходному изображению.
    :param src_surface: Исходное изображение.
    :param color: Накладываемый цвет.
    :param alpha: Прозрачность накладываемого цвета.
    :return: Изменённое изображение.
    """
    src_size = src_surface.get_size()
    return_surface = Surface(src_size, SRCALPHA)
    return_surface.blit(src_surface, (0, 0))  # Исходное изображение
    add_surface = src_surface.copy()  # Копия изображения
    fill_color(add_surface, color, max_alpha=alpha)  # Заливаем копию нужным цветом
    return_surface.blit(add_surface, (0, 0))  # Накладываем копию поверх исходного изображения
    return return_surface
