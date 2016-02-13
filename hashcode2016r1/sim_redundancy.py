import math


def sim(data_dict, wo_distance):
    # pre-process
    warehouse_list = data_dict[u'warehouse_list']
    for wid in xrange(len(warehouse_list)):
        warehouse_list[wid][u'id'] = wid

    drones = [{u'id': i,
               u'location': warehouse_list[0][u'location'][:],
               u'payloads': {},
               u'next_turn': 0} for i in xrange(data_dict[u'drones'])]

    order_list = data_dict[u'order_list']
    for oid in xrange(len(order_list)):
        order_list[oid][u'id'] = oid
    for order in order_list:
        total_weight = 0
        for item in order[u'item_types']:
            total_weight += data_dict[u'product_type_weights'][item]
        order[u'total_weight'] = total_weight

        item_types = {}
        # convert item_types into a dict
        for item in order[u'item_types']:
            if item not in item_types:
                item_types[item] = 0
            item_types[item] += 1
        order[u'item_types'] = item_types

    # stores the commands
    command_lines = []

    # filter out the far-away orders
    order_id_set = get_order_list_close_to_warehouses(order_list, warehouse_list, wo_distance)
    order_list = [o for o in order_list if o[u'id'] in order_id_set]

    # total-weight-first
    order_list = sorted(order_list, key=lambda o: o[u'total_weight'])

    current_drone_id = 0
    while True:
        this_drone = drones[current_drone_id]
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
            current_drone_id = get_next_drone(current_drone_id, data_dict)

    return command_lines


def get_order_list_close_to_warehouses(order_list, warehouse_list, threshold):
    order_id_set = set()
    for wh in warehouse_list:
        for order in order_list:
            if calculate_distance(order[u'location'], wh[u'location']) <= threshold:
                order_id_set.add(order[u'id'])
    return order_id_set


def sort_by_distance(location, data_list):
    return sorted(data_list, key=lambda d: calculate_distance(location, d[u'location']))


def get_next_drone(current_drone_id, data_dict):
    return (current_drone_id + 1) % data_dict[u'drones']


def get_load_cmd(did, wid, iid, count):
    return u"%d L %d %d %d" % (did, wid, iid, count)


def get_unload_cmd(did, wid, iid, count):
    return u"%d U %d %d %d" % (did, wid, iid, count)


def get_deliver_cmd(did, oid, iid, count):
    return u"%d D %d %d %d" % (did, oid, iid, count)


def calculate_distance(loc1, loc2):
    return math.ceil(math.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2))
