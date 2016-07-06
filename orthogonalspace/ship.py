from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import relationship
import ode

Base = declarative_base()


class Ship(ode.Body, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    hp = Column(Integer)
    energy = Column(Integer)

    def __init__(self, universe, name="Ship"):
        super(Ship, self).__init__(universe)

        self.energy = 0
        self.hp = 0
        self.name = name

    def __getstate__(self):
        return {'id': self.id}