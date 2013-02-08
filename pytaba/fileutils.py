import base64
import imghdr
from os.path import abspath

import asyncmongo
from PIL import Image


class UnknowFileType(Exception):
    pass


class FileManager(object):
    #should place in config
    IMG_MAX_SIZE = (250, 250)
    THREAD_IMG_MAX_SIZE = (150, 150)

    def __init__(self, raw_file_object, file_type):
        self.file_object = self._get_file_object(raw_file_object, file_type)
        self.file_type = file_type
        self.file_path = ''
        self.file_name_on_disk = ''
        self.file_origin_name = ''
        self.process()

    def _get_file_object(self, raw_file_object, file_type):
        """file_types = ('from thread', 'from board')"""
        if file_type == 'from board':
            self.file_origin_name = raw_file_object['image'][0]['filename']
            img = raw_file_object['image'][0]['body']
        elif file_type == 'from thread':
            _, img, _ = raw_file_object.split('|||')
            img = base64.decodestring(img[img.find('base64') + 7:])
        else:
            raise UnknowFileType
        return img

    def _img_resize(self):
        max_size = self.IMG_MAX_SIZE
        if self.file_type == 'from thread':
                max_size = self.THREAD_IMG_MAX_SIZE
        img = Image.open('%s/%s' % (self.file_path, self.file_name_on_disk))
        max_x, max_y = max_size
        x, y = float(img.size[0]), float(img.size[1])
        r = min(max_x / x, max_y / y)
        img = img.resize([int(s * r) for s in img.size], Image.ANTIALIAS)
        img.save('%s/resize_%s' % (self.file_path, self.file_name_on_disk))

    def _name_file(self):
        return asyncmongo.bson.ObjectId().__str__()

    def process(self):
        ext = imghdr.what('', self.file_object) or 'jpg'
        self.file_name_on_disk = '%s.%s' % (self._name_file(), ext)
        #need unhardcode that
        self.file_path = '%s/static/files' % abspath('.')
        with open('%s/%s' % (self.file_path, self.file_name_on_disk), 'w') as f:
            f.write(self.file_object)
        self._img_resize()
