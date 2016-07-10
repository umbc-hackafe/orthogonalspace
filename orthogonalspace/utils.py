import functools
import inspect
import asyncio

from orthogonalspace.serializer import serialize, unserialize


class ObjectMapper:
    def __init__(self, kind=object, key='id'):
        self._items = {}
        self._regtype = kind
        self.key = key

    def register(self, obj):
        assert isinstance(obj, self._regtype)
        assert hasattr(obj, self.key)

        key = getattr(obj, self.key)
        assert key not in self._items

        self._items[key] = obj

    def canon(self, obj=None, key=None, update=False):
        # Exactly one of obj an key should be present
        assert (obj is not None) != (key is not None)

        if obj:
            assert hasattr(obj, self.key)
            res = self._items[getattr(obj, self.key)]

            if update:
                res.__dict__.update(obj.__dict__)

            return res

        if key:
            return self._items[key]


def register(uri_pattern):
    def decorator(f):
        setattr(f, "_orth_uri_pattern", uri_pattern)
        return f

    return decorator


def register_patterns(obj, session, prefix=None):
    coros = []
    for name, func in inspect.getmembers(obj, lambda f: inspect.ismethod(f) or inspect.isfunction(f)):
        if hasattr(func, "_orth_uri_pattern"):
            pattern = getattr(func, "_orth_uri_pattern").format(obj)

            if prefix is None and hasattr(obj, 'PREFIX'):
                prefix = getattr(obj, 'PREFIX')

            if prefix:
                pattern = prefix.format(obj) + pattern

            coros.append(session.register(func, pattern))

    return asyncio.gather(*coros)


def publish_prefix(obj, session, topic, *args, **kwargs):
    prefix = getattr(obj, 'PREFIX', '')
    topic = prefix + topic
    topic = topic.format(obj)
    return session.publish(topic, *args, **kwargs)


def serial(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        res = await f(*[unserialize(o) if isinstance(o, (str, bytes)) else o for o in args], **{k: v if k == 'options' or not isinstance(v, (str, bytes)) else unserialize(v) for k, v in kwargs.items()})
        return serialize(res)

    return wrapper


def filter_attrs(obj, *keys):
    return {k: v for k, v in getattr(obj, '__dict__', {}).items() if k not in keys}


async def publish(session, topic, *args, **kwargs):
    return session.publish(topic, [serialize(arg) for arg in args], {k: serialize(v) if k != 'options' else v for k, v in kwargs.items()})