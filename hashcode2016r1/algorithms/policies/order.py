from abc import ABCMeta, abstractmethod
import random
import time

from ..common import calculate_distance


class OrderPolicy(object):
    __metaclass__ = ABCMeta

    def __init__(self, algorithm):
        self.algorithm = algorithm

    @abstractmethod
    def select_order(self, drone, order_list):
        pass


class RandomOrderPolicy(OrderPolicy):
    """
    Select orders in a random fashion.
    """
    def __init__(self, algorithm):
        super(RandomOrderPolicy, self).__init__(algorithm)
        self.random = random.SystemRandom(time.time())

    def select_order(self, drone, order_list):
        return order_list[self.random.randint(0, len(order_list)-1)]


class ModeledCostOrderPolicy(OrderPolicy):
    """
    Select the order that minimizes the traveling distance for the given drone.
    """
    def select_order(self, drone, order_list):
        warehouse_list = self.algorithm.data_dict[u'warehouse']
        max_distance = self.algorithm.data_dict[u'max_order_to_warehouse_distance']

        delivered_ratio = 0.0
        undelivered_ratio = 1.0 - delivered_ratio
        travel_distance = 0.0
        normalized_travel_distance = travel_distance / (2*max_distance)
        location_score = self._calculate_location_score(location)


    def _calculate_location_score(self, location):
        warehouse_list = self.algorithm.data_dict[u'warehouse']

        # the normalized average of the distance between this location to all warehouses.
        max_order_to_warehouse_distance = self.algorithm.data_dict[u'max_order_to_warehouse_distance']
        distance_sum = 0.0
        for warehouse in warehouse_list:
            distance = calculate_distance(location, warehouse[u'location'])
            normalized_distance = float(distance) / max_order_to_warehouse_distance
            distance_sum += normalized_distance
        distance_sum /= len(warehouse_list)

        return distance_sum
