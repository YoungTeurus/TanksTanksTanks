import pygame

from Consts import targetFPS, DARK_GREY
from Menu.MenuObjects.Button import Button
from Menu.MenuObjects.Label import Label
from Menu.MenuObjects.TextBox import TextBox


class Menu:

    is_running = None  # Флаг запущенного меню

    objects = None  # Массив объектов меню

    def __init__(self, window_surface):
        self.window_surface = window_surface  # Основная поверхность

        self.is_running = True

        self.clock = pygame.time.Clock()

        self.objects = []

        button_1 = Button(self.window_surface, pos=(100, 50, 100, 50), text="Button 1", color=(192, 60, 60),
                          selected_color=(215, 120, 120), font_size=24)
        button_2 = Button(self.window_surface, pos=(100, 115, 100, 50), text="Button 2", color=(60, 192, 60),
                          selected_color=(120, 215, 120), active=False, font_size=24)
        button_3 = Button(self.window_surface, pos=(100, 180, 100, 50), text="Unlock Button 2", color=(60, 60, 192),
                          selected_color=(120, 120, 215), text_color=(230, 230, 230),
                          function=(lambda: button_2.set_active(True)), font_size=18)
        textbox_1 = TextBox(self.window_surface, pos=(100, 250, 100, 30))
        label_1 = Label(self.window_surface, font_size=24, text="Cool LABEL, click me!", pos=(100, 0, 100, 50),
                        function=(lambda: print("Clicked!")))
        self.objects.append(button_1)
        self.objects.append(button_2)
        self.objects.append(button_3)
        self.objects.append(label_1)
        self.objects.append(textbox_1)

    def main_cycle(self):
        while self.is_running:
            self.clock.tick(targetFPS)  # Требуемый FPS и соответствующая задержка
            self.window_surface.fill(DARK_GREY)

            # Обработка событий:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                for obj in self.objects:
                    obj.handle_event(event)
            keyboard_pressed = pygame.key.get_pressed()

            for obj in self.objects:
                obj.update()
                obj.draw()

            pygame.display.update()
