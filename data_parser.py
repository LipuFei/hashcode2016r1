#!/usr/bin/env python
import codecs
import os
import sys

from hashcode2016r1 import data_processor
from hashcode2016r1 import parser


def parse_file(dataset_name):
    in_file = os.path.join(dataset_name, u'%s.in' % dataset_name)
    item_weight_file = os.path.join(dataset_name, u'item_weight.csv')
    warehouse_file = os.path.join(dataset_name, u'warehouse.csv')
    order_file = os.path.join(dataset_name, u'order.csv')
    warehouse_order_radius_file = os.path.join(dataset_name, u'warehouse_order_radius.csv')
    summary_file = os.path.join(dataset_name, u'summary.txt')

    data_dict = parser.parse_input_file(in_file)
    data_processor.create_item_weight_csv(data_dict, item_weight_file)
    data_processor.create_warehouse_csv(data_dict, warehouse_file)
    data_processor.create_order_csv(data_dict, order_file)
    data_processor.create_warehouse_order_radius_csv(data_dict, warehouse_order_radius_file,
                                                     [i for i in xrange(5, 300, 5)])

    data_processor.create_data_summary(data_dict, summary_file)

    file_dict = {u'in': in_file,
                 u'item_weight': item_weight_file,
                 u'warehouse': warehouse_file,
                 u'order': order_file,
                 u'summary': summary_file}

    return data_dict, file_dict


if __name__ == '__main__':
    dataset_dict = {u'busy': u'busy_day',
                    u'mother': u'mother_of_all_warehouses',
                    u'redundancy': u'redundancy'}
    dataset_names = u", ".join([u"'%s'" % k for k in dataset_dict])

    if len(sys.argv) < 2:
        print >> sys.stderr, u"missing dataset name, must be one of %s" % dataset_names
        exit(1)
    ds_name = sys.argv[1]
    if ds_name not in dataset_dict:
        msg = u"unexpected dataset name '%s', must be one of %s" % (ds_name, dataset_names)
        print >> sys.stderr, msg
        exit(1)

    parse_file(dataset_dict[ds_name])
