import pandas as pd
import math
import random
import itertools

import numpy as np

def solve_greedy2_with_files(instance_name: str):
    PATH = f"Challenge/training_data/{instance_name}/"

    # Provide the full file paths
    file1_path = PATH + "couriers.csv"
    file2_path = PATH + "deliveries.csv"
    file3_path = PATH + "traveltimes.csv"

    # Read the CSV files into dataframes
    # Read the CSV files into dataframes
    couriers_df = pd.read_csv(file1_path).apply(pd.to_numeric, errors="coerce")
    deliveries_df = pd.read_csv(file2_path).apply(pd.to_numeric, errors="coerce")
    travel_time_df = pd.read_csv(file3_path, index_col="Locations").apply(
        pd.to_numeric, errors="coerce"
    )

    # Ensure the index and column types are integer for travel_time_df
    travel_time_df.index = travel_time_df.index.astype(int)
    travel_time_df.columns = travel_time_df.columns.astype(int)

    # Parameters
    # Parameters
    # Parameters - Extract columns from deliveries dataframe
    aa = pd.to_numeric(deliveries_df.iloc[:, 0], errors="coerce")
    bb = pd.to_numeric(deliveries_df.iloc[:, 2], errors="coerce")
    cc = pd.to_numeric(deliveries_df.iloc[:, 5], errors="coerce")

    # Calculate the max value across aa, bb, cc
    n = max(aa.max(), bb.max(), cc.max())
    pickup_locs = deliveries_df["Pickup Loc"].values.tolist()

    c = len(couriers_df)
    # Create a c x c identity matrix
    couriers_depot = np.eye(c)


    # Sets
    depots = couriers_df["Location"].values.tolist()

    # Extract the pickup and dropoff locations as lists
    pickup_locs = deliveries_df["Pickup Loc"].values.tolist()
    dropoff_locs = deliveries_df["Dropoff Loc"].values.tolist()

    # "pickup_locs:", pickup_locs)
    # print("dropoff_locs:", dropoff_locs)

    # Use zip to combine pickup and dropoff locations element-wise into pairs
    pairs = list(zip(pickup_locs, dropoff_locs))

    # print("pairs:", pairs)
    # Parameters
    cap_utilization = deliveries_df["Capacity"].values.tolist()
    max_cap = couriers_df["Capacity"].values.tolist()

    # Create a vector for capacity utilization
    cap_vector = []

    # Add elements from max_cap to cap_vector
    for i in range(len(max_cap)):
        cap_vector.append((i + 1, max_cap[i]))

    # Add elements from pairs to cap_vector
    for i in range(len(pairs)):
        cap_vector.append((pairs[i][0], -cap_utilization[i]))  # For pickup location
        cap_vector.append((pairs[i][1], cap_utilization[i]))  # For dropoff location

    # print("cap_vector:", cap_vector)
    V = range(1, n)
    K = range(1, c)


    V = range(1, n)
    K = range(1, c)

    EPS = 1.0e-6

    tt = {}

    # Iterate through the dataframe rows and columns
    for i in travel_time_df.index:
        for j in travel_time_df.columns:
            # Assign the value at the (i, j) position to the new dictionary
            tt[(i, j)] = travel_time_df.loc[i, j]

    l = {i: 1000 for i in range(1, n + 1)}
    e = {i: 0 for i in range(1, n + 1)}

    prep = {}

    # Initialize e and prep dictionaries
    e = {i: 0 for i in range(1, n + 1)}  # Assuming n is defined elsewhere
    prep = {i: 0 for i in range(1, n + 1)}

    for i in range(1, n + 1):
        for j in range(0, len(pickup_locs)):
            if deliveries_df.loc[j, "Pickup Loc"] == i:
                a = deliveries_df.loc[j, "Time Window Start"]
                e[i] = a  # Set e[i] only when there is a match
                prep[i] = deliveries_df.loc[j, "Time Window Start"]
            # Avoid overwriting non-zero values
            elif deliveries_df.loc[j, "Pickup Loc"] != i and e[i] == 0:
                e[i] = 0
                prep[i] = 0

    # print("e:", e)
    # print("l:", l)
    courier_positions = couriers_df[
        "Location"
    ].tolist()  # Starting depot locations for each courier
    # print("courier_positions:", courier_positions)
    courier_capacity = couriers_df["Capacity"].tolist()  # Capacity of each courier
    # print("courier_capacity:", courier_capacity)

    # 2. Initialize courier's current load and time
    courier_loads = [0] * len(courier_positions)  # Track current loads of each courier
    courier_times = [0] * len(courier_positions)  # Track current time of each courier

    # print("courier_loads:", courier_loads)
    # print("courier_times:", courier_times)
    # 3. Initialize tracking for assigned deliveries:
    # - Set to track deliveries that have been assigned
    assigned_deliveries = set()

    # 4. Print initialized values for verification
    # print("Courier starting positions (depots):", courier_positions)
    # print("Courier capacities:", courier_capacity)
    # print("Courier initial times:", courier_times)
    # print("Courier initial loads:", courier_loads)
    # print("Assigned deliveries (initially empty):", assigned_deliveries)


    sorted_pairs = sort_pairs_by_earliest_pickup(pairs, e)

    all_solutions = []

    (
        routes0,
        updated_couriers,
        travel_times,
        capacities,
        cap_utilization,
        arrival_times,
        total_travel_times,
        dropoff_counts,
    ) = improved_assignment_with_balanced_constraints(
        pairs, courier_positions, tt, courier_capacity, e, l, cap_utilization
    )

    solution_0 = store_solution(
        routes0, courier_positions, courier_capacity, cap_utilization, arrival_times
    )

    print(
        "Total arrival times at drop-off locations:",
        solution_0["total_arrival_times_dropOff_locations"],
    )

    # Validate that all deliveries are satisfied
    if validate_all_deliveries_assigned(routes0, sorted_pairs):
        print("All deliveries are assigned correctly!")
    else:
        print("Some deliveries are missing or unassigned.")

    # Store the first solution
    all_solutions.append(solution_0)
    all_solutions.sort(key=lambda x: x["total_arrival_times_dropOff_locations"])


    (
        routes0,
        updated_couriers,
        travel_times,
        capacities,
        cap_utilization,
        arrival_times,
        total_travel_times,
        dropoff_counts,
    ) = improved_assignment_with_balanced_constraints(
        sorted_pairs, courier_positions, tt, courier_capacity, e, l, cap_utilization
    )

    solution_1 = store_solution(
        routes0, courier_positions, courier_capacity, cap_utilization, arrival_times
    )

    print(
        "Total arrival times at drop-off locations:",
        solution_1["total_arrival_times_dropOff_locations"],
    )

    # Validate that all deliveries are satisfied
    if validate_all_deliveries_assigned(routes0, sorted_pairs):
        print("All deliveries are assigned correctly!")
    else:
        print("Some deliveries are missing or unassigned.")

    # Store the first solution
    all_solutions.append(solution_1)
    all_solutions.sort(key=lambda x: x["total_arrival_times_dropOff_locations"])

    (
        optimized_routes,
        updated_couriers,
        updated_capacities,
        updated_cap_utilization,
        updated_arrival_times,
    ) = optimize_routes_between_couriers(
        routes0, updated_couriers, capacities, cap_utilization, travel_times, arrival_times
    )

    # Validate that all deliveries are satisfied
    if validate_all_deliveries_assigned(optimized_routes, sorted_pairs):
        print("All deliveries are assigned correctly!")
    else:
        print("Some deliveries are missing or unassigned.")

    solution_2 = store_solution(
        optimized_routes,
        courier_positions,
        courier_capacity,
        cap_utilization,
        updated_arrival_times,
    )

    print(
        "Total arrival times at drop-off locations sol 2:",
        solution_2["total_arrival_times_dropOff_locations"],
    )

    # Store the second solution
    all_solutions.append(solution_2)
    all_solutions.sort(key=lambda x: x["total_arrival_times_dropOff_locations"])

    (
        optimized_routes2,
        updated_couriers,
        updated_capacities,
        updated_cap_utilization,
        updated_arrival_times,
    ) = optimize_routes_randomly(
        optimized_routes,
        updated_couriers,
        capacities,
        cap_utilization,
        travel_times,
        updated_arrival_times,
    )

    # Initialize the best solution with the initial optimized routes
    best_solution = store_solution(
        optimized_routes2,
        courier_positions,
        courier_capacity,
        cap_utilization,
        updated_arrival_times,
    )
    best_total_arrival_time = all_solutions[0]["total_arrival_times_dropOff_locations"]


    num_iterations = 20

    for iteration in range(num_iterations):
        (
            new_optimized_routes2,
            new_updated_couriers,
            new_updated_capacities,
            new_updated_cap_utilization,
            new_updated_arrival_times,
        ) = optimize_routes_randomly(
            routes0,
            updated_couriers,
            capacities,
            cap_utilization,
            travel_times,
            updated_arrival_times,
        )

        # Store the new solution
        new_solution = store_solution(
            new_optimized_routes2,
            courier_positions,
            courier_capacity,
            cap_utilization,
            new_updated_arrival_times,
        )

        # Calculate the total arrival time for the new solution
        new_total_arrival_time = new_solution["total_arrival_times_dropOff_locations"]

        # Check if the new solution is better than the best solution
        if new_total_arrival_time < best_total_arrival_time:
            optimized_routes2 = new_optimized_routes2
            best_solution = new_solution
            best_total_arrival_time = new_total_arrival_time
            print(
                f"Iteration {iteration + 1}: Improved total arrival time to {best_total_arrival_time}"
            )

    # Validate that all deliveries are satisfied
    if validate_all_deliveries_assigned(optimized_routes2, sorted_pairs):
        print("All deliveries are assigned correctly!")
    else:
        print("Some deliveries are missing or unassigned.")

    solution_3 = best_solution

    print(
        "Total arrival times at drop-off locations sol 3:",
        solution_3["total_arrival_times_dropOff_locations"],
    )

    # Store the third solution
    all_solutions.append(solution_3)

    # Sort all solutions by total arrival times at drop-off locations
    all_solutions.sort(key=lambda x: x["total_arrival_times_dropOff_locations"])

    print(
        "best sol: total arrival times at drop-off location",
        all_solutions[0]["total_arrival_times_dropOff_locations"],
    )
    for courier_id, route in all_solutions[0]["routes"].items():
        if route:  # Check if the route is not empty
            print(f"Courier {courier_id}'s length route: {len(route)}")
            # print(f"Courier {courier_id}'s route: {route}")



