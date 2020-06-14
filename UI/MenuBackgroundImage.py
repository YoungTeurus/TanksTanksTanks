from pygame.surface import Surface

from UI.MenuObjects.MenuImage import MenuImage, FILL


class MenuBackgroundImage(MenuImage):
    size_w: float = None  # Размеры окна
    size_h: float = None  # Размеры окна

    max_x_change_possible: float = None  # Максимально возможное смещение по x
    max_y_change_possible: float = None  # Максимально возможное смещение по y

    current_x_change: float = 0  # Текущее смещение по x
    current_y_change: float = 0  # Текущее смещение по y

    collected_x: float = 0  # Накопленное смещение по x
    collected_y: float = 0  # Накопленное смещение по y

    speed: float = None  # Скорость смещения за один Update

    def __init__(self, window_surface: Surface, size: tuple, speed: float, image: Surface,
                 one_image_size: tuple = None):
        self.size_w, self.size_h = size[0], size[1]
        self.speed = speed

        self.max_x_change_possible = size[0] * 0.25
        self.max_y_change_possible = size[1] * 0.25

        super().__init__(window_surface, (0 - self.max_x_change_possible,
                                          0 - self.max_y_change_possible,
                                          size[0] * 1.5, size[1] * 1.5), image,
                         type=FILL, one_image_size=one_image_size)

    def update(self):
        self.current_x_change += self.speed
        self.current_y_change += self.speed
        if self.current_x_change >= self.max_x_change_possible:
            self.current_x_change = 0
            self.collected_x = 0
            self.rect.x = 0 - self.max_x_change_possible
        else:
            self.collected_x += self.speed
            self.rect.x += self.collected_x // 1
            self.collected_x = self.collected_x % 1

        if self.current_y_change >= self.max_y_change_possible:
            self.current_y_change = 0
            self.collected_y = 0
            self.rect.y = 0 - self.max_y_change_possible
        else:
            self.collected_y += self.speed
            self.rect.y += self.collected_y // 1
            self.collected_y = self.collected_y % 1
