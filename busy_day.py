#!/usr/bin/env python
import codecs
import os

from hashcode2016r1 import parser


def parse_file(dataset_name):
    in_file = os.path.join(ds_name, u'%s.in' % dataset_name)
    data_dict = parser.parse_input_file(in_file)

    return data_dict


if __name__ == '__main__':
    ds_name = u'busy_day'
    data = parse_file(ds_name)

    for wh in sorted(data[u'warehouse_list'], key=lambda w: w[u'location'][1]):
        print u"%d  %s" % (wh[u'id'], wh[u'location'])

    from hashcode2016r1.algorithms import min_drone_turns, min_undeliverratioturn_first

    #alg = min_drone_turns.MinDroneTurnsAlgorithm(data, angle_threshold=60.0)
    alg = min_undeliverratioturn_first.MinUndeliverRatioTurnsAlgorithm(data, angle_threshold=45.0)
    alg.pre_process()
    cmd_lines = alg.generate()

    cmd_lines = [u'%d' % len(cmd_lines)] + cmd_lines
    cmd_lines = [l + os.linesep for l in cmd_lines]
    with codecs.open(u'%s.txt' % ds_name, 'wb', encoding='utf-8') as f:
        f.writelines(cmd_lines)
