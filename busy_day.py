#!/usr/bin/env python
import codecs
import os
import sys

from hashcode2016r1 import parser


def parse_file(dataset_name):
    in_file = os.path.join(dataset_name, u'%s.in' % dataset_name)
    data_dict = parser.parse_input_file(in_file)

    return data_dict


if __name__ == '__main__':
    #ds_name = u'busy_day'
    ds_name_list = [u'busy_day', u'mother_of_all_warehouses', u'redundancy']
    ds_name = ds_name_list[int(sys.argv[1])]

    w1 = 1.0
    w2 = 1.0
    w3 = 1.0
    angle_threshold = 25.0

    data = parse_file(ds_name)

    for wh in sorted(data[u'warehouse_list'], key=lambda w: w[u'location'][1]):
        print u"%d  %s" % (wh[u'id'], wh[u'location'])

    from hashcode2016r1.algorithms import min_undeliverratioturn_first
    alg = min_undeliverratioturn_first.MinUndeliverRatioTurnsAlgorithm(data, angle_threshold=angle_threshold,
                                                                       w1=w1, w2=w2, w3=w3)
    alg.pre_process()
    cmd_lines = alg.generate()

    cmd_lines = [u'%d' % len(cmd_lines)] + cmd_lines
    cmd_lines = [l + os.linesep for l in cmd_lines]
    file_name = u'%s_w1_%s_w2_%s_w3_%s_a_%s.txt' % (ds_name, w1, w2, w3, angle_threshold)
    with codecs.open(file_name, 'wb', encoding='utf-8') as f:
        f.writelines(cmd_lines)
