from typing import Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .drone import Drone


class Hub():
    """Class representing a hub.

    Attributes:
        name: The name of the hub.
        x, y: The coordinates of the hub.
        color: The color of the hub.
        zone: The zone where the hub is located.
        max_drones: The maximum number of drones the hub can hold.
    """
    def __init__(
                self,
                name: str,
                x: int,
                y: int,
                color: Optional[str] = None,
                zone: str = "normal",
                max_drones: Union[int, float] = 1
                ) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.color: Optional[str] = color
        self.zone: str = zone
        self.max_drones: Union[int, float] = max_drones
        self.drones: list[Drone] = []

    def is_blocked(self) -> bool:
        """Check whether the hub is blocked.

        Returns:
            True if the hub's zone is blocked, otherwise False.
        """
        return self.zone == "blocked"

    def is_full(self) -> bool:
        """Check whether the hub is full.

        Returns:
            True if the number of drones is equal to or greater than
            the maximum capacity, otherwise False.
        """
        return len(self.drones) >= self.max_drones

    def add_drone(self, drone) -> None:
        """Add a drone to the hub if it is not blocked or full.

        Args:
            drone: The drone to add to the hub.
        """
        if not self.is_blocked() and not self.is_full():
            self.drones.append(drone)

    def remove_drone(self, drone) -> None:
        """Remove Hubs se acordo com o que passo no mapa.txt

        Args:
            drone: drone para remover se
            nao tiver block ou full
        """
        if drone in self.drones:
            self.drones.remove(drone)

    def movement_cost(self) -> int:
        """Return the movement cost of the hub.

        Returns:
            2 if the hub is in a restricted zone, otherwise 1.
        """
        if self.zone == "restricted":
            return 2
        return 1
