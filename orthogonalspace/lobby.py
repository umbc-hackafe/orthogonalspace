import asyncio

class Lobby:
    def __init__(self):
        self.universes = []
        self.ships = []

    @asyncio.coroutine
    def list_universes(self):
        return self.universes

    @asyncio.coroutine
    def list_ships(self):
        return self.ships
