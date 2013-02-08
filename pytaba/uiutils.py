import time


def get_opt(self, opt):
    return self.application.settings.get(opt)


def get_media(self, opt):
    #TODO: hardcode should be remove
    opts = {'css': '/static',
            'js': '/static/js',
            'images': '/static/files'}
    return opts.get(opt, '')


def time_prettify(time_float):
    return time.ctime(time_float)
