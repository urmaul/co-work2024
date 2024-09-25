# SCIP - Python Interface
import numpy as np
import os
from pyscipopt import Model, quicksum
from read_data import load_travel_time_from_csv, load_couriers_from_csv, load_deliveries_from_csv
import itertools


# First step is to create a new problem
class ModelComputationChall:
    def __init__(self, courier_details, delivery_details, time_matrix):
        self.courier_details = courier_details
        self.delivery_details = delivery_details
        self.uniq_deliv_point = np.unique([self.delivery_details[i].dropoff_loc for i in range(len(self.delivery_details))])
        self.uniq_pickup_point = np.unique([self.delivery_details[i].pickup_loc for i in range(len(self.delivery_details))])
        self.uniq_depot = np.unique([self.courier_details[i].courier_id for i in range(len(self.courier_details))])
        time_between_nodes = {}
        for i in range(1,len(time_matrix[:][0])):
            for j in range(1,len(time_matrix[0][:])):
                time_between_nodes[i, j] = time_matrix[i][j]
        self.time_matrix = time_between_nodes
        self.set_depo_pickup = [(x,y) for x in self.uniq_depot for y in  self.uniq_pickup_point]

    def create_model(self, model_each_depot: bool = False, depot_idx: int = 0):
        # This will create model
        set_pickup = set(self.uniq_pickup_point)
        set_deliv = set(self.uniq_deliv_point)
        if model_each_depot:
            list_all_vertex = set_pickup.union(set_deliv)
            list_all_vertex.update([self.uniq_depot[depot_idx]])
        else:
            set_depot = set(self.uniq_depot)
            list_all_vertex = set_pickup.union(set_deliv.union(set_depot))
        #
        set_pickup_delivery = list(itertools.permutations(set_pickup.union(set_deliv),2))
        set_depot_to_pickup = self.assign_depot_to_pickup_pont()
        # set_depot_to_pickup = [(x,y) for x in self.uniq_depot for y in self.uniq_pickup_point]
        set_delivery_to_depot = [(x, y) for x in self.uniq_deliv_point for y in self.uniq_depot]
        set_depot_ideal = [(x,x) for x in self.uniq_depot]
        list_all_orders = [self.delivery_details[i].delivery_id for i in range(len(self.delivery_details))]
        # all edges
        list_all_edge = set_depot_to_pickup + set_pickup_delivery + set_delivery_to_depot + set_depot_ideal
        #
        T_tot = sum(self.time_matrix.values())
        Q_max = np.max([self.courier_details[i].capacity for i in range(len(self.courier_details))])

        model = Model()
        # Model Variable 
        x = {}  # Structure [(start_node, end_node, courier_no)]
        t = {}  # Delivery time
        q = {}  # Load carried by courier

        # variable: decision variable
        for k in self.uniq_depot:
            for val in list_all_edge:
                # x[val[0], val[1], k] = model.addVar(name=f"x{val[0]}_{val[1]}_{k}", lb=0, ub=1)
                x[val[0], val[1], k] = model.addVar(vtype="B", name=f"x{val[0]}_{val[1]}_{k}")

        # variable: load
        for i in list_all_vertex:
            q[i] = model.addVar(name='q[%i]' % i, lb=0, ub=Q_max)

        # variable: time
        for i in list_all_vertex:
            t[i] = model.addVar(name='t[%i]' % i, lb=0, ub=T_tot)

        # constraints - 1
        for i in list_all_vertex:
            in_ray_vertices, _ = self.find_edges_for_a_vertex(i, list_all_edge)
            model.addCons(quicksum(quicksum(x[j,i,k] for j in in_ray_vertices) for k in self.uniq_depot) == 1)

        # Constraint - 2
        for k in set_depot:
            for node in list_all_vertex:
                in_ray_vertices, out_ray_vertices = self.find_edges_for_a_vertex(node, list_all_edge)
                model.addCons(quicksum(x[i,node,k] for i in in_ray_vertices ) == quicksum(x[node,i,k] for i in out_ray_vertices))

        # constraint - 3
        for k in set_depot:
            for idx, o in enumerate(list_all_orders):
                pick_up_vert = self.delivery_details[idx].pickup_loc
                dropoff_vert = self.delivery_details[idx].dropoff_loc
                pick_up_in_vert, _ = self.find_edges_for_a_vertex(pick_up_vert, list_all_edge)
                drop_off_in_vert, _ = self.find_edges_for_a_vertex(dropoff_vert, list_all_edge)
                model.addCons(quicksum(x[i,pick_up_vert,k] for i in pick_up_in_vert)
                              == quicksum(x[j,dropoff_vert,k] for j in drop_off_in_vert))

        # constraint - 4
        for k in set_depot:
            depot_in_vert, _ = self.find_edges_for_a_vertex(k, list_all_edge)
            model.addCons(quicksum(x[j,k,k] for j in depot_in_vert) == 1)

        # constraint - 5
        for k in self.uniq_depot:
            for key in list_all_edge:
                if key[0] in set_pickup and key[1] in set_deliv:
                    model.addCons(
                        t[key[0]] + (self.time_matrix[(key[0],key[1])] + T_tot)*x[key[0],key[1],k] <= t[key[1]] + T_tot
                    )
                    model.addCons(
                        q[key[0]] + (self.time_matrix[(key[0], key[1])] + Q_max) * x[key[0], key[1], k] <= q[key[1]] + Q_max
                    )

        #
        # constraint - 6
        for idx, o in enumerate(list_all_orders):
            model.addCons(t[self.delivery_details[idx].dropoff_loc] - t[self.delivery_details[idx].pickup_loc]
                          >= self.delivery_details[idx].time_window_start)

        # constraint - 7
        for idx, k in enumerate(set_depot):
            model.addCons(q[k] == self.courier_details[idx].capacity )

        # objective
        model.setObjective(
            quicksum(t[j] for j in self.uniq_deliv_point), "minimize"
        )

        # Uncomment the following line if you want to turn off logging from PySCIPOpt:
        model.hideOutput(False)

        return model

    @staticmethod
    def find_edges_for_a_vertex(node, list_all_edge):
        in_ray_vertices = []
        out_ray_vertices = []
        for edge in list_all_edge:
            if edge[0] == node:
                out_ray_vertices.append(edge[1])
            elif edge[1] == node:
                in_ray_vertices.append(edge[0])
        return in_ray_vertices, out_ray_vertices

    def assign_depot_to_pickup_pont(self):
        depot_pickup_edge = []
        for idx, pick_up_loc in enumerate(self.uniq_pickup_point):
            depot_pickup_time = 1000
            pick_up_load = self.delivery_details[idx].capacity
            new_depot_pickup = None
            for idx_courier, depot in enumerate(self.uniq_depot):
                if self.time_matrix[(depot, pick_up_loc)] < depot_pickup_time and pick_up_load < self.courier_details[idx_courier].capacity:
                    depot_pickup_time = self.time_matrix[(depot, pick_up_loc)]
                    new_depot_pickup = depot
            depot_pickup_edge.append((new_depot_pickup, pick_up_loc))
        return depot_pickup_edge


