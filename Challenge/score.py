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
    iids = sorted([c.courier_id for c in instance.couriers ])
    oids = sorted([c.courier_id for c in solution.courier_routes ])
    print(iids, oids)

    hard = 0
    for courier_route in solution.courier_routes:
        route = Route(courier_route.courier_id, courier_route.nodes)
        if not is_feasible(route, instance.couriers, instance.deliveries, instance.travel_time):
            hard += 1

    # hard = 1 # TODO: check feasibility
    soft = 1 # TODO: score

    return Score(hard, soft)