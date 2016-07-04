import ode

class Universe(ode.World):
    def __init__(self, name, *args, **kwargs):
        super(Universe, self).__init__(*args, **kwargs)
        self.name = name
