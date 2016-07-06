import functools

from orthogonalspace.serializer import serialize


def serial(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        res = await f(*args, **kwargs)
        return serialize(res)

    return wrapper


def filter_attrs(obj, *keys):
    return {k: v for k, v in getattr(obj, '__dict__', {}).items() if k not in keys}

async def publish(session, topic, *args, **kwargs):
    return session.publish(topic, [serialize(arg) for arg in args], {k: serialize(v) if k != 'options' else v for k, v in kwargs.items()})