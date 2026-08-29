from typing import Union, TYPE_CHECKING
from .hub import Hub
if TYPE_CHECKING:
    from .drone import Drone


class Connection:
    """ Claase dedicada ao meus caminhos para
    os hubs

    Attributes:
        hub1: Um ponto de partida
        hub2: outro ponto
        (hub1 + hub2 e apenas uma representacao
        de um caminho)
        max_link_capacity: Capacidade de caminho
    """
    def __init__(
            self,
            hub1: Hub,
            hub2: Hub,
            max_link_capacity: Union[int, float] = float("inf")
            ) -> None:
        self.hub1: Hub = hub1
        self.hub2: Hub = hub2
        self.max_link_capacity: Union[int, float] = max_link_capacity
        self.drones: list["Drone"] = []

    def is_full_connect(self) -> bool:
        """Check whether the connection has reached its capacity.

        Returns:
            True if the number of drones is equal to or greater than
            the maximum capacity, otherwise False.
        """
        return len(self.drones) >= self.max_link_capacity

    def add_drone(self, drone) -> None:
        """Add a drone to the connection if there is available capacity.

        Args:
            drone: The drone to add to the connection.
        """
        if not self.is_full_connect():
            self.drones.append(drone)

    def remove_drone(self, drone) -> None:
        """Remove a drone from the connection.

        Args:
            drone: The drone to remove from the connection.
        """
        if drone in self.drones:
            self.drones.remove(drone)
