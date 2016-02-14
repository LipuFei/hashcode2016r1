import math


def get_load_cmd(did, wid, iid, count):
    return u"%d L %d %d %d" % (did, wid, iid, count)


def get_unload_cmd(did, wid, iid, count):
    return u"%d U %d %d %d" % (did, wid, iid, count)


def get_deliver_cmd(did, oid, iid, count):
    return u"%d D %d %d %d" % (did, oid, iid, count)


def calculate_distance(loc1, loc2):
    return math.ceil(math.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2))


def sort_by_distance(location, data_list, reverse=False):
    return sorted(data_list, key=lambda d: calculate_distance(location, d[u'location']), reverse=reverse)
