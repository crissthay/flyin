from typing import Optional


class Hub():
    def __init__(
                self,
                name: str,
                x: int,
                y: int,
                color: Optional[str] = None,
                zone: str = "normal",
                max_drones: int = 1
                ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.color = color
        self.zone = zone
        self.max_drones = max_drones
        self.drones = []

    def __repr__(self):
        return f"Hub({self.name}, {self.x}, {self.y})"

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
