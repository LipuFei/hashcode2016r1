import math


def get_load_cmd(did, wid, iid, count):
    return u"%d L %d %d %d" % (did, wid, iid, count)


def get_unload_cmd(did, wid, iid, count):
    return u"%d U %d %d %d" % (did, wid, iid, count)


def get_deliver_cmd(did, oid, iid, count):
    return u"%d D %d %d %d" % (did, oid, iid, count)


def calculate_distance(loc1, loc2):
    return math.ceil(math.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2))


def calculate_vector(loc1, loc2):
    return [loc2[0] - loc1[0], loc2[1] - loc1[1]]


def calculate_dot_product(vec1, vec2):
    return vec1[0] * vec2[0] + vec1[1] * vec2[1]


def sort_by_distance(location, data_list, reverse=False):
    return sorted(data_list, key=lambda d: calculate_distance(location, d[u'location']), reverse=reverse)


def calculate_angle(location1, location2, location3, angle_threshold):
    vector1 = calculate_vector(location1, location2)
    vector2 = calculate_vector(location1, location3)
    edge1 = calculate_distance(location1, location2)
    edge2 = calculate_distance(location1, location3)

    if edge2 - edge1 > 0:
        return

    dp = calculate_dot_product(vector1, vector2)
    angle = math.acos(dp / edge1 / edge2) / math.pi * 180.0
    if angle > angle_threshold:
        return

    edge3 = calculate_distance(location2, location3)

    # return the location's distance towards the line
    #return math.sin(angle/180.0*math.pi) * edge2
    return edge2 + edge3


def sort_by_distance_to_line(loc1, loc2, data_list, angle_threshold):
    new_data_list = [d for d in data_list if calculate_angle(loc1, loc2, d[u'location'], angle_threshold) is not None]
    return sorted(new_data_list, key=lambda d: calculate_angle(loc1, loc2, d[u'location'], angle_threshold))


def calculate_location_score(location, warehouse_list, max_order_to_warehouse_distance):
    # the normalized average of the distance between this location to all warehouses.
    distance_sum = 0.0
    for warehouse in warehouse_list:
        distance = calculate_distance(location, warehouse[u'location'])
        normalized_distance = float(distance) / max_order_to_warehouse_distance
        distance_sum += normalized_distance
    distance_sum /= len(warehouse_list)

    return distance_sum
