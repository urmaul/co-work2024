import os
import csv
import argparse
from solution import CourierRoute, InstanceSolution
from read_data import Instance, process_all_instances
from typing import List

def solve(instance: Instance) -> InstanceSolution:
    # TODO: solve the instance

    solution = InstanceSolution(
        instance_name = instance.instance_name,
        courier_routes = [
            map(lambda courier: CourierRoute(courier_id=courier.courier_id, nodes=[]), instance.couriers)
        ],
    )

    solution.courier_routes[0] = [ d.delivery_id for i in range(2) for d in instance.deliveries ]

    return solution


# Entry point of the script
def main():
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(description="Process couriers, deliveries, and travel time matrices from multiple instances.")
    parser.add_argument('parent_folder', type=str, help='Path to the parent folder containing all instance folders')
    parser.add_argument('--result-folder', required=False, type=str, help='Path to the folder where results are written', default='Challenge/results')

    args = parser.parse_args()

    # Process all instances
    all_instance_data = process_all_instances(args.parent_folder)

    for instance in all_instance_data:
        solution = solve(instance)
        print(solution)

    # dump_instance_stats(args.parent_folder, all_instance_data)


# Main execution
if __name__ == "__main__":
    main()
