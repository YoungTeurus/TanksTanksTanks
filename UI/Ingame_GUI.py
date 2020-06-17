from typing import List

import pygame
from pygame.event import EventType

from Consts import GREY, BUTTON_YELLOW, BLACK, MAX_PLAYER_TANK_HP, MENU_WHITE, window_w, window_h

from UI.MenuObjects.Button import Button
from UI.MenuObjects.ButtonTrigger import ButtonTrigger
from UI.MenuObjects.Label import Label
from UI.MenuObjects.MenuImage import MenuImage
from UI.MenuObjects.MenuObjectWithText import LEFT_ALIGNMENT
from UI.MenuObjects.PopupBox import PopupBox
from UI.MenuObjects.TextBox import TextBox

chat_textbox_width = window_w / 3  # Ширина строки для отправки сообщения
chat_textbox_height = 40  # Высота строки для отправки сообщения
chat_textbox_margin = 5  # Значение отступа для строки для отправки сообщения
chat_textbox_x = 0 + chat_textbox_margin  # Положение строки для отправки сообщения по X
chat_textbox_y = window_h - chat_textbox_height - chat_textbox_margin  # Положение строки для отправки сообщения по Y
chat_font_size = 22

one_message_height = chat_textbox_height  # Высота одного сообщения
max_messages_in_chatlog = 10  # Максимум одновременного отображения сообщений в чатлоге.

chatlog_x = chat_textbox_x  # X чатолога
chatlog_width = chat_textbox_width  # Ширина чатлога
chatlog_height = one_message_height * max_messages_in_chatlog  # Высота чатлога
chatlog_y = chat_textbox_y - chatlog_height - chat_textbox_margin  # Y чатолога


