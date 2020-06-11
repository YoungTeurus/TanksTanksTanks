import os
import sys
import inspect

import pygame


class ImageLoader:
    """
    Класс, который подгружает все изображения для того, чтобы не подгружать изоражения по одиночке.
    """

    loaded_images = dict()

    def __init__(self):
        path_to_images = get_script_dir() + "\\assets\\textures\\"
        image_files_list = os.listdir(path_to_images)
        for image_file in image_files_list:
            path_to_image = path_to_images + image_file
            self.loaded_images.update({image_file: pygame.image.load(path_to_image).convert_alpha()})

    def get_image_by_name(self, name):
        if name in self.loaded_images:
            return self.loaded_images[name]
        return None


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