def sort_pairs_by_earliest_pickup(pairs, e):
    """
    Sort the pickup-dropoff pairs based on the earliest pickup time.
    :param pairs: List of tuples where each tuple is (pickup, dropoff)
    :param e: Dictionary with earliest pickup times for each location
    :return: Sorted list of pickup-dropoff pairs
    """
    # Sort the pairs by the earliest time of the pickup location
    sorted_pairs = sorted(pairs, key=lambda x: e[x[0]])  # x[0] is the pickup location
    return sorted_pairs


# Method to validate that all deliveries are assigned
def validate_all_deliveries_assigned(routes, sorted_pairs):
    # Extract all deliveries from the routes
    assigned_deliveries = set()
    for courier_id, route in routes.items():
        for pickup, dropoff in route:
            assigned_deliveries.add((pickup, dropoff))

    # Check if all sorted_pairs are in assigned_deliveries
    for pickup, dropoff in sorted_pairs:
        if (pickup, dropoff) not in assigned_deliveries:
            print(f"Error: Delivery from {pickup} to {dropoff} is unassigned!")
            return False

    print("Validation passed: All deliveries are assigned.")
    return True


def store_solution(routes, couriers, capacities, cap_utilization, arrival_times):
    """
    Store the result of a method in a dictionary called 'solution', including total arrival times at drop-off locations.
    :param routes: Assigned routes for each courier.
    :param couriers: List of couriers' current positions.
    :param capacities: List of couriers' remaining capacities.
    :param cap_utilization: List of capacities used by each delivery.
    :param arrival_times: List of arrival times at each drop-off location.
    :return: A dictionary storing the solution including total arrival times at drop-off locations.
    """
    # Calculate total arrival times at drop-off locations
    total_arrival_times_dropOff_locations = sum(
        [time for _, times in arrival_times.items() for _, time in times]
    )

    solution = {
        "routes": routes,
        "couriers": couriers,
        "capacities": capacities,
        "cap_utilization": cap_utilization,
        "arrival_times": arrival_times,
        "total_arrival_times_dropOff_locations": total_arrival_times_dropOff_locations,
    }

    return solution


