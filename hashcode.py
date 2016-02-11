#!/usr/bin/env python
import sys
import os


def parse_file(file_name):
    with open(file_name, 'rb') as f:
        rows, columns, drones, turns, max_payload = [int(v) for v in f.readline().strip().split(' ')]
        product_types = int(f.readline().strip())
        product_type_weights = [int(v) for v in f.readline().strip().split(' ')]

        warehouses = int(f.readline().strip())
        warehouse_list = []
        for i in range(warehouses):
            location = [int(v) for v in f.readline().strip().split(' ')]
            item_count_list = [int(v) for v in f.readline().strip().split(' ')]
            warehouse_list.append({'location': location,
                                   'item_count_list': item_count_list})

        orders = int(f.readline().strip())
        order_list = []
        for i in range(orders):
            location = [int(v) for v in f.readline().strip().split(' ')]
            items = int(f.readline().strip())
            item_types = [int(v) for v in f.readline().strip().split(' ')]
            order_list.append({'location': location,
                               'items': items,
                               'item_types': item_types})

        data_dict = {'rows': rows,
                     'columns': columns,
                     'drones': drones,
                     'turns': turns,
                     'max_payload': max_payload,
                     'product_types': product_types,
                     'product_type_weights': product_type_weights,
                     'warehouses': warehouses,
                     'warehouse_list': warehouse_list,
                     'orders': orders,
                     'order_list': order_list,
                     }
        return data_dict


def print_summary(data_dict):
    print("dimension: %s %s" % (data_dict['rows'], data_dict['columns']))
    print("drones: %s" % data_dict['drones'])
    print("max_payload: %s" % data_dict['max_payload'])
    print("product_types: %s" % data_dict['product_types'])
    print("warehouses: %s" % data_dict['warehouses'])
    print("orders: %s" % data_dict['orders'])


if __name__ == '__main__':
    data = parse_file('busy_day.in')
    print_summary(data)
