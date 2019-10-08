import logging

from datetime import datetime

class Message(object):
    def create(self, msg_type, flag, content=[]):
        if self.validate(msg_type, flag, content):
            return {'msg_type': msg_type,
                    'flag': flag,
                    'content': content,
                    'timestamp': str(datetime.now())}
        else:
            return False

    def validate(self, msg_type, flag, content):
        if isinstance(msg_type, str) and \
            (msg_type is 'request' or msg_type is 'response') and \
            isinstance(flag, int) and \
            (flag > 0 and flag < 100) and  \
            isinstance(content, list):
            return True
        logging.error('Validate: Message raw content variable is not allowed!')
        return False
