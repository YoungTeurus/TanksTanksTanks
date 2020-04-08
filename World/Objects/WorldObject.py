from World.Objects.Drawable import Drawable


class WorldObject(Drawable):

    parent_world = None  # Родительский мир, в котором будут отрисовываться объекты

    def __init__(self, world):
        self.parent_world = world
        super().__init__(self.parent_world.parent_imageloader)

    def draw(self, surface=None):
        """
        Отрисовка объекта в мире.
        :param surface: В данном случае не используется
        :return:
        """
        super().draw(self.parent_world.parent_surface)

    def destroy(self):
        """
        Функция, которая должна удалять объект из всех массивов, в которые он был добавлен при создании
        :return:
        """
        pass

    def __str__(self):
        return "{0} {1} {2} {3} {4} {5}".format(
            "WorldObject", self.object_rect.x, self.object_rect.y,
            self.object_rect.width, self.object_rect.height,
            "img_id"
        )
