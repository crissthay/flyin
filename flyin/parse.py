import sys
from typing import Optional, Union
from .hub import Hub
from .connect import Connection


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
    """Parses and stores the map configuration.

    Attributes:
        file: Path to the map file.
        lines_list: List containing the lines read from the map file.
        nb_drones: Number of drones.
        hubs: List of hubs in the map.
        connections: List of connections between hubs.
        start_hub: Starting hub of the map.
        end_hub: Destination hub of the map.
        _seen_connections: Set of connections that have already been processed.
    """

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
        """Opens the map file and reads its contents.

        Returns:
            A list containing the lines from the map file.

        Raises:
            FileNotFoundError: If the map file cannot be found.
        """
        try:
            with open(self.file, encoding="utf-8") as file:
                for line in file:
                    self.lines_list.append(line.strip())
        except FileNotFoundError:
            print("ERROR - File not found")
            sys.exit(1)
        return self.lines_list

    def check_line(self) -> list[str]:
        """Filters the map lines by removing empty lines and comments.

        Returns:
            A list containing only valid, non-empty lines.
        """
        val_lines: list[str] = []
        for lines in self.lines_list:
            if lines == "" or lines.startswith("#"):
                continue
            val_lines.append(lines)
        return val_lines

    def metadata(self, line: str) -> dict:
        """Parses and validates the metadata of a hub.

        Args:
            line: A line from the map file.

        Returns:
            A dictionary containing the hub metadata.

        Raises:
            ValueError: If a metadata value has an invalid format.
        """
        zone: str = "normal"
        color: Optional[str] = None
        max_drones: int = 1

        splited_meta: list[str] = line.strip().split()
        meta: list[str] = splited_meta[4:]

        for item in meta:
            item = item.strip("[]")
            if "=" not in item:
                print(f"ERROR - Invalid metadata format: '{item}'")
                sys.exit(1)

            parts = item.split("=")
            if len(parts) != 2:
                print(f"ERROR - Invalid metadata format: '{item}'")
                sys.exit(1)
            key, value = parts

            if key == "zone":
                if value in zone_valid:
                    zone = value
                else:
                    print(f"ERROR - Invalid zone: '{value}'")
                    sys.exit(1)
            elif key == "color":
                if value in color_valid:
                    color = value
                else:
                    print(f"ERROR - Invalid color: '{value}'")
                    sys.exit(1)
            elif key == "max_drones":
                try:
                    max_drones = int(value)
                except ValueError:
                    print("ERROR - max_drones must be an integer")
                    sys.exit(1)
                if max_drones <= 0:
                    print("ERROR - max_drones must be a positive integer")
                    sys.exit(1)
            else:
                print(f"ERROR - Unknown metadata key: '{key}'")
                sys.exit(1)

        return {"zone": zone, "color": color, "max_drones": max_drones}

    def meta_connect(self, line: str) -> dict[str, Union[int, float]]:
        """Parses and validates the metadata of a connection.

        Args:
            line: A line from the map file.

        Returns:
            A dictionary containing the connection metadata.

        Raises:
            ValueError: If a metadata value has an invalid format.
        """
        capacity: Union[int, float] = float("inf")
        splited_meta: list[str] = line.strip().split()
        meta: list[str] = splited_meta[2:]

        for item in meta:
            item = item.strip("[]")
            if "=" not in item:
                print(f"ERROR - Invalid metadata format: '{item}'")
                sys.exit(1)

            parts = item.split("=")
            if len(parts) != 2:
                print(f"ERROR - Invalid metadata format: '{item}'")
                sys.exit(1)
            key, value = parts

            if key == "max_link_capacity":
                try:
                    capacity = int(value)
                except ValueError:
                    print("ERROR - max_link_capacity must be an integer")
                    sys.exit(1)
                if capacity <= 0:
                    print(
                        "ERROR - max_link_capacity must be a positive integer"
                        )
                    sys.exit(1)
            else:
                print(f"ERROR - Unknown metadata key: '{key}'")
                sys.exit(1)

        return {"max_link_capacity": capacity}

    def parse_nb(self, line: str) -> None:
        """Parses and validates the number of drones.

        Args:
            line: A line from the map file.

        Raises:
            ValueError: If the number of drones is not
            an integer or is negative.
        """
        splited_nb: list[str] = line.strip().split()
        if len(splited_nb) != 2:
            print("ERROR - Miss args")
            sys.exit(1)

        try:
            self.nb_drones = int(splited_nb[1])
        except ValueError:
            print("ERROR - nb_drones must be an integer")
            sys.exit(1)

        if self.nb_drones <= 0:
            print("ERROR - nb_drones can't be negative")
            sys.exit(1)

    def parse_hub(self, line: str) -> Hub:
        """Parses a hub definition and adds the hub to the hub list.

        Args:
            line: A line from the map file.

        Returns:
            The newly created hub.

        Raises:
            ValueError: If the hub coordinates are not valid integers.
        """
        splited_se: list[str] = line.strip().split()
        if len(splited_se) < 4:
            print("ERROR - Miss args")
            sys.exit(1)

        name: str = splited_se[1]

        if self.find_hub(name) is not None:
            print(f"ERROR - Duplicate hub name: '{name}'")
            sys.exit(1)

        try:
            x = int(splited_se[2])
            y = int(splited_se[3])
        except ValueError:
            print("ERROR - Format must be (name, x, y)")
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
        """Searches for a hub by its name.

        Args:
            name: The name of the hub to search for.

        Returns:
            The matching hub if it exists, otherwise None.
        """
        for hub in self.hubs:
            if hub.name == name:
                return hub
        return None

    def parse_connect(self, line: str) -> None:
        """Parses a connection definition and adds it to the connection list.

        Args:
            line: A line from the map file.

        Raises:
            ValueError: If the connection format is invalid.
        """
        splited_connect: list[str] = line.strip().split()
        if len(splited_connect) < 2:
            print("ERROR - Miss args")
            sys.exit(1)

        try:
            hub1, hub2 = splited_connect[1].split("-")
        except ValueError:
            print("ERROR - Invalid connection format")
            sys.exit(1)

        hub1_obj = self.find_hub(hub1)
        hub2_obj = self.find_hub(hub2)
        if (hub1_obj is None or hub2_obj is None):
            print("ERROR - Hub not found")
            sys.exit(1)

        if hub1 == hub2:
            print(f"ERROR - Connection to itself: '{hub1}'")
            sys.exit(1)

        pair: tuple[str, str] = (min(hub1, hub2), max(hub1, hub2))
        if pair in self._seen_connections:
            print(f"ERROR - Duplicate connection: '{hub1}-{hub2}'")
            sys.exit(1)
        self._seen_connections.add(pair)

        info = self.meta_connect(line)
        connection = Connection(hub1_obj, hub2_obj, info["max_link_capacity"])
        self.connections.append(connection)

    def type_lines(self) -> None:
        """Processes the map lines according to their type.

        Identifies each line as a hub,
        connection, start hub, end hub,
        or drone count and calls the appropriate
        parsing method.
        """
        val_line: list[str] = self.check_line()

        for line in val_line:
            if line.startswith("start_hub:"):
                if self.start_hub is not None:
                    print("ERROR - Multiple start_hub defined")
                    sys.exit(1)
                self.start_hub = self.parse_hub(line)
                self.start_hub.max_drones = float("inf")
            elif line.startswith("end_hub:"):
                if self.end_hub is not None:
                    print("ERROR - Multiple end_hub defined")
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
                print(f"ERROR - Unknown line: '{line}'")
                sys.exit(1)

        if self.nb_drones is None:
            print("ERROR - nb_drones not defined")
            sys.exit(1)
        if self.start_hub is None:
            print("ERROR - No start_hub defined")
            sys.exit(1)
        if self.end_hub is None:
            print("ERROR - No end_hub defined")
            sys.exit(1)

        for line in val_line:
            if line.startswith("connection:"):
                self.parse_connect(line)
