import math


def sim(data_dict, short_percent=0.5):
    # pre-process
    warehouse_list = data_dict[u'warehouse_list']
    for wid in xrange(len(warehouse_list)):
        warehouse_list[wid][u'id'] = wid

    drones = [{u'id': i,
               u'location': warehouse_list[0][u'location'][:],
               u'payloads': {},
               u'next_turn': 0}
              for i in xrange(data_dict[u'drones'])]

    # set short and long task drones
    bound_idx = int(math.ceil(short_percent * data_dict[u'drones']))
    for i in xrange(len(drones)):
        drones[i][u'assignment'] = u'short' if i < bound_idx else u'long'

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

    warehouse = warehouse_list[0]

    # distance-first
    order_list = sorted(order_list, key=lambda o: calculate_distance(warehouse[u'location'], o[u'location']))

    front_order_idx = 0
    back_order_idx = data_dict[u'orders'] - 1
    current_drone_id = 0
    while front_order_idx < back_order_idx or order_list[front_order_idx][u'items'] > 0:
        this_drone = drones[current_drone_id]

        if this_drone[u'assignment'] == u'short':
            this_order = order_list[front_order_idx]
        else:
            this_order = order_list[back_order_idx]

        drone_weight = 0
        while this_order[u'items'] > 0:
            to_carry_dict = {}
            for it, itc in this_order[u'item_types'].iteritems():
                itw = data_dict[u'product_type_weights'][it]
                can_carry_count = (data_dict[u'max_payload'] - drone_weight) / itw
                if can_carry_count > itc:
                    can_carry_count = itc
                if can_carry_count > 0:
                    drone_weight += itw * can_carry_count
                    to_carry_dict[it] = can_carry_count

            # calculate the turns needed
            distance1 = calculate_distance(this_drone[u'location'], warehouse[u'location'])
            distance2 = calculate_distance(warehouse[u'location'], this_order[u'location'])
            # turns = current_turn + (to_warehouse + 1 + to_deliver + 1)
            turns = distance1 + 1 + distance2 + 1
            next_turn = this_drone[u'next_turn'] + turns

            # fetch the item from this warehouse
            this_drone[u'location'] = this_order[u'location'][:]
            this_drone[u'next_turn'] = next_turn

            load_cmd_list = []
            deliver_cmd_list = []

            for it, fetch_count in to_carry_dict.iteritems():
                warehouse[u'item_count_list'][it] -= fetch_count
                this_order[u'item_types'][it] -= fetch_count
                this_order[u'items'] -= fetch_count
                if this_order[u'item_types'][it] == 0:
                    del this_order[u'item_types'][it]

                # set commands and next turn
                # load
                load_cmd_list.append(get_load_cmd(this_drone[u'id'],
                                                  warehouse[u'id'],
                                                  it, fetch_count))

                # deliver
                deliver_cmd_list.append(get_deliver_cmd(this_drone[u'id'],
                                                        this_order[u'id'],
                                                        it, fetch_count))

            command_lines += load_cmd_list
            command_lines += deliver_cmd_list
            break

        # remove this order if it is empty
        if this_order[u'items'] == 0:
            if this_drone[u'assignment'] == u'short':
                front_order_idx += 1
            else:
                back_order_idx -= 1
        # schedule the next drone if this one has a task
        current_drone_id = get_next_drone(current_drone_id, data_dict)

    return command_lines


def get_order_list_close_to_warehouses(order_list, warehouse_list, threshold):
    order_id_set = set()
    for wh in warehouse_list:
        for order in order_list:
            if calculate_distance(order[u'location'], wh[u'location']) <= threshold:
                order_id_set.add(order[u'id'])
    return order_id_set


def sort_by_distance(location, data_list, reverse=False):
    return sorted(data_list, key=lambda d: calculate_distance(location, d[u'location']), reverse=reverse)


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
