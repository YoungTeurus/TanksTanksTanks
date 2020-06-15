from typing import List

from Consts import GREY, BUTTON_YELLOW, BLACK, MAX_PLAYER_TANK_HP
from UI.ConstPopups import chat_textbox_x, chat_textbox_y, chat_textbox_height, chat_textbox_margin, chat_textbox_width, \
    chat_font_size
from UI.MenuObjects.Label import Label
from UI.MenuObjects.MenuImage import MenuImage
from UI.MenuObjects.MenuObjectWithText import LEFT_ALIGNMENT
from UI.MenuObjects.PopupBox import PopupBox

one_message_height = chat_textbox_height  # Высота одного сообщения
max_messages_in_chatlog = 10  # Максимум одновременного отображения сообщений в чатлоге.

chatlog_x = chat_textbox_x  # X чатолога
chatlog_width = chat_textbox_width  # Ширина чатлога
chatlog_height = one_message_height * max_messages_in_chatlog  # Высота чатлога
chatlog_y = chat_textbox_y - chatlog_height - chat_textbox_margin  # Y чатолога


class GUI(PopupBox):
    parent_game = None  # Игра, в которой отображается данный GUI
    chatlog: PopupBox = None  # Чатлог

    lifes: List[MenuImage] = None  # Жизни игрока

    is_chatlog_folded: bool = None  # Свёрнут ли чатлог?

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

        self.is_chatlog_folded = True

        self.lifes = []
        for i in range(MAX_PLAYER_TANK_HP):
            image_life = MenuImage(parent_game.window_surface, (chatlog_x + 48*i, chatlog_y - 64, 48, 48),
                                   parent_game.image_loader.get_image_by_name("life"), shadow=True)
            self.lifes.append(image_life)

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
        lifes = max(min(MAX_PLAYER_TANK_HP, new_lifes), 0)  # 0 <= new_lifes <= MAX_PLAYER_TANK_HP
        for life in self.lifes[lifes:]:
            life.active = False
        for life in self.lifes[:lifes]:
            life.active = True

    def draw(self):
        if self.is_chatlog_folded:
            pass
        else:
            # Отрисовка чатлога
            self.chatlog.draw()
        for life in self.lifes:
            life.draw()

    def update(self):
        self.update_chatlog()  # Апдейт чатлога
