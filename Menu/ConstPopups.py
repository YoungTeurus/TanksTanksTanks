"""
Данный файл содержит popupbox-ы для разных целей.
"""

import pygame

from Consts import BLACK
from Menu.Menu import MAIN_MENU_BACKGROUND_COLOR, MENU_WHITE, BUTTON_YELLOW
from Menu.MenuObjects.ButtonTrigger import ButtonTrigger
from Menu.MenuObjects.Label import Label
from Menu.MenuObjects.PopupBox import PopupBox


# Всплывающее окошко "Сервер закрыт"
def add_disconnected_from_server_popupbox(game):
    game.any_popup_box = None
    # Всплывающее окно "Сервер закрыт":
    popupbox = PopupBox(game.window_surface, pos=(game.window_surface.get_width() / 2 - 100,
                                                  game.window_surface.get_height() / 2 - 50, 200, 100),
                        color=MAIN_MENU_BACKGROUND_COLOR)
    label_popupbox_title = Label(game.window_surface,
                                 pos=(popupbox.rect.x + popupbox.rect.w / 2,
                                      popupbox.rect.y + 15,
                                      0, 0),
                                 text="Отключен от сервера:", text_color=MENU_WHITE,
                                 font_size=20, font="main_menu")
    label_popupbox_title_shadow = Label(game.window_surface,
                                        pos=(popupbox.rect.x + popupbox.rect.w / 2 + 2,
                                             popupbox.rect.y + 17, 0, 0),
                                        text="Отключен от сервера:", text_color=BLACK,
                                        font_size=20, font="main_menu")
    label_popupbox_reason = Label(game.window_surface,
                                  pos=(popupbox.rect.x + popupbox.rect.w / 2,
                                       popupbox.rect.y + 45,
                                       0, 0),
                                  text="Сервер закрыт!", text_color=BUTTON_YELLOW,
                                  font_size=28, font="main_menu")
    label_popupbox_reason_shadow = Label(game.window_surface,
                                         pos=(popupbox.rect.x + popupbox.rect.w / 2 + 2,
                                              popupbox.rect.y + 47, 0, 0),
                                         text="Сервер закрыт!", text_color=BLACK,
                                         font_size=28, font="main_menu")
    label_popupbox_esc = Label(game.window_surface,
                               pos=(popupbox.rect.x + popupbox.rect.w / 2,
                                    popupbox.rect.y + 85,
                                    0, 0),
                               text="Нажмите ESC!", text_color=BUTTON_YELLOW,
                               font_size=16, font="main_menu")
    label_popupbox_esc_shadow = Label(game.window_surface,
                                      pos=(popupbox.rect.x + popupbox.rect.w / 2 + 2,
                                           popupbox.rect.y + 87, 0, 0),
                                      text="Нажмите ESC!", text_color=BLACK,
                                      font_size=16, font="main_menu")
    buttontrigger_popupbox_quit_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                                    function_list=[
                                                        remove_disconnected_from_server_popupbox_and_return_to_menu],
                                                    args_list=[game])

    popupbox.add_object(buttontrigger_popupbox_quit_esc)
    popupbox.add_object(label_popupbox_title_shadow)
    popupbox.add_object(label_popupbox_title)
    popupbox.add_object(label_popupbox_reason_shadow)
    popupbox.add_object(label_popupbox_reason)
    popupbox.add_object(label_popupbox_esc_shadow)
    popupbox.add_object(label_popupbox_esc)

    game.any_popup_box = popupbox


def remove_disconnected_from_server_popupbox_and_return_to_menu(game):
    game.any_popup_box = None
    game.return_to_menu(send_to_server=False)


