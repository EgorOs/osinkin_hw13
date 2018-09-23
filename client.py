#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_STREAM
from tkinter import *
from threading import Thread, Lock
from time import time, sleep
from messages import *


class InterfaceThread(Thread):
    """ Processes the graphical interface"""

    def __init__(self, client, username, queue, lock, stop_signal):
        Thread.__init__(self)
        self.client = client
        self.username = username
        self.user_id = time()
        self.queue = queue
        self.stop_signal = stop_signal
        self.daemon = True
        print("Logged as: %s" % self.username)
        print("Your id: %s" % self.user_id)

    def run(self):
        class GUI(Tk):
            def __init__(self, client, username, user_id, queue, stop_signal):
                super().__init__()
                self.client = client
                self.username = username
                self.user_id = user_id
                self.queue = queue
                self.stop_signal = stop_signal
                self.title('User: %s #%s' % (self.username, self.user_id))
                self.geometry("540x480")
                sbar = Scrollbar(self)
                textbar = Text(self, height=4, width=50)
                userbar = Text(self, height=4, width=25)
                sbar.pack(side=RIGHT, fill=Y)
                sbar.config(command=textbar.yview)
                textbar.config(yscrollcommand=sbar.set, state=DISABLED)
                userbar.config(state=DISABLED)
                textbar.pack(side=LEFT, fill=Y)
                userbar.pack(side=LEFT, fill=Y)
                userbar_lst = set()
                while True:
                    if self.stop_signal:
                        break

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

                        elif msg_type == ADD_CLIENT:
                            userbar.config(state=NORMAL)
                            userbar_lst.add(username)
                            userbar.delete('1.0', END)
                            userbar.insert(END, '%s\n' % (content))
                            textbar.insert(END, '>>> %s joined conversation\n' % username)
                            userbar.config(state=DISABLED)

                        elif msg_type == REMOVE_CLIENT:
                            userbar.config(state=NORMAL)
                            userbar_lst.add(username)
                            userbar.delete('1.0', END)
                            userbar.insert(END, '%s\n' % (content))
                            textbar.insert(END, '>>> %s left conversation\n' % username)
                            userbar.config(state=DISABLED)

                        elif msg_type == USER_MSG:
                            textbar.insert(END, '%s: %s\n' % (username, content))

                        # Prevent from writing into GUI
                        textbar.config(state=DISABLED)
                    self.update()
                    sleep(0.005)

        gui = GUI(self.client, self.username, self.user_id, self.queue, self.stop_signal)
        gui.destroy()

class ProcessThread(Thread):
    """ Manages data input and output """

    def __init__(self, client, address, username, queue, lock, stop_signal):
        Thread.__init__(self)
        self.client = client
        self.address = address
        self.username = username
        self.queue = queue
        self.stop_signal = stop_signal
        self.daemon = True

    def wait_for_data(self, queue):
        """ Listen for incoming messages """

        while True:
            if self.stop_signal:
                break
            data = self.client.recv(10000)
            queue.append(data)

    def receive_input(self):
        """ Await for user input """
        while True:
            content = input('>>> ')
            if content.startswith('@'):
                msg = Message(self.username, content, PRIVATE_MSG).create()
                self.client.send(msg)
            elif content == '!exit':
                self.stop_signal.append(True)
                break
            else:
                msg = Message(self.username, content, USER_MSG).create()
                self.client.send(msg)



    def run(self):
        """ Runs message receiver and user input reader in separate threads """

        data_receiver = Thread(target=self.wait_for_data, args=[self.queue], daemon=True)
        data_receiver.start()
        user_input_proc = Thread(target=self.receive_input, daemon=True)
        user_input_proc.start()
        if self.stop_signal:
            data_receiver.join()
            user_input_proc.join()


class ChatClient:

    def __init__(self, address):
        self.address = address
        self.client = socket(AF_INET, SOCK_STREAM)
        self.username = None
        self.queue = []
        self.stop_signal = []

    def log_in(self):
        self.client.connect(self.address)

        # Authorize user on server
        while True:
            self.username = input('Enter your username:\n>>> ')
            new_client_msg = Message(self.username, '', ADD_CLIENT).create()
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
        processing = ProcessThread(self.client, self.address, self.username, self.queue, lock, self.stop_signal)
        gui = InterfaceThread(self.client, self.username, self.queue, lock, self.stop_signal)
        processing.start()
        gui.start()
        print("Type your message here:")
        while True:
            # Immitate main thread
            if self.stop_signal:
                break
            sleep(2)
        processing.join()
        gui.join()

try:
    address = ('localhost', 6782)
    app = ChatClient(address)
    app.log_in()
    app.run()
except KeyboardInterrupt:
    print("Shutting down")