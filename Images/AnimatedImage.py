import pygame

from Consts import image_w, image_h, TILES


class AnimatedImage:
    """
    Класс, расширяющий Surface, позволяющий на лету менять отображаемую картинку.
    Предварительно необходимо указать какие картинки входят в состав анимации.
    """

    frames = None  # Массив кадров
    width = image_w  # Ширина каждого кадра
    height = image_h  # Высота каждого кадра
    size = (image_w, image_h)
    current_frame = 0
    timer = None
    frozen = False  # Остановлена ли анимация

    def __init__(self):
        self.frames = []

    def froze(self):
        self.frozen = True

    def unfroze(self):
        self.frozen = False

    def add_frame(self, image_surface):
        self.frames.append(image_surface)

    def add_timer(self, delay):
        self.timer = AnimationTimer(delay)

    def next(self):
        if self.frozen:
            return
        if self.timer is not None:
            if not self.timer.is_ready():
                self.timer.tick()
                return
            self.timer.reset()
        self.current_frame = (self.current_frame + 1) % self.frames.__len__()

    def get_current(self):
        return self.frames[self.current_frame]

    def get_current_and_next(self):
        self.next()
        return self.frames[self.current_frame]

    def get_size(self):
        return image_w, image_h


class AnimationTimer:
    current_delay = 0
    max_delay = 0

    def __init__(self, max_delay):
        self.current_delay = self.max_delay = max_delay

    def tick(self):
        self.current_delay = max(0, self.current_delay - 1)

    def is_ready(self):
        return self.current_delay <= 0

    def reset(self):
        self.current_delay = self.max_delay
