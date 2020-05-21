import json
import socket
import socketserver
from threading import Thread
from time import sleep
from typing import Optional, List

from Consts import SOCKET_DEBUG


class ServerFinder(Thread):
    client_ip: str = None  # IP-адрес клиента
    client_port: int = None  # Порт клиента

    ip_list: list = None  # Список ip-адресов для проверки наличия сервера

    good_ip_list: List[tuple] = None  # Список ip-адресов и названий серверов с обратным ответом

    sent_all: bool = False  # Флаг окончания рассылки запросов на все IP

    is_ready: bool = False  # Флаг окончания сканирования

    server_Listener: Optional[socketserver.UDPServer] = None

    def __init__(self, client_ip, client_port):
        super().__init__()
        self.client_ip = client_ip
        self.client_port = client_port

        self.ip_list = []
        self.good_ip_list = []

    def add_all_local_ips(self):
        self.ip_list.append("127.0.0.1")
        for i in range(0, 256):
            self.ip_list.append("192.168.0.{}".format(i))  # Все компьютеры локальной сети

    def _start_checking(self):

        class Sender(Thread):
            serverchecker = self

            def run(self):
                for ip in self.serverchecker.ip_list:
                    self.ask_for_ok(ip)
                self.serverchecker.sent_all = True

            def ask_for_ok(self, ip: str):
                host, port = ip, 9998
                data_dict = dict()
                data_dict["type"] = "ask_for_ok"
                data_dict["ip"] = self.serverchecker.client_ip
                data_dict["port"] = self.serverchecker.client_port
                data = json.dumps(data_dict)
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(data.encode(), (host, port))
                if SOCKET_DEBUG:
                    print("Sent:     {}".format(data))

        class Listener(socketserver.BaseRequestHandler):
            serverchecker = self
            is_running = True  # Флаг активности Listener-а

            def handle(self):
                data = self.request[0].decode()  # Вытаскиваем data
                data_dict = json.loads(data)  # Делаем из этого словарь
                if SOCKET_DEBUG:
                    print("{} wrote: ".format(self.client_address[0]), end="")
                    print(data_dict)  # Вывод дебаг-информации

                if data_dict["type"] == "ok":
                    # Если сервер отправил ok
                    # Запоминаем IP и название сервера
                    self.serverchecker.good_ip_list.append((data_dict["ip"], data_dict["server_name"]))

            def serve_forever(self):
                while self.is_running:
                    self.handle()

            def stop_serve(self):
                self.is_running = False

        s = Sender()

        HOST, PORT = self.client_ip, self.client_port
        self.server_Listener = socketserver.UDPServer((HOST, PORT), Listener)  # Созадём севрер
        server_thread = Thread(target=self.server_Listener.serve_forever)  # Создаём поток
        server_thread.setDaemon(True)
        server_thread.start()  # Запускаем поток

        s.run()

        while not self.sent_all:
            pass

        sleep(1.5)  # Выжидаем полторы секунды до ответа серверов

        self.server_Listener.shutdown()
        self.server_Listener.server_close()

        self.is_ready = True

    def run(self) -> None:
        self._start_checking()

    def force_shutdown(self):
        if self.server_Listener is not None:
            self.server_Listener.shutdown()
            self.good_ip_list = []
            self.is_ready = True
            print("Прервано!")


if __name__ == "__main__":
    sc = ServerFinder("127.0.0.1", 12314)
    sc.add_all_local_ips()
    sc.start()
    sleep(1)
    sc.force_shutdown()
    sleep(1)
    # while not sc.is_ready:
    #     print(sc.is_ready)
    #     sleep(1)
    print(sc.is_ready)
    # ip_list = sc.start_checking()
    # print(ip_list)
