from typing import Union, TYPE_CHECKING
from .hub import Hub
if TYPE_CHECKING:
    from .drone import Drone


class Connection:
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
        return len(self.drones) >= self.max_link_capacity

    def add_drone(self, drone) -> None:
        if not self.is_full_connect():
            self.drones.append(drone)

    def remove_drone(self, drone) -> None:
        if drone in self.drones:
            self.drones.remove(drone)
