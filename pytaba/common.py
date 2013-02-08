import time
import json

import asyncmongo


def get_time():
    return time.time()


class JsonEncoder(json.JSONEncoder):
    """ Encode mongo ObjectId type """
    def default(self, obj):
        if isinstance(obj, asyncmongo.bson.ObjectId):
            return "%s" % obj.__str__()
        return json.JSONEncoder.default(self, obj)
