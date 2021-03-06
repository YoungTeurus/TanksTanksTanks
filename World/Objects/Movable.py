from World.Objects.RotatableWorldObject import RotatableWorldObject


class Movable(RotatableWorldObject):
    """
    Класс двигаемых объектов
    """

    def __init__(self, world, tileset_name: str):
        super().__init__(world, tileset_name)

    def move(self, dx, dy):
        self.set_pos(self.float_x+dx, self.float_y+dy)
        # self.object_rect.x += dx
        # self.object_rect.y += dy
