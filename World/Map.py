import logging
from typing import Dict, List

from Consts import MAPS, SERVER_MAPS
from Files import get_script_dir
from World.Objects.WorldTile import WorldTile


class Map:
    """
    Класс, реализующий текстовую карту, объектную карту, процесс загрузки и сохранения карты
    Также хранит все свойства карты из текстового файла.
    """

    parent_world = None

    map_id = None

    text_map = []  # Здесь хранится карта в виде числовоых значения
    player_spawn_places = []
    enemy_spawn_places = []
    player_bases: List[WorldTile] = []  # Базы игрока

    size_w = None
    size_h = None

    object_map: list = []  # Двумерный массив для хранения всех тайлов карты (для синхронизации)

    property_map: bool = False  # Если данный флаг = True, данная карта не должна загружать мир,
    # она используется только для подгрузки свойств
    properties: Dict[str, object] = None  # Словарь для хранения свойств карты
    # Возможные properties: title, max_players

    def __init__(self, world):
        # Использование None в качестве World будет подгружать только свойства карты
        if world is None:
            self.property_map = True
        else:
            self.parent_world = world
        self.properties = dict()

    def load_from_file(self, filename: str) -> None:
        try:
            with open(get_script_dir() + filename, "r", encoding='utf-8') as file:
                rows = 0
                while (current_line := file.readline()).__len__() > 0:
                    if current_line[0] == "#":
                        key_arg_array: List[str] = current_line[1:-1].split("=")  # Отрезаем "#" и "\n" от строки
                        # Свойство карты начинается с #
                        self.properties[key_arg_array[0]] = key_arg_array[1]
                        continue
                    else:
                        if self.property_map:  # Если карта свойст, то пропускаем другие строки
                            break  # СЧИТАЕМ, ЧТО СВОЙСТВА ИДУТ ПОДРЯД С НАЧАЛА ФАЙЛА
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
            print("There was an attempt to open a file but it does not exist: {}".format(filename))

    def create_object_map(self) -> None:
        if self.property_map:
            return
        self.object_map.clear()  # Отчистка object_map-а.
        if self.size_w is not None: # Если мир загружен (размер не пуст)
            tile_x = 0
            tile_y = 0
            for row in self.text_map:
                object_row = []
                for tile in row:
                    temp_tile = WorldTile(self.parent_world)
                    temp_tile.set_tile(int(tile), tile_x, tile_y)
                    object_row.append(temp_tile)
                    tile_x += 1
                self.object_map.append(object_row)
                tile_y += 1
                tile_x = 0
        else:
            logging.error("There was an attempt to create objects for a world by it was not loaded.")

    def load_by_id(self, map_id: int, server_map: bool = False) -> None:
        """
        Загрузка мира по ID.
        :param map_id: ID мира из Consts.
        """
        self.map_id = map_id

        if server_map:
            # Если грузим серверную карту
            map_dict = SERVER_MAPS
        else:
            map_dict = MAPS

        if map_id in map_dict:
            # Очистка перед загрузкой
            self.text_map.clear()
            self.player_spawn_places.clear()
            self.enemy_spawn_places.clear()
            self.size_w = None
            self.size_h = None

            self.load_from_file(map_dict[map_id])
        else:
            logging.error("There was an attempt to load a world by id but it does not exist: {}".format(map_id))

    def check(self) -> None:
        if len(self.player_spawn_places) <= 0:
            logging.error("There is no available spawn places for players!")
        if len(self.enemy_spawn_places) <= 0:
            logging.warning("There is no available spawn places for enemies!")


class MapLoader:
    """
    Класс, который проходится по картам для того, чтобы подгрузить их свойства.
    """
    maps: List[Map] = None  # Массив карт

    def load_maps(self) -> None:
        """
        Загружает карты во внутренний массив.
        """
        if self.maps is None:
            self.maps = []
        else:
            self.maps.clear()
        for map_id in MAPS:
            temp_map = Map(None)
            temp_map.load_by_id(map_id)
            self.maps.append(temp_map)

    def get_maps(self) -> List[Map]:
        """
        Возвращает карты, если они были загружены.
        """
        assert self.maps is not None
        return self.maps
