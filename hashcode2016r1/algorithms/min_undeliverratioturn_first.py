from .algorithm import Algorithm
from .common import calculate_distance, get_load_cmd, get_deliver_cmd
from .tools import get_delivery_with_min_undelivered_ratio_turn, get_intermediate_delivery_with_min_turns


class MinUndeliverRatioTurnsAlgorithm(Algorithm):
    """
    Deliver the orders with the minimal weight-turn-metric first.
    weight-turn = total weight of the deliver * total turns
    """

    def __init__(self, data_dict, w1=1.0, w2=1.0, w3=1.0, angle_threshold=45.0):
        super(MinUndeliverRatioTurnsAlgorithm, self).__init__(data_dict)
        self.angle_threshold = angle_threshold
        self.w1 = w1
        self.w2 = w2
        self.w3 = w3

    def pre_process(self):
        super(MinUndeliverRatioTurnsAlgorithm, self).pre_process()

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
            this_delivery = get_delivery_with_min_undelivered_ratio_turn(this_drone, order_list, warehouse_list, data_dict,
                                                                         w1=self.w1, w2=self.w2, w3=self.w3)
            if this_delivery is None:
                current_drone_id = self.get_next_drone_idx(current_drone_id)
                continue

            this_order = self.get_order(this_delivery[u'oid'])
            this_warehouse = self.get_warehouse(this_delivery[u'wid'])

            # fetch items
            load_cmd_list = []
            deliver_cmd_list = []
            this_drone[u'payloads'] = {}
            for it, itc in this_delivery[u'items_to_deliver'].iteritems():
                this_warehouse[u'item_count_list'][it] -= itc
                this_order[u'item_types'][it] -= itc
                this_order[u'items'] -= itc
                if this_order[u'item_types'][it] == 0:
                    del this_order[u'item_types'][it]

                this_drone[u'payloads'][it] = itc

                # add commands
                load_cmd_list.append(get_load_cmd(current_drone_id, this_warehouse[u'id'], it, itc))
                deliver_cmd_list.append(get_deliver_cmd(current_drone_id, this_order[u'id'], it, itc))

            # try to get extra plaload
            inter_delivery = get_intermediate_delivery_with_min_turns(this_drone, this_order, this_warehouse,
                                                                      order_list, data_dict,
                                                                      this_delivery[u'total_weight'],
                                                                      self.angle_threshold,
                                                                      w1=self.w1, w2=self.w2, w3=self.w3)
            if inter_delivery is not None:
                # append this delivery to the commands
                t_o = self.get_order(inter_delivery[u'oid'])
                t_w = self.get_warehouse(inter_delivery[u'wid'])
                for it, itc in inter_delivery[u'items_to_deliver'].iteritems():
                    t_w[u'item_count_list'][it] -= itc
                    t_o[u'item_types'][it] -= itc
                    t_o[u'items'] -= itc
                    if t_o[u'item_types'][it] == 0:
                        del t_o[u'item_types'][it]

                    if it in this_drone[u'payloads']:
                        # modify load command
                        this_drone[u'payloads'][it] += itc
                        for cmd_idx in xrange(len(load_cmd_list)):
                            cmd = load_cmd_list[cmd_idx]
                            if int(cmd.split(u' ')[-2]) == it:
                                load_cmd_list[cmd_idx] = get_load_cmd(current_drone_id, inter_delivery[u'wid'],
                                                                      it, this_drone[u'payloads'][it])
                                break
                    else:
                        # append load command
                        this_drone[u'payloads'][it] = itc
                        load_cmd_list.append(get_load_cmd(current_drone_id, t_w[u'id'], it, itc))

                    # append delivery command
                    deliver_cmd_list = [get_deliver_cmd(current_drone_id, t_o[u'id'], it, itc)] + deliver_cmd_list

                # new_turns = to_warehouse + load + to_intermediate + deliver + to_final + deliver
                to_warehouse = calculate_distance(this_drone[u'location'], t_w[u'location'])
                to_intermediate = calculate_distance(t_w[u'location'], t_o[u'location'])
                to_final = calculate_distance(t_o[u'location'], this_delivery[u'final_location'])
                loads = len(load_cmd_list)
                delivers = len(deliver_cmd_list)
                turns = to_warehouse + to_intermediate + to_final + loads + delivers

            else:
                turns = this_delivery[u'turns']
            final_location = this_delivery[u'final_location'][:]

            this_drone[u'location'] = final_location
            this_drone[u'next_turn'] += turns

            command_lines += load_cmd_list
            command_lines += deliver_cmd_list

            # schedule the next drone
            min_drone = None
            for drone in drone_list:
                if min_drone is None:
                    min_drone = drone
                elif min_drone[u'next_turn'] > drone[u'next_turn']:
                    min_drone = drone
            current_drone_id = min_drone[u'id']
            #current_drone_id = self.get_next_drone_idx(current_drone_id)

        return command_lines
