#!/usr/bin/env python
import os
import sys

from hashcode2016r1 import parser
from hashcode2016r1 import data_processor


def parse_file(dataset_name):
    in_file = os.path.join(ds_name, u'%s.in' % dataset_name)
    item_weight_file = os.path.join(ds_name, u'%s_item_weight.csv' % dataset_name)
    warehouse_file = os.path.join(ds_name, u'%s_warehouse.csv' % dataset_name)
    order_file = os.path.join(ds_name, u'%s_order.csv' % dataset_name)

    data_dict = parser.parse_input_file(in_file)
    data_processor.create_item_weight_csv(data_dict, item_weight_file)
    data_processor.create_warehouse_csv(data_dict, warehouse_file)
    data_processor.create_order_csv(data_dict, order_file)

    data_processor.print_data_summary(data_dict)

    return data_dict


if __name__ == '__main__':
    ds_name = sys.argv[1].decode('utf-8')

    parse_file(ds_name)
