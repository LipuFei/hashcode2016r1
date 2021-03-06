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

    w1 = 0.2
    w2 = 0.7
    angle_threshold = 0.5

    for angle_threshold in [5.0 * n for n in xrange(1, 11)]:
    #for angle_threshold in [5.0, 15.0, 25.0, 35.0, 40.0, 50.0]:
        data = parse_file(ds_name)

        for wh in sorted(data[u'warehouse_list'], key=lambda w: w[u'location'][1]):
            print u"%d  %s" % (wh[u'id'], wh[u'location'])

        from hashcode2016r1.algorithms import min_undeliverratioturn_first
        alg = min_undeliverratioturn_first.MinUndeliverRatioTurnsAlgorithm(data, angle_threshold=angle_threshold,
                                                                           w1=w1, w2=w2)
        alg.pre_process()
        cmd_lines = alg.generate()

        cmd_lines = [u'%d' % len(cmd_lines)] + cmd_lines
        cmd_lines = [l + os.linesep for l in cmd_lines]
        with codecs.open(u'%s_w1_%s_w2_%s_a_%s.txt' % (ds_name, w1, w2, angle_threshold), 'wb', encoding='utf-8') as f:
            f.writelines(cmd_lines)
