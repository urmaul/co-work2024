import numpy as np
import os
from optimisationModel import ModelComputationChall
from heuristicModel import HeuristicModel
from read_data import load_travel_time_from_csv, load_couriers_from_csv, load_deliveries_from_csv
import matplotlib.pyplot as plt
import csv
from solution import CourierRoute, InstanceSolution

data_folder = 'final_test_set'
folderpath = os.listdir('./Challenge/' + data_folder)
file_idx = 3
mip_model = False
#
print(f"Simulation for data in {folderpath[file_idx]}")
print("="*50)
#
travel_time = load_travel_time_from_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), data_folder,
                                                     folderpath[file_idx],
                                                     # 'example_data',
                                                     'traveltimes.csv'))
#
courier = load_couriers_from_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), data_folder,
                                              folderpath[file_idx],
                                              # 'example_data',
                                              'couriers.csv'))
#
deliveries = load_deliveries_from_csv(os.path.join(os.path.dirname(os.path.realpath(__file__)), data_folder,
                                                   folderpath[file_idx],
                                                   # 'example_data',
                                                   'deliveries.csv'))

if mip_model:
    model_inst_mip = ModelComputationChall(courier_details=courier,
                                       delivery_details=deliveries,
                                       time_matrix=travel_time
                                       )

    model_inst_mip.assign_depot_to_pickup_pont()

    # get the objective value
    model = model_inst_mip.create_model(model_each_depot=True,
                                    depot_idx=1)
    model.optimize()  # trigger SCIP to solve the problem
    #
    # print the objective value
    print(f"decision var: {model.getObjective()}")
    print("=" * 50)
    print(f"Objective value {model.getObjVal()}")
else:
    model_inst_heu = HeuristicModel(instance=folderpath[file_idx],
                                    method='heu1')
    courier_order_assignment, objective_val = model_inst_heu.find_courier_assignment()
    #
    # Save the result
    solution =  InstanceSolution(instance_name = folderpath[file_idx], 
                    #  courier_routes = [courier_order_assignment[idx] for idx in courier_order_assignment])
                     courier_routes = [])
    # Courier route
    for key  in courier_order_assignment:
        solution.courier_routes.append(CourierRoute(courier_id = key, 
                    nodes = courier_order_assignment[key]))
