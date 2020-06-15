import pygame

from World.Objects.Movable import Movable


class Collisionable(Movable):
    is_solid = None

    on_collision = None  # Функция, которая выполняется с каждым пересечённым объектом

    def __init__(self, world, tileset_name: str):
        super().__init__(world, tileset_name)
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
