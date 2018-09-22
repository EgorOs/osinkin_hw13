#!/usr/bin/env python3

from socket import socket, AF_INET, SOCK_STREAM
from tkinter import *
from threading import Thread, Lock
from time import time, sleep
from messages import Message, msg_encode, msg_decode


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
                        username = header.split(' ')[0]
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

    def run(self):
        self.client.connect(self.adress)
        while True:
            content = input('>>> ')
            msg = Message(self.username, content).create()
            self.client.send(msg)
            data = self.client.recv(1000)
            if data:
                self.queue.append(data)

class ChatClient:

    def __init__(self, adress):
        self.adress = adress
        self.client = socket(AF_INET, SOCK_STREAM)
        self.client.setblocking(1)
        self.username = None
        self.queue = []

    def log_in(self):
        self.username = input('Enter your username:\n>>> ')

    def run(self):
        lock = Lock()
        processing = ProcessThread(self.client, self.adress, self.username, self.queue, lock)
        gui = InterfaceThread(self.client, self.username, self.queue, lock)
        processing.start()
        gui.start()
        print("Type your message here:")

adress = ('localhost', 6783)
app = ChatClient(adress)
app.log_in()
app.run()