# Всплывающее окошко "Ожидайте начала игры"
def add_wait_for_start_popupbox(game):
    game.any_popup_box = None
    # Всплывающее окно "Ожидайте начала игры":
    popupbox = PopupBox(game.window_surface, pos=(game.window_surface.get_width() / 2 - 150,
                                                  game.window_surface.get_height() / 2 - 75, 300, 150),
                        color=MAIN_MENU_BACKGROUND_COLOR)
    label_popupbox_title = Label(game.window_surface,
                                 pos=(popupbox.rect.x + popupbox.rect.w / 2,
                                      popupbox.rect.y + 15,
                                      0, 0),
                                 text="Вы подключёны к серверу", text_color=MENU_WHITE,
                                 font_size=20, font="main_menu")
    label_popupbox_title_shadow = Label(game.window_surface,
                                        pos=(popupbox.rect.x + popupbox.rect.w / 2 + 2,
                                             popupbox.rect.y + 17, 0, 0),
                                        text="Вы подключёны к серверу", text_color=BLACK,
                                        font_size=20, font="main_menu")
    label_popupbox_title2 = Label(game.window_surface,
                                  pos=(popupbox.rect.x + popupbox.rect.w / 2,
                                       popupbox.rect.y + 45,
                                       0, 0),
                                  text="Ожидайте начала игры", text_color=BUTTON_YELLOW,
                                  font_size=28, font="main_menu")
    label_popupbox_title2_shadow = Label(game.window_surface,
                                         pos=(popupbox.rect.x + popupbox.rect.w / 2 + 2,
                                              popupbox.rect.y + 47, 0, 0),
                                         text="Ожидайте начала игры", text_color=BLACK,
                                         font_size=28, font="main_menu")
    label_popupbox_esc = Label(game.window_surface,
                               pos=(popupbox.rect.x + popupbox.rect.w / 2,
                                    popupbox.rect.y + 125,
                                    0, 0),
                               text="Нажмите ESC, чтобы отключиться", text_color=BUTTON_YELLOW,
                               font_size=16, font="main_menu")
    label_popupbox_esc_shadow = Label(game.window_surface,
                                      pos=(popupbox.rect.x + popupbox.rect.w / 2 + 2,
                                           popupbox.rect.y + 127, 0, 0),
                                      text="Нажмите ESC, чтобы отключиться", text_color=BLACK,
                                      font_size=16, font="main_menu")
    buttontrigger_popupbox_quit_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                                    function_list=[
                                                        remove_wait_popupbox_and_return_to_menu],
                                                    args_list=[game])

    popupbox.add_object(buttontrigger_popupbox_quit_esc)
    popupbox.add_object(label_popupbox_title_shadow)
    popupbox.add_object(label_popupbox_title)
    popupbox.add_object(label_popupbox_title2_shadow)
    popupbox.add_object(label_popupbox_title2)
    popupbox.add_object(label_popupbox_esc_shadow)
    popupbox.add_object(label_popupbox_esc)

    game.any_popup_box = popupbox


def remove_wait_popupbox_for_start_popupbox(game):
    game.any_popup_box = None
    game.game_started = True


def remove_wait_popupbox_and_return_to_menu(game):
    game.any_popup_box = None
    game.return_to_menu(send_to_server=True)


# Всплывающее окошко "Сервер запущен"
def add_server_started_popupbox(game):
    game.any_popup_box = None
    # Всплывающее окно "Сервер закрыт":
    popupbox = PopupBox(game.window_surface, pos=(game.window_surface.get_width() / 2 - 100,
                                                  game.window_surface.get_height() / 2 - 50, 200, 100),
                        color=MAIN_MENU_BACKGROUND_COLOR)
    label_popupbox_title = Label(game.window_surface,
                                 pos=(popupbox.rect.x + popupbox.rect.w / 2,
                                      popupbox.rect.y + 15,
                                      0, 0),
                                 text="Сервер запущен", text_color=MENU_WHITE,
                                 font_size=20, font="main_menu")
    label_popupbox_title_shadow = Label(game.window_surface,
                                        pos=(popupbox.rect.x + popupbox.rect.w / 2 + 2,
                                             popupbox.rect.y + 17, 0, 0),
                                        text="Сервер запущен:", text_color=BLACK,
                                        font_size=20, font="main_menu")
    label_popupbox_title2 = Label(game.window_surface,
                                  pos=(popupbox.rect.x + popupbox.rect.w / 2,
                                       popupbox.rect.y + 45,
                                       0, 0),
                                  text="Ожидание клиентов", text_color=BUTTON_YELLOW,
                                  font_size=28, font="main_menu")
    label_popupbox_title2_shadow = Label(game.window_surface,
                                         pos=(popupbox.rect.x + popupbox.rect.w / 2 + 2,
                                              popupbox.rect.y + 47, 0, 0),
                                         text="Ожидание клиентов", text_color=BLACK,
                                         font_size=28, font="main_menu")
    label_popupbox_esc = Label(game.window_surface,
                               pos=(popupbox.rect.x + popupbox.rect.w / 2,
                                    popupbox.rect.y + 85,
                                    0, 0),
                               text="Нажмите ESC, чтобы закрыть сервер", text_color=BUTTON_YELLOW,
                               font_size=16, font="main_menu")
    label_popupbox_esc_shadow = Label(game.window_surface,
                                      pos=(popupbox.rect.x + popupbox.rect.w / 2 + 2,
                                           popupbox.rect.y + 87, 0, 0),
                                      text="Нажмите ESC, чтобы закрыть сервер", text_color=BLACK,
                                      font_size=16, font="main_menu")
    buttontrigger_popupbox_quit_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                                    function_list=[
                                                        remove_server_started_popupbox_and_return_to_menu],
                                                    args_list=[game])

    popupbox.add_object(buttontrigger_popupbox_quit_esc)
    popupbox.add_object(label_popupbox_title_shadow)
    popupbox.add_object(label_popupbox_title)
    popupbox.add_object(label_popupbox_title2_shadow)
    popupbox.add_object(label_popupbox_title2)
    popupbox.add_object(label_popupbox_esc_shadow)
    popupbox.add_object(label_popupbox_esc)

    game.any_popup_box = popupbox


def remove_server_started_popupbox_and_return_to_menu(game):
    game.any_popup_box = None
    game.return_to_menu(send_to_server=True)


def remove_server_started_popupbox(game):
    game.any_popup_box = None
