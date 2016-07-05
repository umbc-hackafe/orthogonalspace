##############################################################################
# Stolen from https://groups.google.com/forum/#!topic/autobahnws/6Pk0c8JiSn0 #
# Mostly written by Florian Conrady                                          #
##############################################################################

from autobahn.wamp.serializer import *
from autobahn.wamp.interfaces import IObjectSerializer, ISerializer
import jsonpickle
import six

class JsonPickleObjectSerializer:

    BINARY = False

    def __init__(self, batched = False):
        """
        Ctor.

        :param batched: Flag that controls whether serializer operates in batched mode.
        :type batched: bool
        """
        self._batched = batched

    def serialize(self, obj):
        """
        Implements :func:`autobahn.wamp.interfaces.IObjectSerializer.serialize`
        """
        try:
            _dumps = lambda obj: jsonpickle.dumps(obj)
            s = _dumps(obj)
            if isinstance(s, six.text_type):
                s = s.encode('utf8')
            if self._batched:
                return s + b'\30'
            else:
                return s
        except Exception as e:
            print(e)

    def unserialize(self, payload):
        """
        Implements :func:`autobahn.wamp.interfaces.IObjectSerializer.unserialize`
        """
        if self._batched:
            chunks = payload.split(b'\30')[:-1]
        else:
            chunks = [payload]
        if len(chunks) == 0:
            raise Exception("batch format error")
        _loads = jsonpickle.loads
        return [_loads(data.decode('utf8')) for data in chunks]

IObjectSerializer.register(JsonPickleObjectSerializer)


class JsonPickleSerializer(Serializer):

    SERIALIZER_ID = "json"
    MIME_TYPE = "application/json"

    def __init__(self, batched = False):
        """
        Ctor.

        :param batched: Flag to control whether to put this serialized into batched mode.
        :type batched: bool
        """
        Serializer.__init__(self, JsonPickleObjectSerializer(batched=batched))
        if batched:
            self.SERIALIZER_ID = "json.batched"

ISerializer.register(JsonPickleSerializer)
