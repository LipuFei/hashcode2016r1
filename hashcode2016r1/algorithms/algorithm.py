from abc import ABCMeta, abstractmethod

from .common import calculate_distance, calculate_location_score


class Algorithm(object):
    __metaclass__ = ABCMeta

    def __init__(self, data_dict):
        self.data_dict = data_dict

        self.warehouse_list = []
        self.drone_list = []
        self.order_list = []

    def get_order(self, order_id):
        order = None
        for o in self.order_list:
            if o[u'id'] == order_id:
                order = o
                break
        return order

    def get_warehouse(self, warehouse_id):
        warehouse = None
        for wh in self.warehouse_list:
            if wh[u'id'] == warehouse_id:
                warehouse = wh
                break
        return warehouse

    def get_next_drone_idx(self, drone_idx):
        return (drone_idx + 1) % self.data_dict[u'drones']

    def get_product_weight(self, item_id):
        return self.data_dict[u'product_type_weights'][item_id]

    def pre_process(self):
        # distance normalizer
        self.data_dict[u'max_distance'] = calculate_distance([0, 0],
                                                             [self.data_dict[u'rows'], self.data_dict[u'columns']])

        # warehouse list
        warehouse_list = self.data_dict[u'warehouse_list']

        # drone list
        drone_list = [{u'id': i,
                       u'location': warehouse_list[0][u'location'][:],
                       u'payloads': {},
                       u'max_payload': self.data_dict[u'max_payload'],
                       u'weight': 0,
                       u'next_turn': 0}
                      for i in xrange(self.data_dict[u'drones'])]

        # order list
        max_order_to_warehouse_distance = 0.0
        order_list = self.data_dict[u'order_list']
        for order in order_list:
            # convert product types to dict and calculate total weight
            total_weight = 0
            for item in order[u'item_types']:
                total_weight += self.data_dict[u'product_type_weights'][item]
            order[u'total_weight'] = total_weight

            for wh in warehouse_list:
                distance = calculate_distance(order[u'location'], wh[u'location'])
                if max_order_to_warehouse_distance < distance:
                    max_order_to_warehouse_distance = distance

            item_types = {}
            # convert item_types into a dict
            for item in order[u'item_types']:
                if item not in item_types:
                    item_types[item] = 0
                item_types[item] += 1
            order[u'item_types'] = item_types

        self.data_dict[u'max_order_to_warehouse_distance'] = max_order_to_warehouse_distance
        # calculate the location scores
        for order in order_list:
            order[u'location_score'] = calculate_location_score(order[u'location'], warehouse_list,
                                                                max_order_to_warehouse_distance)

        self.warehouse_list = warehouse_list
        self.drone_list = drone_list
        self.order_list = order_list

    @abstractmethod
    def generate(self):
        pass
