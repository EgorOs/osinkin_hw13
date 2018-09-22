#!/usr/bin/env python3


class Message:

    def __init__(self, username, content):
        self.username = username
        self.content = content
        if self.username:
            # If user has logged in add username to header
            self.msg_header = self.username + '\n'
        else:
            # Pass empty header
            self.msg_header = '\n'

    def create(self):
        # Add target user to header too
        self.msg = self.msg_header + self.content
        return self.msg.encode('utf-8')


def msg_decode(data):
    header, content = data.decode('utf-8').split('\n')
    return header, ''.join(content).lstrip('\n')


def msg_encode(header, content):
    data = header + '\n' + content
    return data.encode('utf-8')


if __name__ == '__main__':
    pass