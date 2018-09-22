#!/usr/bin/env python3

PRIVATE_MSG = '0'
USER_MSG = '1'
ADD_CLIENT = '2'
REMOVE_CLIENT = '3'
ERROR_MSG = '4'


class Message:

    def __init__(self, username, content, message_type):
        self.username = username
        self.content = content
        self.message_type = message_type
        if self.username:
            # If user has logged in add username to header
            self.msg_header = '%s|%s\n' % (username, message_type)
        else:
            # Pass empty header
            self.msg_header = '\n'

    def create(self):
        # Add target user to header too
        self.msg = self.msg_header + self.content
        return self.msg.encode('utf-8')


def msg_decode(data):
    header, *content = data.decode('utf-8').split('\n')
    return header, ''.join(content).lstrip('\n')


def msg_encode(header, content):
    data = header + '\n' + content
    return data.encode('utf-8')


if __name__ == '__main__':
    pass