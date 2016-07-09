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
    max_id = 0

    class _RPC(orthogonalspace.utils.ObjectMapper):
        def __init__(self):
            super().__init__()

        @wamp.register(u'space.orthogonal.lobby.ship.enlist')
        @orthogonalspace.utils.serial
        async def _enlist(self, ship, user, position):
            await self.canon(ship).enlist(user, position)

        @wamp.register(u'space.orthogonal.lobby.ship.leave')
        @orthogonalspace.utils.serial
        async def _leave(self, ship, user, position):
            await self.canon(ship).leave(user, position)

        @wamp.register(u'space.orthogonal.lobby.ship.set_name')
        @orthogonalspace.utils.serial
        async def _set_name(self, ship, name):
            await self.canon(ship).set_name(name)

        @wamp.register(u'space.orthogonal.lobby.ship.updated')
        @orthogonalspace.utils.serial
        async def _name_updated(self, ship, name):
            self.canon(ship).set_name(name)
            LOG.info("Name changed to {}".format(name))

        @wamp.register(u'space.orthogonal.lobby.ship.list_officers')
        @orthogonalspace.utils.serial
        async def list_officers(self, ship):
            return self.canon(ship).officers

    RPC = _RPC()

    def __init__(self, session, name="Shippy McShipFace", roles=None):
        self.name = name
        self.officers = {}
        if roles is None:
            roles = ROLES
        self.roles = roles
        self.session = session

        LobbyShip.max_id += 1
        self.id = LobbyShip.max_id

        self.RPC.register(self)

    def __getstate__(self):
        return orthogonalspace.utils.filter_attrs(self, 'session', 'max_id')

    async def set_name(self, name):
        if isinstance(name, str):
            self.name = name
            self.session.publish(u'space.orthogonal.lobby.ship.event.updated', self.name)
        else:
            raise ValueError("`name` must be str")

    async def enlist(self, user, position):
        if position not in self.roles:
            raise ValueError("Role '" + position + "' does not exist")

        if position in self.officers and self.officers[position]:
            raise ValueError("Role '" + position + "' is already taken")

        self.officers[position] = user
        self.session.publish(u'space.orthogonal.lobby.ship.event.role_filled', position, user)

    async def leave(self, user, position):
        if position not in self.roles:
            raise ValueError("Role '" + position + "' does not exist")

        if position not in self.officers or self.officers[position] != user:
            raise ValueError("User is not enlisted in '" + position + "'")

        del self.officers[position]
        self.session.publish(u'space.orthogonal.lobby.ship.event.role_vacated', position)


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