def improved_assignment_with_balanced_constraints(
    sorted_pairs, couriers, travel_times, capacities, e, l, cap_utilization
):
    """
    Perform balanced assignment of deliveries where each pickup-dropoff pair is assigned to a courier.
    Enforce constraints:
    - Maximum 8 drop-offs
    - 180 minutes of travel time
    - Capacity constraints
    Redistribute to balance pick-ups and drop-offs across couriers.
    :param sorted_pairs: List of sorted (pickup, dropoff) pairs
    :param couriers: List of couriers' current positions
    :param travel_times: Dictionary of travel times between locations
    :param capacities: List of couriers' capacities
    :param e: Dictionary of earliest pickup times
    :param l: Dictionary of latest delivery times
    :param cap_utilization: List of delivery capacities to ensure capacity constraints
    """
    # Initialize tracking of which deliveries are assigned
    assigned_deliveries = set()
    unassigned_deliveries = []  # To store deliveries that cannot be initially assigned

    # Initialize routes, time, and capacity tracking for each courier
    routes = {courier_id: [] for courier_id in range(len(couriers))}
    arrival_times = {
        courier_id: [] for courier_id in range(len(couriers))
    }  # To store arrival times
    total_travel_times = {
        courier_id: 0 for courier_id in range(len(couriers))
    }  # Track travel times
    dropoff_counts = {
        courier_id: 0 for courier_id in range(len(couriers))
    }  # Track drop-offs per courier

    # Function to find the courier with the fewest deliveries
    def get_least_loaded_courier():
        return min(dropoff_counts, key=dropoff_counts.get)

    # Try to assign deliveries to balance the number of pickups and drop-offs
    for idx, (pickup, dropoff) in enumerate(sorted_pairs):
        delivery_capacity = cap_utilization[
            idx
        ]  # The capacity required for the current delivery

        assigned = False  # Track if delivery was assigned
        for _ in range(len(couriers)):
            courier_id = (
                get_least_loaded_courier()
            )  # Get the courier with the fewest deliveries
            current_position = couriers[courier_id]
            current_capacity = capacities[courier_id]
            current_time = total_travel_times[courier_id]

            # Check if the courier can handle the delivery based on capacity, time, and drop-off limit
            if (
                current_capacity
                >= abs(delivery_capacity)  # Ensure enough capacity for pickup
                and dropoff_counts[courier_id] < 8  # Ensure no more than 8 drop-offs
                and current_time < 180  # Ensure total time does not exceed 180 minutes
            ):
                # Calculate travel time to the pickup location
                travel_to_pickup = travel_times[(current_position, pickup)]
                new_time_after_pickup = current_time + travel_to_pickup

                # Calculate travel time to the drop-off location
                travel_to_dropoff = travel_times[(pickup, dropoff)]
                new_time_after_dropoff = new_time_after_pickup + travel_to_dropoff

                # Check if the new time would exceed the limit of 180 minutes
                if new_time_after_dropoff <= 180:
                    # Update courier's state
                    current_time = new_time_after_dropoff
                    total_travel_times[courier_id] = current_time
                    dropoff_counts[courier_id] += 1
                    current_capacity -= abs(
                        delivery_capacity
                    )  # Decrease capacity at pickup
                    current_capacity += (
                        delivery_capacity  # Restore capacity at drop-off
                    )

                    # Assign delivery
                    routes[courier_id].append((pickup, dropoff))
                    couriers[courier_id] = dropoff  # Update the courier's position
                    assigned_deliveries.add(pickup)
                    assigned = True

                    # Store arrival time at drop-off
                    arrival_times[courier_id].append((dropoff, current_time))
                    # print(
                    #     f"Assigned delivery {pickup} -> {dropoff} to Courier {courier_id}."
                    # )
                    break

        if not assigned:
            # print(
            #     f"Skipped: Could not assign delivery {pickup} -> {dropoff}. Adding to unassigned."
            # )
            unassigned_deliveries.append((pickup, dropoff, idx))

    # Redistribute unassigned deliveries to balance the number of deliveries
    for pickup, dropoff, idx in unassigned_deliveries:
        delivery_capacity = cap_utilization[idx]

        for courier_id in range(len(couriers)):
            current_position = couriers[courier_id]
            current_capacity = capacities[courier_id]
            current_time = total_travel_times[courier_id]

            # Check if the courier can handle the delivery
            if (
                current_capacity
                >= abs(delivery_capacity)  # Ensure enough capacity for pickup
                and dropoff_counts[courier_id] < 4  # Ensure no more than X drop-offs
                and current_time < 180  # Ensure total time does not exceed 180 minutes
            ):
                # Calculate travel time for reassignment
                travel_to_pickup = travel_times[(current_position, pickup)]
                travel_to_dropoff = travel_times[(pickup, dropoff)]
                new_time = current_time + travel_to_pickup + travel_to_dropoff

                if new_time <= 180:
                    # Assign the delivery
                    # print(
                    #     f"Assigning unassigned delivery {pickup} -> {dropoff} to Courier {courier_id}."
                    # )
                    routes[courier_id].append((pickup, dropoff))
                    couriers[courier_id] = dropoff
                    total_travel_times[courier_id] = new_time
                    dropoff_counts[courier_id] += 1
                    current_capacity -= abs(delivery_capacity)
                    current_capacity += delivery_capacity
                    arrival_times[courier_id].append((dropoff, new_time))
                    break

    return (
        routes,
        couriers,
        travel_times,
        capacities,
        cap_utilization,
        arrival_times,
        total_travel_times,
        dropoff_counts,
    )


