import codecs
import csv
import math
import os


def create_data_summary(data_dict, file_name):
    msg_list = [u"map dimension: %s %s" % (data_dict[u'rows'], data_dict[u'columns']),
                u"drones: %s" % data_dict[u'drones'],
                u"max_payload: %s" % data_dict[u'max_payload'],
                u"product_types: %s" % data_dict[u'product_types'],
                u"warehouses: %s" % data_dict[u'warehouses'],
                u"orders: %s" % data_dict[u'orders'],
                u"turns: %s" % data_dict[u'turns']]

    with codecs.open(file_name, 'wb', encoding='utf-8') as f:
        f.writelines([msg + os.linesep for msg in msg_list])
    for msg in msg_list:
        print msg


def create_item_weight_csv(data_dict, csv_file):
    field_names = [u'id', u'weight']
    with codecs.open(csv_file, 'wb', encoding='utf-8') as f:
        writer = csv.DictWriter(f, field_names)
        writer.writeheader()

        iid = 0
        for it in data_dict[u'product_type_weights']:
            it_dict = {u'id': iid,
                       u'weight': it,
                       }
            writer.writerow(it_dict)
            iid += 1


def create_warehouse_csv(data_dict, csv_file):
    field_names = [u'id', u'pos_x', u'pos_y']
    field_names += [u'item_count_%d' % i for i in xrange(data_dict[u'product_types'])]
    field_names += [u'item_weight_%d' % i for i in xrange(data_dict[u'product_types'])]
    with codecs.open(csv_file, 'wb', encoding='utf-8') as f:
        writer = csv.DictWriter(f, field_names)
        writer.writeheader()

        wid = 0
        for wh in data_dict[u'warehouse_list']:
            wh_dict = {u'id': wid,
                       u'pos_x': wh[u'location'][0],
                       u'pos_y': wh[u'location'][1],
                       }
            for i in xrange(data_dict[u'product_types']):
                wh_dict[u'item_count_%d' % i] = wh[u'item_count_list'][i]
                wh_dict[u'item_weight_%d' % i] = wh[u'item_count_list'][i] * data_dict[u'product_type_weights'][i]
            writer.writerow(wh_dict)
            wid += 1


def create_order_csv(data_dict, csv_file):
    field_names = [u'id', u'pos_x', u'pos_y', u'items', u'total_weight']
    field_names += [u'item_count_%d' % i for i in xrange(data_dict[u'product_types'])]
    field_names += [u'item_weight_%d' % i for i in xrange(data_dict[u'product_types'])]
    with codecs.open(csv_file, 'wb', encoding='utf-8') as f:
        writer = csv.DictWriter(f, field_names)
        writer.writeheader()

        oid = 0
        for order in data_dict[u'order_list']:
            total_weight = 0
            order_dict = {u'id': oid,
                          u'pos_x': order[u'location'][0],
                          u'pos_y': order[u'location'][1],
                          u'items': order[u'items'],
                          }
            for i in xrange(data_dict[u'product_types']):
                order_dict[u'item_count_%d' % i] = 0
                order_dict[u'item_weight_%d' % i] = 0
            for it in order[u'item_types']:
                order_dict[u'item_count_%d' % it] += 1
                order_dict[u'item_weight_%d' % it] += data_dict[u'product_type_weights'][it]
                total_weight += data_dict[u'product_type_weights'][it]
            order_dict[u'total_weight'] = total_weight
            writer.writerow(order_dict)
            oid += 1


def create_warehouse_order_radius_csv(data_dict, csv_file, steps):
    field_names = [u'radius', u'order_count']

    with codecs.open(csv_file, 'wb', encoding='utf-8') as f:
        writer = csv.DictWriter(f, field_names)
        writer.writeheader()

        for st in steps:
            wid = 0
            order_ids = []
            for wh in data_dict[u'warehouse_list']:
                oid = 0
                for order in data_dict[u'order_list']:
                    if get_distance(wh[u'location'], order[u'location']) <= st and oid not in order_ids:
                        order_ids.append(oid)
                    oid += 1

            data = {u'radius': st,
                    u'order_count': len(order_ids)}

            writer.writerow(data)
            wid += 1


def get_distance(p1, p2):
    return int(math.ceil(math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)))
