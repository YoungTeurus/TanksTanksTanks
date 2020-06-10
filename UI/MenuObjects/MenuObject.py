from pygame.surface import Surface

SKIP_EVENT = -1  # Используется для PopupBox-а


class MenuObject:
    window_surface: Surface = None  # Поверхность окна

    def draw(self):
        pass

    def handle_event(self, event):
        pass

    def update(self):
        pass
