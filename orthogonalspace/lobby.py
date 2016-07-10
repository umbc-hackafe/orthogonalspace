import orthogonalspace.utils
from orthogonalspace import serializer
from autobahn import wamp
import logging

LOG = logging.getLogger('orthogonalspace.lobby')

ROLE_NAMES = {
    "CAPTAIN": "Captain",
    "COMMS": "Comms Officer",
    "ENGINEER": "Engineer",
    "HELM": "Helmsman",
    "SCIENCE": "Scientist",
    "WEAPONS": "Weapons Officer",
}

ROLES = list(ROLE_NAMES.keys())


class LobbyShip:
    PREFIX = 'space.orthogonal.lobby.ship.ship{.id}.'
    max_id = 0

    def __init__(self, session, name="Shippy McShipFace", roles=None):
        self.name = name
        self.officers = {}
        if roles is None:
            roles = ROLES
        self.roles = roles
        self.session = session

        LobbyShip.max_id += 1
        self.id = LobbyShip.max_id

        orthogonalspace.utils.register_patterns(self, session, 'space.orthogonal.lobby.ship.ship{.id}.')

        session.publish('space.orthogonal.lobby.ship.new', self)

    def __getstate__(self):
        return orthogonalspace.utils.filter_attrs(self, 'session', 'max_id')

    def send_update(self):
        orthogonalspace.utils.publish_prefix(self, self.session, 'updated', self)

    @orthogonalspace.utils.register('set_name')
    @orthogonalspace.utils.serial
    async def set_name(self, name):
        if isinstance(name, str):
            self.name = name
            self.send_update()
            return self
        else:
            raise ValueError("`name` must be str")

    @orthogonalspace.utils.register('set_roles')
    @orthogonalspace.utils.serial
    async def enlist(self, user, positions):
        for position in positions:
            assert position in self.roles

        self.officers[user] = positions
        self.send_update()

    @orthogonalspace.utils.register('leave')
    async def leave(self, user, position):
        if position not in self.roles:
            raise ValueError("Role '" + position + "' does not exist")

        if position not in self.officers or self.officers[position] != user:
            raise ValueError("User is not enlisted in '" + position + "'")

        del self.officers[position]
        self.send_update()

class Lobby:
    EVENT_SHIPS_UPDATED = u'space.orthogonal.lobby.event.ships_updated'

    def __init__(self, session):
        self.universes = []
        self.ships = []
        self.session = session

    @wamp.register(u'space.orthogonal.lobby.list_universes')
    @orthogonalspace.utils.serial
    async def list_universes(self):
        return self.universes

    @wamp.register(u'space.orthogonal.lobby.list_ships')
    @orthogonalspace.utils.serial
    async def list_ships(self):
        return self.ships

    @wamp.register(u'space.orthogonal.lobby.ship.create')
    @orthogonalspace.utils.serial
    async def create_ship(self):
        ship = LobbyShip(self.session)

        self.ships.append(ship)
        self.session.publish(Lobby.EVENT_SHIPS_UPDATED, self.ships)
        return ship

    @wamp.register(u'space.orthogonal.lobby.ship.destroy')
    @orthogonalspace.utils.serial
    async def destroy_ship(self, ship):
        if ship in self.ships:
            self.ships.remove(ship)
            self.session.publish(Lobby.EVENT_SHIPS_UPDATED, self.ships)
        else:
            raise ValueError("Ship does not exist")
