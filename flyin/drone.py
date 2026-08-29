from .hub import Hub
from typing import Optional
from .connect import Connection


class Drone:
    """Class representing a drone and its current state.

    Attributes:
        id_name: The name or identifier of the drone.
        location: The drone's current location.
        in_transit: Indicates whether the drone is currently traveling.
        target: The hub where the drone is heading.
        remaining_turns: The number of turns remaining in the trip.
        connection: The connection the drone is currently using.
    """
    def __init__(self, id_name: str, location: Hub) -> None:
        self.id_name: str = id_name
        self.location: Hub = location
        self.in_transit: bool = False
        self.target: Optional[Hub] = None
        self.remaining_turns: int = 0
        self.connection: Optional[Connection] = None
