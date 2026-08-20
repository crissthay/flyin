from flyin.hub import Hub
from typing import Optional
from flyin.conect import Connection


class Drone:
    def __init__(self, id_name: str, location: Hub) -> None:
        self.id_name: str = id_name
        self.location: Hub = location
        self.in_transit: bool = False
        self.target: Optional[Hub] = None
        self.remaining_turns: int = 0
        self.connection: Optional[Connection] = None
