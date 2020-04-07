from Consts import sprite_w, sprite_h
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

    size = (0, 0)

    def __init__(self, parent_surface, size):
        self.parent_surface = parent_surface
        self.size = size
        # self.player.set_angle("LEFT")

    def setup_world(self):
        self.player = Tank(self)
        self.player.set_pos(64, 64)
        self.player.set_size(sprite_w, sprite_h)
        self.player.set_image(get_script_dir() + "\\assets\\textures\\tank.png")
        self.player.set_is_soild(True)

        self.all_objects.append(self.player)
        self.collisionable_objects.append(self.player)

        # Рисование 4-х стен, ограничивающих поле
        for i in range(self.size[0]+2):
            temp_object = Collisionable(self)
            temp_object.set_pos(i * sprite_w, 0)
            temp_object.set_size(sprite_w, sprite_h)
            temp_object.set_image(get_script_dir() + "\\assets\\textures\\strong_bricks.png")
            temp_object.set_is_soild(True)
            self.all_objects.append(temp_object)
            self.collisionable_objects.append(temp_object)
        for i in range(self.size[0]+2):
            temp_object = Collisionable(self)
            temp_object.set_pos(i * sprite_w, self.size[1] * sprite_h + sprite_h)
            temp_object.set_size(sprite_w, sprite_h)
            temp_object.set_image(get_script_dir() + "\\assets\\textures\\strong_bricks.png")
            temp_object.set_is_soild(True)
            self.all_objects.append(temp_object)
            self.collisionable_objects.append(temp_object)
        for i in range(self.size[1]):
            temp_object = Collisionable(self)
            temp_object.set_pos(0, i * sprite_h + sprite_h)
            temp_object.set_size(sprite_w, sprite_h)
            temp_object.set_image(get_script_dir() + "\\assets\\textures\\strong_bricks.png")
            temp_object.set_is_soild(True)
            self.all_objects.append(temp_object)
            self.collisionable_objects.append(temp_object)
        for i in range(self.size[1]):
            temp_object = Collisionable(self)
            temp_object.set_pos((self.size[0] + 1) * sprite_w, i * sprite_h + sprite_h)
            temp_object.set_size(sprite_w, sprite_h)
            temp_object.set_image(get_script_dir() + "\\assets\\textures\\strong_bricks.png")
            temp_object.set_is_soild(True)
            self.all_objects.append(temp_object)
            self.collisionable_objects.append(temp_object)

        #for i in range(self.size[0]):
        #    for j in range(self.size[1]):
        #        temp_object = Collisionable(self)
        #        temp_object.set_pos(i*sprite_w, j*s)

        self.test_add_object(2, 2)
        self.test_add_object(2, 3)
        self.test_add_object(2, 4)
        self.test_add_object(2, 5)
        self.test_add_object(2, 6)
        self.test_add_object(2, 7)
        self.test_add_object(3, 7)
        self.test_add_object(4, 7)
        self.test_add_object(5, 7)
        self.test_add_object(6, 7)
        self.test_add_object(6, 8)
        self.test_add_object(6, 9)
        self.test_add_object(4, 4)
        self.test_add_object(3, 3)
        self.test_add_object(5, 5)

    def draw(self):
        for obj in self.all_objects:
            obj.draw()

    def test_add_object(self, x, y):
        just_an_object = Collisionable(self)
        just_an_object.set_pos(sprite_w * x + sprite_w, sprite_h * y + sprite_h)
        just_an_object.set_size(sprite_w, sprite_h)
        just_an_object.set_image(get_script_dir() + "\\assets\\textures\\bricks.png")
        just_an_object.set_is_soild(True)

        self.all_objects.append(just_an_object)
        self.collisionable_objects.append(just_an_object)
