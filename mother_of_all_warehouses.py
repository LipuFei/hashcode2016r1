#!/usr/bin/env python
import codecs
import os

from hashcode2016r1 import parser
from hashcode2016r1 import data_processor


def parse_file(dataset_name):
    in_file = os.path.join(ds_name, u'%s.in' % dataset_name)
    item_weight_file = os.path.join(ds_name, u'%s_item_weight.csv' % dataset_name)
    warehouse_file = os.path.join(ds_name, u'%s_warehouse.csv' % dataset_name)
    order_file = os.path.join(ds_name, u'%s_order.csv' % dataset_name)
    warehouse_order_radius_file = os.path.join(ds_name, u'%s_warehouse_order_radius.csv' % dataset_name)

    data_dict = parser.parse_input_file(in_file)
    #data_processor.create_item_weight_csv(data_dict, item_weight_file)
    #data_processor.create_order_csv(data_dict, order_file)
    #data_processor.create_warehouse_order_radius_csv(data_dict, warehouse_order_radius_file,
    #                                                 [i for i in xrange(5, 300, 5)])

    data_processor.print_data_summary(data_dict)

    file_dict = {u'in': in_file,
                 u'item_weight': item_weight_file,
                 u'warehouse': warehouse_file,
                 u'order': order_file}

    return data_dict, file_dict


if __name__ == '__main__':
    ds_name = u'mother_of_all_warehouses'

    data, _ = parse_file(ds_name)

    from hashcode2016r1 import sim_mother
    cmd_lines = sim_mother.sim(data)

    cmd_lines = [u'%d' % len(cmd_lines)] + cmd_lines
    cmd_lines = [l + os.linesep for l in cmd_lines]
    with codecs.open(u'%s.txt' % ds_name, 'wb', encoding='utf-8') as f:
        f.writelines(cmd_lines)
