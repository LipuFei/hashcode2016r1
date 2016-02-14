from .algorithm import Algorithm
from .common import calculate_distance, sort_by_distance, get_load_cmd, get_deliver_cmd


class RedundancyAlgorithm(Algorithm):

    def __init__(self, data_dict):
        super(RedundancyAlgorithm, self).__init__(data_dict)

    def pre_process(self):
        super(RedundancyAlgorithm, self).pre_process()

    def generate(self):
        # stores the commands
        command_lines = []

        # for convenience
        data_dict = self.data_dict
        drone_list = self.drone_list
        order_list = self.order_list
        warehouse_list = self.warehouse_list

        # total-weight-first
        order_list = sorted(order_list, key=lambda o: o[u'total_weight'])

        current_drone_id = 0
        while True:
            this_drone = drone_list[current_drone_id]
            drone_task_is_set = False

            # find the closest order
            order_list = sort_by_distance(this_drone[u'location'], order_list)
            if len(order_list) == 0:
                break
            this_order = order_list[0]

            drone_weight = 0
            while this_order[u'items'] > 0:
                this_item, this_item_count = this_order[u'item_types'].items()[0]
                this_item_weight = data_dict[u'product_type_weights'][this_item]

                can_carry_count = (data_dict[u'max_payload'] - drone_weight) / this_item_weight
                if can_carry_count == 0:
                    break

                # find the nearest warehouse to this order with this item
                warehouse_list = sort_by_distance(this_drone[u'location'], warehouse_list)
                warehouse_idx = 0
                while True:
                    this_warehouse = warehouse_list[warehouse_idx]
                    item_count_in_this_warehouse = this_warehouse[u'item_count_list'][this_item]
                    if item_count_in_this_warehouse == 0:
                        warehouse_idx += 1
                        continue

                    # calculate the turns needed
                    distance1 = calculate_distance(this_drone[u'location'], this_warehouse[u'location'])
                    distance2 = calculate_distance(this_warehouse[u'location'], this_order[u'location'])
                    # turns = current_turn + (to_warehouse + 1 + to_deliver + 1)
                    turns = distance1 + 1 + distance2 + 1
                    next_turn = this_drone[u'next_turn'] + turns
                    if next_turn > data_dict[u'turns']:
                        # stop if the maximum turns has reached
                        return command_lines

                    # fetch the item from this warehouse
                    fetch_count = can_carry_count
                    if fetch_count > this_item_count:
                        fetch_count = this_item_count
                    if fetch_count > item_count_in_this_warehouse:
                        fetch_count = item_count_in_this_warehouse

                    this_warehouse[u'item_count_list'][this_item] -= fetch_count

                    this_drone[u'location'] = this_order[u'location'][:]
                    this_drone[u'payloads'] = {u'this_item': fetch_count}
                    this_drone[u'next_turn'] = next_turn

                    this_order[u'item_types'][this_item] -= fetch_count
                    this_order[u'items'] -= fetch_count
                    if this_order[u'item_types'][this_item] == 0:
                        del this_order[u'item_types'][this_item]

                    # set commands and next turn
                    # load
                    command_lines.append(get_load_cmd(this_drone[u'id'],
                                                      this_warehouse[u'id'],
                                                      this_item, fetch_count))
                    # deliver
                    command_lines.append(get_deliver_cmd(this_drone[u'id'],
                                                         this_order[u'id'],
                                                         this_item, fetch_count))
                    drone_task_is_set = True
                    break

                if drone_task_is_set:
                    break

            # remove this order if it is empty
            if this_order[u'items'] == 0:
                order_list = order_list[1:]
            # schedule the next drone if this one has a task
            if drone_task_is_set:
                current_drone_id = self.get_next_drone_idx(current_drone_id)

        return command_lines


def get_order_list_close_to_warehouses(order_list, warehouse_list, threshold):
    order_id_set = set()
    for wh in warehouse_list:
        for order in order_list:
            if calculate_distance(order[u'location'], wh[u'location']) <= threshold:
                order_id_set.add(order[u'id'])
    return order_id_set
