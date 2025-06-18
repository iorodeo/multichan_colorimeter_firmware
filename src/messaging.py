import sys
import json
import supervisor

class MessageReceiver:

    def __init__(self):
        self.buffer = []
        self.error_flag = False
        self.error_count = 0

    @property
    def error(self):
        return self.error_flag

    def update(self):
        new_message = False
        while supervisor.runtime.serial_bytes_available:
            byte = sys.stdin.read(1)
            if byte != '\n':
                self.buffer.append(byte)
            else:
                message_str = ''.join(self.buffer)
                self.buffer = []
                new_message = True
                break
        message_dict = {}
        self.error_flag = False
        if new_message:
            try:
                message_dict = json.loads(message_str)
            except ValueError:
                self.error_flag = True
                self.error_count += 1
        return message_dict


def send_message(msg):
    print(json.dumps(msg))