################ Second part ###########


# 2-Opt Local Search between two different routes for optimization
def two_opt_between_routes(route1, route2, travel_times, arrival_times):
    best_route1, best_route2 = route1, route2
    best_arrival_time = calculate_total_arrival_time(
        route1, arrival_times
    ) + calculate_total_arrival_time(route2, arrival_times)

    # Attempt 2-Opt between two routes (i.e., swapping parts of the routes)
    for i, j in itertools.combinations(range(1, len(route1)), 2):
        for k, l in itertools.combinations(range(1, len(route2)), 2):
            # Swap sections between the two routes
            new_route1 = route1[:i] + route2[k:l] + route1[j:]
            new_route2 = route2[:k] + route1[i:j] + route2[l:]

            # Calculate the new total arrival times
            new_arrival_time = calculate_total_arrival_time(
                new_route1, arrival_times
            ) + calculate_total_arrival_time(new_route2, arrival_times)

            # If the new arrival times are better, update the routes
            if new_arrival_time < best_arrival_time:
                best_route1, best_route2 = new_route1, new_route2
                best_arrival_time = new_arrival_time

    return best_route1, best_route2


# Helper function to calculate the total arrival time for a route
def calculate_total_arrival_time(route, arrival_times):
    total_arrival_time = 0
    for pickup, dropoff in route:
        total_arrival_time += arrival_times.get(
            dropoff, float("inf")
        )  # Sum arrival times at drop-off locations
    return total_arrival_time


