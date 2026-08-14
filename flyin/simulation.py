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
        distances = {
            hub: (float('inf'), 0)
            for hub in self.hubs
        }

        distances[self.start_hub] = (0, 0)
        parent = {
            self.start_hub: None
        }

        queue = [(0, 0, self.start_hub)]
        while queue:
            current_dis, current_priority, current_hub = heapq.heappop(queue)
            if current_dis > distances[current_hub][0]:
                continue

            for neighbor in self.get_neighbors(current_hub):
                if neighbor.is_blocked():
                    continue
                    
                if neighbor.zone == "restricted":
                    weight = 2
                else:
                    weight = 1
                
                priority = current_priority

                if neighbor.zone == "priority":
                    priority += 1
                distance = current_dis + weight

                if (
                    distance < distances[neighbor][0]
                    or
                    (
                        distance == distances[neighbor][0]
                        and priority > distances[neighbor][1]
                    )
                ):
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

            for drone in self.drone_list:
                if not drone.in_transit:
                    continue

                drone.remaining_turns -= 1

                if drone.remaining_turns == 0:
                    drone.target.add_drone(drone)
                    drone.location = drone.target

                    drone.in_transit = False
                    drone.target = None
                    drone.connection = None

                    print(
                        drone.id_name,
                        "arrived at",
                        drone.location.name
                    )

            moves = []

            for drone in self.drone_list:

                if drone.location == self.end_hub:
                    continue

                if drone.in_transit:
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

            moved = False

            for drone, next_hub, connection in moves:

                # blockeddd 
                if next_hub.is_blocked():
                    continue

                if connection.is_full_connect():
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

                connection.add_drone(drone)
                drone.location.remove_drone(drone)

                if next_hub.zone == "restricted":

                    drone.in_transit = True
                    drone.target = next_hub
                    drone.remaining_turns = 1
                    drone.connection = connection

                    print(
                        drone.id_name,
                        "->",
                        next_hub.name,
                        "(restricted)"
                    )

                else:

                    next_hub.add_drone(drone)
                    drone.location = next_hub

                    print(
                        drone.id_name,
                        "->",
                        next_hub.name
                    )

                moved = True

            for connection in self.connections:
                connection.drones.clear()

            if not moved:
                print("Can't move anymore.")
                break

            turn += 1