from autobahn import wamp

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
    EVENT_NAME_UPDATED = u'space.orthogonal.lobby.ship.event.name_updated'
    EVENT_POSITION_FILLED = u'space.orthogonal.lobby.ship.event.position_filled'
    EVENT_POSITION_VACATED = u'space.orthogonal.lobby.ship.event.position_vacated'

    @wamp.register(u'space.orthogonal.lobby.ship.enlist')
    async def _enlist(ship, user, position):
        await ship.enlist(user, position)

    @wamp.register(u'space.orthogonal.lobby.ship.leave')
    async def _leave(ship ,user, position):
        await ship.leave(user, position)

    @wamp.register(u'space.orthogonal.lobby.ship.set_name')
    async def _set_name(ship, name):
        await ship.set_name(name)

    def __init__(self, session, name="Shippy McShipFace", roles=None):
        self.name = name
        self.officers = {}
        if roles is None:
            roles = ROLES
        self.roles = roles
        self.session = session

    async def set_name(self, name):
        if isinstance(name, str):
            self.name = name
            self.session.publish(LobbyShip.EVENT_NAME_UPDATED, self.name)
        else:
            raise ValueError("`name` must be str")

    async def enlist(self, user, position):
        if position not in self.roles:
            raise ValueError("Role '" + position + "' does not exist")

        if position in self.officers and self.officers[position]:
            raise ValueError("Role '" + position + "' is already taken")

        self.officers[position] = user
        self.session.publish(LobbyShip.EVENT_POSITION_FILLED, position, user)

    async def leave(self, user, position):
        if position not in self.roles:
            raise ValueError("Role '" + position + "' does not exist")

        if position not in self.officers or self.officers[position] != user:
            raise ValueError("User is not enlisted in '" + position + "'")

        del self.officers[position]
        self.session.publish(LobbyShip.EVENT_POSITION_VACATED, position)

    @wamp.register(u'space.orthogonal.lobby.ship.list_officers')
    async def list_officers(self):
        return self.officers


class Lobby:
    EVENT_SHIPS_UPDATED = u'space.orthogonal.lobby.event.ships_updated'

    def __init__(self, session):
        self.universes = []
        self.ships = []
        self.session = session

    @wamp.register(u'space.orthogonal.lobby.list_universes')
    async def list_universes(self):
        return self.universes

    @wamp.register(u'space.orthogonal.lobby.list_ships')
    async def list_ships(self):
        return self.ships

    @wamp.register(u'space.orthogonal.lobby.ship.create')
    async def create_ship(self):
        ship = LobbyShip(self.session)
        self.ships.append(ship)
        self.session.publish(Lobby.EVENT_SHIPS_UPDATED, self.ships)

    @wamp.register(u'space.orthogonal.lobby.ship.destroy')
    async def destroy_ship(self, ship):
        if ship in self.ships:
            self.ships.remove(ship)
            self.session.publish(Lobby.EVENT_SHIPS_UPDATED, self.ships)
        else:
            raise ValueError("Ship does not exist")
