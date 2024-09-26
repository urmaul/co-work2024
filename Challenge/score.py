from solution import CourierRoute, InstanceSolution
from read_data import Instance

class Score:
    def __init__(self, hard: int, soft: int):
        self.hard = hard
        self.soft = soft

    def better_than(self, that: Score) -> bool:
        return self.hard < that.hard or (self.hard == that.hard and self.soft < that.soft)

def solution_score(solution: InstanceSolution, instance: Instance) -> Score:
    hard = 1 # TODO: check feasibility
    soft = 1 # TODO: score

    return Score(hard, soft)