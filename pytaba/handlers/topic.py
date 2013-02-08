import json

from tornado.web import asynchronous
from tornado import gen
from asyncmongo import bson
import tornadio2
from tornadio2 import gen as tiogen

from pytaba.handlers import BaseHandler
from pytaba.forms import CommentForm
from pytaba.model import Topic, TopicMetaData
from pytaba.fileutils import FileManager


class TopicHandler(BaseHandler):

    @asynchronous
    @gen.engine
    def get(self, board_name, topic_hash):
        topic = Topic()
        topic_data = yield gen.Task(topic.get,
                                    {'_id': bson.ObjectId(topic_hash)})
        self.render('topic.html', form=CommentForm(),
                                  content=topic_data[0],
                                  action_url='',
                                  topic_hash=topic_hash)

    @asynchronous
    @gen.engine
    def post(self, board_name, topic_hash):
        form = CommentForm(self.request.arguments)
        if form.validate():
            topic = Topic()
            yield gen.Task(topic.add_comment, form.data,
                           bson.ObjectId(topic_hash))
            self.redirect('/%s/res/%s' % (board_name, topic_hash))


class CommentRealtimeHandler(tornadio2.SocketConnection):
    participants = set()

    @tiogen.engine
    def on_open(self, *args, **kwargs):
        self.participants.add(self)
        #topic_meta = TopicMetaData()
        #yield gen.Task(topic_meta.inc_participants, topic_hash, 1)

    #trash and hell here, send images throught
    #websocks and dump messages to DB
    #DEEP REFACTORING NEED HERE
    @tiogen.engine
    def on_message(self, message):
        comment, img, topic_hash = message.split('|||')
        data = {'comment': comment, 'img': ''}
        if img:
            fm = FileManager(message, 'from thread')
            file_name_on_disk = fm.file_name_on_disk
            data['img'] = file_name_on_disk
        for p in self.participants:
            p.send(json.dumps(data))
        topic = Topic()
        c = dict()
        data = json.loads(data)
        c['body'] = data.get('comment')
        c['image'] = data.get('img')
        yield gen.Task(topic.add_comment, c,
                        bson.ObjectId(topic_hash))
    @tiogen.engine
    def on_close(self):
        self.participants.remove(self)
        topic_meta = TopicMetaData()
        yield gen.Task(topic_meta.participants, topic_hash, -1)

    @tiogen.engine
    @tornadio2.event
    def register_new_participant(self, thread_hash):
        topic_meta = TopicMetaData()
        yield gen.Task(topic_meta.participants(thread_hash, 1))
        