import pygame

from World.Objects.Movable import Movable


class Collisionable(Movable):
    is_solid = None

    on_collision = None  # Функция, которая выполняется с каждым пересечённым объектом

    def __init__(self, world):
        super().__init__(world)
        self.is_solid = False

    def set_is_soild(self, is_solid):
        self.is_solid = is_solid

    def set_on_collsion(self, fun):
        self.on_collision = fun

    def check_collisions(self, array_of_collisionable):
        """
        Метод возвращает массив со всеми объектами, которые пересекаются с данным объектом
        :param array_of_collisionable: Массив объектов, с которыми нужно проверить столкновения
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

    def check_and_process_collisions(self, array_of_collisionable):
        """
        Метод возвращает массив со всеми объектами, которые пересекаются с данным объектом.
        Для каждого объекта выполнится функция, записанная в on_collision.
        :param array_of_collisionable: Массив объектов, с которыми нужно проверить столкновения
        :return:
        """
        return_array = self.check_collisions(array_of_collisionable)

        if self.on_collision is not None:
            for obj in return_array:
                self.on_collision(self, obj)

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

        if (collided_objects := self.check_collisions(self.parent_world.collisionable_objects)).__len__() > 0:
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
                        previous_x = obj.float_x - self.object_rect.width
                    else:
                        # Иначе - ПРАВУЮ
                        previous_x = obj.float_x + obj.object_rect.width
                else:
                    # Если y больше x, значит пересекает вертикальную грань
                    if distance_vector.y > 0:
                        # Если y больше 0, значит пересекает ВЕРХНЮЮ грань
                        previous_y = obj.object_rect.y - self.object_rect.height
                    else:
                        # Иначе - НИЖНЮЮ
                        previous_y = obj.float_y + obj.object_rect.height

            # Если с чем-то столкнулись, возвращаем прежнее положение
            self.set_pos(previous_x, previous_y)


class Vector2:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y


def remove_if_exists_in(obj, array):
    """
    Пытается удалить объект obj из array. Если obj нет в array, возвращает false.
    :param obj: Объект, который нужно удалить.
    :param array: Массив, из которого нужно удалить.
    :return: true - если успешно удалён, false - если не был удалён
    """
    try:
        array.remove(obj)
        return True
    except ValueError:
        return False
