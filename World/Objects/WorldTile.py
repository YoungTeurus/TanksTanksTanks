import logging

from Consts import sprite_w, sprite_h
from Files import get_script_dir
from World.Objects.Collisionable import Collisionable

# путь_до_текстуры is_solid
ID = {
    0: [None,                                        False],
    1: ["\\assets\\textures\\bricks.png",            True],
    2: ["\\assets\\textures\\strong_bricks.png",     True],
    3: ["\\assets\\textures\\bricks.png",            True],
    4: ["\\assets\\textures\\bricks.png",            True],
    5: ["\\assets\\textures\\bricks.png",            True],
    6: [None,                                        False],
    7: [None,                                        False],
}


class WorldTile(Collisionable):
    """
    Класс, реализующий тайлы мира.
    Всего есть 7 тайлов:
    0 - пустой тайл
    1 - кирпичи
    2 - укреплённые кирпичи
    3 - вода
    4 - кусты
    5 - база игрока
    6 - место спавна игрока
    7 - место спавна врагов
    """
    def __init__(self, world):
        super().__init__(world)

    def set_tile(self, tile_id, x, y):
        """
        Выполняет полную настройку выбранного тайла, а так же заносит данный тайл в массивы для отрисовки и
        обработки столкновений (если нужно).
        :param tile_id: ID данного тайла для выбора свойств и текстур
        :param x: Кооридната x по сетке
        :param y: Кооридната y по сетке
        :return:
        """
        self.set_by_id(tile_id)
        self.set_pos(x, y)
        self.set_size(sprite_w, sprite_h)

        self.parent_world.all_tiles.append(self)
        if self.is_solid:
            self.parent_world.collisionable_objects.append(self)

    def set_by_id(self, tile_id):
        if tile_id in ID:
            if (path_to_img := ID[tile_id][0]) is not None:  # Если у тайла есть текстура
                self.set_image(get_script_dir() + path_to_img)
            self.set_is_soild(ID[tile_id][1])

        else:
            logging.error("There was an attempt to set wrong tile_id for tile: {}".format(tile_id))

    def set_pos(self, x, y):
        """
        Установка позиции в мире
        :param x: Кооридната x по сетке
        :param y: Кооридната y по сетке
        :return:
        """
        super().set_pos(x*sprite_w, y*sprite_h)
