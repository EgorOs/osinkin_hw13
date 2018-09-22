#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_STREAM
from tkinter import *
from threading import Thread, Lock
from time import time, sleep
from messages import *


class InterfaceThread(Thread):

    def __init__(self, client, username, queue, lock):
        Thread.__init__(self)
        self.client = client
        self.username = username
        self.user_id = time()
        self.queue = queue
        print("Logged as: %s" % self.username)
        print("Your id: %s" % self.user_id)

    def run(self):
        class GUI(Tk):
            def __init__(self, client, username, user_id, queue):
                super().__init__()
                self.client = client
                self.username = username
                self.user_id = user_id
                self.queue = queue
                self.title('User: %s #%s' % (self.username, self.user_id))
                self.geometry("360x480")
                sbar = Scrollbar(self)
                textbar = Text(self, height=4, width=50)
                sbar.pack(side=RIGHT, fill=Y)
                sbar.config(command=textbar.yview)
                textbar.config(yscrollcommand=sbar.set, state=DISABLED)
                textbar.pack(side=LEFT, fill=Y)
                while True:
                    if self.queue:
                        textbar.config(state=NORMAL)
                        data = queue.pop(0)
                        header, content = msg_decode(data)
                        username, msg_type = header.split('|')
                        if msg_type == PRIVATE_MSG:
                            target_user, *msg_content = content.split(' ')
                            target_user = target_user[1::]
                            content = ' '.join(msg_content)
                            textbar.insert(END, '%s/%s: %s\n' % (username, target_user, content))
                        elif msg_type == USER_MSG or msg_type != ERROR_MSG:
                            textbar.insert(END, '%s: %s\n' % (username, content))

                        # Prevent from writing into GUI
                        textbar.config(state=DISABLED)
                    self.update()
                    sleep(0.02)

        gui = GUI(self.client, self.username, self.user_id, self.queue)

class ProcessThread(Thread):

    def __init__(self, client, adress, username, queue, lock):
        Thread.__init__(self)
        self.client = client
        self.adress = adress
        self.username = username
        self.queue = queue

    def wait_for_data(self, queue):
        while True:
            data = self.client.recv(10000)
            queue.append(data)

    def recieve_input(self):
        while True:
            content = input('>>> ')
            if content.startswith('@'):
                msg = Message(self.username, content, PRIVATE_MSG).create()
            else:
                msg = Message(self.username, content, USER_MSG).create()
            self.client.send(msg)



    def run(self):

        # Run message reciever and user input reader in separate threads
        data_reciever = Thread(target=self.wait_for_data, args=[self.queue])
        data_reciever.start()
        user_input_proc = Thread(target=self.recieve_input)
        user_input_proc.start()


class ChatClient:

    def __init__(self, adress):
        self.adress = adress
        self.client = socket(AF_INET, SOCK_STREAM)
        self.username = None
        self.queue = []

    def log_in(self):
        self.client.connect(self.adress)

        # Authorize user on server
        while True:
            self.username = input('Enter your username:\n>>> ')
            new_client_msg = Message(self.username, 'new_user', ADD_CLIENT).create()
            self.client.send(new_client_msg)
            echo = self.client.recv(10000)
            header, content = msg_decode(echo)
            username, msg_type = header.split('|')
            if msg_type != ERROR_MSG:
                self.queue.append(echo)
                break
            else:
                # Print error message if user already logged in
                print(content)

    def run(self):
        lock = Lock()
        processing = ProcessThread(self.client, self.adress, self.username, self.queue, lock)
        gui = InterfaceThread(self.client, self.username, self.queue, lock)
        processing.start()
        gui.start()
        print("Type your message here:")

try:
    adress = ('localhost', 6782)
    app = ChatClient(adress)
    app.log_in()
    app.run()
except KeyboardInterrupt:
    print("Shutting down")