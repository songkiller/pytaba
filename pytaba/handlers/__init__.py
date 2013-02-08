import tornado.web
from asyncmongo import bson


class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)

    @property
    def hash(self):
        return bson.ObjectId()
