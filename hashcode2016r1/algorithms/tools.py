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
    item_count = len(warehouse_list[u'product_types'])
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
