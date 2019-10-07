import logging

from validate import Validate
from datetime import datetime

class Content:
    validate = Validate()
    def create_message(self, msg_type, flag, content):
        if self.validate.message_raw(msg_type, flag, content):
            return {'msg_type': msg_type,
                    'flag': flag,
                    'content': content,
                    'timestamp': str(datetime.now())}
        return False
