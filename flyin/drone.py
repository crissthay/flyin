class Drone:
    def __init__(self, id_name: str, location) -> None:
        self.id_name: str = id_name
        self.location = location
        #self.indice = indice
    def __repr__(self):
        return f"Name({self.id_name}, location{self.location})"