from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import relationship
from orthogonalspace.body import Body, Vector
import logging

from orthogonalspace import utils

#: The proportion of energy converted to heat when it is generated or consumed
HEAT_WASTE_RATE = .05

LOG = logging.getLogger("ship")

Base = declarative_base()

class Component(Body):
    def __init__(self, ship):
        super().__init__(ship.universe)
        self.ship = ship

        self.energy = 0

        self.stored = 0
        self.max_storage = 0

        self._in_pre_tick = False
        self._in_post_tick = False

    def request_energy(self, amount, proportional=False):
        """
        Request an amount of energy from the ship.

        :param amount: The amount of energy to request
        :param proportional: Whether or not it is acceptable to grant less than the requested amount
        :return: None
        """
        assert self._in_pre_tick

        self.ship.request_energy(self, amount, proportional)

    def generate_energy(self, amount):
        """
        Generate an amount of energy from this component.
        :param amount: The amount of energy generated
        :return: None
        """
        assert self._in_pre_tick


        self.ship._generated_energy += amount

    def store_energy(self, amount):
        """
        Attempt to store an amount of energy in this component.

        :param amount: The amount of energy to be stored
        :return: The amount of energy that was able to be stored
        """

        margin = self.max_storage - self.stored

        store = min(margin, amount)
        self.stored += store
        return store

    def use_energy(self, amount):
        assert not self._in_pre_tick

        if amount > self.energy:
            return False

        self.energy -= amount

        return True

    def run_pre_tick(self, dt):
        self._in_pre_tick = True

        self.energy = 0

        try:
            self.pre_tick(dt)
        finally:
            self._in_pre_tick = False

    def pre_tick(self, dt):
        pass

    def do_tick(self, dt):
        pass

    def run_post_tick(self, dt):
        self._in_post_tick = True

        try:
            self.post_tick(dt)
        finally:
            self._in_post_tick = False

    def post_tick(self, dt):
        pass


class Generator(Component):
    def __init__(self, base, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.base = base

    def pre_tick(self, dt):
        self.generate_energy(self.base * dt)


class Battery(Component):
    def __init__(self, capacity, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.max_storage = capacity
        self.stored_energy = 0


class Thruster(Component):
    def __init__(self, force, usage, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.throttle_force = force
        self.usage = usage

        self._throttle = 0

    @property
    def throttle(self):
        return self._throttle

    @throttle.setter
    def throttle(self, value):
        self._throttle = min(1, max(-1, value))

    def pre_tick(self, dt):
        self.request_energy(abs(self.throttle) * self.usage * dt, True)

    def post_tick(self, dt):
        self.ship.force += self.ship.heading * self.throttle * self.throttle_force * (self.energy / self.usage) * dt
        self.use_energy(self.energy)


class EnergySink(Component):
    def __init__(self, base, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.base = base

    def pre_tick(self, dt):
        self.request_energy(self.base * dt)

    def post_tick(self, dt):
        self.use_energy(self.base * dt)


class Radiator(Component):
    def __init__(self, base, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.base = base

    def post_tick(self, dt):
        self.ship.heat -= dt * self.base


class Ship(Body, Base):
    PREFIX = 'space.orthogonal.ship.ship{.id}.'
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

        self.heat = 0

        self.session = session

        self.heading = Vector(1, 0, 0).normalize()

        # FIXME temporary
        self.components = [
            Generator(1000, self),
            Battery(50000, self),
            #EnergySink(1000, self),
            Radiator(750, self),
            Thruster(100, 1500, self),
        ]

        self._energy_requests = []
        self._energy_requests_prop = []
        self._generated_energy = 0
        self.stored_energy = 0

        utils.register_patterns(self, session, 'space.orthogonal.ship.ship{.id}.')

    def request_energy(self, component, amount, proportional=False):
        if proportional:
            LOG.info("PREQ %d from %s", amount, component)
            self._energy_requests_prop.append((amount, component))
        else:
            LOG.info("REQ %d from %s", amount, component)
            self._energy_requests.append((amount, component))

    def do_tick(self, dt):
        # Reset all energy counters
        self._energy_requests = []
        self._energy_requests_prop = []
        self._generated_energy = 0

        # We'll keep track of how much stored energy there is separately
        stored_energy = 0

        # Run pre-tick
        # This is where components generate and request energy
        for component in self.components:
            component.run_pre_tick(dt)
            stored_energy += component.stored
            component.stored = 0

        # Total amount of proportional requests
        # If less than this amonut is available, each component will get the same proportion of what it requested
        prop_sum = sum((amount for amount, component in self._energy_requests_prop))

        LOG.info(
            "[ENERGY] GEN: %0.2d, REQ: %0.2d, PREQ: %0.2d, STO: %0.2d",
            self._generated_energy,
            sum((amt for amt, _ in self._energy_requests)),
            prop_sum,
            stored_energy,
        )

        # Add waste heat for all the generated energy
        self.heat += self._generated_energy * HEAT_WASTE_RATE

        # Components can use stored energy as well as energy
        # generated this tick
        avail_energy = stored_energy + self._generated_energy

        # Sort requests by largest-first, so ideally the most important stuff gets run first
        # Maybe this should be smallest-first? no idea
        self._energy_requests.sort(reverse=True)

        for amount, component in self._energy_requests:
            if amount < avail_energy:
                component.energy += amount
                avail_energy -= amount
                self.heat += HEAT_WASTE_RATE * amount
            # If sorting changes to smallest-first, we can break otherwise

        if prop_sum:
            if prop_sum <= avail_energy:
                # Enough energy for everyone! Yay
                proportion = 1
                avail_energy -= prop_sum
            else:
                # Not quite enough, portion it out
                proportion = (avail_energy / prop_sum)
                avail_energy = 0

            self.heat += prop_sum * proportion * HEAT_WASTE_RATE

            for amount, component in self._energy_requests_prop:
                component.energy += amount * proportion

        self.stored_energy = 0

        for component in self.components:
            # Store any excess energy wherever possible. The exact component it goes into
            # doesn't really matter because we take it all out next tick anyway
            if avail_energy and component.stored < component.max_storage:
                store_amt = min(component.max_storage - component.stored, avail_energy)

                component.stored += store_amt
                avail_energy -= store_amt
                self.stored_energy += store_amt

            component.run_post_tick(dt)

        # Convert all unused energy into heat
        self.heat += avail_energy

        # Heat can't be negative
        self.heat = max(self.heat, 0)

        return False

    def consume_energy(self, amt):
        avail = min(self.energy, amt)
        self.energy -= avail
        return avail

    def send_update(self):
        utils.publish_prefix(self, self.session, 'updated', self)

    @property
    def thrust(self):
        if not hasattr(self, 'components'): return 0
        thrusts = [c.thrust for c in self.components if isinstance(c, Thruster)]
        return sum(thrusts) / len(thrusts) if thrusts else 0

    @utils.register('set_throttle')
    @utils.serial
    async def set_throttle(self, n):
        for thruster in (c for c in self.components if isinstance(c, Thruster)):
            thruster.throttle = n
        self.throttle = n
        return self.throttle

    def __getstate__(self):
        return utils.update(utils.include_attrs(self, 'id', 'energy', 'hp', 'name', 'heading', 'throttle', 'heat', 'stored_energy'), super().__getstate__())
