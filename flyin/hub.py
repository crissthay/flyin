from typing import Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .drone import Drone


class Hub():
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
        return self.zone == "blocked"

    def is_full(self) -> bool:
        return len(self.drones) >= self.max_drones

    def add_drone(self, drone):
        if not self.is_blocked() and not self.is_full():
            self.drones.append(drone)

    def remove_drone(self, drone):
        if drone in self.drones:
            self.drones.remove(drone)

    def movement_cost(self):
        if self.zone == "restricted":
            return 2
        return 1
