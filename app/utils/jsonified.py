import inspect
import json


def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except (TypeError, OverflowError):
        return False


class Jsonified:
    def to_json(self):
        return {k: v for k, v in inspect.getmembers(self) if
                not inspect.ismethod(v) and
                not k.startswith('_') and
                is_jsonable(v)}
