from abc import ABCMeta, abstractmethod


class Algorithm(object):
    __metaclass__ = ABCMeta

    def __init__(self, data_dict):
        self.data_dict = data_dict

        self.warehouse_list = []
        self.drone_list = []
        self.order_list = []

    def get_next_drone_idx(self, drone_idx):
        return (drone_idx + 1) % self.data_dict[u'drones']

    def get_product_weight(self, item_id):
        return self.data_dict[u'product_type_weights'][item_id]

    def pre_process(self):
        # warehouse list
        warehouse_list = self.data_dict[u'warehouse_list']

        # drone list
        drone_list = [{u'id': i,
                       u'location': warehouse_list[0][u'location'][:],
                       u'payloads': {},
                       u'weight': 0,
                       u'next_turn': 0}
                      for i in xrange(self.data_dict[u'drones'])]

        # order list
        order_list = self.data_dict[u'order_list']
        for order in order_list:
            total_weight = 0
            for item in order[u'item_types']:
                total_weight += self.data_dict[u'product_type_weights'][item]
            order[u'total_weight'] = total_weight

            item_types = {}
            # convert item_types into a dict
            for item in order[u'item_types']:
                if item not in item_types:
                    item_types[item] = 0
                item_types[item] += 1
            order[u'item_types'] = item_types

        self.warehouse_list = warehouse_list
        self.drone_list = drone_list
        self.order_list = order_list

    @abstractmethod
    def generate(self):
        pass
