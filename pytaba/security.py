import re
import logging

import tornado.web
from tornado.web import asynchronous
from tornado import gen


import tornado

from pytaba import BaseHandler


class Security(object):
    """This is a not really class it's just
    a set of methods from BaseHandler compose where
    for future purposes"""

    def __init__(self, *args, **kwargs):
        super(BaseHandler, self).__init__(*args, **kwargs)
        self.method = self.request.method.lower()
        self.handler_name = self._get_called_handler_name()
        self.user = None

    def _get_called_handler_name(self):
        path = self.request.path
        handlers = self.application.named_handlers
        handler_name = [k for k, v in handlers.iteritems()
                        if re.match(v.regex, path)]
        if len(handler_name) > 1:
            raise tornado.web.HTTPError(500, 'Found more then one handlers')
        elif len(handler_name) == 0:
            raise tornado.web.HTTPError(404, 'Page not found')
        else:
            return handler_name[0]

    @gen.engine
    def _has_permissions_to_handler(self, handler_name, method):
        def mock(r): return r
        method = method.lower()
        has_permission = False
        right = Right()
        right_data = right.get({'name': handler_name}, mock)
        print 'This is return ', right.get({'name': handler_name}, mock)
        user = User()
        user_data = user.get({'login': self.user}, mock)
        #import ipdb; ipdb.set_trace()
        if not all([right_data, user_data]):
            raise tornado.web.HTTPError(403, 'Access deniend')
        rights = right_data[0].get('rights')
        user_groups = user_data[0].get('group')
        for group in user_groups:
            if group in rights.get(method):
                has_permission = True
        if not has_permission:
            raise tornado.web.HTTPError(403, 'Access deniend')

    @asynchronous
    def prepare(self):
        handler_name = self._get_called_handler_name()
        method = self.request.method
        self._has_permissions_to_handler(handler_name, method)

    def get_current_user(self):
        self.user = self.get_secure_cookie('login')
        has_perm = self._has_permissions_to_handler(self.handler_name, self.method)
        print 'has perm is ', has_perm
        if not has_perm:
            return False
        return True