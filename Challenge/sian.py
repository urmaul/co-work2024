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
import copy

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

    current_score = solution_score(current_solution, instance)
    best_solution = current_solution
    best_score = current_score

    first_score = current_score

    steps = len(instance.deliveries) * 3

    # print("sian start", best_score)

    if best_score.hard == 0:
        return best_solution

    for step in range(0, steps):
        # if step % len(instance.deliveries) == 0:
        #     print("step", step, step / steps * 100, best_score)

        courier1_idx = random.randrange(0, n_couriers)
        courier2_idx = random.randrange(0, n_couriers)
        n_nodes = len(current_solution.courier_routes[courier1_idx].nodes)

        if n_nodes > 0:
            next_solution = copy.deepcopy(current_solution)

            node_idx = random.randrange(0, n_nodes)
            delivery_id = current_solution.courier_routes[courier1_idx].nodes[node_idx]
            # Remove delivery from courier1
            next_solution.courier_routes[courier1_idx].nodes = [
                node for node in next_solution.courier_routes[courier1_idx].nodes if node != delivery_id
            ]
            # Add delivery to courier2
            next_solution.courier_routes[courier2_idx].nodes.append(delivery_id)
            next_solution.courier_routes[courier2_idx].nodes.append(delivery_id)

            next_score = solution_score(current_solution, instance)

            if next_score.hard <= current_score.hard:
                current_score = next_score
                current_solution = next_solution
            
                if current_score.better_than(best_score):
                    best_score = copy.deepcopy(current_score)
                    best_solution = copy.deepcopy(current_solution)

                    if best_score.hard == 0:
                        break

    
    # print("sian", first_score, "=>", best_score, best_score.better_than(first_score), best_score.better_than(first_score), best_score.better_than(first_score), best_score.better_than(first_score), best_score.better_than(first_score), best_score.better_than(first_score), best_score.better_than(first_score), best_score.better_than(first_score), best_score.better_than(first_score), best_score.better_than(first_score), best_score.better_than(first_score), best_score.better_than(first_score), best_score.better_than(first_score), best_score.better_than(first_score), best_score.better_than(first_score), best_score.better_than(first_score))

    return best_solution

