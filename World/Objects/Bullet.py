from Consts import TANK_DEFAULT_SPEED_PER_SECOND, sprite_w, sprite_h
from Files import get_script_dir
from World.Objects.Tank import Tank
from World.Objects.Actable import Actable
from World.Objects.Collisionable import Collisionable, remove_if_exists_in
from World.Objects.WorldTile import WorldTile


class Bullet(Collisionable, Actable):
    parent_tank = None  # Танк, который выстрелил данной пулей
    bullet_direction = None  # Направление, в котором летит пуля

    speed = TANK_DEFAULT_SPEED_PER_SECOND * 2

    def __init__(self, world, parent_tank):
        super().__init__(world)
        self.parent_tank = parent_tank
        self.on_collision = bullet_collision
        self.set_is_soild(False)  # Пуля - твёрдая
        # TODO: сделать пулю твёрдой, чтобы они могли врезаться друг в друга

    def create(self):
        """
        Данный метод помещает пулю в нужные массивы, даёт ей направление движения
        :return:
        """
        self.set_pos(self.parent_tank.float_x + self.parent_tank.object_rect.width / 2,
                     self.parent_tank.float_y + self.parent_tank.object_rect.height / 2)
        self.set_image(get_script_dir() + "\\assets\\textures\\bullet.png")

        self.bullet_direction = self.parent_tank.last_direction
        self.set_angle(self.bullet_direction)  # Установка поворота спрайта
        self.set_size(sprite_w / 12, sprite_h / 4)  # Относительный размер пули от размера спрайта

        # Поправка координат для того, чтобы пуля вылетала из ствола
        if self.bullet_direction == "UP":
            self.set_pos(self.parent_tank.float_x + self.parent_tank.object_rect.width / 2,
                         self.parent_tank.float_y)
        if self.bullet_direction == "DOWN":
            self.set_pos(self.parent_tank.float_x + self.parent_tank.object_rect.width / 2,
                         self.parent_tank.float_y + self.parent_tank.object_rect.height)
        if self.bullet_direction == "LEFT":
            self.set_pos(self.parent_tank.float_x,
                         self.parent_tank.float_y + self.parent_tank.object_rect.height / 2)
        if self.bullet_direction == "RIGHT":
            self.set_pos(self.parent_tank.float_x + self.parent_tank.object_rect.width,
                         self.parent_tank.float_y + self.parent_tank.object_rect.height / 2)

        self.parent_world.collisionable_objects.append(self)
        self.parent_world.actable_object.append(self)
        self.parent_world.all_bullets.append(self)

    def destroy(self):
        """
        Данный метод удаляет пулю из нужных массивов
        """
        remove_if_exists_in(self, self.parent_world.collisionable_objects)
        remove_if_exists_in(self, self.parent_world.actable_object)
        remove_if_exists_in(self, self.parent_world.all_bullets)

    def act(self):
        self.check_and_process_collisions(self.parent_world.collisionable_objects)  # Проверяем коллижены
        self.bullet_move()  # Двигаем пулю

    def bullet_move(self):
        if self.bullet_direction == "UP":
            self.move(0, -self.speed)
        if self.bullet_direction == "DOWN":
            self.move(0, self.speed)
        if self.bullet_direction == "LEFT":
            self.move(-self.speed, 0)
        if self.bullet_direction == "RIGHT":
            self.move(self.speed, 0)

def bullet_collision(bullet, obj):
    if obj is bullet.parent_tank:  # Не реагируем на коллизию с танком, который выстрелил
        return
    if obj.is_solid:  # Если объект твёрдый
        if isinstance(obj, Tank):
            # Если столкнулись с танком:
            pass
        if isinstance(obj, WorldTile):
            # Если столкнулись с тайлом мира
            obj.get_hit()
        bullet.destroy()
        bullet.parent_tank.set_current_delay_before_fire_to_zero()
