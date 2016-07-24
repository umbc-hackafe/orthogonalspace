import itertools
import asyncio
import ode

from orthogonalspace import lobby

FORCE_UPDATE_FREQ = 5
GAME_SPEED = 1.0
TICK_RATE = 30
STEP_SIZE = 1 / TICK_RATE * GAME_SPEED

# Code for call_periodic taken from: https://gist.github.com/akaIDIOT/48c2474bd606cd2422ca
def call_periodic(interval, callback, *args, **kwargs):
    # get loop as a kwarg or take the default one
    loop = kwargs.get('loop') or asyncio.get_event_loop()
    # record the loop's time when call_periodic was called
    start = loop.time()

    def run(handle):
        # XXX: we could record before = loop.time() and warn when callback(*args) took longer than interval
        # call callback now (possibly blocks run)
        callback(*args)
        # reschedule run at the soonest time n * interval from start
        # re-assign delegate to the new handle
        handle.delegate = loop.call_later(interval - ((loop.time() - start) % interval), run, handle)

    class PeriodicHandle:  # not extending Handle, needs a lot of arguments that make no sense here
        def __init__(self):
            self.delegate = None

        def cancel(self):
            assert isinstance(self.delegate, asyncio.Handle), 'no delegate handle to cancel'
            self.delegate.cancel()

    periodic = PeriodicHandle()  # can't pass result of loop.call_at here, it needs periodic as an arg to run
    # set the delegate to be the Handle for call_at, causes periodic.cancel() to cancel the call to run
    periodic.delegate = loop.call_at(start + interval, run, periodic)
    # return the 'wrapper'
    return periodic


def collide_callback(args, obj1:  ode.GeomObject, obj2: ode.GeomObject):
    if ode.areConnected(obj1.getBody(),obj2.getBody()):
        pass

    contacts = ode.collide(obj1, obj2)

    world, joint_group = args

    for c in contacts:
        j = ode.ContactJoint(world, joint_group, c)
        j.attach(obj1.getBody(), obj2.getBody())


def step(counter, session, event_loop, db, lobby, space, joint_group):
    for universe in lobby.universes:
        count = next(counter)
        space.collide((universe.world, joint_group), collide_callback)
        universe.world.step(STEP_SIZE)

        for entity in universe.entities:
            do_send = False

            if hasattr(entity, 'do_tick'):
                do_send = entity.do_tick(STEP_SIZE)

            if hasattr(entity, 'send_update'):
                # Offset force updates by the entity ID so they're more spread out
                if do_send or (not (count + entity.id) % FORCE_UPDATE_FREQ):
                    event_loop.call_soon(entity.send_update)

        joint_group.empty()


def main_loop(session, db, lobby: lobby.Lobby):
    event_loop = asyncio.get_event_loop()
    space = ode.SimpleSpace()
    joint_group = ode.JointGroup()

    counter = itertools.count()

    handle = call_periodic(
        1 / TICK_RATE,
        step,
        counter, session, event_loop, db, lobby, space, joint_group, loop=event_loop
    )