# Apply 2-Opt between different routes for optimization
def optimize_routes_between_couriers(
    routes, couriers, capacities, cap_utilization, travel_times, arrival_times
):
    optimized_routes = {}
    route_ids = list(routes.keys())

    # Iterate over all pairs of routes for potential optimization
    for i in range(len(route_ids)):
        for j in range(i + 1, len(route_ids)):
            courier1 = route_ids[i]
            courier2 = route_ids[j]

            route1, route2 = routes[courier1], routes[courier2]

            # Only apply 2-Opt between two routes if both have more than 1 pair of deliveries
            if len(route1) > 1 and len(route2) > 1:
                optimized_route1, optimized_route2 = two_opt_between_routes(
                    route1, route2, travel_times, arrival_times
                )
                optimized_routes[courier1] = optimized_route1
                optimized_routes[courier2] = optimized_route2
                # print(
                #     f"Optimized routes between Courier {courier1} and Courier {courier2} based on arrival times."
                # )
            else:
                # If no optimization is possible, leave the routes unchanged
                optimized_routes[courier1] = route1
                optimized_routes[courier2] = route2

    # Update couriers' positions, capacities, and arrival times based on optimized routes
    for courier_id, route in optimized_routes.items():
        last_dropoff = (
            route[-1][1] if route else couriers[courier_id]
        )  # Last drop-off location or original position
        couriers[courier_id] = last_dropoff  # Update courier's current position

        # Recalculate capacity and update arrival times
        current_capacity = capacities[courier_id]
        current_time = 0  # Reinitialize time tracking
        for pickup, dropoff in route:
            # Update capacity based on pickup and dropoff
            capacity_index = [
                i
                for i, (p, d) in enumerate(routes[courier_id])
                if p == pickup and d == dropoff
            ]
            if capacity_index:
                current_capacity -= abs(
                    cap_utilization[capacity_index[0]]
                )  # Subtract pickup capacity
                current_capacity += cap_utilization[
                    capacity_index[0]
                ]  # Add dropoff capacity

            # Calculate arrival times at drop-off points based on travel times
            travel_to_pickup = travel_times.get((couriers[courier_id], pickup), 0)
            travel_to_dropoff = travel_times.get((pickup, dropoff), 0)
            current_time += travel_to_pickup + travel_to_dropoff
            arrival_times[courier_id].append((dropoff, current_time))

        capacities[courier_id] = current_capacity  # Update the capacity for the courier

    # Return updated information
    return optimized_routes, couriers, capacities, cap_utilization, arrival_times


