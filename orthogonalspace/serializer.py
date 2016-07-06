import jsonpickle


def serialize(obj):
    return jsonpickle.encode(obj)


def unserialize(obj):
    return jsonpickle.decode(obj)
