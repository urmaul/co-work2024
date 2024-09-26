import numpy as np
import os
from optimisationModel import ModelComputationChall
import matplotlib.pyplot as plt
import random, copy


class HeuristicModel(ModelComputationChall):
    def __init__(self, courier_details, delivery_details, time_matrix, method):
        super().__init__(courier_details, delivery_details, time_matrix)

    def create_heu_model(self, delivery_details, courier_ID, time_limit, max_pickup, already_served_order):
        '''
        Args:
            delivery_details:
            courier_ID:
            time_limit:
            max_pickup:
            already_served_order
        Returns:
            delivery_load: List --> for a particular Courier as
            delivery_time: List --> for a particular Courier as
            random_courier_ID: int --> for a particular Courier as
            random_order_list: List --> for a particular Courier as
            delivery_details: List --> Remaining order list
        '''
        delivery_details_copy = copy.deepcopy(delivery_details)
        delivery_time = []
        delivery_load = []
        rand_even_node = random.randrange(4, max_pickup*2+1, 2)
        while True:
            idx_to_be_dropped = None
            pick_up_no = 0
            random_courier_ID = random.choice(courier_ID)
            courier_location = [self.courier_details[i].location for i in range(len(self.courier_details)) if self.courier_details[i].courier_id == random_courier_ID]
            random_node_list = np.zeros(rand_even_node, dtype=int)
            random_order_list = np.zeros(rand_even_node, dtype=int)
            dropped_idx_order = np.zeros(rand_even_node, dtype=int)
            random_order = random.choice(np.unique([delivery_details[idx].delivery_id for idx in range(len(delivery_details))]))
            for idx_o in range(len(delivery_details)):
                if delivery_details[idx_o].delivery_id == random_order:     # and delivery_details[idx_o].time_window_start <= self.time_matrix[(courier_location[0], delivery_details[idx_o].pickup_loc)]:
                    random_node_list[0] = delivery_details[idx_o].pickup_loc
                    random_node_list[-1] = delivery_details[idx_o].dropoff_loc
                    random_order_list[0] = random_order
                    random_order_list[-1] = random_order
                    idx_to_be_dropped = idx_o
            # update index list, pick_up_no, delivery details
            remaining_idx = np.arange(1, len(random_node_list)-1)
            pick_up_no += 1
            if idx_to_be_dropped is not None:
                delivery_details.pop(idx_to_be_dropped)
                dropped_idx_order[0] = idx_to_be_dropped
                dropped_idx_order[-1] = idx_to_be_dropped
            else:
                raise ValueError
            #
            center_node = random_node_list[0]       # nearest node to be searched off
            # check nearest pickup point of center_node
            remaining_idx_bool = True
            if remaining_idx.size == 0:
                remaining_idx_bool = False
            #
            while remaining_idx_bool:  # pick_up_no < max_pickup:  #  or remaining_idx_bool:
                nearest_neighbour_dict = {}
                for val in self.time_matrix:
                     if val[0] == center_node and self.time_matrix[val] != 0 and val[1] in [delivery_details[i].pickup_loc for i in range(len(delivery_details))]:
                         nearest_neighbour_dict[val] = self.time_matrix[val]
                # find the neighbouring node
                tmp_pickup_node = []
                if nearest_neighbour_dict:
                    neighbour_node = min(nearest_neighbour_dict, key=nearest_neighbour_dict.get)
                else:       # if not found
                    tmp_pick_up = [delivery_details[idx].pickup_loc for idx in range(len(delivery_details))]
                    neighbour_node = random.choice(np.unique(tmp_pick_up))
                #
                if isinstance(tmp_pickup_node, list):
                    tmp_pickup_node = neighbour_node[1]
                else:
                    tmp_pickup_node = neighbour_node

                # check which order belongs to this node
                if tmp_pickup_node is not None:
                    tmp_order = [delivery_details[i].delivery_id for i in range(len(delivery_details)) if tmp_pickup_node == delivery_details[i].pickup_loc]
                    #
                    if len(tmp_order)>1:
                        tmp_order = random.choice(tmp_order)
                    else:
                        if isinstance(tmp_order, list):
                            tmp_order = tmp_order[0]
                    # find the index of the tmp_order in the delivery_details list
                    idx_tmp_order = [i for i in range(len(delivery_details)) if tmp_order == delivery_details[i].delivery_id]
                    #
                    delivery_node = delivery_details[idx_tmp_order[0]].dropoff_loc

                    # Suffle the remaining index ensure the drop off comes after pick up
                    used_idx_2 = 10
                    used_idx_1 = 1000
                    while used_idx_1 > used_idx_2:
                        random.shuffle(remaining_idx)
                        used_idx_1 = remaining_idx[0]
                        used_idx_2 = remaining_idx[-1]

                    random_node_list[used_idx_1] = tmp_pickup_node
                    random_node_list[used_idx_2] = delivery_node
                    random_order_list[used_idx_1] = tmp_order
                    random_order_list[used_idx_2] = tmp_order

                    remaining_idx = np.delete(remaining_idx, np.where(remaining_idx == used_idx_1)[0])
                    remaining_idx = np.delete(remaining_idx, np.where(remaining_idx == used_idx_2)[0])
                    #
                    # update the delivery_details list
                    delivery_details.pop(idx_tmp_order[0])
                    dropped_idx_order[used_idx_1] = idx_tmp_order[0]
                    dropped_idx_order[used_idx_2] = idx_tmp_order[0]
                    # update center node
                    center_node = tmp_pickup_node
                    #
                    if remaining_idx.size == 0:
                        remaining_idx_bool = False
                    #
                else:
                    raise ValueError
                #
                pick_up_no += 1
            # Update the node list i.e. add the courier location at the beginning of the list
            random_node_list = np.insert(random_node_list, 0, courier_location)
            # calculate the total time and load and
            for idx, order in enumerate(random_order_list):
                # first from depot to first pick up point
                pickup_travel_time = self.time_matrix[(random_node_list[idx], random_node_list[idx+1])]
                # print(f"Dropped index order {len(dropped_idx_order)} \n")
                if self.delivery_details[dropped_idx_order[idx]].time_window_start > pickup_travel_time:
                    delivery_time.append(self.delivery_details[dropped_idx_order[idx]].time_window_start)
                else:
                    delivery_time.append(pickup_travel_time)
                # provide delivery load
                if random_node_list[idx+1] in self.uniq_pickup_point:
                    delivery_load.append(self.delivery_details[dropped_idx_order[idx]].capacity)
                else:
                    delivery_load.append(self.delivery_details[dropped_idx_order[idx]].capacity)

            # check the feasibility
            if sum(delivery_time) <= time_limit and sum(delivery_load) <= self.courier_details[random_courier_ID-1].capacity:  # ToDo: Fix it with courier index
                break
            else:       # restart the search process
                # print(f"Delivery time: {sum(delivery_time)} and sum of load : {sum(delivery_load)} \n")
                delivery_time = []
                delivery_load = []
                delivery_details = copy.deepcopy(delivery_details_copy)
                if already_served_order:
                    for delivered_order in already_served_order:
                        delivery_details.pop([i for i in range(len(delivery_details)) if delivery_details[i].delivery_id == delivered_order])
        # if it found then return the same
        return delivery_load, delivery_time, random_courier_ID, random_order_list, delivery_details

    def find_courier_assignment(self) -> tuple:
        no_iter = 0
        delivery_details = copy.deepcopy(self.delivery_details)
        courier_ID = [self.courier_details[i].courier_id for i in
                      range(len(self.courier_details))]  # List of courier ids
        print("This is heutistic method")
        time_limit = 180  # given 3 hour
        max_pickup = 4  # given
        # Optimal result
        original_order_list = np.unique([delivery_details[idx].delivery_id for idx in range(len(delivery_details))])
        courier_order_assignment = {}
        objective_val = {}
        already_served_order = []
        while True:
            delivery_load, delivery_time, random_courier_ID, random_order_list, delivery_details = self.create_heu_model(delivery_details, courier_ID, time_limit, max_pickup, already_served_order)
            courier_order_assignment[random_courier_ID] = random_order_list
            objective_val[random_courier_ID] = sum(delivery_time)
            print(f"courier {random_courier_ID} served order {random_order_list}")
            no_iter +=1
            order_list = np.unique([delivery_details[idx].delivery_id for idx in range(len(delivery_details))])
            courier_ID.remove(random_courier_ID)
            np.append(already_served_order, random_order_list)
            #
            # print(f"Order list : {len(order_list)}")
            # print(f"NO of iteration {no_iter}")
            if len(order_list) < 4 or len(courier_ID) <= 0 or no_iter > np.ceil(len(original_order_list)/max_pickup)+10:
                break
        return courier_order_assignment, objective_val


if __name__ == "__main__":
    pass