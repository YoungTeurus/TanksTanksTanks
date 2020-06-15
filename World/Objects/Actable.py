from World.Objects.WorldObject import WorldObject


class Actable(WorldObject):
    def __init__(self, world):
        super().__init__(world)

    def act(self):
        # Действие, которое нужно делать каждый кадр
        pass
