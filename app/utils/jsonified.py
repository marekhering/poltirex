from datetime import datetime
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
        members = list(inspect.getmembers(self))
        for i, member in enumerate(members):
            k, v = member
            if isinstance(v, datetime):
                members[i] = (k, v.strftime("%m/%d/%Y, %H:%M:%S"))

        return {k: v for k, v in members if
                not inspect.ismethod(v) and
                not k.startswith('_') and
                is_jsonable(v)}
