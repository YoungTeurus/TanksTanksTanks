import json
import socket
import socketserver
from threading import Thread
from time import sleep

from Consts import SOCKET_DEBUG


class ServerChecker(Thread):
    client_ip: str = None  # IP-адрес клиента
    client_port: int = None  # Порт клиента

    ip_list: list = None  # Список ip-адресов для проверки наличия сервера

    good_ip_list: list = None  # Список ip-адресов с обратным ответом

    sent_all: bool = False  # Флаг окончания рассылки запросов на все IP

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

    def start_checking(self):
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

            def handle(self):
                data = self.request[0].decode()  # Вытаскиваем data
                data_dict = json.loads(data)  # Делаем из этого словарь
                if SOCKET_DEBUG:
                    print("{} wrote: ".format(self.client_address[0]), end="")
                    print(data_dict)  # Вывод дебаг-информации

                if data_dict["type"] == "ok":
                    # Если сервер отправил ok
                    self.serverchecker.good_ip_list.append(data_dict["ip"])  # Запоминаем IP сервера

        s = Sender()

        HOST, PORT = self.client_ip, self.client_port
        Listener = socketserver.UDPServer((HOST, PORT), Listener)  # Созадём севрер
        server_thread = Thread(target=Listener.serve_forever)  # Создаём поток
        server_thread.setDaemon(True)
        server_thread.start()  # Запускаем поток

        s.run()

        while not self.sent_all:
            pass

        sleep(3)  # Выжидаем 3 секунды до ответа сервера

        Listener.timeout = 3

        print(self.good_ip_list)
        # return self.good_ip_list

    def run(self) -> None:
        self.start_checking()


if __name__ == "__main__":
    sc = ServerChecker("127.0.0.1", 12314)
    sc.add_all_local_ips()
    sc.start()
    for i in range(100):
        print(i)
        sleep(0.1)
    # ip_list = sc.start_checking()
    # print(ip_list)
