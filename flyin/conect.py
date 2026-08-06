from flyin.hub import Hub

class Connection:
    def __init__(
            self,
            hub1: Hub,
            hub2: Hub,
            max_link_capacity: int = float("inf")) -> None:
        self.hub1 = hub1
        self.hub2 = hub2
        self.max_link_capacity = max_link_capacity
        self.drones = []
        
    def is_full_connect(self) -> bool:
        return len(self.drones) >= self.max_link_capacity
    
    def add_drone(self, drone):
        if not self.is_full_connect():
            self.drones.append(drone)           

    def remove_drone(self, drone):
        if drone in self.drones:
            self.drones.remove(drone)


    def __repr__(self):
        return f"Connection({self.hub1.name} -> {self.hub2.name})"    
