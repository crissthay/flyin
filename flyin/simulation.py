from .drone import Drone
import heapq
from .hub import Hub
from .conect import Connection
from typing import Union, Optional


class Simulation:
    def __init__(
        self,
        hubs: list[Hub],
        connections: list[Connection],
        nb_drones: int,
        start_hub: Hub,
        end_hub: Hub
    ):
        self.hubs: list[Hub] = hubs
        self.connections: list[Connection] = connections
        self.nb_drones: int = nb_drones
        self.start_hub: Hub = start_hub
        self.end_hub: Hub = end_hub
        self.drone_list: list[Drone] = []
        self.history: list[list[tuple[str, Hub, Hub]]] = []

    def create_drones(self):
        for i in range(self.nb_drones):
            name_drone: str = f"\nD{i}"
            new_drone: Drone = Drone(name_drone, self.start_hub)
            self.start_hub.add_drone(new_drone)
            self.drone_list.append(new_drone)

    def get_neighbors(self, hub):
        neighbors: list[Hub] = []
        for conn in self.connections:
            if conn.hub1 == hub:
                neighbors.append(conn.hub2)
            elif conn.hub2 == hub:
                neighbors.append(conn.hub1)
        return neighbors

    def dijkstra(self):
        distances: dict[Hub, tuple[Union[int, float], int]] = {
            hub: (float('inf'), 0)
            for hub in self.hubs
        }

        distances[self.start_hub] = (0, 0)

        parent: dict[Hub, Optional[Hub]] = {
            self.start_hub: None
        }

        counter: int = 0

        queue: list[tuple[Union[int, float], int, int, Hub]] = [
            (0, 0, counter, self.start_hub)
        ]

        while queue:
            (current_dis, current_priority,
             _, current_hub) = heapq.heappop(queue)

            current_priority = -current_priority

            if (
                current_dis > distances[current_hub][0]
                or
                (
                    current_dis == distances[current_hub][0]
                    and current_priority < distances[current_hub][1]
                )
            ):
                continue

            for neighbor in self.get_neighbors(current_hub):

                if neighbor.is_blocked():
                    continue

                if neighbor.zone == "restricted":
                    weight: int = 2
                else:
                    weight = 1

                priority: int = current_priority

                if neighbor.zone == "priority":
                    priority += 1

                distance: Union[int, float] = current_dis + weight

                if (
                    distance < distances[neighbor][0]
                    or
                    (
                        distance == distances[neighbor][0]
                        and priority > distances[neighbor][1]
                    )
                ):
                    distances[neighbor] = (
                        distance,
                        priority
                    )

                    parent[neighbor] = current_hub

                    counter += 1

                    heapq.heappush(
                        queue,
                        (
                            distance,
                            -priority,
                            counter,
                            neighbor
                        )
                    )

        path: list[Hub] = []

        if self.end_hub not in parent:
            return []

        current = self.end_hub

        while current is not None:
            path.append(current)
            current = parent[current]

        path.reverse()
        total_cost: int = 0
        total_priority: int = 0

        for hub in path[1:]:
            if hub.zone == "restricted":
                total_cost += 2
            else:
                total_cost += 1

            if hub.zone == "priority":
                total_priority += 1

        print("COST:", total_cost)
        print("PRIORITY:", total_priority)
        print("PATH:", path)
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

    def print_capacity_info(self) -> None:
        for hub in self.hubs:
            cap = hub.max_drones
            cap_str = "inf" if cap == float("inf") else str(int(cap))
            print(f"Zone {hub.name}: {len(hub.drones)}/{cap_str} drones")

        for conn in self.connections:
            cap = conn.max_link_capacity
            cap_str = "inf" if cap == float("inf") else str(int(cap))
            print(
                f"Connection {conn.hub1.name}-{conn.hub2.name}: "
                f"{len(conn.drones)}/{cap_str} capacity used"
            )

    def simulate(self, capacity_info: bool = False):
        path: list[Hub] = self.dijkstra()
        turn: int = 1

        if not path:
            print("Can't move: no path to destination.")
            return

        while any(
            drone.location != self.end_hub
            for drone in self.drone_list
        ):
            turn_output: list[str] = []

            turn_moves: list[tuple[str, Hub, Hub]] = []

            already_acted: set[Drone] = set()

            for drone in self.drone_list:

                if not drone.in_transit:
                    continue

                drone.remaining_turns -= 1

                if drone.remaining_turns == 0:

                    drone.target.add_drone(drone)
                    drone.location = drone.target

                    if drone.connection is not None:
                        drone.connection.remove_drone(drone)

                    drone.in_transit = False
                    drone.target = None
                    drone.connection = None

                    already_acted.add(drone)

                    turn_output.append(
                        f"{drone.id_name}-{drone.location.name}"
                    )

            moves: list[
                tuple[Drone, Hub, Optional[Connection]]
            ] = []

            for drone in self.drone_list:

                if drone in already_acted:
                    continue

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

                if next_hub.is_blocked():
                    continue

                if connection.is_full_connect():
                    continue

                available_space = (
                    next_hub.max_drones
                    - len(next_hub.drones)
                )

                if available_space <= 0:
                    continue

                # GUARDAR DE ONDE O DRONE SAIU
                start_hub = drone.location

                connection.add_drone(drone)
                drone.location.remove_drone(drone)

                if next_hub.zone == "restricted":

                    drone.in_transit = True
                    drone.target = next_hub
                    drone.remaining_turns = 1
                    drone.connection = connection

                    turn_output.append(
                        f"{drone.id_name}-"
                        f"{start_hub.name}-{next_hub.name}"
                    )

                else:

                    next_hub.add_drone(drone)
                    drone.location = next_hub
                    connection.remove_drone(drone)

                    turn_output.append(
                        f"{drone.id_name}-{next_hub.name}"
                    )

                #GUARDAR MOVIMENTO
                turn_moves.append(
                    (
                        drone.id_name,
                        start_hub,
                        next_hub
                    )
                )

                moved = True

            if not turn_output and not any(
                d.in_transit for d in self.drone_list
            ):
                print("Can't move anymore.")
                break

            if turn_output:
                print(" ".join(turn_output))

            if capacity_info:
                self.print_capacity_info()
                print()

            self.history.append(turn_moves)

            turn += 1