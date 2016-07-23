import ode

class Universe:
    def __init__(self, name, *args, **kwargs):
        self.world = ode.World()
        self.name = name
