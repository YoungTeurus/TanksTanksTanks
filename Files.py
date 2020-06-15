import os
import sys
import inspect
from typing import Dict, Optional

import pygame
from pygame.mixer import Sound
from pygame.surface import Surface

from Consts import SOUNDS_VOLUME


class ImageLoader:
    """
    Класс, который подгружает все изображения для того, чтобы не подгружать изоражения по одиночке.
    """

    loaded_images: Dict[str, Surface] = dict()

    def __init__(self):
        path_to_images = get_script_dir() + "\\assets\\textures\\"
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
