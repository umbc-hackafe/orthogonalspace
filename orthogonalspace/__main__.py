#!/usr/bin/env python3
import txaio
txaio.use_asyncio()
from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
import asyncio
import os

class OrthogonalSpaceComponent(ApplicationSession):
    @asyncio.coroutine
    def onJoin(self, details):
        def echo(msg):
            return str(msg[::-1])
        yield from self.register(echo, u'space.orthogonal.echo')

        while True:
            self.publish(u'space.orthogonal.heartbeat', 'Hi')
            yield from asyncio.sleep(1)

def main():
    runner = ApplicationRunner(
        os.environ.get("AUTOBAHN_DEMO_ROUTER", u"ws://127.0.0.1:8080/ws"),
        u'orthogonalspace',
    )
    runner.run(OrthogonalSpaceComponent)

if __name__ == '__main__':
    main()
