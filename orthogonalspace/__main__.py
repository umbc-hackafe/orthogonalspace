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
import orthogonalspace
import asyncio
import docopt
import logging
import json
import sys
import os
from orthogonalspace.database import Database
from orthogonalspace.types import *

LOG = logging.getLogger()

class OrthogonalSpaceComponent(ApplicationSession):
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.traceback_app = True
        self.db = Database(self.config.extra)
        self.lobby = orthogonalspace.lobby.Lobby()

    @asyncio.coroutine
    def onJoin(self, details):
        yield from self.register(self.lobby.list_universes, u'space.orthogonal.lobby.list_universes')
        yield from self.register(self.lobby.list_ships, u'space.orthogonal.lobby.list_ships')

        while True:
            self.publish(u'space.orthogonal.heartbeat', 'Hi')
            yield from asyncio.sleep(1)

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

    logging.basicConfig(level=level)

    config = {}

    try:
        conf_path = arguments["config"]
        if not os.path.isfile(conf_path):
            conf_path = "/etc/orthogonalspace/conf.json"
        if not os.path.isfile(conf_path):
            conf_path = "/usr/lib/orthogonalspace/conf.json"
        if not os.path.isfile(conf_path):
            sys.exit("You must provide a config file")
         
        with open(arguments["config"]) as conf_file:
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
