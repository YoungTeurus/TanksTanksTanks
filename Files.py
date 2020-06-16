import os
import sys
import inspect
from typing import Dict, Optional, List

import pygame
from pygame.mixer import Sound
from pygame.surface import Surface

from Consts import SOUNDS_VOLUME, MAPS


class ImageLoader:
    """
    Класс, который подгружает все изображения для того, чтобы не подгружать изоражения по одиночке.
    """

    loaded_images: Dict[str, Surface] = dict()

    def __init__(self):
        path_to_images = get_script_dir() + "\\assets\\textures\\"

        # Рекурсивный обход, если нужен будет:
        # for path, subdirs, files in os.walk(path_to_images):
        #     print(path, subdirs, files)
        #     # for name in files:
        #     #     print("{name} - {path}".format(name=name, path=os.path.join(path, name)))

        image_files_list = os.listdir(path_to_images)
        for image_file in image_files_list:
            if not image_file.endswith(".png"):
                continue
            path_to_image = path_to_images + image_file
            image_file = image_file.split(".")[0]
            self.loaded_images[image_file] = pygame.image.load(path_to_image).convert_alpha()

    def get_image_by_name(self, name) -> Optional[Surface]:
        """
        Возвращает Surface с указанным именем, если такой был найден и загружен.
        :param name: Название файла звука.
        :return: Sound или None.
        """
        if name in self.loaded_images:
            return self.loaded_images[name]
        return None


class SoundLoader:
    """
    Класс, который подгружает все звуки.
    """
    sounds: Dict[str, Sound] = None  # Все звуки в формате "название_файла" - "звук"

    def __init__(self) -> None:
        self.sounds = dict()

        path_to_sounds = get_script_dir() + "\\assets\\sounds\\"
        sound_files_list = os.listdir(path_to_sounds)
        for sound_file in sound_files_list:
            path_to_sound = path_to_sounds + sound_file
            sound_file = sound_file.split(".")[0]  # Название файла - всё, что находится до ПЕРВОЙ точки.
            self.sounds[sound_file] = Sound(path_to_sound)
            self.sounds[sound_file].set_volume(SOUNDS_VOLUME)

    def get_sound_by_name(self, name: str) -> Optional[Sound]:
        """
        Возвращает Sound с указанным именем, если такой был найден и загружен.
        :param name: Название файла звука.
        :return: Sound или None.
        """
        if name in self.sounds:
            return self.sounds[name]
        return None

    def play_sound(self, name: str) -> None:
        """
        Проигрывает  звук с указанным именем, если такой был найден и загружен.
        :param name: Название файла звука.
        """
        sn = self.get_sound_by_name(name)
        if sn is not None:
            sn.play()


class MapLoader:
    """
    Класс, подгружающий карты в массив MAPS заполняя его
    """
    def __init__(self):
        path_to_maps = get_script_dir() + "\\assets\\maps\\"

        maps_files_list: List[str] = os.listdir(path_to_maps)
        for (i, map_file_name) in enumerate(maps_files_list):
            if not map_file_name.endswith(".txt"):
                continue
            MAPS[i] = {
                "path": f"\\assets\\maps\\{map_file_name}",
                "name": f"{map_file_name.split('.')[0]}"
            }

    def get_map_id_by_name(self, name: str) -> Optional[int]:
        """
        Возвращает карту, если карта с таким именем файла была загружена.
        :param name: Имя необходимой карты.
        :return: Запись карты.
        """
        for map_id in MAPS:
            if MAPS[map_id]["name"] == name:
                return map_id


script_dir = None


# Возвращает путь до папки скрипта
# НЕ ПЕРЕМЕЩАТЬ ДАННЫЙ КОД ИЗ КОРНЕВОЙ ПАПКИ!
def get_script_dir(follow_symlinks=True):
    global script_dir
    if script_dir is not None:
        return script_dir
    if getattr(sys, 'frozen', False):  # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    script_dir = os.path.dirname(path)
    return script_dir
