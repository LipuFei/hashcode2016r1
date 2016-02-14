from abc import ABCMeta, abstractmethod
import random
import time


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


class MinTravelDistanceOrderPolicy(OrderPolicy):
    """
    Select the order that minimizes the traveling distance for the given drone.
    """
    def select_order(self, drone, order_list):
        pass


class MaxCarryWeightOrderPolicy(OrderPolicy):
    """
    Select the order that maximizes the carrying-weight for the given drone.
    """
    def select_order(self, drone, order_list):
        pass
