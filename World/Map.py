import logging

from Consts import MAPS
from Files import get_script_dir
from World.Objects.WorldTile import WorldTile


class Map:
    """
    Класс, реализующий текстовую карту, объектную карту, процесс загрузки и сохранения карты
    """

    parent_world = None

    text_map = []  # Здесь хранится карта в виде числовоых значения
    player_spawn_places = []
    enemy_spawn_places = []
    player_bases = []  # Базы игрока
    # object_map = []
    size_w = None
    size_h = None

    def __init__(self, world):
        self.parent_world = world

    def load_from_file(self, filename):
        try:
            with open(get_script_dir() + filename, "r") as file:
                rows = 0
                while (current_line := file.readline()).__len__() > 0:
                    temp_list = []

                    # Вычисление ширины мира
                    # Подразумевается, что мир одинаково широк во всех местах
                    if self.size_w is None:
                        self.size_w = current_line.replace("  ", " ").split(" ").__len__()

                    for symbol in current_line.replace("  ", " ").replace("\n", "").split(" "):
                        temp_list.append(symbol)

                    self.text_map.append(temp_list)
                    rows += 1
                self.size_h = rows
        except FileNotFoundError:
            logging.error("There was an attempt to open a file but it does not exist: {}".format(filename))

    def create_object_map(self):
        if self.size_w is not None: # Если мир загружен (размер не пуст)
            tile_x = 0
            tile_y = 0
            for row in self.text_map:
                for tile in row:
                    temp_tile = WorldTile(self.parent_world)
                    temp_tile.set_tile(int(tile), tile_x, tile_y)
                    tile_x += 1
                tile_y += 1
                tile_x = 0
        else:
            logging.error("There was an attempt to create objects for a world by it was not loaded.")

    def load_by_id(self, map_id):
        if map_id in MAPS:
            # Очистка перед загрузкой
            self.text_map.clear()
            self.player_spawn_places.clear()
            self.enemy_spawn_places.clear()
            self.size_w = None
            self.size_h = None

            self.load_from_file(MAPS[map_id])
            self.create_object_map()
        else:
            logging.error("There was an attempt to load a world by id but it does not exist: {}".format(map_id))

    def check(self):
        if len(self.player_spawn_places) <= 0:
            logging.error("There is no available spawn places for players!")
        if len(self.enemy_spawn_places) <= 0:
            logging.warning("There is no available spawn places for enemies!")
