from utils import Utils

class Transaction(object):
    def new(self, data):
        if self.validate(data):
            return {'index': data['index'],
                    'company_name': data['company_name'],
                    'company_user': data['company_user'],
                    'company_data': data['company_data']}
        return False

    def validate(self, data):
        tx_required_items = {   'index': int,
                                'company_name': str,
                                'company_user': str,
                                'company_data': str}
        utils = Utils()
        if utils.validate_dict_keys(data, tx_required_items) and \
            utils.validate_dict_values(data, tx_required_items):
            return True
        return False
