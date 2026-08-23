import sys
from typing import Optional, Union
from .hub import Hub
from .conect import Connection


zone_valid: list[str] = ["normal", "blocked", "restricted", "priority"]
color_valid: list[str] = [
    "green",
    "red",
    "blue",
    "yellow",
    "black",
    "purple",
    "gray",
    "pink",
    "cyan",
    "magenta",
    "brown",
    "orange",
    "lime",
    "gold",
    "silver",
    "rainbow",
]


class Parse:
    def __init__(self, file: str) -> None:
        self.file: str = file
        self.lines_list: list[str] = []
        self.nb_drones: Optional[int] = None
        self.hubs: list[Hub] = []
        self.connections: list[Connection] = []
        self.start_hub: Optional[Hub] = None
        self.end_hub: Optional[Hub] = None
        self._seen_connections: set[tuple[str, str]] = set()

    def open_read_file(self) -> list[str]:
        try:
            with open(self.file, encoding="utf-8") as file:
                for line in file:
                    self.lines_list.append(line.strip())
        except FileNotFoundError:
            print("ERRO - File not found")
            sys.exit(1)
        return self.lines_list

    def check_line(self) -> list[str]:
        val_lines: list[str] = []
        for lines in self.lines_list:
            if lines == "" or lines.startswith("#"):
                continue
            val_lines.append(lines)
        return val_lines

    def metadata(self, line: str) -> dict:
        zone: str = "normal"
        color: Optional[str] = None
        max_drones: int = 1

        splited_meta: list[str] = line.strip().split()
        meta: list[str] = splited_meta[4:]

        for item in meta:
            item = item.strip("[]")
            if "=" not in item:
                print(f"ERRO - Invalid metadata format: '{item}'")
                sys.exit(1)

            parts = item.split("=")
            if len(parts) != 2:
                print(f"ERRO - Invalid metadata format: '{item}'")
                sys.exit(1)
            key, value = parts

            if key == "zone":
                if value in zone_valid:
                    zone = value
                else:
                    print(f"ERRO - Invalid zone: '{value}'")
                    sys.exit(1)
            elif key == "color":
                if value in color_valid:
                    color = value
                else:
                    print(f"ERRO - Invalid color: '{value}'")
                    sys.exit(1)
            elif key == "max_drones":
                try:
                    max_drones = int(value)
                except ValueError:
                    print("ERRO - max_drones must be an integer")
                    sys.exit(1)
                if max_drones <= 0:
                    print("ERRO - max_drones must be a positive integer")
                    sys.exit(1)
            else:
                print(f"ERRO - Unknown metadata key: '{key}'")
                sys.exit(1)

        return {"zone": zone, "color": color, "max_drones": max_drones}

    def meta_connect(self, line: str) -> dict[str, Union[int, float]]:
        capacity: Union[int, float] = float("inf")
        splited_meta: list[str] = line.strip().split()
        meta: list[str] = splited_meta[2:]

        for item in meta:
            item = item.strip("[]")
            if "=" not in item:
                print(f"ERRO - Invalid metadata format: '{item}'")
                sys.exit(1)

            parts = item.split("=")
            if len(parts) != 2:
                print(f"ERRO - Invalid metadata format: '{item}'")
                sys.exit(1)
            key, value = parts

            if key == "max_link_capacity":
                try:
                    capacity = int(value)
                except ValueError:
                    print("ERRO - max_link_capacity must be an integer")
                    sys.exit(1)
                if capacity <= 0:
                    print(
                        "ERRO - max_link_capacity must be a positive integer"
                        )
                    sys.exit(1)
            else:
                print(f"ERRO - Unknown metadata key: '{key}'")
                sys.exit(1)

        return {"max_link_capacity": capacity}

    def parse_nb(self, line: str) -> None:
        splited_nb: list[str] = line.strip().split()
        if len(splited_nb) != 2:
            print("ERRO - Miss args")
            sys.exit(1)

        try:
            self.nb_drones = int(splited_nb[1])
        except ValueError:
            print("ERRO - nb_drones must be an integer")
            sys.exit(1)

        if self.nb_drones < 0:
            print("ERRO - nb_drones can't be negative")
            sys.exit(1)

    def parse_hub(self, line: str) -> Hub:
        splited_se: list[str] = line.strip().split()
        if len(splited_se) < 4:
            print("ERRO - Miss args")
            sys.exit(1)

        name: str = splited_se[1]

        if self.find_hub(name) is not None:
            print(f"ERRO - Duplicate hub name: '{name}'")
            sys.exit(1)

        try:
            x = int(splited_se[2])
            y = int(splited_se[3])
        except ValueError:
            print("ERRO - Format must be (name, x, y)")
            sys.exit(1)

        info = self.metadata(line)

        color = info["color"]
        zone = info["zone"]
        max_drones = info["max_drones"]

        hub = Hub(
            name,
            x,
            y,
            color if isinstance(color, (str, type(None))) else None,
            str(zone),
            int(max_drones) if isinstance(max_drones, int) else 1
        )
        self.hubs.append(hub)
        return hub

    def find_hub(self, name: str) -> Optional[Hub]:
        for hub in self.hubs:
            if hub.name == name:
                return hub
        return None

    def parse_connect(self, line: str) -> None:
        splited_connect: list[str] = line.strip().split()
        if len(splited_connect) < 2:
            print("ERRO - Miss args")
            sys.exit(1)

        try:
            hub1, hub2 = splited_connect[1].split("-")
        except ValueError:
            print("ERRO - Invalid connection format")
            sys.exit(1)

        hub1_obj = self.find_hub(hub1)
        hub2_obj = self.find_hub(hub2)
        if hub1_obj is None or hub2_obj is None:
            print("ERRO - Hub not found")
            sys.exit(1)

        if hub1 == hub2:
            print(f"ERRO - Connection to itself: '{hub1}'")
            sys.exit(1)

        pair: tuple[str, str] = (min(hub1, hub2), max(hub1, hub2))
        if pair in self._seen_connections:
            print(f"ERRO - Duplicate connection: '{hub1}-{hub2}'")
            sys.exit(1)
        self._seen_connections.add(pair)

        info = self.meta_connect(line)
        connection = Connection(hub1_obj, hub2_obj, info["max_link_capacity"])
        self.connections.append(connection)

    def type_lines(self) -> None:
        val_line: list[str] = self.check_line()

        for line in val_line:
            if line.startswith("start_hub:"):
                if self.start_hub is not None:
                    print("ERRO - Multiple start_hub defined")
                    sys.exit(1)
                self.start_hub = self.parse_hub(line)
                self.start_hub.max_drones = float("inf")
            elif line.startswith("end_hub:"):
                if self.end_hub is not None:
                    print("ERRO - Multiple end_hub defined")
                    sys.exit(1)
                self.end_hub = self.parse_hub(line)
                self.end_hub.max_drones = float("inf")
            elif line.startswith("hub:"):
                self.parse_hub(line)
            elif line.startswith("nb_drones:"):
                self.parse_nb(line)
            elif line.startswith("connection:"):
                continue
            else:
                print(f"ERRO - Unknown line: '{line}'")
                sys.exit(1)

        if self.nb_drones is None:
            print("ERRO - nb_drones not defined")
            sys.exit(1)
        if self.start_hub is None:
            print("ERRO - No start_hub defined")
            sys.exit(1)
        if self.end_hub is None:
            print("ERRO - No end_hub defined")
            sys.exit(1)

        for line in val_line:
            if line.startswith("connection:"):
                self.parse_connect(line)
