import logging

from Consts import sprite_w, sprite_h
from Files import get_script_dir
from World.Objects.Collisionable import Collisionable, remove_if_exists_in

# название_текстуры is_solid is_passable_for_bullets is_destroyable hits_to_destroy
ID = {
    0: [None,                       False, True,   False, 0],
    1: ["bricks.png",               True,  False,  True , 3],
    2: ["strong_bricks.png",        True,  False,  False, 3],
    3: ["water.png",                True,  True,   False, 0],
    4: ["bush.png",                 False, True,   False, 0],
    5: ["base.png",                 True,  False,  False, 0],
    6: [None,                       False, True,   False, 0],
    7: [None,                       False, True,   False, 0]
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

    is_destroyable = False
    is_passable_for_bullets = False

    hits_to_destroy = 0
    current_hitpoints = 0

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

    def get_hit(self, direction_of_bullet):
        if self.is_destroyable:
            if direction_of_bullet == "UP":
                # Если ударили снизу
                self.set_size(self.object_rect.width, self.object_rect.height - sprite_h/4)
            if direction_of_bullet == "DOWN":
                # Если ударили сверху
                super().set_pos(self.float_x, self.float_y + sprite_h/4)
                self.set_size(self.object_rect.width, self.object_rect.height - sprite_h/4)
            if direction_of_bullet == "RIGHT":
                # Если ударили слева
                super().set_pos(self.float_x + sprite_h / 4, self.float_y)
                self.set_size(self.object_rect.width - sprite_w / 4, self.object_rect.height)
            if direction_of_bullet == "LEFT":
                # Если ударили справа
                self.set_size(self.object_rect.width - sprite_w / 4, self.object_rect.height)
            if self.object_rect.width <= 0 or self.object_rect.height <= 0:
                self.destroy()
            # self.current_hitpoints -= 1
            # if self.current_hitpoints <= 0:
            #     self.destroy()

    def destroy(self):
        remove_if_exists_in(self, self.parent_world.all_tiles)
        if self.is_solid:
            remove_if_exists_in(self, self.parent_world.collisionable_objects)

    def set_by_id(self, tile_id):
        if tile_id in ID:
            if (img_name := ID[tile_id][0]) is not None:  # Если у тайла есть текстура
                self.set_image(img_name)
            self.set_is_soild(ID[tile_id][1])
            self.is_passable_for_bullets = ID[tile_id][2]
            self.is_destroyable = ID[tile_id][3]
            self.hits_to_destroy = ID[tile_id][4]
            self.current_hitpoints = self.hits_to_destroy

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
