from typing import List

from pygame.surface import Surface

from Consts import image_w, image_h
from Images.ImageMethods import fill_color, add_color
from World.Timer import Timer


class AnimatedImage:
    """
    Класс, расширяющий Surface, позволяющий на лету менять отображаемую картинку.
    Предварительно необходимо указать какие картинки входят в состав анимации.
    """

    frames: List[Surface] = None  # Массив кадров
    width = image_w  # Ширина каждого кадра
    height = image_h  # Высота каждого кадра
    current_frame: int = None  # Текущий кадр анимации
    cycles_count: int = None  # Количество совершённых циклов анимации
    timer = None
    frozen = False  # Остановлена ли анимация

    def __init__(self):
        self.current_frame = 0
        self.cycles_count = 0
        self.frames = []

    def set_size(self, size: tuple):
        self.width = size[0]
        self.height = size[1]

    def froze(self):
        self.frozen = True

    def unfroze(self):
        self.frozen = False

    def add_frame(self, image_surface: Surface):
        self.frames.append(image_surface)

    def add_timer(self, delay):
        self.timer = Timer(delay)

    def set_color(self, color: tuple) -> None:
        """
        Меняет цвет каждого кадра на указанный.
        :param color: Цвет в виде 3-х чисел.
        """
        for frame in self.frames:
            fill_color(frame, color)

    def add_color(self, color: tuple, alpha: int = 128) -> None:
        """
        Добавляет цвет к каждому кадру.
        :param color: Цвет в виде 3-х чисел.
        :param alpha: Прозрачность накладываемого цвета.
        """
        for i_frame in range(len(self.frames)):
            self.frames[i_frame] = add_color(self.frames[i_frame], color, alpha=alpha)

    def next(self):
        if self.frozen:
            return
        if self.timer is not None:
            if not self.timer.is_ready():
                self.timer.tick()
                return
            self.timer.reset()
        self.current_frame += 1
        if self.current_frame > len(self.frames):
            self.current_frame = 0
            self.cycles_count += 1
        # self.current_frame = (self.current_frame + 1) % self.frames.__len__()

    def get_current(self):
        try:
            return self.frames[self.current_frame]
        except IndexError:  # Если что-то не так с текущим кадром
            return self.frames[0]

    def get_current_and_next(self):
        self.next()
        return self.frames[self.current_frame]

    def get_size(self):
        return image_w, image_h
