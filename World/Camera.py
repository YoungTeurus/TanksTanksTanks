from pygame import Rect


class Camera:
    """
    Класс, инкапсулирующий rect для улучшения логики
    """
    visible_rect = None
    parent_world = None

    def __init__(self, parent_world):
        self.parent_world = parent_world
        self.visible_rect = Rect(0, 0,
                                 self.parent_world.parent_surface.width,
                                 self.parent_world.parent_surface.height)

    def setSize(self, width, height):
        self.visible_rect.size = (width, height)

    def setCoords(self, x, y):
        self.visible_rect.x, self.visible_rect.y = x, y

    def getSize(self):
        return self.visible_rect.size

    def getCoords(self):
        return self.visible_rect.x, self.visible_rect.y
