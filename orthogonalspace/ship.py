import ode

class Ship(ode.Body):
    def __init__(self, name="Ship"):
        self.energy = 0
        self.hp = 0
        self.name = name
