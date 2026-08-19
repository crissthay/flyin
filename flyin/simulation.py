from typing import Optional
import heapq

from .drone import Drone
from .conect import Connection
from .hub import Hub


class Simulation:
    def __init__(
        self,
        hubs: list[Hub],
        connections: list[Connection],
        nb_drones: int,
        start_hub: Hub,
        end_hub: Hub,
    ) -> None:
        self.hubs = hubs
        self.connections = connections
        self.nb_drones = nb_drones
        self.start_hub = start_hub
        self.end_hub = end_hub
        self.drone_list: list[Drone] = []
        self._adj: dict[Hub, list[Hub]] = self._build_adjacency()

    def _build_adjacency(self) -> dict[Hub, list[Hub]]:
        adj: dict[Hub, list[Hub]] = {hub: [] for hub in self.hubs}
        for conn in self.connections:
            adj[conn.hub1].append(conn.hub2)
            adj[conn.hub2].append(conn.hub1)
        return adj

    def create_drones(self) -> None:
        for i in range(self.nb_drones):
            name_drone = f"drone_{i}"
            new_drone = Drone(name_drone, self.start_hub)
            self.start_hub.add_drone(new_drone)
            self.drone_list.append(new_drone)

    def get_neighbors(self, hub: Hub) -> list[Hub]:
        return self._adj[hub]

    def dijkstra_from(self, source: Hub) -> dict[Hub, Optional[Hub]]:
        distances: dict[Hub, tuple[float, int]] = {
            hub: (float("inf"), 0) for hub in self.hubs
        }
        distances[source] = (0, 0)
        parent: dict[Hub, Optional[Hub]] = {source: None}
        counter = 0
        queue: list[tuple[float, int, int, Hub]] = [(0, 0, counter, source)]

        while queue:
            current_dis, neg_priority, _, current_hub = heapq.heappop(queue)
            current_priority = -neg_priority

            if (
                current_dis > distances[current_hub][0]
                or (
                    current_dis == distances[current_hub][0]
                    and current_priority < distances[current_hub][1]
                )
            ):
                continue

            for neighbor in self.get_neighbors(current_hub):
                if neighbor.is_blocked():
                    continue

                weight = 2 if neighbor.zone == "restricted" else 1
                priority = current_priority + (1 if neighbor.zone == "priority" else 0)
                distance = current_dis + weight

                if (
                    distance < distances[neighbor][0]
                    or (
                        distance == distances[neighbor][0]
                        and priority > distances[neighbor][1]
                    )
                ):
                    distances[neighbor] = (distance, priority)
                    parent[neighbor] = current_hub
                    counter += 1
                    heapq.heappush(
                        queue, (distance, -priority, counter, neighbor)
                    )

        return parent

    @staticmethod
    def rebuild_path(
        parent: dict[Hub, Optional[Hub]], source: Hub, target: Hub
    ) -> list[Hub]:
        if target not in parent:
            return []
        path: list[Hub] = []
        current: Optional[Hub] = target
        while current is not None:
            path.append(current)
            current = parent[current]
        path.reverse()
        if not path or path[0] != source:
            return []
        return path

    def next_hop(self, drone: Drone) -> Optional[Hub]:
        parent = self.dijkstra_from(drone.location)
        path = self.rebuild_path(parent, drone.location, self.end_hub)
        if len(path) < 2:
            return None
        return path[1]

    def check_connect(self, hub1: Hub, hub2: Hub) -> Optional[Connection]:
        for connect in self.connections:
            if (connect.hub1 == hub1 and connect.hub2 == hub2) or (
                connect.hub1 == hub2 and connect.hub2 == hub1
            ):
                return connect
        return None

    def is_done(self) -> bool:
        return all(drone.location == self.end_hub for drone in self.drone_list)

    def simulate(self) -> None:
        parent = self.dijkstra_from(self.start_hub)
        if self.end_hub not in parent:
            print("Can't move: no path to destination.")
            return

        self.turn = 1
        while not self.is_done():
            if not self.step():
                break

    def step(self) -> bool:
       
        if not hasattr(self, "turn"):
            self.turn = 1

        if self.is_done():
            return False

        turn = self.turn
        if True:
            print(f"\nTURN {turn}")

            for drone in self.drone_list:
                if not drone.in_transit:
                    continue

                drone.remaining_turns -= 1

                if drone.remaining_turns == 0:
                    assert drone.target is not None
                    drone.target.add_drone(drone)
                    drone.location = drone.target

                    if drone.connection is not None:
                        drone.connection.remove_drone(drone)

                    drone.in_transit = False
                    drone.target = None
                    drone.connection = None

                    print(drone.id_name, "arrived at", drone.location.name)

            moves: list[tuple[Drone, Hub, Connection]] = []

            for drone in self.drone_list:
                if drone.location == self.end_hub or drone.in_transit:
                    continue

                next_hub = self.next_hop(drone)
                if next_hub is None:
                    continue

                connection = self.check_connect(drone.location, next_hub)
                if connection is None:
                    continue

                moves.append((drone, next_hub, connection))

            moved = False

   
            for drone, next_hub, connection in moves:
                if next_hub.is_blocked():
                    continue
                if connection.is_full_connect():
                    continue

                leaving = sum(
                    1
                    for d, _, _ in moves
                    if d.location == next_hub and d is not drone
                )
                available_space = (
                    next_hub.max_drones - len(next_hub.drones) + leaving
                )
                if available_space <= 0:
                    continue

                connection.add_drone(drone)
                drone.location.remove_drone(drone)
                drone.connection = connection

                if next_hub.zone == "restricted":
                    drone.in_transit = True
                    drone.target = next_hub
                    drone.remaining_turns = 1
                    print(drone.id_name, "->", next_hub.name, "(restricted)")
                else:
                    next_hub.add_drone(drone)
                    drone.location = next_hub
                    connection.remove_drone(drone)
                    drone.connection = None
                    print(drone.id_name, "->", next_hub.name)

                moved = True

            if not moved and not any(d.in_transit for d in self.drone_list):
                print("Can't move anymore.")
                return False

            self.turn += 1
            return True