# Apply 2-Opt with random selection of route pairs and optimization based on arrival times
def optimize_routes_randomly(
    routes, couriers, capacities, cap_utilization, travel_times, arrival_times
):
    optimized_routes = routes.copy()
    route_ids = list(routes.keys())

    # Randomly shuffle the route IDs for random selection
    random.shuffle(route_ids)

    # Iterate randomly through all pairs of routes for potential optimization
    for _ in range(
        len(route_ids) // 2
    ):  # Limit the number of iterations to half the number of couriers
        # Randomly select two distinct routes (two different couriers)
        courier1, courier2 = random.sample(route_ids, 2)  # Ensure they are different

        route1, route2 = optimized_routes[courier1], optimized_routes[courier2]

        # Only apply 2-Opt between two routes if both have more than 1 pair of deliveries
        if len(route1) > 1 and len(route2) > 1:
            optimized_route1, optimized_route2 = two_opt_between_routes(
                route1, route2, travel_times, arrival_times
            )

            # If the routes were improved based on arrival time, accept the change
            if calculate_total_arrival_time(
                optimized_route1, arrival_times
            ) < calculate_total_arrival_time(
                route1, arrival_times
            ) or calculate_total_arrival_time(
                optimized_route2, arrival_times
            ) < calculate_total_arrival_time(
                route2, arrival_times
            ):
                optimized_routes[courier1] = optimized_route1
                optimized_routes[courier2] = optimized_route2
                print(
                    f"Optimized routes between Courier {courier1} and Courier {courier2} based on arrival times."
                )
        else:
            # If no optimization is possible, leave the routes unchanged
            optimized_routes[courier1] = route1
            optimized_routes[courier2] = route2

    # Update couriers' positions, capacities, and arrival times based on optimized routes
    for courier_id, route in optimized_routes.items():
        last_dropoff = (
            route[-1][1] if route else couriers[courier_id]
        )  # Last drop-off location or original position
        couriers[courier_id] = last_dropoff  # Update courier's current position

        # Recalculate capacity and update arrival times
        current_capacity = capacities[courier_id]
        current_time = 0  # Reinitialize time tracking
        for pickup, dropoff in route:
            # Update capacity based on pickup and dropoff
            capacity_index = [
                i
                for i, (p, d) in enumerate(routes[courier_id])
                if p == pickup and d == dropoff
            ]
            if capacity_index:
                current_capacity -= abs(
                    cap_utilization[capacity_index[0]]
                )  # Subtract pickup capacity
                current_capacity += cap_utilization[
                    capacity_index[0]
                ]  # Add dropoff capacity

            # Calculate arrival times at drop-off points based on travel times
            travel_to_pickup = travel_times.get((couriers[courier_id], pickup), 0)
            travel_to_dropoff = travel_times.get((pickup, dropoff), 0)
            current_time += travel_to_pickup + travel_to_dropoff
            arrival_times[courier_id].append((dropoff, current_time))

        capacities[courier_id] = current_capacity  # Update the capacity for the courier

    # Return updated information
    return optimized_routes, couriers, capacities, cap_utilization, arrival_times


if __name__ == "__main__":
    # /Users/lorenareyes/Library/CloudStorage/OneDrive-UniversidaddelaSabana/workspace_python/co-work2024-main-5/Challenge/training_data/1adef166-1111-45fd-b722-0f817c7fa055
    # PATH = "Challenge/training_data/ae2e3aac-1651-469c-9366-879a1142ed36/"
    solve_greedy2_with_files("ae2e3aac-1651-469c-9366-879a1142ed36")
    # 1adef166-1111-45fd-b722-0f817c7fa055
    # 1ad01be7-2897-4c4f-83f0-cfa7953cc8b8
    # medium
    # 55040a39-20d3-4346-b351-22d23633e976
    # large
    # ae2e3aac-1651-469c-9366-879a1142ed36

