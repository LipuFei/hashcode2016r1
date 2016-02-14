from abc import ABCMeta, abstractmethod
import random
import time


class DronePolicy(object):
    __metaclass__ = ABCMeta

    def __init__(self, algorithm):
        self.algorithm = algorithm
        self.drone_count = len(self.algorithm.drone_list)

    @abstractmethod
    def get_current_drone(self):
        pass

    @abstractmethod
    def switch_to_next_drone(self):
        pass


class RoundRobinDronePolicy(DronePolicy):
    """
    Select drones in a round-robin fashion.
    """
    def __init__(self, algorithm):
        super(RoundRobinDronePolicy, self).__init__(algorithm)
        self.current_drone_idx = 0

    def get_current_drone(self):
        return self.algorithm.drone_list[self.current_drone_idx]

    def switch_to_next_drone(self):
        self.current_drone_idx = (self.current_drone_idx + 1) % self.drone_count


class RandomDronePolicy(DronePolicy):
    """
    Select drones in a random fashion.
    """
    def __init__(self, algorithm):
        super(RandomDronePolicy, self).__init__(algorithm)
        self.random = random.SystemRandom(time.time())
        self.current_drone_idx = 0
        self.switch_to_next_drone()

    def get_current_drone(self):
        return self.algorithm.drone_list[self.current_drone_idx]

    def switch_to_next_drone(self):
        self.current_drone_idx = self.random.randint(0, self.drone_count-1)


class MinNextTurnsDronePolicy(DronePolicy):
    """
    Select the drone with the minimum next_turn value.
    """
    def __init__(self, algorithm):
        super(MinNextTurnsDronePolicy, self).__init__(algorithm)
        self.current_drone_idx = 0

    def get_current_drone(self):
        return self.algorithm.drone_list[self.current_drone_idx]

    def switch_to_next_drone(self):
        min_drone = None
        for drone in self.algorithm.drone_list:
            if min_drone is None:
                min_drone = drone
            elif min_drone[u'next_turn'] > drone[u'next_turn']:
                min_drone = drone

        self.current_drone_idx = min_drone[u'id']
