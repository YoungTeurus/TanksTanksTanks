from typing import List

from pygame.surface import Surface


class Tileset:
    """
    Класс, хранящий группу изображений в виде сетки
    """

    grid: List[List[Surface]] = None
    width = 0
    height = 0
    size_x = 0
    size_y = 0

    def __init__(self, width, height, image: Surface):
        self.grid = []
        self.width = width
        self.height = height
        image_width, image_height = image.get_size()
        for tile_x in range(0, image_width//self.width):
            line = []
            self.grid.append(line)
            self.size_x += 1
            for tile_y in range(0, image_height//height):
                rect = (tile_x * width, tile_y * height, self.width, self.height)
                line.append(image.subsurface(rect))
                self.size_y += 1

    def get_image(self, x, y):
        if x < 0 or x > self.size_x or y < 0 or y > self.size_y:
            return None
        return self.grid[x][y]