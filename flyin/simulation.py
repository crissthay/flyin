from .drone import Drone
from .conect import Connection
from .hub import Hub
from collections import deque
import heapq



class Simulation:
    def __init__(
        self,
        hubs,
        connections,
        nb_drones: int,
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


    def dijkstra(self):
        distances = {hub: float('inf') for hub in self.hubs}
        distances[self.start_hub] = 0
        parent = {
            self.start_hub: None
        }

        queue = [(0, self.start_hub)]
        while queue:
            current_dis, current_hub = heapq.heappop(queue)
            if current_dis > distances[current_hub]:
                continue

            for neighbor in self.get_neighbors(current_hub):
                if neighbor.is_blocked():
                    continue

                if neighbor.zone == "restricted":
                    weight = 2
                else:
                    weight = 1
                
                distance = current_dis + weight

                if distance < distances[neighbor]:
                    distances[neighbor] = distance
                    parent[neighbor] = current_hub
                    heapq.heappush(queue, (distance, neighbor))
        
        path = []
        if self.end_hub not in parent:
            return []
        
        current = self.end_hub
        while current is not None:
            path.append(current)
            current = parent[current]

        path.reverse() 
        return path



    """ def bfs(self):
        visited = set()
        queue = deque([self.start_hub])
        visited.add(self.start_hub)
        parent = {
            self.start_hub: None
            }

        while queue:
            hub_now = queue.popleft()
            if hub_now == self.end_hub:
                break
            for hub in self.get_neighbors(hub_now):
                if hub.is_blocked():
                    continue
                if hub in visited:
                    continue

                visited.add(hub)
                queue.append(hub)
                parent[hub] = hub_now
        path = []
        current = self.end_hub
        
        if self.end_hub not in parent:
            return []
        while current is not None:
            path.append(current)
            current = parent[current]

        path.reverse() 
        return path"""
    
    def check_connect(self, hub1, hub2):
        for connect in self.connections:
            if (
                (connect.hub1 == hub1 and connect.hub2 == hub2)
                or
                (connect.hub1 == hub2 and connect.hub2 == hub1)
            ):
                return connect
        return None
        
    def move_drone(self, drone, next_hub) -> bool:
        current = drone.location
        connection = self.check_connect(current, next_hub)
        if connection is None:
            return False
        
        if (
            not next_hub.is_full()
            and not next_hub.is_blocked()
            and not connection.is_full_connect()
        ):
            connection.add_drone(drone)
            current.remove_drone(drone)
            next_hub.add_drone(drone)
            drone.location = next_hub
            return True
        return False

    """def simulate(self):
        path = self.dijkstra()
        print("PATH:", [hub.name for hub in path])
        if not path:
            print("Can't move: no path to destination.")
            return
        turn = 1
        while any(drone.location != self.end_hub for drone in self.drone_list):
            print(f"\nTurn {turn}")
            moved = False

            for drone in self.drone_list:
                if drone.location == self.end_hub:
                    continue

                indice = path.index(drone.location)
                if indice == len(path) - 1:
                    continue

                next_hub = path[indice + 1]
                if self.move_drone(drone, next_hub):
                    moved = True
                    print(drone.id_name, "->", next_hub.name)

            for connection in self.connections:
                connection.drones.clear()  

            turn += 1

            if not moved:
                print("Can't move anymore.")
                break
"""

    def simulate(self):
        path = self.dijkstra()
        turn = 1

        if not path:
            print("Can't move: no path to destination.")
            return

        while any(
            drone.location != self.end_hub
            for drone in self.drone_list
        ):
            print(f"\nTURN {turn}")
            moves = []
            moving_out = set()

            for drone in self.drone_list:
                if drone.location == self.end_hub:
                    continue
                indice = path.index(drone.location)

                if indice == len(path) - 1:
                    continue

                next_hub = path[indice + 1]
                connection = self.check_connect(
                    drone.location,
                    next_hub
                )

                moves.append(
                    (drone, next_hub, connection)
                )
                moving_out.add(drone.location)
            moved = False
            for drone, next_hub, connection in moves:
                if next_hub.is_blocked():
                    continue

                leaving = sum(
                    1
                    for d, _, _ in moves
                    if d.location == next_hub
                )

                available_space = (
                    next_hub.max_drones
                    - len(next_hub.drones)
                    + leaving
                )

                if available_space <= 0:
                    continue

                if connection.is_full_connect():
                    continue

                connection.add_drone(drone)
                drone.location.remove_drone(drone)
                next_hub.add_drone(drone)
                drone.location = next_hub

                moved = True

                print(
                    drone.id_name,
                    "->",
                    next_hub.name
                )
            for connection in self.connections:
                connection.drones.clear()

            if not moved:
                print("Can't move anymore.")
                break

            turn += 1