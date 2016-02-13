import codecs
import csv


def print_data_summary(data_dict):
    print u"map dimension: %s %s" % (data_dict[u'rows'], data_dict[u'columns'])
    print u"drones: %s" % data_dict[u'drones']
    print u"max_payload: %s" % data_dict[u'max_payload']
    print u"product_types: %s" % data_dict[u'product_types']
    print u"warehouses: %s" % data_dict[u'warehouses']
    print u"orders: %s" % data_dict[u'orders']


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
            writer.writerow(wh_dict)
            wid += 1


def create_order_csv(data_dict, csv_file):
    field_names = [u'id', u'pos_x', u'pos_y', u'items']
    field_names += [u'item_count_%d' % i for i in xrange(data_dict[u'product_types'])]
    with codecs.open(csv_file, 'wb', encoding='utf-8') as f:
        writer = csv.DictWriter(f, field_names)
        writer.writeheader()

        oid = 0
        for order in data_dict[u'order_list']:
            order_dict = {u'id': oid,
                          u'pos_x': order[u'location'][0],
                          u'pos_y': order[u'location'][1],
                          u'items': order[u'items'],
                          }
            for i in xrange(data_dict[u'product_types']):
                order_dict[u'item_count_%d' % i] = 0
            for it in order[u'item_types']:
                order_dict[u'item_count_%d' % it] += 1
            writer.writerow(order_dict)
            oid += 1
