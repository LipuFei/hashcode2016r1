from .common import calculate_distance


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
    :param drone_weight: The initial payload this drone is carrying.
    :param data_dict: The data_dict.
    :return: A dict with delivery details if there is something to deliver, otherwise None.
    """
    can_carry_weight = drone[u'max_payload'] - drone_weight
    if can_carry_weight == 0:
        return

    # fetch as many items as possible for this order in this warehouse
    items_to_deliver = {}
    for it, itc in order[u'item_types'].iteritems():
        itw = data_dict[u'product_type_weights'][it]
        wh_itc = warehouse[u'item_count_list'][it]

        carry_count = can_carry_weight / itw
        carry_count = itc if carry_count > itc else carry_count
        carry_count = wh_itc if carry_count > wh_itc else carry_count

        if carry_count > 0:
            items_to_deliver[it] = carry_count
    if not items_to_deliver:
        return

    # calculate the turns needed
    distance1 = calculate_distance(drone[u'location'], warehouse[u'location'])
    distance2 = calculate_distance(warehouse[u'location'], order[u'location'])
    load_turns = len(items_to_deliver)
    delivery_turns = len(items_to_deliver)
    # turns = (to_warehouse + load_turns + to_order + deliver_turns)
    turns = distance1 + load_turns + distance2 + delivery_turns

    delivery_dict = {u'did': drone[u'id'],
                     u'oid': order[u'id'],
                     u'wid': warehouse[u'id'],
                     u'items_to_deliver': items_to_deliver,
                     u'turns': turns}
    return delivery_dict
