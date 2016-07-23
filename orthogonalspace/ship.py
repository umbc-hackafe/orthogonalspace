from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from orthogonalspace.body import Body, Vector

from orthogonalspace import utils

Base = declarative_base()

class Ship(Body, Base):
    __tablename__ = 'ship'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    hp = Column(Integer)
    energy = Column(Integer)
    universe = Column(Integer, ForeignKey('universe.id'))

    @staticmethod
    def from_lobbyship(lobby_ship, universe):
        return Ship(lobby_ship.session, universe, lobby_ship.name)

    def __init__(self, session, universe, name="Ship"):
        super().__init__(universe)

        self.id = 1

        self.energy = 0
        self.hp = 0
        self.name = name

        self.session = session

        utils.register_patterns(self, session, 'space.orthogonal.ship.ship{.id}.')

    def send_update(self):
        utils.publish_prefix(self, self.session, 'updated', self)

    @property
    def heading(self):
        return 0.0

    @utils.register('add_thrust')
    @utils.serial
    async def add_thrust(self, x, y, z):
        self.force += Vector(x, y, z)
        self.send_update()
        return self.force

    def __getstate__(self):
        return utils.update(utils.include_attrs(self, 'id', 'energy', 'hp', 'name', 'heading'), super().__getstate__())
