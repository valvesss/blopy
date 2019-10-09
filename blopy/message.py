import logging

from datetime import datetime
from pprint import pprint

class Message(object):
    def create(self, msg_type, flag, content=[]):
        return {'msg_type': msg_type,
                'flag': flag,
                'content': content,
                'timestamp': str(datetime.now())}

    def validate(self, message):
        if message['msg_type'] != 'request' and message['msg_type'] != 'response':
            logging.error('Message: {msg_type} is not valid!')
            return False

        if message['flag'] < 1 or message['flag'] > 100:
            logging.error('Message: {flag} is not valid!')
            return False

        if not (isinstance(message['msg_type'], str) and
                isinstance(message['flag'], int) and
                isinstance(message['content'], list)):
            logging.error('Message: {content} is not valid!')
            return False
        return True