if __name__ == "__main__":
    filefolders = os.listdir('./Challenge/training_data')
    file_idx = 7
    #
    print(f"Simulation for data in {filefolders[file_idx]}")
    print("="*50)
    #
    travel_time = load_travel_time_from_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'training_data',
                                                         filefolders[file_idx],
                                                        'traveltimes.csv'))
    #
    courier = load_couriers_from_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'training_data',
                                                  filefolders[file_idx],
                                                  'couriers.csv'))
    #
    deliveries = load_deliveries_from_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)),'training_data',
                                                       filefolders[file_idx],
                                                       'deliveries.csv'))

    model_inst = ModelComputationChall(courier_details=courier,
                                       delivery_details=deliveries,
                                       time_matrix=travel_time
                                       )

    model_inst.assign_depot_to_pickup_pont()

    # get the objective value
    model = model_inst.create_model(model_each_depot=False,
                                    depot_idx=1)
    model.optimize()  # trigger SCIP to solve the problem
    # print the objective value
    print(f"decision var: {model.getObjective()}")
    print("="*50)
    print(f"Objective value {model.getObjVal()}")
    
    # Print the variable
    for var in model.getVars(transformed=True):
        val = model.getVal(var)
        if val > 1e-6:
            var_name = str(var).replace("t_", "")
            print(var_name, end=", ")
