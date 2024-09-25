from typing import List

class CourierRoute:
    def __init__(self, courier_id: int, nodes: List[int]):
        self.courier_id = courier_id
        self.nodes = nodes

class InstanceSolution:
    def __init__(self, instance_name: str, courier_routes: List[CourierRoute]):
        self.instance_name = instance_name
        self.courier_routes = courier_routes
