from .algorithm import Algorithm
from .common import calculate_distance, sort_by_distance, get_load_cmd, get_deliver_cmd
from .tools import get_delivery_with_min_turns


class BusyAlgorithm(Algorithm):

    def __init__(self, data_dict):
        super(BusyAlgorithm, self).__init__(data_dict)

    def pre_process(self):
        super(BusyAlgorithm, self).pre_process()

    def generate(self):
        # stores the commands
        command_lines = []

        # for convenience
        warehouse_list = self.warehouse_list
        data_dict = self.data_dict
        order_list = self.order_list
        drone_list = self.drone_list

        # total-weight-first
        order_list = sorted(order_list, key=lambda o: o[u'total_weight'])

        current_drone_id = 0
        last_order_count = 0
        while True:
            # clean up order list
            order_list = [o for o in order_list if o[u'items'] > 0]
            if len(order_list) == 0:
                break
            if last_order_count != len(order_list):
                last_order_count = len(order_list)
                print u"remaining orders: %d" % last_order_count

            this_drone = drone_list[current_drone_id]

            # find the delivery that takes the least turns
            this_delivery = get_delivery_with_min_turns(this_drone, order_list, warehouse_list, data_dict)
            if this_delivery is None:
                current_drone_id = self.get_next_drone_idx(current_drone_id)
                continue

            this_order = self.get_order(this_delivery[u'oid'])
            this_warehouse = self.get_warehouse(this_delivery[u'wid'])

            # fetch items
            load_cmd_list = []
            deliver_cmd_list = []
            for it, itc in this_delivery[u'items_to_deliver'].iteritems():
                this_warehouse[u'item_count_list'][it] -= itc
                this_order[u'item_types'][it] -= itc
                this_order[u'items'] -= itc
                if this_order[u'item_types'][it] == 0:
                    del this_order[u'item_types'][it]

                # add commands
                load_cmd_list.append(get_load_cmd(current_drone_id, this_warehouse[u'id'], it, itc))
                deliver_cmd_list.append(get_deliver_cmd(current_drone_id, this_order[u'id'], it, itc))

            this_drone[u'location'] = this_delivery[u'final_location'][:]
            this_drone[u'next_turn'] += this_delivery[u'turns']

            command_lines += load_cmd_list
            command_lines += deliver_cmd_list

            # schedule the next drone
            current_drone_id = self.get_next_drone_idx(current_drone_id)

        return command_lines


def get_order_list_close_to_warehouses(order_list, warehouse_list, threshold):
    order_id_set = set()
    for wh in warehouse_list:
        for order in order_list:
            if calculate_distance(order[u'location'], wh[u'location']) <= threshold:
                order_id_set.add(order[u'id'])
    return order_id_set
