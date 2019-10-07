import logging

class Validate:
    def message_raw(self, msg_type, flag, content):
        if isinstance(msg_type, str) and \
            (msg_type is 'request' or msg_type is 'response') and \
            isinstance(flag, int) and \
            (flag > 0 and flag < 100) and  \
            isinstance(content, list):
            return True
        logging.error('Validate: Message raw content variable is not allowed!')
        return False