class GUI(PopupBox):
    parent_game = None  # Игра, в которой отображается данный GUI
    chatlog: PopupBox = None  # Чатлог

    chat_sender: PopupBox = None  # Строка для отправки сообщения.

    current_lifes: int = None  # Количество жизней у игрока.
    lifes: List[MenuImage] = None  # Жизни игрока

    is_chatlog_folded: bool = None  # Свёрнут ли чатлог?
    is_chat_sender_shown: bool = None  # Показывается ли строка отправки сообщения

    # TODO: Может, сделать такую штуку для любой кнопки?
    is_change_chatlog_action_button_pressed: bool = False  # Флаг нажатия клавиши (для предотвращения

    # складывания/раскладывания чатлога)

    def __init__(self, parent_game):
        self.parent_game = parent_game
        super().__init__(parent_game.window_surface, pos=(0, 0, 0, 0),
                         fill=False, darken_background=False, blocking=False)

        self.chatlog = PopupBox(parent_game.window_surface,
                                pos=(chatlog_x, chatlog_y,
                                     chatlog_width, chatlog_height),
                                color=GREY, darken_background=False, blocking=False,
                                transparent=True, alpha_color=80)

        self.setup_chat_sender()

        self.is_chatlog_folded = True

        self.current_lifes = MAX_PLAYER_TANK_HP  # Начальные жизни игрока
        self.lifes = []
        for i in range(MAX_PLAYER_TANK_HP):
            image_life = MenuImage(parent_game.window_surface, (chatlog_x + 48 * i, chatlog_y - 64, 48, 48),
                                   parent_game.image_loader.get_image_by_name("life"), shadow=True)
            self.lifes.append(image_life)

    def setup_chat_sender(self) -> None:
        """
        Инициализирует поле chat_sender класса.
        """

        # class MessageSentState:
        #     message_sent = False

        # def send_msg(message_sent_state: MessageSentState):
        def send_msg():
            # if not message_sent_state.message_sent:
            #     message = textbox_message.text_str
            #     if len(message) > 0:
            #         self.parent_game.send_chat_message(message)
            #     textbox_message.text_str = ""
            #     self.hide_chat_sender()
            #     message_sent_state.message_sent = True
            message = textbox_message.text_str
            if len(message) > 0:
                self.parent_game.send_chat_message(message)
            textbox_message.text_str = ""
            self.hide_chat_sender()

        # mss = MessageSentState()

        self.chat_sender = PopupBox(self.parent_game.window_surface, pos=(0, 0, 0, 0),
                                    fill=False, darken_background=True)

        textbox_message = TextBox(self.parent_game.window_surface,
                                  pos=(chat_textbox_x, chat_textbox_y,
                                       chat_textbox_width, chat_textbox_height),
                                  empty_text="Введите сюда своё сообщение...",
                                  font="main_menu", font_size=chat_font_size,
                                  function_onEnter=send_msg,
                                  arg_onEnter=None, active=True)

        button_send_message_width = chat_textbox_width * 0.1
        button_send_message_x = chat_textbox_x + chat_textbox_width - button_send_message_width

        button_send_message_shadow = Label(self.parent_game.window_surface,
                                           pos=(button_send_message_x + 2, chat_textbox_y + 2,
                                                button_send_message_width, chat_textbox_height),
                                           text=">>", text_color=BLACK,
                                           font_size=chat_font_size, font="main_menu")
        button_send_message = Button(self.parent_game.window_surface, pos=(button_send_message_x, chat_textbox_y,
                                                                           button_send_message_width,
                                                                           chat_textbox_height),
                                     transparent=True, text_color=GREY, selected_text_color=MENU_WHITE,
                                     text=">>", font_size=chat_font_size, font="main_menu",
                                     function_onClick_list=[send_msg],
                                     args_list=[None])
        #                              args_list=[mss])

        buttontrigger_popupbox_quit_esc = ButtonTrigger(key=pygame.K_ESCAPE,
                                                        function_list=[self.hide_chat_sender],
                                                        args_list=[None])
        buttontrigger_send_message_enter = ButtonTrigger(key=pygame.K_RETURN,
                                                         function_list=[send_msg],
                                                         args_list=[None])
        #                              args_list=[mss])

        self.chat_sender.add_object(buttontrigger_popupbox_quit_esc)
        self.chat_sender.add_object(buttontrigger_send_message_enter)
        self.chat_sender.add_object(textbox_message)
        self.chat_sender.add_object(button_send_message_shadow)
        self.chat_sender.add_object(button_send_message)

        self.is_chat_sender_shown = False

    def hide_chat_sender(self):
        self.is_chat_sender_shown = False
        self.blocking = False

    def show_chat_sender(self):
        self.is_chat_sender_shown = True
        self.blocking = True

    def update_chatlog(self) -> None:
        """
        Удаляет все старые сообещния в чатлоге и создаёт новые Labels основываясь
        на chat_history в Game.
        """
        if self.parent_game.chat_history.has_new_messages:
            self.chatlog.clear()  # Очистка всех сообщений

            for (i, message) in enumerate(self.parent_game.chat_history.read_messages()):
                if i > max_messages_in_chatlog:
                    break
                temp_message_y = chatlog_y + chatlog_height - (one_message_height * (i + 1))

                temp_label_message = Label(self.parent_game.window_surface,
                                           pos=(chat_textbox_x, temp_message_y,
                                                chatlog_width, one_message_height),
                                           text=message, font_size=chat_font_size, text_color=BUTTON_YELLOW,
                                           font="main_menu", alignment=LEFT_ALIGNMENT)
                temp_label_message_shadow = Label(self.parent_game.window_surface,
                                                  pos=(chat_textbox_x + 2, temp_message_y + 2,
                                                       chatlog_width, one_message_height),
                                                  text=message, font_size=chat_font_size, text_color=BLACK,
                                                  font="main_menu", alignment=LEFT_ALIGNMENT)

                self.chatlog.add_object(temp_label_message_shadow)
                self.chatlog.add_object(temp_label_message)

    def show_chatlog(self) -> None:
        """
        Показывает (разворачивает) чатлог.
        """
        self.is_chatlog_folded = False

    def fold_chatlog(self) -> None:
        """
        Сворачивает (скрывает) чатлог.
        """
        self.is_chatlog_folded = True

    def change_chatlog_action(self):
        if not self.is_change_chatlog_action_button_pressed:
            self.is_chatlog_folded = not self.is_chatlog_folded
            self.is_change_chatlog_action_button_pressed = True

    def reset_button(self):
        self.is_change_chatlog_action_button_pressed = False

    def set_lifes(self, new_lifes: int) -> None:
        """
        Устанавливает количество видимых значков жизни.
        :param new_lifes: Целочисленное значение от 0 до MAX_PLAYER_TANK_HP.
        """
        self.current_lifes = max(min(MAX_PLAYER_TANK_HP, new_lifes), 0)  # 0 <= new_lifes <= MAX_PLAYER_TANK_HP
        for life in self.lifes[self.current_lifes:]:
            life.active = False
        for life in self.lifes[:self.current_lifes]:
            life.active = True

    def decrease_lifes(self):
        new_lifes = max(min(MAX_PLAYER_TANK_HP, self.current_lifes - 1), 0)
        self.set_lifes(new_lifes)

    def draw(self):
        if not self.is_chatlog_folded:
            # Отрисовка чатлога
            self.chatlog.draw()
        if self.is_chat_sender_shown:
            self.chat_sender.draw()
        for life in self.lifes:
            life.draw()

    def update(self):
        self.update_chatlog()  # Апдейт чатлога

        if self.is_chat_sender_shown:
            self.chat_sender.update()

        if not self.parent_game.multi:
            # Обновление жизней в одиночке
            current_player_lifes = self.parent_game.world.objects_id_dict[self.parent_game.client_world_object_id].lifes
            if self.current_lifes != current_player_lifes:
                self.set_lifes(current_player_lifes)

    def handle_event(self, event: EventType):
        if self.is_chat_sender_shown:
            self.chat_sender.handle_event(event)
