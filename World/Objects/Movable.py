from World.Objects.RotatableWorldObject import RotatableWorldObject


class Movable(RotatableWorldObject):
    """
    Класс двигаемых объектов
    """

    def __init__(self, world):
        super().__init__(world)

    def move(self, dx, dy):
        self.object_rect.x += dx
        self.object_rect.y += dy
