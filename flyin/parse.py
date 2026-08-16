import sys
from typing import Optional
from flyin.hub import Hub
from flyin.conect import Connection

zone_valid: list[str] = ['normal', 'blocked', 'restricted', 'priority']
color_valid: list[str] = [
    "green",
    "red",
    "blue",
    "yellow",
    "black",
    "purple",
    "gray",
    "pink",
    "rainbow"
]
class Parse:
    def __init__(self, file: str) -> None:
       self.file = file
       self.lines_list = []
       self.nb_drones = None
       self.hubs = []
       self.connections = []
       self.start_hub = None
       self.end_hub = None


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
            if lines == "":
                continue
            if lines.startswith("#"):
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
            key, value = item.split("=")
            if key == "zone":
                if value in zone_valid:
                    zone = value
                else:
                    print("ERRO - Invalid zone")
                    sys.exit(1)
            elif key == "color":
                if value in color_valid:
                    color = value
                else:
                    print("ERRO - Invalid color")
                    sys.exit(1)
            elif key == "max_drones":
                try:
                    max_drones = int(value)
                except ValueError:
                    print("ERRO - Max_drone must to be a integer")
                    sys.exit(1)
            else:
                print("ERRO - Metadata doesn't exist")
                sys.exit(1)
            
        return {
            "zone": zone,
            "color": color,
            "max_drones": max_drones
        }
    
    def meta_connect(self, line: str) -> dict:
        capacity = float("inf")

        splited_meta = line.strip().split()
        meta = splited_meta[2:]

        for item in meta:
            item = item.strip("[]")
            key, value = item.split("=")

            if key == "max_link_capacity":
                capacity = int(value)

        return {
            "max_link_capacity": capacity
        }
        
    def parse_nb(self, line: str):
        splited_nb: list[str] = line.strip().split()
        if len(splited_nb) != 2:
            print("ERRO - Miss args")
            sys.exit(1)

        int_ = splited_nb[1]

        try:
            self.nb_drones = int(int_)
        except ValueError:
            print(f"ERRO  - Must to be an interger number")
            sys.exit(1)

        if  self.nb_drones < 0:
            print("NB_drones can't be negative")
            sys.exit(1)

    def parse_hub(self, line):
        splited_se: list[str] = line.strip().split()
        if len(splited_se) < 4:
            print("ERRO - Miss args")
            sys.exit(1)
        name: str = splited_se[1]
        try:
            x = int(splited_se[2])
            y = int(splited_se[3])
        except ValueError:
            print("ERRO - Format must to bem (name, x, y)")
            sys.exit(1)
        info = self.metadata(line)
        hub = Hub(
            name,
            x,
            y,
            info["color"],
            info["zone"],
            info["max_drones"])
        self.hubs.append(hub)
        return hub
    
    def find_hub(self, name: str) -> None:
        for hub in self.hubs:
            if hub.name == name:
                return hub
        return None
        
    def parse_connect(self, line):
        splited_connect = line.strip().split()
        if len(splited_connect) < 2:
            print("ERRO - Miss args")
            sys.exit(1)
        try:
            hub1, hub2 = splited_connect[1].split("-")
            hub1_obj = self.find_hub(hub1)
            hub2_obj = self.find_hub(hub2)
            if hub1_obj is None or hub2_obj is None:
                print("ERRO - Hub not found")
                sys.exit(1)
        except ValueError:
            print("ERRO - Invalid connection format")
            sys.exit(1)
        info = self.meta_connect(line)
        connection = Connection(
            hub1_obj,
            hub2_obj,
            info["max_link_capacity"]
        )
        self.connections.append(connection)  


    def type_lines(self) -> None:
        val_line: list[str] = self.check_line()

        for line in val_line:
            if line.startswith("hub:"):
                self.parse_hub(line)

            elif line.startswith("start_hub:"):
                self.start_hub = self.parse_hub(line)
                self.start_hub.max_drones = float("inf")
            elif line.startswith("end_hub:"):
                self.end_hub = self.parse_hub(line)
                self.end_hub.max_drones = float("inf")
            elif line.startswith("nb_drones:"):
                self.parse_nb(line)
            elif line.startswith("connection:"):
                continue
            else:
                print("UNKNOW")
                sys.exit(1)

        for line in val_line:
            if line.startswith("connection:"):
                self.parse_connect(line)
