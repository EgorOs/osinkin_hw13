#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_STREAM
from messages import *
from threading import *

class ChatServer:

    def __init__(self, address):
        self.address = address
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind(address)
        self.server.listen(5)
        self.client_by_addr = {}
        self.user_by_addr = {}

    def client_process(self, client, server, addr, client_by_addr, user_by_addr):
        while True:
            try:
                data = client.recv(10000)
                if data:
                    header, content = msg_decode(data)
                    username, msg_type = header.split('|')
                    if msg_type == ADD_CLIENT:
                        # Add new user
                        if username not in user_by_addr.values():
                            user_by_addr[addr] = username
                            response = Message(username, '<joined conversation>', ADD_CLIENT).create()
                        else:
                            # Send error message if user already logged in
                            response = Message(username, 'User already logged in', ERROR_MSG).create()
                        for key in client_by_addr.keys():
                            client_by_addr[key].sendall(response)

                    elif msg_type == USER_MSG:
                        for key in client_by_addr.keys():
                            new_data = msg_encode(header, content)
                            client_by_addr[key].sendall(new_data)

                    elif msg_type == PRIVATE_MSG:
                        target_user = content.split(' ')[0]
                        target_user = target_user[1::]
                        if target_user in user_by_addr.values():
                            addr_by_user = {v:k for k,v in user_by_addr.items()}
                            target_addr = addr_by_user[target_user]
                            new_data = msg_encode(header, content)
                            # Copy message to own screen
                            client_by_addr[addr].sendall(new_data)
                            # Send message
                            client_by_addr[target_addr].sendall(new_data)
                        else:
                            new_data = msg_encode(header, '<No such user>')
                            # Print error
                            client_by_addr[addr].sendall(new_data)
                        
                else:
                    # Client disconnected
                    del client_by_addr[addr]
                    del user_by_addr[addr]
                    print('Client with address', addr, 'has disconnected')
                    client.close()
                    break

            except Exception as e:
                print(e)
                break

    def run(self):
        while True:
            client, addr = self.server.accept()
            print('Connected client with address', addr)
            self.client_by_addr[addr] = client
            Thread(target=self.client_process, args=[client, self.server, addr, 
                self.client_by_addr, self.user_by_addr]).start()

address = ('localhost', 6782)
try:
    print('Started server at', address)
    print('Press CTRL+C to shut down')
    app = ChatServer(address)
    app.run()
except KeyboardInterrupt:
    print('Shutting down')
    app.server.close()
except Exception as e:
    print(e)
    app.server.close()