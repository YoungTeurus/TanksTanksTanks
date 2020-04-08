import pygame

from World.Objects.Movable import Movable


class Collisionable(Movable):
    is_solid = None

    def __init__(self, world):
        super().__init__(world)
        self.is_solid = False

    def set_is_soild(self, is_solid):
        self.is_solid = is_solid

    def check_collsions(self, array_of_collisionable):
        """
        Метод возвращает массив со всеми объектами, которые пересекаются с данным объектом
        :param array_of_collisionable:
        :return:
        """
        return_array = []
        for collisionable_object in array_of_collisionable:
            if collisionable_object is self:  # Если проверяем на столкновение с самим собой
                continue
            # Если проверяемый объект "твёрдый" и пересекает текущий объект, заносим его в массив для вывода
            if collisionable_object.is_solid and self.object_rect.colliderect(collisionable_object.object_rect):
                return_array.append(collisionable_object)
        return return_array

    def smart_move(self, dx, dy):
        """
        Перемещение, непозволяющее "въехать" в другие collisionable объекты
        :param dx: Перемещение по оси x
        :param dy: Перемещение по оси y
        :return:
        """

        # Запоминаем предыдущее положение
        previous_x = self.float_x
        previous_y = self.float_y
        # previous_rect = pygame.Rect.copy(self.object_rect)

        super().move(dx, dy)

        if (collided_objects := self.check_collsions(self.parent_world.collisionable_objects)).__len__() > 0:
            for obj in collided_objects:
                distance_vector = Vector2
                distance_vector.x = obj.object_rect.x + (obj.object_rect.width / 2) \
                                    - (self.object_rect.x + (self.object_rect.width / 2))
                distance_vector.y = obj.object_rect.y + (obj.object_rect.height / 2) \
                                    - (self.object_rect.y + (self.object_rect.height / 2))
                if abs(distance_vector.x) > abs(distance_vector.y):
                    # Если x больше y, значит пересекает горизонтальную грань
                    if distance_vector.x > 0:
                        # Если x больше 0, значит пересекает ЛЕВУЮ грань
                        # previous_rect.x = obj.object_rect.x - previous_rect.width
                        previous_x = obj.float_x - self.object_rect.width
                    else:
                        # Иначе - ПРАВУЮ
                        # previous_rect.x = obj.object_rect.x + obj.object_rect.width
                        previous_x = obj.float_x + obj.object_rect.width
                else:
                    # Если y больше x, значит пересекает вертикальную грань
                    if distance_vector.y > 0:
                        # Если y больше 0, значит пересекает ВЕРХНЮЮ грань
                        # previous_rect.y = obj.object_rect.y - previous_rect.height
                        previous_y = obj.object_rect.y - self.object_rect.height
                    else:
                        # Иначе - НИЖНЮЮ
                        # previous_rect.y = obj.object_rect.y + obj.object_rect.height
                        previous_y = obj.float_y + obj.object_rect.height

            # Если с чем-то столкнулись, возвращаем прежнее положение
            self.set_pos(previous_x, previous_y)
            # self.object_rect = previous_rect


class Vector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
