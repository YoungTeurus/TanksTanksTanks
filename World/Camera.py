from pygame import Rect

from Consts import sprite_w, sprite_h


class Camera:
    """
    Класс, инкапсулирующий rect для улучшения логики
    """
    visible_rect = None
    parent_world = None

    def __init__(self, parent_world):
        self.parent_world = parent_world
        self.visible_rect = Rect(0, 0,
                                 self.parent_world.parent_surface.get_width(),
                                 self.parent_world.parent_surface.get_height())

    def set_size(self, width, height):
        self.visible_rect.size = (width, height)

    def set_coords(self, x, y):
        self.visible_rect.x, self.visible_rect.y = x, y

    def get_size(self):
        return self.visible_rect.size

    def get_coords(self):
        return self.visible_rect.x, self.visible_rect.y

    def move(self, dx, dy):
        self.set_coords(self.get_coords()[0] - dx, self.get_coords()[1] - dy)

    def center_on(self, game_object):
        """
        Центрует камеру на определённом объекте
        :param game_object: Объект, на котороый нужно отцентроваться
        :return:
        """
        new_coords = self.get_coords_if_would_be_centered_on(game_object)
        self.set_coords(new_coords[0], new_coords[1])
        #self.set_coords(
        #    -game_object.float_x - game_object.object_rect.width / 2 + self.parent_world.parent_surface.get_width() / 2,
        #    -game_object.float_y - game_object.object_rect.height / 2 + self.parent_world.parent_surface.get_height() / 2)

    def smart_center_on(self, game_object):
        (new_camera_x, new_camera_y) = self.get_coords_if_would_be_centered_on(game_object)  # Конечное положение камеры
        was_x_corrected = was_y_corrected = False  # Была ли одна из координат изменена
        world_w, world_h = self.parent_world.world_map.size_w, self.parent_world.world_map.size_h
        surface_width = self.parent_world.parent_surface.get_width()
        surface_height = self.parent_world.parent_surface.get_height()

        if self.check_if_tile_is_visible(0, None, new_camera_x, new_camera_y) and not was_x_corrected:
            # Видим ли левую стенку с новыми координатами
            # Если видим, то:
            if self.can_set_coords_and_dont_see_each_tile(0, None, world_w-1, None):
                # Можем ли не видеть левую и правую стенку
                # Если да, то устанавливаем x координату правее левой стенки
                new_camera_x = 0 - sprite_w
            else:
                # Если нет, то устанавливает x координату по середине между стенками
                # new_camera_x = (world_w/2) * sprite_w
                new_camera_x = surface_width / 2 - (world_w * sprite_w) / 2
            was_x_corrected = True
        if self.check_if_tile_is_visible(world_w-1, None, new_camera_x, new_camera_y) and not was_x_corrected:
            # Видим ли правую стенку с новыми координатами
            # Если видим, то:
            if self.can_set_coords_and_dont_see_each_tile(0, None, world_w-1, None):
                # Можем ли не видеть левую и правую стенку
                # Если да, то устанавливаем x координату левее правой стенки
                new_camera_x = -(world_w - 1) * sprite_w + surface_width
            else:
                # Если нет, то устанавливает x координату по середине между стенками
                new_camera_x = surface_width / 2 - (world_w * sprite_w) / 2
            was_x_corrected = True
        if self.check_if_tile_is_visible(None, 0, new_camera_x, new_camera_y) and not was_y_corrected:
            # Видим ли верхнюю стенку с новыми координатами
            # Если видим, то:
            if self.can_set_coords_and_dont_see_each_tile(None, 0, None, world_h - 1):
                # Можем ли не видеть верхнюю и нижнюю стенку
                # Если да, то устанавливаем x координату ниже верхней стенки
                new_camera_y = 0 - sprite_h
            else:
                # Если нет, то устанавливает x координату по середине между стенками
                new_camera_y = surface_height / 2 - (world_h * sprite_h) / 2
                # new_camera_y = (world_h/2) * sprite_h
            was_y_corrected = True
        if self.check_if_tile_is_visible(None, world_h - 1, new_camera_x, new_camera_y) and not was_y_corrected:
            # Видим ли ниюжнюю стенку с новыми координатами
            # Если видим, то:
            if self.can_set_coords_and_dont_see_each_tile(None, 0, None, world_h - 1):
                # Можем ли не видеть верхнюю и нижнюю стенку
                # Если да, то устанавливаем x координату выше нижней стенки
                new_camera_y = -(world_h - 1) * sprite_h + surface_height
            else:
                # Если нет, то устанавливает x координату по середине между стенками
                new_camera_y = surface_height / 2 - (world_h * sprite_h) / 2
                # new_camera_y = -(world_h/2) * sprite_h
            was_y_corrected = True

        # После всего этого устанавливаем координаты камеры
        self.set_coords(new_camera_x, new_camera_y)

    def get_coords_if_would_be_centered_on(self, game_object):
        """
        Возвращает координаты камеры, если бы она была отцентрована на определённом объекте
        :param game_object: Объект, на котороый нужно отцентроваться
        :return:
        """
        return (-game_object.float_x - game_object.object_rect.width / 2 + self.parent_world.parent_surface.get_width() / 2,\
               -game_object.float_y - game_object.object_rect.height / 2 + self.parent_world.parent_surface.get_height() / 2)

    def check_if_tile_is_visible(self, tile_x, tile_y, new_camera_x=None, new_camera_y=None):
        """
        Проверяет виден ли тайл с координатами (tile_x,tile_y) в данный момент на экране.
        Если какая-то из координат = None, значит она не важна для проверки
        :param new_camera_y: Новое положение камеры по y
        :param new_camera_x: Новое положение камеры по x
        :param tile_y: Координата y тайла
        :param tile_x: Координата x тайла
        :return: Возваращает true - если да, false - если нет
        """
        camera_x = self.visible_rect.x
        if new_camera_x is not None:
            camera_x = new_camera_x
        camera_y = self.visible_rect.y
        if new_camera_y is not None:
            camera_y = new_camera_y
        if tile_x is not None:
            pos_x_on_screen = tile_x * sprite_w + camera_x
            surface_width = self.parent_world.parent_surface.get_width()
            # Проверка левой границы экрана
            if pos_x_on_screen + sprite_w < 0:
                return False
            # Проверка правой границы экрана
            if pos_x_on_screen > surface_width:
                return False
        if tile_y is not None:
            pos_y_on_screen = tile_y * sprite_h + camera_y
            surface_height = self.parent_world.parent_surface.get_height()
            # Проверка верхней границы экрана
            if pos_y_on_screen + sprite_h < 0:
                return False
            # Проверка нижней границы экрана
            if pos_y_on_screen > surface_height:
                return False
        return True

    def check_if_left_side_visible(self):
        """
        Определяет, видна ли в данный момент левая граница карты
        :return:
        """
        # Виден ли столбик с координатой x = 0
        return self.check_if_tile_is_visible(0, None)

    def check_if_whole_world_can_be_visible(self):
        world_w = self.parent_world.world_map.size_w
        world_h = self.parent_world.world_map.size_h

        if not self.check_if_tile_is_visible(0, None):
            return False
        if not self.check_if_tile_is_visible(None, 0):
            return False
        if not self.check_if_tile_is_visible(world_w, None):
            return False
        if not self.check_if_tile_is_visible(None, world_h):
            return False
        return True

    def can_set_coords_and_dont_see_other_tile(self, x1, y1, x2, y2):
        """
        Проверяет, можно ли установить камеру так, чтобы можно было видеть один тайл, не видя другой.
        Если x1 и x2 = None, значит не важна координата x, если y1 и y2 = None, значит не важна координата y
        :param x1: Координаты 1-ого тайла
        :param y1:
        :param x2: Координаты 2-ого тайла
        :param y2:
        :return: True - если можно, False - если нельзя
        """
        if x1 is not None and x2 is not None:
            distance_between_tiles_x = abs(x1 - x2) * sprite_w
            if distance_between_tiles_x < self.parent_world.parent_surface.get_width():
                # Если расстояние по x меньше ширины экрана
                return False
        if y1 is not None and y2 is not None:
            distance_between_tiles_y = abs(y1 - y2) * sprite_h
            if distance_between_tiles_y < self.parent_world.parent_surface.get_height():
                # Если расстояние по y меньше высоты экрана
                return False
        return True

    def can_set_coords_and_dont_see_each_tile(self, x1, y1, x2, y2):
        """
        Проверяет, можно ли установить камеру так, чтобы можно было не видеть оба тайла.
        Если x1 и x2 = None, значит не важна координата x, если y1 и y2 = None, значит не важна координата y
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :return:
        """
        _x1, _x2 = None, None
        _y1, _y2 = None, None
        if x1 is not None and x2 is not None:
            _x1, _x2 = x1, x2 + 1
        if y1 is not None and y2 is not None:
            _y1, _y2 = y1, y2 + 1
        return self.can_set_coords_and_dont_see_other_tile(_x1, _y1, _x2, _y2)