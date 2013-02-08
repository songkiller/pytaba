import logging

import tornado
import tornadio2
from tornado.web import url
from tornado.options import define, options

from handlers import main, board, topic
import uiutils

log = logging.getLogger(__name__)

settings = {'debug': True, 'template_path': 'tpls', 'autoescape': None,
            'cookie_secret': 'somesecrete', 'login_url': '/',
            'socket_io_port': 8000, 'ui_methods': uiutils, 'domain':
            'localhost', 'project_name': 'codename Pytaba'}

MyRouter = tornadio2.TornadioRouter(topic.CommentRealtimeHandler)

router = [#url(r"/", main.EntranceHandler, name='entrance'),
          #url(r"/main$", main.MainHandler, name='main'),
          url(r"/", main.MainHandler, name='main'),
          url(r"/([a-z]{1,4})", board.BoardHandler, name='board'),
          url(r"/(?P<board_name>[a-z]+)/res/(?P<topic_hash>.*)",
              topic.TopicHandler, name='topic'),
          (r"/static/(.*)", tornado.web.StaticFileHandler, {'path': 'static'}),
          ]

application = tornado.web.Application(router, **settings)

sock_app = tornado.web.Application(MyRouter.urls,
                                   flash_policy_port=843,
                                   flash_policy_file='/your/absolute/path/to/pytaba/static/js/flashpolicy.xml',
                                   socket_io_port=8002)

if __name__ == '__main__':
    define('init', default=False, help='Init DB')
    tornado.options.parse_command_line()
    if options.init:
        from pytaba.model import initial
        initial()
        log.info('DB fixtures is setup')
        exit()
    logging.basicConfig(level=logging.DEBUG)
    application.listen(80)
    socketio_server = tornadio2.SocketServer(sock_app)
    tornado.ioloop.IOLoop.instance().start()
    
