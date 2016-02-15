import math

from .common import calculate_distance, sort_by_distance_to_line


def get_unique_item_list(wid_list, warehouse_list):
    """
    Finds the unique items in the given warehouses (the items that are not stored in other warehouses.
    :param wid_list: The list of warehouse IDs.
    :param warehouse_list: The list of all warehouses.
    :return: A list of unique items.
    """
    if not wid_list:
        return list()

    unique_items = set()
    item_count = len(warehouse_list[0][u'item_count_list'])
    # find the items available in the specified warehouses
    for wid in wid_list:
        for i in xrange(item_count):
            if warehouse_list[wid][u'item_count_list'][i] > 0:
                unique_items.add(i)

    # remove the items available in other warehouses
    new_warehouse_list = [wh for wh in warehouse_list if wh[u'id'] not in wid_list]
    for warehouse in new_warehouse_list:
        for i in xrange(item_count):
            if warehouse[u'item_count_list'][i] > 0 and i in unique_items:
                unique_items.remove(i)

    return list(unique_items)


def get_delivery_details(drone, order, warehouse, data_dict, drone_weight=0):
    """
    Gets the delivery details of the given drone loading items in the given warehouse and then
    delivering to the given order.
    :param drone: The given drone.
    :param order: The given order.
    :param warehouse: The given warehouse.
    :param data_dict: The data_dict.
    :param drone_weight: The initial payload this drone is carrying.
    :return: A dict with delivery details if there is something to deliver, otherwise None.
    """
    can_carry_weight = drone[u'max_payload'] - drone_weight
    if can_carry_weight == 0:
        return

    # fetch as many items as possible for this order in this warehouse
    items_to_deliver = {}
    total_order_weight = 0
    total_carry_weight = 0
    for it, itc in order[u'item_types'].iteritems():
        itw = data_dict[u'product_type_weights'][it]
        wh_itc = warehouse[u'item_count_list'][it]

        total_order_weight += itw * itc

        carry_count = can_carry_weight / itw
        carry_count = itc if carry_count > itc else carry_count
        carry_count = wh_itc if carry_count > wh_itc else carry_count

        if carry_count > 0:
            items_to_deliver[it] = carry_count
            total_carry_weight += carry_count * itw
            can_carry_weight -= carry_count * itw
    if not items_to_deliver:
        return

    # calculate the turns needed
    distance1 = calculate_distance(drone[u'location'], warehouse[u'location'])
    distance2 = calculate_distance(warehouse[u'location'], order[u'location'])
    travel_turns = distance1 + distance2
    load_turns = len(items_to_deliver)
    delivery_turns = len(items_to_deliver)
    # turns = (to_warehouse + load_turns + to_order + deliver_turns)
    turns = travel_turns + load_turns + delivery_turns

    deliver_ratio = float(total_carry_weight) / total_order_weight

    delivery_dict = {u'did': drone[u'id'],
                     u'oid': order[u'id'],
                     u'wid': warehouse[u'id'],
                     u'items_to_deliver': items_to_deliver,
                     u'total_weight': total_carry_weight,
                     u'final_location': order[u'location'][:],
                     u'travel_turns': travel_turns,
                     u'deliver_ratio': deliver_ratio,
                     u'turns': turns}
    return delivery_dict


def get_delivery_with_min_turns(drone, order_list, warehouse_list, data_dict, drone_weight=0):
    """
    Finds the delivery that takes the minimum turns for the given drone.
    :param drone: The given drone.
    :param order_list: The whole order list.
    :param warehouse_list: The whole warehouse list.
    :param data_dict: The data_dict.
    :param drone_weight: The initial payload this drone is carrying.
    :return: The delivery detail that takes the minimum turns for the given drone.
    """
    min_delivery_dict = None
    for order in order_list:
        for warehouse in warehouse_list:
            delivery_dict = get_delivery_details(drone, order, warehouse, data_dict, drone_weight=drone_weight)
            if delivery_dict is None:
                continue
            if min_delivery_dict is None:
                min_delivery_dict = delivery_dict
                continue

            # prefer the delivery with less travel time
            if min_delivery_dict[u'travel_turns'] > delivery_dict[u'travel_turns']:
                min_delivery_dict = delivery_dict
            # the tie-breaker is the total weight (prefer the higher)
            elif min_delivery_dict[u'travel_turns'] == delivery_dict[u'travel_turns']:
                if min_delivery_dict[u'total_weight'] < delivery_dict[u'total_weight']:
                    min_delivery_dict = delivery_dict

    return min_delivery_dict


