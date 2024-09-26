import os
import csv
import argparse
from optimisationModel import ModelComputationChall
from greedy import solve_greedy2
from solution import CourierRoute, InstanceSolution
from read_data import Instance, process_all_instances
from typing import List
from score import solution_score, Score
import random

def solve_sian(instance: Instance) -> InstanceSolution:

    n_couriers = len(instance.couriers)

    current_solution = InstanceSolution(
        instance_name = instance.instance_name,
        courier_routes = [CourierRoute(courier_id=courier.courier_id, nodes=[]) for courier in instance.couriers],
    )
    current_solution.algo = "sian"

    for i,d in enumerate(instance.deliveries):
        current_solution.courier_routes[i % n_couriers].nodes.append(d.delivery_id)
        current_solution.courier_routes[i % n_couriers].nodes.append(d.delivery_id)

    print(current_solution)

    current_score = solution_score(current_solution, instance)
    best_solution = current_solution
    best_score = current_score

    steps = len(instance.deliveries) * 50

    for step in range(0, steps):
        courier1_idx = random.randrange(0, n_couriers)
        courier2_idx = random.randrange(0, n_couriers)
        n_nodes = len(current_solution.courier_routes[courier1_idx].nodes)

        if n_nodes > 0:
            node_idx = random.randrange(0, n_nodes)
            delivery_id = current_solution.courier_routes[courier1_idx].nodes[node_idx]
            # Remove delivery from courier1
            current_solution.courier_routes[courier1_idx].nodes = [
                node for node in current_solution.courier_routes[courier1_idx].nodes if node != delivery_id
            ]
            # Add delivery to courier2
            current_solution.courier_routes[courier2_idx].nodes.append(delivery_id)
            current_solution.courier_routes[courier2_idx].nodes.append(delivery_id)

            current_score = solution_score(current_solution, instance)

            if current_score.better_than(best_score):
                best_score = current_score
                best_solution = current_solution
    
    return best_solution

