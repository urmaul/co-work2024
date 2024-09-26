from solution import CourierRoute, InstanceSolution
from read_data import Instance
from feasibility_checker import is_feasible, Route

class Score:
    def __init__(self, hard: int, soft: int):
        self.hard = hard
        self.soft = soft

    def better_than(self, that) -> bool:
        return self.hard < that.hard or (self.hard == that.hard and self.soft < that.soft)

    def __repr__(self):
        return f"{self.hard}/{self.soft}"

def solution_score(solution: InstanceSolution, instance: Instance) -> Score:
    hard = 0
    for courier_route in solution.courier_routes:
        route = Route(courier_route.courier_id, courier_route.nodes)
        if not is_feasible(route, instance.couriers, instance.deliveries, instance.travel_time):
            hard += 1

    couriers_by_id = {}
    for c in instance.couriers:
        couriers_by_id[c.courier_id] = c

    deliveries_by_id = {}
    for d in instance.deliveries:
        deliveries_by_id[d.delivery_id] = d

    soft = 0

    for courier_route in solution.courier_routes:
        current_time = 0
        prev_location = couriers_by_id[courier_route.courier_id].location

        start_times = {}
        for node in courier_route.nodes:
            delivery = deliveries_by_id[node]
            if node not in start_times:
                # This is pickup
                new_location = delivery.pickup_loc
                current_time = max(current_time + instance.travel_time[prev_location - 1][new_location - 1], delivery.time_window_start)
                start_times[node] = current_time
                prev_location = new_location
            else:
                # This is dropoff
                new_location = delivery.dropoff_loc
                current_time = current_time + instance.travel_time[prev_location - 1][new_location - 1]
                soft += current_time - start_times[node]
                prev_location = new_location

    return Score(hard, soft)