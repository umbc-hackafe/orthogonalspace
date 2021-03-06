#!/usr/bin/env python3
"""{0}

Usage:
  {0} --help
  {0} --version
  {0} [--config=<file>] [-v | -vv | -vvv | -vvvv | -q | -qq]

Options:
  -h --help           Show this text.
     --version        Print the version.
  -v --verbose        Set verbosity.
  -q --quiet          Suppress output. Use -qq to suppress even errors.
  -c --config=<file>  Path to config file[default: /etc/orthogonalspace/conf.json].
"""

from autobahn.asyncio.wamp import ApplicationSession, ApplicationRunner
from autobahn import wamp
import asyncio
import docopt
import logging
import json
import sys
import os

import orthogonalspace
from orthogonalspace.database import Database
from orthogonalspace.types import *
from orthogonalspace.lobby import Lobby, LobbyShip
from orthogonalspace.serializer import serialize

LOG = logging.getLogger()


class OrthogonalSpaceComponent(ApplicationSession):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.traceback_app = True
        self.db = Database(self.config.extra)
        self.lobby = Lobby(self)

    def publish(self, topic, *args, **kwargs):
        return super().publish(topic, [serialize(arg) for arg in args], {k: serialize(v) if k != 'options' else v for k,v in kwargs.items()})

    async def single_register(self, method):
        if isinstance(method, wamp.protocol.Registration):
            LOG.debug("Registered procedure {} successfully".format(method))
        else:
            LOG.error("Failed to register procedure {}".format(method))

    async def register_object(self, obj):
        results = await self.register(obj)
        for res in results:
            val = await self.single_register(res)

    async def onJoin(self, details):
        for target in [self, self.lobby]:
            LOG.debug("Registering {}".format(target))
            await self.register_object(target)

        results = await self.subscribe(self)
        for res in results:
            if isinstance(res, wamp.protocol.Subscription):
                LOG.debug("Subscribed handler with subscription ID {}".format(res))
            else:
                LOG.error("Failed to subscribe handler: {}".format(res))

        orthogonalspace.main_loop(self, self.db, self.lobby)

    @wamp.register(u'com.add_user')
    def add_user(self, username, password):
        session = self.db.Session()
        user = User()
        user.name = username
        user.password_hash = user.generate_hash(password)
        session.add(user)
        session.commit()
        session.close()

    @wamp.register(u'com.login')
    def login(self, username, password):
        session = self.db.Session()
        try:
            user = session.query(User).filter(User.name == username).one()
        except:
            LOG.error("Could not find username {0}".format(username))
            session.close()
            return None
        if user.login(password):
            # Success!
            websessions = session.query(WebSession).filter(WebSession.user_id == user.ID).all()
            for i in websessions:
                if i.expired(self.config.extra['session_duration']) and i.user.name == username:
                    session.delete(i)
            websession = WebSession(user.ID)
            websessionID = websession.uuid
            session.add(websession)
            LOG.info("User {0} logged in successfully with session {1}".format(username, websession.uuid))
            session.commit()
            session.close()
            return str(websessionID)
        else:
            LOG.info("Login failed for user {0}".format(username))
            # Failure!
            session.close()
            return None

    @wamp.register(u'com.sessioncheck')
    def sessioncheck(self, username, sessionID):
        session = self.db.Session()
        try:
            websession = session.query(WebSession).filter(WebSession.uuid == sessionID).one()
        except:
            LOG.error("Could not find session {0} for user {1}".format(sessionID, username))
            session.close()
            return False
        if not websession.expired(self.config.extra['session_duration']) and websession.user.name == username:
            LOG.info("Renewing session {0} for user {1}".format(sessionID, username))
            websession.timestamp = datetime.datetime.now()
            session.add(websession)
            session.commit()
            session.close()
            return True
        else:
            LOG.info("Invalid session {0} attempted for user {1}".format(sessionID, username))
            session.close()
            return False

    @wamp.register(u'com.logout')
    def logout(self, username, sessionID):
        session = self.db.Session()
        try:
            websession = session.query(WebSession).filter(WebSession.uuid == sessionID).one()
        except:
            LOG.error("Could not find session {0} for user {1} during logout".format(sessionID, username))
            session.close()
            return False
        if not websession.expired(self.config.extra['session_duration']) and websession.user.name == username:
            LOG.info("Logging out user {0} from session {1}".format(username, sessionID))
            session.delete(websession)
            session.commit()
            session.close()
            return True
        else:
            LOG.info("User {0} failed to log out with session {1}".format(username, sessionID))
            session.close()
            return False


def main():
    # load command-line options
    arguments = docopt.docopt(__doc__.format(sys.argv[0]), version="0.0.1")

    # All these dashes are stupid
    arguments = {k.lstrip('--'): v for k,v in arguments.items()}

    verbose = arguments.get("verbose", 0)
    quiet = arguments.get("quiet", 0)
    level = logging.WARN

    if verbose == 1:
        level = logging.INFO
    elif verbose == 2:
        level = logging.DEBUG
    elif verbose == 3:
        level = logging.DEBUG - 1
    elif verbose == 4:
        level = logging.DEBUG - 2
    elif quiet == 1:
        level = logging.ERROR
    elif quiet == 2:
        level = logging.CRITICAL + 1


    config = {}

    try:
        conf_path = arguments["config"]
        if not os.path.isfile(conf_path):
            conf_path = "/etc/orthogonalspace/conf.json"
        if not os.path.isfile(conf_path):
            conf_path = "/usr/lib/orthogonalspace/conf.json"
        if not os.path.isfile(conf_path):
            sys.exit("You must provide a config file")
         
        with open(conf_path) as conf_file:
            config = json.load(conf_file)

    except (OSError, IOError):
        LOG.exception("Could not load config file {}:".format(arguments["config"]))
        pass

    runner = ApplicationRunner(
        os.environ.get("AUTOBAHN_DEMO_ROUTER", u"ws://127.0.0.1:8080/ws"),
        u'orthogonalspace',
        extra=config,
    )
    runner.run(OrthogonalSpaceComponent)


if __name__ == '__main__':
    main()
