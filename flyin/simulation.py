from .drone import Drone
import heapq
from .hub import Hub
from .conect import Connection
from typing import Union, Optional


class Simulation:
    """Class dedicated to managing the simulation algorithm.

    Attributes:
        hubs: The locations where drones can be.
        connections: The paths connecting the hubs.
        nb_drones: The number of drones in the simulation.
        start_hub: The starting point of the path.
        end_hub: The destination of the path.
    """

    def __init__(
        self,
        hubs: list[Hub],
        connections: list[Connection],
        nb_drones: int,
        start_hub: Hub,
        end_hub: Hub
    ) -> None:
        self.hubs: list[Hub] = hubs
        self.connections: list[Connection] = connections
        self.nb_drones: int = nb_drones
        self.start_hub: Hub = start_hub
        self.end_hub: Hub = end_hub
        self.drone_list: list[Drone] = []
        self.history: list[list[tuple[str, Hub, Hub]]] = []

    def create_drones(self) -> None:
        """Create the drones and place them at the starting hub.

        The number of drones created is determined by nb_drones.
        Each drone is also added to the simulation's drone list.
        """
        for i in range(self.nb_drones):
            name_drone: str = f"\nD{i}"
            new_drone: Drone = Drone(name_drone, self.start_hub)
            self.start_hub.add_drone(new_drone)
            self.drone_list.append(new_drone)

    def get_neighbors(self, hub: Hub) -> list[Hub]:
        """Find all hubs directly connected to a given hub.

        Args:
            hub: The hub whose neighbors are being searched.

        Returns:
            A list containing all hubs directly connected to the given hub.
        """
        neighbors: list[Hub] = []

        for conn in self.connections:
            if conn.hub1 == hub:
                neighbors.append(conn.hub2)
            elif conn.hub2 == hub:
                neighbors.append(conn.hub1)

        return neighbors

    def dijkstra(self) -> list[Hub]:
        """Find the best path from the starting hub to the destination.

        The algorithm uses Dijkstra's algorithm to find the path with
        the lowest cost. Restricted zones have a higher cost, while
        priority zones are preferred when paths have the same cost.

        Returns:
            A list of hubs representing the best path from the starting
            hub to the destination. Returns an empty list if no path
            exists.
        """
        distances: dict[Hub, tuple[Union[int, float], int]] = {
            hub: (float("inf"), 0)
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
            (
                current_dis,
                current_priority,
                _,
                current_hub
            ) = heapq.heappop(queue)

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

        current: Optional[Hub] = self.end_hub

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
        print("PATH:", [hub.name for hub in path])

        return path

    def check_connect(
        self,
        hub1: Hub,
        hub2: Hub
    ) -> Optional[Connection]:
        """Check whether there is a direct connection between two hubs.

        Args:
            hub1: The first hub.
            hub2: The second hub.

        Returns:
            The connection between the two hubs if one exists.
            Otherwise, returns None.
        """
        for connect in self.connections:
            if (
                (connect.hub1 == hub1 and connect.hub2 == hub2)
                or
                (connect.hub1 == hub2 and connect.hub2 == hub1)
            ):
                return connect

        return None

    def move_drone(
        self,
        drone: Drone,
        next_hub: Hub
    ) -> bool:
        """Try to move a drone to the next hub.

        The move is only performed if there is a connection and
        both the destination hub and the connection have available
        capacity.

        Args:
            drone: The drone to move.
            next_hub: The hub where the drone wants to go.

        Returns:
            True if the drone was successfully moved, otherwise False.
        """
        current: Hub = drone.location
        connection: Optional[Connection] = self.check_connect(
            current,
            next_hub
        )

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

    """Algoritmo do pc em casa:"""
    def next_hop_dijkstra(
        self,
        source: Hub,
        avoid: Optional[Hub] = None
    ) -> Optional[Hub]:
        """Find the next hub using Dijkstra's algorithm.

        The algorithm searches for a path from the source hub to the
        destination while optionally avoiding a specific hub.

        This method is used as a fallback when the preferred next hub
        is temporarily full or blocked, allowing the drone to take
        an alternative route.

        Args:
            source: The hub where the drone currently is.
            avoid: A hub that should be avoided, if provided.

        Returns:
            The first hub after the source in the calculated path.
            Returns None if no valid path exists.
        """
        distances: dict[Hub, tuple[Union[int, float], int]] = {
            hub: (float("inf"), 0)
            for hub in self.hubs
        }

        distances[source] = (0, 0)

        parent: dict[Hub, Optional[Hub]] = {
            source: None
        }

        counter: int = 0

        queue: list[tuple[Union[int, float], int, int, Hub]] = [
            (0, 0, counter, source)
        ]

        while queue:
            (
                current_dis,
                current_priority,
                _,
                current_hub
            ) = heapq.heappop(queue)

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

                if avoid is not None and neighbor == avoid:
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

        if self.end_hub not in parent:
            return None

        path: list[Hub] = []

        current: Optional[Hub] = self.end_hub

        while current is not None:
            path.append(current)
            current = parent[current]

        path.reverse()

        if len(path) < 2 or path[0] != source:
            return None

        return path[1]

    def get_preferred_next_hub(
        self,
        drone: Drone,
        path: list[Hub]
    ) -> Optional[Hub]:
        """Determine the preferred next hub for a drone.

        If the drone is still on the main path, the next hub in that
        path is returned. If the drone has already taken a different
        route, a new path is calculated from its current location.

        Args:
            drone: The drone whose next destination is being determined.
            path: The main path from the start to the destination.

        Returns:
            The next hub the drone should move to, or None if there
            is no next hub.
        """
        if drone.location in path:
            index: int = path.index(drone.location)

            if index == len(path) - 1:
                return None

            return path[index + 1]

        return self.next_hop_dijkstra(drone.location)

    def hub_reserved_space(
        self,
        hub: Hub
    ) -> Union[int, float]:
        """Calculate the actual available space in a hub.

        The available space is calculated by subtracting the drones
        already inside the hub and the drones currently in transit
        toward it from the hub's maximum capacity.

        Returns:
            The number of available spaces in the hub.
        """
        reserved: int = sum(
            1
            for d in self.drone_list
            if d.in_transit and d.target == hub
        )

        return hub.max_drones - len(hub.drones) - reserved

    def print_capacity_info(self) -> None:
        """Print the current capacity of hubs and connections.

        This method is used by the --capacity-info flag and is called
        once per simulation turn.
        """
        for hub in self.hubs:
            cap = hub.max_drones
            cap_str: str = (
                "inf"
                if cap == float("inf")
                else str(int(cap))
            )

            print(
                f"Zone {hub.name}: "
                f"{len(hub.drones)}/{cap_str} drones"
            )

        for conn in self.connections:
            cap = conn.max_link_capacity
            cap_str: str = (
                "inf"
                if cap == float("inf")
                else str(int(cap))
            )

            print(
                f"Connection {conn.hub1.name}-{conn.hub2.name}: "
                f"{len(conn.drones)}/{cap_str} capacity used"
            )

    def simulate(self, capacity_info: bool = False) -> None:
        """Run the drone simulation turn by turn.

        The simulation calculates the main path, moves drones while
        respecting hub and connection capacities, handles restricted
        zones, and finds alternative routes when necessary.

        Args:
            capacity_info: If True, print hub and connection capacity
                information after each turn.
        """
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

                    if drone.target is not None:
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
                tuple[Drone, Hub, Connection]
            ] = []

            for drone in self.drone_list:

                if drone in already_acted:
                    continue

                if drone.location == self.end_hub:
                    continue

                if drone.in_transit:
                    continue

                next_hub: Optional[Hub] = (
                    self.get_preferred_next_hub(
                        drone,
                        path
                    )
                )

                if next_hub is None:
                    continue

                connection: Optional[Connection] = (
                    self.check_connect(
                        drone.location,
                        next_hub
                    )
                )

                if connection is None:
                    continue

                moves.append(
                    (
                        drone,
                        next_hub,
                        connection
                    )
                )

            for drone, next_hub, connection in moves:

                chosen_hub: Hub = next_hub
                chosen_connection: Connection = connection

                primary_blocked: bool = (
                    chosen_hub.is_blocked()
                    or chosen_connection.is_full_connect()
                    or self.hub_reserved_space(chosen_hub) <= 0
                )

                if primary_blocked:

                    alt_hub: Optional[Hub] = (
                        self.next_hop_dijkstra(
                            drone.location,
                            avoid=chosen_hub
                        )
                    )

                    if alt_hub is None:
                        continue

                    alt_connection: Optional[Connection] = (
                        self.check_connect(
                            drone.location,
                            alt_hub
                        )
                    )

                    if alt_connection is None:
                        continue

                    alt_blocked: bool = (
                        alt_hub.is_blocked()
                        or alt_connection.is_full_connect()
                        or self.hub_reserved_space(alt_hub) <= 0
                    )

                    if alt_blocked:
                        continue

                    chosen_hub = alt_hub
                    chosen_connection = alt_connection

                start_hub: Hub = drone.location

                chosen_connection.add_drone(drone)
                drone.location.remove_drone(drone)

                if chosen_hub.zone == "restricted":

                    drone.in_transit = True
                    drone.target = chosen_hub
                    drone.remaining_turns = 1
                    drone.connection = chosen_connection

                    turn_output.append(
                        f"{drone.id_name}-"
                        f"{start_hub.name}-{chosen_hub.name}"
                    )

                else:

                    chosen_hub.add_drone(drone)
                    drone.location = chosen_hub
                    chosen_connection.remove_drone(drone)

                    turn_output.append(
                        f"{drone.id_name}-{chosen_hub.name}"
                    )

                turn_moves.append(
                    (
                        drone.id_name,
                        start_hub,
                        chosen_hub
                    )
                )

            if not turn_output and not any(
                d.in_transit
                for d in self.drone_list
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
