from tornado.web import asynchronous
from tornado import gen

from pytaba.handlers import BaseHandler
from pytaba.model import Board
from pytaba.forms import TopicForm


class MainHandler(BaseHandler):

    @asynchronous
    @gen.engine
    def get(self):
        board = Board()
        boards = yield gen.Task(board.get_all)
        self.render('ver2/index.html', boards=boards,
                                    form=TopicForm())
