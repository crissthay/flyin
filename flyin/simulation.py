from .drone import Drone
from .conect import Connection
from .hub import Hub
from collections import deque

class Simulation:
    def __init__(
        self,
        hubs,
        connections,
        nb_drones,
        start_hub,
        end_hub
        ):
            self.hubs = hubs
            self.connections = connections
            self.nb_drones = nb_drones
            self.start_hub = start_hub
            self.end_hub = end_hub
            self.drone_list = []

    def  create_drones(self):
        for i in range(self.nb_drones):
            name_drone = f"drone_{i}"
            new_drone = Drone(name_drone, self.start_hub)
            self.start_hub.add_drone(new_drone)
            self.drone_list.append(new_drone)
    
    def get_neighbors(self, hub):
        neighbors = []
        for conn in self.connections:
            if conn.hub1 == hub:
                neighbors.append(conn.hub2)
            elif conn.hub2 == hub:
                neighbors.append(conn.hub1)
        return neighbors

    def bfs(self):
        visited = set()
        queue = deque([self.start_hub])
        visited.add(self.start_hub)
        parent = {
            self.start_hub: None
            }
        visit_order = []

        while queue:
            hub_now = queue.popleft()
            visit_order.append(hub_now)
            if hub_now == self.end_hub:
                break
            for hub in self.get_neighbors(hub_now):
                if hub not in visited:
                    visited.add(hub)
                    queue.append(hub)
                    parent[hub] = hub_now

            
        return