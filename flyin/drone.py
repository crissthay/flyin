class Drone:
    def __init__(self, id_name: str, location) -> None:
        self.id_name: str = id_name
        self.location = location
        self.in_transit = False
        self.target = None
        self.remaining_turns = 0
        self.connection = None
        #self.indice = indice
