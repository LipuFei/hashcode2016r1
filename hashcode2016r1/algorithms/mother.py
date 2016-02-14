import math

from .algorithm import Algorithm
from .common import calculate_distance, sort_by_distance, get_load_cmd, get_deliver_cmd


class MotherAlgorithm(Algorithm):

    def __init__(self, data_dict, short_percent=1.0, switch_task=False):
        super(MotherAlgorithm, self).__init__(data_dict)
        self.short_percent = short_percent
        self.switch_task = switch_task

    def pre_process(self):
        super(MotherAlgorithm, self).pre_process()

        # set short and long task drones
        bound_idx = int(math.ceil(self.short_percent * self.data_dict[u'drones']))
        for i in xrange(len(self.drone_list)):
            self.drone_list[i][u'assignment'] = u'short' if i < bound_idx else u'long'

    def generate(self, ):
        data_dict = self.data_dict

        # stores the commands
        command_lines = []

        warehouse = self.warehouse_list[0]

        # distance-first
        order_list = sort_by_distance(warehouse[u'location'], self.order_list)

        front_order_idx = 0
        back_order_idx = data_dict[u'orders'] - 1
        current_drone_id = 0
        while front_order_idx <= back_order_idx and (order_list[front_order_idx][u'items'] > 0 or order_list[back_order_idx][u'items'] > 0):
            this_drone = self.drone_list[current_drone_id]

            if this_drone[u'assignment'] == u'short':
                this_order = order_list[front_order_idx]
            else:
                this_order = order_list[back_order_idx]

            drone_load_commands = []
            drone_deliver_commands = []
            while this_order[u'items'] > 0:
                to_carry_dict, drone_weight = get_can_carry_dict(this_order, data_dict)

                # calculate the turns needed
                distance1 = calculate_distance(this_drone[u'location'], warehouse[u'location'])
                distance2 = calculate_distance(warehouse[u'location'], this_order[u'location'])
                travel_turns = distance1 + distance2
                next_turn = this_drone[u'next_turn'] + travel_turns

                # fetch the item from this warehouse
                this_drone[u'location'] = this_order[u'location'][:]
                this_drone[u'next_turn'] = next_turn
                this_drone[u'weight'] = drone_weight

                for it, fetch_count in to_carry_dict.iteritems():
                    warehouse[u'item_count_list'][it] -= fetch_count
                    this_order[u'item_types'][it] -= fetch_count
                    this_order[u'items'] -= fetch_count
                    if this_order[u'item_types'][it] == 0:
                        del this_order[u'item_types'][it]

                    # set commands and next turn
                    # load
                    drone_load_commands.append(get_load_cmd(this_drone[u'id'],
                                                            warehouse[u'id'],
                                                            it, fetch_count))

                    # deliver
                    drone_deliver_commands.append(get_deliver_cmd(this_drone[u'id'],
                                                                  this_order[u'id'],
                                                                  it, fetch_count))

                    this_drone[u'next_turn'] += 2

                break

            # remove this order if it is empty
            if this_order[u'items'] == 0:
                if this_drone[u'assignment'] == u'short':
                    front_order_idx += 1
                else:
                    back_order_idx -= 1

            # give extra payload to this drone if possible
            give_extra_load(this_drone, warehouse, order_list, data_dict, drone_load_commands, drone_deliver_commands)

            # set commands
            command_lines += drone_load_commands
            command_lines += drone_deliver_commands

            # switch this drone's next task
            if self.switch_task:
                this_drone[u'assignment'] = u'short' if this_drone[u'assignment'] == u'long' else u'long'

            # schedule the next drone if this one has a task
            current_drone_id = self.get_next_drone_idx(current_drone_id)

        return command_lines


def give_extra_load(drone, warehouse, order_list, data_dict, drone_load_commands, drone_deliver_commands,
                    max_hops=2):
    if drone[u'weight'] >= data_dict[u'max_payload']:
        return
    hops = 0

    tmp_order_list = sort_by_distance(drone[u'location'], [o for o in order_list if o[u'items'] > 0])
    for order in tmp_order_list:
        can_carry_dict, drone_weight = get_can_carry_dict(order, data_dict, drone_weight=drone[u'weight'])
        if len(can_carry_dict) > 0:
            # load extra payload
            distance1 = calculate_distance(drone[u'location'], order[u'location'])
            next_turn = drone[u'next_turn'] + distance1

            drone[u'location'] = order[u'location'][:]
            drone[u'next_turn'] = next_turn
            drone[u'weight'] += drone_weight

            for it, fetch_count in can_carry_dict.iteritems():
                warehouse[u'item_count_list'][it] -= fetch_count
                order[u'item_types'][it] -= fetch_count
                order[u'items'] -= fetch_count
                if order[u'item_types'][it] == 0:
                    del order[u'item_types'][it]

                # add load command
                load_command_appended = False
                for cmd_idx in xrange(len(drone_load_commands)):
                    cmd = drone_load_commands[cmd_idx]
                    item_id = int(cmd.split(u' ')[-2])
                    if item_id == it:
                        new_count = int(cmd.split(u' ')[-1]) + fetch_count
                        cmd = u' '.join(cmd.split(u' ')[:-1] + [u'%d' % new_count])
                        drone_load_commands[cmd_idx] = cmd
                        load_command_appended = True
                        break
                if not load_command_appended:
                    drone_load_commands.append(get_load_cmd(drone[u'id'], warehouse[u'id'],
                                                            it, fetch_count))
                    drone[u'next_turn'] += 1

                # add delivery command
                drone_deliver_commands.append(get_deliver_cmd(drone[u'id'], order[u'id'],
                                                              it, fetch_count))
                drone[u'next_turn'] += 1

        hops += 1
        if hops > max_hops:
            break


def get_can_carry_dict(order, data_dict, drone_weight=0):
    to_carry_dict = {}
    for it, itc in order[u'item_types'].iteritems():
        itw = data_dict[u'product_type_weights'][it]
        can_carry_count = (data_dict[u'max_payload'] - drone_weight) / itw
        if can_carry_count > itc:
            can_carry_count = itc
        if can_carry_count > 0:
            drone_weight += itw * can_carry_count
            to_carry_dict[it] = can_carry_count
    return to_carry_dict, drone_weight


def get_order_list_close_to_warehouses(order_list, warehouse_list, threshold):
    order_id_set = set()
    for wh in warehouse_list:
        for order in order_list:
            if calculate_distance(order[u'location'], wh[u'location']) <= threshold:
                order_id_set.add(order[u'id'])
    return order_id_set
