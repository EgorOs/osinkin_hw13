#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_STREAM
from messages import msg_decode, msg_encode
from threading import *

class ChatServer:

    def __init__(self, adress):
        self.adress = adress
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind(adress)
        self.server.listen(2)

    def client_process(self, client):
        while True:
            try:
                data = client.recv(1000)
                if data:
                    header, content = msg_decode(data)
                    print(content)
                    new_data = msg_encode(header, content)
                    client.sendall(new_data)
                else:
                    # Client disconnected
                    # wait for new client
                    print('no data')
                    client.close()
                    client, addr = self.server.accept()
                # client.close()
            except Exception as e:
                print(e)

    def run(self):
        while True:
            client, addr = self.server.accept()
            Thread(target=self.client_process, args=[client]).start()
        # while True:
        #     try:
        #         data = client.recv(1000)
        #         if data:
        #             header, content = msg_decode(data)
        #             print(content)
        #             new_data = msg_encode(header, content)
        #             client.sendall(new_data)
        #         else:
        #             # Client disconnected
        #             # wait for new client
        #             print('no data')
        #             client.close()
        #             client, addr = self.server.accept()
        #         # client.close()
        #     except Exception as e:
        #         print(e)

adress = ('localhost', 6783)
try:
    app = ChatServer(adress)
    app.run()
except Exception as e:
    print(e)
    app.server.close()