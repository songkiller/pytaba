# -*- coding: utf8 -*-

import time
import logging

import asyncmongo

from tornado import gen

log = logging.getLogger(__name__)


def mock():
    pass


def initial():
    boards = [{'category':'Main', 'title':'Программирование', 'url':'pr',
               'order':1}, {'category':'Main', 'title':'Бред', 'url': 'b',
               'order':2}]
    users = [{'login': 'admin', 'password': 'random', 'group':['admin']}]
    rights = [{'name': 'main', 'rights': {'get': ['admin', 'user', 'reader']}}]
    b = Board()
    for board in boards:
        b.create(board, callback=mock)


class BaseDB(object):
    def __init__(self):
        #MUST be place as singleton out of here
        self.db = asyncmongo.Client(pool_id='mydb', host='127.0.0.1',
                                         port=27017, maxcached=10,
                                         maxconnections=50, dbname='pytaba')
        self.table = None

    def _data_cleaner(self):
        """Need create decorator for output
        data. All actions with data MUST placed in
        models"""
        pass

    @gen.engine
    def create(self, data, callback=None):
        yield gen.Task(self.table.insert, data)
        callback()

    @gen.engine
    def update(self, where, query, callback=None):
        yield gen.Task(self.table.update, where, query)
        callback()

    def remove(self, where, callback=None):
        self.table.remove(where)
        callback()

    @gen.engine
    def get(self, where, callback=None, **kwargs):
        r = yield gen.Task(self.table.find, where, **kwargs)
        callback(r[0][0])

    @gen.engine
    def get_one(self, where, callback=None):
        r = yield gen.Task(self.table.find_one, where)
        callback(r[0][0])

    @gen.engine
    def get_all(self, callback=None):
        r = yield gen.Task(self.table.find)
        callback(r[0][0])

    def record_timestamp(self):
        return time.time()


class Topic(BaseDB):
    """
    Fields:
        title(str)
        board(str)
        last_update(int)
        image(str)
        owner(str)
        hash(str)
        comments(list):
            created(int)
            #title(str)
            body(str)
            image(str)
            #owner(str)??? if only privat schema work
    """
    def __init__(self):
        super(Topic, self).__init__()
        self.table = self.db.topic

    @gen.engine
    def add_comment(self, comment, topic_hash, callback):
        query = {'$push': {'comments': {'created': self.record_timestamp(),
                                        'body': comment.get('body'),
                                        'image': comment.get('image'),
                                        'is_resized_img': comment.get('is_resized_img')
                                        }
                           }
                 }
        where = {'_id': topic_hash}
        yield gen.Task(self.update, where, query)
        callback()


class Board(BaseDB):
    """
    Fields:
        category(str)
        title(str)
        order(int)
    """
    def __init__(self):
        super(Board, self).__init__()
        self.table = self.db.board


class TopicMetaData(BaseDB):
    """Meta information based on websockets events"""
    def __init__(self, topic_id=None):
        super(TopicMetaData, self).__init__()
        self.table = self.db.board
        self.topic_id = topic_id

    @gen.engine
    def get_meta_data(self, callback):
        query = {'_id': asyncmongo.bson.ObjectId(self.topic_id)}
        yield gen.Task(self.get_one, query)
        callback()

    @gen.engine
    def participants(self, inc_value, callback):
        query = {'$inc': {'participants': inc_value}}
        where = {'_id': asyncmongo.bson.ObjectId(self.topic_id)}
        yield gen.Task(self.update, where, query)
        callback()