from Files import get_script_dir
from World.Objects.Collisionable import Collisionable
from World.Objects.Tank import Tank


class World:
    """
    Класс, содеражащий в себе информацию об отображаемой карте и всех объектах на ней.
    """

    player = None  # Игрок
    parent_surface = None  # Та поверхность, на которой будет происходить отрисовка всего мира

    all_objects = []
    collisionable_objects = []

    def __init__(self, parent_surface):
        self.parent_surface = parent_surface

        self.player = Tank(self)
        self.player.set_pos(50, 50)
        self.player.set_size(64, 64)
        self.player.set_image(get_script_dir() + "\\tank.png")
        self.player.set_is_soild(True)

        self.all_objects.append(self.player)
        self.collisionable_objects.append(self.player)

        just_an_object = Collisionable(self)
        just_an_object.set_pos(150,150)
        just_an_object.set_size(64, 64)
        just_an_object.set_image(get_script_dir() + "\\tank.png")
        just_an_object.set_is_soild(True)

        self.all_objects.append(just_an_object)
        self.collisionable_objects.append(just_an_object)
        # self.player.set_angle("LEFT")

    def draw(self):
        for obj in self.all_objects:
            obj.draw()
