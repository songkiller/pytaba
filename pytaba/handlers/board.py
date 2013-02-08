import logging
import json
import urlparse
import math

from tornado.web import asynchronous
from tornado import gen

from pytaba.handlers import BaseHandler
from pytaba.forms import TopicForm
from pytaba.model import Topic, TopicMetaData
from pytaba.common import get_time, JsonEncoder
from pytaba.fileutils import FileManager

log = logging.getLogger(__name__)


class BoardHandler(BaseHandler):

    def _paginate(self):
        page = int(self.request.arguments.get('page', 1))
        #some hardcode here
        max_on_page = 5
        max_lists = 5
        i = 0
        for el in range(0, max_on_page * max_lists, max_on_page):
            if i == page:
                return (el - max_on_page, el, page)
            i += 1

    def _render_paginator(self, count_of_pages, page):
        html = ''
        if count_of_pages > 1:
            html = self.render('ver2/paginate.html',
                               page={'count_of_pages': count_of_pages,
                                     'page': page})
        return html

    @asynchronous
    @gen.engine
    def get(self, board_name):
        topic = Topic()
        board = yield gen.Task(topic.get, {'board': board_name},
                               limit=50, sort=[('$natural', -1)])
        min, max, page = self._paginate()
        count_of_pages = math.ceil(len(board[:25]) / 5)
        for topic in board:
            topic['number_of_comments'] = len(topic.get('comments', []))
            topic['comments_with_image'] = sum([1 for comment in
                                                topic.get('comments', [])
                                                if comment.get('image')])
        board[0]['comments'] = board[0]['comments'][len(board[0]['comments'])-3:]
        self.write(json.dumps({'threads': board[min:max], 'page': page,
                               'count_of_pages': count_of_pages},
                              cls=JsonEncoder))
        self.finish()

    def _save_file_adapter(self):
        try:
            fm = FileManager(self.request.files, 'from board')
            return fm.file_origin_name, fm.file_name_on_disk
        except Exception as e:
            log.error('On file save error: %s', e)
            return None, None

    def _request_to_dict(self):
        return {k: v for k, v in (el for el in urlparse.parse_qsl(
                                self.request.arguments.get('0')[0]))}

    @asynchronous
    @gen.engine
    def post(self, board_name):
        form = TopicForm(**self._request_to_dict())
        response = {'status': 'error', 'error_fields': form.errors}
        print form.validate()
        if form.validate():
            topic = Topic()
            data = form.data
            data['created'] = get_time()
            data['board'] = board_name
            data['_id'] = self.hash
            data['url'] = '%s/res/%s' % (board_name, data['_id'])
            data['comments'] = []
            file_origin_name, file_name_on_disk = self._save_file_adapter()
            if (file_origin_name, file_name_on_disk):
                #all goes fine and we finish create of topic document
                data['file_origin_name'] = file_origin_name
                data['image'] = file_name_on_disk
            yield gen.Task(topic.create, data)
            meta_data = TopicMetaData()
            meta_struct = {'participants': 1}
            yield gen.Task(meta_data.create, meta_struct)
            response = {'status': 'success'}
        self.write(json.dumps(response))
        self.finish()
