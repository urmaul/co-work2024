import os
import csv
import argparse
from optimisationModel import ModelComputationChall
from greedy import solve_greedy2
from solution import CourierRoute, InstanceSolution
from read_data import Instance, process_all_instances
from typing import List
from score import solution_score, Score

def solve(instance: Instance) -> InstanceSolution:
    solutions = [
        solve_dumb(instance),
        solve_greedy2(instance),
    ]

    best_solution = solutions[0]
    best_score = Score(1000, 1000)
    for solution in solutions:
        score = solution_score(solution, instance)
        if score.better_than(best_score):
            best_score = score
            best_solution = solution

    return best_solution

def solve_dumb(instance: Instance) -> InstanceSolution:
    solution = InstanceSolution(
        instance_name = instance.instance_name,
        courier_routes = list(map(lambda courier: CourierRoute(courier_id=courier.courier_id, nodes=[]), instance.couriers)),
    )

    solution.courier_routes[0].nodes = [ d.delivery_id for i in range(2) for d in instance.deliveries ]

    return solution

def solve_via_om(instance: Instance) -> InstanceSolution:
    model_inst = ModelComputationChall(
        courier_details=instance.couriers,
        delivery_details=instance.deliveries,
        time_matrix=instance.travel_time
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

    # print(model.getVars())
    return model_inst.to_solution()


def write_solution(result_folder: str, solution: InstanceSolution):
    file = open(f"{result_folder}/f{solution.instance_name}.csv", "w")

    file.write(f"ID\n")
    for route in solution.courier_routes:
        if len(route.nodes) == 0:
            file.write(f"{route.courier_id}\n")
        else:
            file.write(f"{route.courier_id}," + (",".join([ str(node) for node in route.nodes ])) + "\n")

    file.close()


# Entry point of the script
def main():
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(description="Process couriers, deliveries, and travel time matrices from multiple instances.")
    parser.add_argument('parent_folder', type=str, help='Path to the parent folder containing all instance folders')
    parser.add_argument('--result-folder', required=False, type=str, help='Path to the folder where results are written', default='Challenge/results')

    args = parser.parse_args()

    # Process all instances
    all_instance_data = process_all_instances(args.parent_folder)

    instances = sorted(all_instance_data, key=lambda instance: instance.complexity())

    count = len(instances)

    for i, instance in enumerate(instances):
        print(f"Solving {i}/{count} {instance.instance_name} (complexity f{instance.complexity()})...")
        solution = solve(instance)
        # print(solution)
        # print(solution_score(solution, instance))
        write_solution(args.result_folder, solution)
    # dump_instance_stats(args.parent_folder, all_instance_data)


# Main execution
if __name__ == "__main__":
    main()
