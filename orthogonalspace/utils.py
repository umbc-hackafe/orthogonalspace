import functools
import logging

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