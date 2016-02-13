def parse_input_file(file_name):
    with open(file_name, 'rb') as f:
        rows, columns, drones, turns, max_payload = [int(v) for v in f.readline().strip().split(' ')]
        product_types = int(f.readline().strip())
        product_type_weights = [int(v) for v in f.readline().strip().split(' ')]

        warehouses = int(f.readline().strip())
        warehouse_list = []
        for i in range(warehouses):
            location = [int(v) for v in f.readline().strip().split(' ')]
            item_count_list = [int(v) for v in f.readline().strip().split(' ')]
            warehouse_list.append({u'location': location,
                                   u'item_count_list': item_count_list})

        orders = int(f.readline().strip())
        order_list = []
        for i in range(orders):
            location = [int(v) for v in f.readline().strip().split(' ')]
            items = int(f.readline().strip())
            item_types = [int(v) for v in f.readline().strip().split(' ')]
            order_list.append({u'location': location,
                               u'items': items,
                               u'item_types': item_types})

        data_dict = {u'rows': rows,
                     u'columns': columns,
                     u'drones': drones,
                     u'turns': turns,
                     u'max_payload': max_payload,
                     u'product_types': product_types,
                     u'product_type_weights': product_type_weights,
                     u'warehouses': warehouses,
                     u'warehouse_list': warehouse_list,
                     u'orders': orders,
                     u'order_list': order_list,
                     }
        return data_dict