def get_delivery_with_min_weight(drone, order_list, warehouse_list, data_dict, drone_weight=0):
    """
    Finds the delivery that takes the minimum weight for the given drone.
    :param drone: The given drone.
    :param order_list: The whole order list.
    :param warehouse_list: The whole warehouse list.
    :param data_dict: The data_dict.
    :param drone_weight: The initial payload this drone is carrying.
    :return: The delivery detail that takes the minimum turns for the given drone.
    """
    min_delivery_dict = None
    for order in order_list:
        for warehouse in warehouse_list:
            delivery_dict = get_delivery_details(drone, order, warehouse, data_dict, drone_weight=drone_weight)
            if delivery_dict is None:
                continue
            if min_delivery_dict is None:
                min_delivery_dict = delivery_dict
                continue

            # prefer the delivery with less travel weight (faster fulfillment)
            if min_delivery_dict[u'total_weight'] > delivery_dict[u'total_weight']:
                min_delivery_dict = delivery_dict
            # the tie-breaker is the travel_turns (prefer the lower)
            elif min_delivery_dict[u'total_weight'] == delivery_dict[u'total_weight']:
                if min_delivery_dict[u'travel_turns'] > delivery_dict[u'travel_turns']:
                    min_delivery_dict = delivery_dict

    return min_delivery_dict


def get_delivery_with_min_undelivered_ratio_turn(drone, order_list, warehouse_list, data_dict, drone_weight=0):
    """
    Finds the delivery that takes the minimum undelivered-ratio-turn metric.
    """
    min_delivery_dict = None
    for order in order_list:
        for warehouse in warehouse_list:
            delivery_dict = get_delivery_details(drone, order, warehouse, data_dict, drone_weight=drone_weight)
            if delivery_dict is None:
                continue
            delivery_dict[u'normalized_travel_turns'] = float(delivery_dict[u'travel_turns']) / data_dict[u'max_distance']
            #delivery_dict[u'undelivered-ratio-turn'] = (1 - delivery_dict[u'deliver_ratio']) * delivery_dict[u'normalized_travel_turns']
            delivery_dict[u'undelivered-ratio-turn'] = (1 - delivery_dict[u'deliver_ratio']) + delivery_dict[u'normalized_travel_turns']

            if min_delivery_dict is None:
                min_delivery_dict = delivery_dict
                continue

            if min_delivery_dict[u'undelivered-ratio-turn'] > delivery_dict[u'undelivered-ratio-turn']:
                min_delivery_dict = delivery_dict
            # the tie-breaker is the deliver_ratio (prefer the higher)
            elif min_delivery_dict[u'undelivered-ratio-turn'] == delivery_dict[u'undelivered-ratio-turn']:
                if min_delivery_dict[u'deliver_ratio'] < delivery_dict[u'deliver_ratio']:
                    min_delivery_dict = delivery_dict

    return min_delivery_dict


def get_intermediate_delivery_with_min_turns(drone, order, warehouse, order_list, data_dict, drone_weight, angle_threshold):
    """
    Find the intermediate delivery for a given delivery with the minimum extra turns.
    """
    ol = sort_by_distance_to_line(warehouse[u'location'], order[u'location'], order_list, angle_threshold)
    min_delivery_dict = None
    ratio = 0.4
    oid_bound = int(math.ceil(len(ol) * ratio))
    for oid in xrange(oid_bound):
        o = ol[oid]
        if o[u'id'] == order[u'id']:
            continue
        delivery_dict = get_delivery_details(drone, o, warehouse, data_dict, drone_weight=drone_weight)
        if delivery_dict is None:
            break

        delivery_dict[u'normalized_travel_turns'] = float(delivery_dict[u'travel_turns']) / data_dict[u'max_distance']
        #delivery_dict[u'undelivered-ratio-turn'] = (1 - delivery_dict[u'deliver_ratio']) * delivery_dict[u'travel_turns']
        delivery_dict[u'undelivered-ratio-turn'] = (1 - delivery_dict[u'deliver_ratio']) * delivery_dict[u'normalized_travel_turns']

        if min_delivery_dict is None:
            min_delivery_dict = delivery_dict
            continue
        if min_delivery_dict[u'undelivered-ratio-turn'] > delivery_dict[u'undelivered-ratio-turn']:
            min_delivery_dict = delivery_dict
        # the tie-breaker is the deliver_ratio (prefer the higher)
        elif min_delivery_dict[u'undelivered-ratio-turn'] == delivery_dict[u'undelivered-ratio-turn']:
            if min_delivery_dict[u'deliver_ratio'] < delivery_dict[u'deliver_ratio']:
                min_delivery_dict = delivery_dict

    return min_delivery_dict
