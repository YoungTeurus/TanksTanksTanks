from typing import List

max_messages = 15  # Максимальное количество сообщений


class ChatHistory:
    messages: List[str] = None  # Массив сообщений
    has_new_messages: bool = None  # Флаг наличия нового, не обработанного сообщения

    def __init__(self):
        self.messages = []
        self.has_new_messages = False

    def add_message(self, msg: str):
        self.messages.insert(0, msg)
        if len(self.messages) > max_messages:
            self.messages.pop(max_messages)
        self.has_new_messages = True

    def read_messages(self) -> list:
        self.has_new_messages = False
        return self.messages
